"""League API endpoints - Priority 5.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#league-v4
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.cache.redis_cache import cache
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
    params: Annotated[LeagueByQueueParams, Depends()],
    query: Annotated[LeagueByQueueQuery, Depends()],
):
    """
    Get challenger league entries for a queue.

    This endpoint returns the top players in a region, including their summonerIds.
    Use this to get a list of high-level players to track.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getChallengerLeague

    Args:
        queue: Queue type (RANKED_SOLO_5x5, RANKED_FLEX_SR, RANKED_FLEX_TT)
        region: Region code (default: euw1)

    Returns:
        League object with entries array containing summoner information
    """
    logger.info("Fetching challenger league", queue=params.queue, region=query.region)

    # Check cache first
    cache_key = f"league:challenger:{query.region}:{params.queue}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for challenger league", queue=params.queue)
        return cached_data

    # Fetch from Riot API
    path = f"/lol/league/v4/challengerleagues/by-queue/{params.queue}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache (1 hour - challenger changes frequently)
    await cache.set(cache_key, data, ttl=settings.cache_ttl_league)

    logger.success(
        "Challenger league fetched", queue=params.queue, entries=len(data.get("entries", []))
    )
    return data


@router.get("/grandmasterleagues/by-queue/{queue}")
async def get_grandmaster_league(
    params: Annotated[LeagueByQueueParams, Depends()],
    query: Annotated[LeagueByQueueQuery, Depends()],
):
    """
    Get grandmaster league entries for a queue.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getGrandmasterLeague

    Args:
        queue: Queue type (RANKED_SOLO_5x5, RANKED_FLEX_SR, RANKED_FLEX_TT)
        region: Region code

    Returns:
        League object with entries
    """
    logger.info("Fetching grandmaster league", queue=params.queue, region=query.region)

    # Check cache first
    cache_key = f"league:grandmaster:{query.region}:{params.queue}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for grandmaster league", queue=params.queue)
        return cached_data

    # Fetch from Riot API
    path = f"/lol/league/v4/grandmasterleagues/by-queue/{params.queue}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_league)

    logger.success(
        "Grandmaster league fetched", queue=params.queue, entries=len(data.get("entries", []))
    )
    return data


@router.get("/masterleagues/by-queue/{queue}")
async def get_master_league(
    params: Annotated[LeagueByQueueParams, Depends()],
    query: Annotated[LeagueByQueueQuery, Depends()],
):
    """
    Get master league entries for a queue.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getMasterLeague

    Args:
        queue: Queue type (RANKED_SOLO_5x5, RANKED_FLEX_SR, RANKED_FLEX_TT)
        region: Region code

    Returns:
        League object with entries
    """
    logger.info("Fetching master league", queue=params.queue, region=query.region)

    # Check cache first
    cache_key = f"league:master:{query.region}:{params.queue}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for master league", queue=params.queue)
        return cached_data

    # Fetch from Riot API
    path = f"/lol/league/v4/masterleagues/by-queue/{params.queue}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_league)

    logger.success(
        "Master league fetched", queue=params.queue, entries=len(data.get("entries", []))
    )
    return data


@router.get("/entries/by-summoner/{encryptedSummonerId}")
async def get_league_entries_by_summoner(
    params: Annotated[LeagueEntriesBySummonerParams, Depends()],
    query: Annotated[LeagueEntriesBySummonerQuery, Depends()],
):
    """
    Get league entries for a summoner (all queues).

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntriesForSummoner

    Args:
        encryptedSummonerId: Encrypted summoner ID
        region: Region code

    Returns:
        Array of league entries
    """
    logger.info(
        "Fetching league entries by summoner",
        summoner_id=params.encryptedSummonerId,
        region=query.region,
    )

    # Check cache first
    cache_key = f"league:entries:summoner:{query.region}:{params.encryptedSummonerId}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for league entries")
        return cached_data

    # Fetch from Riot API
    path = f"/lol/league/v4/entries/by-summoner/{params.encryptedSummonerId}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_league)

    logger.success("League entries fetched", entries=len(data))
    return data


@router.get("/entries/{queue}/{tier}/{division}")
async def get_league_entries(
    params: Annotated[LeagueEntriesParams, Depends()],
    query: Annotated[LeagueEntriesQuery, Depends()],
):
    """
    Get league entries by queue, tier, and division.

    This endpoint provides paginated access to league entries at specific ranks.
    Use this for fetching large sets of ranked players.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntries

    Args:
        queue: Queue type (RANKED_SOLO_5x5, RANKED_FLEX_SR, RANKED_FLEX_TT)
        tier: Tier (IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND)
        division: Division (I, II, III, IV)
        region: Region code
        page: Page number (starts at 1)

    Returns:
        Array of league entries with summoner info, LP, win/loss stats
    """
    logger.info(
        "Fetching league entries",
        queue=params.queue,
        tier=params.tier,
        division=params.division,
        region=query.region,
        page=query.page,
    )

    # Check cache first
    cache_key = (
        f"league:entries:{query.region}:{params.queue}:{params.tier}:{params.division}:{query.page}"
    )
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for league entries")
        return cached_data

    # Fetch from Riot API
    path = f"/lol/league/v4/entries/{params.queue}/{params.tier}/{params.division}"
    # Add page parameter if not default
    if query.page != 1:
        path += f"?page={query.page}"

    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache (1 hour - league entries change frequently)
    await cache.set(cache_key, data, ttl=settings.cache_ttl_league)

    logger.success(
        "League entries fetched",
        queue=params.queue,
        tier=params.tier,
        division=params.division,
        entries=len(data),
    )
    return data
