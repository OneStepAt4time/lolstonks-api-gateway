"""Champion-Mastery-V4 API endpoints.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#champion-mastery-v4
"""

from fastapi import APIRouter, Query

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/champion-mastery/v4", tags=["champion-mastery"])


@router.get("/champion-masteries/by-puuid/{puuid}")
async def get_all_champion_masteries(
    puuid: str, region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Retrieves all champion mastery entries for a summoner.

    This endpoint fetches a list of all champion mastery objects for a given
    player, sorted by champion level in descending order. The results are
    cached to optimize performance.

    API Reference: https://developer.riotgames.com/apis#champion-mastery-v4/GET_getAllChampionMasteries

    Args:
        puuid (str): The player's unique PUUID.
        region (str): The region to fetch the champion mastery data from.

    Returns:
        list: A list of champion mastery objects.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"mastery:all:{region}:{puuid}",
        resource_name="Champion masteries",
        fetch_fn=lambda: riot_client.get(
            f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}", region, False
        ),
        ttl=settings.cache_ttl_mastery,
        context={"puuid": puuid[:8], "region": region},
    )


@router.get("/champion-masteries/by-puuid/{puuid}/by-champion/{championId}")
async def get_champion_mastery(
    puuid: str,
    championId: int,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
):
    """
    Retrieves the champion mastery entry for a specific champion.

    This endpoint fetches a single champion mastery object, which includes
    details like level, points, and tokens. The results are cached for
    improved performance.

    API Reference: https://developer.riotgames.com/apis#champion-mastery-v4/GET_getChampionMastery

    Args:
        puuid (str): The player's unique PUUID.
        championId (int): The ID of the champion.
        region (str): The region to fetch the mastery data from.

    Returns:
        dict: A dictionary containing the champion mastery information.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/1?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"mastery:champion:{region}:{puuid}:{championId}",
        resource_name="Champion mastery",
        fetch_fn=lambda: riot_client.get(
            f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{championId}",
            region,
            False,
        ),
        ttl=settings.cache_ttl_mastery,
        context={"puuid": puuid[:8], "championId": championId, "region": region},
    )


@router.get("/champion-masteries/by-puuid/{puuid}/top")
async def get_top_champion_masteries(
    puuid: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    count: int = Query(default=3, ge=1, le=20, description="Number of top champions"),
):
    """
    Retrieves the top N champion mastery entries for a summoner.

    This endpoint fetches a list of the highest-scoring champion mastery
    objects for a player. The number of champions to return can be specified
    with the `count` parameter.

    API Reference: https://developer.riotgames.com/apis#champion-mastery-v4/GET_getTopChampionMasteries

    Args:
        puuid (str): The player's unique PUUID.
        region (str): The region to fetch the mastery data from.
        count (int): The number of top champions to retrieve (1-20, default 3).

    Returns:
        list: A list of the top champion mastery objects.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?region=euw1&count=5"
    """
    return await fetch_with_cache(
        cache_key=f"mastery:top:{region}:{puuid}:{count}",
        resource_name="Top champion masteries",
        fetch_fn=lambda: riot_client.get(
            f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top",
            region,
            False,
            params={"count": count},
        ),
        ttl=settings.cache_ttl_mastery,
        context={"puuid": puuid[:8], "count": count, "region": region},
    )


@router.get("/scores/by-puuid/{puuid}")
async def get_mastery_score(
    puuid: str, region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Retrieves the total mastery score for a summoner.

    This endpoint calculates and returns the total mastery score, which is the
    sum of all individual champion mastery levels.

    API Reference: https://developer.riotgames.com/apis#champion-mastery-v4/GET_getChampionMasteryScore

    Args:
        puuid (str): The player's unique PUUID.
        region (str): The region to fetch the mastery score from.

    Returns:
        int: The total mastery score for the summoner.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/champion-mastery/v4/scores/by-puuid/{puuid}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"mastery:score:{region}:{puuid}",
        resource_name="Mastery score",
        fetch_fn=lambda: riot_client.get(
            f"/lol/champion-mastery/v4/scores/by-puuid/{puuid}", region, False
        ),
        ttl=settings.cache_ttl_mastery,
        context={"puuid": puuid[:8], "region": region},
    )
