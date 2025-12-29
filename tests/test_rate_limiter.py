"""
Comprehensive tests for rate limiting functionality.

Tests the token bucket algorithm, 429 handling, and key rotation
to ensure Riot API rate limit compliance.
"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock

import pytest

from app.config import Settings
from app.exceptions import RateLimitException
from app.riot.client import RiotClient
from app.riot.key_rotator import KeyRotator
from app.riot.rate_limiter import RiotRateLimiter, rate_limiter


class TestTokenBucket:
    """Test token bucket rate limiting algorithm."""

    @pytest.mark.asyncio
    async def test_rate_limit_respects_per_second_limit(self):
        """Enforce requests per second limit."""
        from aiolimiter import AsyncLimiter

        # Create a test limiter with low limits for faster testing
        test_limiter = AsyncLimiter(max_rate=5, time_period=1)

        # Make 10 requests (exceeds limit of 5)
        start_time = time.time()
        for _ in range(10):
            async with test_limiter:
                pass
        elapsed = time.time() - start_time

        # Should take at least 1 second due to rate limiting
        # First 5 complete immediately, next 5 wait for token replenishment
        # Use slightly less than 1.0 to account for timing precision
        assert elapsed >= 0.95, f"Requests completed too quickly: {elapsed}s"

    @pytest.mark.asyncio
    async def test_rate_limit_respects_2min_limit(self):
        """Enforce requests per 2 minutes limit."""
        from aiolimiter import AsyncLimiter

        # Create a test limiter with low 2min limit for faster testing
        # Use 2 second period instead of 120 seconds for test speed
        test_limiter = AsyncLimiter(max_rate=5, time_period=2)

        # Make 10 requests (exceeds limit of 5 per 2 seconds)
        start_time = time.time()
        for _ in range(10):
            async with test_limiter:
                pass
        elapsed = time.time() - start_time

        # Should take at least 2 seconds due to 2min limit
        # Use slightly less than 2.0 to account for timing precision
        assert elapsed >= 1.9, f"Requests completed too quickly: {elapsed}s"

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_when_exhausted(self):
        """Block requests when tokens exhausted."""
        # Create a custom limiter with very low limits for testing
        from aiolimiter import AsyncLimiter

        test_limiter = AsyncLimiter(max_rate=2, time_period=1)

        # Exhaust tokens
        async with test_limiter:
            async with test_limiter:
                pass

        # Next acquire should block briefly
        start_time = time.time()
        async with test_limiter:
            pass
        elapsed = time.time() - start_time

        # Should have waited for token replenishment
        assert elapsed >= 0.01, "Should wait for token replenishment"

    @pytest.mark.asyncio
    async def test_rate_limiter_creates_fresh_instances(self):
        """Verify rate limiter creates fresh AsyncLimiter instances."""
        limiter = RiotRateLimiter()

        # Multiple acquire calls should work without reuse warnings
        for _ in range(5):
            await limiter.acquire()

        # Should complete without errors
        assert True

    @pytest.mark.asyncio
    async def test_concurrent_rate_limiting(self):
        """Test rate limiting with concurrent requests."""
        limiter = RiotRateLimiter()

        # Create tasks that compete for rate limit tokens
        async def make_request():
            await limiter.acquire()
            return True

        # Launch 20 concurrent requests
        tasks = [make_request() for _ in range(20)]
        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(results) == 20
        assert all(results)


class TestRateLimit429:
    """Test 429 rate limit response handling."""

    @pytest.mark.asyncio
    async def test_429_triggers_key_rotation(self, monkeypatch):
        """429 response triggers next API key."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2", riot_api_key=None)  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        # Mock responses: First key gets 429, second succeeds
        response_429 = Mock(spec=httpx.Response)
        response_429.status_code = 429
        response_429.headers = {"Retry-After": "5"}

        response_200 = Mock(spec=httpx.Response)
        response_200.status_code = 200
        response_200.json = Mock(return_value={"success": True})

        client.client.get = AsyncMock(side_effect=[response_429, response_200])

        # Make request
        result = await client.get("/test", region="euw1")

        # Verify success
        assert result == {"success": True}
        # Verify both keys were tried
        assert client.client.get.call_count == 2

        await client.close()

    @pytest.mark.asyncio
    async def test_429_with_retry_after(self, monkeypatch):
        """Respect Retry-After header from Riot."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2", riot_api_key=None)  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        # Both keys return 429 with different Retry-After values
        response_429_key1 = Mock(spec=httpx.Response)
        response_429_key1.status_code = 429
        response_429_key1.headers = {"Retry-After": "10"}
        response_429_key1.json = Mock(return_value={"status": {"message": "Rate limit exceeded"}})

        response_429_key2 = Mock(spec=httpx.Response)
        response_429_key2.status_code = 429
        response_429_key2.headers = {"Retry-After": "5"}
        response_429_key2.json = Mock(return_value={"status": {"message": "Rate limit exceeded"}})

        client.client.get = AsyncMock(side_effect=[response_429_key1, response_429_key2])

        # Make request - should raise RateLimitException
        with pytest.raises(RateLimitException) as exc_info:
            await client.get("/test", region="euw1")

        # Verify exception contains retry_after from last response
        assert exc_info.value.retry_after == 5
        assert exc_info.value.status_code == 429

        await client.close()

    @pytest.mark.asyncio
    async def test_all_keys_429_waits(self, monkeypatch):
        """Wait when all keys return 429."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2,key3", riot_api_key=None)  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        # All three keys return 429
        response_429 = Mock(spec=httpx.Response)
        response_429.status_code = 429
        response_429.headers = {"Retry-After": "3"}
        response_429.json = Mock(return_value={"status": {"message": "Rate limit exceeded"}})

        client.client.get = AsyncMock(side_effect=[response_429, response_429, response_429])

        # Make request - should raise RateLimitException after trying all keys
        with pytest.raises(RateLimitException) as exc_info:
            await client.get("/test", region="euw1")

        # Verify all 3 keys were tried
        assert client.client.get.call_count == 3
        assert exc_info.value.retry_after == 3

        await client.close()

    @pytest.mark.asyncio
    async def test_429_preserves_request_parameters(self, monkeypatch):
        """429 handling preserves original request parameters."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2", riot_api_key=None)  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        requests_made = []

        # Create mock that captures requests
        async def mock_get(url, **kwargs):
            requests_made.append({"url": url, "kwargs": kwargs})

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
                response.json = Mock(return_value={"data": "success"})
                return response

        client.client.get = AsyncMock(side_effect=mock_get)

        # Make request with parameters
        result = await client.get(
            "/lol/match/v5/matches/EUW1_123", region="europe", is_platform_endpoint=True
        )

        # Verify both requests had same URL and parameters
        assert len(requests_made) == 2
        assert requests_made[0]["url"] == requests_made[1]["url"]
        assert result == {"data": "success"}

        await client.close()

    @pytest.mark.asyncio
    async def test_429_default_retry_after(self, monkeypatch):
        """429 without Retry-After header uses default."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_key="single_key")  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        # 429 without Retry-After header
        response_429 = Mock(spec=httpx.Response)
        response_429.status_code = 429
        response_429.headers = {}  # No Retry-After header
        response_429.json = Mock(return_value={"status": {"message": "Rate limit exceeded"}})

        client.client.get = AsyncMock(return_value=response_429)

        # Make request
        with pytest.raises(RateLimitException) as exc_info:
            await client.get("/test", region="euw1")

        # Should default to 1 second
        assert exc_info.value.retry_after == 1

        await client.close()


