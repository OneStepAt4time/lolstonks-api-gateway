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
    Get match IDs for a summoner by PUUID.

    This endpoint is used for match discovery with optional filtering.

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID

    Args:
        puuid: Player UUID
        region: Region code
        start: Start index (pagination)
        count: Number of matches to return (1-100)
        startTime: Optional epoch timestamp - only matches after this time
        endTime: Optional epoch timestamp - only matches before this time
        queue: Optional queue ID filter
        type: Optional match type filter (ranked, normal, tourney, tutorial)

    Returns:
        List of match IDs
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
    Get match details by match ID.

    This is the core match data endpoint with dual-layer caching:
    - Layer 1: Response cache (24h TTL)
    - Layer 2: Permanent tracking to prevent duplicate processing

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getMatch

    Args:
        matchId: Match ID (e.g., EUW1_123456789)
        region: Region code
        force: If True, bypass cache and fetch fresh data

    Returns:
        Match object from Riot API
    """
    logger.info("Match request received", match_id=params.matchId, region=query.region, force=query.force)

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
                logger.debug("Cache miss for processed match (TTL expired)", match_id=params.matchId)
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
    Get match timeline (detailed events).

    Priority 4 endpoint - detailed timeline data.

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getTimeline

    Args:
        matchId: Match ID
        region: Region code

    Returns:
        Match timeline object from Riot API
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
