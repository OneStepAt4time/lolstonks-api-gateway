# Pydantic Models Structure

This document describes the organization and usage of Pydantic V2 input validation models for the API Gateway.

## Overview

All API endpoint input parameters are now validated using Pydantic V2 models. This provides:
- **Type safety**: Automatic validation of input types
- **Better documentation**: Self-documenting API through OpenAPI schema
- **Reusability**: Shared models reduce code duplication
- **Extensibility**: Easy to add new validation rules and constraints

## Directory Structure

```
app/models/
├── __init__.py          # Central exports
├── common.py            # Reusable base models and enums
├── account.py           # ACCOUNT-V1 models
├── summoner.py          # SUMMONER-V4 models
├── match.py             # MATCH-V5 models
├── league.py            # LEAGUE-V4 models
├── champion_mastery.py  # CHAMPION-MASTERY-V4 models
├── challenges.py        # CHALLENGES-V1 models
├── clash.py             # CLASH-V1 models
├── spectator.py         # SPECTATOR-V5 models
├── platform.py          # LOL-STATUS-V4 models
└── champion.py          # CHAMPION-V3 models
```

## Common Models (`app/models/common.py`)

### Enums

#### `PlatformRegion`
Regional routing for platform endpoints (ACCOUNT-V1, MATCH-V5):
- `AMERICAS`
- `EUROPE`
- `ASIA`
- `SEA`

#### `GameRegion`
Game-specific regions:
- **Europe**: `EUW1`, `EUN1`, `TR1`, `RU`
- **Americas**: `NA1`, `BR1`, `LA1`, `LA2`
- **Asia**: `KR`, `JP1`
- **SEA/Oceania**: `OC1`, `PH2`, `SG2`, `TH2`, `TW2`, `VN2`

#### `QueueType`
Ranked queue types:
- `RANKED_SOLO_5x5`
- `RANKED_FLEX_SR`
- `RANKED_FLEX_TT`

#### `ChallengeLevel`
Challenge tier levels:
- `MASTER`
- `GRANDMASTER`
- `CHALLENGER`

### Base Query Models

#### `RegionQuery`
Standard region parameter for game-specific endpoints.

**Fields:**
- `region: GameRegion` - Defaults to `settings.riot_default_region`

**Usage:**
```python
from app.models.common import RegionQuery

class MyEndpointQuery(RegionQuery):
    # Inherits region field
    additional_param: str
```

#### `PlatformRegionQuery`
Regional routing for platform endpoints (ACCOUNT, MATCH APIs).

**Fields:**
- `region: PlatformRegion` - Defaults to `PlatformRegion.AMERICAS`

#### `PaginationQuery`
Pagination parameters for list endpoints.

**Fields:**
- `start: int` - Start index (default: 0, min: 0)
- `count: int` - Number of items (default: 20, min: 1, max: 100)

## Usage Pattern

### Router Implementation

Routers use `Depends()` to inject Pydantic models for both path and query parameters:

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from app.models.match import MatchIdsByPuuidParams, MatchIdsByPuuidQuery

router = APIRouter()

@router.get("/matches/by-puuid/{puuid}/ids")
async def get_match_ids_by_puuid(
    params: Annotated[MatchIdsByPuuidParams, Depends()],
    query: Annotated[MatchIdsByPuuidQuery, Depends()],
):
    # Access validated parameters
    puuid = params.puuid
    region = query.region
    start = query.start
    count = query.count

    # Optional parameters
    if query.startTime:
        # Filter by start time
        pass
```

### Model Naming Convention

Models follow a consistent naming pattern:

- **Path parameters**: `{EndpointName}Params`
  - Example: `MatchIdsByPuuidParams`, `AccountByPuuidParams`

- **Query parameters**: `{EndpointName}Query`
  - Example: `MatchIdsByPuuidQuery`, `AccountByPuuidQuery`

## API-Specific Models

### MATCH-V5 (`app/models/match.py`)

#### `MatchIdsByPuuidQuery`
Includes **all optional filtering parameters** from Riot API:

```python
class MatchIdsByPuuidQuery(PlatformRegionQuery, PaginationQuery):
    startTime: Optional[int] = None  # Epoch timestamp filter
    endTime: Optional[int] = None    # Epoch timestamp filter
    queue: Optional[int] = None      # Queue ID filter
    type: Optional[str] = None       # Match type (ranked, normal, tourney, tutorial)
