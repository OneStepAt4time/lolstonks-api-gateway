# Tournament Router Architecture Design

**Version**: 1.0
**Date**: 2025-01-29
**Status**: Design Document
**Author**: ArchitectAgent

---

## Executive Summary

This document outlines the architecture for implementing **Tournament V5** and **Tournament Stub V5** API routers in the lolstonks-api-gateway. These routers provide endpoints for managing Riot's tournament system, including provider registration, tournament creation, and tournament code generation.

**Key Design Decisions**:
- Two separate routers (production vs stub) following existing patterns
- Passthrough architecture (no data transformation)
- Intelligent caching with short TTLs for dynamic data
- Special handling for 403 Forbidden (tournament access restrictions)
- POST/PUT endpoints bypass cache (state-changing operations)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [Router Structure](#3-router-structure)
4. [Endpoint Specifications](#4-endpoint-specifications)
5. [Caching Strategy](#5-caching-strategy)
6. [Configuration Requirements](#6-configuration-requirements)
7. [Integration Points](#7-integration-points)
8. [Error Handling](#8-error-handling)
9. [Testing Strategy](#9-testing-strategy)
10. [Implementation Guidance](#10-implementation-guidance)

---

## 1. Overview

### 1.1 Purpose

The Tournament API routers enable:
- **Tournament Providers**: Register tournament providers with Riot
- **Tournament Management**: Create and manage tournament definitions
- **Code Generation**: Generate tournament codes for lobby creation
- **Lobby Events**: Monitor tournament lobby events in real-time

### 1.2 API Versions

| Router | API Path | Purpose |
|--------|----------|---------|
| **Tournament V5** | `/lol/tournament/v5/*` | Production tournament API |
| **Tournament Stub V5** | `/lol/tournament-stub/v5/*` | Testing/development stub API |

### 1.3 Special Considerations

**Tournament API Access Requirements**:
- Requires **tournament-specific API key** (standard keys return 403 Forbidden)
- Must apply for tournament access at [Riot Developer Portal](https://developer.riotgames.com/)
- Not all API keys have tournament permissions by default

**Use Cases**:
- **Production API**: Live tournaments with real players and prizes
- **Stub API**: Testing tournament logic without affecting live data

---

## 2. Architecture Principles

### 2.1 Design Principles

Following the existing gateway patterns from `clash.py` and `spectator.py`:

```python
# Standard pattern observed in existing routers
from fastapi import APIRouter, Query
from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/tournament/v5", tags=["tournament"])
```

### 2.2 Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Passthrough** | No data transformation, return Riot response as-is |
| **Caching** | Use `fetch_with_cache` for all GET endpoints |
| **Force Refresh** | Support `?force=true` query parameter |
| **State-Changing** | POST/PUT endpoints bypass cache entirely |
| **Error Handling** | Use existing custom exceptions |
| **Logging** | Structured logging with contextual information |
| **Documentation** | Comprehensive docstrings with API reference links |

### 2.3 Naming Conventions

```python
# File: app/routers/tournament.py
# Router instance: router
# Endpoint functions: <action>_<resource>
# Example: register_provider, create_tournament, generate_codes

# Cache keys: tournament:<resource>:<region>:<identifier>
# Example: tournament:code:euw1:TURNACODE123
```

---

## 3. Router Structure

### 3.1 File Organization

```
app/routers/
├── tournament.py          # Production Tournament V5 API
├── tournament_stub.py     # Tournament Stub V5 API
├── clash.py               # Existing - reference pattern
├── spectator.py           # Existing - reference pattern
└── __init__.py            # Export routers
```

### 3.2 Router Template

```python
"""Tournament-V5 API endpoints (Tournament management).

This module provides endpoints for managing Riot's tournament system,
including provider registration, tournament creation, and code generation.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#tournament-v5

Tournament API Access:
    Requires tournament-specific API key. Standard API keys will return 403 Forbidden.
    Apply for access at: https://developer.riotgames.com/

Use Cases:
    - Tournament Provider Registration
    - Tournament Creation and Management
    - Tournament Code Generation
    - Lobby Event Monitoring
"""

from fastapi import APIRouter, Query
from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/tournament/v5", tags=["tournament"])
```

### 3.3 Stub Router Template

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

from fastapi import APIRouter, Query
from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/tournament-stub/v5", tags=["tournament-stub"])
```

---

## 4. Endpoint Specifications

### 4.1 Tournament V5 Endpoints

#### 4.1.1 POST /providers - Register Tournament Provider

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

    Request Body:
        {
            "region": "euw1",
            "url": "https://example.com/callback"
        }

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/providers?region=euw1" \
        >>>      -H "Content-Type: application/json" \
        >>>      -d '{"region": "euw1", "url": "https://example.com/callback"}'

    Note:
        - POST endpoint: NOT cached (state-changing operation)
        - Requires tournament-specific API key (403 if no access)
        - Provider URL must be reachable by Riot servers
    """
    # Direct API call, no caching for POST
    return await riot_client.post(
        "/lol/tournament/v5/providers",
        region,
        is_platform_endpoint=False
    )
```

**Design Notes**:
- **No caching**: POST endpoints are state-changing, bypass cache entirely
- **Direct call**: Use `riot_client.post()` (need to add POST method to client)
- **Region required**: Provider registration is region-specific

#### 4.1.2 POST /tournaments - Create Tournament

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

    Request Body:
        {
            "name": "My Tournament",
            "providerId": 123
        }

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/tournaments?region=euw1" \
        >>>      -H "Content-Type: application/json" \
        >>>      -d '{"name": "My Tournament", "providerId": 123}'

    Note:
        - POST endpoint: NOT cached (state-changing operation)
        - Requires valid provider ID from previous provider registration
    """
    return await riot_client.post(
        "/lol/tournament/v5/tournaments",
        region,
        is_platform_endpoint=False
    )
```

#### 4.1.3 POST /codes - Generate Tournament Codes

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

    Request Body:
        {
            "tournamentId": 456,
            "count": 5,
            "teamSize": 5
        }

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/codes?region=euw1" \
        >>>      -H "Content-Type: application/json" \
        >>>      -d '{"tournamentId": 456, "count": 5, "teamSize": 5}'

    Note:
        - POST endpoint: NOT cached (state-changing operation)
        - Codes can be used in League client to create tournament lobbies
    """
    return await riot_client.post(
        "/lol/tournament/v5/codes",
        region,
        is_platform_endpoint=False
    )
```

#### 4.1.4 GET /codes/{tournamentCode} - Get Code Details

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

**Design Notes**:
- **Cached with short TTL**: 5 minutes (code details change during tournaments)
- **Force refresh**: Supports `?force=true` for real-time updates
- **Cache key**: Includes region and tournament code for uniqueness

#### 4.1.5 PUT /codes/{tournamentCode} - Update Code Settings

```python
@router.put("/codes/{tournamentCode}")
async def update_tournament_code(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code")
):
    """
    Update tournament code settings.

    This endpoint updates the settings for an existing tournament code,
    such as pick type, map type, or spectator type.

    API Reference: https://developer.riotgames.com/apis#tournament-v5/PUT_putCode

    Args:
        tournamentCode (str): The tournament code to update.
        region (str): The region of the tournament code.

    Returns:
        dict: Updated tournament code details.

    Request Body:
        {
            "pickType": "TOURNAMENT_DRAFT",
            "mapType": "SUMMONERS_RIFT",
            "spectatorType": "ALL"
        }

    Example:
        >>> curl -X PUT "http://127.0.0.1:8080/lol/tournament/v5/codes/TURNACODE123?region=euw1" \
        >>>      -H "Content-Type: application/json" \
        >>>      -d '{"pickType": "TOURNAMENT_DRAFT", "mapType": "SUMMONERS_RIFT"}'

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

**Design Notes**:
- **Cache invalidation**: After successful PUT, delete cached code details
- **Requires PUT method**: Need to add `riot_client.put()` method

#### 4.1.6 GET /lobby-events/by-code/{tournamentCode} - Get Lobby Events

```python
@router.get("/lobby-events/by-code/{tournamentCode}")
async def get_lobby_events(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region, description="Region code"),
    force: bool = Query(default=False, description="Force cache refresh")
):
    """
    Retrieve lobby events for a tournament code.

    This endpoint fetches real-time lobby events for a tournament code,
    including player joins, lobby updates, and game start events.

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
        - Use WebSocket or polling for continuous updates
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

**Design Notes**:
- **Very short TTL**: 30 seconds (lobby events change constantly)
- **Real-time monitoring**: Use `?force=true` for live updates
- **Polling consideration**: For continuous monitoring, poll every 30+ seconds

### 4.2 Tournament Stub V5 Endpoints

The stub API mirrors the production API with identical endpoints but operates in a sandbox environment:

```python
# Endpoints are identical to production, just different base path
router = APIRouter(prefix="/lol/tournament-stub/v5", tags=["tournament-stub"])

# Same 6 endpoints:
POST   /providers
POST   /tournaments
POST   /codes
GET    /codes/{tournamentCode}
PUT    /codes/{tournamentCode}
GET    /lobby-events/by-code/{tournamentCode}
```

**Key Differences**:
- **Sandbox data**: Operations don't affect production tournaments
- **Same API key**: Can use standard API key (no special access required)
- **Testing environment**: Ideal for development and testing

---

## 5. Caching Strategy

### 5.1 Cache TTL Configuration

Add to `app/config.py` in the Cache TTL section:

```python
# TOURNAMENT-V5: Tournament management and codes
cache_ttl_tournament_code: int = 300  # 5 minutes - Code details
cache_ttl_tournament_lobby_events: int = 30  # 30 seconds - Very dynamic
```

**Placement** (after Clash TTLs, line ~190):

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

### 5.2 Cache Key Patterns

| Endpoint | Cache Key Pattern | TTL |
|----------|------------------|-----|
| GET /codes/{code} | `tournament:code:{region}:{tournamentCode}` | 300s (5 min) |
| GET /lobby-events/by-code/{code} | `tournament:lobby_events:{region}:{tournamentCode}` | 30s |

**Cache Key Design**:
```python
# Pattern: tournament:<resource_type>:<region>:<identifier>
cache_key = f"tournament:{resource}:{region}:{identifier}"

# Examples:
tournament:code:euw1:TURNACODE123
tournament:lobby_events:euw1:TURNACODE123
```

### 5.3 Caching Behavior

| Operation | Caching | Behavior |
|-----------|---------|----------|
| POST /providers | **NO** | State-changing, bypass cache |
| POST /tournaments | **NO** | State-changing, bypass cache |
| POST /codes | **NO** | State-changing, bypass cache |
| GET /codes/{code} | **YES** | Cache with 5 min TTL, support ?force=true |
| PUT /codes/{code} | **NO** | State-changing, invalidate cache |
| GET /lobby-events | **YES** | Cache with 30s TTL, support ?force=true |

### 5.4 Cache Invalidation

```python
# When updating a code, invalidate its cache
@router.put("/codes/{tournamentCode}")
async def update_tournament_code(...):
    result = await riot_client.put(...)

    # Invalidate related caches
    await cache.delete(f"tournament:code:{region}:{tournamentCode}")

    return result
```

---

## 6. Configuration Requirements

### 6.1 Settings Configuration

**File**: `app/config.py`

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Cache TTL (seconds) - Organized by API service

    # ... existing TTLs ...

    # TOURNAMENT-V5: Tournament management and codes
    cache_ttl_tournament_code: int = 300  # 5 minutes
    cache_ttl_tournament_lobby_events: int = 30  # 30 seconds

    # ... rest of settings ...
```

### 6.2 Environment Variables

Optional environment variable overrides:

```bash
# .env file or environment
CACHE_TTL_TOURNAMENT_CODE=300
CACHE_TTL_TOURNAMENT_LOBBY_EVENTS=30
```

### 6.3 Router Exports

**File**: `app/routers/__init__.py`

```python
"""Routers package for lolstonks-api-gateway."""

from app.routers import (
    # ... existing routers ...
    tournament,
    tournament_stub,
)

__all__ = [
    # ... existing exports ...
    "tournament",
    "tournament_stub",
]
```

---

## 7. Integration Points

### 7.1 Files to Create

| File | Purpose | Lines (approx) |
|------|---------|----------------|
| `app/routers/tournament.py` | Production Tournament V5 API | ~350 lines |
| `app/routers/tournament_stub.py` | Tournament Stub V5 API | ~350 lines |

### 7.2 Files to Modify

| File | Changes | Impact |
|------|---------|--------|
| `app/config.py` | Add 2 TTL settings | +2 lines |
| `app/routers/__init__.py` | Export 2 routers | +2 lines |
| `app/main.py` | Include routers | +2 lines (later task) |
| `app/riot/client.py` | Add POST/PUT methods | +~100 lines |

### 7.3 Main.py Integration (Later)

```python
# In app/main.py, add to imports:
from app.routers import (
    # ... existing ...
    tournament,
    tournament_stub,
)

# In router inclusion section (after Clash router):
app.include_router(tournament.router)  # Tournament-V5
app.include_router(tournament_stub.router)  # Tournament-Stub-V5
```

### 7.4 HTTP Client Enhancement

**File**: `app/riot/client.py`

Need to add POST and PUT methods:

```python
async def post(
    self,
    path: str,
    region: str,
    is_platform_endpoint: bool = False,
    data: dict | None = None,
) -> dict:
    """Make a POST request to the Riot API."""
    # Similar to get(), but uses POST method
    # Include request body (data parameter)
    # Handle errors same way as GET
    pass

async def put(
    self,
    path: str,
    region: str,
    is_platform_endpoint: bool = False,
    data: dict | None = None,
) -> dict:
    """Make a PUT request to the Riot API."""
    # Similar to post(), but uses PUT method
    pass
```

---

## 8. Error Handling

### 8.1 Special Tournament Errors

| HTTP Status | Meaning | Handling |
|-------------|---------|----------|
| **403 Forbidden** | No tournament access | Special message about tournament API key requirement |
| **400 Bad Request** | Invalid tournament parameters | Riot's exact error message |
| **404 Not Found** | Tournament code doesn't exist | Tournament code not found |
| **429 Rate Limit** | Too many requests | Retry-After header |

### 8.2 403 Forbidden Handling

```python
# In error handler, provide helpful message
if response.status_code == 403 and "tournament" in str(e.request.url).lower():
    logger.error(
        f"Tournament API access forbidden (403): {error_msg} [region={region}]",
    )
    raise ForbiddenException(
        message=f"Tournament API access forbidden. This endpoint requires a tournament-specific API key. "
                f"Standard API keys do not have tournament access. Apply at https://developer.riotgames.com/ - "
                f"Details: {error_msg}"
    )
```

### 8.3 Error Response Format

Follow existing error format from `app/exceptions.py`:

```json
{
  "detail": "Tournament API access forbidden. This endpoint requires a tournament-specific API key..."
}
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

**File**: `tests/test_tournament.py`

```python
"""Tests for tournament routers."""

import pytest
from unittest.mock import AsyncMock, patch
from app.routers.tournament import router
from app.routers.tournament_stub import router as stub_router


class TestTournamentRouter:
    """Test tournament router endpoints."""

    @pytest.mark.asyncio
    async def test_register_provider(self):
        """Test POST /providers endpoint."""
        # Mock riot_client.post
        pass

    @pytest.mark.asyncio
    async def test_get_tournament_code_caching(self):
        """Test GET /codes/{code} uses cache."""
        # Test cache hit scenario
        # Test cache miss scenario
        pass

    @pytest.mark.asyncio
    async def test_get_lobby_events_force_refresh(self):
        """Test ?force=true bypasses cache."""
        pass

    @pytest.mark.asyncio
    async def test_update_code_invalidates_cache(self):
        """Test PUT /codes invalidates cache."""
        pass


class TestTournamentStubRouter:
    """Test tournament stub router endpoints."""

    @pytest.mark.asyncio
    async def test_stub_provider_registration(self):
        """Test stub provider registration."""
        pass
```

### 9.2 Integration Tests

**File**: `tests/integration/test_endpoints.py`

```python
# Add to existing integration tests

@pytest.mark.asyncio
async def test_tournament_providers_validation(async_client: AsyncClient):
    """Test tournament provider endpoint validates region."""
    response = await async_client.post(
        "/lol/tournament/v5/providers?region=invalid_region"
    )
    # Should return validation error
    assert response.status_code in [400, 403, 422]


@pytest.mark.asyncio
async def test_tournament_code_validation(async_client: AsyncClient):
    """Test tournament code endpoint validates parameters."""
    response = await async_client.get(
        "/lol/tournament/v5/codes/TESTCODE?region=invalid_region"
    )
    assert response.status_code in [400, 403, 404, 422]
```

### 9.3 Test Coverage Requirements

| Category | Coverage Target | Priority |
|----------|----------------|----------|
| POST endpoints | 80% | High |
| GET endpoints with cache | 90% | High |
| PUT with cache invalidation | 85% | High |
| Error handling (403, 404) | 85% | Medium |
| Force refresh logic | 80% | Medium |

---

## 10. Implementation Guidance

### 10.1 Implementation Order

**Phase 1: Foundation** (1 hour)
1. Add TTL settings to `app/config.py`
2. Export routers in `app/routers/__init__.py`
3. Add POST/PUT methods to `app/riot/client.py`

**Phase 2: Tournament Router** (1.5 hours)
1. Create `app/routers/tournament.py`
2. Implement all 6 endpoints
3. Add comprehensive docstrings

**Phase 3: Stub Router** (30 minutes)
1. Create `app/routers/tournament_stub.py`
2. Copy endpoints from tournament.py
3. Update prefix and tags

**Phase 4: Testing** (1 hour)
1. Create unit tests
2. Add integration tests
3. Verify error handling

**Phase 5: Integration** (15 minutes)
1. Include routers in `app/main.py`
2. Test endpoints with Swagger UI
3. Verify caching behavior

**Total Time**: ~4 hours

### 10.2 Implementation Checklist

- [ ] Add cache TTL settings to `app/config.py`
- [ ] Export routers in `app/routers/__init__.py`
- [ ] Add `riot_client.post()` method
- [ ] Add `riot_client.put()` method
- [ ] Create `app/routers/tournament.py`
  - [ ] POST /providers
  - [ ] POST /tournaments
  - [ ] POST /codes
  - [ ] GET /codes/{tournamentCode}
  - [ ] PUT /codes/{tournamentCode}
  - [ ] GET /lobby-events/by-code/{tournamentCode}
- [ ] Create `app/routers/tournament_stub.py`
  - [ ] All 6 endpoints (mirrored)
- [ ] Include routers in `app/main.py`
- [ ] Write unit tests
- [ ] Add integration tests
- [ ] Test with Swagger UI
- [ ] Verify caching behavior
- [ ] Test 403 Forbidden handling

### 10.3 Code Review Checklist

**Architecture**:
- [ ] Follows existing patterns (clash.py, spectator.py)
- [ ] Passthrough architecture (no data transformation)
- [ ] Proper use of `fetch_with_cache` for GET endpoints
- [ ] POST/PUT bypass cache entirely
- [ ] Cache invalidation on PUT operations

**Configuration**:
- [ ] TTL settings added to config.py
- [ ] Cache keys follow pattern: `tournament:<resource>:<region>:<id>`
- [ ] Router prefixes match API paths exactly
- [ ] Tags for OpenAPI documentation

**Error Handling**:
- [ ] Special 403 Forbidden message for tournament access
- [ ] Uses existing custom exceptions
- [ ] Proper error propagation from Riot API

**Documentation**:
- [ ] Comprehensive module docstrings
- [ ] API reference links in each endpoint
- [ ] Usage examples in docstrings
- [ ] Notes about tournament API key requirements

**Testing**:
- [ ] Unit tests for all endpoints
- [ ] Integration tests in test suite
- [ ] Cache behavior verified
- [ ] Error cases tested

### 10.4 Common Pitfalls to Avoid

**Pitfall 1: Caching POST/PUT endpoints**
```python
# WRONG - Don't use fetch_with_cache for POST
@router.post("/providers")
async def register_provider(...):
    return await fetch_with_cache(...)  # ❌

# CORRECT - Direct API call for state-changing operations
@router.post("/providers")
async def register_provider(...):
    return await riot_client.post(...)  # ✓
```

**Pitfall 2: Missing cache invalidation**
```python
# WRONG - Update without invalidating cache
@router.put("/codes/{code}")
async def update_code(...):
    return await riot_client.put(...)  # ❌

# CORRECT - Invalidate cache after update
@router.put("/codes/{code}")
async def update_code(...):
    result = await riot_client.put(...)
    await cache.delete(f"tournament:code:{region}:{code}")
    return result  # ✓
```

**Pitfall 3: Wrong TTL values**
```python
# WRONG - TTL too long for dynamic data
ttl=3600  # 1 hour for lobby events ❌

# CORRECT - Short TTL for dynamic data
ttl=settings.cache_ttl_tournament_lobby_events  # 30 seconds ✓
```

**Pitfall 4: Forgetting ?force=true support**
```python
# WRONG - No force parameter
@router.get("/codes/{code}")
async def get_code(code: str, region: str):  # ❌
    return await fetch_with_cache(...)

# CORRECT - Support force refresh
@router.get("/codes/{code}")
async def get_code(code: str, region: str, force: bool = False):  # ✓
    return await fetch_with_cache(..., force_refresh=force)
```

---

## 11. API Reference

### 11.1 Official Riot Documentation

- **Tournament V5**: https://developer.riotgames.com/apis#tournament-v5
- **Tournament Stub V5**: https://developer.riotgames.com/apis#tournament-stub-v5
- **Tournament Access**: https://developer.riotgames.com/tournaments

### 11.2 Endpoint Summary

| Method | Path | Description | Cache |
|--------|------|-------------|-------|
| POST | /providers | Register provider | NO |
| POST | /tournaments | Create tournament | NO |
| POST | /codes | Generate codes | NO |
| GET | /codes/{code} | Get code details | YES (5 min) |
| PUT | /codes/{code} | Update code | NO (invalidate) |
| GET | /lobby-events/by-code/{code} | Get events | YES (30s) |

---

## 12. Monitoring and Observability

### 12.1 Logging Patterns

```python
# Structured logging examples
logger.info(
    "Tournament provider registered",
    region=region,
    provider_id=provider_id
)

logger.info(
    "Tournament codes generated",
    region=region,
    count=len(codes),
    tournament_id=tournament_id
)

logger.warning(
    "Tournament code not found",
    tournament_code=tournamentCode,
    region=region
)
```

### 12.2 Metrics to Track

- Provider registration success rate
- Code generation rate
- Lobby event polling frequency
- Cache hit/miss ratio for codes
- 403 Forbidden errors (indicates access issues)

---

## 13. Security Considerations

### 13.1 Tournament API Key Requirements

**Important**: Standard Riot API keys do NOT have tournament access.

**Required Actions**:
1. Apply for tournament access at [Riot Developer Portal](https://developer.riotgames.com/)
2. Receive tournament-specific API key
3. Configure key in environment: `RIOT_API_KEY` or `RIOT_API_KEYS`

**Error Indication**:
```json
{
  "detail": "Forbidden"
}
```

If all tournament endpoints return 403, you likely don't have tournament access.

### 13.2 Stub API Advantage

The stub API can use standard API keys (no special access required), making it ideal for:
- Development testing
- CI/CD pipelines
- Integration tests

---

## 14. Conclusion

This architecture design provides a complete blueprint for implementing Tournament V5 and Tournament Stub V5 routers in the lolstonks-api-gateway. The design:

- Follows existing patterns from clash.py and spectator.py
- Implements intelligent caching for GET endpoints
- Properly handles state-changing operations (POST/PUT)
- Provides clear error messages for tournament access issues
- Includes comprehensive testing strategy

**Next Steps**:
1. Review and approve this design
2. Implement HTTP client POST/PUT methods
3. Create tournament router file
4. Create tournament stub router file
5. Write tests
6. Integrate into main.py
7. Deploy and monitor

**Estimated Implementation Time**: 4 hours
**Estimated Testing Time**: 1 hour
**Total**: ~5 hours

---

## Appendix A: Code Templates

### A.1 Complete Tournament Router Template

See Section 4.1 for detailed endpoint implementations.

### A.2 HTTP Client POST/PUT Implementation

See Section 7.4 for method signatures.

### A.3 Configuration Snippets

See Section 6 for complete configuration examples.

---

**Document Version**: 1.0
**Last Updated**: 2025-01-29
**Status**: Ready for Implementation
