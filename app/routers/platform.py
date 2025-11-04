"""Platform-V4 / LOL-STATUS-V4 API endpoints.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#lol-status-v4
"""

from fastapi import APIRouter, Query

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/status/v4", tags=["platform"])


@router.get("/platform-data")
async def get_platform_status(
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves the platform status for a specific region.

    This endpoint fetches the current status of the League of Legends platform,
    including any ongoing maintenance or incidents.

    API Reference: https://developer.riotgames.com/apis#lol-status-v4/GET_getPlatformData

    Args:
        region (str): The region to fetch the platform status for.

    Returns:
        dict: A dictionary containing the platform status, including region ID,
              name, locales, maintenances, and incidents.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/status/v4/platform-data?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"platform:status:{region}",
        resource_name="Platform status",
        fetch_fn=lambda: riot_client.get("/lol/status/v4/platform-data", region, False),
        ttl=settings.cache_ttl_platform_status,
        context={"region": region},
    )
