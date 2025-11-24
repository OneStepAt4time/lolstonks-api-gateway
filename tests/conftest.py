"""Pytest configuration and fixtures for testing."""

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
    """Provide the FastAPI application for testing."""
    return app


@pytest.fixture(scope="function")
def client(test_app) -> Generator[TestClient, None, None]:
    """Provide a synchronous test client."""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous test client."""
    from httpx import ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def mock_riot_response():
    """Provide mock responses for Riot API calls."""
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
    """
    Reset Riot API client for each test.

    This ensures the httpx.AsyncClient is recreated with a fresh state,
    preventing "RuntimeError: Event loop is closed" errors.
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
    """Reset cache between tests if needed."""
    # This fixture runs automatically before each test
    # Add cache reset logic here if needed
    yield
    # Cleanup after test
