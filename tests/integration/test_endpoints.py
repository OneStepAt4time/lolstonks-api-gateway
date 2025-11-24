"""Integration smoke tests for critical API endpoints.

These tests verify that endpoints are properly wired up and return
expected HTTP status codes. They use real routing logic without mocking.

Note: These are smoke tests, not functional tests. Detailed functionality
is covered by unit tests in tests/test_*.py files.
"""

import pytest
from httpx import AsyncClient


# ============================================================================
# HEALTH CHECK
# ============================================================================


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    """Test health check endpoint is accessible."""
    response = await async_client.get("/health")
    assert response.status_code in [200, 503]  # OK or Service Unavailable


# ============================================================================
# ACCOUNT API SMOKE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_account_by_riot_id_validation(async_client: AsyncClient):
    """Test account endpoint validates region parameter."""
    response = await async_client.get(
        "/riot/account/v1/accounts/by-riot-id/TestPlayer/EUW?region=invalid_region"
    )
    assert response.status_code in [400, 422]  # Validation error


@pytest.mark.asyncio
async def test_account_by_puuid_validation(async_client: AsyncClient):
    """Test account by PUUID endpoint validates region parameter."""
    response = await async_client.get(
        "/riot/account/v1/accounts/by-puuid/test-puuid?region=invalid_region"
    )
    assert response.status_code in [400, 422]  # Validation error


# ============================================================================
# SUMMONER API SMOKE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_summoner_by_puuid_validation(async_client: AsyncClient):
    """Test summoner endpoint validates region parameter."""
    response = await async_client.get(
        "/lol/summoner/v4/summoners/by-puuid/test-puuid?region=invalid_region"
    )
    assert response.status_code in [400, 422]  # Validation error


# ============================================================================
# CHAMPION MASTERY SMOKE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_champion_mastery_validation(async_client: AsyncClient):
    """Test champion mastery endpoint validates parameters."""
    response = await async_client.get(
        "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/by-champion/999999?region=euw1"
    )
    # Should either validate or attempt to call API (which will fail without real key)
    assert response.status_code in [400, 401, 403, 422, 500]


# ============================================================================
# MATCH API SMOKE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_match_by_id_validation(async_client: AsyncClient):
    """Test match endpoint validates region parameter."""
    response = await async_client.get("/lol/match/v5/matches/EUW1_123456?region=invalid_region")
    assert response.status_code in [400, 422]  # Validation error


# ============================================================================
# LEAGUE API SMOKE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_league_entries_validation(async_client: AsyncClient):
    """Test league entries endpoint validates tier/division."""
    response = await async_client.get("/lol/league/v4/entries/INVALID_QUEUE/GOLD/I?region=euw1")
    assert response.status_code in [400, 422, 500]  # Validation or Riot error


# ============================================================================
# CLASH API SMOKE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_clash_players_validation(async_client: AsyncClient):
    """Test clash players endpoint validates region."""
    response = await async_client.get(
        "/lol/clash/v1/players/by-puuid/test-puuid?region=invalid_region"
    )
    # May return validation error or attempt API call (which fails without real key)
    assert response.status_code in [400, 401, 403, 422, 500]


# ============================================================================
# SPECTATOR API SMOKE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_spectator_validation(async_client: AsyncClient):
    """Test spectator endpoint validates region."""
    response = await async_client.get(
        "/lol/spectator/v5/active-games/by-summoner/test-id?region=invalid_region"
    )
    assert response.status_code in [400, 422]  # Validation error
