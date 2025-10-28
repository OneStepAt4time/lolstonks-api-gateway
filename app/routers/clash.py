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
    puuid: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get clash player info by PUUID.

    Returns list of clash tournament registrations for the player.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getPlayersByPUUID

    Returns:
        List of player registration objects with:
        - summonerId
        - teamId
        - position
        - role
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

    # Cache with short TTL (5 minutes)
    await cache.set(cache_key, data, ttl=300)
    logger.success("Clash player data fetched", puuid=puuid[:8], registrations=len(data))

    return data


@router.get("/teams/{teamId}")
async def get_clash_team(
    teamId: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get clash team by team ID.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getTeamById

    Returns:
        Team object with:
        - id: Team ID
        - tournamentId
        - name: Team name
        - iconId: Team icon
        - tier: Tournament tier
        - captain: Captain summoner ID
        - abbreviation: Team abbreviation
        - players: List of player objects
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

    # Cache with short TTL (5 minutes)
    await cache.set(cache_key, data, ttl=300)
    logger.success("Clash team data fetched", teamId=teamId, name=data.get("name"))

    return data


@router.get("/tournaments")
async def get_clash_tournaments(
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get all active and upcoming clash tournaments.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getTournaments

    Returns:
        List of tournament objects with:
        - id: Tournament ID
        - themeId: Theme ID
        - nameKey: Name key for localization
        - nameKeySecondary: Secondary name key
        - schedule: List of tournament phase objects
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

    # Cache with short TTL (10 minutes)
    await cache.set(cache_key, data, ttl=600)
    logger.success("Clash tournaments fetched", region=region, count=len(data))

    return data


@router.get("/tournaments/{tournamentId}")
async def get_clash_tournament(
    tournamentId: int,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get clash tournament by tournament ID.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getTournamentById

    Returns:
        Tournament object with:
        - id: Tournament ID
        - themeId: Theme ID
        - nameKey: Name key
        - nameKeySecondary: Secondary name key
        - schedule: Tournament schedule phases
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

    # Cache with short TTL (10 minutes)
    await cache.set(cache_key, data, ttl=600)
    logger.success("Clash tournament fetched", tournamentId=tournamentId)

    return data


@router.get("/tournaments/by-team/{teamId}")
async def get_clash_tournament_by_team(
    teamId: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get clash tournament that a team is registered for.

    API Reference: https://developer.riotgames.com/apis#clash-v1/GET_getTournamentByTeam

    Returns:
        Tournament object for the team's registered tournament.
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

    # Cache with short TTL (5 minutes)
    await cache.set(cache_key, data, ttl=300)
    logger.success("Clash tournament by team fetched", teamId=teamId)

    return data
