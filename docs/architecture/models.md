# Data Models & Validation

This section describes the comprehensive Pydantic V2 input validation system used throughout the LOLStonks API Gateway.

## Overview

All API endpoints use Pydantic V2 models for input validation, providing:

- **Type Safety**: Automatic validation of input types and constraints
- **Self-Documenting API**: Automatic OpenAPI schema generation
- **Reusability**: Shared models reduce code duplication
- **Extensibility**: Easy to add new validation rules and constraints
- **Better Error Handling**: Detailed validation error messages

## Model Architecture

### Directory Structure

```
app/models/
├── __init__.py          # Central exports and registry
├── common.py            # Base models, enums, and shared utilities
├── account.py           # ACCOUNT-V1 (Riot ID) models
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

## Core Components

### Regional Routing Models

#### Platform Regions
Used for Account-V1 and Match-V5 APIs that require regional routing:

```python
class PlatformRegion(str, Enum):
    """Regional routing for platform endpoints."""
    AMERICAS = "americas"
    EUROPE = "europe"
    ASIA = "asia"
    SEA = "sea"
```

#### Game Regions
Used for game-specific endpoints (summoner, league, etc.):

```python
class GameRegion(str, Enum):
    """Game-specific regions."""
    # Europe
    EUW1 = "euw1"     # Europe West
    EUN1 = "eun1"     # Europe Nordic & East
    TR1 = "tr1"       # Turkey
    RU = "ru"         # Russia

    # Americas
    NA1 = "na1"       # North America
    BR1 = "br1"       # Brazil
    LA1 = "la1"       # Latin America North
    LA2 = "la2"       # Latin America South

    # Asia
    KR = "kr"         # Korea
    JP1 = "jp1"       # Japan

    # SEA/Oceania
    OC1 = "oc1"       # Oceania
    PH2 = "ph2"       # Philippines
    SG2 = "sg2"       # Singapore
    TH2 = "th2"       # Thailand
    TW2 = "tw2"       # Taiwan
    VN2 = "vn2"       # Vietnam
```

### Base Query Models

#### Region Query
Standard region parameter for game-specific endpoints:

```python
class RegionQuery(BaseModel):
    """Standard region parameter for game-specific endpoints."""
    region: Annotated[GameRegion, Field(
        default_factory=lambda: GameRegion(settings.riot_default_region),
        description="Riot API game region"
    )]
```

#### Platform Region Query
Regional routing for platform endpoints:

```python
class PlatformRegionQuery(BaseModel):
    """Regional routing for platform endpoints (ACCOUNT, MATCH APIs)."""
    region: Annotated[PlatformRegion, Field(
        default=PlatformRegion.AMERICAS,
        description="Riot API platform region"
    )]
```

#### Pagination Query
Standard pagination parameters for list endpoints:

```python
class PaginationQuery(BaseModel):
    """Pagination parameters for list endpoints."""
    start: Annotated[int, Field(
        default=0,
        ge=0,
        description="Start index for pagination"
    )]
    count: Annotated[int, Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items to return (1-100)"
    )]
```

### Specialized Enums

#### Queue Types
Ranked queue identifiers:

```python
class QueueType(str, Enum):
    """Ranked queue types."""
    RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"
    RANKED_FLEX_SR = "RANKED_FLEX_SR"
    RANKED_FLEX_TT = "RANKED_FLEX_TT"
```

#### Challenge Levels
Challenge tier levels:

```python
class ChallengeLevel(str, Enum):
    """Challenge tier levels."""
    MASTER = "MASTER"
    GRANDMASTER = "GRANDMASTER"
    CHALLENGER = "CHALLENGER"
```

## Usage Patterns

### Router Implementation

Endpoints use FastAPI's dependency injection system with Pydantic models:

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

    # Optional filtering parameters
    if query.startTime:
        # Filter by start time
        pass
```

### Model Naming Conventions

Models follow consistent naming patterns:

- **Path Parameters**: `{EndpointName}Params`
  - Examples: `MatchIdsByPuuidParams`, `AccountByPuuidParams`

- **Query Parameters**: `{EndpointName}Query`
  - Examples: `MatchIdsByPuuidQuery`, `AccountByPuuidQuery`

## API-Specific Examples

### Match V5 Models

Enhanced query parameters for match history:

