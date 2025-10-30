"""Clash-V1 API endpoints (Clash tournament data).

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#clash-v1
"""

from fastapi import APIRouter, Query
from loguru import logger

from app.config import settings
from app.riot.client import riot_client
from app.cache.redis_cache import cache

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
    cache_key = f"clash:player:{region}:{puuid}"

    # Check cache (short TTL as tournament data changes)
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for clash player", puuid=puuid[:8])
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching clash player data", puuid=puuid[:8], region=region)
    path = f"/lol/clash/v1/players/by-puuid/{puuid}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_clash_player)
    logger.success("Clash player data fetched", puuid=puuid[:8], registrations=len(data))

    return data


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
    cache_key = f"clash:team:{region}:{teamId}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for clash team", teamId=teamId)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching clash team data", teamId=teamId, region=region)
    path = f"/lol/clash/v1/teams/{teamId}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_clash_team)
    logger.success("Clash team data fetched", teamId=teamId, name=data.get("name"))

    return data


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
    cache_key = f"clash:tournaments:{region}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for clash tournaments", region=region)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching clash tournaments", region=region)
    path = "/lol/clash/v1/tournaments"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_clash_tournament)
    logger.success("Clash tournaments fetched", region=region, count=len(data))

    return data


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
    cache_key = f"clash:tournament:{region}:{tournamentId}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for clash tournament", tournamentId=tournamentId)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching clash tournament", tournamentId=tournamentId, region=region)
    path = f"/lol/clash/v1/tournaments/{tournamentId}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_clash_tournament)
    logger.success("Clash tournament fetched", tournamentId=tournamentId)

    return data


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
    cache_key = f"clash:tournament:team:{region}:{teamId}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for clash tournament by team", teamId=teamId)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching clash tournament by team", teamId=teamId, region=region)
    path = f"/lol/clash/v1/tournaments/by-team/{teamId}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_clash_team)
    logger.success("Clash tournament by team fetched", teamId=teamId)

    return data
