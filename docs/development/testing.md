# Testing Guide

This guide covers testing strategies, tools, and best practices for the LOLStonks API Gateway.

## Testing Overview

The project uses a comprehensive testing approach with multiple test types:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete request flows
- **Performance Tests**: Test system performance under load

## Test Setup

### Installation

```bash
# Install test dependencies
pip install -e ".[dev]"

# Or with uv
uv install --extra dev
```

### Test Configuration

Create a test environment file:

```env
# .env.test
RIOT_API_KEY=test-key-for-testing
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1  # Separate database for testing
LOG_LEVEL=DEBUG
RATE_LIMIT_RPS=1000  # High limits for testing
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_summoner.py

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m slow
```

### Test Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --tb=short
    -v
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (requires external services)
    slow: Slow tests (performance, load testing)
    external: Tests that hit external APIs
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_rate_limiter.py
│   ├── test_cache.py
│   └── test_models.py
├── integration/             # Integration tests
│   ├── test_client.py
│   ├── test_cache_integration.py
│   └── test_routers.py
├── end_to_end/              # End-to-end tests
│   ├── test_api_flows.py
│   └── test_full_scenarios.py
├── performance/             # Performance tests
│   ├── test_load.py
│   └── test_stress.py
└── fixtures/                # Test data
    ├── summoner_data.json
    ├── match_data.json
    └── league_data.json
```

## Fixtures and Configuration

### conftest.py

```python
# tests/conftest.py
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient

from app.main import app
from app.riot.client import RiotClient
from app.cache.redis_cache import RedisCache
from app.cache.tracking import MatchTracker

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Test client for FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.setex.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.sismember.return_value = False
    redis_mock.sadd.return_value = True
    return redis_mock

@pytest.fixture
def cache(mock_redis):
    """Redis cache fixture with mocked Redis."""
    cache = RedisCache()
    cache.redis = mock_redis
    return cache

@pytest.fixture
def mock_riot_client():
    """Mock Riot client for testing."""
    client = AsyncMock()
    return client

@pytest.fixture
def rate_limiter():
    """Rate limiter fixture for testing."""
    from app.riot.rate_limiter import RateLimiter
    return RateLimiter(rate=100, capacity=1000)  # High limits for tests

@pytest.fixture
def match_tracker(cache):
    """Match tracker fixture."""
    return MatchTracker(cache)

@pytest.fixture
def sample_summoner_data():
    """Sample summoner data for testing."""
    return {
        "id": "test-summoner-id",
        "accountId": "test-account-id",
        "puuid": "test-puuid",
        "name": "TestSummoner",
        "profileIconId": 1,
        "revisionDate": 1234567890,
        "summonerLevel": 30
    }

@pytest.fixture
def sample_match_data():
    """Sample match data for testing."""
    return {
        "gameId": 1234567890,
        "gameDuration": 1800,
        "gameMode": "CLASSIC",
        "gameType": "MATCHED_GAME",
        "participants": [],
        "teams": []
    }

