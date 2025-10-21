"""Champion-V3 API endpoints."""

from fastapi import APIRouter, Query
from loguru import logger

from app.config import settings
from app.riot.client import riot_client
from app.cache.redis_cache import cache

router = APIRouter(prefix="/lol/platform/v3", tags=["champion"])


@router.get("/champion-rotations")
async def get_champion_rotations(
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get current champion rotation (free-to-play champions).

    Returns:
        - freeChampionIds: List of free champion IDs
        - freeChampionIdsForNewPlayers: List for new players
        - maxNewPlayerLevel: Max level for new player rotation
    """
    cache_key = f"champion:rotation:{region}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for champion rotation", region=region)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching champion rotation from Riot API", region=region)
    path = "/lol/platform/v3/champion-rotations"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with 24 hour TTL (rotations change weekly)
    await cache.set(cache_key, data, ttl=86400)
    logger.success("Champion rotation fetched", region=region)

    return data
