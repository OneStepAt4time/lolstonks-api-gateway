"""Challenges-V1 API endpoints (Player challenges and progression).

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#lol-challenges-v1
"""

from fastapi import APIRouter, Query

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/challenges/v1", tags=["challenges"])


@router.get("/challenges/config")
async def get_all_challenges_config(
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves the configuration for all challenges.

    This endpoint fetches a list of all available challenge configurations,
    including their IDs, localized names, and thresholds. The results are
    cached to optimize performance.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getAllChallengeConfigs

    Args:
        region (str): The region to fetch the challenges configuration for.

    Returns:
        list: A list of challenge configuration objects.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/challenges/v1/challenges/config?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"challenges:config:{region}",
        resource_name="Challenges config",
        fetch_fn=lambda: riot_client.get("/lol/challenges/v1/challenges/config", region, False),
        ttl=settings.cache_ttl_challenges_config,
        context={"region": region},
    )


@router.get("/challenges/{challengeId}/config")
async def get_challenge_config(
    challengeId: int,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves the configuration for a specific challenge.

    This endpoint fetches the configuration for a single challenge by its ID,
    including details like thresholds and localized names. The results are
    cached for better performance.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getChallengeConfigs

    Args:
        challengeId (int): The ID of the challenge to retrieve.
        region (str): The region to fetch the challenge configuration from.

    Returns:
        dict: A dictionary containing the challenge configuration.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/challenges/v1/challenges/1/config?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"challenges:config:{region}:{challengeId}",
        resource_name="Challenge config",
        fetch_fn=lambda: riot_client.get(
            f"/lol/challenges/v1/challenges/{challengeId}/config", region, False
        ),
        ttl=settings.cache_ttl_challenges_config,
        context={"challengeId": challengeId, "region": region},
    )


@router.get("/challenges/{challengeId}/leaderboards/by-level/{level}")
async def get_challenge_leaderboard(
    challengeId: int,
    level: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    limit: int = Query(default=None, ge=1, description="Limit results (optional)"),
):
    """
    Retrieves the leaderboard for a specific challenge and level.

    This endpoint fetches the leaderboard for a given challenge, filtered by
    a specific competitive level (e.g., MASTER, GRANDMASTER). It supports an
    optional limit on the number of results and uses a short cache TTL to
    keep the data fresh.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getChallengeLeaderboards

    Args:
        challengeId (int): The ID of the challenge.
        level (str): The competitive level to retrieve the leaderboard for.
        region (str): The region to fetch the leaderboard from.
        limit (int, optional): The maximum number of leaderboard entries to return.

    Returns:
        list: A list of leaderboard entries, each containing player PUUIDs and their values.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/challenges/v1/challenges/1/leaderboards/by-level/CHALLENGER?region=euw1&limit=10"
    """
    path = f"/lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}"
    params = {"limit": limit} if limit else None

    return await fetch_with_cache(
        cache_key=f"challenges:leaderboard:{region}:{challengeId}:{level}:{limit}",
        resource_name="Challenge leaderboard",
        fetch_fn=lambda: riot_client.get(path, region, False, params=params),
        ttl=settings.cache_ttl_challenges_leaderboard,
        context={"challengeId": challengeId, "level": level, "region": region},
    )


@router.get("/challenges/{challengeId}/percentiles")
async def get_challenge_percentiles(
    challengeId: int,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves the percentile distribution for a challenge.

    This endpoint fetches a map of percentile values for a specific challenge,
    allowing for a detailed statistical overview. The results are cached to
    optimize performance.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getChallengePercentiles

    Args:
        challengeId (int): The ID of the challenge.
        region (str): The region to fetch the percentiles from.

    Returns:
        dict: A dictionary mapping challenge values to their corresponding percentiles.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/challenges/v1/challenges/1/percentiles?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"challenges:percentiles:{region}:{challengeId}",
        resource_name="Challenge percentiles",
        fetch_fn=lambda: riot_client.get(
            f"/lol/challenges/v1/challenges/{challengeId}/percentiles", region, False
        ),
        ttl=settings.cache_ttl_challenges_percentiles,
        context={"challengeId": challengeId, "region": region},
    )


@router.get("/player-data/{puuid}")
async def get_player_challenges(
    puuid: str, region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Retrieves all challenge data for a player.

    This endpoint fetches a comprehensive overview of a player's challenge
    progression, including their total points, category points, and individual
    challenge progress. The results are cached to optimize performance.

    API Reference: https://developer.riotgames.com/apis#lol-challenges-v1/GET_getPlayerData

    Args:
        puuid (str): The player's unique PUUID.
        region (str): The region to fetch the player's challenge data from.

    Returns:
        dict: A dictionary containing the player's total points, category points,
              challenge progress, and preferences.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/challenges/v1/player-data/{puuid}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"challenges:player:{region}:{puuid}",
        resource_name="Player challenges",
        fetch_fn=lambda: riot_client.get(f"/lol/challenges/v1/player-data/{puuid}", region, False),
        ttl=settings.cache_ttl_challenges_player,
        context={"puuid": puuid[:8], "region": region},
    )
