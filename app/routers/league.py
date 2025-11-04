"""League API endpoints - Priority 5.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#league-v4
"""

from fastapi import APIRouter, Depends

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.league import (
    LeagueByQueueParams,
    LeagueByQueueQuery,
    LeagueEntriesBySummonerParams,
    LeagueEntriesBySummonerQuery,
    LeagueEntriesParams,
    LeagueEntriesQuery,
)
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/league/v4", tags=["league"])


@router.get("/challengerleagues/by-queue/{queue}")
async def get_challenger_league(
    params: LeagueByQueueParams = Depends(),
    query: LeagueByQueueQuery = Depends(),
):
    """
    Retrieves the Challenger league for a specific queue.

    This endpoint fetches a list of all players in the Challenger league for a
    given queue, providing a snapshot of the top-ranked players in a region.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getChallengerLeague

    Args:
        params (LeagueByQueueParams): The path parameters, containing the queue type.
        query (LeagueByQueueQuery): The query parameters, specifying the region.

    Returns:
        dict: A league object containing an array of summoner entries.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"league:challenger:{query.region}:{params.queue}",
        resource_name="Challenger league",
        fetch_fn=lambda: riot_client.get(
            f"/lol/league/v4/challengerleagues/by-queue/{params.queue}", query.region, False
        ),
        ttl=settings.cache_ttl_league,
        context={"queue": params.queue, "region": query.region},
    )


@router.get("/grandmasterleagues/by-queue/{queue}")
async def get_grandmaster_league(
    params: LeagueByQueueParams = Depends(),
    query: LeagueByQueueQuery = Depends(),
):
    """
    Retrieves the Grandmaster league for a specific queue.

    This endpoint fetches a list of all players in the Grandmaster league for a
    given queue, providing a snapshot of the top-ranked players in a region.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getGrandmasterLeague

    Args:
        params (LeagueByQueueParams): The path parameters, containing the queue type.
        query (LeagueByQueueQuery): The query parameters, specifying the region.

    Returns:
        dict: A league object containing an array of summoner entries.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"league:grandmaster:{query.region}:{params.queue}",
        resource_name="Grandmaster league",
        fetch_fn=lambda: riot_client.get(
            f"/lol/league/v4/grandmasterleagues/by-queue/{params.queue}", query.region, False
        ),
        ttl=settings.cache_ttl_league,
        context={"queue": params.queue, "region": query.region},
    )


@router.get("/masterleagues/by-queue/{queue}")
async def get_master_league(
    params: LeagueByQueueParams = Depends(),
    query: LeagueByQueueQuery = Depends(),
):
    """
    Retrieves the Master league for a specific queue.

    This endpoint fetches a list of all players in the Master league for a
    given queue, providing a snapshot of the top-ranked players in a region.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getMasterLeague

    Args:
        params (LeagueByQueueParams): The path parameters, containing the queue type.
        query (LeagueByQueueQuery): The query parameters, specifying the region.

    Returns:
        dict: A league object containing an array of summoner entries.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"league:master:{query.region}:{params.queue}",
        resource_name="Master league",
        fetch_fn=lambda: riot_client.get(
            f"/lol/league/v4/masterleagues/by-queue/{params.queue}", query.region, False
        ),
        ttl=settings.cache_ttl_league,
        context={"queue": params.queue, "region": query.region},
    )


@router.get("/entries/by-summoner/{encryptedSummonerId}")
async def get_league_entries_by_summoner(
    params: LeagueEntriesBySummonerParams = Depends(),
    query: LeagueEntriesBySummonerQuery = Depends(),
):
    """
    Retrieves the league entries for a summoner across all queues.

    This endpoint fetches a list of a summoner's league entries, providing
    details about their rank in each queue they participate in.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntriesForSummoner

    Args:
        params (LeagueEntriesBySummonerParams): The path parameters, containing the encrypted summoner ID.
        query (LeagueEntriesBySummonerQuery): The query parameters, specifying the region.

    Returns:
        list: A list of league entry objects.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/entries/by-summoner/{encryptedSummonerId}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"league:entries:summoner:{query.region}:{params.encryptedSummonerId}",
        resource_name="League entries",
        fetch_fn=lambda: riot_client.get(
            f"/lol/league/v4/entries/by-summoner/{params.encryptedSummonerId}", query.region, False
        ),
        ttl=settings.cache_ttl_league,
        context={"summoner_id": params.encryptedSummonerId, "region": query.region},
    )


@router.get("/entries/{queue}/{tier}/{division}")
async def get_league_entries(
    params: LeagueEntriesParams = Depends(),
    query: LeagueEntriesQuery = Depends(),
):
    """
    Retrieves league entries by queue, tier, and division.

    This endpoint provides paginated access to league entries for a specific
    rank, allowing for the retrieval of large sets of ranked players.

    API Reference: https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntries

    Args:
        params (LeagueEntriesParams): The path parameters, containing the queue, tier, and division.
        query (LeagueEntriesQuery): The query parameters, specifying the region and page number.

    Returns:
        list: A list of league entry objects, including summoner info, LP, and win/loss stats.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/league/v4/entries/RANKED_SOLO_5x5/DIAMOND/I?region=euw1&page=1"
    """
    # Build path with page parameter if not default
    path = f"/lol/league/v4/entries/{params.queue}/{params.tier}/{params.division}"
    if query.page != 1:
        path += f"?page={query.page}"

    return await fetch_with_cache(
        cache_key=f"league:entries:{query.region}:{params.queue}:{params.tier}:{params.division}:{query.page}",
        resource_name="League entries",
        fetch_fn=lambda: riot_client.get(path, query.region, False),
        ttl=settings.cache_ttl_league,
        context={
            "queue": params.queue,
            "tier": params.tier,
            "division": params.division,
            "page": query.page,
            "region": query.region,
        },
    )
