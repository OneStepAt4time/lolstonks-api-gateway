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
    params: LeagueExpEntriesParams = Depends(),
    query: LeagueExpEntriesQuery = Depends(),
):
    """
    Retrieves league entries from the experimental endpoint.

    This endpoint provides paginated access to league entries for a specific
    rank, allowing for the retrieval of large sets of ranked players.

    API Reference: https://developer.riotgames.com/apis#league-exp-v4/GET_getLeagueEntries

    Args:
        params (LeagueExpEntriesParams): The path parameters, containing the queue, tier, and division.
        query (LeagueExpEntriesQuery): The query parameters, specifying the region and page number.

    Returns:
        list: A list of league entry objects, including summoner info, LP, and win/loss stats.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league-exp/v4/entries/RANKED_SOLO_5x5/DIAMOND/I?region=euw1&page=1"
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
