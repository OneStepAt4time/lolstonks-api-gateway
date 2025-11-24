"""League-V4 API router for ranked ladder and league information.

This module provides FastAPI endpoints for retrieving ranked ladder data in
League of Legends, including Challenger, Grandmaster, and Master tier leagues,
as well as league entries for individual summoners and paginated rank queries.

The League-V4 API is fundamental for:
- Leaderboard applications tracking high-ELO players
- Analytics systems analyzing ranked distribution
- Player profile applications showing rank and LP
- Tournament qualification systems

Ranked System Overview:
    Tiers (Highest to Lowest):
        - Challenger: Top 200-300 players per region
        - Grandmaster: Top 500-700 players per region
        - Master: Top tier with no player cap
        - Diamond, Emerald, Platinum, Gold, Silver, Bronze, Iron

    Divisions:
        - Challenger, Grandmaster, Master: No divisions (single tier)
        - Others: I (highest), II, III, IV (lowest)

    Queue Types:
        - RANKED_SOLO_5x5: Solo/Duo ranked queue
        - RANKED_FLEX_SR: Flex 5v5 ranked queue
        - RANKED_FLEX_TT: Twisted Treeline (deprecated but may appear in old data)

Regional Behavior:
    - Each region maintains separate ranked ladders
    - Challenger/Grandmaster/Master lists are updated frequently
    - Entry pages are cached but can become stale during active play

Caching Strategy:
    - League data: Medium TTL (typically 5-10 minutes)
    - High-tier leagues: Shorter TTL due to frequent LP changes
    - Summoner entries: Cached to reduce redundant lookups
    - Paginated entries: Each page cached independently

API Reference:
    https://developer.riotgames.com/apis#league-v4

See Also:
    app.models.league: Request/response models for league endpoints
    app.riot.client: HTTP client for Riot API communication
    app.cache.helpers: Caching utilities and decorators
"""

from fastapi import APIRouter, Depends

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.league import (
    LeagueByQueueParams,
    LeagueByQueueQuery,
    LeagueEntriesBySummonerParams,
    LeagueEntriesBySummonerQuery,
    LeagueEntriesParams,
    LeagueEntriesQuery,
)
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/league/v4", tags=["league"])


@router.get("/challengerleagues/by-queue/{queue}")
async def get_challenger_league(
    params: LeagueByQueueParams = Depends(),
    query: LeagueByQueueQuery = Depends(),
):
    """Retrieves the complete Challenger tier league for a specific ranked queue.

    This endpoint returns the full list of all players currently in Challenger rank
    for the specified queue and region. Challenger is the highest tier in League of
    Legends ranked play, typically limited to the top 200-300 players per region.

    The data includes each player's summoner information, League Points (LP), win/loss
    record, and current position in the ladder. This is commonly used for leaderboard
    applications, rank tracking systems, and competitive analytics.

    Challenger leagues are highly dynamic with frequent LP changes as players compete
    for top positions. The cache TTL is set accordingly to balance freshness with
    API efficiency.

    HTTP Method: GET
    Rate Limit: Standard Riot API rate limits apply (varies by API key tier)
    Cache TTL: Configurable via settings.cache_ttl_league (default: 5-10 minutes)

    Args:
        params: Path parameters containing:
            - queue (str): The ranked queue type. Valid values:
                * "RANKED_SOLO_5x5" - Solo/Duo ranked queue
                * "RANKED_FLEX_SR" - Flex 5v5 ranked queue
        query: Query parameters containing:
            - region (str): Platform region code (na1, euw1, kr, etc.)

    Returns:
        dict: Challenger league object containing:
            - tier (str): Always "CHALLENGER"
            - leagueId (str): Unique identifier for this league
            - queue (str): Queue type (same as input)
            - name (str): League name (e.g., "Teemo's Scouts")
            - entries (list[dict]): Array of summoner entries, each containing:
                * summonerId (str): Encrypted summoner ID
                * summonerName (str): Summoner display name
                * leaguePoints (int): Current LP in Challenger
                * rank (str): Always "I" for Challenger
                * wins (int): Number of ranked wins
                * losses (int): Number of ranked losses
                * veteran (bool): Long-time ranked player flag
                * inactive (bool): Inactivity flag
                * freshBlood (bool): Recently promoted flag
                * hotStreak (bool): Win streak flag

    Raises:
        HTTPException: With status code:
            - 400: Invalid queue type or region code
            - 404: No Challenger league exists for this queue/region combination
            - 429: Rate limit exceeded
            - 500: Riot API error or internal server error
            - 503: Riot API service unavailable

    Example:
        Fetch NA Challenger Solo/Duo ladder:

        ```bash
        curl "http://127.0.0.1:8080/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?region=na1"
        ```

        Fetch EUW Challenger Flex ladder:

        ```bash
        curl "http://127.0.0.1:8080/lol/league/v4/challengerleagues/by-queue/RANKED_FLEX_SR?region=euw1"
        ```

    Note:
        - Challenger league size varies by region (typically 200-300 players)
        - LP values change frequently as players compete; consider cache staleness
        - The entries array is not necessarily sorted; sort by leaguePoints if needed
        - Use force=true query parameter to bypass cache for real-time data
        - Some regions may have fewer than 200 players in Challenger

    See Also:
        get_grandmaster_league: Next tier down from Challenger
        get_master_league: Third highest tier
        get_league_entries_by_summoner: Get rank info for specific summoner

    API Reference:
        https://developer.riotgames.com/apis#league-v4/GET_getChallengerLeague
    """
    return await fetch_with_cache(
        cache_key=f"league:challenger:{query.region}:{params.queue}",
        resource_name="Challenger league",
        fetch_fn=lambda: riot_client.get(
            f"/lol/league/v4/challengerleagues/by-queue/{params.queue}", query.region, False
        ),
        ttl=settings.cache_ttl_league,
        context={"queue": params.queue, "region": query.region},
    )


