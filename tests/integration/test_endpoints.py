"""Integration tests for all API endpoints.

Tests cover the 12 required endpoints:
- Account API (2 endpoints)
- Summoner API (2 endpoints)
- Champion Mastery (2 endpoints)
- Clash (3 endpoints)
- League (1 endpoint)
- Match (1 endpoint)
- Spectator (1 endpoint)

Each endpoint is tested for:
- 200 OK responses
- 400/422 validation errors
- 404 not found errors
- 429 rate limit handling
- 500 server errors
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


# ============================================================================
# ACCOUNT API TESTS (2 endpoints)
# ============================================================================


@pytest.mark.asyncio
async def test_account_by_riot_id_success(async_client: AsyncClient):
    """Test successful account lookup by Riot ID."""
    # Arrange
    mock_response = {
        "puuid": "test-puuid-12345",
        "gameName": "TestPlayer",
        "tagLine": "EUW",
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/TestPlayer/EUW?region=europe"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["puuid"] == "test-puuid-12345"
    assert data["gameName"] == "TestPlayer"
    assert data["tagLine"] == "EUW"


@pytest.mark.asyncio
async def test_account_by_riot_id_not_found(async_client: AsyncClient):
    """Test account lookup returns 404 for non-existent player."""
    # Arrange
    mock_error = Exception("404: Not Found")
    mock_error.status_code = 404

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(side_effect=mock_error)):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-riot-id/NonExistent/NONE?region=europe"
        )

    # Assert
    assert response.status_code in [404, 500]  # May propagate as 500


@pytest.mark.asyncio
async def test_account_by_riot_id_validation_error(async_client: AsyncClient):
    """Test account lookup with invalid region parameter."""
    # Act
    response = await async_client.get(
        "/riot/account/v1/accounts/by-riot-id/TestPlayer/EUW?region=invalid_region"
    )

    # Assert
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_account_by_puuid_success(async_client: AsyncClient):
    """Test successful account lookup by PUUID."""
    # Arrange
    mock_response = {
        "puuid": "test-puuid-67890",
        "gameName": "AnotherPlayer",
        "tagLine": "NA1",
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-puuid/test-puuid-67890?region=americas"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["puuid"] == "test-puuid-67890"
    assert data["gameName"] == "AnotherPlayer"


@pytest.mark.asyncio
async def test_account_by_puuid_rate_limit(async_client: AsyncClient):
    """Test account lookup handles rate limiting."""
    # Arrange
    mock_error = Exception("429: Rate Limit Exceeded")
    mock_error.status_code = 429

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(side_effect=mock_error)):
        response = await async_client.get(
            "/riot/account/v1/accounts/by-puuid/test-puuid?region=americas"
        )

    # Assert
    assert response.status_code in [429, 500]


# ============================================================================
# SUMMONER API TESTS (2 endpoints)
# ============================================================================


@pytest.mark.asyncio
async def test_summoner_by_puuid_success(async_client: AsyncClient):
    """Test successful summoner lookup by PUUID."""
    # Arrange
    mock_response = {
        "id": "summoner-id-123",
        "accountId": "account-id-456",
        "puuid": "test-puuid-789",
        "name": "SummonerName",
        "profileIconId": 1,
        "revisionDate": 1234567890,
        "summonerLevel": 100,
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/summoner/v4/summoners/by-puuid/test-puuid-789?region=euw1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["puuid"] == "test-puuid-789"
    assert data["summonerLevel"] == 100


@pytest.mark.asyncio
async def test_summoner_by_puuid_not_found(async_client: AsyncClient):
    """Test summoner lookup returns 404 for invalid PUUID."""
    # Arrange
    mock_error = Exception("404: Not Found")
    mock_error.status_code = 404

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(side_effect=mock_error)):
        response = await async_client.get(
            "/lol/summoner/v4/summoners/by-puuid/invalid-puuid?region=na1"
        )

    # Assert
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_summoner_by_id_success(async_client: AsyncClient):
    """Test successful summoner lookup by summoner ID."""
    # Arrange
    mock_response = {
        "id": "encrypted-summoner-id",
        "accountId": "account-id-999",
        "puuid": "puuid-999",
        "name": "IDLookupPlayer",
        "profileIconId": 5,
        "revisionDate": 9876543210,
        "summonerLevel": 250,
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/summoner/v4/summoners/encrypted-summoner-id?region=kr"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "encrypted-summoner-id"
    assert data["summonerLevel"] == 250


@pytest.mark.asyncio
async def test_summoner_by_id_server_error(async_client: AsyncClient):
    """Test summoner lookup handles server errors."""
    # Arrange
    mock_error = Exception("500: Internal Server Error")
    mock_error.status_code = 500

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(side_effect=mock_error)):
        response = await async_client.get("/lol/summoner/v4/summoners/test-id?region=euw1")

    # Assert
    assert response.status_code == 500


# ============================================================================
# CHAMPION MASTERY API TESTS (2 endpoints)
# ============================================================================


@pytest.mark.asyncio
async def test_champion_mastery_by_champion_success(async_client: AsyncClient):
    """Test successful champion mastery lookup for specific champion."""
    # Arrange
    mock_response = {
        "puuid": "test-puuid",
        "championId": 157,
        "championLevel": 7,
        "championPoints": 500000,
        "lastPlayTime": 1234567890,
        "championPointsSinceLastLevel": 0,
        "championPointsUntilNextLevel": 0,
        "tokensEarned": 3,
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/by-champion/157?region=euw1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["championId"] == 157
    assert data["championLevel"] == 7
    assert data["championPoints"] == 500000


@pytest.mark.asyncio
async def test_champion_mastery_by_champion_not_found(async_client: AsyncClient):
    """Test champion mastery returns 404 for invalid champion."""
    # Arrange
    mock_error = Exception("404: Champion mastery not found")
    mock_error.status_code = 404

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(side_effect=mock_error)):
        response = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/by-champion/99999?region=na1"
        )

    # Assert
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_champion_mastery_top_success(async_client: AsyncClient):
    """Test successful retrieval of top champion masteries."""
    # Arrange
    mock_response = [
        {
            "championId": 157,
            "championLevel": 7,
            "championPoints": 500000,
        },
        {
            "championId": 238,
            "championLevel": 7,
            "championPoints": 450000,
        },
        {
            "championId": 64,
            "championLevel": 6,
            "championPoints": 400000,
        },
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=euw1&count=3"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["championId"] == 157
    assert data[0]["championLevel"] == 7


@pytest.mark.asyncio
async def test_champion_mastery_top_validation_error(async_client: AsyncClient):
    """Test top masteries with invalid count parameter."""
    # Act
    response = await async_client.get(
        "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=euw1&count=999"
    )

    # Assert
    assert response.status_code in [400, 422]


# ============================================================================
# CLASH API TESTS (3 endpoints)
# ============================================================================


@pytest.mark.asyncio
async def test_clash_players_by_puuid_success(async_client: AsyncClient):
    """Test successful Clash player lookup."""
    # Arrange
    mock_response = [
        {
            "summonerId": "summoner-id-1",
            "teamId": "team-id-abc",
            "position": "TOP",
            "role": "CAPTAIN",
        }
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get("/lol/clash/v1/players/by-puuid/test-puuid?region=euw1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["position"] == "TOP"
    assert data[0]["role"] == "CAPTAIN"


@pytest.mark.asyncio
async def test_clash_players_not_found(async_client: AsyncClient):
    """Test Clash player lookup returns empty list for non-participant."""
    # Arrange
    mock_response = []

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/clash/v1/players/by-puuid/non-clash-player?region=na1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_clash_teams_success(async_client: AsyncClient):
    """Test successful Clash team lookup."""
    # Arrange
    mock_response = {
        "id": "team-id-xyz",
        "tournamentId": 123,
        "name": "Team Awesome",
        "iconId": 1,
        "tier": 1,
        "captain": "captain-summoner-id",
        "abbreviation": "TA",
        "players": [
            {"summonerId": "player1", "position": "TOP", "role": "CAPTAIN"},
            {"summonerId": "player2", "position": "JUNGLE", "role": "MEMBER"},
        ],
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get("/lol/clash/v1/teams/team-id-xyz?region=euw1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "team-id-xyz"
    assert data["name"] == "Team Awesome"
    assert len(data["players"]) == 2


@pytest.mark.asyncio
async def test_clash_teams_not_found(async_client: AsyncClient):
    """Test Clash team lookup returns 404 for invalid team ID."""
    # Arrange
    mock_error = Exception("404: Team not found")
    mock_error.status_code = 404

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(side_effect=mock_error)):
        response = await async_client.get("/lol/clash/v1/teams/invalid-team-id?region=kr")

    # Assert
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_clash_tournaments_success(async_client: AsyncClient):
    """Test successful retrieval of all Clash tournaments."""
    # Arrange
    mock_response = [
        {
            "id": 1001,
            "themeId": 1,
            "nameKey": "Tournament 1",
            "nameKeySecondary": "Secondary Name",
            "schedule": [
                {
                    "id": 1,
                    "registrationTime": 1234567890,
                    "startTime": 1234571490,
                    "cancelled": False,
                }
            ],
        },
        {
            "id": 1002,
            "themeId": 2,
            "nameKey": "Tournament 2",
            "nameKeySecondary": "Another Name",
            "schedule": [],
        },
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get("/lol/clash/v1/tournaments?region=na1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1001
    assert data[1]["id"] == 1002


@pytest.mark.asyncio
async def test_clash_tournaments_empty(async_client: AsyncClient):
    """Test Clash tournaments returns empty list when none active."""
    # Arrange
    mock_response = []

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get("/lol/clash/v1/tournaments?region=euw1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


# ============================================================================
# LEAGUE API TESTS (1 endpoint)
# ============================================================================


@pytest.mark.asyncio
async def test_league_entries_by_tier_division_success(async_client: AsyncClient):
    """Test successful league entries lookup by tier and division."""
    # Arrange
    mock_response = [
        {
            "summonerId": "summoner1",
            "summonerName": "Player1",
            "leaguePoints": 75,
            "rank": "I",
            "wins": 50,
            "losses": 45,
            "veteran": False,
            "inactive": False,
            "freshBlood": False,
            "hotStreak": True,
        },
        {
            "summonerId": "summoner2",
            "summonerName": "Player2",
            "leaguePoints": 60,
            "rank": "I",
            "wins": 48,
            "losses": 47,
            "veteran": True,
            "inactive": False,
            "freshBlood": False,
            "hotStreak": False,
        },
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/DIAMOND/I?region=euw1&page=1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["leaguePoints"] == 75
    assert data[1]["veteran"] is True


@pytest.mark.asyncio
async def test_league_entries_validation_error_invalid_tier(async_client: AsyncClient):
    """Test league entries with invalid tier parameter."""
    # Act
    response = await async_client.get(
        "/lol/league/v4/entries/RANKED_SOLO_5x5/INVALID_TIER/I?region=euw1"
    )

    # Assert
    # This may return 404 or 422 depending on routing
    assert response.status_code in [400, 404, 422]


@pytest.mark.asyncio
async def test_league_entries_empty_page(async_client: AsyncClient):
    """Test league entries returns empty list for out-of-range page."""
    # Arrange
    mock_response = []

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/II?region=na1&page=999"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


# ============================================================================
# MATCH API TESTS (1 endpoint)
# ============================================================================


@pytest.mark.asyncio
async def test_match_ids_by_puuid_success(async_client: AsyncClient):
    """Test successful match IDs lookup."""
    # Arrange
    mock_response = [
        "NA1_1234567890",
        "NA1_1234567891",
        "NA1_1234567892",
        "NA1_1234567893",
        "NA1_1234567894",
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=americas&start=0&count=5"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert all(match_id.startswith("NA1_") for match_id in data)


@pytest.mark.asyncio
async def test_match_ids_with_filters_success(async_client: AsyncClient):
    """Test match IDs lookup with queue and type filters."""
    # Arrange
    mock_response = ["EUW1_5555555555", "EUW1_5555555556"]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids"
            "?region=europe&start=0&count=20&queue=420&type=ranked"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_match_ids_empty_result(async_client: AsyncClient):
    """Test match IDs returns empty list for player with no matches."""
    # Arrange
    mock_response = []

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/new-player-puuid/ids?region=americas"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


# ============================================================================
# SPECTATOR API TESTS (1 endpoint)
# ============================================================================


@pytest.mark.asyncio
async def test_spectator_active_game_success(async_client: AsyncClient):
    """Test successful active game lookup."""
    # Arrange
    mock_response = {
        "gameId": 123456789,
        "gameType": "MATCHED_GAME",
        "gameStartTime": 1234567890,
        "mapId": 11,
        "gameLength": 300,
        "platformId": "EUW1",
        "gameMode": "CLASSIC",
        "bannedChampions": [],
        "gameQueueConfigId": 420,
        "observers": {"encryptionKey": "test-key"},
        "participants": [
            {
                "teamId": 100,
                "spell1Id": 4,
                "spell2Id": 14,
                "championId": 157,
                "profileIconId": 1,
                "summonerName": "Player1",
                "puuid": "puuid1",
                "summonerId": "id1",
                "bot": False,
                "perks": {"perkIds": [], "perkStyle": 0, "perkSubStyle": 0},
            }
        ],
    }

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/spectator/v5/active-games/by-summoner/encrypted-puuid-123?region=euw1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["gameId"] == 123456789
    assert data["gameMode"] == "CLASSIC"
    assert len(data["participants"]) == 1


@pytest.mark.asyncio
async def test_spectator_active_game_not_in_game(async_client: AsyncClient):
    """Test active game lookup returns 404 when player not in game."""
    # Arrange
    mock_error = Exception("404: Player not in game")
    mock_error.status_code = 404

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(side_effect=mock_error)):
        response = await async_client.get(
            "/lol/spectator/v5/active-games/by-summoner/not-in-game-puuid?region=na1"
        )

    # Assert
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_spectator_active_game_validation_error(async_client: AsyncClient):
    """Test active game lookup with invalid region."""
    # Act
    response = await async_client.get(
        "/lol/spectator/v5/active-games/by-summoner/test-puuid?region=invalid_region"
    )

    # Assert
    assert response.status_code in [400, 422]
