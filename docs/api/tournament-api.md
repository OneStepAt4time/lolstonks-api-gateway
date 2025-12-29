# Tournament API Documentation

**Version**: 1.0
**Last Updated**: 2025-01-29
**Status**: Designed, Ready for Implementation

---

## Overview

The lolstonks-api-gateway provides routers for both **Tournament V5** (production) and **Tournament Stub V5** (testing) APIs from Riot Games.

### Important: Tournament API Access

**Requires Tournament-Specific API Key**

The Tournament API requires special access that is **NOT included with standard Riot API keys**. Standard API keys will receive `403 Forbidden` errors.

**How to Get Access**:
1. Visit [Riot Developer Portal](https://developer.riotgames.com/)
2. Apply for tournament API access
3. Receive tournament-specific API key
4. Configure in gateway: `RIOT_API_KEY` or `RIOT_API_KEYS`

**Alternative**: Use the **Tournament Stub V5** API for testing without special access.

---

## Available Routers

| Router | Base Path | Purpose | Special Access Required |
|--------|-----------|---------|------------------------|
| **Tournament V5** | `/lol/tournament/v5/*` | Production tournaments | Yes |
| **Tournament Stub V5** | `/lol/tournament-stub/v5/*` | Testing/development | No |

---

## Endpoints

### Tournament V5 Endpoints

#### POST /providers

Register a tournament provider.

**Endpoint**: `POST /lol/tournament/v5/providers`

**Query Parameters**:
- `region` (string): Region code (default: `euw1`)

**Request Body**:
```json
{
  "region": "euw1",
  "url": "https://example.com/callback"
}
```

**Response**:
```json
{
  "providerId": 123
}
```

**Example**:
```bash
curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/providers?region=euw1" \
  -H "Content-Type: application/json" \
  -d '{"region": "euw1", "url": "https://example.com/callback"}'
```

---

#### POST /tournaments

Create a tournament.

**Endpoint**: `POST /lol/tournament/v5/tournaments`

**Query Parameters**:
- `region` (string): Region code (default: `euw1`)

**Request Body**:
```json
{
  "name": "My Tournament",
  "providerId": 123
}
```

**Response**:
```json
{
  "tournamentId": 456
}
```

**Example**:
```bash
curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/tournaments?region=euw1" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Tournament", "providerId": 123}'
```

---

#### POST /codes

Generate tournament codes.

**Endpoint**: `POST /lol/tournament/v5/codes`

**Query Parameters**:
- `region` (string): Region code (default: `euw1`)

**Request Body**:
```json
{
  "tournamentId": 456,
  "count": 5,
  "teamSize": 5
}
```

**Response**:
```json
["TURNACODE1", "TURNACODE2", "TURNACODE3", "TURNACODE4", "TURNACODE5"]
```

**Example**:
```bash
curl -X POST "http://127.0.0.1:8080/lol/tournament/v5/codes?region=euw1" \
  -H "Content-Type: application/json" \
  -d '{"tournamentId": 456, "count": 5, "teamSize": 5}'
```

---

#### GET /codes/{tournamentCode}

Get tournament code details.

**Endpoint**: `GET /lol/tournament/v5/codes/{tournamentCode}`

**Path Parameters**:
- `tournamentCode` (string): The tournament code

**Query Parameters**:
- `region` (string): Region code (default: `euw1`)
- `force` (boolean): Force cache refresh (default: `false`)

**Response**:
```json
{
  "tournamentId": 456,
  "tournamentCode": "TURNACODE123",
  "spectators": "ALL",
  "lobbyName": "My Lobby"
}
```

**Caching**: 5 minutes TTL

**Example**:
```bash
# Normal request (uses cache)
curl "http://127.0.0.1:8080/lol/tournament/v5/codes/TURNACODE123?region=euw1"

# Force refresh (bypass cache)
curl "http://127.0.0.1:8080/lol/tournament/v5/codes/TURNACODE123?region=euw1&force=true"
```

---

#### PUT /codes/{tournamentCode}

Update tournament code settings.

**Endpoint**: `PUT /lol/tournament/v5/codes/{tournamentCode}`

**Path Parameters**:
- `tournamentCode` (string): The tournament code

**Query Parameters**:
- `region` (string): Region code (default: `euw1`)

**Request Body**:
```json
{
  "pickType": "TOURNAMENT_DRAFT",
  "mapType": "SUMMONERS_RIFT",
  "spectatorType": "ALL"
}
```

**Response**: Updated tournament code details

**Cache Invalidation**: Automatically invalidates cached code details

**Example**:
```bash
curl -X PUT "http://127.0.0.1:8080/lol/tournament/v5/codes/TURNACODE123?region=euw1" \
  -H "Content-Type: application/json" \
  -d '{"pickType": "TOURNAMENT_DRAFT", "mapType": "SUMMONERS_RIFT"}'
```

---

#### GET /lobby-events/by-code/{tournamentCode}

Get lobby events for a tournament code.

**Endpoint**: `GET /lol/tournament/v5/lobby-events/by-code/{tournamentCode}`

**Path Parameters**:
- `tournamentCode` (string): The tournament code

**Query Parameters**:
- `region` (string): Region code (default: `euw1`)
- `force` (boolean): Force cache refresh (default: `false`)

**Response**:
```json
{
  "lobbyEvents": [
    {
      "eventType": "PlayerJoined",
      "summonerName": "Player1",
      "timestamp": "2025-01-29T10:00:00Z"
    }
  ]
}
```

**Caching**: 30 seconds TTL (very dynamic data)

**Example**:
```bash
# Get current lobby events
curl "http://127.0.0.1:8080/lol/tournament/v5/lobby-events/by-code/TURNACODE123?region=euw1"

# Force refresh for real-time monitoring
curl "http://127.0.0.1:8080/lol/tournament/v5/lobby-events/by-code/TURNACODE123?region=euw1&force=true"
```

---

### Tournament Stub V5 Endpoints

The stub API has identical endpoints but operates in a sandbox environment:

- `POST /lol/tournament-stub/v5/providers`
- `POST /lol/tournament-stub/v5/tournaments`
- `POST /lol/tournament-stub/v5/codes`
- `GET /lol/tournament-stub/v5/codes/{tournamentCode}`
- `PUT /lol/tournament-stub/v5/codes/{tournamentCode}`
- `GET /lol/tournament-stub/v5/lobby-events/by-code/{tournamentCode}`

**Advantages**:
- No tournament API key required
- Safe for testing and development
- Operations don't affect production data

---

## Caching Behavior

### Cached Endpoints

| Endpoint | TTL | Force Refresh |
|----------|-----|---------------|
| GET /codes/{code} | 5 minutes | Yes |
| GET /lobby-events/by-code/{code} | 30 seconds | Yes |

**Cache Key Pattern**:
```
tournament:code:{region}:{tournamentCode}
tournament:lobby_events:{region}:{tournamentCode}
```

### Non-Cached Endpoints

The following endpoints are **NOT cached** (state-changing operations):
- POST /providers
- POST /tournaments
- POST /codes
- PUT /codes/{code}

**Note**: PUT endpoints invalidate related caches automatically.

---

## Configuration

### Environment Variables

```bash
# Cache TTLs (optional, defaults shown)
CACHE_TTL_TOURNAMENT_CODE=300          # 5 minutes
CACHE_TTL_TOURNAMENT_LOBBY_EVENTS=30   # 30 seconds

# Tournament API key (if you have access)
RIOT_API_KEY=your-tournament-api-key
# OR multiple keys for rotation
RIOT_API_KEYS=key1,key2,key3
```

---

## Error Handling

### Common Errors

#### 403 Forbidden

**Cause**: No tournament API access

**Solution**:
1. Apply for tournament access at [Riot Developer Portal](https://developer.riotgames.com/)
2. Use tournament-stub endpoints for testing

**Example Response**:
```json
{
  "detail": "Forbidden"
}
```

#### 400 Bad Request

**Cause**: Invalid request parameters

**Example Response**:
```json
{
  "detail": "Bad Request - Invalid region"
}
```

#### 404 Not Found

**Cause**: Tournament code doesn't exist

**Example Response**:
```json
{
  "detail": "Data not found"
}
```

#### 429 Rate Limit

**Cause**: Too many requests

**Headers**: `Retry-After: 10` (seconds to wait)

**Example Response**:
```json
{
  "detail": "Rate limit exceeded. Retry after 10 seconds"
}
```

---

## Usage Examples

### Complete Workflow

```bash
# 1. Register provider
PROVIDER_ID=$(curl -s -X POST "http://127.0.0.1:8080/lol/tournament/v5/providers?region=euw1" \
  -H "Content-Type: application/json" \
  -d '{"region": "euw1", "url": "https://example.com/callback"}' \
  | jq -r '.providerId')

echo "Provider ID: $PROVIDER_ID"

# 2. Create tournament
TOURNAMENT_ID=$(curl -s -X POST "http://127.0.0.1:8080/lol/tournament/v5/tournaments?region=euw1" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"My Tournament\", \"providerId\": $PROVIDER_ID}" \
  | jq -r '.tournamentId')

echo "Tournament ID: $TOURNAMENT_ID"

# 3. Generate codes
CODES=$(curl -s -X POST "http://127.0.0.1:8080/lol/tournament/v5/codes?region=euw1" \
  -H "Content-Type: application/json" \
  -d "{\"tournamentId\": $TOURNAMENT_ID, \"count\": 1, \"teamSize\": 5}" \
  | jq -r '.[0]')

echo "Tournament Code: $CODES"

# 4. Check code details
curl "http://127.0.0.1:8080/lol/tournament/v5/codes/$CODES?region=euw1"

# 5. Monitor lobby events (poll every 30 seconds)
watch -n 30 "curl -s 'http://127.0.0.1:8080/lol/tournament/v5/lobby-events/by-code/$CODES?region=euw1' | jq"
```

---

## Architecture Documents

For detailed implementation information, see:

- **[tournament-router-design.md](../architecture/tournament-router-design.md)** - Complete architecture design
- **[tournament-router-diagram.md](../architecture/tournament-router-diagram.md)** - Visual architecture diagrams
- **[tournament-router-implementation.md](../architecture/tournament-router-implementation.md)** - Step-by-step implementation guide

---

## API Reference

Official Riot Documentation:
- **Tournament V5**: https://developer.riotgames.com/apis#tournament-v5
- **Tournament Stub V5**: https://developer.riotgames.com/apis#tournament-stub-v5
- **Tournament Portal**: https://developer.riotgames.com/tournaments

---

## Support

For issues or questions:
1. Check architecture documents in `docs/architecture/`
2. Review test files in `tests/test_tournament.py`
3. Check logs: `make logs`

---

**Last Updated**: 2025-01-29
**Status**: Designed, Ready for Implementation
