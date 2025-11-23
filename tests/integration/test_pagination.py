"""Integration tests for pagination behavior.

Tests cover:
- League entries pagination (page parameter)
- Match IDs pagination (start/count)
- Champion Mastery top pagination (count)
- Boundary conditions
- Validation
- Empty results
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


# ============================================================================
# LEAGUE ENTRIES PAGINATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_league_entries_page_1(async_client: AsyncClient):
    """Test league entries retrieval for page 1."""
    # Arrange
    mock_response = [
        {"summonerId": f"player-{i}", "leaguePoints": 100 - i, "wins": 50, "losses": 45}
        for i in range(10)
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/I?region=euw1&page=1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert data[0]["summonerId"] == "player-0"


@pytest.mark.asyncio
async def test_league_entries_page_2(async_client: AsyncClient):
    """Test league entries retrieval for page 2."""
    # Arrange
    mock_response = [
        {"summonerId": f"player-page2-{i}", "leaguePoints": 90 - i, "wins": 48, "losses": 47}
        for i in range(10)
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/I?region=euw1&page=2"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert data[0]["summonerId"] == "player-page2-0"


@pytest.mark.asyncio
async def test_league_entries_page_increment(async_client: AsyncClient):
    """Test that different pages return different data."""
    # Arrange
    mock_response_page1 = [{"summonerId": "page1-player", "leaguePoints": 100}]
    mock_response_page2 = [{"summonerId": "page2-player", "leaguePoints": 95}]

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        mock_get.side_effect = [mock_response_page1, mock_response_page2]

        response_page1 = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/PLATINUM/II?region=na1&page=1"
        )
        response_page2 = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/PLATINUM/II?region=na1&page=2"
        )

    # Assert
    assert response_page1.status_code == 200
    assert response_page2.status_code == 200
    assert response_page1.json()[0]["summonerId"] != response_page2.json()[0]["summonerId"]


@pytest.mark.asyncio
async def test_league_entries_last_page_partial(async_client: AsyncClient):
    """Test that last page can have fewer entries than full page."""
    # Arrange
    mock_response = [
        {"summonerId": "last-player-1", "leaguePoints": 10},
        {"summonerId": "last-player-2", "leaguePoints": 5},
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/SILVER/IV?region=kr&page=50"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_league_entries_empty_page(async_client: AsyncClient):
    """Test that out-of-range page returns empty list."""
    # Arrange
    mock_response = []

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/BRONZE/III?region=euw1&page=9999"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_league_entries_page_zero_validation(async_client: AsyncClient):
    """Test that page 0 is rejected."""
    # Act
    response = await async_client.get(
        "/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/I?region=euw1&page=0"
    )

    # Assert - page must be >= 1
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_league_entries_negative_page_validation(async_client: AsyncClient):
    """Test that negative page numbers are rejected."""
    # Act
    response = await async_client.get(
        "/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/I?region=euw1&page=-5"
    )

    # Assert
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_league_entries_default_page(async_client: AsyncClient):
    """Test that omitting page parameter defaults to page 1."""
    # Arrange
    mock_response = [{"summonerId": "default-player", "leaguePoints": 75}]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        # Request without page parameter
        response = await async_client.get(
            "/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/I?region=euw1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 0


# ============================================================================
# MATCH IDS PAGINATION TESTS (start/count)
# ============================================================================


@pytest.mark.asyncio
async def test_match_ids_default_pagination(async_client: AsyncClient):
    """Test match IDs with default start/count parameters."""
    # Arrange
    mock_response = [f"EUW1_{1000000 + i}" for i in range(20)]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=europe"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20


@pytest.mark.asyncio
async def test_match_ids_custom_count(async_client: AsyncClient):
    """Test match IDs with custom count parameter."""
    # Arrange
    mock_response = [f"NA1_{2000000 + i}" for i in range(10)]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=americas&count=10"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10


@pytest.mark.asyncio
async def test_match_ids_start_offset(async_client: AsyncClient):
    """Test match IDs with start offset."""
    # Arrange
    mock_response = [f"KR_{3000000 + i}" for i in range(20)]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=asia&start=20&count=20"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20


@pytest.mark.asyncio
async def test_match_ids_pagination_sequence(async_client: AsyncClient):
    """Test paginating through match IDs with start/count."""
    # Arrange
    mock_response_batch1 = [f"EUW1_A{i}" for i in range(10)]
    mock_response_batch2 = [f"EUW1_B{i}" for i in range(10)]

    # Act
    with patch("app.riot.client.riot_client.get") as mock_get:
        mock_get.side_effect = [mock_response_batch1, mock_response_batch2]

        # First batch
        response1 = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=europe&start=0&count=10"
        )

        # Second batch
        response2 = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=europe&start=10&count=10"
        )

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    data1 = response1.json()
    data2 = response2.json()
    assert len(data1) == 10
    assert len(data2) == 10
    # Verify different batches
    assert data1[0] != data2[0]


@pytest.mark.asyncio
async def test_match_ids_count_max_limit(async_client: AsyncClient):
    """Test match IDs with maximum count limit (100)."""
    # Arrange
    mock_response = [f"NA1_MAX{i}" for i in range(100)]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=americas&count=100"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 100


@pytest.mark.asyncio
async def test_match_ids_count_exceeds_limit(async_client: AsyncClient):
    """Test match IDs with count exceeding limit is rejected."""
    # Act
    response = await async_client.get(
        "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=europe&count=101"
    )

    # Assert - count should not exceed 100
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_match_ids_negative_start(async_client: AsyncClient):
    """Test match IDs with negative start is rejected."""
    # Act
    response = await async_client.get(
        "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=americas&start=-10"
    )

    # Assert
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_match_ids_zero_count(async_client: AsyncClient):
    """Test match IDs with zero count is rejected."""
    # Act
    response = await async_client.get(
        "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=europe&count=0"
    )

    # Assert
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_match_ids_empty_result_beyond_available(async_client: AsyncClient):
    """Test match IDs returns empty when start is beyond available matches."""
    # Arrange
    mock_response = []

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/match/v5/matches/by-puuid/test-puuid/ids?region=europe&start=1000&count=20"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


# ============================================================================
# CHAMPION MASTERY TOP PAGINATION TESTS (count)
# ============================================================================


@pytest.mark.asyncio
async def test_champion_mastery_top_default_count(async_client: AsyncClient):
    """Test top champion masteries with default count (3)."""
    # Arrange
    mock_response = [
        {"championId": 157, "championLevel": 7, "championPoints": 500000},
        {"championId": 238, "championLevel": 7, "championPoints": 450000},
        {"championId": 64, "championLevel": 6, "championPoints": 400000},
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=euw1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_champion_mastery_top_custom_count(async_client: AsyncClient):
    """Test top champion masteries with custom count."""
    # Arrange
    mock_response = [
        {"championId": i, "championLevel": 7, "championPoints": 500000 - (i * 1000)}
        for i in range(10)
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=na1&count=10"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10


@pytest.mark.asyncio
async def test_champion_mastery_top_count_1(async_client: AsyncClient):
    """Test top champion masteries with count=1 (minimum)."""
    # Arrange
    mock_response = [{"championId": 157, "championLevel": 7, "championPoints": 999999}]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=kr&count=1"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_champion_mastery_top_count_20(async_client: AsyncClient):
    """Test top champion masteries with count=20 (maximum)."""
    # Arrange
    mock_response = [
        {"championId": i, "championLevel": 5 + (i % 3), "championPoints": 400000 - (i * 5000)}
        for i in range(20)
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=euw1&count=20"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20


@pytest.mark.asyncio
async def test_champion_mastery_top_count_exceeds_limit(async_client: AsyncClient):
    """Test top champion masteries with count exceeding limit (21+)."""
    # Act
    response = await async_client.get(
        "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=euw1&count=21"
    )

    # Assert - count should not exceed 20
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_champion_mastery_top_count_zero(async_client: AsyncClient):
    """Test top champion masteries with count=0 is rejected."""
    # Act
    response = await async_client.get(
        "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=na1&count=0"
    )

    # Assert
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_champion_mastery_top_negative_count(async_client: AsyncClient):
    """Test top champion masteries with negative count is rejected."""
    # Act
    response = await async_client.get(
        "/lol/champion-mastery/v4/champion-masteries/by-puuid/test-puuid/top?region=kr&count=-5"
    )

    # Assert
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_champion_mastery_top_fewer_than_requested(async_client: AsyncClient):
    """Test top champion masteries when player has fewer champions than requested."""
    # Arrange - player only has 2 champions
    mock_response = [
        {"championId": 1, "championLevel": 5, "championPoints": 50000},
        {"championId": 2, "championLevel": 4, "championPoints": 30000},
    ]

    # Act
    with patch("app.riot.client.riot_client.get", new=AsyncMock(return_value=mock_response)):
        response = await async_client.get(
            "/lol/champion-mastery/v4/champion-masteries/by-puuid/new-player/top?region=euw1&count=10"
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    # Returns only 2 even though we requested 10
    assert len(data) == 2
