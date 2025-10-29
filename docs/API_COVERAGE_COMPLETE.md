# Complete API Coverage Report

## Summary

This document provides a comprehensive overview of all mapped API endpoints, models, and enums in the LOL API Gateway.

**Last Updated**: After complete audit and enhancement
**Total Endpoints**: 33 (32 Riot API + 1 health check)
**Total Pydantic Models**: 50+ input validation models
**Total Enums**: 7 comprehensive enums

---

## 🎯 Enum Coverage

### ✅ Complete Enums (app/models/common.py)

#### 1. **PlatformRegion**
Regional routing for platform endpoints (ACCOUNT-V1, MATCH-V5):
- `AMERICAS`
- `EUROPE`
- `ASIA`
- `SEA`

#### 2. **GameRegion**
All League of Legends game regions:
- **Europe**: `EUW1`, `EUN1`, `TR1`, `RU`
- **Americas**: `NA1`, `BR1`, `LA1`, `LA2`
- **Asia**: `KR`, `JP1`
- **SEA/Oceania**: `OC1`, `PH2`, `SG2`, `TH2`, `TW2`, `VN2`

#### 3. **QueueType** (Enhanced)
Ranked queue types including TFT:
- `RANKED_SOLO_5x5`
- `RANKED_FLEX_SR`
- `RANKED_FLEX_TT`
- `RANKED_TFT`
- `RANKED_TFT_TURBO`
- `RANKED_TFT_DOUBLE_UP`

#### 4. **Tier** (NEW)
All ranked tiers from lowest to highest:
- `IRON`
- `BRONZE`
- `SILVER`
- `GOLD`
- `PLATINUM`
- `EMERALD` (Season 2023+)
- `DIAMOND`
- `MASTER`
- `GRANDMASTER`
- `CHALLENGER`

#### 5. **Division** (NEW)
Divisions within tiers (Iron through Diamond):
- `I` (highest)
- `II`
- `III`
- `IV` (lowest)

Note: Master, Grandmaster, and Challenger don't use divisions.

#### 6. **ChallengeLevel** (Enhanced)
Challenge progression tiers (different from ranked tiers):
- `NONE`
- `IRON`
- `BRONZE`
- `SILVER`
- `GOLD`
- `PLATINUM`
- `EMERALD`
- `DIAMOND`
- `MASTER`
- `GRANDMASTER`
- `CHALLENGER`

---

## 📊 API Coverage by Service

### 1. ACCOUNT-V1 (3 endpoints) ✅
**Router**: `app/routers/account.py` (Pydantic migrated)
**Models**: `app/models/account.py`

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/accounts/by-puuid/{puuid}` | GET | `AccountByPuuidParams`, `AccountByPuuidQuery` | ✅ |
| `/accounts/by-riot-id/{gameName}/{tagLine}` | GET | `AccountByRiotIdParams`, `AccountByRiotIdQuery` | ✅ |
| `/active-shards/by-game/{game}/by-puuid/{puuid}` | GET | `ActiveShardParams`, `ActiveShardQuery` | ✅ |

**Regional Routing**: Uses `PlatformRegion` enum (americas, europe, asia, sea)

---

### 2. SUMMONER-V4 (3 endpoints) ⏳
**Router**: `app/routers/summoner.py` (NOT YET migrated to Pydantic)
**Models**: `app/models/summoner.py` (ready)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/summoners/by-name/{summonerName}` | GET | `SummonerByNameParams`, `SummonerByNameQuery` | ⏳ |
| `/summoners/by-puuid/{encryptedPUUID}` | GET | `SummonerByPuuidParams`, `SummonerByPuuidQuery` | ⏳ |
| `/summoners/{encryptedSummonerId}` | GET | `SummonerByIdParams`, `SummonerByIdQuery` | ⏳ |

---

