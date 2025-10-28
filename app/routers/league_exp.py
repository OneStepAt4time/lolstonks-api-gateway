"""League-EXP-V4 API endpoints (Experimental) - Priority 5.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#league-exp-v4

Note: This is an experimental API providing paginated league entries.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.cache.redis_cache import cache
from app.config import settings
from app.models.league_exp import LeagueExpEntriesParams, LeagueExpEntriesQuery
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/league-exp/v4", tags=["league-exp"])


@router.get("/entries/{queue}/{tier}/{division}")
async def get_league_exp_entries(
    params: Annotated[LeagueExpEntriesParams, Depends()],
    query: Annotated[LeagueExpEntriesQuery, Depends()],
):
    """
    Get league entries by queue, tier, and division (experimental endpoint).

    This experimental endpoint provides paginated access to league entries.
    Use this for fetching large sets of ranked players at specific ranks.

    API Reference: https://developer.riotgames.com/apis#league-exp-v4/GET_getLeagueEntries

    Args:
        queue: Queue type (RANKED_SOLO_5x5, RANKED_FLEX_SR, etc.)
        tier: Tier (IRON through DIAMOND)
        division: Division (I, II, III, IV)
        region: Region code
        page: Page number (starts at 1)

    Returns:
        Array of league entries with summoner info, LP, win/loss stats
    """
    logger.info(
        "Fetching league exp entries",
        queue=params.queue,
        tier=params.tier,
        division=params.division,
        region=query.region,
        page=query.page,
    )

    # Check cache first
    cache_key = f"league-exp:entries:{query.region}:{params.queue}:{params.tier}:{params.division}:{query.page}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for league exp entries")
        return cached_data

    # Fetch from Riot API
    path = f"/lol/league-exp/v4/entries/{params.queue}/{params.tier}/{params.division}"
    # Add page parameter if not default
    if query.page != 1:
        path += f"?page={query.page}"

    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache (1 hour - league entries change frequently)
    await cache.set(cache_key, data, ttl=settings.cache_ttl_league)

    logger.success(
        "League exp entries fetched",
        queue=params.queue,
        tier=params.tier,
        division=params.division,
        entries=len(data),
    )
    return data
