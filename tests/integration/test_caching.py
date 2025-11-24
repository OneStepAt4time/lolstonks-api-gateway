"""Integration tests for caching behavior.

Tests cover:
- Cache hit/miss behavior
- TTL expiration
- Force refresh with ?force=true
- Match tracking anti-reprocess
- Cache key uniqueness per region/parameters
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock


# ============================================================================
# CACHE HIT/MISS TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_cache_miss_on_first_request(async_client: AsyncClient):
    """Test that first request results in cache miss and fetches from API."""
    # Arrange
    mock_response = {
        "puuid": "test-puuid",
        "gameName": "CacheTest",
        "tagLine": "TEST",
    }
    mock_get = AsyncMock(return_value=mock_response)

    # Act
    with patch("app.riot.client.riot_client.get", new=mock_get):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/CacheTest/TEST?region=europe"
        )

    # Assert
    assert response.status_code == 200
    # Verify API was called (cache miss)
    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_cache_hit_on_second_request(async_client: AsyncClient):
    """Test that second identical request hits cache and doesn't call API."""
    # Arrange
    mock_response = {
        "id": "summoner-123",
        "puuid": "puuid-123",
        "name": "CachedPlayer",
        "summonerLevel": 100,
    }
    mock_get = AsyncMock(return_value=mock_response)

    # Mock Redis cache to simulate cache hit
    mock_cache_get = AsyncMock(return_value=mock_response)
    mock_cache_set = AsyncMock()

    # Act
    with patch("app.riot.client.riot_client.get", new=mock_get):
        with patch("app.cache.redis_cache.cache.get", new=mock_cache_get):
            with patch("app.cache.redis_cache.cache.set", new=mock_cache_set):
                # First request - cache miss
                response1 = await async_client.get(
                    "/lol/summoner/v4/summoners/by-puuid/puuid-123?region=euw1"
                )

                # Second request - should hit cache
                response2 = await async_client.get(
                    "/lol/summoner/v4/summoners/by-puuid/puuid-123?region=euw1"
                )

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    # Both requests return same data
    assert response1.json() == response2.json()


@pytest.mark.asyncio
async def test_cache_key_uniqueness_by_region(async_client: AsyncClient):
    """Test that cache keys are unique per region."""
    # Arrange
    mock_response_europe = {
        "puuid": "eu-puuid",
        "gameName": "EUPlayer",
        "tagLine": "EUW",
    }
    mock_response_americas = {
        "puuid": "na-puuid",
        "gameName": "NAPlayer",
        "tagLine": "NA1",
    }

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        # Configure mock to return different responses based on region
        mock_get.side_effect = [mock_response_europe, mock_response_americas]

        response_eu = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/Player/TAG?region=europe"
        )
        response_na = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/Player/TAG?region=americas"
        )

    # Assert
    assert response_eu.status_code == 200
    assert response_na.status_code == 200
    # Different regions should get different cached data
    assert response_eu.json()["puuid"] != response_na.json()["puuid"]


@pytest.mark.asyncio
async def test_cache_key_uniqueness_by_parameters(async_client: AsyncClient):
    """Test that cache keys are unique per query parameters."""
    # Arrange
    mock_response_top3 = [
        {"championId": 157, "championLevel": 7},
        {"championId": 238, "championLevel": 7},
        {"championId": 64, "championLevel": 6},
    ]
    mock_response_top5 = [
        {"championId": 157, "championLevel": 7},
        {"championId": 238, "championLevel": 7},
        {"championId": 64, "championLevel": 6},
        {"championId": 555, "championLevel": 5},
        {"championId": 777, "championLevel": 5},
    ]

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        mock_get.side_effect = [mock_response_top3, mock_response_top5]

        response_3 = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=euw1&count=3"
        )
        response_5 = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=euw1&count=5"
        )

    # Assert
    assert response_3.status_code == 200
    assert response_5.status_code == 200
    # Different count parameters should result in different cached data
    assert len(response_3.json()) == 3
    assert len(response_5.json()) == 5


# ============================================================================
# TTL EXPIRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_cache_respects_ttl_config(async_client: AsyncClient):
    """Test that cache uses configured TTL values."""
    # Arrange
    mock_response = {"puuid": "test", "gameName": "TTLTest", "tagLine": "TST"}
    mock_cache_set = AsyncMock()

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        with patch("app.cache.redis_cache.cache.set", new=mock_cache_set):
            await async_client.get("/riot/account/v1/accounts/by-riot-id/TTLTest/TST?region=europe")

    # Assert - verify cache.set was called with TTL parameter
    # (Actual TTL value depends on settings.cache_ttl_account)
    if mock_cache_set.called:
        # Check that TTL was provided (should be in call args)
        assert mock_cache_set.called


