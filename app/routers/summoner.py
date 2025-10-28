"""Summoner API endpoints - Priority 1.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#summoner-v4
"""

from fastapi import APIRouter, Query
from loguru import logger

from app.cache.redis_cache import cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/summoner/v4", tags=["summoner"])


@router.get("/summoners/by-name/{summonerName}")
async def get_summoner_by_name(
    summonerName: str,
    region: str = Query(default=settings.riot_default_region, description="Region code (e.g., euw1, kr, na1)")
):
    """
    Get summoner by summoner name.

    This is the primary entry point for user lookups.

    API Reference: https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerName

    Args:
        summonerName: Summoner name (URL encoded)
        region: Region code (default: euw1)

    Returns:
        Summoner object from Riot API
    """
    logger.info("Fetching summoner by name", summoner=summonerName, region=region)

    # Check cache first
    cache_key = f"summoner:name:{region}:{summonerName}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for summoner", summoner=summonerName)
        return cached_data

    # Fetch from Riot API
    path = f"/lol/summoner/v4/summoners/by-name/{summonerName}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_summoner)

    logger.success("Summoner fetched successfully", summoner=summonerName, puuid=data.get("puuid", "unknown"))
    return data


@router.get("/summoners/by-puuid/{encryptedPUUID}")
async def get_summoner_by_puuid(
    encryptedPUUID: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get summoner by PUUID.

    API Reference: https://developer.riotgames.com/apis#summoner-v4/GET_getByPUUID

    Args:
        encryptedPUUID: Encrypted PUUID
        region: Region code

    Returns:
        Summoner object from Riot API
    """
    logger.info("Fetching summoner by PUUID", puuid=encryptedPUUID, region=region)

    # Check cache first
    cache_key = f"summoner:puuid:{region}:{encryptedPUUID}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for summoner by PUUID")
        return cached_data

    # Fetch from Riot API
    path = f"/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_summoner)

    logger.success("Summoner fetched by PUUID", name=data.get("name", "unknown"))
    return data


@router.get("/summoners/{encryptedSummonerId}")
async def get_summoner_by_id(
    encryptedSummonerId: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get summoner by summoner ID.

    API Reference: https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerId

    Args:
        encryptedSummonerId: Encrypted summoner ID
        region: Region code

    Returns:
        Summoner object from Riot API
    """
    logger.info("Fetching summoner by ID", summoner_id=encryptedSummonerId, region=region)

    # Check cache first
    cache_key = f"summoner:id:{region}:{encryptedSummonerId}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for summoner by ID")
        return cached_data

    # Fetch from Riot API
    path = f"/lol/summoner/v4/summoners/{encryptedSummonerId}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_summoner)

    logger.success("Summoner fetched by ID", name=data.get("name", "unknown"))
    return data
