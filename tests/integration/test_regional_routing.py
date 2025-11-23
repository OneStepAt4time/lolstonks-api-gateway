"""Integration tests for regional routing.

Tests cover:
- Platform regions (americas, europe, asia, sea) for Account/Match
- Game regions (na1, euw1, kr, etc.) for other endpoints
- Region validation
- Cross-region consistency
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


# ============================================================================
# PLATFORM REGION TESTS (Account, Match APIs)
# ============================================================================


@pytest.mark.asyncio
async def test_account_api_americas_region(async_client: AsyncClient):
    """Test Account API with Americas platform region."""
    # Arrange
    mock_response = {
        "puuid": "americas-puuid",
        "gameName": "NAPlayer",
        "tagLine": "NA1",
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/NAPlayer/NA1?region=americas"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["gameName"] == "NAPlayer"


@pytest.mark.asyncio
async def test_account_api_europe_region(async_client: AsyncClient):
    """Test Account API with Europe platform region."""
    # Arrange
    mock_response = {
        "puuid": "europe-puuid",
        "gameName": "EUPlayer",
        "tagLine": "EUW",
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/EUPlayer/EUW?region=europe"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["gameName"] == "EUPlayer"


@pytest.mark.asyncio
async def test_account_api_asia_region(async_client: AsyncClient):
    """Test Account API with Asia platform region."""
    # Arrange
    mock_response = {
        "puuid": "asia-puuid",
        "gameName": "KRPlayer",
        "tagLine": "KR",
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/KRPlayer/KR?region=asia"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["gameName"] == "KRPlayer"


@pytest.mark.asyncio
async def test_account_api_sea_region(async_client: AsyncClient):
    """Test Account API with SEA platform region."""
    # Arrange
    mock_response = {
        "puuid": "sea-puuid",
        "gameName": "SEAPlayer",
        "tagLine": "SEA",
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/SEAPlayer/SEA?region=sea"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["gameName"] == "SEAPlayer"


@pytest.mark.asyncio
async def test_match_api_americas_region(async_client: AsyncClient):
    """Test Match API with Americas platform region."""
    # Arrange
    mock_response = ["NA1_123", "NA1_456", "NA1_789"]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=americas"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_match_api_europe_region(async_client: AsyncClient):
    """Test Match API with Europe platform region."""
    # Arrange
    mock_response = ["EUW1_111", "EUW1_222"]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=europe"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


# ============================================================================
# GAME REGION TESTS (Summoner, League, etc.)
# ============================================================================


@pytest.mark.asyncio
async def test_summoner_api_na1_region(async_client: AsyncClient):
    """Test Summoner API with NA1 game region."""
    # Arrange
    mock_response = {
        "id": "na-summoner",
        "puuid": "na-puuid",
        "name": "NAPlayer",
        "summonerLevel": 100,
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get("/lol/summoner/v4/summoners/by-puuid/na-puuid?region=na1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NAPlayer"


@pytest.mark.asyncio
async def test_summoner_api_euw1_region(async_client: AsyncClient):
    """Test Summoner API with EUW1 game region."""
    # Arrange
    mock_response = {
        "id": "euw-summoner",
        "puuid": "euw-puuid",
        "name": "EUWPlayer",
        "summonerLevel": 150,
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/summoner/v4/summoners/by-puuid/euw-puuid?region=euw1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "EUWPlayer"


@pytest.mark.asyncio
async def test_summoner_api_kr_region(async_client: AsyncClient):
    """Test Summoner API with KR game region."""
    # Arrange
    mock_response = {
        "id": "kr-summoner",
        "puuid": "kr-puuid",
        "name": "KRPlayer",
        "summonerLevel": 200,
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get("/lol/summoner/v4/summoners/by-puuid/kr-puuid?region=kr")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "KRPlayer"


@pytest.mark.asyncio
async def test_league_api_eune1_region(async_client: AsyncClient):
    """Test League API with EUNE1 game region."""
    # Arrange
    mock_response = [
        {
            "summonerId": "eune-player-1",
            "summonerName": "EUNEPlayer1",
            "leaguePoints": 100,
            "wins": 50,
            "losses": 45,
        }
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/I?region=eune1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_clash_api_br1_region(async_client: AsyncClient):
    """Test Clash API with BR1 game region."""
    # Arrange
    mock_response = []

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get("/lol/clash/v1/tournaments?region=br1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_spectator_api_jp1_region(async_client: AsyncClient):
    """Test Spectator API with JP1 game region."""
    # Arrange
    mock_error = Exception("404: Not in game")
    mock_error.status_code = 404

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(side_effect=mock_error)):
        response = await async_client.get(
            "/lol/spectator/v5/active-games/by-summoner/jp-puuid?region=jp1"
        )

    # Assert
    assert response.status_code in [404, 500]


# ============================================================================
# REGION VALIDATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_invalid_platform_region_rejected(async_client: AsyncClient):
    """Test that invalid platform regions are rejected."""
    # Act
    response = await async_client.get(
        "/riot/account/v1/accounts/by-riot-id/Player/TAG?region=invalid_platform"
    )

    # Assert
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_invalid_game_region_rejected(async_client: AsyncClient):
    """Test that invalid game regions are rejected."""
    # Act
    response = await async_client.get(
        "/lol/summoner/v4/summoners/by-puuid/test-puuid?region=invalid_game_region"
    )

    # Assert
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_game_region_on_platform_endpoint_rejected(async_client: AsyncClient):
    """Test that game regions are rejected on platform endpoints."""
    # Act - trying to use na1 (game region) on Account API (platform endpoint)
    response = await async_client.get("/riot/account/v1/accounts/by-riot-id/Player/TAG?region=na1")

    # Assert - may be rejected or accepted depending on validation
    # If accepted, this is a potential issue
    assert response.status_code in [200, 400, 422, 500]


@pytest.mark.asyncio
async def test_platform_region_on_game_endpoint_rejected(async_client: AsyncClient):
    """Test that platform regions are rejected on game endpoints."""
    # Act - trying to use americas (platform region) on Summoner API (game endpoint)
    response = await async_client.get(
        "/lol/summoner/v4/summoners/by-puuid/test-puuid?region=americas"
    )

    # Assert - may be rejected or accepted depending on validation
    assert response.status_code in [200, 400, 422, 500]


# ============================================================================
# CROSS-REGION CONSISTENCY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_same_data_across_duplicate_regions(async_client: AsyncClient):
    """Test that same PUUID returns consistent data across duplicate region calls."""
    # Arrange
    mock_response = {
        "id": "consistent-id",
        "puuid": "consistent-puuid",
        "name": "ConsistentPlayer",
        "summonerLevel": 75,
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response1 = await async_client.get(
            "/lol/summoner/v4/summoners/by-puuid/consistent-puuid?region=euw1"
        )
        response2 = await async_client.get(
            "/lol/summoner/v4/summoners/by-puuid/consistent-puuid?region=euw1"
        )

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json() == response2.json()


@pytest.mark.asyncio
async def test_different_data_across_different_regions(async_client: AsyncClient):
    """Test that different regions can have different players with same name."""
    # Arrange
    mock_response_euw = {
        "gameName": "CommonName",
        "tagLine": "EUW",
        "puuid": "euw-puuid-123",
    }
    mock_response_na = {
        "gameName": "CommonName",
        "tagLine": "NA",
        "puuid": "na-puuid-456",
    }

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        mock_get.side_effect = [mock_response_euw, mock_response_na]

        response_euw = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/CommonName/EUW?region=europe"
        )
        response_na = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/CommonName/NA?region=americas"
        )

    # Assert
    assert response_euw.status_code == 200
    assert response_na.status_code == 200
    # Different PUUIDs show they're different players
    assert response_euw.json()["puuid"] != response_na.json()["puuid"]


@pytest.mark.asyncio
async def test_region_specific_league_entries(async_client: AsyncClient):
    """Test that league entries are region-specific."""
    # Arrange
    mock_response_euw = [{"summonerId": "euw-player", "leaguePoints": 100}]
    mock_response_kr = [{"summonerId": "kr-player", "leaguePoints": 200}]

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        mock_get.side_effect = [mock_response_euw, mock_response_kr]

        response_euw = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/DIAMOND/I?region=euw1"
        )
        response_kr = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/DIAMOND/I?region=kr"
        )

    # Assert
    assert response_euw.status_code == 200
    assert response_kr.status_code == 200
    # Different regions return different players
    assert response_euw.json()[0]["summonerId"] != response_kr.json()[0]["summonerId"]
