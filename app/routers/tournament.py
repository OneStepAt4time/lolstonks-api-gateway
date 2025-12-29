"""Tournament-V5 API endpoints (Tournament management and code generation).

This module provides FastAPI endpoints for the League of Legends Tournament API,
which allows third-party developers to create and manage tournaments, generate
tournament codes, and retrieve lobby events for tournament games.

The Tournament API is essential for:
- Creating custom tournaments and brackets
- Generating tournament codes for lobby creation
- Monitoring tournament lobby events and game states
- Managing provider registrations and tournament settings
- Building tournament platforms and esports tools

Tournament API Concepts:
    Provider Registration:
        - Applications must register as a provider before creating tournaments
        - Each provider has a unique registration callback URL
        - Providers can be created for different regions
        - Requires Tournament API key (different from standard API key)

    Tournament Creation:
        - Tournaments are created under a provider
        - Define tournament metadata (name, description)
        - Specify supported queue types and game settings
        - Return tournament ID for code generation

    Tournament Codes:
        - Unique codes used to create custom lobbies
        - Generated for specific tournaments with defined settings
        - Can specify pick type, map, spectator type, team size
        - Codes are single-use by default but can be reused
        - Maximum of 1000 codes per batch request

    Code Details:
        - Retrieve metadata about a tournament code
        - Includes all settings used to generate the code
        - Shows which lobby/game the code is associated with

    Lobby Events:
        - Real-time events from tournament lobbies
        - Tracks player actions (join, leave, ready, etc.)
        - Essential for monitoring tournament progress
        - Events are generated as lobby state changes

Regional Behavior:
    - All operations are region-specific
    - Provider registrations are per-region
    - Tournament codes work only in their creation region
    - Lobby events are region-specific to the game's server

Authentication Requirements:
    - Requires Tournament API key (NOT standard Riot API key)
    - Tournament API keys have different permissions
    - Standard API keys cannot access Tournament endpoints
    - Returns 403 Forbidden if using wrong API key type

Caching Strategy:
    - Code details: 5 minutes TTL (moderately dynamic)
      * Code metadata can change as lobbies progress
      * Balance between freshness and API efficiency

    - Lobby events: 30 seconds TTL (very dynamic)
      * Real-time event stream from active lobbies
      * Events occur frequently during lobby phase
      * Short TTL ensures fresh event data

    - POST/PUT endpoints: No caching (state-changing operations)
      * Provider registration creates new resources
      * Tournament creation modifies server state
      * Code generation allocates new codes
      * Settings updates modify existing codes

API Reference:
    https://developer.riotgames.com/apis#tournament-v5

See Also:
    app.models.tournament: Request/response models for tournament endpoints
    app.riot.client: HTTP client for Riot API communication
    app.cache.helpers: Caching utilities and decorators
"""

from typing import Annotated

from fastapi import APIRouter, Body, Query

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/tournament/v5", tags=["tournament"])


@router.post("/providers")
async def register_provider(
    region: Annotated[str, Query(description="Region code")],
    body: Annotated[dict, Body(description="Provider registration data")],
):
    """
    Register a tournament provider.

    This endpoint registers a new tournament provider with the specified callback URL.
    A provider must be registered before creating tournaments or generating codes.
    Each provider registration is region-specific and requires a Tournament API key.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/POST_registerProvider

    Args:
        region (str): The region to register the provider in.
        body (dict): Provider registration details containing:
            - url (str): The callback URL where tournament events will be sent.
            - region (str): The region for the provider.
            - tournamentProviderCallbackUrl (str): Alternative callback URL field.

    Returns:
        dict: A dictionary containing the provider ID.

    Raises:
        ForbiddenException: If using a standard API key instead of Tournament API key.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/providers?region=euw1" \\
        >>>      -H "Content-Type: application/json" \\
        >>>      -d '{"url": "https://example.com/callback"}'
    """
    return await riot_client.post("/lol/tournament/v5/providers", region, body)


@router.post("/tournaments")
async def create_tournament(
    region: Annotated[str, Query(description="Region code")],
    body: Annotated[dict, Body(description="Tournament creation data")],
):
    """
    Create a tournament.

    This endpoint creates a new tournament under a registered provider.
    The tournament can then be used to generate tournament codes for lobby creation.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/POST_registerTournament

    Args:
        region (str): The region to create the tournament in.
        body (dict): Tournament details containing:
            - name (str): The name of the tournament.
            - providerId (int): The ID of the registered provider.
            - description (str, optional): Description of the tournament.

    Returns:
        dict: A dictionary containing the tournament ID.

    Raises:
        ForbiddenException: If using a standard API key instead of Tournament API key.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/tournaments?region=euw1" \\
        >>>      -H "Content-Type: application/json" \\
        >>>      -d '{"name": "My Tournament", "providerId": 123}'
    """
    return await riot_client.post("/lol/tournament/v5/tournaments", region, body)


