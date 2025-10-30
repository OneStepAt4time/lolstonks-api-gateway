"""Match API endpoints - Priority 2 & 3.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#match-v5
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.cache.redis_cache import cache
from app.cache.tracking import tracker
from app.config import settings
from app.models.match import (
    MatchIdsByPuuidParams,
    MatchIdsByPuuidQuery,
    MatchParams,
    MatchQuery,
    MatchTimelineParams,
    MatchTimelineQuery,
)
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/match/v5", tags=["match"])


@router.get("/matches/by-puuid/{puuid}/ids")
async def get_match_ids_by_puuid(
    params: Annotated[MatchIdsByPuuidParams, Depends()],
    query: Annotated[MatchIdsByPuuidQuery, Depends()],
):
    """
    Retrieves a list of match IDs for a summoner.

    This endpoint fetches a list of match IDs based on a player's PUUID, with
    options for pagination and filtering by time, queue, and match type.

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID

    Args:
        params (MatchIdsByPuuidParams): The path parameters, containing the PUUID.
        query (MatchIdsByPuuidQuery): The query parameters, for pagination and filtering.

    Returns:
        list: A list of match IDs.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/match/v5/matches/by-puuid/{puuid}/ids?region=americas&count=20"
    """
    logger.info(
        "Fetching match IDs",
        puuid=params.puuid[:8],
        region=query.region,
        start=query.start,
        count=query.count,
        filters={
            "startTime": query.startTime,
            "endTime": query.endTime,
            "queue": query.queue,
            "type": query.type,
        },
    )

    # Build query parameters
    query_params = [f"start={query.start}", f"count={query.count}"]
    if query.startTime is not None:
        query_params.append(f"startTime={query.startTime}")
    if query.endTime is not None:
        query_params.append(f"endTime={query.endTime}")
    if query.queue is not None:
        query_params.append(f"queue={query.queue}")
    if query.type is not None:
        query_params.append(f"type={query.type}")

    # Build path with query parameters
    path = f"/lol/match/v5/matches/by-puuid/{params.puuid}/ids?{'&'.join(query_params)}"
    match_ids = await riot_client.get(path, query.region, is_platform_endpoint=True)

    logger.success("Match IDs fetched", count=len(match_ids), region=query.region)
    return match_ids


@router.get("/matches/{matchId}")
async def get_match(
    params: Annotated[MatchParams, Depends()],
    query: Annotated[MatchQuery, Depends()],
):
    """
    Retrieves match details by match ID.

    This endpoint fetches the core data for a specific match. It employs a
    dual-layer caching strategy, with a response cache and permanent tracking,
    to minimize redundant API calls.

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getMatch

    Args:
        params (MatchParams): The path parameters, containing the match ID.
        query (MatchQuery): The query parameters, specifying the region and an
                           optional force refresh flag.

    Returns:
        dict: A dictionary containing the match details.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/match/v5/matches/EUW1_123456789?region=americas"
    """
    logger.info(
        "Match request received", match_id=params.matchId, region=query.region, force=query.force
    )

    cache_key = f"match:{query.region}:{params.matchId}"

    # Check force refresh
    if not query.force:
        # Check if already processed (permanent tracking)
        is_processed = await tracker.is_processed(query.region, params.matchId)

        if is_processed:
            logger.debug("Match already processed, checking cache", match_id=params.matchId)

            # Try to get from cache
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug("Cache hit for processed match", match_id=params.matchId)
                return cached_data
            else:
                logger.debug(
                    "Cache miss for processed match (TTL expired)", match_id=params.matchId
                )
        else:
            logger.debug("Match not yet processed", match_id=params.matchId)
    else:
        logger.info("Force refresh requested, bypassing cache", match_id=params.matchId)

    # Fetch from Riot API (rate-limited)
    logger.info("Fetching match from Riot API", match_id=params.matchId, region=query.region)
    path = f"/lol/match/v5/matches/{params.matchId}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=True)

    # Store in cache with TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_match)
    logger.debug("Match stored in cache", match_id=params.matchId, ttl=settings.cache_ttl_match)

    # Mark as processed (permanent, no TTL)
    await tracker.mark_processed(query.region, params.matchId)
    logger.debug("Match marked as processed", match_id=params.matchId, region=query.region)

    logger.success("Match fetched and cached successfully", match_id=params.matchId)
    return data


@router.get("/matches/{matchId}/timeline")
async def get_match_timeline(
    params: Annotated[MatchTimelineParams, Depends()],
    query: Annotated[MatchTimelineQuery, Depends()],
):
    """
    Retrieves the timeline for a specific match.

    This endpoint fetches a detailed timeline of events for a given match,
    providing in-depth data for analysis.

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getTimeline

    Args:
        params (MatchTimelineParams): The path parameters, containing the match ID.
        query (MatchTimelineQuery): The query parameters, specifying the region.

    Returns:
        dict: A dictionary containing the match timeline data.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/match/v5/matches/EUW1_123456789/timeline?region=americas"
    """
    logger.info("Fetching match timeline", match_id=params.matchId, region=query.region)

    # Check cache first
    cache_key = f"match:timeline:{query.region}:{params.matchId}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for match timeline", match_id=params.matchId)
        return cached_data

    # Fetch from Riot API
    path = f"/lol/match/v5/matches/{params.matchId}/timeline"
    data = await riot_client.get(path, query.region, is_platform_endpoint=True)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_timeline)

    logger.success("Match timeline fetched", match_id=params.matchId)
    return data
