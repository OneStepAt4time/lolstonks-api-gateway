"""Spectator-V5 API router for live game and featured games data.

This module provides FastAPI endpoints for retrieving information about games
currently in progress in League of Legends. This includes looking up active games
for specific players by PUUID, and fetching the list of featured games promoted
by Riot in the client.

The Spectator-V5 API is essential for:
- Live game tracking and spectator applications
- Streaming overlays showing current game info
- Tournament and esports live viewing tools
- Featured games discovery for high-profile matches
- Real-time player activity monitoring

Live Game Data:
    Active Game Information:
        - Game mode, map, and queue type
        - All 10 participants with summoner IDs and champion picks
        - Banned champions for each team
        - Game start time and current duration
        - Summoner spell selections
        - Rune/masteryIds (deprecated but may appear)

    Featured Games:
        - Curated list of high-profile ongoing matches
        - Similar data structure to active games
        - Includes professional players, streamers, high-ELO games
        - Client refresh interval for polling frequency
        - Updated periodically by Riot's selection algorithm

Regional Behavior:
    - Active games are region-specific (player must be in-game on that server)
    - Featured games list is region-specific
    - Returns 404 if player is not currently in a game
    - Game data becomes available shortly after game starts (champion select delay)

Caching Strategy:
    - Active games: Very short TTL (30 seconds default)
      * Game state changes rapidly
      * Player may finish game and start new one
      * Cache mostly useful for burst requests

    - Featured games: Short TTL (2-5 minutes)
      * List changes as games end and new ones start
      * Balances freshness with API efficiency
      * Riot provides recommended refresh interval in response

Error Handling:
    - 404 for active games is normal (player not in game)
    - Applications should handle 404 gracefully, not as an error
    - Featured games should always return data unless API issues

API Reference:
    https://developer.riotgames.com/apis#spectator-v5

See Also:
    app.models.spectator: Request/response models for spectator endpoints
    app.riot.client: HTTP client for Riot API communication
    app.cache.helpers: Caching utilities and decorators
"""

from fastapi import APIRouter, Depends

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.spectator import ActiveGameParams, ActiveGameQuery, FeaturedGamesQuery
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/spectator/v5", tags=["spectator"])


@router.get("/active-games/by-summoner/{encryptedPUUID}")
async def get_active_game(
    params: ActiveGameParams = Depends(),
    query: ActiveGameQuery = Depends(),
):
    """
    Retrieves the active game for a summoner.

    This endpoint fetches the current game information for a player, if they
    are currently in a game. It returns a 404 error if the player is not in a
    game.

    API Reference: https://developer.riotgames.com/apis#spectator-v5/GET_getCurrentGameInfoByPuuid

    Args:
        params.encryptedPUUID (str): The player's encrypted PUUID.
        query.region (str): The region to fetch the game data from.

    Returns:
        dict: A dictionary containing the active game information, including
              game mode, start time, participants, and banned champions.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/spectator/v5/active-games/by-summoner/{encryptedPUUID}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"spectator:active:{query.region}:{params.encryptedPUUID}",
        resource_name="Active game",
        fetch_fn=lambda: riot_client.get(
            f"/lol/spectator/v5/active-games/by-summoner/{params.encryptedPUUID}",
            query.region,
            False,
        ),
        ttl=settings.cache_ttl_spectator_active,
        context={"encryptedPUUID": params.encryptedPUUID[:8], "region": query.region},
    )


@router.get("/featured-games")
async def get_featured_games(
    query: FeaturedGamesQuery = Depends(),
):
    """
    Retrieves a list of featured games.

    This endpoint fetches a list of high-profile matches that are currently
    featured in the League of Legends client.

    API Reference: https://developer.riotgames.com/apis#spectator-v5/GET_getFeaturedGames

    Args:
        query.region (str): The region to fetch the featured games from.

    Returns:
        dict: A dictionary containing the list of featured games and the
              client refresh interval.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/spectator/v5/featured-games?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"spectator:featured:{query.region}",
        resource_name="Featured games",
        fetch_fn=lambda: riot_client.get("/lol/spectator/v5/featured-games", query.region, False),
        ttl=settings.cache_ttl_spectator_featured,
        context={"region": query.region},
    )
