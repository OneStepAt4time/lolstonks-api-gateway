"""Tournament Stub V5 API endpoints (Testing/Tournament API mock).

This module provides FastAPI endpoints for the League of Legends Tournament Stub API,
which is a testing environment for the Tournament API. It allows developers to test
tournament-related functionality without affecting production data or requiring
tournament API keys.

The Tournament Stub API is essential for:
- Testing tournament code generation in a safe environment
- Developing tournament platforms without production risks
- Validating tournament workflows before deployment
- Mocking tournament scenarios for development
- Integration testing without production API keys

Tournament Stub vs Tournament API:
    The Tournament Stub API mirrors the production Tournament API but with:
    - No requirement for Tournament API keys
    - No actual creation of production resources
    - Mock responses that simulate production behavior
    - Safe testing environment for code development
    - Faster rate limits for testing
    - Isolated from production tournament systems

Supported Operations:
    Provider Registration (Mock):
        - Simulates provider registration
        - Returns mock provider IDs
        - No actual registration created
        - Useful for testing registration workflows

    Tournament Creation (Mock):
        - Simulates tournament creation
        - Returns mock tournament IDs
        - No actual tournament created
        - Safe for iterative testing

    Code Generation (Mock):
        - Simulates tournament code generation
        - Returns mock tournament codes
        - Codes are not valid in production
        - Useful for testing code generation logic

    Code Details (Mock):
        - Returns mock code metadata
        - Simulates code settings and configuration
        - No actual code data from production
        - Cached for consistency (5 min TTL)

    Code Updates (Mock):
        - Simulates code settings updates
        - Confirms update operations
        - No actual codes modified
        - Safe for testing update logic

    Lobby Events (Mock):
        - Returns mock lobby event data
        - Simulates tournament lobby activity
        - No actual lobby events from production
        - Cached for consistency (30 sec TTL)

Regional Behavior:
    - All operations respect region parameter
    - Mock responses are region-aware
    - Returns data consistent with requested region
    - No cross-region data leakage

Authentication:
    - Does NOT require Tournament API key
    - Can use standard Riot API key
    - No special permissions needed
    - Accessible for development testing

Caching Strategy:
    - Code details: 5 minutes TTL (moderately dynamic)
      * Mock data changes infrequently
      * Balance between consistency and efficiency

    - Lobby events: 30 seconds TTL (very dynamic)
      * Simulates real-time event behavior
      * Consistent with production API TTL
      * Short TTL for realistic testing

    - POST/PUT endpoints: No caching (state-changing operations)
      * Provider registration simulates resource creation
      * Tournament creation simulates resource allocation
      * Code generation simulates code allocation
      * Settings updates simulate code modification

API Reference:
    https://developer.riotgames.com/apis#tournament-stub-v5

See Also:
    app.routers.tournament: Production Tournament V5 API
    app.riot.client: HTTP client for Riot API communication
    app.cache.helpers: Caching utilities and decorators
"""

from typing import Annotated

from fastapi import APIRouter, Body, Query

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/tournament-stub/v5", tags=["tournament-stub"])


@router.post("/providers")
async def register_provider(
    region: Annotated[str, Query(description="Region code")],
    body: Annotated[dict, Body(description="Provider registration data")],
):
    """
    Register a tournament provider (testing environment).

    This endpoint simulates registering a tournament provider in the test environment.
    No actual provider is created, making it safe for testing without Tournament API keys.

    API Reference: https://developer.riotgames.com/apis#tournament-stub-v5/POST_registerProvider

    Args:
        region (str): The region to register the provider in.
        body (dict): Provider registration details containing:
            - url (str): The callback URL where tournament events would be sent.
            - region (str): The region for the provider.
            - tournamentProviderCallbackUrl (str): Alternative callback URL field.

    Returns:
        dict: A dictionary containing the mock provider ID.

    Note:
        This is a testing endpoint. No actual provider is created in production.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament-stub/v5/providers?region=euw1" \\
        >>>      -H "Content-Type: application/json" \\
        >>>      -d '{"url": "https://example.com/callback"}'
    """
    return await riot_client.post("/lol/tournament-stub/v5/providers", region, body)


@router.post("/tournaments")
async def create_tournament(
    region: Annotated[str, Query(description="Region code")],
    body: Annotated[dict, Body(description="Tournament creation data")],
):
    """
    Create a tournament (testing environment).

    This endpoint simulates creating a tournament in the test environment.
    No actual tournament is created, making it safe for testing without Tournament API keys.

    API Reference: https://developer.riotgames.com/apis#tournament-stub-v5/POST_registerTournament

    Args:
        region (str): The region to create the tournament in.
        body (dict): Tournament details containing:
            - name (str): The name of the tournament.
            - providerId (int): The ID of the registered provider.
            - description (str, optional): Description of the tournament.

    Returns:
        dict: A dictionary containing the mock tournament ID.

    Note:
        This is a testing endpoint. No actual tournament is created in production.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament-stub/v5/tournaments?region=euw1" \\
        >>>      -H "Content-Type: application/json" \\
        >>>      -d '{"name": "My Tournament", "providerId": 123}'
    """
    return await riot_client.post("/lol/tournament-stub/v5/tournaments", region, body)


