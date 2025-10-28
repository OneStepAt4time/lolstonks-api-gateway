"""Platform-V4 / LOL-STATUS-V4 API endpoints.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#lol-status-v4
"""

from fastapi import APIRouter, Query
from loguru import logger

from app.config import settings
from app.riot.client import riot_client
from app.cache.redis_cache import cache

router = APIRouter(prefix="/lol/status/v4", tags=["platform"])


@router.get("/platform-data")
async def get_platform_status(
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Get League of Legends platform status for a region.

    API Reference: https://developer.riotgames.com/apis#lol-status-v4/GET_getPlatformData

    Returns:
        - id: Region ID
        - name: Region name
        - locales: Supported locales
        - maintenances: Scheduled maintenance events
        - incidents: Current incidents/issues
    """
    cache_key = f"platform:status:{region}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for platform status", region=region)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching platform status", region=region)
    path = "/lol/status/v4/platform-data"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_platform_status)

    logger.success(
        "Platform status fetched",
        region=region,
        maintenances=len(data.get("maintenances", [])),
        incidents=len(data.get("incidents", [])),
    )

    return data
