"""Champion-Mastery-V4 API endpoints."""

from fastapi import APIRouter, Query
from loguru import logger

from app.config import settings
from app.riot.client import riot_client
from app.cache.redis_cache import cache

router = APIRouter(prefix="/lol/champion-mastery/v4", tags=["champion-mastery"])


@router.get("/champion-masteries/by-puuid/{puuid}")
async def get_all_champion_masteries(
    puuid: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get all champion mastery entries for a summoner by PUUID.

    Returns list of champion mastery objects sorted by champion level descending.
    """
    cache_key = f"mastery:all:{region}:{puuid}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for champion masteries", puuid=puuid[:8])
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching all champion masteries", puuid=puuid[:8], region=region)
    path = f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with 1 hour TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_mastery)
    logger.success("Champion masteries fetched", puuid=puuid[:8], count=len(data))

    return data


@router.get("/champion-masteries/by-puuid/{puuid}/by-champion/{championId}")
async def get_champion_mastery(
    puuid: str,
    championId: int,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get champion mastery entry for a specific champion.

    Returns champion mastery object with level, points, tokens, etc.
    """
    cache_key = f"mastery:champion:{region}:{puuid}:{championId}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for champion mastery", puuid=puuid[:8], championId=championId)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching champion mastery", puuid=puuid[:8], championId=championId, region=region)
    path = f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{championId}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with 1 hour TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_mastery)
    logger.success("Champion mastery fetched", puuid=puuid[:8], championId=championId)

    return data


@router.get("/champion-masteries/by-puuid/{puuid}/top")
async def get_top_champion_masteries(
    puuid: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    count: int = Query(default=3, ge=1, le=20, description="Number of top champions")
):
    """
    Get top N champion mastery entries for a summoner.

    Args:
        count: Number of top champions (1-20, default 3)

    Returns list of top champion mastery objects.
    """
    cache_key = f"mastery:top:{region}:{puuid}:{count}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for top masteries", puuid=puuid[:8], count=count)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching top champion masteries", puuid=puuid[:8], count=count, region=region)
    path = f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top"
    data = await riot_client.get(path, region, is_platform_endpoint=False, params={"count": count})

    # Cache with 1 hour TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_mastery)
    logger.success("Top champion masteries fetched", puuid=puuid[:8], count=len(data))

    return data


@router.get("/scores/by-puuid/{puuid}")
async def get_mastery_score(
    puuid: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get total mastery score for a summoner.

    Returns integer representing total mastery points across all champions.
    """
    cache_key = f"mastery:score:{region}:{puuid}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data is not None:  # Score can be 0
        logger.debug("Cache hit for mastery score", puuid=puuid[:8])
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching mastery score", puuid=puuid[:8], region=region)
    path = f"/lol/champion-mastery/v4/scores/by-puuid/{puuid}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with 1 hour TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_mastery)
    logger.success("Mastery score fetched", puuid=puuid[:8], score=data)

    return data
