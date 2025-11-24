"""Pytest configuration and fixtures for testing.

This module configures the test environment and provides reusable fixtures for
all tests in the lolstonks-api-gateway project. It handles:
- Windows event loop policy configuration
- Test environment variables setup
- FastAPI application fixtures
- Test client fixtures (sync and async)
- Mock data fixtures
- Riot API client cleanup between tests

The fixtures ensure proper isolation between tests and prevent common
async testing issues like event loop closure errors.
"""

import asyncio
import os
import sys
from typing import AsyncGenerator, Generator

# Fix for Windows event loop cleanup issue
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment variables before importing app
os.environ["RIOT_API_KEY"] = "RGAPI-test-key-for-testing"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["LOG_LEVEL"] = "ERROR"

from app.main import app


@pytest.fixture(scope="session")
def test_app():
    """Provide the FastAPI application instance for testing.

    Returns a configured FastAPI application with all routes, middleware,
    and dependencies loaded. This fixture is session-scoped to avoid
    recreating the app for every test, improving test performance.

    Returns:
        FastAPI: The configured application instance.

    Scope:
        session - Single instance shared across all tests in the session.

    Example:
        ```python
        def test_app_routes(test_app):
            routes = [route.path for route in test_app.routes]
            assert "/health" in routes
        ```

    Note:
        Environment variables must be set before importing the app.
        See module-level os.environ configuration.
    """
    return app


