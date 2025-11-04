"""Match API endpoints - Priority 2 & 3.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#match-v5
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.cache.helpers import fetch_with_cache
from app.cache.tracking import tracker
from app.config import settings
from app.models.match import (
    MatchIdsByPuuidParams,
    MatchIdsByPuuidQuery,
    MatchParams,
    MatchQuery,
    MatchTimelineParams,
    MatchTimelineQuery,
)
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/match/v5", tags=["match"])


@router.get("/matches/by-puuid/{puuid}/ids")
async def get_match_ids_by_puuid(
    params: Annotated[MatchIdsByPuuidParams, Depends()],
    query: Annotated[MatchIdsByPuuidQuery, Depends()],
):
    """
    Retrieves a list of match IDs for a summoner.

    This endpoint fetches a list of match IDs based on a player's PUUID, with
    options for pagination and filtering by time, queue, and match type.

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID

    Args:
        params (MatchIdsByPuuidParams): The path parameters, containing the PUUID.
        query (MatchIdsByPuuidQuery): The query parameters, for pagination and filtering.

    Returns:
        list: A list of match IDs.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/match/v5/matches/by-puuid/{puuid}/ids?region=americas&count=20"
    """
    logger.info(
        "Fetching match IDs",
        puuid=params.puuid[:8],
        region=query.region,
        start=query.start,
        count=query.count,
        filters={
            "startTime": query.startTime,
            "endTime": query.endTime,
            "queue": query.queue,
            "type": query.type,
        },
    )

    # Build query parameters
    query_params = [f"start={query.start}", f"count={query.count}"]
    if query.startTime is not None:
        query_params.append(f"startTime={query.startTime}")
    if query.endTime is not None:
        query_params.append(f"endTime={query.endTime}")
    if query.queue is not None:
        query_params.append(f"queue={query.queue}")
    if query.type is not None:
        query_params.append(f"type={query.type}")

    # Build path with query parameters
    path = f"/lol/match/v5/matches/by-puuid/{params.puuid}/ids?{'&'.join(query_params)}"
    match_ids = await riot_client.get(path, query.region, is_platform_endpoint=True)

    logger.success("Match IDs fetched", count=len(match_ids), region=query.region)
    return match_ids


@router.get("/matches/{matchId}")
async def get_match(
    params: Annotated[MatchParams, Depends()],
    query: Annotated[MatchQuery, Depends()],
):
    """
    Retrieves match details by match ID.

    This endpoint fetches the core data for a specific match. It employs a
    dual-layer caching strategy, with a response cache and permanent tracking,
    to minimize redundant API calls.

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getMatch

    Args:
        params (MatchParams): The path parameters, containing the match ID.
        query (MatchQuery): The query parameters, specifying the region and an
                           optional force refresh flag.

    Returns:
        dict: A dictionary containing the match details.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/match/v5/matches/EUW1_123456789?region=americas"
    """
    # Check if match was already processed (if not forcing refresh)
    is_processed = False
    if not query.force:
        is_processed = await tracker.is_processed(query.region, params.matchId)

    # Use helper with force_refresh flag based on force parameter and processed status
    # If force=True OR not processed yet, skip cache check
    data = await fetch_with_cache(
        cache_key=f"match:{query.region}:{params.matchId}",
        resource_name="Match data",
        fetch_fn=lambda: riot_client.get(
            f"/lol/match/v5/matches/{params.matchId}", query.region, True
        ),
        ttl=settings.cache_ttl_match,
        context={"match_id": params.matchId, "region": query.region},
        force_refresh=query.force or not is_processed,
    )

    # Mark as processed after successful fetch (if not already processed)
    if not is_processed:
        await tracker.mark_processed(query.region, params.matchId)

    return data


@router.get("/matches/{matchId}/timeline")
async def get_match_timeline(
    params: Annotated[MatchTimelineParams, Depends()],
    query: Annotated[MatchTimelineQuery, Depends()],
):
    """
    Retrieves the timeline for a specific match.

    This endpoint fetches a detailed timeline of events for a given match,
    providing in-depth data for analysis.

    API Reference: https://developer.riotgames.com/apis#match-v5/GET_getTimeline

    Args:
        params (MatchTimelineParams): The path parameters, containing the match ID.
        query (MatchTimelineQuery): The query parameters, specifying the region.

    Returns:
        dict: A dictionary containing the match timeline data.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/match/v5/matches/EUW1_123456789/timeline?region=americas"
    """
    return await fetch_with_cache(
        cache_key=f"match:timeline:{query.region}:{params.matchId}",
        resource_name="Match timeline",
        fetch_fn=lambda: riot_client.get(
            f"/lol/match/v5/matches/{params.matchId}/timeline", query.region, True
        ),
        ttl=settings.cache_ttl_timeline,
        context={"match_id": params.matchId, "region": query.region},
    )