@router.post("/codes")
async def create_tournament_codes(
    region: Annotated[str, Query(description="Region code")],
    body: Annotated[dict, Body(description="Tournament code generation data")],
):
    """
    Generate tournament codes.

    This endpoint generates tournament codes for creating custom game lobbies.
    Each code is unique and can be used to create a lobby with the specified settings.
    Maximum of 1000 codes can be generated in a single request.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/POST_createTournamentCode

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
        list: A list of generated tournament code strings.

    Raises:
        ForbiddenException: If using a standard API key instead of Tournament API key.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/codes?region=euw1" \\
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
    return await riot_client.post("/lol/tournament/v5/codes", region, body)


@router.get("/codes/{tournamentCode}")
async def get_tournament_code(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    force: bool | None = Query(default=None, description="Force refresh cache"),
):
    """
    Retrieve tournament code details.

    This endpoint fetches the metadata and settings associated with a tournament code.
    Includes information about the code's configuration and the game it represents.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/GET_getTournamentCode

    Args:
        tournamentCode (str): The tournament code to look up.
        region (str): The region to fetch the code data from.
        force (bool): If true, bypass cache and fetch from API.

    Returns:
        dict: A dictionary containing the tournament code details, including:
            - mapType (str): Map type setting.
            - pickType (str): Pick type setting.
            - spectatorType (str): Spectator type setting.
            - teamSize (int): Team size setting.
            - tournamentId (int): Associated tournament ID.
            - lobbyName (str): Lobby name (if game started).
            - lobbyPassword (str): Lobby password (if set).
            - code (str): The tournament code itself.
            - participants (list): List of participant summoner IDs.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/tournament/v5/codes/{tournamentCode}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"tournament:code:{region}:{tournamentCode}",
        resource_name="Tournament code details",
        fetch_fn=lambda: riot_client.get(
            f"/lol/tournament/v5/codes/{tournamentCode}", region, False
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
    Update tournament code settings.

    This endpoint updates the settings of an existing tournament code.
    Use this to modify lobby parameters or metadata for a code.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/PUT_updateTournamentCode

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
        dict: Confirmation of the update.

    Raises:
        ForbiddenException: If using a standard API key instead of Tournament API key.

    Example:
        >>> curl -X PUT "http://127.0.0.1:8080/lol/tournament/v5/codes/{tournamentCode}?region=euw1" \\
        >>>      -H "Content-Type: application/json" \\
        >>>      -d '{"spectatorType": "ALL"}'
    """
    return await riot_client.put(f"/lol/tournament/v5/codes/{tournamentCode}", region, body)


@router.get("/lobby-events/by-code/{tournamentCode}")
async def get_lobby_events(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    force: bool | None = Query(default=None, description="Force refresh cache"),
):
    """
    Retrieve lobby events for a tournament code.

    This endpoint fetches real-time events from the lobby associated with
    a tournament code. Events include players joining, leaving, readying up,
    and other lobby state changes.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/GET_getTournamentLobbyEvents

    Args:
        tournamentCode (str): The tournament code to get events for.
        region (str): The region to fetch the events from.
        force (bool): If true, bypass cache and fetch from API.

    Returns:
        dict: A dictionary containing:
            - eventList (list): List of lobby events, each with:
                - eventType (str): Type of event (e.g., "PlayerJoined", "PlayerReady").
                - timestamp (str): When the event occurred.
                - summonerId (str): Summoner ID involved in the event.
                - summonerName (str): Summoner name involved in the event.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/tournament/v5/lobby-events/by-code/{tournamentCode}?region=euw1"
    """
    return await fetch_with_cache(
        cache_key=f"tournament:lobby_events:{region}:{tournamentCode}",
        resource_name="Tournament lobby events",
        fetch_fn=lambda: riot_client.get(
            f"/lol/tournament/v5/lobby-events/by-code/{tournamentCode}", region, False
        ),
        ttl=settings.cache_ttl_tournament_lobby_events,
        context={"tournamentCode": tournamentCode, "region": region},
        force_refresh=force or False,
    )
