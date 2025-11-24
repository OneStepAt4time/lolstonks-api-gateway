"""Account-V1 API router for Riot Games account operations.

This module provides FastAPI endpoints for retrieving account information using
Riot's Account-V1 API. It supports lookups by PUUID (Player Universally Unique
Identifier) and Riot ID (gameName + tagLine), as well as active shard queries
for cross-game functionality.

All endpoints implement regional routing and Redis caching to minimize API calls
and improve response times. Cache TTLs are configurable via application settings.

Regional Routing:
    - Account endpoints use regional routing (americas, europe, asia, esports)
    - PUUIDs are globally unique across all Riot games and regions
    - Active shard endpoints determine which game server a player is currently on

Caching Strategy:
    - Account lookups: Long TTL (account data rarely changes)
    - Active shards: Short TTL (server data can change frequently)
    - All caches support force refresh via query parameter

API Reference:
    https://developer.riotgames.com/apis#account-v1

See Also:
    app.models.account: Request/response models for account endpoints
    app.riot.client: HTTP client for Riot API communication
    app.cache.helpers: Caching utilities and decorators
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.account import (
    AccountByPuuidParams,
    AccountByPuuidQuery,
    AccountByRiotIdParams,
    AccountByRiotIdQuery,
    ActiveShardParams,
    ActiveShardQuery,
)
from app.riot.client import riot_client

router = APIRouter(prefix="/riot/account/v1", tags=["account"])


@router.get("/accounts/by-puuid/{puuid}")
async def get_account_by_puuid(
    params: Annotated[AccountByPuuidParams, Depends()],
    query: Annotated[AccountByPuuidQuery, Depends()],
):
    """Retrieves account information by Player Universally Unique Identifier (PUUID).

    This endpoint performs a reverse lookup from PUUID to Riot ID, returning the
    account's current gameName and tagLine. PUUIDs are persistent identifiers that
    remain constant even when players change their Riot IDs, making them ideal for
    long-term player tracking across all Riot games.

    The response is cached with a long TTL since account data changes infrequently.
    Regional routing is required as PUUIDs are globally unique but account data is
    stored regionally.

    HTTP Method: GET
    Rate Limit: Standard Riot API rate limits apply (varies by API key tier)
    Cache TTL: Configurable via settings.cache_ttl_account (default: 1 hour)

    Args:
        params: Path parameters containing:
            - puuid (str): The player's PUUID. Must be a valid 78-character encrypted
              identifier obtained from previous API calls.
        query: Query parameters containing:
            - region (str): Regional routing value. Must be one of: americas, europe,
              asia, esports. This determines which regional server to query.

    Returns:
        dict: Account information containing:
            - puuid (str): The player's PUUID (same as input)
            - gameName (str): Current display name (without tag)
            - tagLine (str): Current tag/discriminator (e.g., "NA1", "EUW")

    Raises:
        HTTPException: With status code:
            - 404: PUUID not found (invalid or non-existent account)
            - 429: Rate limit exceeded
            - 500: Riot API error or internal server error
            - 503: Riot API service unavailable

    Example:
        Basic lookup:

        ```bash
        curl "http://127.0.0.1:8080/riot/account/v1/accounts/by-puuid/abc123.../def456...?region=americas"
        ```

        Response:

        ```json
        {
            "puuid": "abc123...def456...",
            "gameName": "Faker",
            "tagLine": "KR1"
        }
        ```

    Note:
        - PUUIDs are case-sensitive and must be passed exactly as received
        - The region parameter affects routing but PUUID is globally unique
        - Cache can be bypassed using force=true query parameter (not shown in signature)

    See Also:
        get_account_by_riot_id: Lookup PUUID from gameName/tagLine
        app.models.account.AccountByPuuidParams: Path parameter validation
        app.models.account.AccountByPuuidQuery: Query parameter validation

    API Reference:
        https://developer.riotgames.com/apis#account-v1/GET_getByPuuid
    """
    return await fetch_with_cache(
        cache_key=f"account:puuid:{query.region}:{params.puuid}",
        resource_name="Account",
        fetch_fn=lambda: riot_client.get(
            f"/riot/account/v1/accounts/by-puuid/{params.puuid}", query.region, True
        ),
        ttl=settings.cache_ttl_account,
        context={"puuid": params.puuid[:8], "region": query.region},
    )


@router.get("/accounts/by-riot-id/{gameName}/{tagLine}")
async def get_account_by_riot_id(
    params: Annotated[AccountByRiotIdParams, Depends()],
    query: Annotated[AccountByRiotIdQuery, Depends()],
):
    """Retrieves account information by Riot ID (gameName and tagLine).

    This endpoint is the primary method for looking up accounts using their
    publicly visible Riot ID. It returns the account's PUUID, which can then be
    used for subsequent API calls. Riot IDs are the modern replacement for summoner
    names and work across all Riot games.

    The Riot ID format is "gameName#tagLine" (e.g., "Faker#KR1"), where:
    - gameName: The display name chosen by the player (3-16 characters)
    - tagLine: A unique discriminator assigned by Riot (3-5 characters)

    This endpoint is heavily cached as it's the entry point for most player lookups.

    HTTP Method: GET
    Rate Limit: Standard Riot API rate limits apply (varies by API key tier)
    Cache TTL: Configurable via settings.cache_ttl_account (default: 1 hour)

    Args:
        params: Path parameters containing:
            - gameName (str): The player's display name (case-insensitive). Spaces
              and special characters should be URL-encoded.
            - tagLine (str): The player's unique tag/discriminator (case-insensitive).
              Examples: "NA1", "EUW", "KR1", "0001".
        query: Query parameters containing:
            - region (str): Regional routing value. Must be one of: americas, europe,
              asia, esports. Choose based on account's home region.

    Returns:
        dict: Account information containing:
            - puuid (str): The player's globally unique PUUID (78 characters)
            - gameName (str): Current display name (canonical case)
            - tagLine (str): Current tag (canonical case)

    Raises:
        HTTPException: With status code:
            - 404: Riot ID not found (account doesn't exist or wrong region)
            - 400: Invalid gameName or tagLine format
            - 429: Rate limit exceeded
            - 500: Riot API error or internal server error
            - 503: Riot API service unavailable

    Example:
        Looking up a professional player:

        ```bash
        curl "http://127.0.0.1:8080/riot/account/v1/accounts/by-riot-id/Faker/KR1?region=asia"
        ```

        Looking up with spaces (URL-encoded):

        ```bash
        curl "http://127.0.0.1:8080/riot/account/v1/accounts/by-riot-id/Doublelift/NA1?region=americas"
        ```

        Response:

        ```json
        {
            "puuid": "abc123...def456...",
            "gameName": "Faker",
            "tagLine": "KR1"
        }
        ```

    Note:
        - gameName and tagLine are case-insensitive for lookup but returned in canonical case
        - Special characters in gameName must be URL-encoded (e.g., spaces as %20)
        - If lookup fails with 404, verify the region parameter matches the account's home region
        - The returned PUUID should be used for all subsequent API calls for this player
        - Region parameter does not always match game server (e.g., "europe" for both EUW and EUNE)

    See Also:
        get_account_by_puuid: Reverse lookup from PUUID to Riot ID
        app.models.account.AccountByRiotIdParams: Path parameter validation
        app.models.account.AccountByRiotIdQuery: Query parameter validation

    API Reference:
        https://developer.riotgames.com/apis#account-v1/GET_getByRiotId
    """
    return await fetch_with_cache(
        cache_key=f"account:riotid:{query.region}:{params.gameName}:{params.tagLine}",
        resource_name="Account",
        fetch_fn=lambda: riot_client.get(
            f"/riot/account/v1/accounts/by-riot-id/{params.gameName}/{params.tagLine}",
            query.region,
            True,
        ),
        ttl=settings.cache_ttl_account,
        context={"gameName": params.gameName, "tagLine": params.tagLine, "region": query.region},
    )


@router.get("/active-shards/by-game/{game}/by-puuid/{puuid}")
async def get_active_shard(
    params: Annotated[ActiveShardParams, Depends()],
    query: Annotated[ActiveShardQuery, Depends()],
):
    """Retrieves the active game shard (server) where a player is currently active.

    This endpoint determines which game-specific server a player is actively playing
    on or was last active on. It's primarily used for cross-game functionality and
    spectator features, allowing applications to route game-specific API calls to
    the correct regional shard.

    A "shard" represents a game-specific regional server. For example, a player with
    a PUUID might have:
    - League of Legends: Active on "na1" shard
    - Valorant: Active on "na" shard
    - Teamfight Tactics: Active on "na1" shard

    This endpoint uses a shorter cache TTL than account lookups since active shard
    data can change as players move between servers or games.

    HTTP Method: GET
    Rate Limit: Standard Riot API rate limits apply (varies by API key tier)
    Cache TTL: Configurable via settings.cache_ttl_account_shard (default: 5 minutes)

    Args:
        params: Path parameters containing:
            - game (str): The game identifier. Valid values include:
                * "val" - Valorant
                * "lor" - Legends of Runeterra
                * "lol" - League of Legends (less commonly used for this endpoint)
            - puuid (str): The player's PUUID (78-character encrypted identifier)
        query: Query parameters containing:
            - region (str): Regional routing value. Must be one of: americas, europe,
              asia, esports.

    Returns:
        dict: Active shard information containing:
            - puuid (str): The player's PUUID (same as input)
            - game (str): The game identifier (same as input)
            - activeShard (str): The specific game server/region where the player
              is currently active (e.g., "na1", "euw1", "kr")

    Raises:
        HTTPException: With status code:
            - 404: Player has no active shard for this game (never played or inactive)
            - 400: Invalid game identifier
            - 429: Rate limit exceeded
            - 500: Riot API error or internal server error
            - 503: Riot API service unavailable

    Example:
        Check Valorant active shard:

        ```bash
        curl "http://127.0.0.1:8080/riot/account/v1/active-shards/by-game/val/by-puuid/abc123.../def456...?region=americas"
        ```

        Check Legends of Runeterra active shard:

        ```bash
        curl "http://127.0.0.1:8080/riot/account/v1/active-shards/by-game/lor/by-puuid/abc123.../def456...?region=europe"
        ```

        Response:

        ```json
        {
            "puuid": "abc123...def456...",
            "game": "val",
            "activeShard": "na"
        }
        ```

    Note:
        - A 404 response means the player has never played the specified game or has been
          inactive long enough for shard data to expire
        - The activeShard value is game-specific and may not match League of Legends region codes
        - Use this endpoint before making game-specific API calls to ensure correct routing
        - Cache TTL is intentionally short to handle players switching regions or servers
        - For League of Legends specifically, the summoner endpoint is usually preferred

    See Also:
        get_account_by_puuid: Get account information from PUUID
        get_account_by_riot_id: Get PUUID from Riot ID
        app.models.account.ActiveShardParams: Path parameter validation
        app.models.account.ActiveShardQuery: Query parameter validation

    API Reference:
        https://developer.riotgames.com/apis#account-v1/GET_getActiveShard
    """
    return await fetch_with_cache(
        cache_key=f"account:shard:{query.region}:{params.game}:{params.puuid}",
        resource_name="Active shard",
        fetch_fn=lambda: riot_client.get(
            f"/riot/account/v1/active-shards/by-game/{params.game}/by-puuid/{params.puuid}",
            query.region,
            True,
        ),
        ttl=settings.cache_ttl_account_shard,
        context={"puuid": params.puuid[:8], "game": params.game, "region": query.region},
    )
