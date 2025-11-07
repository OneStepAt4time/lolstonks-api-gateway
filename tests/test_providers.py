"""
Tests for API provider implementations.
"""

import pytest

from app.config import Settings
from app.providers.base import ProviderCapability, ProviderType
from app.providers.community_dragon import CommunityDragonProvider
from app.providers.data_dragon import DataDragonProvider
from app.providers.registry import ProviderRegistry, initialize_providers
from app.providers.riot_api import RiotAPIProvider


class TestRiotAPIProvider:
    """Tests for Riot API provider."""

    def test_provider_initialization(self):
        """Test that RiotAPIProvider initializes correctly."""
        settings = Settings(riot_api_key="test-key")
        provider = RiotAPIProvider(settings_override=settings)

        assert provider.name == "Riot Games Developer API"
        assert provider.provider_type == ProviderType.RIOT_API
        assert provider.requires_auth is True

    def test_provider_capabilities(self):
        """Test that RiotAPIProvider declares correct capabilities."""
        settings = Settings(riot_api_key="test-key")
        provider = RiotAPIProvider(settings_override=settings)

        capabilities = provider.get_capabilities()
        assert ProviderCapability.LIVE_DATA in capabilities
        assert ProviderCapability.HISTORICAL_DATA in capabilities


class TestDataDragonProvider:
    """Tests for Data Dragon provider."""

    def test_provider_initialization(self):
        """Test that DataDragonProvider initializes correctly."""
        provider = DataDragonProvider(version="13.24.1", locale="en_US")

        assert provider.name == "Data Dragon CDN"
        assert provider.provider_type == ProviderType.DATA_DRAGON
        assert provider.requires_auth is False
        assert provider.version == "13.24.1"
        assert provider.locale == "en_US"

    def test_provider_capabilities(self):
        """Test that DataDragonProvider declares correct capabilities."""
        provider = DataDragonProvider()

        capabilities = provider.get_capabilities()
        assert ProviderCapability.STATIC_DATA in capabilities
        assert ProviderCapability.ASSETS in capabilities
        assert ProviderCapability.VERSIONED in capabilities

    def test_champion_image_url(self):
        """Test champion image URL generation."""
        provider = DataDragonProvider(version="13.24.1")

        url = provider.get_champion_image_url("Ahri")
        assert "13.24.1" in url
        assert "Ahri.png" in url

    def test_champion_splash_url(self):
        """Test champion splash URL generation."""
        provider = DataDragonProvider()

        url = provider.get_champion_splash_url("Ahri", skin_num=1)
        assert "Ahri_1.jpg" in url

    def test_item_image_url(self):
        """Test item image URL generation."""
        provider = DataDragonProvider(version="13.24.1")

        url = provider.get_item_image_url("3089")
        assert "13.24.1" in url
        assert "3089.png" in url


class TestCommunityDragonProvider:
    """Tests for Community Dragon provider."""

    def test_provider_initialization(self):
        """Test that CommunityDragonProvider initializes correctly."""
        provider = CommunityDragonProvider(version="13.24")

        assert provider.name == "Community Dragon"
        assert provider.provider_type == ProviderType.COMMUNITY_DRAGON
        assert provider.requires_auth is False
        assert provider.version == "13.24"

    def test_provider_capabilities(self):
        """Test that CommunityDragonProvider declares correct capabilities."""
        provider = CommunityDragonProvider()

        capabilities = provider.get_capabilities()
        assert ProviderCapability.STATIC_DATA in capabilities
        assert ProviderCapability.ASSETS in capabilities
        assert ProviderCapability.VERSIONED in capabilities

    def test_champion_icon_url(self):
        """Test champion icon URL generation."""
        provider = CommunityDragonProvider(version="latest")

        url = provider.get_champion_icon_url(103)  # Ahri
        assert "latest" in url
        assert "103.png" in url

    def test_champion_splash_url(self):
        """Test champion splash URL generation."""
        provider = CommunityDragonProvider()

        url = provider.get_champion_splash_url(103, skin_id=1)
        assert "103/1.jpg" in url


class TestProviderRegistry:
    """Tests for provider registry."""

    def test_registry_singleton(self):
        """Test that registry is a singleton."""
        registry1 = ProviderRegistry()
        registry2 = ProviderRegistry()

        assert registry1 is registry2

    def test_register_and_get_provider(self):
        """Test provider registration and retrieval."""
        registry = ProviderRegistry()
        registry.clear()  # Clear any existing providers

        settings = Settings(riot_api_key="test-key")
        provider = RiotAPIProvider(settings_override=settings)
        registry.register_provider(provider)

        retrieved = registry.get_provider(ProviderType.RIOT_API)
        assert retrieved is provider

    def test_get_nonexistent_provider(self):
        """Test that getting non-existent provider raises error."""
        registry = ProviderRegistry()
        registry.clear()

        with pytest.raises(ValueError, match="not registered"):
            registry.get_provider(ProviderType.DATA_DRAGON)

    def test_has_provider(self):
        """Test provider existence check."""
        registry = ProviderRegistry()
        registry.clear()

        settings = Settings(riot_api_key="test-key")
        provider = RiotAPIProvider(settings_override=settings)
        registry.register_provider(provider)

        assert registry.has_provider(ProviderType.RIOT_API) is True
        assert registry.has_provider(ProviderType.DATA_DRAGON) is False

    def test_get_all_providers(self):
        """Test getting all providers."""
        registry = ProviderRegistry()
        registry.clear()

        settings = Settings(riot_api_key="test-key")
        riot_provider = RiotAPIProvider(settings_override=settings)
        ddragon_provider = DataDragonProvider()

        registry.register_provider(riot_provider)
        registry.register_provider(ddragon_provider)

        all_providers = registry.get_all_providers()
        assert len(all_providers) == 2
        assert riot_provider in all_providers
        assert ddragon_provider in all_providers

    def test_initialize_providers(self):
        """Test provider initialization from config."""
        settings = Settings(
            riot_api_key="test-key",
            enabled_providers=["riot_api", "data_dragon"],
            data_dragon_version="13.24.1",
            data_dragon_locale="en_US",
        )

        registry = ProviderRegistry()
        registry.clear()

        initialize_providers(settings_override=settings)

        assert registry.has_provider(ProviderType.RIOT_API)
        assert registry.has_provider(ProviderType.DATA_DRAGON)

        ddragon = registry.get_provider(ProviderType.DATA_DRAGON)
        assert isinstance(ddragon, DataDragonProvider)
        assert ddragon.version == "13.24.1"
        assert ddragon.locale == "en_US"


class TestProviderIntegration:
    """Integration tests for providers."""

    @pytest.mark.asyncio
    async def test_data_dragon_health_check(self):
        """Test Data Dragon health check (requires network)."""
        provider = DataDragonProvider()

        # This will make a real network request
        is_healthy = await provider.health_check()

        # Data Dragon should be available
        assert is_healthy is True

        await provider.close()

    @pytest.mark.asyncio
    async def test_community_dragon_health_check(self):
        """Test Community Dragon health check (requires network)."""
        provider = CommunityDragonProvider()

        # This will make a real network request
        is_healthy = await provider.health_check()

        # Community Dragon should be available
        assert is_healthy is True

        await provider.close()