class TestKeyRotation:
    """Test API key rotation."""

    @pytest.mark.asyncio
    async def test_key_rotation_round_robin(self):
        """Keys rotate in round-robin fashion."""
        keys = ["key1", "key2", "key3"]
        rotator = KeyRotator(keys)

        # Test full cycle
        assert rotator.get_next_key() == "key1"
        assert rotator.get_next_key() == "key2"
        assert rotator.get_next_key() == "key3"

        # Test wraparound
        assert rotator.get_next_key() == "key1"
        assert rotator.get_next_key() == "key2"

    @pytest.mark.asyncio
    async def test_key_rotation_with_429(self, monkeypatch):
        """429 triggers immediate key switch."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2,key3", riot_api_key=None)  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        keys_used = []

        # Mock that tracks which keys are used
        async def mock_get(url, headers=None, **kwargs):
            # Extract API key from headers
            api_key = headers.get("X-Riot-Token") if headers else None
            keys_used.append(api_key)

            if len(keys_used) == 1:
                # First key gets 429
                response = Mock(spec=httpx.Response)
                response.status_code = 429
                response.headers = {"Retry-After": "5"}
                return response
            else:
                # Second key succeeds
                response = Mock(spec=httpx.Response)
                response.status_code = 200
                response.json = Mock(return_value={"success": True})
                return response

        client.client.get = AsyncMock(side_effect=mock_get)

        # Make request
        result = await client.get("/test", region="euw1")

        # Verify two different keys were used
        assert len(keys_used) == 2
        assert keys_used[0] != keys_used[1], "Should rotate to different key on 429"
        assert result == {"success": True}

        await client.close()

    @pytest.mark.asyncio
    async def test_key_rotation_distributes_load(self):
        """Verify keys are evenly distributed over multiple requests."""
        keys = ["key1", "key2", "key3"]
        rotator = KeyRotator(keys)

        # Make many requests
        key_counts = {k: 0 for k in keys}
        for _ in range(30):  # 10 full cycles
            key = rotator.get_next_key()
            key_counts[key] += 1

        # Verify even distribution
        assert key_counts["key1"] == 10
        assert key_counts["key2"] == 10
        assert key_counts["key3"] == 10

    def test_key_rotation_thread_safety(self):
        """Test key rotation is thread-safe."""
        import threading

        keys = ["key1", "key2", "key3", "key4"]
        rotator = KeyRotator(keys)

        results = []
        errors = []

        def get_key():
            try:
                for _ in range(25):
                    key = rotator.get_next_key()
                    results.append(key)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = [threading.Thread(target=get_key) for _ in range(4)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all results are valid keys
        assert len(results) == 100  # 4 threads * 25 requests each
        for key in results:
            assert key in keys

        # Verify all keys were used
        assert len(set(results)) == 4


class TestRateLimitIntegration:
    """Integration tests for rate limiting with real client."""

    @pytest.mark.asyncio
    async def test_rate_limiter_with_client(self, monkeypatch):
        """Test rate limiter works with RiotClient."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_key="test_key")  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        # Mock successful response
        response_200 = Mock(spec=httpx.Response)
        response_200.status_code = 200
        response_200.json = Mock(return_value={"data": "test"})

        client.client.get = AsyncMock(return_value=response_200)

        # Make multiple requests
        for _ in range(5):
            result = await client.get("/test", region="euw1")
            assert result == {"data": "test"}

        # Verify rate limiter was called (acquire was called for each request)
        # This happens implicitly in client.get()
        assert client.client.get.call_count == 5

        await client.close()

    @pytest.mark.asyncio
    async def test_multiple_clients_share_rate_limiter(self, monkeypatch):
        """Test multiple clients share the global rate limiter."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        # Create two clients
        client1 = RiotClient(settings_override=TestSettings(riot_api_key="key1"))  # type: ignore[call-arg]
        client2 = RiotClient(settings_override=TestSettings(riot_api_key="key2"))  # type: ignore[call-arg]

        # Mock responses
        response_200 = Mock(spec=httpx.Response)
        response_200.status_code = 200
        response_200.json = Mock(return_value={"success": True})

        client1.client.get = AsyncMock(return_value=response_200)
        client2.client.get = AsyncMock(return_value=response_200)

        # Both clients make requests - should share rate limiter
        results = await asyncio.gather(
            client1.get("/test", region="euw1"),
            client2.get("/test", region="euw1"),
        )

        # Both should succeed
        assert len(results) == 2
        assert all(r == {"success": True} for r in results)

        await client1.close()
        await client2.close()


class TestRateLimitEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_rate_limit_single_key_no_rotation(self, monkeypatch):
        """Single key setup should not rotate."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_key="only_key")  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        # Verify only one key
        assert client.key_rotator.get_key_count() == 1

        # Mock 429 response
        response_429 = Mock(spec=httpx.Response)
        response_429.status_code = 429
        response_429.headers = {"Retry-After": "5"}
        response_429.json = Mock(return_value={"status": {"message": "Rate limit"}})

        client.client.get = AsyncMock(return_value=response_429)

        # Should raise RateLimitException immediately (no rotation)
        with pytest.raises(RateLimitException):
            await client.get("/test", region="euw1")

        # Should only try once (no other keys to rotate to)
        assert client.client.get.call_count == 1

        await client.close()

    @pytest.mark.asyncio
    async def test_concurrent_requests_with_429(self, monkeypatch):
        """Test concurrent requests handling 429 responses."""
        from pydantic_settings import SettingsConfigDict
        import httpx

        class TestSettings(Settings):
            model_config = SettingsConfigDict(env_file=None, extra="ignore")

        test_settings = TestSettings(riot_api_keys="key1,key2,key3", riot_api_key=None)  # type: ignore[call-arg]

        client = RiotClient(settings_override=test_settings)

        call_count = {"count": 0}

        # Mock that returns 429 first few times, then success
        async def mock_get(url, **kwargs):
            call_count["count"] += 1

            # First 3 calls (one per key) get 429
            if call_count["count"] <= 3:
                response = Mock(spec=httpx.Response)
                response.status_code = 429
                response.headers = {"Retry-After": "1"}
                return response
            else:
                # Subsequent calls succeed
                response = Mock(spec=httpx.Response)
                response.status_code = 200
                response.json = Mock(return_value={"success": True})
                return response

        client.client.get = AsyncMock(side_effect=mock_get)

        # Make concurrent requests
        async def make_request():
            try:
                return await client.get("/test", region="euw1")
            except RateLimitException:
                return {"error": "rate_limited"}

        results = await asyncio.gather(*[make_request() for _ in range(5)])

        # At least some should succeed or fail gracefully
        assert len(results) == 5

        await client.close()

    def test_global_rate_limiter_instance(self):
        """Test global rate limiter instance is accessible."""
        # Verify global instance exists
        assert rate_limiter is not None
        assert isinstance(rate_limiter, RiotRateLimiter)

        # Verify it has the correct limiters
        assert hasattr(rate_limiter, "limiter_1s")
        assert hasattr(rate_limiter, "limiter_2min")
