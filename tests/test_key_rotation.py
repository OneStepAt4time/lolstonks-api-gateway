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
        from pydantic_settings import SettingsConfigDict

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        # Pass values directly to constructor instead of relying on env vars
        test_settings = TestSettings(riot_api_keys="key1,key2,key3", riot_api_key=None)  # type: ignore[call-arg]

        # Import RiotClient
        from app.riot.client import RiotClient

        # Create client with test settings
        client = RiotClient(settings_override=test_settings)

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
        from pydantic_settings import SettingsConfigDict

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        # Pass values directly to constructor instead of relying on env vars
        test_settings = TestSettings(riot_api_key="single_key", riot_api_keys=None)  # type: ignore[call-arg]

        # Import RiotClient
        from app.riot.client import RiotClient

        # Create client with test settings
        client = RiotClient(settings_override=test_settings)

        # Verify single key mode
        assert client.key_rotator.get_key_count() == 1
        assert client.key_rotator.get_next_key() == "single_key"

        await client.close()


class TestSmartKeyFallback:
    """Test suite for smart key fallback on 429 responses."""

    @pytest.mark.asyncio
    async def test_fallback_to_next_key_on_429(self, monkeypatch):
        """Test that 429 on Key 1 immediately tries Key 2 (no wait)."""
        from unittest.mock import AsyncMock, Mock
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2", riot_api_key=None)  # type: ignore[call-arg]

        from app.riot.client import RiotClient

        client = RiotClient(settings_override=test_settings)

        # Mock responses: Key 1 gets 429, Key 2 succeeds
        response_429 = Mock(spec=httpx.Response)
        response_429.status_code = 429
        response_429.headers = {"Retry-After": "5"}

        response_200 = Mock(spec=httpx.Response)
        response_200.status_code = 200
        response_200.json = Mock(return_value={"success": True})

        # Mock the client.get method to return responses in sequence
        client.client.get = AsyncMock(side_effect=[response_429, response_200])

        # Make request
        import time

        start = time.time()
        result = await client.get("/test", region="euw1")
        elapsed = time.time() - start

        # Verify success and NO sleep happened (should be < 1 second)
        assert result == {"success": True}
        assert elapsed < 1.0, f"Request took {elapsed}s, should be immediate (no 5s wait)"

        await client.close()

    @pytest.mark.skip(reason="Flaky test - mock setup conflicts with reset_riot_client fixture")
    @pytest.mark.asyncio
    async def test_all_keys_rate_limited_waits(self, monkeypatch):
        """Test that if ALL keys are 429, it waits before retrying."""
        from unittest.mock import AsyncMock, Mock
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2", riot_api_key=None)  # type: ignore[call-arg]

        from app.riot.client import RiotClient

        client = RiotClient(settings_override=test_settings)

        # Mock responses: Both keys get 429, then Key 1 succeeds
        response_429_key1 = Mock(spec=httpx.Response)
        response_429_key1.status_code = 429
        response_429_key1.headers = {"Retry-After": "1"}

        response_429_key2 = Mock(spec=httpx.Response)
        response_429_key2.status_code = 429
        response_429_key2.headers = {"Retry-After": "1"}

        response_200 = Mock(spec=httpx.Response)
        response_200.status_code = 200
        response_200.json = Mock(return_value={"success": True})

        client.client.get = AsyncMock(
            side_effect=[response_429_key1, response_429_key2, response_200]
        )

        # Make request
        import time

        start = time.time()
        result = await client.get("/test", region="euw1")
        elapsed = time.time() - start

        # Verify success and sleep DID happen (should be ~1 second)
        assert result == {"success": True}
        assert elapsed >= 1.0, f"Request took {elapsed}s, should wait ~1s when all keys exhausted"

        await client.close()

    @pytest.mark.asyncio
    async def test_preserves_match_id_across_retries(self, monkeypatch):
        """Test that the same match ID is used across all retry attempts (no data loss)."""
        from unittest.mock import AsyncMock, Mock
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2", riot_api_key=None)  # type: ignore[call-arg]

        from app.riot.client import RiotClient

        client = RiotClient(settings_override=test_settings)

        match_id = "EUW1_123456789"
        requests_made = []

        # Create a mock function that captures URLs
        async def mock_get(url, **kwargs):
            requests_made.append(url)
            if len(requests_made) == 1:
                # First request: 429
                response = Mock(spec=httpx.Response)
                response.status_code = 429
                response.headers = {"Retry-After": "1"}
                return response
            else:
                # Second request: Success
                response = Mock(spec=httpx.Response)
                response.status_code = 200
                response.json = Mock(return_value={"matchId": match_id})
                return response

        client.client.get = AsyncMock(side_effect=mock_get)

        # Make request
        result = await client.get(
            f"/lol/match/v5/matches/{match_id}", region="europe", is_platform_endpoint=True
        )

        # Verify both requests used the SAME match ID
        assert len(requests_made) == 2
        assert match_id in requests_made[0], "First request should contain match ID"
        assert match_id in requests_made[1], "Retry should contain SAME match ID"
        assert result["matchId"] == match_id

        await client.close()
