"""Summoner API endpoints - Priority 1.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#summoner-v4
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.cache.redis_cache import cache
from app.config import settings
from app.models.summoner import (
    SummonerByIdParams,
    SummonerByIdQuery,
    SummonerByNameParams,
    SummonerByNameQuery,
    SummonerByPuuidParams,
    SummonerByPuuidQuery,
)
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/summoner/v4", tags=["summoner"])


@router.get("/summoners/by-name/{summonerName}")
async def get_summoner_by_name(
    params: Annotated[SummonerByNameParams, Depends()],
    query: Annotated[SummonerByNameQuery, Depends()],
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
    logger.info("Fetching summoner by name", summoner=params.summonerName, region=query.region)

    # Check cache first
    cache_key = f"summoner:name:{query.region}:{params.summonerName}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for summoner", summoner=params.summonerName)
        return cached_data

    # Fetch from Riot API
    path = f"/lol/summoner/v4/summoners/by-name/{params.summonerName}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_summoner)

    logger.success(
        "Summoner fetched successfully",
        summoner=params.summonerName,
        puuid=data.get("puuid", "unknown"),
    )
    return data


@router.get("/summoners/by-puuid/{encryptedPUUID}")
async def get_summoner_by_puuid(
    params: Annotated[SummonerByPuuidParams, Depends()],
    query: Annotated[SummonerByPuuidQuery, Depends()],
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
    logger.info("Fetching summoner by PUUID", puuid=params.encryptedPUUID, region=query.region)

    # Check cache first
    cache_key = f"summoner:puuid:{query.region}:{params.encryptedPUUID}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for summoner by PUUID")
        return cached_data

    # Fetch from Riot API
    path = f"/lol/summoner/v4/summoners/by-puuid/{params.encryptedPUUID}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_summoner)

    logger.success("Summoner fetched by PUUID", name=data.get("name", "unknown"))
    return data


@router.get("/summoners/{encryptedSummonerId}")
async def get_summoner_by_id(
    params: Annotated[SummonerByIdParams, Depends()],
    query: Annotated[SummonerByIdQuery, Depends()],
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
    logger.info(
        "Fetching summoner by ID", summoner_id=params.encryptedSummonerId, region=query.region
    )

    # Check cache first
    cache_key = f"summoner:id:{query.region}:{params.encryptedSummonerId}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for summoner by ID")
        return cached_data

    # Fetch from Riot API
    path = f"/lol/summoner/v4/summoners/{params.encryptedSummonerId}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=False)

    # Store in cache
    await cache.set(cache_key, data, ttl=settings.cache_ttl_summoner)

    logger.success("Summoner fetched by ID", name=data.get("name", "unknown"))
    return data
