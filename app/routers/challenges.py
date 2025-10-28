"""Challenges-V1 API endpoints (Player challenges and progression).

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#lol-challenges-v1
"""

from fastapi import APIRouter, Query
from loguru import logger

from app.config import settings
from app.riot.client import riot_client
from app.cache.redis_cache import cache

router = APIRouter(prefix="/lol/challenges/v1", tags=["challenges"])


@router.get("/challenges/config")
async def get_all_challenges_config(
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Get configuration for all challenges.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getAllChallengeConfigs

    Returns list of all challenge configuration objects with:
    - id: Challenge ID
    - localizedNames: Localized challenge names
    - state: Challenge state (ENABLED, DISABLED, etc.)
    - leaderboard: Whether has leaderboard
    - thresholds: Thresholds for tiers
    """
    cache_key = f"challenges:config:{region}"

    # Check cache (challenges config changes rarely)
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for challenges config", region=region)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching challenges config", region=region)
    path = "/lol/challenges/v1/challenges/config"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_challenges_config)
    logger.success("Challenges config fetched", region=region, count=len(data))

    return data


@router.get("/challenges/{challengeId}/config")
async def get_challenge_config(
    challengeId: int,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Get configuration for a specific challenge.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getChallengeConfigs

    Returns:
        Challenge configuration object with thresholds, localized names, etc.
    """
    cache_key = f"challenges:config:{region}:{challengeId}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for challenge config", challengeId=challengeId)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching challenge config", challengeId=challengeId, region=region)
    path = f"/lol/challenges/v1/challenges/{challengeId}/config"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_challenges_config)
    logger.success("Challenge config fetched", challengeId=challengeId)

    return data


@router.get("/challenges/{challengeId}/leaderboards/by-level/{level}")
async def get_challenge_leaderboard(
    challengeId: int,
    level: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    limit: int = Query(default=None, ge=1, description="Limit results (optional)"),
):
    """
    Get leaderboard for a specific challenge at a specific level.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getChallengeLeaderboards

    Args:
        challengeId: Challenge ID
        level: Challenge level (MASTER, GRANDMASTER, CHALLENGER)
        limit: Optional limit on results

    Returns:
        List of leaderboard entries with player PUUIDs and values.
    """
    cache_key = f"challenges:leaderboard:{region}:{challengeId}:{level}:{limit}"

    # Check cache (short TTL as leaderboards change frequently)
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for challenge leaderboard", challengeId=challengeId, level=level)
        return cached_data

    # Fetch from Riot API
    logger.info(
        "Fetching challenge leaderboard", challengeId=challengeId, level=level, region=region
    )
    path = f"/lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}"
    params = {"limit": limit} if limit else None
    data = await riot_client.get(path, region, is_platform_endpoint=False, params=params)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_challenges_leaderboard)
    logger.success("Challenge leaderboard fetched", challengeId=challengeId, level=level)

    return data


@router.get("/challenges/{challengeId}/percentiles")
async def get_challenge_percentiles(
    challengeId: int,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Get percentile distribution for a challenge.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getChallengePercentiles

    Returns map of challenge values to percentiles.
    """
    cache_key = f"challenges:percentiles:{region}:{challengeId}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for challenge percentiles", challengeId=challengeId)
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching challenge percentiles", challengeId=challengeId, region=region)
    path = f"/lol/challenges/v1/challenges/{challengeId}/percentiles"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_challenges_percentiles)
    logger.success("Challenge percentiles fetched", challengeId=challengeId)

    return data


@router.get("/player-data/{puuid}")
async def get_player_challenges(
    puuid: str, region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Get all challenge data for a player by PUUID.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getPlayerData

    Returns:
        - totalPoints: Total challenge points
        - categoryPoints: Points per category
        - challenges: List of all challenge progress
        - preferences: Player challenge preferences
    """
    cache_key = f"challenges:player:{region}:{puuid}"

    # Check cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.debug("Cache hit for player challenges", puuid=puuid[:8])
        return cached_data

    # Fetch from Riot API
    logger.info("Fetching player challenges", puuid=puuid[:8], region=region)
    path = f"/lol/challenges/v1/player-data/{puuid}"
    data = await riot_client.get(path, region, is_platform_endpoint=False)

    # Cache with configured TTL
    await cache.set(cache_key, data, ttl=settings.cache_ttl_challenges_player)
    logger.success(
        "Player challenges fetched",
        puuid=puuid[:8],
        totalPoints=data.get("totalPoints", {}).get("current", 0),
    )

    return data
