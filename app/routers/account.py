"""Account-V1 API endpoints (Riot ID lookups).

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#account-v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.cache.redis_cache import cache
from app.config import settings
from app.models.account import (
    AccountByPuuidParams,
    AccountByPuuidQuery,
    AccountByRiotIdParams,
    AccountByRiotIdQuery,
    ActiveShardParams,
    ActiveShardQuery,
)
from app.riot.client import riot_client

router = APIRouter(prefix="/riot/account/v1", tags=["account"])


@router.get("/accounts/by-puuid/{puuid}")
async def get_account_by_puuid(
    params: Annotated[AccountByPuuidParams, Depends()],
    query: Annotated[AccountByPuuidQuery, Depends()],
):
    """
    Retrieves an account by its PUUID.

    This endpoint fetches account information, including the game name and tag line,
    based on a player's unique PUUID. It supports regional routing and caches
    the results to improve performance.

    API Reference: https://developer.riotgames.com/apis#account-v1/GET_getByPuuid

    Args:
        params (AccountByPuuidParams): The path parameters, containing the PUUID.
        query (AccountByPuuidQuery): The query parameters, specifying the region.

    Returns:
        dict: A dictionary containing the account's PUUID, game name, and tag line.

    Example:
        >>> curl "http://127.0.0.1:8080/riot/account/v1/accounts/by-puuid/{puuid}?region=americas"
    """
    cache_key = f"account:puuid:{query.region}:{params.puuid}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for account by PUUID", puuid=params.puuid[:8])
        return cached_data

    # Fetch from Riot API (use platform endpoint for regional routing)
    logger.info("Fetching account by PUUID", puuid=params.puuid[:8], region=query.region)
    path = f"/riot/account/v1/accounts/by-puuid/{params.puuid}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=True)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_account)
    logger.success(
        "Account fetched by PUUID", puuid=params.puuid[:8], gameName=data.get("gameName")
    )

    return data


@router.get("/accounts/by-riot-id/{gameName}/{tagLine}")
async def get_account_by_riot_id(
    params: Annotated[AccountByRiotIdParams, Depends()],
    query: Annotated[AccountByRiotIdQuery, Depends()],
):
    """
    Retrieves an account by its Riot ID.

    This endpoint fetches account information based on a player's game name and
    tag line. It supports regional routing and caches the results to optimize
    performance.

    API Reference: https://developer.riotgames.com/apis#account-v1/GET_getByRiotId

    Args:
        params (AccountByRiotIdParams): The path parameters, containing the game name and tag line.
        query (AccountByRiotIdQuery): The query parameters, specifying the region.

    Returns:
        dict: A dictionary containing the account's PUUID, game name, and tag line.

    Example:
        >>> curl "http://127.0.0.1:8080/riot/account/v1/accounts/by-riot-id/Faker/KR1?region=americas"
    """
    cache_key = f"account:riotid:{query.region}:{params.gameName}:{params.tagLine}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug(
            "Cache hit for account by Riot ID", gameName=params.gameName, tagLine=params.tagLine
        )
        return cached_data

    # Fetch from Riot API (use platform endpoint for regional routing)
    logger.info(
        "Fetching account by Riot ID",
        gameName=params.gameName,
        tagLine=params.tagLine,
        region=query.region,
    )
    path = f"/riot/account/v1/accounts/by-riot-id/{params.gameName}/{params.tagLine}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=True)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_account)
    logger.success(
        "Account fetched by Riot ID", gameName=params.gameName, puuid=data.get("puuid", "")[:8]
    )

    return data


@router.get("/active-shards/by-game/{game}/by-puuid/{puuid}")
async def get_active_shard(
    params: Annotated[ActiveShardParams, Depends()],
    query: Annotated[ActiveShardQuery, Depends()],
):
    """
    Retrieves the active shard for a player.

    This endpoint identifies the active game server for a player based on their
    PUUID and the specified game. It supports regional routing and uses a short
    cache TTL to ensure the data remains current.

    API Reference: https://developer.riotgames.com/apis#account-v1/GET_getActiveShard

    Args:
        params (ActiveShardParams): The path parameters, containing the game and PUUID.
        query (ActiveShardQuery): The query parameters, specifying the region.

    Returns:
        dict: A dictionary containing the PUUID, game, and active shard.

    Example:
        >>> curl "http://127.0.0.1:8080/riot/account/v1/active-shards/by-game/val/by-puuid/{puuid}?region=americas"
    """
    cache_key = f"account:shard:{query.region}:{params.game}:{params.puuid}"

    # Check cache (short TTL as active shard can change)
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for active shard", puuid=params.puuid[:8], game=params.game)
        return cached_data

    # Fetch from Riot API (use platform endpoint for regional routing)
    logger.info(
        "Fetching active shard", puuid=params.puuid[:8], game=params.game, region=query.region
    )
    path = f"/riot/account/v1/active-shards/by-game/{params.game}/by-puuid/{params.puuid}"
    data = await riot_client.get(path, query.region, is_platform_endpoint=True)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_account_shard)
    logger.success("Active shard fetched", puuid=params.puuid[:8], shard=data.get("activeShard"))

    return data
