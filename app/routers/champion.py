"""Champion-V3 API router for champion rotation data.

This module provides FastAPI endpoints for retrieving the current free-to-play
champion rotation in League of Legends. The champion rotation changes weekly,
typically on Tuesday mornings (Pacific Time), and consists of:
- Free champions available to all players (typically 14-16 champions)
- Additional free champions for new players (level 1-10, typically 10 champions)

The data is region-specific and heavily cached since it only changes weekly.
This endpoint is commonly used by:
- Client applications showing available free champions
- Analytics tools tracking rotation patterns
- New player onboarding systems

Regional Behavior:
    - Each region (na1, euw1, kr, etc.) has the same rotation globally
    - Rotation changes happen simultaneously across all regions
    - Cache TTL is set to 24 hours since rotation is stable for a week

Caching Strategy:
    - Long TTL (24 hours) due to weekly rotation cycle
    - Force refresh available via query parameter
    - Minimal API calls due to infrequent data changes

API Reference:
    https://developer.riotgames.com/apis#champion-v3

See Also:
    app.riot.client: HTTP client for Riot API communication
    app.cache.helpers: Caching utilities and decorators
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
    """Retrieves the current free-to-play champion rotation.

    This endpoint returns the list of champions that are currently available to play
    for free in League of Legends. The rotation includes two sets:
    1. Standard free rotation: Available to all players (typically 14-16 champions)
    2. New player rotation: Available only to players below a certain level (typically
       level 10, includes 10 champions)

    Champion rotations reset weekly on Tuesday mornings (Pacific Time). The rotation
    is identical across all regions globally, though this endpoint requires a region
    parameter for API routing purposes.

    This data is heavily cached (24-hour TTL) since rotations only change weekly,
    significantly reducing API calls and improving response times.

    HTTP Method: GET
    Rate Limit: Standard Riot API rate limits apply (varies by API key tier)
    Cache TTL: Configurable via settings.cache_ttl_champion_rotation (default: 24 hours)

    Args:
        region: The platform region code. Valid values include: na1, euw1, euw, kr,
            br1, jp1, la1, la2, oc1, ph2, ru, sg2, th2, tr1, tw2, vn2. Defaults to
            the value configured in settings.riot_default_region.

    Returns:
        dict: Champion rotation data containing:
            - freeChampionIds (list[int]): List of champion IDs in the standard free
              rotation (available to all players). Each ID corresponds to a champion's
              numeric identifier (e.g., 1 = Annie, 157 = Yasuo).
            - freeChampionIdsForNewPlayers (list[int]): List of champion IDs in the
              new player rotation (available only to low-level accounts).
            - maxNewPlayerLevel (int): Maximum account level to qualify for the new
              player rotation (typically 10).

    Raises:
        HTTPException: With status code:
            - 400: Invalid region code provided
            - 429: Rate limit exceeded
            - 500: Riot API error or internal server error
            - 503: Riot API service unavailable

    Example:
        Fetch current rotation for EUW:

        ```bash
        curl "http://127.0.0.1:8080/lol/platform/v3/champion-rotations?region=euw1"
        ```

        Response:

        ```json
        {
            "freeChampionIds": [1, 3, 11, 17, 18, 22, 25, 30, 33, 40, 45, 51, 53, 63],
            "freeChampionIdsForNewPlayers": [222, 254, 427, 82, 131, 147, 54, 17, 18, 37],
            "maxNewPlayerLevel": 10
        }
        ```

    Note:
        - Champion IDs must be mapped to champion names using Data Dragon or other resources
        - The rotation is the same globally; region parameter only affects API routing
        - New player rotation is a separate, stable set designed for beginner-friendly champions
        - Cache TTL is 24 hours but data only changes weekly, so most requests hit cache
        - Use force=true query parameter to bypass cache if needed (not shown in signature)

    See Also:
        Data Dragon: For mapping champion IDs to names and details
        app.cache.helpers.fetch_with_cache: Caching implementation details

    API Reference:
        https://developer.riotgames.com/apis#champion-v3/GET_getChampionInfo
    """
    return await fetch_with_cache(
        cache_key=f"champion:rotation:{region}",
        resource_name="Champion rotation",
        fetch_fn=lambda: riot_client.get("/lol/platform/v3/champion-rotations", region, False),
        ttl=settings.cache_ttl_champion_rotation,
        context={"region": region},
    )