@router.post("/codes")
async def create_tournament_codes(
    region: Annotated[str, Query(description="Region code")],
    body: Annotated[dict, Body(description="Tournament code generation data")],
):
    """
    Generate tournament codes (testing environment).

    This endpoint simulates generating tournament codes in the test environment.
    Generated codes are mock codes and cannot be used to create actual game lobbies.

    API Reference: https://developer.riotgames.com/apis#tournament-stub-v5/POST_createTournamentCode

    Args:
        region (str): The region to generate codes for.
        body (dict): Code generation details containing:
            - count (int): Number of codes to generate (max 1000).
            - mapType (str): Map type (e.g., "SUMMONERS_RIFT").
            - pickType (str): Pick type (e.g., "TOURNAMENT_DRAFT").
            - spectatorType (str): Spectator type (e.g., "LOBBYONLY", "ALL").
            - teamSize (int): Number of players per team (e.g., 5).
            - tournamentId (int): The ID of the tournament.
            - allowedSummonerIds (list, optional): List of summoner IDs allowed to join.
            - metadata (str, optional): Optional metadata string.

    Returns:
        list: A list of mock tournament code strings.

    Note:
        This is a testing endpoint. Generated codes are not valid in production.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament-stub/v5/codes?region=euw1" \\
        >>>      -H "Content-Type: application/json" \\
        >>>      -d '{
        >>>          "count": 5,
        >>>          "mapType": "SUMMONERS_RIFT",
        >>>          "pickType": "TOURNAMENT_DRAFT",
        >>>          "spectatorType": "LOBBYONLY",
        >>>          "teamSize": 5,
        >>>          "tournamentId": 456
        >>>      }'
    """
    return await riot_client.post("/lol/tournament-stub/v5/codes", region, body)


@router.get("/codes/{tournamentCode}")
async def get_tournament_code(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    force: bool | None = Query(default=None, description="Force refresh cache"),
):
    """
    Retrieve tournament code details (testing environment).

    This endpoint fetches mock metadata and settings for a tournament code.
    Returns simulated code configuration data for testing purposes.

    API Reference: https://developer.riotgames.com/apis#tournament-stub-v5/GET_getTournamentCode

    Args:
        tournamentCode (str): The tournament code to look up.
        region (str): The region to fetch the code data from.
        force (bool): If true, bypass cache and fetch from API.

    Returns:
        dict: A dictionary containing mock tournament code details, including:
            - mapType (str): Mock map type setting.
            - pickType (str): Mock pick type setting.
            - spectatorType (str): Mock spectator type setting.
            - teamSize (int): Mock team size setting.
            - tournamentId (int): Mock tournament ID.
            - lobbyName (str): Mock lobby name.
            - lobbyPassword (str): Mock lobby password.
            - code (str): The tournament code itself.
            - participants (list): Mock participant summoner IDs.

    Note:
        This is a testing endpoint. Returns mock data, not actual code details.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/tournament-stub/v5/codes/{tournamentCode}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"tournament_stub:code:{region}:{tournamentCode}",
        resource_name="Tournament stub code details",
        fetch_fn=lambda: riot_client.get(
            f"/lol/tournament-stub/v5/codes/{tournamentCode}", region, False
        ),
        ttl=settings.cache_ttl_tournament_code,
        context={"tournamentCode": tournamentCode, "region": region},
        force_refresh=force or False,
    )


@router.put("/codes/{tournamentCode}")
async def update_tournament_code(
    tournamentCode: str,
    region: Annotated[str, Query(description="Region code")],
    body: Annotated[dict, Body(description="Tournament code update data")],
):
    """
    Update tournament code settings (testing environment).

    This endpoint simulates updating settings for a tournament code.
    No actual codes are modified in production.

    API Reference: https://developer.riotgames.com/apis#tournament-stub-v5/PUT_updateTournamentCode

    Args:
        tournamentCode (str): The tournament code to update.
        region (str): The region of the tournament code.
        body (dict): Updated code settings:
            - mapType (str, optional): New map type.
            - pickType (str, optional): New pick type.
            - spectatorType (str, optional): New spectator type.
            - allowedSummonerIds (list, optional): Updated allowed summoner IDs.
            - metadata (str, optional): Updated metadata string.

    Returns:
        dict: Confirmation of the mock update.

    Note:
        This is a testing endpoint. No actual codes are modified in production.

    Example:
        >>> curl -X PUT "http://127.0.0.1:8080/lol/tournament-stub/v5/codes/{tournamentCode}?region=euw1" \\
        >>>      -H "Content-Type: application/json" \\
        >>>      -d '{"spectatorType": "ALL"}'
    """
    return await riot_client.put(f"/lol/tournament-stub/v5/codes/{tournamentCode}", region, body)


@router.get("/lobby-events/by-code/{tournamentCode}")
async def get_lobby_events(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    force: bool | None = Query(default=None, description="Force refresh cache"),
):
    """
    Retrieve lobby events for a tournament code (testing environment).

    This endpoint fetches mock lobby events for a tournament code.
    Returns simulated event data for testing lobby event handling logic.

    API Reference: https://developer.riotgames.com/apis#tournament-stub-v5/GET_getTournamentLobbyEvents

    Args:
        tournamentCode (str): The tournament code to get events for.
        region (str): The region to fetch the events from.
        force (bool): If true, bypass cache and fetch from API.

    Returns:
        dict: A dictionary containing mock lobby events:
            - eventList (list): List of mock lobby events, each with:
                - eventType (str): Type of event (e.g., "PlayerJoined", "PlayerReady").
                - timestamp (str): When the mock event occurred.
                - summonerId (str): Mock summoner ID involved in the event.
                - summonerName (str): Mock summoner name involved in the event.

    Note:
        This is a testing endpoint. Returns mock data, not actual lobby events.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/tournament-stub/v5/lobby-events/by-code/{tournamentCode}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"tournament_stub:lobby_events:{region}:{tournamentCode}",
        resource_name="Tournament stub lobby events",
        fetch_fn=lambda: riot_client.get(
            f"/lol/tournament-stub/v5/lobby-events/by-code/{tournamentCode}", region, False
        ),
        ttl=settings.cache_ttl_tournament_lobby_events,
        context={"tournamentCode": tournamentCode, "region": region},
        force_refresh=force or False,
    )
