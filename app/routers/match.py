"""Match API endpoints - Priority 2 & 3."""

from fastapi import APIRouter, Query
from loguru import logger

from app.cache.redis_cache import cache
from app.cache.tracking import tracker
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/match/v5", tags=["match"])


@router.get("/matches/by-puuid/{puuid}/ids")
async def get_match_ids_by_puuid(
    puuid: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    start: int = Query(default=0, ge=0, description="Start index"),
    count: int = Query(default=20, ge=1, le=100, description="Number of match IDs to return (max 100)")
):
    """
    Get match IDs for a summoner by PUUID.

    This endpoint is used for match discovery.

    Args:
        puuid: Player UUID
        region: Region code
        start: Start index (pagination)
        count: Number of matches to return (1-100)

    Returns:
        List of match IDs
    """
    logger.info("Fetching match IDs", puuid=puuid[:8], region=region, start=start, count=count)

    # Build path with query parameters
    path = f"/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
    match_ids = await riot_client.get(path, region, is_platform_endpoint=True)

    logger.success("Match IDs fetched", count=len(match_ids), region=region)
    return match_ids


@router.get("/matches/{matchId}")
async def get_match(
    matchId: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    force: bool = Query(default=False, description="Force refresh from Riot API (bypass cache)")
):
    """
    Get match details by match ID.

    This is the core match data endpoint with dual-layer caching:
    - Layer 1: Response cache (24h TTL)
    - Layer 2: Permanent tracking to prevent duplicate processing

    Args:
        matchId: Match ID (e.g., EUW1_123456789)
        region: Region code
        force: If True, bypass cache and fetch fresh data

    Returns:
        Match object from Riot API
    """
    logger.info("Match request received", match_id=matchId, region=region, force=force)

    cache_key = f"match:{region}:{matchId}"

    # Check force refresh
    if not force:
        # Check if already processed (permanent tracking)
        is_processed = await tracker.is_processed(region, matchId)

        if is_processed:
            logger.debug("Match already processed, checking cache", match_id=matchId)

            # Try to get from cache
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug("Cache hit for processed match", match_id=matchId)
                return cached_data
            else:
                logger.debug("Cache miss for processed match (TTL expired)", match_id=matchId)
        else:
            logger.debug("Match not yet processed", match_id=matchId)
    else:
        logger.info("Force refresh requested, bypassing cache", match_id=matchId)

    # Fetch from Riot API (rate-limited)
    logger.info("Fetching match from Riot API", match_id=matchId, region=region)
    path = f"/lol/match/v5/matches/{matchId}"
    data = await riot_client.get(path, region, is_platform_endpoint=True)

    # Store in cache with TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_match)
    logger.debug("Match stored in cache", match_id=matchId, ttl=settings.cache_ttl_match)

    # Mark as processed (permanent, no TTL)
    await tracker.mark_processed(region, matchId)
    logger.debug("Match marked as processed", match_id=matchId, region=region)

    logger.success("Match fetched and cached successfully", match_id=matchId)
    return data


@router.get("/matches/{matchId}/timeline")
async def get_match_timeline(
    matchId: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get match timeline (detailed events).

    Priority 4 endpoint - detailed timeline data.

    Args:
        matchId: Match ID
        region: Region code

    Returns:
        Match timeline object from Riot API
    """
    logger.info("Fetching match timeline", match_id=matchId, region=region)

    # Check cache first
    cache_key = f"match:timeline:{region}:{matchId}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for match timeline", match_id=matchId)
        return cached_data

    # Fetch from Riot API
    path = f"/lol/match/v5/matches/{matchId}/timeline"
    data = await riot_client.get(path, region, is_platform_endpoint=True)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_timeline)

    logger.success("Match timeline fetched", match_id=matchId)
    return data
