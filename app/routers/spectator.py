"""Spectator-V5 API endpoints.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#spectator-v5
"""

from fastapi import APIRouter, Query
from loguru import logger

from app.config import settings
from app.riot.client import riot_client
from app.cache.redis_cache import cache

router = APIRouter(prefix="/lol/spectator/v5", tags=["spectator"])


@router.get("/active-games/by-summoner/{puuid}")
async def get_active_game(
    puuid: str, region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Retrieves the active game for a summoner.

    This endpoint fetches the current game information for a player, if they
    are currently in a game. It returns a 404 error if the player is not in a
    game.

    API Reference: https://developer.riotgames.com/apis#spectator-v5/GET_getCurrentGameInfoByPuuid

    Args:
        puuid (str): The player's unique PUUID.
        region (str): The region to fetch the game data from.

    Returns:
        dict: A dictionary containing the active game information, including
              game mode, start time, participants, and banned champions.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/spectator/v5/active-games/by-summoner/{puuid}?region=euw1"
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

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_spectator_active)
    logger.success("Active game fetched", puuid=puuid[:8], gameId=data.get("gameId"))

    return data


@router.get("/featured-games")
async def get_featured_games(
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves a list of featured games.

    This endpoint fetches a list of high-profile matches that are currently
    featured in the League of Legends client.

    API Reference: https://developer.riotgames.com/apis#spectator-v5/GET_getFeaturedGames

    Args:
        region (str): The region to fetch the featured games from.

    Returns:
        dict: A dictionary containing the list of featured games and the
              client refresh interval.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/spectator/v5/featured-games?region=euw1"
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

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_spectator_featured)
    logger.success("Featured games fetched", region=region, count=len(data.get("gameList", [])))

    return data