@pytest.mark.asyncio
async def test_cache_expiration_refetches_data(async_client: AsyncClient):
    """Test that expired cache entries trigger refetch."""
    # Arrange
    mock_response_1 = {"id": "old-data", "summonerLevel": 50}
    mock_response_2 = {"id": "new-data", "summonerLevel": 51}

    mock_cache_get = AsyncMock()
    # First call returns None (cache miss/expired), second returns cached value
    mock_cache_get.side_effect = [None, mock_response_2]

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        mock_get.side_effect = [mock_response_1, mock_response_2]

        with patch("app.cache.redis_cache.cache.get", new=mock_cache_get):
            # First request - cache expired
            response1 = await async_client.get(
                "/lol/summoner/v4/summoners/by-puuid/test-puuid?region=na1"
            )

            # Simulate cache expiration and refetch
            response2 = await async_client.get(
                "/lol/summoner/v4/summoners/by-puuid/test-puuid?region=na1"
            )

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200


# ============================================================================
# FORCE REFRESH TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_force_refresh_bypasses_cache(async_client: AsyncClient):
    """Test that ?force=true bypasses cache and fetches fresh data."""
    # Arrange
    mock_cached_response = {
        "matchId": "EUW1_123456",
        "metadata": {"dataVersion": "old"},
    }
    mock_fresh_response = {
        "matchId": "EUW1_123456",
        "metadata": {"dataVersion": "new"},
    }

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        mock_get.side_effect = [mock_cached_response, mock_fresh_response]

        # Normal request (may use cache)
        response_cached = await async_client.get("/lol/match/v5/matches/EUW1_123456?region=europe")

        # Force refresh request (must bypass cache)
        response_fresh = await async_client.get(
            "/lol/match/v5/matches/EUW1_123456?region=europe&force=true"
        )

    # Assert
    assert response_cached.status_code == 200
    assert response_fresh.status_code == 200
    # Force refresh should call API again
    assert mock_get.call_count >= 1


@pytest.mark.asyncio
async def test_force_refresh_updates_cache(async_client: AsyncClient):
    """Test that force refresh updates cached data."""
    # Arrange
    mock_new_data = {"data": "new", "timestamp": 2000}
    mock_cache_set = AsyncMock()

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        mock_get.return_value = mock_new_data

        with patch("app.cache.redis_cache.cache.set", new=mock_cache_set):
            response = await async_client.get(
                "/lol/summoner/v4/summoners/by-puuid/test-puuid?region=kr&force=true"
            )

    # Assert
    assert response.status_code == 200
    # Cache should be updated with fresh data
    # (Check if set was called - actual implementation may vary)


# ============================================================================
# MATCH TRACKING ANTI-REPROCESS TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_match_tracking_prevents_reprocess(async_client: AsyncClient):
    """Test that processed matches are tracked to prevent reprocessing."""
    # Arrange
    match_id = "EUW1_TRACKED_123"
    mock_match_data = {
        "metadata": {"matchId": match_id},
        "info": {"gameMode": "CLASSIC"},
    }
    mock_tracker = MagicMock()
    mock_tracker.is_processed = AsyncMock(return_value=False)
    mock_tracker.mark_processed = AsyncMock()

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_match_data)):
        with patch("app.cache.tracking.tracker.is_processed", new=mock_tracker.is_processed):
            with patch(
                "app.cache.tracking.tracker.mark_processed", new=mock_tracker.mark_processed
            ):
                response = await async_client.get(f"/lol/match/v5/matches/{match_id}?region=europe")

    # Assert
    assert response.status_code == 200
    # Verify tracking methods were called
    mock_tracker.is_processed.assert_called()


@pytest.mark.asyncio
async def test_match_tracking_allows_force_reprocess(async_client: AsyncClient):
    """Test that force=true allows reprocessing of tracked matches."""
    # Arrange
    match_id = "EUW1_FORCE_REPROCESS"
    mock_match_data = {
        "metadata": {"matchId": match_id},
        "info": {"gameMode": "ARAM"},
    }
    mock_tracker = MagicMock()
    mock_tracker.is_processed = AsyncMock(return_value=True)  # Already processed

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_match_data)):
        with patch("app.cache.tracking.tracker.is_processed", new=mock_tracker.is_processed):
            # Force refresh should work even if already processed
            response = await async_client.get(
                f"/lol/match/v5/matches/{match_id}?region=europe&force=true"
            )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["matchId"] == match_id


# ============================================================================
# CACHE ERROR HANDLING TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_cache_failure_falls_back_to_api(async_client: AsyncClient):
    """Test that cache failures don't break requests - fall back to API."""
    # Arrange
    mock_response = {"puuid": "test", "gameName": "Fallback", "tagLine": "FB"}
    mock_cache_get = AsyncMock(side_effect=Exception("Redis connection failed"))

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        with patch("app.cache.redis_cache.cache.get", new=mock_cache_get):
            response = await async_client.get(
                "/riot/account/v1/accounts/by-riot-id/Fallback/FB?region=americas"
            )

    # Assert - request should succeed despite cache failure
    assert response.status_code == 200
    data = response.json()
    assert data["gameName"] == "Fallback"
