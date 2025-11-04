"""Champion-V3 API endpoints.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#champion-v3
"""

from fastapi import APIRouter, Query

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/platform/v3", tags=["champion"])


@router.get("/champion-rotations")
async def get_champion_rotations(
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves the current champion rotation.

    This endpoint fetches the list of free-to-play champions, including those
    available for new players. The results are cached to optimize performance.

    API Reference: https://developer.riotgames.com/apis#champion-v3/GET_getChampionInfo

    Args:
        region (str): The region to fetch the champion rotation from.

    Returns:
        dict: A dictionary containing the list of free champion IDs, a separate
              list for new players, and the maximum level for the new player rotation.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/platform/v3/champion-rotations?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"champion:rotation:{region}",
        resource_name="Champion rotation",
        fetch_fn=lambda: riot_client.get("/lol/platform/v3/champion-rotations", region, False),
        ttl=settings.cache_ttl_champion_rotation,
        context={"region": region},
    )