```

**Example usage:**
```bash
GET /lol/match/v5/matches/by-puuid/{puuid}/ids?region=europe&start=0&count=20&startTime=1640000000&queue=420&type=ranked
```

### ACCOUNT-V1 (`app/models/account.py`)

#### `AccountByRiotIdParams`
Validates Riot ID components:

```python
class AccountByRiotIdParams(BaseModel):
    gameName: str  # min_length=1, max_length=100
    tagLine: str   # min_length=1, max_length=100
```

### LEAGUE-V4 (`app/models/league.py`)

#### `LeagueByQueueParams`
Uses enum for queue type validation:

```python
class LeagueByQueueParams(BaseModel):
    queue: QueueType  # RANKED_SOLO_5x5, RANKED_FLEX_SR, RANKED_FLEX_TT
```

## Completed Migrations

✅ **Account-V1** (`app/routers/account.py`)
- All 3 endpoints migrated
- Uses `PlatformRegionQuery` for regional routing

✅ **Match-V5** (`app/routers/match.py`)
- All 3 endpoints migrated
- **NEW**: Added `startTime`, `endTime`, `queue`, `type` optional parameters
- Uses `PlatformRegionQuery` for regional routing

## Pending Migrations

The following routers still need to be updated to use Pydantic models:

- `app/routers/summoner.py` (SUMMONER-V4)
- `app/routers/league.py` (LEAGUE-V4)
- `app/routers/champion_mastery.py` (CHAMPION-MASTERY-V4)
- `app/routers/challenges.py` (CHALLENGES-V1)
- `app/routers/clash.py` (CLASH-V1)
- `app/routers/spectator.py` (SPECTATOR-V5)
- `app/routers/platform.py` (LOL-STATUS-V4)
- `app/routers/champion.py` (CHAMPION-V3)

## Benefits

### 1. Type Safety
```python
# Before: No validation
async def get_match(matchId: str, region: str = "euw1"):
    pass  # Any string accepted

# After: Validated with Pydantic
async def get_match(
    params: Annotated[MatchParams, Depends()],
    query: Annotated[MatchQuery, Depends()],
):
    pass  # matchId must match pattern ^[A-Z0-9]+_\d+$
```

### 2. Better OpenAPI Documentation
FastAPI automatically generates detailed OpenAPI schemas from Pydantic models, showing:
- Field types and constraints
- Default values
- Descriptions
- Enum values

### 3. Reusability
```python
# Region query used across multiple endpoints
class SummonerByNameQuery(RegionQuery):
    pass

class SummonerByPuuidQuery(RegionQuery):
    pass

# Both inherit region field with validation
```

### 4. Easy Extension
```python
# Add new optional parameter
class MatchIdsByPuuidQuery(PlatformRegionQuery, PaginationQuery):
    # Easy to add new filters
    champion: Optional[int] = None  # Filter by champion
    role: Optional[str] = None      # Filter by role
```

## Validation Rules

Common validation patterns used:

### String Length
```python
puuid: Annotated[str, Field(min_length=1, max_length=100)]
```

### Numeric Ranges
```python
count: Annotated[int, Field(ge=1, le=100)]  # 1 <= count <= 100
```

### Pattern Matching
```python
matchId: Annotated[str, Field(pattern=r"^[A-Z0-9]+_\d+$")]
```

### Enums
```python
queue: Annotated[QueueType, Field(description="Queue type")]
```

## Next Steps

To complete the migration of remaining routers:

1. Import appropriate models from `app.models`
2. Replace function parameters with `Annotated[ModelName, Depends()]`
3. Update parameter access from `param` to `params.param` or `query.param`
4. Test endpoint to ensure validation works correctly

Example migration pattern:
```python
# Before
@router.get("/endpoint/{param}")
async def handler(param: str, query_param: str = "default"):
    value = param
    query_value = query_param

# After
@router.get("/endpoint/{param}")
async def handler(
    params: Annotated[EndpointParams, Depends()],
    query: Annotated[EndpointQuery, Depends()],
):
    value = params.param
    query_value = query.query_param
```