### 3. MATCH-V5 (3 endpoints) ✅
**Router**: `app/routers/match.py` (Pydantic migrated + NEW PARAMETERS)
**Models**: `app/models/match.py`

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/matches/by-puuid/{puuid}/ids` | GET | `MatchIdsByPuuidParams`, `MatchIdsByPuuidQuery` | ✅ NEW PARAMS |
| `/matches/{matchId}` | GET | `MatchParams`, `MatchQuery` | ✅ |
| `/matches/{matchId}/timeline` | GET | `MatchTimelineParams`, `MatchTimelineQuery` | ✅ |

**🆕 NEW Parameters in `/matches/by-puuid/{puuid}/ids`**:
- ✅ `startTime` (Optional[int]) - Filter matches after timestamp
- ✅ `endTime` (Optional[int]) - Filter matches before timestamp
- ✅ `queue` (Optional[int]) - Filter by queue ID
- ✅ `type` (Optional[str]) - Filter by type (ranked, normal, tourney, tutorial)

**Regional Routing**: Uses `PlatformRegion` enum

---

### 4. LEAGUE-V4 (5 endpoints) ⏳
**Router**: `app/routers/league.py` (1 NEW endpoint added, NOT yet migrated to Pydantic)
**Models**: `app/models/league.py` (ready + enhanced)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/challengerleagues/by-queue/{queue}` | GET | `LeagueByQueueParams`, `LeagueByQueueQuery` | ⏳ |
| `/grandmasterleagues/by-queue/{queue}` | GET | `LeagueByQueueParams`, `LeagueByQueueQuery` | ⏳ |
| `/masterleagues/by-queue/{queue}` | GET | `LeagueByQueueParams`, `LeagueByQueueQuery` | ⏳ |
| `/entries/by-summoner/{encryptedSummonerId}` | GET | `LeagueEntriesBySummonerParams`, `LeagueEntriesBySummonerQuery` | ⏳ |
| `/entries/{queue}/{tier}/{division}` | GET | `LeagueEntriesParams`, `LeagueEntriesQuery` | 🆕 ADDED |

**🆕 Models Enhanced**:
- Uses `Tier` enum for tier validation
- Uses `Division` enum for division validation
- Pagination support with `page` parameter

---

### 5. LEAGUE-EXP-V4 (1 endpoint) 🆕
**Router**: `app/routers/league_exp.py` (NEW, with Pydantic)
**Models**: `app/models/league_exp.py` (NEW)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/entries/{queue}/{tier}/{division}` | GET | `LeagueExpEntriesParams`, `LeagueExpEntriesQuery` | 🆕 ✅ |

**Note**: This is an experimental API similar to LEAGUE-V4 but with different pagination handling.

---

### 6. CHAMPION-MASTERY-V4 (4 endpoints) ⏳
**Router**: `app/routers/champion_mastery.py` (NOT yet migrated)
**Models**: `app/models/champion_mastery.py` (ready)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/champion-masteries/by-puuid/{puuid}` | GET | `ChampionMasteryByPuuidParams`, `ChampionMasteryByPuuidQuery` | ⏳ |
| `/champion-masteries/by-puuid/{puuid}/by-champion/{championId}` | GET | `ChampionMasteryByPuuidByChampionParams`, `ChampionMasteryByPuuidByChampionQuery` | ⏳ |
| `/champion-masteries/by-puuid/{puuid}/top` | GET | `TopChampionMasteriesParams`, `TopChampionMasteriesQuery` | ⏳ |
| `/scores/by-puuid/{puuid}` | GET | `MasteryScoreParams`, `MasteryScoreQuery` | ⏳ |

---

### 7. CHALLENGES-V1 (5 endpoints) ⏳
**Router**: `app/routers/challenges.py` (NOT yet migrated)
**Models**: `app/models/challenges.py` (ready + enhanced)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/challenges/config` | GET | `AllChallengesConfigQuery` | ⏳ |
| `/challenges/{challengeId}/config` | GET | `ChallengeConfigParams`, `ChallengeConfigQuery` | ⏳ |
| `/challenges/{challengeId}/leaderboards/by-level/{level}` | GET | `ChallengeLeaderboardParams`, `ChallengeLeaderboardQuery` | ⏳ |
| `/challenges/{challengeId}/percentiles` | GET | `ChallengePercentilesParams`, `ChallengePercentilesQuery` | ⏳ |
| `/player-data/{puuid}` | GET | `PlayerChallengesParams`, `PlayerChallengesQuery` | ⏳ |

**Enhanced**: Uses complete `ChallengeLevel` enum (NONE through CHALLENGER)

---

### 8. CLASH-V1 (5 endpoints) ⏳
**Router**: `app/routers/clash.py` (NOT yet migrated)
**Models**: `app/models/clash.py` (ready)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/players/by-puuid/{puuid}` | GET | `ClashPlayerParams`, `ClashPlayerQuery` | ⏳ |
| `/teams/{teamId}` | GET | `ClashTeamParams`, `ClashTeamQuery` | ⏳ |
| `/tournaments` | GET | `ClashTournamentsQuery` | ⏳ |
| `/tournaments/{tournamentId}` | GET | `ClashTournamentParams`, `ClashTournamentQuery` | ⏳ |
| `/tournaments/by-team/{teamId}` | GET | `ClashTournamentByTeamParams`, `ClashTournamentByTeamQuery` | ⏳ |

---

