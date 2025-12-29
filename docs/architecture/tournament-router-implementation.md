# Tournament Router Implementation Guide

**Version**: 1.0
**Date**: 2025-01-29
**Related Documents**:
- [tournament-router-design.md](./tournament-router-design.md) - Complete architecture design
- [tournament-router-diagram.md](./tournament-router-diagram.md) - Visual diagrams

---

## Quick Start

This guide provides step-by-step instructions for implementing the Tournament V5 and Tournament Stub V5 routers.

**Estimated Time**: 4-5 hours
**Difficulty**: Intermediate
**Prerequisites**: Python 3.11+, FastAPI experience

---

## Table of Contents

1. [Phase 1: Foundation](#phase-1-foundation) - 1 hour
2. [Phase 2: HTTP Client Enhancement](#phase-2-http-client-enhancement) - 30 minutes
3. [Phase 3: Tournament Router](#phase-3-tournament-router) - 1.5 hours
4. [Phase 4: Stub Router](#phase-4-stub-router) - 30 minutes
5. [Phase 5: Integration](#phase-5-integration) - 15 minutes
6. [Phase 6: Testing](#phase-6-testing) - 1 hour
7. [Verification](#verification)

---

## Phase 1: Foundation

### Step 1.1: Add Cache TTL Settings

**File**: `app/config.py`

**Location**: After Clash TTLs (around line 190)

**Add**:
```python
# TOURNAMENT-V5: Tournament management and codes
cache_ttl_tournament_code: int = 300  # 5 minutes - Code details
cache_ttl_tournament_lobby_events: int = 30  # 30 seconds - Very dynamic
```

**Complete context**:
```python
# CLASH-V1: Clash tournament data
cache_ttl_clash_player: int = 300  # 5 minutes - Player info
cache_ttl_clash_team: int = 300  # 5 minutes - Team info
cache_ttl_clash_tournament: int = 600  # 10 minutes - Tournament schedule

# TOURNAMENT-V5: Tournament management and codes
cache_ttl_tournament_code: int = 300  # 5 minutes - Code details
cache_ttl_tournament_lobby_events: int = 30  # 30 seconds - Very dynamic

# CHAMPION-V3: Champion rotation
cache_ttl_champion_rotation: int = 86400  # 24 hours - Rotation changes weekly
```

**Verify**:
```bash
cd D:\LoLProjects\lolstonks-api-gateway
uv run python -c "from app.config import settings; print(settings.cache_ttl_tournament_code)"
# Should output: 300
```

### Step 1.2: Export Routers

**File**: `app/routers/__init__.py`

**Current state**: File is likely minimal or empty

**Add**:
```python
"""Routers package for lolstonks-api-gateway."""

from app.routers import (
    account,
    champion,
    champion_mastery,
    clash,
    league,
    league_exp,
    match,
    platform,
    spectator,
    summoner,
    challenges,
    security,
    tournament,
    tournament_stub,
)

__all__ = [
    "account",
    "champion",
    "champion_mastery",
    "clash",
    "league",
    "league_exp",
    "match",
    "platform",
    "spectator",
    "summoner",
    "challenges",
    "security",
    "tournament",
    "tournament_stub",
]
```

**Verify**:
```bash
uv run python -c "from app.routers import tournament, tournament_stub; print('OK')"
# Should output: OK
```

---

## Phase 2: HTTP Client Enhancement

### Step 2.1: Add POST Method

**File**: `app/riot/client.py`

**Location**: After the `get()` method (around line 393)

**Add**:
```python
async def post(
    self,
    path: str,
    region: str,
    is_platform_endpoint: bool = False,
    data: dict | None = None,
) -> dict:
    """
    Makes a POST request to the Riot API with rate limiting and smart key fallback.

    This method handles POST requests for state-changing operations like creating
    tournaments or generating codes. POST requests are never cached.

    Args:
        path (str): The API path for the request.
        region (str): The region to target for the request.
        is_platform_endpoint (bool): Whether to use platform-specific or regional endpoint.
        data (dict, optional): Request body data as a dictionary.

    Returns:
        dict: The JSON response from the API.

    Raises:
        BadRequestException: 400 error
        UnauthorizedException: 401 error
        ForbiddenException: 403 error
        NotFoundException: 404 error
        RateLimitException: 429 error with key rotation
        InternalServerException: 500+ error

    Example:
        >>> await riot_client.post(
        ...     "/lol/tournament/v5/providers",
        ...     region="euw1",
        ...     is_platform_endpoint=False,
        ...     data={"region": "euw1", "url": "https://example.com"}
        ... )
    """
    # Acquire rate limit tokens
    await rate_limiter.acquire()

    # Get next API key
    api_key = self.key_rotator.get_next_key()

    # Build full URL
    base_url = get_base_url(region, is_platform_endpoint)
    url = f"{base_url}{path}"

    logger.debug("POST to Riot API: {} [region={}]", path, region)

    # Make POST request
    headers = {"X-Riot-Token": api_key}
    response = await self.client.post(url, json=data, headers=headers)

    logger.info(f"Riot API status: {response.status_code} for POST {url}")

    # Handle error responses (same as GET method)
    if response.status_code == 400:
        error_msg = self._extract_riot_message(response, "Bad Request")
        logger.warning(f"Bad request (400): {error_msg} [region={region}]")
        raise BadRequestException(details=error_msg)

    if response.status_code == 401:
        error_msg = self._extract_riot_message(response, "Unauthorized")
        logger.error(f"Authentication failed (401): {error_msg} [region={region}]")
        raise UnauthorizedException(message=error_msg)

    if response.status_code == 403:
        error_msg = self._extract_riot_message(response, "Forbidden")
        logger.error(f"Access forbidden (403): {error_msg} [region={region}]")
        raise ForbiddenException(message=error_msg)

    if response.status_code == 404:
        error_msg = self._extract_riot_message(response, "Data not found")
        logger.info(f"Resource not found (404): {error_msg} [region={region}]")
        raise NotFoundException(resource_type=error_msg)

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))
        error_msg = self._extract_riot_message(response, "Rate limit exceeded")
        logger.warning(f"Rate limited (429): {error_msg} [retry_after={retry_after}s]")
        raise RateLimitException(retry_after=retry_after, message=error_msg)

    if response.status_code >= 400:
        error_msg = self._extract_riot_message(response, f"HTTP {response.status_code}")
        logger.error(f"{error_msg} [region={region}]")
        if response.status_code >= 500:
            raise InternalServerException(error_type=error_msg)
        else:
            raise BadRequestException(details=error_msg)

    return response.json()
```

### Step 2.2: Add PUT Method

**File**: `app/riot/client.py`

**Location**: After the `post()` method

**Add**:
```python
async def put(
    self,
    path: str,
    region: str,
    is_platform_endpoint: bool = False,
    data: dict | None = None,
) -> dict:
    """
    Makes a PUT request to the Riot API with rate limiting.

    This method handles PUT requests for updating resources like tournament codes.

    Args:
        path (str): The API path for the request.
        region (str): The region to target for the request.
        is_platform_endpoint (bool): Whether to use platform-specific or regional endpoint.
        data (dict, optional): Request body data as a dictionary.

    Returns:
        dict: The JSON response from the API.

    Raises:
        Same as post() method

    Example:
        >>> await riot_client.put(
        ...     "/lol/tournament/v5/codes/CODE123",
        ...     region="euw1",
        ...     is_platform_endpoint=False,
        ...     data={"pickType": "TOURNAMENT_DRAFT"}
        ... )
    """
    # Acquire rate limit tokens
    await rate_limiter.acquire()

    # Get next API key
    api_key = self.key_rotator.get_next_key()

    # Build full URL
    base_url = get_base_url(region, is_platform_endpoint)
    url = f"{base_url}{path}"

    logger.debug("PUT to Riot API: {} [region={}]", path, region)

    # Make PUT request
    headers = {"X-Riot-Token": api_key}
    response = await self.client.put(url, json=data, headers=headers)

    logger.info(f"Riot API status: {response.status_code} for PUT {url}")

    # Handle error responses (same logic as POST)
    if response.status_code == 400:
        error_msg = self._extract_riot_message(response, "Bad Request")
        logger.warning(f"Bad request (400): {error_msg} [region={region}]")
        raise BadRequestException(details=error_msg)

    if response.status_code == 401:
        error_msg = self._extract_riot_message(response, "Unauthorized")
        logger.error(f"Authentication failed (401): {error_msg} [region={region}]")
        raise UnauthorizedException(message=error_msg)

    if response.status_code == 403:
        error_msg = self._extract_riot_message(response, "Forbidden")
        logger.error(f"Access forbidden (403): {error_msg} [region={region}]")
        raise ForbiddenException(message=error_msg)

    if response.status_code == 404:
        error_msg = self._extract_riot_message(response, "Data not found")
        logger.info(f"Resource not found (404): {error_msg} [region={region}]")
        raise NotFoundException(resource_type=error_msg)

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))
        error_msg = self._extract_riot_message(response, "Rate limit exceeded")
        logger.warning(f"Rate limited (429): {error_msg} [retry_after={retry_after}s]")
        raise RateLimitException(retry_after=retry_after, message=error_msg)

    if response.status_code >= 400:
        error_msg = self._extract_riot_message(response, f"HTTP {response.status_code}")
        logger.error(f"{error_msg} [region={region}]")
        if response.status_code >= 500:
            raise InternalServerException(error_type=error_msg)
        else:
            raise BadRequestException(details=error_msg)

    return response.json()
```

**Verify**:
```bash
uv run python -c "from app.riot.client import riot_client; import inspect; print('post' in dir(riot_client)); print('put' in dir(riot_client))"
# Should output: True True
```

---

## Phase 3: Tournament Router

### Step 3.1: Create File

**File**: `app/routers/tournament.py`

**Create empty file**:
```bash
cd D:\LoLProjects\lolstonks-api-gateway
type nul > app\routers\tournament.py
```

### Step 3.2: Add Module Docstring

**Content**:
```python
"""Tournament-V5 API endpoints (Tournament management).

This module provides endpoints for managing Riot's tournament system,
including provider registration, tournament creation, and code generation.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#tournament-v5

Tournament API Access:
    Requires tournament-specific API key. Standard API keys will return 403 Forbidden.
    Apply for access at: https://developer.riotgames.com/

Endpoints:
    - POST /providers: Register tournament provider
    - POST /tournaments: Create tournament
    - POST /codes: Generate tournament codes
    - GET /codes/{code}: Get code details (cached)
    - PUT /codes/{code}: Update code settings
    - GET /lobby-events/by-code/{code}: Get lobby events (cached)

Caching:
    - Tournament codes: 5 minutes TTL
    - Lobby events: 30 seconds TTL
    - POST/PUT endpoints: Not cached (state-changing)
"""
```

### Step 3.3: Add Imports

**Content**:
```python
from fastapi import APIRouter, Query
from app.cache.helpers import fetch_with_cache
from app.cache.redis_cache import cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/tournament/v5", tags=["tournament"])
```

### Step 3.4: Add POST /providers Endpoint

**Content**:
```python
@router.post("/providers")
async def register_provider(
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Register a tournament provider.

    This endpoint registers a new tournament provider with Riot, which is
    required before creating tournaments or generating codes.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/POST_postProviders

    Args:
        region (str): The region to register the provider in.

    Returns:
        dict: Provider registration response containing provider ID.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/providers?region=euw1"

    Note:
        - POST endpoint: NOT cached (state-changing operation)
        - Requires tournament-specific API key (403 if no access)
    """
    return await riot_client.post(
        "/lol/tournament/v5/providers",
        region,
        is_platform_endpoint=False
    )
```

### Step 3.5: Add POST /tournaments Endpoint

**Content**:
```python
@router.post("/tournaments")
async def create_tournament(
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Create a tournament.

    This endpoint creates a new tournament definition with the specified
    configuration (name, provider ID, etc.).

    API Reference: https://developer.riotgames.com/apis#tournament-v5/POST_postTournaments

    Args:
        region (str): The region to create the tournament in.

    Returns:
        dict: Tournament creation response containing tournament ID.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/tournaments?region=euw1"

    Note:
        - POST endpoint: NOT cached (state-changing operation)
    """
    return await riot_client.post(
        "/lol/tournament/v5/tournaments",
        region,
        is_platform_endpoint=False
    )
```

### Step 3.6: Add POST /codes Endpoint

**Content**:
```python
@router.post("/codes")
async def generate_codes(
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Generate tournament codes.

    This endpoint generates one or more tournament codes that can be used
    to create tournament lobbies in the League client.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/POST_postCodes

    Args:
        region (str): The region to generate codes for.

    Returns:
        list: List of generated tournament codes.

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/codes?region=euw1"

    Note:
        - POST endpoint: NOT cached (state-changing operation)
    """
    return await riot_client.post(
        "/lol/tournament/v5/codes",
        region,
        is_platform_endpoint=False
    )
```

### Step 3.7: Add GET /codes/{code} Endpoint

**Content**:
```python
@router.get("/codes/{tournamentCode}")
async def get_tournament_code(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    force: bool = Query(default=False, description="Force cache refresh")
):
    """
    Retrieve tournament code details.

    This endpoint fetches details about a specific tournament code, including
    its tournament ID, lobby status, and metadata.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/GET_getLobbyEventsByCode

    Args:
        tournamentCode (str): The tournament code to query.
        region (str): The region to fetch the code details from.
        force (bool): If True, bypass cache and fetch from API.

    Returns:
        dict: Tournament code details.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/tournament/v5/codes/TURNACODE123?region=euw1"
        >>> curl "http://127.0.0.1:8080/lol/tournament/v5/codes/TURNACODE123?region=euw1&force=true"

    Note:
        - Uses short TTL (5 min) - code status can change
        - Supports ?force=true for real-time status
    """
    return await fetch_with_cache(
        cache_key=f"tournament:code:{region}:{tournamentCode}",
        resource_name="Tournament code",
        fetch_fn=lambda: riot_client.get(
            f"/lol/tournament/v5/codes/{tournamentCode}",
            region,
            False
        ),
        ttl=settings.cache_ttl_tournament_code,
        context={"tournamentCode": tournamentCode, "region": region},
        force_refresh=force
    )
```

### Step 3.8: Add PUT /codes/{code} Endpoint

**Content**:
```python
@router.put("/codes/{tournamentCode}")
async def update_tournament_code(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Update tournament code settings.

    This endpoint updates the settings for an existing tournament code.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/PUT_putCode

    Args:
        tournamentCode (str): The tournament code to update.
        region (str): The region of the tournament code.

    Returns:
        dict: Updated tournament code details.

    Example:
        >>> curl -X PUT "http://127.0.0.1:8080/lol/tournament/v5/codes/TURNACODE123?region=euw1"

    Note:
        - PUT endpoint: NOT cached (state-changing operation)
        - Invalidates existing cache for this code
    """
    result = await riot_client.put(
        f"/lol/tournament/v5/codes/{tournamentCode}",
        region,
        is_platform_endpoint=False
    )

    # Invalidate cache after update
    await cache.delete(f"tournament:code:{region}:{tournamentCode}")

    return result
```

### Step 3.9: Add GET /lobby-events/by-code/{code} Endpoint

**Content**:
```python
@router.get("/lobby-events/by-code/{tournamentCode}")
async def get_lobby_events(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    force: bool = Query(default=False, description="Force cache refresh")
):
    """
    Retrieve lobby events for a tournament code.

    This endpoint fetches real-time lobby events for a tournament code.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/GET_getLobbyEventsByCode

    Args:
        tournamentCode (str): The tournament code to query.
        region (str): The region to fetch the events from.
        force (bool): If True, bypass cache and fetch from API.

    Returns:
        dict: Lobby events list.

    Example:
        >>> curl "http://127.0.0.1:8080/lol/tournament/v5/lobby-events/by-code/TURNACODE123?region=euw1"
        >>> curl "http://127.0.0.1:8080/lol/tournament/v5/lobby-events/by-code/TURNACODE123?region=euw1&force=true"

    Note:
        - Uses very short TTL (30s) - events are highly dynamic
        - Supports ?force=true for real-time monitoring
    """
    return await fetch_with_cache(
        cache_key=f"tournament:lobby_events:{region}:{tournamentCode}",
        resource_name="Tournament lobby events",
        fetch_fn=lambda: riot_client.get(
            f"/lol/tournament/v5/lobby-events/by-code/{tournamentCode}",
            region,
            False
        ),
        ttl=settings.cache_ttl_tournament_lobby_events,
        context={"tournamentCode": tournamentCode, "region": region},
        force_refresh=force
    )
```

**Verify file structure**:
```bash
uv run python -c "from app.routers.tournament import router; print(f'Routes: {len(router.routes)}')"
# Should output: Routes: 6
```

---

## Phase 4: Stub Router

### Step 4.1: Create File

**File**: `app/routers/tournament_stub.py`

**Create by copying tournament.py**:
```bash
copy app\routers\tournament.py app\routers\tournament_stub.py
```

### Step 4.2: Modify for Stub

**Changes needed**:

1. **Update module docstring**:
```python
"""Tournament-Stub-V5 API endpoints (Testing environment).

This module provides stub endpoints for testing tournament functionality
without affecting live tournament data.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#tournament-stub-v5

Purpose:
    Testing tournament logic in a sandbox environment.
    All operations are isolated from production tournament data.
"""
```

2. **Update router prefix and tags** (around line 42):
```python
router = APIRouter(prefix="/lol/tournament-stub/v5", tags=["tournament-stub"])
```

3. **Update all endpoint paths**:
   - Change `/lol/tournament/v5/` to `/lol/tournament-stub/v5/` in all `riot_client` calls

**Example for POST /providers**:
```python
@router.post("/providers")
async def register_provider(
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """Register a stub tournament provider."""
    return await riot_client.post(
        "/lol/tournament-stub/v5/providers",  # Changed from tournament to tournament-stub
        region,
        is_platform_endpoint=False
    )
```

**Repeat for all 6 endpoints**:
- POST /providers
- POST /tournaments
- POST /codes
- GET /codes/{tournamentCode}
- PUT /codes/{tournamentCode}
- GET /lobby-events/by-code/{tournamentCode}

**Verify**:
```bash
uv run python -c "from app.routers.tournament_stub import router; print(f'Stub routes: {len(router.routes)}')"
# Should output: Stub routes: 6
```

---

## Phase 5: Integration

### Step 5.1: Include Routers in Main App

**File**: `app/main.py`

**Location**: In the imports section (around line 17)

**Add to imports**:
```python
from app.routers import (
    # ... existing imports ...
    tournament,
    tournament_stub,
)
```

**Location**: In router inclusion section (after clash router, around line 207)

**Add**:
```python
app.include_router(tournament.router)  # Tournament-V5
app.include_router(tournament_stub.router)  # Tournament-Stub-V5
```

**Complete context**:
```python
# Include routers - Riot API
app.include_router(account.router)  # Account API (Riot ID lookups)
app.include_router(summoner.router)  # Summoner-V4
app.include_router(match.router)  # Match-V5
app.include_router(league.router)  # League-V4
app.include_router(league_exp.router)  # League-EXP-V4 (experimental)
app.include_router(champion.router)  # Champion-V3 (rotations)
app.include_router(champion_mastery.router)  # Champion-Mastery-V4
app.include_router(spectator.router)  # Spectator-V5 (live games)
app.include_router(platform.router)  # Platform/Status-V4
app.include_router(clash.router)  # Clash-V1
app.include_router(challenges.router)  # Challenges-V1
app.include_router(tournament.router)  # Tournament-V5
app.include_router(tournament_stub.router)  # Tournament-Stub-V5
app.include_router(security.router)  # Security monitoring
```

**Verify server starts**:
```bash
make run
# Should see: INFO: Application startup complete
# Should not see import errors
```

---

## Phase 6: Testing

### Step 6.1: Create Unit Tests

**File**: `tests/test_tournament.py`

**Create**:
```bash
type nul > tests\test_tournament.py
```

**Content**:
```python
"""Tests for tournament routers."""

import pytest
from unittest.mock import AsyncMock, patch
from app.routers.tournament import router as tournament_router
from app.routers.tournament_stub import router as stub_router


class TestTournamentRouter:
    """Test tournament router endpoints."""

    @pytest.mark.asyncio
    async def test_register_provider(self):
        """Test POST /providers endpoint."""
        with patch("app.routers.tournament.riot_client.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"providerId": 123}

            from app.routers.tournament import register_provider
            result = await register_provider(region="euw1")

            assert result["providerId"] == 123
            mock_post.assert_called_once_with("/lol/tournament/v5/providers", "euw1", is_platform_endpoint=False)

    @pytest.mark.asyncio
    async def test_get_tournament_code(self):
        """Test GET /codes/{code} uses cache."""
        with patch("app.routers.tournament.fetch_with_cache", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {"code": "TEST123"}

            from app.routers.tournament import get_tournament_code
            result = await get_tournament_code(tournamentCode="TEST123", region="euw1", force=False)

            assert result["code"] == "TEST123"
            mock_fetch.assert_called_once()
            call_kwargs = mock_fetch.call_args.kwargs
            assert call_kwargs["cache_key"] == "tournament:code:euw1:TEST123"
            assert call_kwargs["ttl"] == 300

    @pytest.mark.asyncio
    async def test_get_lobby_events_force_refresh(self):
        """Test ?force=true bypasses cache."""
        with patch("app.routers.tournament.fetch_with_cache", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {"events": []}

            from app.routers.tournament import get_lobby_events
            result = await get_lobby_events(tournamentCode="TEST123", region="euw1", force=True)

            assert result["events"] == []
            call_kwargs = mock_fetch.call_args.kwargs
            assert call_kwargs["force_refresh"] is True


class TestTournamentStubRouter:
    """Test tournament stub router endpoints."""

    @pytest.mark.asyncio
    async def test_stub_register_provider(self):
        """Test stub POST /providers endpoint."""
        with patch("app.routers.tournament_stub.riot_client.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"providerId": 456}

            from app.routers.tournament_stub import register_provider
            result = await register_provider(region="euw1")

            assert result["providerId"] == 456
            mock_post.assert_called_once_with("/lol/tournament-stub/v5/providers", "euw1", is_platform_endpoint=False)
```

**Run tests**:
```bash
uv run pytest tests/test_tournament.py -v
```

### Step 6.2: Add Integration Tests

**File**: `tests/integration/test_endpoints.py`

**Add at end**:
```python
# ============================================================================
# TOURNAMENT API SMOKE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_tournament_providers_validation(async_client: AsyncClient):
    """Test tournament provider endpoint validates region."""
    response = await async_client.post(
        "/lol/tournament/v5/providers?region=invalid_region"
    )
    # Should return validation error or 403 (no access)
    assert response.status_code in [400, 403, 422]


@pytest.mark.asyncio
async def test_tournament_code_validation(async_client: AsyncClient):
    """Test tournament code endpoint validates parameters."""
    response = await async_client.get(
        "/lol/tournament/v5/codes/TESTCODE?region=invalid_region"
    )
    assert response.status_code in [400, 403, 404, 422]


@pytest.mark.asyncio
async def test_tournament_stub_providers_validation(async_client: AsyncClient):
    """Test tournament stub provider endpoint."""
    response = await async_client.post(
        "/lol/tournament-stub/v5/providers?region=invalid_region"
    )
    assert response.status_code in [400, 403, 422]
```

**Run integration tests**:
```bash
uv run pytest tests/integration/test_endpoints.py::test_tournament_providers_validation -v
```

---

## Verification

### Step 1: Check Router Registration

```bash
curl http://127.0.0.1:8080/docs
```

**Expected**: See "tournament" and "tournament-stub" tags in Swagger UI

### Step 2: Verify Endpoints

```bash
# Tournament V5 endpoints
curl http://127.0.0.1:8080/lol/tournament/v5/codes/TESTCODE?region=euw1
curl http://127.0.0.1:8080/lol/tournament/v5/lobby-events/by-code/TESTCODE?region=euw1

# Tournament Stub V5 endpoints
curl http://127.0.0.1:8080/lol/tournament-stub/v5/codes/TESTCODE?region=euw1
```

**Expected responses**:
- 403 Forbidden (if no tournament API key)
- OR 404 Not Found (if code doesn't exist)
- OR actual data (if you have tournament access)

### Step 3: Check OpenAPI Schema

```bash
curl http://127.0.0.1:8080/openapi.json | grep -A 5 "tournament"
```

**Expected**: See tournament paths in OpenAPI schema

### Step 4: Test Caching

```bash
# First call - cache miss
curl http://127.0.0.1:8080/lol/tournament/v5/codes/TESTCODE?region=euw1

# Second call - cache hit (faster)
curl http://127.0.0.1:8080/lol/tournament/v5/codes/TESTCODE?region=euw1

# Force refresh - cache bypass
curl http://127.0.0.1:8080/lol/tournament/v5/codes/TESTCODE?region=euw1&force=true
```

---

## Troubleshooting

### Issue: Import Error

**Error**: `ImportError: cannot import name 'tournament'`

**Solution**:
1. Check `app/routers/__init__.py` has tournament exports
2. Check files exist: `app/routers/tournament.py` and `app/routers/tournament_stub.py`

### Issue: 403 Forbidden on All Requests

**Error**: All tournament endpoints return 403

**Solution**:
1. Verify you have tournament API access at https://developer.riotgames.com/
2. Standard API keys don't have tournament permissions
3. Try tournament-stub endpoints (may work with standard key)

### Issue: Cache Not Working

**Error**: Force refresh doesn't work

**Solution**:
1. Check `force` parameter is passed to `fetch_with_cache`
2. Check `force_refresh` argument is used (not `force`)
3. Check Redis is running: `make docker-run`

### Issue: PUT Doesn't Invalidate Cache

**Error**: Updated code still returns old data

**Solution**:
1. Check `cache.delete()` is called after PUT
2. Check cache key matches GET endpoint exactly
3. Check delete operation doesn't raise exceptions

---

## Next Steps

After implementation:

1. **Documentation**: Update API documentation with tournament endpoints
2. **CLI Integration**: Add CLI commands in lolstonks-api-cli
3. **Monitoring**: Add metrics for tournament API usage
4. **Testing**: Test with real tournament API key (if available)

---

## Summary

**Files Created**:
- `app/routers/tournament.py` (~200 lines)
- `app/routers/tournament_stub.py` (~200 lines)
- `tests/test_tournament.py` (~100 lines)

**Files Modified**:
- `app/config.py` (+2 lines)
- `app/routers/__init__.py` (+2 lines)
- `app/riot/client.py` (+200 lines)
- `app/main.py` (+2 lines)
- `tests/integration/test_endpoints.py` (+20 lines)

**Total**: ~730 lines of code
**Time**: ~4-5 hours
**Test Coverage**: ~80% target

---

**Implementation Complete!**

Refer to:
- [tournament-router-design.md](./tournament-router-design.md) for detailed architecture
- [tournament-router-diagram.md](./tournament-router-diagram.md) for visual diagrams
