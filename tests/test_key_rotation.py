"""
Tests for API key rotation functionality.
"""

import pytest
from app.riot.key_rotator import KeyRotator
from app.config import Settings


class TestKeyRotator:
    """Test suite for KeyRotator class."""

    def test_init_with_single_key(self):
        """Test initialization with a single API key."""
        rotator = KeyRotator(["key1"])
        assert rotator.get_key_count() == 1

    def test_init_with_multiple_keys(self):
        """Test initialization with multiple API keys."""
        keys = ["key1", "key2", "key3"]
        rotator = KeyRotator(keys)
        assert rotator.get_key_count() == 3

    def test_init_with_empty_list(self):
        """Test initialization with empty list raises ValueError."""
        with pytest.raises(ValueError, match="at least one API key"):
            KeyRotator([])

    def test_round_robin_rotation(self):
        """Test round-robin rotation through keys."""
        keys = ["key1", "key2", "key3"]
        rotator = KeyRotator(keys)

        # First cycle
        assert rotator.get_next_key() == "key1"
        assert rotator.get_next_key() == "key2"
        assert rotator.get_next_key() == "key3"

        # Second cycle (wraps around)
        assert rotator.get_next_key() == "key1"
        assert rotator.get_next_key() == "key2"

    def test_single_key_rotation(self):
        """Test rotation with a single key always returns same key."""
        rotator = KeyRotator(["only_key"])

        for _ in range(5):
            assert rotator.get_next_key() == "only_key"

    def test_reset_rotation(self):
        """Test reset() returns rotation to first key."""
        keys = ["key1", "key2", "key3"]
        rotator = KeyRotator(keys)

        # Advance rotation
        rotator.get_next_key()  # key1
        rotator.get_next_key()  # key2

        # Reset and verify
        rotator.reset()
        assert rotator.get_next_key() == "key1"

    def test_thread_safety(self):
        """Test concurrent access to key rotator."""
        import threading

        keys = ["key1", "key2", "key3"]
        rotator = KeyRotator(keys)
        results = []

        def get_keys():
            for _ in range(10):
                results.append(rotator.get_next_key())

        # Create multiple threads
        threads = [threading.Thread(target=get_keys) for _ in range(5)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify all 50 calls (5 threads * 10 calls each)
        assert len(results) == 50

        # Verify all results are valid keys
        for key in results:
            assert key in keys


class TestSettingsKeyParsing:
    """Test suite for Settings.get_api_keys() method."""

    def test_get_api_keys_with_riot_api_keys(self, monkeypatch):
        """Test get_api_keys() with RIOT_API_KEYS (comma-separated)."""
        monkeypatch.setenv("RIOT_API_KEYS", "key1,key2,key3")
        monkeypatch.setenv("RIOT_API_KEY", "old_key")  # Should be ignored

        settings = Settings()  # type: ignore[call-arg]
        keys = settings.get_api_keys()

        assert len(keys) == 3
        assert keys == ["key1", "key2", "key3"]

    def test_get_api_keys_with_riot_api_key_fallback(self, monkeypatch):
        """Test get_api_keys() falls back to RIOT_API_KEY if RIOT_API_KEYS not set."""
        # Disable .env file loading for isolated test
        monkeypatch.setenv("RIOT_API_KEY", "single_key")
        monkeypatch.delenv("RIOT_API_KEYS", raising=False)

        # Create settings without loading .env file
        from pydantic_settings import SettingsConfigDict

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        settings = TestSettings()  # type: ignore[call-arg]
        keys = settings.get_api_keys()

        assert len(keys) == 1
        assert keys == ["single_key"]

    def test_get_api_keys_with_spaces(self, monkeypatch):
        """Test get_api_keys() trims whitespace from keys."""
        monkeypatch.setenv("RIOT_API_KEYS", " key1 , key2 , key3 ")

        settings = Settings()  # type: ignore[call-arg]
        keys = settings.get_api_keys()

        assert len(keys) == 3
        assert keys == ["key1", "key2", "key3"]

    def test_get_api_keys_with_empty_strings(self, monkeypatch):
        """Test get_api_keys() filters out empty strings."""
        monkeypatch.setenv("RIOT_API_KEYS", "key1,,key2,  ,key3")

        settings = Settings()  # type: ignore[call-arg]
        keys = settings.get_api_keys()

        assert len(keys) == 3
        assert keys == ["key1", "key2", "key3"]

    def test_get_api_keys_no_keys_configured(self, monkeypatch):
        """Test get_api_keys() raises ValueError if no keys configured."""
        monkeypatch.delenv("RIOT_API_KEY", raising=False)
        monkeypatch.delenv("RIOT_API_KEYS", raising=False)

        # Create settings without loading .env file
        from pydantic_settings import SettingsConfigDict

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        with pytest.raises(ValueError, match="No Riot API keys configured"):
            settings = TestSettings()  # type: ignore[call-arg]
            settings.get_api_keys()


class TestRiotClientKeyRotation:
    """Test suite for RiotClient key rotation integration."""

    @pytest.mark.asyncio
    async def test_riot_client_uses_rotated_keys(self, monkeypatch):
        """Test RiotClient rotates through multiple keys."""
        # Import and patch settings before creating client
        from app import config as app_config
        from pydantic_settings import SettingsConfigDict

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        monkeypatch.setenv("RIOT_API_KEYS", "key1,key2,key3")
        monkeypatch.delenv("RIOT_API_KEY", raising=False)

        test_settings = TestSettings()  # type: ignore[call-arg]
        monkeypatch.setattr(app_config, "settings", test_settings)

        # Import after patching
        from app.riot.client import RiotClient

        client = RiotClient()

        # Verify key rotator is initialized
        assert client.key_rotator.get_key_count() == 3

        # Verify rotation works
        keys_used = []
        for _ in range(6):
            keys_used.append(client.key_rotator.get_next_key())

        # Should cycle through keys twice
        assert keys_used == ["key1", "key2", "key3", "key1", "key2", "key3"]

        await client.close()

    @pytest.mark.asyncio
    async def test_riot_client_backward_compatible(self, monkeypatch):
        """Test RiotClient works with single RIOT_API_KEY (backward compatible)."""
        # Import and patch settings before creating client
        from app import config as app_config
        from pydantic_settings import SettingsConfigDict

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        monkeypatch.setenv("RIOT_API_KEY", "single_key")
        monkeypatch.delenv("RIOT_API_KEYS", raising=False)

        test_settings = TestSettings()  # type: ignore[call-arg]
        monkeypatch.setattr(app_config, "settings", test_settings)

        from app.riot.client import RiotClient

        client = RiotClient()

        # Verify single key mode
        assert client.key_rotator.get_key_count() == 1
        assert client.key_rotator.get_next_key() == "single_key"

        await client.close()