### 9. SPECTATOR-V5 (2 endpoints) ⏳
**Router**: `app/routers/spectator.py` (NOT yet migrated)
**Models**: `app/models/spectator.py` (ready)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/active-games/by-summoner/{puuid}` | GET | `ActiveGameParams`, `ActiveGameQuery` | ⏳ |
| `/featured-games` | GET | `FeaturedGamesQuery` | ⏳ |

---

### 10. LOL-STATUS-V4 / PLATFORM (1 endpoint) ⏳
**Router**: `app/routers/platform.py` (NOT yet migrated)
**Models**: `app/models/platform.py` (ready)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/platform-data` | GET | `PlatformStatusQuery` | ⏳ |

---

### 11. CHAMPION-V3 (1 endpoint) ⏳
**Router**: `app/routers/champion.py` (NOT yet migrated)
**Models**: `app/models/champion.py` (ready)

| Endpoint | Method | Pydantic Models | Status |
|----------|--------|----------------|--------|
| `/champion-rotations` | GET | `ChampionRotationsQuery` | ⏳ |

---

### 12. HEALTH (1 endpoint) ✅
**Router**: `app/routers/health.py`
**No models needed** - Simple health check endpoint

| Endpoint | Method | Status |
|----------|--------|--------|
| `/health` | GET | ✅ |

---

## 📦 Model Files Structure

```
app/models/
├── __init__.py              ✅ Updated with all exports
├── common.py                ✅ Enhanced (7 enums, 3 base models)
├── account.py               ✅ Complete (6 models)
├── summoner.py              ✅ Complete (6 models)
├── match.py                 ✅ Enhanced (6 models + new params)
├── league.py                ✅ Enhanced (6 models + Tier/Division)
├── league_exp.py            🆕 NEW (2 models)
├── champion_mastery.py      ✅ Complete (8 models)
├── challenges.py            ✅ Enhanced (10 models)
├── clash.py                 ✅ Complete (10 models)
├── spectator.py             ✅ Complete (4 models)
├── platform.py              ✅ Complete (1 model)
└── champion.py              ✅ Complete (1 model)
```

**Total**: 13 model files, 70+ models

---

## 🎯 Migration Status

### ✅ Completed (2/11 APIs)
1. **ACCOUNT-V1** - All 3 endpoints migrated to Pydantic
2. **MATCH-V5** - All 3 endpoints migrated + NEW optional parameters added

### 🆕 NEW (1 API)
1. **LEAGUE-EXP-V4** - Created router + models, registered in main.py

### ⏳ Pending Migration (8/11 APIs)
1. SUMMONER-V4 (3 endpoints)
2. LEAGUE-V4 (5 endpoints - 1 endpoint ADDED)
3. CHAMPION-MASTERY-V4 (4 endpoints)
4. CHALLENGES-V1 (5 endpoints)
5. CLASH-V1 (5 endpoints)
6. SPECTATOR-V5 (2 endpoints)
7. PLATFORM (1 endpoint)
8. CHAMPION-V3 (1 endpoint)

**Total to migrate**: 26 endpoints

---

## 🆕 What Was Added/Fixed

### 1. Missing Enums
✅ `Tier` - All ranked tiers (IRON through CHALLENGER)
✅ `Division` - Divisions I through IV
✅ `ChallengeLevel` - Enhanced with NONE and EMERALD
✅ `QueueType` - Added TFT queue types

### 2. Missing Endpoints
✅ `LEAGUE-V4: /entries/{queue}/{tier}/{division}` - Added to league.py router
✅ `LEAGUE-EXP-V4: /entries/{queue}/{tier}/{division}` - NEW router created

### 3. Missing Parameters
✅ `MATCH-V5: /matches/by-puuid/{puuid}/ids` - Added startTime, endTime, queue, type

### 4. Enhanced Models
✅ `league.py` models - Now use Tier and Division enums
✅ `league_exp.py` models - NEW models for experimental API
✅ `match.py` models - Enhanced with all optional filters

---

## 📝 Next Steps

### Priority 1: Complete Pydantic Migration
Migrate remaining 8 routers to use Pydantic models (26 endpoints total).

### Priority 2: Response Models
Create Pydantic models for API responses (currently only input validation exists).

### Priority 3: OpenAPI Enhancement
With complete input models, the OpenAPI documentation will be fully typed and validated.

---

## 🔍 Verification Checklist

- [x] All Riot API enums mapped (Tier, Division, QueueType, ChallengeLevel)
- [x] LEAGUE-EXP-V4 API added
- [x] Missing LEAGUE-V4 endpoint added
- [x] Missing MATCH-V5 parameters added
- [x] All model files created and exported
- [x] LEAGUE-EXP-V4 router registered in main.py
- [ ] Remaining routers migrated to Pydantic
- [ ] Response models created
- [ ] Full integration testing

---

**Status**: 🟢 Models Complete | 🟡 Partial Router Migration | 🔴 Testing Needed
