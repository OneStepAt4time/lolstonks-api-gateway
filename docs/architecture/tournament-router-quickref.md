# Tournament Router Quick Reference

**For Developers Implementing Tournament Routers**

---

## File Structure

```
app/
├── routers/
│   ├── tournament.py          # CREATE - Production router
│   ├── tournament_stub.py     # CREATE - Stub router
│   └── __init__.py            # MODIFY - Export routers
├── riot/
│   └── client.py              # MODIFY - Add POST/PUT methods
└── config.py                  # MODIFY - Add TTL settings

tests/
├── test_tournament.py         # CREATE - Unit tests
└── integration/
    └── test_endpoints.py      # MODIFY - Add integration tests

docs/
└── architecture/
    ├── tournament-router-design.md        # Created ✓
    ├── tournament-router-diagram.md       # Created ✓
    ├── tournament-router-implementation.md # Created ✓
    └── tournament-router-quickref.md      # This file
```

---

## Implementation Checklist

### Phase 1: Foundation (15 minutes)
- [ ] Add TTL settings to `app/config.py`:
  ```python
  cache_ttl_tournament_code: int = 300  # 5 minutes
  cache_ttl_tournament_lobby_events: int = 30  # 30 seconds
  ```
- [ ] Export routers in `app/routers/__init__.py`:
  ```python
  from app.routers import tournament, tournament_stub
  ```

### Phase 2: HTTP Client (35 minutes)
- [ ] Add `post()` method to `app/riot/client.py`
- [ ] Add `put()` method to `app/riot/client.py`
- [ ] Both methods handle errors like `get()` method

### Phase 3: Tournament Router (90 minutes)
- [ ] Create `app/routers/tournament.py`
- [ ] Implement 6 endpoints:
  - [ ] POST /providers
  - [ ] POST /tournaments
  - [ ] POST /codes
  - [ ] GET /codes/{tournamentCode} (cached, force refresh)
  - [ ] PUT /codes/{tournamentCode} (invalidate cache)
  - [ ] GET /lobby-events/by-code/{tournamentCode} (cached, force refresh)

### Phase 4: Stub Router (30 minutes)
- [ ] Copy `tournament.py` to `tournament_stub.py`
- [ ] Change prefix to `/lol/tournament-stub/v5`
- [ ] Update all API paths to use stub endpoint

### Phase 5: Integration (10 minutes)
- [ ] Import routers in `app/main.py`
- [ ] Include routers:
  ```python
  app.include_router(tournament.router)
  app.include_router(tournament_stub.router)
  ```

### Phase 6: Testing (60 minutes)
- [ ] Create `tests/test_tournament.py`
- [ ] Add unit tests for all endpoints
- [ ] Add integration tests
- [ ] Run `pytest` and verify >80% coverage

---

## Code Snippets

### Cache TTL Settings

```python
# In app/config.py (around line 190)
# TOURNAMENT-V5: Tournament management and codes
cache_ttl_tournament_code: int = 300  # 5 minutes
cache_ttl_tournament_lobby_events: int = 30  # 30 seconds
```

### Router Template

```python
"""Tournament-V5 API endpoints (Tournament management)."""

from fastapi import APIRouter, Query
from app.cache.helpers import fetch_with_cache
from app.cache.redis_cache import cache
from app.config import settings
from app.riot.client import riot_client

router = APIRouter(prefix="/lol/tournament/v5", tags=["tournament"])
```

### POST Endpoint (Not Cached)

```python
@router.post("/providers")
async def register_provider(
    region: str = Query(default=settings.riot_default_region)
):
    """Register a tournament provider."""
    return await riot_client.post(
        "/lol/tournament/v5/providers",
        region,
        is_platform_endpoint=False
    )
```

### GET Endpoint (Cached)

```python
@router.get("/codes/{tournamentCode}")
async def get_tournament_code(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region),
    force: bool = Query(default=False)
):
    """Get tournament code details."""
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

### PUT Endpoint (Invalidate Cache)

```python
@router.put("/codes/{tournamentCode}")
async def update_tournament_code(
    tournamentCode: str,
    region: str = Query(default=settings.riot_default_region)
):
    """Update tournament code settings."""
    result = await riot_client.put(
        f"/lol/tournament/v5/codes/{tournamentCode}",
        region,
        is_platform_endpoint=False
    )

    # Invalidate cache
    await cache.delete(f"tournament:code:{region}:{tournamentCode}")

    return result
