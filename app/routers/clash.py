"""Clash-V1 API endpoints (Clash tournament data).

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#clash-v1
"""

from fastapi import APIRouter, Query

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/clash/v1", tags=["clash"])


@router.get("/players/by-puuid/{puuid}")
async def get_clash_player(
    puuid: str, region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Retrieves Clash player information by PUUID.

    This endpoint fetches a list of a player's Clash tournament registrations.
    Due to the dynamic nature of tournament data, it uses a short cache TTL.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getPlayersByPUUID

    Args:
        puuid (str): The player's unique PUUID.
        region (str): The region to fetch the Clash player data from.

    Returns:
        list: A list of player registration objects, each containing details
              like summonerId, teamId, position, and role.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/clash/v1/players/by-puuid/{puuid}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"clash:player:{region}:{puuid}",
        resource_name="Clash player",
        fetch_fn=lambda: riot_client.get(f"/lol/clash/v1/players/by-puuid/{puuid}", region, False),
        ttl=settings.cache_ttl_clash_player,
        context={"puuid": puuid[:8], "region": region},
    )


@router.get("/teams/{teamId}")
async def get_clash_team(
    teamId: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves Clash team information by team ID.

    This endpoint fetches detailed information about a Clash team, including
    its tournament ID, name, icon, tier, and list of players.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getTeamById

    Args:
        teamId (str): The ID of the Clash team.
        region (str): The region to fetch the team data from.

    Returns:
        dict: A dictionary containing the Clash team's details.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/clash/v1/teams/{teamId}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"clash:team:{region}:{teamId}",
        resource_name="Clash team",
        fetch_fn=lambda: riot_client.get(f"/lol/clash/v1/teams/{teamId}", region, False),
        ttl=settings.cache_ttl_clash_team,
        context={"teamId": teamId, "region": region},
    )


@router.get("/tournaments")
async def get_clash_tournaments(
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves all active and upcoming Clash tournaments.

    This endpoint fetches a list of all current and future Clash tournaments,
    including their schedules and themes.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getTournaments

    Args:
        region (str): The region to fetch the tournament data from.

    Returns:
        list: A list of tournament objects.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/clash/v1/tournaments?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"clash:tournaments:{region}",
        resource_name="Clash tournaments",
        fetch_fn=lambda: riot_client.get("/lol/clash/v1/tournaments", region, False),
        ttl=settings.cache_ttl_clash_tournament,
        context={"region": region},
    )


@router.get("/tournaments/{tournamentId}")
async def get_clash_tournament(
    tournamentId: int,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves a Clash tournament by its ID.

    This endpoint fetches detailed information about a specific Clash
    tournament, including its schedule and theme.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getTournamentById

    Args:
        tournamentId (int): The ID of the tournament.
        region (str): The region to fetch the tournament data from.

    Returns:
        dict: A dictionary containing the tournament's details.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/clash/v1/tournaments/{tournamentId}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"clash:tournament:{region}:{tournamentId}",
        resource_name="Clash tournament",
        fetch_fn=lambda: riot_client.get(
            f"/lol/clash/v1/tournaments/{tournamentId}", region, False
        ),
        ttl=settings.cache_ttl_clash_tournament,
        context={"tournamentId": tournamentId, "region": region},
    )


@router.get("/tournaments/by-team/{teamId}")
async def get_clash_tournament_by_team(
    teamId: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves the Clash tournament a team is registered for.

    This endpoint fetches the tournament object for the tournament that the
    specified team is a part of.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getTournamentByTeam

    Args:
        teamId (str): The ID of the team.
        region (str): The region to fetch the tournament data from.

    Returns:
        dict: A dictionary containing the tournament's details.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/clash/v1/tournaments/by-team/{teamId}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"clash:tournament:team:{region}:{teamId}",
        resource_name="Clash tournament by team",
        fetch_fn=lambda: riot_client.get(
            f"/lol/clash/v1/tournaments/by-team/{teamId}", region, False
        ),
        ttl=settings.cache_ttl_clash_team,
        context={"teamId": teamId, "region": region},
    )