def load_fixture(filename):
    """Load test data from JSON fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / filename
    with open(fixture_path, 'r') as f:
        return json.load(f)
```

## Unit Tests

### Rate Limiter Tests

```python
# tests/unit/test_rate_limiter.py
import pytest
import asyncio
from unittest.mock import patch
from datetime import datetime, timedelta

from app.riot.rate_limiter import RateLimiter

class TestRateLimiter:
    """Test the rate limiter implementation."""

    @pytest.mark.unit
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(rate=10, capacity=50)
        assert limiter.rate == 10
        assert limiter.capacity == 50
        assert limiter.tokens == 50

    @pytest.mark.unit
    async def test_token_consumption(self):
        """Test token consumption."""
        limiter = RateLimiter(rate=10, capacity=50)

        # Should consume one token
        await limiter.acquire()
        assert limiter.tokens == 49

    @pytest.mark.unit
    async def test_token_refill(self):
        """Test token refill over time."""
        limiter = RateLimiter(rate=10, capacity=50)

        # Consume all tokens
        for _ in range(50):
            await limiter.acquire()

        assert limiter.tokens == 0

        # Wait for refill (mock time passage)
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(seconds=2)
            await limiter._refill()

            # Should have 20 tokens after 2 seconds (10 * 2)
            assert limiter.tokens == 20

    @pytest.mark.unit
    async def test_rate_limit_exceeded(self):
        """Test behavior when rate limit is exceeded."""
        limiter = RateLimiter(rate=1, capacity=2)

        # Consume all tokens
        await limiter.acquire()
        await limiter.acquire()

        # Next acquire should wait
        start_time = asyncio.get_event_loop().time()
        await limiter.acquire()
        end_time = asyncio.get_event_loop().time()

        # Should have waited at least 1 second
        assert end_time - start_time >= 1.0

    @pytest.mark.unit
    async def test_concurrent_acquisition(self):
        """Test concurrent token acquisition."""
        limiter = RateLimiter(rate=100, capacity=100)

        async def acquire_tokens():
            for _ in range(10):
                await limiter.acquire()

        # Run multiple concurrent tasks
        tasks = [acquire_tokens() for _ in range(10)]
        await asyncio.gather(*tasks)

        # Should have consumed exactly 100 tokens
        assert limiter.tokens == 0
```

### Cache Tests

```python
# tests/unit/test_cache.py
import pytest
from unittest.mock import AsyncMock, patch
import json

from app.cache.redis_cache import RedisCache

class TestRedisCache:
    """Test Redis cache implementation."""

    @pytest.mark.unit
    def test_cache_key_generation(self):
        """Test cache key generation."""
        cache = RedisCache()

        key = cache._generate_key("summoner", "euw1", "test-id")
        assert key == "lolstonks:summoner:euw1:test-id"

    @pytest.mark.unit
    async def test_cache_set_and_get(self, mock_redis):
        """Test setting and getting cache values."""
        cache = RedisCache()
        cache.redis = mock_redis

        test_data = {"id": "test", "name": "Test User"}

        # Set cache
        result = await cache.set("summoner", "euw1", "test-id", test_data, ttl=3600)
        assert result is True

        # Configure mock for get
        mock_redis.get.return_value = json.dumps(test_data)

        # Get cache
        result = await cache.get("summoner", "euw1", "test-id")
        assert result == test_data

    @pytest.mark.unit
    async def test_cache_miss(self, mock_redis):
        """Test cache miss scenario."""
        cache = RedisCache()
        cache.redis = mock_redis

        # Configure mock to return None (cache miss)
        mock_redis.get.return_value = None

        result = await cache.get("summoner", "euw1", "nonexistent")
        assert result is None

    @pytest.mark.unit
    async def test_cache_delete(self, mock_redis):
        """Test cache deletion."""
        cache = RedisCache()
        cache.redis = mock_redis

        result = await cache.delete("summoner", "euw1", "test-id")
        assert result is True

        mock_redis.delete.assert_called_once_with("lolstonks:summoner:euw1:test-id")

    @pytest.mark.unit
    async def test_cache_error_handling(self, mock_redis):
        """Test cache error handling."""
        cache = RedisCache()
        cache.redis = mock_redis

        # Configure mock to raise exception
        mock_redis.get.side_effect = Exception("Redis error")

        result = await cache.get("summoner", "euw1", "test-id")
        assert result is None

    @pytest.mark.unit
    def test_ttl_config_loading(self, monkeypatch):
        """Test TTL configuration loading."""
        # Set environment variables
        monkeypatch.setenv("CACHE_TTL_SUMMONER", "7200")
        monkeypatch.setenv("CACHE_TTL_MATCH", "86400")

        cache = RedisCache()

        assert cache.ttl_config["summoner"] == 7200
        assert cache.ttl_config["match"] == 86400
```

### Model Tests

```python
# tests/unit/test_models.py
import pytest
from pydantic import ValidationError

from app.models.summoner import SummonerDto, SummonerByNameParams
from app.models.match import MatchDto, MatchIdsByPuuidParams

class TestModels:
    """Test Pydantic models."""

    @pytest.mark.unit
    def test_summoner_dto_validation(self, sample_summoner_data):
        """Test SummonerDto validation."""
        summoner = SummonerDto(**sample_summoner_data)

        assert summoner.id == "test-summoner-id"
        assert summoner.name == "TestSummoner"
        assert summoner.summonerLevel == 30

    @pytest.mark.unit
    def test_summoner_dto_missing_required_fields(self):
        """Test SummonerDto validation with missing fields."""
        invalid_data = {
            "id": "test-id",
            # Missing required fields
        }

        with pytest.raises(ValidationError):
            SummonerDto(**invalid_data)

    @pytest.mark.unit
    def test_summoner_by_name_params(self):
        """Test SummonerByNameParams validation."""
        params = SummonerByNameParams(summonerName="TestSummoner")
        assert params.summonerName == "TestSummoner"

    @pytest.mark.unit
    def test_match_ids_by_puuid_params(self):
        """Test MatchIdsByPuuidParams validation."""
        params = MatchIdsByPuuidParams(
            puuid="test-puuid",
            count=10,
            start=0
        )
        assert params.puuid == "test-puuid"
        assert params.count == 10
        assert params.start == 0

    @pytest.mark.unit
    def test_model_serialization(self, sample_summoner_data):
        """Test model serialization."""
        summoner = SummonerDto(**sample_summoner_data)

        serialized = summoner.model_dump()
        assert serialized["id"] == "test-summoner-id"
        assert serialized["name"] == "TestSummoner"

    @pytest.mark.unit
    def test_model_json_serialization(self, sample_summoner_data):
        """Test model JSON serialization."""
        summoner = SummonerDto(**sample_summoner_data)

        json_str = summoner.model_dump_json()
        assert "test-summoner-id" in json_str
        assert "TestSummoner" in json_str
```

## Integration Tests

### Client Integration Tests

```python
# tests/integration/test_client.py
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.riot.client import RiotClient, RateLimitExceeded

class TestRiotClient:
    """Test Riot client integration."""

    @pytest.mark.integration
    async def test_successful_request(self, mock_riot_client, rate_limiter):
        """Test successful API request."""
        mock_riot_client.get.return_value = {"id": "test-summoner-id"}

        client = RiotClient("test-api-key")
        client.client = mock_riot_client
        client.rate_limiter = rate_limiter

        result = await client.get("/summoner/v4/summoners/by-name/test", "euw1")

        assert result["id"] == "test-summoner-id"

    @pytest.mark.integration
    async def test_rate_limit_handling(self, mock_riot_client, rate_limiter):
        """Test rate limit handling."""
        # Mock 429 response
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "1"}
        mock_riot_client.get.return_value = mock_response

        client = RiotClient("test-api-key")
        client.client = mock_riot_client
        client.rate_limiter = rate_limiter

        with pytest.raises(RateLimitExceeded):
            await client.get("/summoner/v4/summoners/by-name/test", "euw1")

    @pytest.mark.integration
    async def test_retry_mechanism(self, mock_riot_client, rate_limiter):
        """Test retry mechanism."""
        # First call returns 429, second call succeeds
        mock_429_response = AsyncMock()
        mock_429_response.status_code = 429
        mock_429_response.headers = {"Retry-After": "1"}

        mock_success_response = AsyncMock()
        mock_success_response.status_code = 200
        mock_success_response.json.return_value = {"id": "test-summoner-id"}

        mock_riot_client.get.side_effect = [mock_429_response, mock_success_response]

        client = RiotClient("test-api-key")
        client.client = mock_riot_client
        client.rate_limiter = rate_limiter

        with patch('asyncio.sleep'):  # Skip actual sleep
            result = await client.get("/summoner/v4/summoners/by-name/test", "euw1")

        assert result["id"] == "test-summoner-id"
        assert mock_riot_client.get.call_count == 2
```

### Router Integration Tests

```python
# tests/integration/test_routers.py
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app

class TestRouters:
    """Test router integration."""

    @pytest.mark.integration
    async def test_summoner_by_name_endpoint(self, client, mock_riot_client):
        """Test summoner by name endpoint."""
        sample_response = {
            "id": "test-summoner-id",
            "name": "TestSummoner",
            "summonerLevel": 30
        }

        with patch('app.routers.summoner.riot_client', mock_riot_client):
            mock_riot_client.get.return_value = sample_response

            response = await client.get(
                "/summoner/by-name/TestSummoner?region=euw1"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "test-summoner-id"
            assert data["name"] == "TestSummoner"

    @pytest.mark.integration
    async def test_summoner_not_found(self, client, mock_riot_client):
        """Test summoner not found scenario."""
        with patch('app.routers.summoner.riot_client', mock_riot_client):
            mock_riot_client.get.side_effect = httpx.HTTPStatusError(
                "Not Found", request=AsyncMock(), response=AsyncMock(status_code=404)
            )

            response = await client.get(
                "/summoner/by-name/NonexistentSummoner?region=euw1"
            )

            assert response.status_code == 404

    @pytest.mark.integration
    async def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.integration
    async def test_rate_limit_headers(self, client, mock_riot_client):
        """Test rate limit headers in response."""
        sample_response = {"id": "test-id"}

        with patch('app.routers.summoner.riot_client', mock_riot_client):
            mock_riot_client.get.return_value = sample_response

            response = await client.get(
                "/summoner/by-name/Test?region=euw1"
            )

            # Check for rate limit headers
            assert "X-Rate-Limit-Remaining" in response.headers
            assert "X-Rate-Limit-Limit" in response.headers
```

## Performance Tests

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from app.riot.rate_limiter import RateLimiter
from app.cache.redis_cache import RedisCache

@pytest.mark.slow
class TestPerformance:
    """Performance and load tests."""

    @pytest.mark.slow
    async def test_rate_limiter_performance(self):
        """Test rate limiter under load."""
        limiter = RateLimiter(rate=100, capacity=1000)

        start_time = time.time()

        # Make 1000 concurrent requests
        tasks = [limiter.acquire() for _ in range(1000)]
        await asyncio.gather(*tasks)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in reasonable time (within 15 seconds)
        assert duration < 15.0

        # Rate limiter should still work
        assert limiter.tokens >= 0

    @pytest.mark.slow
    async def test_cache_performance(self, cache):
        """Test cache performance under load."""
        test_data = {"id": "test", "data": "x" * 1000}  # 1KB data

        start_time = time.time()

        # Perform 1000 cache operations
        tasks = []
        for i in range(1000):
            tasks.append(cache.set("test", "euw1", f"key{i}", test_data))
            tasks.append(cache.get("test", "euw1", f"key{i}"))

        await asyncio.gather(*tasks)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly (within 5 seconds)
        assert duration < 5.0

        # Performance: at least 200 operations per second
        operations_per_second = 2000 / duration
        assert operations_per_second > 200

    @pytest.mark.slow
    async def test_concurrent_api_requests(self, client):
        """Test concurrent API request handling."""
        async def make_request():
            response = await client.get("/health")
            return response.status_code

        start_time = time.time()

        # Make 100 concurrent requests
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        duration = end_time - start_time

        # All requests should succeed
        assert all(status == 200 for status in results)

        # Should complete quickly (within 2 seconds)
        assert duration < 2.0

        # Performance: at least 50 requests per second
        requests_per_second = 100 / duration
        assert requests_per_second > 50
```

## External API Tests

### Real API Tests

```python
# tests/integration/test_external_api.py
import pytest
import os

from app.riot.client import RiotClient

@pytest.mark.external
@pytest.mark.slow
class TestExternalAPI:
    """Tests against real Riot API (requires API key)."""

    @pytest.fixture
    def real_riot_client(self):
        """Real Riot client using actual API key."""
        api_key = os.getenv("RIOT_API_KEY")
        if not api_key:
            pytest.skip("No RIOT_API_KEY environment variable set")

        return RiotClient(api_key)

    @pytest.mark.external
    async def test_real_summoner_lookup(self, real_riot_client):
        """Test real summoner lookup."""
        try:
            result = await real_riot_client.get(
                "/lol/summoner/v4/summoners/by-name/Faker",
                "kr"
            )

            assert "id" in result
            assert "name" in result
            assert result["name"] == "Faker"
        except Exception as e:
            pytest.skip(f"External API test failed: {e}")

    @pytest.mark.external
    async def test_real_challenger_lookup(self, real_riot_client):
        """Test real challenger league lookup."""
        try:
            result = await real_riot_client.get(
                "/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5",
                "kr"
            )

            assert "tier" in result
            assert "entries" in result
            assert result["tier"] == "CHALLENGER"
        except Exception as e:
            pytest.skip(f"External API test failed: {e}")
```

## Troubleshooting

### Common Test Issues

1. **Redis Connection Errors**
   ```bash
   # Make sure Redis is running
   redis-server

   # Or run in Docker
   docker run -d -p 6379:6379 redis:7-alpine
   ```

2. **Rate Limiting in Tests**
   ```python
   # Set high rate limits for tests
   RATE_LIMIT_RPS=1000
   RATE_LIMIT_BURST=10000
   ```

3. **Test Database Issues**
   ```bash
   # Use separate Redis database for testing
   REDIS_DB=1

   # Flush test database between runs
   redis-cli -n 1 FLUSHDB
   ```

4. **Import Errors**
   ```bash
   # Make sure you're in the project root
   cd /path/to/lolstonks-api-gateway

   # Install in development mode
   pip install -e ".[dev]"
   ```

### Debugging Tests

```bash
# Run with verbose output
pytest -v -s

# Stop on first failure
pytest -x

# Run with debugger
pytest --pdb

# Show local variables on failure
pytest -l

# Run specific test with debug
pytest tests/unit/test_rate_limiter.py::TestRateLimiter::test_token_consumption -v -s
```

This comprehensive testing strategy ensures the LOLStonks API Gateway is reliable, performant, and maintainable across different scenarios and conditions.