"""Account-V1 API endpoints (Riot ID lookups)."""

from fastapi import APIRouter, Query
from loguru import logger

from app.config import settings
from app.riot.client import riot_client
from app.cache.redis_cache import cache

router = APIRouter(prefix="/riot/account/v1", tags=["account"])


@router.get("/accounts/by-puuid/{puuid}")
async def get_account_by_puuid(
    puuid: str,
    region: str = Query(default="americas", description="Regional routing value (americas, europe, asia, sea)")
):
    """
    Get account by PUUID.

    Note: This endpoint uses regional routing (americas, europe, asia, sea).

    Returns:
        - puuid: Player UUID
        - gameName: Riot ID game name
        - tagLine: Riot ID tag line
    """
    cache_key = f"account:puuid:{region}:{puuid}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for account by PUUID", puuid=puuid[:8])
        return cached_data

    # Fetch from Riot API (use platform endpoint for regional routing)
    logger.info("Fetching account by PUUID", puuid=puuid[:8], region=region)
    path = f"/riot/account/v1/accounts/by-puuid/{puuid}"
    data = await riot_client.get(path, region, is_platform_endpoint=True)

    # Cache with 1 hour TTL
    await cache.set(cache_key, data, ttl=3600)
    logger.success("Account fetched by PUUID", puuid=puuid[:8], gameName=data.get("gameName"))

    return data


@router.get("/accounts/by-riot-id/{gameName}/{tagLine}")
async def get_account_by_riot_id(
    gameName: str,
    tagLine: str,
    region: str = Query(default="americas", description="Regional routing value (americas, europe, asia, sea)")
):
    """
    Get account by Riot ID (gameName#tagLine).

    Note: This endpoint uses regional routing (americas, europe, asia, sea).

    Args:
        gameName: Riot ID game name (before the #)
        tagLine: Riot ID tag line (after the #)
        region: Regional routing (americas, europe, asia, sea)

    Returns:
        - puuid: Player UUID
        - gameName: Riot ID game name
        - tagLine: Riot ID tag line
    """
    cache_key = f"account:riotid:{region}:{gameName}:{tagLine}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for account by Riot ID", gameName=gameName, tagLine=tagLine)
        return cached_data

    # Fetch from Riot API (use platform endpoint for regional routing)
    logger.info("Fetching account by Riot ID", gameName=gameName, tagLine=tagLine, region=region)
    path = f"/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    data = await riot_client.get(path, region, is_platform_endpoint=True)

    # Cache with 1 hour TTL
    await cache.set(cache_key, data, ttl=3600)
    logger.success("Account fetched by Riot ID", gameName=gameName, puuid=data.get("puuid", "")[:8])

    return data


@router.get("/active-shards/by-game/{game}/by-puuid/{puuid}")
async def get_active_shard(
    game: str,
    puuid: str,
    region: str = Query(default="americas", description="Regional routing value (americas, europe, asia, sea)")
):
    """
    Get active shard for a player (which server they're actively playing on).

    Note: This endpoint uses regional routing (americas, europe, asia, sea).

    Args:
        game: Game identifier (val for Valorant, lor for LoR)
        puuid: Player UUID
        region: Regional routing

    Returns:
        - puuid: Player UUID
        - game: Game identifier
        - activeShard: Active shard identifier
    """
    cache_key = f"account:shard:{region}:{game}:{puuid}"

    # Check cache (short TTL as active shard can change)
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for active shard", puuid=puuid[:8], game=game)
        return cached_data

    # Fetch from Riot API (use platform endpoint for regional routing)
    logger.info("Fetching active shard", puuid=puuid[:8], game=game, region=region)
    path = f"/riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}"
    data = await riot_client.get(path, region, is_platform_endpoint=True)

    # Cache with short TTL (10 minutes)
    await cache.set(cache_key, data, ttl=600)
    logger.success("Active shard fetched", puuid=puuid[:8], shard=data.get("activeShard"))

    return data
