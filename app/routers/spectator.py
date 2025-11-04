"""Spectator-V5 API endpoints.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#spectator-v5
"""

from fastapi import APIRouter, Query

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

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
    return await fetch_with_cache(
        cache_key=f"spectator:active:{region}:{puuid}",
        resource_name="Active game",
        fetch_fn=lambda: riot_client.get(
            f"/lol/spectator/v5/active-games/by-summoner/{puuid}", region, False
        ),
        ttl=settings.cache_ttl_spectator_active,
        context={"puuid": puuid[:8], "region": region},
    )


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
    return await fetch_with_cache(
        cache_key=f"spectator:featured:{region}",
        resource_name="Featured games",
        fetch_fn=lambda: riot_client.get("/lol/spectator/v5/featured-games", region, False),
        ttl=settings.cache_ttl_spectator_featured,
        context={"region": region},
    )