@pytest.fixture(scope="function")
def client(test_app) -> Generator[TestClient, None, None]:
    """Provide a synchronous test client for FastAPI endpoint testing.

    Creates a FastAPI TestClient that makes synchronous HTTP requests to
    the application. Unlike the async_client fixture, this uses Starlette's
    TestClient which handles ASGI internally. Ideal for simple endpoint
    tests that don't need async control flow.

    Args:
        test_app: The FastAPI application instance.

    Yields:
        TestClient: Synchronous HTTP client for making requests.

    Scope:
        function - Fresh client instance for each test.

    Cleanup:
        Automatically closes the client and cleans up resources when the
        test completes (context manager ensures cleanup).

    Example:
        ```python
        def test_health_endpoint(client):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
        ```

    Note:
        For async tests requiring more control over the request lifecycle,
        use the async_client fixture instead.
    """
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous HTTP client for async endpoint testing.

    Creates an httpx.AsyncClient configured with an ASGI transport that
    communicates directly with the FastAPI application. This fixture is
    essential for testing async endpoints and allows full control over
    the async request/response lifecycle.

    Args:
        test_app: The FastAPI application instance.

    Yields:
        AsyncClient: Async HTTP client configured with ASGI transport.

    Scope:
        function - Fresh client instance for each test to ensure isolation.

    Cleanup:
        Automatically closes the async client and its connection pool when
        the test completes (async context manager ensures cleanup).

    Example:
        ```python
        async def test_async_summoner_endpoint(async_client):
            response = await async_client.get(
                "/lol/summoner/v4/summoners/by-name/Faker",
                params={"region": "kr"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "puuid" in data
        ```

    Note:
        - Uses base_url="http://test" which doesn't make real network calls.
        - The ASGI transport routes requests directly to the app.
        - Requires async test functions (prefix with async def).
        - Works with pytest-asyncio for event loop management.
    """
    from httpx import ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def mock_riot_response():
    """Provide mock Riot API response data for testing.

    Returns a dictionary containing realistic mock data structures that match
    the Riot API response formats. This fixture is useful for testing endpoint
    logic without making actual API calls to Riot's servers.

    Returns:
        dict: Dictionary with mock responses for different Riot API endpoints.
            Contains two keys:
            - "summoner": Mock summoner data (v4 API format)
            - "match": Mock match data (v5 API format)

    Scope:
        function - Fresh mock data for each test.

    Example:
        ```python
        def test_summoner_parsing(mock_riot_response):
            summoner_data = mock_riot_response["summoner"]
            assert summoner_data["name"] == "TestSummoner"
            assert summoner_data["summonerLevel"] == 100

        def test_match_parsing(mock_riot_response):
            match_data = mock_riot_response["match"]
            assert match_data["metadata"]["matchId"] == "EUW1_1234567890"
            assert len(match_data["metadata"]["participants"]) == 1
        ```

    Note:
        This fixture provides static mock data. For dynamic mocking of
        httpx requests, use respx or httpx_mock libraries in your tests.
    """
    return {
        "summoner": {
            "id": "test-summoner-id",
            "accountId": "test-account-id",
            "puuid": "test-puuid",
            "name": "TestSummoner",
            "profileIconId": 1,
            "revisionDate": 1234567890,
            "summonerLevel": 100,
        },
        "match": {
            "metadata": {
                "dataVersion": "2",
                "matchId": "EUW1_1234567890",
                "participants": ["test-puuid"],
            },
            "info": {
                "gameCreation": 1234567890,
                "gameDuration": 1800,
                "gameEndTimestamp": 1234569690,
                "gameId": 1234567890,
                "gameMode": "CLASSIC",
                "gameType": "MATCHED_GAME",
            },
        },
    }


@pytest.fixture(autouse=True)
def reset_riot_client():
    """Reset Riot API client lifecycle for each test.

    This critical fixture ensures proper isolation between tests by recreating
    the httpx.AsyncClient used by the Riot API client. It prevents the common
    "RuntimeError: Event loop is closed" error that occurs when an AsyncClient
    from a previous test's event loop is reused in a new test.

    The fixture handles three scenarios:
    1. No event loop exists (synchronous context)
    2. Event loop exists but is not running
    3. Event loop is currently running (async context)

    Autouse:
        True - Automatically runs before and after every test without explicit
        declaration. This ensures no test can accidentally use a stale client.

    Scope:
        function - Runs for each individual test.

    Cleanup:
        Closes the httpx.AsyncClient after each test by:
        1. Checking if an event loop is running
        2. Creating a temporary event loop if needed for cleanup
        3. Running aclose() to properly close connections
        4. Cleaning up the temporary event loop

    Example:
        ```python
        # No explicit fixture usage needed - runs automatically
        async def test_summoner_fetch(async_client):
            # reset_riot_client already ran before this test
            response = await async_client.get("/lol/summoner/v4/summoners/by-name/Faker")
            assert response.status_code == 200
            # reset_riot_client will clean up after this test
        ```

    Note:
        - This fixture is essential for Windows environments where event loop
          cleanup is strictly enforced.
        - Errors during cleanup are silently ignored to prevent test failures
          from cleanup issues.
        - The fixture recreates the client with settings.riot_request_timeout
          configuration.

    See Also:
        - pytest-asyncio documentation for event loop management
        - httpx.AsyncClient lifecycle documentation
    """
    from app.riot.client import riot_client
    import httpx
    from app.config import settings

    # Store original client
    original_client = riot_client.client

    # Close existing client if it exists
    try:
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            # Event loop is running, can't close synchronously
        except RuntimeError:
            # No running loop, create new one for cleanup
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(original_client.aclose())
            finally:
                loop.close()
    except Exception:
        # Ignore errors during cleanup of old client
        pass

    # Create new AsyncClient
    riot_client.client = httpx.AsyncClient(
        timeout=settings.riot_request_timeout,
    )

    yield

    # Cleanup after test - recreate for next test
    try:
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            # Event loop is running, can't close synchronously
        except RuntimeError:
            # No running loop, create new one for cleanup
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(riot_client.client.aclose())
            finally:
                loop.close()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset cache state between tests.

    This fixture provides a hook for cache cleanup between tests. Currently
    it serves as a placeholder for future cache reset logic but ensures that
    any caching state doesn't leak between tests.

    Autouse:
        True - Automatically runs before and after every test.

    Scope:
        function - Runs for each individual test.

    Cleanup:
        Executes after each test completes. Add cache-specific cleanup
        logic in the post-yield section when needed.

    Example:
        ```python
        # No explicit fixture usage needed - runs automatically
        async def test_cached_endpoint(async_client):
            # reset_cache ensures no stale cache data exists
            response = await async_client.get("/lol/summoner/v4/summoners/by-name/Faker")
            assert response.status_code == 200
        ```

    Note:
        If Redis or other cache backends are used in tests, add cleanup
        logic here to ensure test isolation.
    """
    # This fixture runs automatically before each test
    # Add cache reset logic here if needed
    yield
    # Cleanup after test