```python
class MatchIdsByPuuidQuery(PlatformRegionQuery, PaginationQuery):
    """Match history query parameters with comprehensive filtering."""
    startTime: Annotated[Optional[int], Field(
        default=None,
        description="Filter matches after this timestamp (epoch milliseconds)"
    )]
    endTime: Annotated[Optional[int], Field(
        default=None,
        description="Filter matches before this timestamp (epoch milliseconds)"
    )]
    queue: Annotated[Optional[int], Field(
        default=None,
        description="Filter by queue ID (420 for Ranked Solo)"
    )]
    type: Annotated[Optional[str], Field(
        default=None,
        description="Match type: ranked, normal, tourney, tutorial"
    )]
```

**Example Usage:**
```bash
GET /lol/match/v5/matches/by-puuid/{puuid}/ids?region=europe&start=0&count=20&startTime=1640000000&queue=420&type=ranked
```

### Account V1 Models

Riot ID validation with proper constraints:

```python
class AccountByRiotIdParams(BaseModel):
    """Riot ID components with validation."""
    gameName: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Summoner name (1-100 characters)"
    )]
    tagLine: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Tag line (1-100 characters)"
    )]
```

### League V4 Models

Enum-based queue validation:

```python
class LeagueByQueueParams(BaseModel):
    """League parameters with queue type validation."""
    queue: Annotated[QueueType, Field(
        description="Ranked queue type"
    )]
```

## Validation Features

### Common Validation Patterns

#### String Length Validation
```python
puuid: Annotated[str, Field(
    min_length=1,
    max_length=100,
    description="Player UUID (1-100 characters)"
)]
```

#### Numeric Range Validation
```python
count: Annotated[int, Field(
    ge=1,
    le=100,
    description="Number of items (1-100)"
)]
```

#### Pattern Matching
```python
matchId: Annotated[str, Field(
    pattern=r"^[A-Z0-9]+_\d+$",
    description="Match ID format: TRAILING_NUMBER"
)]
```

#### Enum Validation
```python
queue: Annotated[QueueType, Field(
    description="Queue type for ranked play"
)]
```

## Migration Status

### ✅ Completed Migrations

- **Account-V1**: All endpoints migrated to PlatformRegionQuery
- **Match-V5**: All endpoints migrated with enhanced filtering parameters

### 🔄 Pending Migrations

The following endpoints are scheduled for migration to Pydantic models:

- SUMMONER-V4 (summonerByName, summonerByPuuid, etc.)
- LEAGUE-V4 (challengerByQueue, grandmasterByQueue, etc.)
- CHAMPION-MASTERY-V4 (all mastery endpoints)
- CHALLENGES-V1 (player challenges)
- CLASH-V1 (tournament information)
- SPECTATOR-V5 (live game data)
- LOL-STATUS-V4 (platform status)
- CHAMPION-V3 (champion information)

## Benefits

### 1. Type Safety & Validation
```python
# Before: No validation
async def get_summoner(name: str, region: str = "euw1"):
    pass  # Any string accepted, no validation

# After: Comprehensive validation
async def get_summoner(
    params: Annotated[SummonerByNameParams, Depends()],
    query: Annotated[RegionQuery, Depends()],
):
    pass  # Validated summoner name and region
```

### 2. Automatic OpenAPI Documentation
FastAPI generates detailed API documentation from Pydantic models:
- Field types and constraints
- Default values and descriptions
- Enum values and meanings
- Validation rules and error messages

### 3. Code Reusability
```python
# Region query used across multiple endpoints
class SummonerByNameQuery(RegionQuery):
    pass

class SummonerByPuuidQuery(RegionQuery):
    pass

# Both inherit region validation automatically
```

### 4. Easy Extension
```python
# Add new optional parameter without breaking changes
class MatchIdsByPuuidQuery(PlatformRegionQuery, PaginationQuery):
    # Future extensions
    champion: Annotated[Optional[int], Field(
        default=None,
        description="Filter by champion ID"
    )]
    role: Annotated[Optional[str], Field(
        default=None,
        description="Filter by role"
    )]
```

## Error Handling

Pydantic provides detailed validation errors:

```json
{
  "detail": [
    {
      "loc": ["query", "count"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 100}
    }
  ]
}
```

This validation system ensures API reliability, developer productivity, and excellent user experience through clear error messages and comprehensive API documentation.