```

---

## Cache Key Patterns

```python
# Code details
f"tournament:code:{region}:{tournamentCode}"
# Example: tournament:code:euw1:TURNACODE123

# Lobby events
f"tournament:lobby_events:{region}:{tournamentCode}"
# Example: tournament:lobby_events:euw1:TURNACODE123
```

---

## TTL Values

| Endpoint | TTL | Reason |
|----------|-----|--------|
| GET /codes/{code} | 300s (5 min) | Code status changes during tournament |
| GET /lobby-events | 30s | Very dynamic, real-time events |

---

## Testing Commands

```bash
# Unit tests
uv run pytest tests/test_tournament.py -v

# Integration tests
uv run pytest tests/integration/test_endpoints.py::test_tournament_providers_validation -v

# All tests
uv run pytest tests/ -v

# Coverage
uv run pytest tests/test_tournament.py --cov=app/routers/tournament --cov-report=html
```

---

## Verification Commands

```bash
# Check server starts
make run

# Check OpenAPI docs
curl http://127.0.0.1:8080/docs

# Check tournament endpoints
curl http://127.0.0.1:8080/lol/tournament/v5/codes/TEST?region=euw1
curl http://127.0.0.1:8080/lol/tournament-stub/v5/codes/TEST?region=euw1

# Check OpenAPI schema
curl http://127.0.0.1:8080/openapi.json | jq -r '.paths | keys | .[]' | grep tournament
```

---

## Common Issues & Fixes

### Issue: 403 Forbidden on all requests

**Cause**: No tournament API access

**Fix**:
1. Apply at https://developer.riotgames.com/
2. Or use tournament-stub endpoints

### Issue: Import error for tournament module

**Cause**: Router not exported in `__init__.py`

**Fix**:
```python
# app/routers/__init__.py
from app.routers import tournament, tournament_stub
```

### Issue: PUT doesn't invalidate cache

**Cause**: Missing `cache.delete()` call

**Fix**:
```python
await cache.delete(f"tournament:code:{region}:{tournamentCode}")
```

### Issue: force refresh doesn't work

**Cause**: Not passing `force_refresh` to `fetch_with_cache`

**Fix**:
```python
force_refresh=force  # Use force_refresh, not force
```

---

## Quick Copy-Paste Templates

### POST Method (client.py)

```python
async def post(self, path: str, region: str, is_platform_endpoint: bool = False, data: dict | None = None) -> dict:
    await rate_limiter.acquire()
    api_key = self.key_rotator.get_next_key()
    base_url = get_base_url(region, is_platform_endpoint)
    url = f"{base_url}{path}"
    headers = {"X-Riot-Token": api_key}
    response = await self.client.post(url, json=data, headers=headers)
    # ... error handling (same as get method)
    return response.json()
```

### PUT Method (client.py)

```python
async def put(self, path: str, region: str, is_platform_endpoint: bool = False, data: dict | None = None) -> dict:
    await rate_limiter.acquire()
    api_key = self.key_rotator.get_next_key()
    base_url = get_base_url(region, is_platform_endpoint)
    url = f"{base_url}{path}"
    headers = {"X-Riot-Token": api_key}
    response = await self.client.put(url, json=data, headers=headers)
    # ... error handling (same as get method)
    return response.json()
```

---

## Endpoints Summary

| Method | Path | Cached | TTL | Force Refresh |
|--------|------|--------|-----|---------------|
| POST | /providers | No | - | No |
| POST | /tournaments | No | - | No |
| POST | /codes | No | - | No |
| GET | /codes/{code} | Yes | 300s | Yes |
| PUT | /codes/{code} | No* | - | No |
| GET | /lobby-events/by-code/{code} | Yes | 30s | Yes |

*Invalidates existing cache

---

## Documentation Links

- **Design Doc**: `docs/architecture/tournament-router-design.md`
- **Diagrams**: `docs/architecture/tournament-router-diagram.md`
- **Implementation**: `docs/architecture/tournament-router-implementation.md`
- **API Docs**: `docs/api/tournament-api.md`
- **Riot API**: https://developer.riotgames.com/apis#tournament-v5

---

## Time Estimate

- **Foundation**: 15 minutes
- **HTTP Client**: 35 minutes
- **Tournament Router**: 90 minutes
- **Stub Router**: 30 minutes
- **Integration**: 10 minutes
- **Testing**: 60 minutes

**Total**: ~4 hours

---

**Status**: Ready for Implementation
**Next**: Start with Phase 1 (Foundation)
