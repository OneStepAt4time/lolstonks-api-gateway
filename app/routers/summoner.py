"""Summoner-V4 API router for summoner profile information.

This module provides FastAPI endpoints for retrieving League of Legends summoner
data, including lookups by summoner name, PUUID, and summoner ID. Summoner data
includes account level, profile icon, and encrypted identifiers needed for other
API endpoints.

The Summoner-V4 API is foundational for:
- Player profile applications showing level and icons
- Account verification and identity resolution
- Obtaining encrypted IDs for league and mastery queries
- Legacy summoner name lookups (before Riot ID migration)

Summoner Identifiers:
    Three types of summoner identifiers exist:

    1. Summoner Name (Legacy):
        - Display name visible in game
        - Region-specific and not unique across regions
        - Deprecated in favor of Riot IDs for new accounts
        - Still supported but being phased out

    2. PUUID (Player Universally Unique Identifier):
        - Global unique identifier across all Riot games
        - 78 characters, encrypted format
        - Persistent even when summoner name changes
        - Primary identifier for Match-V5 and Account-V1 APIs
        - Preferred for long-term player tracking

    3. Encrypted Summoner ID:
        - Region-specific encrypted identifier
        - Required for League-V4 (rank) and Champion-Mastery-V4 APIs
        - Changes if account transfers regions
        - Legacy identifier being replaced by PUUID

Regional Behavior:
    - Summoner data is region-specific (na1, euw1, kr, etc.)
    - Each region maintains its own summoner database
    - Account transfers create new summoner IDs in target region
    - PUUID remains constant across all regions

Caching Strategy:
    - Long TTL (1 hour default) for summoner data
    - Data rarely changes except for level and icon updates
    - Cache key includes region and lookup method
    - Force refresh available for updated data

Migration Note:
    Riot is transitioning from summoner names to Riot IDs (Account-V1 API).
    For new integrations, prefer using Account-V1 API for lookups, then use
    PUUID with Summoner-V4 to get encrypted summoner ID.

API Reference:
    https://developer.riotgames.com/apis#summoner-v4

See Also:
    app.routers.account: Modern Riot ID lookup endpoints
    app.models.summoner: Request/response models for summoner endpoints
    app.riot.client: HTTP client for Riot API communication
    app.cache.helpers: Caching utilities and decorators
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.summoner import (
    SummonerByIdParams,
    SummonerByIdQuery,
    SummonerByNameParams,
    SummonerByNameQuery,
    SummonerByPuuidParams,
    SummonerByPuuidQuery,
)
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/summoner/v4", tags=["summoner"])


@router.get("/summoners/by-name/{summonerName}")
async def get_summoner_by_name(
    params: Annotated[SummonerByNameParams, Depends()],
    query: Annotated[SummonerByNameQuery, Depends()],
):
    """
    Retrieves a summoner by their summoner name.

    This endpoint is the primary method for looking up a player by their in-game
    name. It is a foundational part of the API, providing the necessary IDs for
    further queries.

    API Reference: https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerName

    Args:
        params (SummonerByNameParams): The path parameters, containing the summoner name.
        query (SummonerByNameQuery): The query parameters, specifying the region.

    Returns:
        dict: A dictionary containing the summoner's information.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/summoner/v4/summoners/by-name/Faker?region=kr"
    """
    return await fetch_with_cache(
        cache_key=f"summoner:name:{query.region}:{params.summonerName}",
        resource_name="Summoner",
        fetch_fn=lambda: riot_client.get(
            f"/lol/summoner/v4/summoners/by-name/{params.summonerName}", query.region, False
        ),
        ttl=settings.cache_ttl_summoner,
        context={"summoner": params.summonerName, "region": query.region},
    )


@router.get("/summoners/by-puuid/{encryptedPUUID}")
async def get_summoner_by_puuid(
    params: Annotated[SummonerByPuuidParams, Depends()],
    query: Annotated[SummonerByPuuidQuery, Depends()],
):
    """
    Retrieves a summoner by their PUUID.

    This endpoint fetches summoner information using a player's unique PUUID,
    which is a persistent and globally unique identifier.

    API Reference: https://developer.riotgames.com/apis#summoner-v4/GET_getByPUUID

    Args:
        params (SummonerByPuuidParams): The path parameters, containing the encrypted PUUID.
        query (SummonerByPuuidQuery): The query parameters, specifying the region.

    Returns:
        dict: A dictionary containing the summoner's information.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"summoner:puuid:{query.region}:{params.encryptedPUUID}",
        resource_name="Summoner",
        fetch_fn=lambda: riot_client.get(
            f"/lol/summoner/v4/summoners/by-puuid/{params.encryptedPUUID}", query.region, False
        ),
        ttl=settings.cache_ttl_summoner,
        context={"puuid": params.encryptedPUUID, "region": query.region},
    )


@router.get("/summoners/{encryptedSummonerId}")
async def get_summoner_by_id(
    params: Annotated[SummonerByIdParams, Depends()],
    query: Annotated[SummonerByIdQuery, Depends()],
):
    """
    Retrieves a summoner by their summoner ID.

    This endpoint fetches summoner information using a player's encrypted
    summoner ID, which is a region-specific identifier.

    API Reference: https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerId

    Args:
        params (SummonerByIdParams): The path parameters, containing the encrypted summoner ID.
        query (SummonerByIdQuery): The query parameters, specifying the region.

    Returns:
        dict: A dictionary containing the summoner's information.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/summoner/v4/summoners/{encryptedSummonerId}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"summoner:id:{query.region}:{params.encryptedSummonerId}",
        resource_name="Summoner",
        fetch_fn=lambda: riot_client.get(
            f"/lol/summoner/v4/summoners/{params.encryptedSummonerId}", query.region, False
        ),
        ttl=settings.cache_ttl_summoner,
        context={"summoner_id": params.encryptedSummonerId, "region": query.region},
    )
