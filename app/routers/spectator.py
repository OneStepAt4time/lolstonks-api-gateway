"""Spectator-V5 API endpoints."""

from fastapi import APIRouter, Query
from loguru import logger

from app.config import settings
from app.riot.client import riot_client
from app.cache.redis_cache import cache

router = APIRouter(prefix="/lol/spectator/v5", tags=["spectator"])


@router.get("/active-games/by-summoner/{puuid}")
async def get_active_game(
    puuid: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get current game information for a summoner (if in game).

    Returns 404 if player is not currently in a game.

    Returns:
        - gameId: Current game ID
        - gameMode: Game mode
        - gameStartTime: Start time (epoch ms)
        - participants: List of players in the game
        - bannedChampions: Banned champions
        - observers: Spectator key
    """
    # Note: Active games should not be cached heavily as they change quickly
    cache_key = f"spectator:active:{region}:{puuid}"

    # Check cache with short TTL
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for active game", puuid=puuid[:8])
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching active game", puuid=puuid[:8], region=region)
    path = f"/lol/spectator/v5/active-games/by-summoner/{puuid}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with very short TTL (30 seconds - game state changes quickly)
    await cache.set(cache_key, data, ttl=30)
    logger.success("Active game fetched", puuid=puuid[:8], gameId=data.get("gameId"))

    return data


@router.get("/featured-games")
async def get_featured_games(
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get list of featured games (high-profile matches shown in client).

    Returns:
        - gameList: List of featured game objects
        - clientRefreshInterval: Refresh interval (ms)
    """
    cache_key = f"spectator:featured:{region}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for featured games", region=region)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching featured games", region=region)
    path = "/lol/spectator/v5/featured-games"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with short TTL (2 minutes - featured games change frequently)
    await cache.set(cache_key, data, ttl=120)
    logger.success("Featured games fetched", region=region, count=len(data.get("gameList", [])))

    return data
