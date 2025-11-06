"""
Provider registry and factory.

Manages provider instances and provides factory methods for creating
and retrieving providers.
"""

from typing import TYPE_CHECKING

from loguru import logger

from app.config import settings
from app.providers.base import BaseProvider, ProviderType
from app.providers.community_dragon import CommunityDragonProvider
from app.providers.data_dragon import DataDragonProvider
from app.providers.riot_api import RiotAPIProvider

if TYPE_CHECKING:
    from app.config import Settings


class ProviderRegistry:
    """
    Singleton registry for managing API provider instances.

    Handles creation, caching, and retrieval of provider instances.
    Ensures only one instance of each provider type exists (singleton pattern).
    """

    _instance: "ProviderRegistry | None" = None
    _providers: dict[ProviderType, BaseProvider]

    def __new__(cls) -> "ProviderRegistry":
        """Ensure only one registry instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            logger.info("Provider registry initialized")
        return cls._instance

    def register_provider(self, provider: BaseProvider) -> None:
        """
        Register a provider instance.

        Args:
            provider: Provider instance to register
        """
        self._providers[provider.provider_type] = provider
        logger.info(f"Registered provider: {provider.name} ({provider.provider_type.value})")

    def get_provider(self, provider_type: ProviderType) -> BaseProvider:
        """
        Get a provider instance by type.

        Args:
            provider_type: Type of provider to retrieve

        Returns:
            Provider instance

        Raises:
            ValueError: If provider type is not registered
        """
        if provider_type not in self._providers:
            raise ValueError(f"Provider type '{provider_type.value}' is not registered")

        return self._providers[provider_type]

    def has_provider(self, provider_type: ProviderType) -> bool:
        """
        Check if a provider type is registered.

        Args:
            provider_type: Type of provider to check

        Returns:
            True if provider is registered
        """
        return provider_type in self._providers

    def get_all_providers(self) -> list[BaseProvider]:
        """
        Get all registered providers.

        Returns:
            List of all provider instances
        """
        return list(self._providers.values())

    async def health_check_all(self) -> dict[str, bool]:
        """
        Check health of all registered providers.

        Returns:
            Dictionary mapping provider names to health status
        """
        results = {}
        for provider in self._providers.values():
            results[provider.name] = await provider.health_check()
        return results

    async def close_all(self) -> None:
        """Close all provider connections."""
        for provider in self._providers.values():
            await provider.close()
        logger.info("All providers closed")

    def clear(self) -> None:
        """Clear all registered providers (useful for testing)."""
        self._providers.clear()
        logger.debug("Provider registry cleared")


# Global registry instance
_registry = ProviderRegistry()


def initialize_providers(settings_override: "Settings | None" = None) -> None:
    """
    Initialize and register all configured providers.

    Args:
        settings_override: Optional Settings instance for testing
    """
    config = settings_override if settings_override is not None else settings

    # Always initialize Riot API provider (core functionality)
    riot_provider = RiotAPIProvider(settings_override=settings_override)
    _registry.register_provider(riot_provider)

    # Check which providers are enabled
    enabled = config.enabled_providers

    # Initialize Data Dragon if enabled
    if "data_dragon" in enabled:
        ddragon_provider = DataDragonProvider(
            version=config.data_dragon_version,
            locale=config.data_dragon_locale,
        )
        _registry.register_provider(ddragon_provider)

    # Initialize Community Dragon if enabled
    if "community_dragon" in enabled:
        cdragon_provider = CommunityDragonProvider(
            version=config.community_dragon_version,
        )
        _registry.register_provider(cdragon_provider)

    logger.info(f"Initialized {len(_registry.get_all_providers())} provider(s)")


def get_provider(provider_type: ProviderType) -> BaseProvider:
    """
    Get a provider instance from the global registry.

    Args:
        provider_type: Type of provider to retrieve

    Returns:
        Provider instance

    Raises:
        ValueError: If provider is not registered
    """
    return _registry.get_provider(provider_type)


def get_registry() -> ProviderRegistry:
    """
    Get the global provider registry.

    Returns:
        Global registry instance
    """
    return _registry