@router.get("/grandmasterleagues/by-queue/{queue}")
async def get_grandmaster_league(
    params: LeagueByQueueParams = Depends(),
    query: LeagueByQueueQuery = Depends(),
):
    """
    Retrieves the Grandmaster league for a specific queue.

    This endpoint fetches a list of all players in the Grandmaster league for a
    given queue, providing a snapshot of the top-ranked players in a region.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getGrandmasterLeague

    Args:
        params (LeagueByQueueParams): The path parameters, containing the queue type.
        query (LeagueByQueueQuery): The query parameters, specifying the region.

    Returns:
        dict: A league object containing an array of summoner entries.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"league:grandmaster:{query.region}:{params.queue}",
        resource_name="Grandmaster league",
        fetch_fn=lambda: riot_client.get(
            f"/lol/league/v4/grandmasterleagues/by-queue/{params.queue}", query.region, False
        ),
        ttl=settings.cache_ttl_league,
        context={"queue": params.queue, "region": query.region},
    )


@router.get("/masterleagues/by-queue/{queue}")
async def get_master_league(
    params: LeagueByQueueParams = Depends(),
    query: LeagueByQueueQuery = Depends(),
):
    """
    Retrieves the Master league for a specific queue.

    This endpoint fetches a list of all players in the Master league for a
    given queue, providing a snapshot of the top-ranked players in a region.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getMasterLeague

    Args:
        params (LeagueByQueueParams): The path parameters, containing the queue type.
        query (LeagueByQueueQuery): The query parameters, specifying the region.

    Returns:
        dict: A league object containing an array of summoner entries.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"league:master:{query.region}:{params.queue}",
        resource_name="Master league",
        fetch_fn=lambda: riot_client.get(
            f"/lol/league/v4/masterleagues/by-queue/{params.queue}", query.region, False
        ),
        ttl=settings.cache_ttl_league,
        context={"queue": params.queue, "region": query.region},
    )


@router.get("/entries/by-summoner/{encryptedSummonerId}")
async def get_league_entries_by_summoner(
    params: LeagueEntriesBySummonerParams = Depends(),
    query: LeagueEntriesBySummonerQuery = Depends(),
):
    """
    Retrieves the league entries for a summoner across all queues.

    This endpoint fetches a list of a summoner's league entries, providing
    details about their rank in each queue they participate in.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntriesForSummoner

    Args:
        params (LeagueEntriesBySummonerParams): The path parameters, containing the encrypted summoner ID.
        query (LeagueEntriesBySummonerQuery): The query parameters, specifying the region.

    Returns:
        list: A list of league entry objects.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/entries/by-summoner/{encryptedSummonerId}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"league:entries:summoner:{query.region}:{params.encryptedSummonerId}",
        resource_name="League entries",
        fetch_fn=lambda: riot_client.get(
            f"/lol/league/v4/entries/by-summoner/{params.encryptedSummonerId}", query.region, False
        ),
        ttl=settings.cache_ttl_league,
        context={"summoner_id": params.encryptedSummonerId, "region": query.region},
    )


@router.get("/entries/{queue}/{tier}/{division}")
async def get_league_entries(
    params: LeagueEntriesParams = Depends(),
    query: LeagueEntriesQuery = Depends(),
):
    """
    Retrieves league entries by queue, tier, and division.

    This endpoint provides paginated access to league entries for a specific
    rank, allowing for the retrieval of large sets of ranked players.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntries

    Args:
        params (LeagueEntriesParams): The path parameters, containing the queue, tier, and division.
        query (LeagueEntriesQuery): The query parameters, specifying the region and page number.

    Returns:
        list: A list of league entry objects, including summoner info, LP, and win/loss stats.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/entries/RANKED_SOLO_5x5/DIAMOND/I?region=euw1&page=1"
    """
    # Build path with page parameter if not default
    path = f"/lol/league/v4/entries/{params.queue}/{params.tier}/{params.division}"
    if query.page != 1:
        path += f"?page={query.page}"

    return await fetch_with_cache(
        cache_key=f"league:entries:{query.region}:{params.queue}:{params.tier}:{params.division}:{query.page}",
        resource_name="League entries",
        fetch_fn=lambda: riot_client.get(path, query.region, False),
        ttl=settings.cache_ttl_league,
        context={
            "queue": params.queue,
            "tier": params.tier,
            "division": params.division,
            "page": query.page,
            "region": query.region,
        },
    )
