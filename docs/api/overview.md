# LOL API Gateway

Intelligent proxy for Riot Games API with caching, rate limiting, and match tracking

**Version**: 1.0.0

**Generated**: 2025-10-28 18:34:54 UTC

## API Statistics

- **Total Endpoints**: 34
- **Total Schemas**: 7
- **API Base URL**: `http://localhost:8080`

## Interactive Documentation

When the server is running, you can access:

- **Swagger UI**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **ReDoc**: [http://localhost:8080/redoc](http://localhost:8080/redoc)
- **OpenAPI JSON**: [http://localhost:8080/openapi.json](http://localhost:8080/openapi.json)

## API Endpoints

### health

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/health` | Health Check | None | Unknown |

### challenges

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/challenges/v1/challenges/config` | Get All Challenges Config | Query: region | Unknown |
| 🟢 GET | `/lol/challenges/v1/challenges/{challengeId}/config` | Get Challenge Config | Path: challengeId<br>Query: region | Unknown |
| 🟢 GET | `/lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}` | Get Challenge Leaderboard | Path: challengeId, level<br>Query: region, limit | Unknown |
| 🟢 GET | `/lol/challenges/v1/challenges/{challengeId}/percentiles` | Get Challenge Percentiles | Path: challengeId<br>Query: region | Unknown |
| 🟢 GET | `/lol/challenges/v1/player-data/{puuid}` | Get Player Challenges | Path: puuid<br>Query: region | Unknown |

### champion-mastery

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}` | Get All Champion Masteries | Path: puuid<br>Query: region | Unknown |
| 🟢 GET | `/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{championId}` | Get Champion Mastery | Path: puuid, championId<br>Query: region | Unknown |
| 🟢 GET | `/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top` | Get Top Champion Masteries | Path: puuid<br>Query: region, count | Unknown |
| 🟢 GET | `/lol/champion-mastery/v4/scores/by-puuid/{puuid}` | Get Mastery Score | Path: puuid<br>Query: region | Unknown |

### clash

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/clash/v1/players/by-puuid/{puuid}` | Get Clash Player | Path: puuid<br>Query: region | Unknown |
| 🟢 GET | `/lol/clash/v1/teams/{teamId}` | Get Clash Team | Path: teamId<br>Query: region | Unknown |
| 🟢 GET | `/lol/clash/v1/tournaments` | Get Clash Tournaments | Query: region | Unknown |
| 🟢 GET | `/lol/clash/v1/tournaments/by-team/{teamId}` | Get Clash Tournament By Team | Path: teamId<br>Query: region | Unknown |
| 🟢 GET | `/lol/clash/v1/tournaments/{tournamentId}` | Get Clash Tournament | Path: tournamentId<br>Query: region | Unknown |

### league-exp

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/league-exp/v4/entries/{queue}/{tier}/{division}` | Get League Exp Entries | Path: queue, tier, division<br>Query: region, page | Unknown |

### league

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/league/v4/challengerleagues/by-queue/{queue}` | Get Challenger League | Path: queue<br>Query: region | Unknown |
| 🟢 GET | `/lol/league/v4/entries/by-summoner/{encryptedSummonerId}` | Get League Entries By Summoner | Path: encryptedSummonerId<br>Query: region | Unknown |
| 🟢 GET | `/lol/league/v4/entries/{queue}/{tier}/{division}` | Get League Entries | Path: queue, tier, division<br>Query: region, page | Unknown |
| 🟢 GET | `/lol/league/v4/grandmasterleagues/by-queue/{queue}` | Get Grandmaster League | Path: queue<br>Query: region | Unknown |
| 🟢 GET | `/lol/league/v4/masterleagues/by-queue/{queue}` | Get Master League | Path: queue<br>Query: region | Unknown |

### match

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/match/v5/matches/by-puuid/{puuid}/ids` | Get Match Ids By Puuid | Path: puuid<br>Query: start, count, region, startTime, endTime, queue, type | Unknown |
| 🟢 GET | `/lol/match/v5/matches/{matchId}` | Get Match | Path: matchId<br>Query: region, force | Unknown |
| 🟢 GET | `/lol/match/v5/matches/{matchId}/timeline` | Get Match Timeline | Path: matchId<br>Query: region | Unknown |

### champion

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/platform/v3/champion-rotations` | Get Champion Rotations | Query: region | Unknown |

### spectator

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/spectator/v5/active-games/by-summoner/{puuid}` | Get Active Game | Path: puuid<br>Query: region | Unknown |
| 🟢 GET | `/lol/spectator/v5/featured-games` | Get Featured Games | Query: region | Unknown |

### platform

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/status/v4/platform-data` | Get Platform Status | Query: region | Unknown |

### summoner

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/lol/summoner/v4/summoners/by-name/{summonerName}` | Get Summoner By Name | Path: summonerName<br>Query: region | Unknown |
| 🟢 GET | `/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}` | Get Summoner By Puuid | Path: encryptedPUUID<br>Query: region | Unknown |
| 🟢 GET | `/lol/summoner/v4/summoners/{encryptedSummonerId}` | Get Summoner By Id | Path: encryptedSummonerId<br>Query: region | Unknown |

### account

| Method | Path | Summary | Parameters | Response |
|--------|------|---------|------------|----------|
| 🟢 GET | `/riot/account/v1/accounts/by-puuid/{puuid}` | Get Account By Puuid | Path: puuid<br>Query: region | Unknown |
| 🟢 GET | `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` | Get Account By Riot Id | Path: gameName, tagLine<br>Query: region | Unknown |
| 🟢 GET | `/riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}` | Get Active Shard | Path: puuid, game<br>Query: region | Unknown |

## Data Schemas

### Other Models

#### Division

Division within a tier.

Used for Iron through Diamond (and Emerald) tiers.
Master, Grandmaster, and Challenger don't use divisions.

#### GameRegion

Game regions for platform-specific endpoints.

#### HTTPValidationError

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `detail` | array |  | ❌ |

#### PlatformRegion

Platform regions for regional routing (ACCOUNT, MATCH APIs).

#### QueueType

Queue types for League of Legends.

Includes ranked, normal, and special game modes.

#### Tier

League tier/rank levels.

Used for:
- Ranked league entries and progression (IRON → CHALLENGER)
- Challenge progression (all tiers)
- Challenge leaderboards (MASTER, GRANDMASTER, CHALLENGER only)

#### ValidationError

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `loc` | array |  | ✅ |
| `msg` | string |  | ✅ |
| `type` | string |  | ✅ |


## Error Handling

The API uses standard HTTP status codes and returns error information in the following format:

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

### Common Error Codes

| Status Code | Description | Cause |
|-------------|-------------|-------|
| 400 | Bad Request | Invalid parameters or malformed request |
| 404 | Not Found | Resource does not exist |
| 429 | Too Many Requests | Rate limit exceeded (handled automatically) |
| 500 | Internal Server Error | Server error or external API failure |
| 503 | Service Unavailable | External API (Riot) is down |

### Rate Limiting

The gateway includes automatic rate limiting with the following features:

- **Automatic Retry**: 429 responses are automatically retried with exponential backoff
- **Rate Limit Headers**: All responses include rate limit information
- **Graceful Degradation**: The service continues to operate during rate limit events

## Usage Examples

### Get Summoner by Name

Retrieve summoner information using their summoner name.

**Endpoint**: `GET /summoner/by-name/{summonerName}`

```bash
curl "http://localhost:8080/summoner/by-name/Faker?region=kr"
```

### Get Match History

Retrieve recent match IDs for a player using their PUUID.

**Endpoint**: `GET /match/ids/by-puuid/{puuid}`

```bash
curl "http://localhost:8080/match/ids/by-puuid/puuid-here?region=kr&count=5"
```

### Get Challenger League

Retrieve the challenger league for a specific queue.

**Endpoint**: `GET /league/challenger/{queue}`

```bash
curl "http://localhost:8080/league/challenger/RANKED_SOLO_5x5?region=kr"
```

### Python Client Example

```python
import httpx
import asyncio

async def get_summoner_data():
    """Get summoner information example."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8080/summoner/by-name/Faker",
            params={"region": "kr"}
        )
        if response.status_code == 200:
            return response.json()
        return None

# Usage
summoner = asyncio.run(get_summoner_data())
if summoner:
    print(f"Summoner: {summoner[\'name\']} (Level {summoner[\'summonerLevel\']})")
```

---

*Documentation generated on 2025-10-28 18:34:54 UTC*

For the most up-to-date interactive documentation, visit [Swagger UI](http://localhost:8000/docs) when the server is running.