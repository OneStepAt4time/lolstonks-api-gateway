# Data Flow Architecture

> **Detailed request processing** and data flow through the lolstonks-api-gateway system

---

## Overview

This document describes how data flows through the gateway, from incoming client requests to cached responses. Understanding these flows is critical for optimizing performance, debugging issues, and maintaining the system.

---

## Complete Request Flow

### End-to-End Request Processing

```mermaid
flowchart TD
    start([Client Request<br/>HTTP GET/POST]) -->|1. TCP Connection| server[Uvicorn Server<br/>127.0.0.1:8080]
    server -->|2. ASGI Protocol| fastapi[FastAPI Application<br/>Request Parsing]
    fastapi -->|3. Middleware Chain| cors[CORS Middleware<br/>Origin Check]
    cors --> logging[Logging Middleware<br/>Request ID Generation]
    logging --> errorhandler[Error Handler<br/>Global Exception Catching]
    errorhandler -->|4. Route Matching| router{Router<br/>Match<br/>Endpoint?}

    router -->|No Match| notfound[404 Not Found]
    notfound --> errorresponse([Error Response])

    router -->|Match Found| validate[Pydantic Validation<br/>Path/Query Parameters]
    validate -->|Invalid| validationerror[422 Validation Error]
    validationerror --> errorresponse

    validate -->|Valid| ratelimit{Rate Limit<br/>Check}
    ratelimit -->|Exceeded| toomany[429 Too Many Requests]
    toomany --> errorresponse

    ratelimit -->|OK| cachecheck{Cache<br/>Check}
    cachecheck -->|"Hit (<1ms)"| cachehit[Retrieve from Redis]
    cachehit -->|Deserialize| cachedresponse[Cached Data]
    cachedresponse --> format[Format Response<br/>Add Headers]

    cachecheck -->|"Miss or ?force=true"| provider[Provider Registry<br/>Select Provider]
    provider -->|Static Data| dataDragon[Data Dragon Provider]
    provider -->|Live Data| riotProvider[Riot API Provider]
    provider -->|Community Data| communityProvider[Community Dragon Provider]

    dataDragon -->|"HTTP GET (20-100ms)"| dragonAPI[Data Dragon CDN]
    riotProvider -->|"HTTP GET + API Key (50-200ms)"| riotAPI[Riot API]
    communityProvider -->|"HTTP GET (20-100ms)"| communityAPI[Community Dragon CDN]

    dragonAPI -->|Response| processData[Process Response<br/>Validate & Transform]
    riotAPI -->|Response| processData
    communityAPI -->|Response| processData

    processData -->|Success| updatecache[Update Redis Cache<br/>Set TTL]
    processData -->|API Error| apierror[Handle API Error<br/>Retry or Fallback]

    apierror -->|Retry Success| updatecache
    apierror -->|Retry Failed| errorresponse

    updatecache -.->|"Async (<1ms)"| redis[(Redis Cache)]
    updatecache --> format

    format -->|6. Response Middleware| addheaders[Add Headers<br/>Cache-Control, X-Response-Time]
    addheaders -->|7. Log Response| logresponse[Log Response Time<br/>& Cache Status]
    logresponse -->|8. Send| success([HTTP Response<br/>200 OK + JSON])

    classDef gateway fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef provider fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef cache fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef external fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    classDef decision fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef error fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#000

    class server,fastapi,cors,logging,errorhandler,validate,format,addheaders,logresponse gateway
    class dataDragon,riotProvider,communityProvider provider
    class cachehit,cachedresponse,updatecache,redis cache
    class dragonAPI,riotAPI,communityAPI external
    class router,ratelimit,cachecheck decision
    class notfound,validationerror,toomany,apierror error
```

### Performance Breakdown

| Step | Component | Time (Typical) | Notes |
|------|-----------|----------------|-------|
| 1 | TCP Connection | `<1ms` | Local network, very fast |
| 2 | Request Parsing | `<1ms` | FastAPI/Pydantic validation |
| 3 | Middleware Chain | `<1ms` | CORS, logging, error handler |
| 4 | Route Matching | `<1ms` | FastAPI router lookup |
| 5 | Parameter Validation | `<1ms` | Pydantic model validation |
| 6 | Rate Limit Check | `<1ms` | Redis counter check |
| **7a** | **Cache Hit** | **<1ms** | **Redis GET operation** |
| **7b** | **Cache Miss** | **50-200ms** | **External API call** |
| 8 | Response Formatting | `<1ms` | JSON serialization |
| 9 | Response Headers | `<1ms` | Header injection |
| 10 | Response Logging | `<1ms` | Async log write |

**Total Time**:
- **Cache Hit**: `<10ms` (typically `5-8ms`)
- **Cache Miss**: `60-220ms` (depends on external API latency)

---

## Cache Flow Detailed

### Cache Hit Path (Fast Path)

```mermaid
sequenceDiagram
    participant C as Client
    participant G as Gateway
    participant R as Redis Cache
    participant L as Logger

    C->>G: GET /lol/summoner/v4/by-name/euw1/Player
    activate G

    Note over G: Generate cache key<br/>riot:summoner:euw1:player_hash

    G->>R: GET cache key
    activate R
    R-->>G: Cached data (JSON)
    deactivate R

    Note over G: Deserialize JSON<br/>Validate expiry

    G->>L: Log cache hit (async)

    G-->>C: 200 OK + Cached Data<br/>X-Cache-Status: HIT<br/>X-Response-Time: 7ms
    deactivate G

    Note over C,G: Total time: ~7ms
```

**Cache Key Format**:
```
{provider}:{endpoint}:{region}:{params_hash}
```

**Example Keys**:
- `riot:summoner:euw1:d4f2a1b9` (summoner by name)
- `dragon:champion:14.1.1:en_us` (champion data)
- `riot:match:europe:euw1_123456` (match details)

**Cache Headers in Response**:
```http
X-Cache-Status: HIT
X-Cache-TTL: 285
X-Response-Time: 7
Cache-Control: public, max-age=300
```

### Cache Miss Path (Slow Path)

```mermaid
sequenceDiagram
    participant C as Client
    participant G as Gateway
    participant RC as Redis Cache
    participant P as Provider
    participant E as External API
    participant L as Logger

    C->>G: GET /lol/summoner/v4/by-name/euw1/NewPlayer
    activate G

    Note over G: Generate cache key<br/>riot:summoner:euw1:newplayer_hash

    G->>RC: GET cache key
    activate RC
    RC-->>G: NULL (not found)
    deactivate RC

    Note over G: Select Provider<br/>(Riot API for summoner)

    G->>P: Fetch summoner data
    activate P

    P->>E: HTTPS GET + X-Riot-Token header
    activate E
    Note over E: Process request<br/>Check rate limits<br/>Query database
    E-->>P: 200 OK + JSON response
    deactivate E

    Note over P: Validate response<br/>Transform if needed

    P-->>G: Processed data
    deactivate P

    Note over G: Serialize for cache

    G->>RC: SET cache key (TTL=300s)
    activate RC
    RC-->>G: OK
    deactivate RC

    G->>L: Log cache miss + latency (async)

    G-->>C: 200 OK + Fresh Data<br/>X-Cache-Status: MISS<br/>X-Response-Time: 157ms
    deactivate G

    Note over C,G: Total time: ~157ms
```

**Cache Update Logic**:
```python
# Pseudo-code for cache update
async def cache_or_fetch(key: str, ttl: int, fetch_fn):
    # Try cache first
    cached = await redis.get(key)
    if cached and not force_refresh:
        return json.loads(cached)

    # Cache miss - fetch from provider
    data = await fetch_fn()

    # Update cache (async, don't block response)
    await redis.set(key, json.dumps(data), ex=ttl)

    return data
```

### Force Refresh Path

```mermaid
flowchart LR
    request([Request with<br/>?force=true]) -->|Skip cache| provider[Provider Fetch]
    provider -->|Fetch fresh| external[External API]
    external --> update[Update Cache]
    update -.->|Overwrite| cache[(Redis Cache)]
    update --> response([Fresh Response])

    style request fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style provider fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style external fill:#ffebee,stroke:#c62828,stroke-width:2px
    style cache fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

**Use Cases**:
- Debugging stale cache data
- Manual cache invalidation
- Testing external API changes
- Ensuring real-time data accuracy

**Example**:
```bash
# Normal request (may return cached data)
curl "http://127.0.0.1:8080/lol/summoner/v4/by-name/euw1/Player"

# Force refresh (always fetches fresh data)
curl "http://127.0.0.1:8080/lol/summoner/v4/by-name/euw1/Player?force=true"
```

---

## Cache TTL Strategy

### TTL Configuration by Data Type

| Data Type | TTL | Rationale | Example Endpoints |
|-----------|-----|-----------|-------------------|
| **Live Game Data** | 30 seconds | Changes frequently during active game | `/spectator/active-game` |
| **Player Profiles** | 5 minutes | Updates occasionally (rank, level) | `/summoner/by-name`, `/summoner/by-puuid` |
| **Match History** | 10 minutes | Recent matches may update, older stable | `/match/by-puuid` (list) |
| **Match Details** | 30 minutes | Match details don't change after completion | `/match/by-match-id` (details) |
| **Ranked Ladders** | 5 minutes | Ladder updates frequently | `/league/challenger`, `/league/entries` |
| **Champion Mastery** | 10 minutes | Updates after games | `/champion-mastery/by-puuid` |
| **Static Data** | 1 hour | Changes only with patches | `/champion/all`, `/item/all` |
| **Version Info** | 6 hours | Updates with new patches (~2 weeks) | `/version/latest` |

### Dynamic TTL Adjustment

```mermaid
flowchart TD
    fetch[Fetch Data] --> analyze{Analyze<br/>Data Type}

    analyze -->|Live/Active| short[Short TTL<br/>30s - 5min]
    analyze -->|Historical| medium[Medium TTL<br/>10min - 30min]
    analyze -->|Static| long[Long TTL<br/>1h - 6h]

    short --> cache[(Redis Cache)]
    medium --> cache
    long --> cache

    cache -->|TTL Expired| evict[Auto-Evict]
    evict -.->|Next Request| fetch

    style analyze fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style cache fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

**Configuration**:
```python
# app/core/cache_config.py
CACHE_TTL = {
    "summoner": 300,          # 5 minutes
    "match_list": 600,        # 10 minutes
    "match_details": 1800,    # 30 minutes
    "league": 300,            # 5 minutes
    "champion_data": 3600,    # 1 hour
    "spectator": 30,          # 30 seconds
}
```

---

## Error Handling Flow

### Error Propagation and Recovery

```mermaid
flowchart TD
    request([Incoming Request]) --> process[Process Request]

    process --> success{Success?}
    success -->|Yes| response([200 OK Response])

    success -->|No| classify{Classify<br/>Error Type}

    classify -->|Validation Error| validate_error[422 Unprocessable Entity<br/>Invalid parameters]
    classify -->|Not Found| not_found[404 Not Found<br/>Endpoint/resource missing]
    classify -->|Rate Limit| rate_error[429 Too Many Requests<br/>Rate limit exceeded]
    classify -->|External API Error| api_error{API<br/>Error<br/>Code?}
    classify -->|Server Error| server_error[500 Internal Server Error<br/>Unexpected error]

    api_error -->|404| resource_missing[404 Not Found<br/>Resource doesn't exist in API]
    api_error -->|429| external_rate[502 Bad Gateway<br/>External API rate limited]
    api_error -->|500/502/503| retry{Retry<br/>Count<br/>< 3?}
    api_error -->|403| forbidden[403 Forbidden<br/>Invalid API key or permissions]

    retry -->|Yes| backoff[Exponential Backoff<br/>Wait 1s, 2s, 4s...]
    backoff -.->|Retry| process
    retry -->|No| give_up[503 Service Unavailable<br/>External API down]

    validate_error --> log[Log Error Details]
    not_found --> log
    rate_error --> log
    resource_missing --> log
    external_rate --> log
    forbidden --> log
    server_error --> log
    give_up --> log

    log --> error_response([Error Response<br/>JSON + Error Details])

    classDef success fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef client_error fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef server_error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    classDef decision fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000

    class response success
    class validate_error,not_found,rate_error,resource_missing client_error
    class server_error,external_rate,forbidden,give_up server_error
    class success,classify,api_error,retry decision
```

### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "SUMMONER_NOT_FOUND",
    "message": "Summoner 'PlayerName' not found in region 'euw1'",
    "details": {
      "region": "euw1",
      "summoner_name": "PlayerName",
      "provider": "riot_api"
    },
    "request_id": "req_abc123xyz",
    "timestamp": "2025-01-24T12:00:00Z"
  }
}
```

### HTTP Status Code Mapping

| Status Code | Error Type | When It Occurs | Retry? |
|-------------|------------|----------------|--------|
| **400** | Bad Request | Malformed request syntax | No |
| **404** | Not Found | Resource doesn't exist | No |
| **422** | Unprocessable Entity | Validation error (invalid parameters) | No |
| **429** | Too Many Requests | Gateway rate limit exceeded | Yes (with backoff) |
| **403** | Forbidden | Invalid API key or permissions | No |
| **500** | Internal Server Error | Unexpected gateway error | Maybe (check logs) |
| **502** | Bad Gateway | External API error (4xx/5xx) | Yes (auto-retry) |
| **503** | Service Unavailable | External API down after retries | Yes (manual retry later) |
| **504** | Gateway Timeout | External API timeout | Yes (with backoff) |

### Retry Strategy

```mermaid
sequenceDiagram
    participant G as Gateway
    participant P as Provider
    participant E as External API

    G->>P: Request data
    P->>E: API Call (Attempt 1)
    E-->>P: 503 Service Unavailable

    Note over P: Wait 1 second<br/>(2^0 = 1s)

    P->>E: API Call (Attempt 2)
    E-->>P: 502 Bad Gateway

    Note over P: Wait 2 seconds<br/>(2^1 = 2s)

    P->>E: API Call (Attempt 3)
    E-->>P: 500 Internal Error

    Note over P: Wait 4 seconds<br/>(2^2 = 4s)

    P->>E: API Call (Attempt 4 - Final)
    E-->>P: 503 Service Unavailable

    P-->>G: Error: Max retries exceeded
    G-->>G: Return 503 to client
```

**Retry Configuration**:
```python
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1.0  # seconds
RETRY_BACKOFF_MAX = 10.0  # seconds
RETRYABLE_STATUS_CODES = [500, 502, 503, 504]
```

---

## Provider Selection Flow

### Dynamic Provider Routing

```mermaid
flowchart TD
    request([API Request]) --> parse[Parse Endpoint]
    parse --> registry[Provider Registry]

    registry --> detect{Data<br/>Type?}

    detect -->|Summoner, Match, League| live[Live Data]
    detect -->|Champion, Item, Spell| static[Static Data]
    detect -->|Augments, Missions| community[Community Data]

    live --> region_check{Region<br/>Valid?}
    region_check -->|Yes| riot[Riot API Provider<br/>Live game data]
    region_check -->|No| error[400 Bad Request<br/>Invalid region]

    static --> version_check{Version<br/>Specified?}
    version_check -->|Yes| dragon[Data Dragon Provider<br/>Specific version]
    version_check -->|No| latest[Data Dragon Provider<br/>Latest version]

    community --> community_provider[Community Dragon Provider<br/>Enhanced static data]

    riot -->|With API Key| riot_api[Riot API<br/>HTTPS + Auth]
    dragon --> dragon_cdn[Data Dragon CDN<br/>HTTPS]
    latest --> dragon_cdn
    community_provider --> community_cdn[Community Dragon CDN<br/>HTTPS]

    riot_api --> response([Provider Response])
    dragon_cdn --> response
    community_cdn --> response
    error --> error_response([Error Response])

    classDef decision fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef provider fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef external fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000

    class detect,region_check,version_check decision
    class riot,dragon,latest,community_provider provider
    class riot_api,dragon_cdn,community_cdn external
```

### Provider Selection Logic

**Decision Table**:

| Endpoint Pattern | Data Type | Provider | Authentication | Cache TTL |
|------------------|-----------|----------|----------------|-----------|
| `/summoner/**` | Live | Riot API | API Key Required | 5 min |
| `/match/**` | Live | Riot API | API Key Required | 10-30 min |
| `/league/**` | Live | Riot API | API Key Required | 5 min |
| `/spectator/**` | Live | Riot API | API Key Required | 30 sec |
| `/champion-mastery/**` | Live | Riot API | API Key Required | 10 min |
| `/champion/**` | Static | Data Dragon | Public | 1 hour |
| `/item/**` | Static | Data Dragon | Public | 1 hour |
| `/spell/**` | Static | Data Dragon | Public | 1 hour |
| `/augments/**` | Static | Community Dragon | Public | 1 hour |
| `/missions/**` | Community | Community Dragon | Public | 1 hour |

**Code Example**:
```python
async def select_provider(endpoint: str, region: str) -> BaseProvider:
    if endpoint.startswith("/lol/summoner"):
        return RiotAPIProvider(region=region, api_key=settings.RIOT_API_KEY)
    elif endpoint.startswith("/lol/static/champion"):
        return DataDragonProvider(version="latest", locale="en_US")
    elif endpoint.startswith("/lol/community"):
        return CommunityDragonProvider(version="latest")
    else:
        raise ValueError(f"No provider for endpoint: {endpoint}")
```

---

## Regional Routing

### Region Mapping and Validation

```mermaid
flowchart TD
    request([Request with Region]) --> validate{Region<br/>Valid?}

    validate -->|Invalid| error[400 Bad Request<br/>Invalid region code]
    error --> error_response([Error Response])

    validate -->|Valid| map[Map to API Region]

    map --> platform{Platform<br/>Region?}

    platform -->|Americas| americas[americas.api.riotgames.com<br/>na1, br1, la1, la2]
    platform -->|Europe| europe[europe.api.riotgames.com<br/>euw1, eun1, tr1, ru]
    platform -->|Asia| asia[asia.api.riotgames.com<br/>kr, jp1, oc1, ph2, sg2, th2, tw2, vn2]
    platform -->|SEA| sea[sea.api.riotgames.com<br/>ph2, sg2, th2, tw2, vn2]

    americas --> endpoint[Platform-Specific Endpoint]
    europe --> endpoint
    asia --> endpoint
    sea --> endpoint

    endpoint -->|Add Region Header| headers[X-Region: {region}]
    headers --> call[Make API Call]
    call --> response([API Response])

    classDef decision fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef provider fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000

    class validate,platform decision
    class americas,europe,asia,sea,endpoint,headers,call provider
    class error error
```

### Region Configuration

**Platform Routing Table**:

| Platform | Regions | API Domain |
|----------|---------|------------|
| **Americas** | `na1`, `br1`, `la1`, `la2` | `americas.api.riotgames.com` |
| **Europe** | `euw1`, `eun1`, `tr1`, `ru` | `europe.api.riotgames.com` |
| **Asia** | `kr`, `jp1`, `oc1` | `asia.api.riotgames.com` |
| **SEA** | `ph2`, `sg2`, `th2`, `tw2`, `vn2` | `sea.api.riotgames.com` |

**Regional Aliases**:
```python
REGION_ALIASES = {
    "euw": "euw1",
    "eune": "eun1",
    "na": "na1",
    "br": "br1",
    "lan": "la1",
    "las": "la2",
    "oce": "oc1",
}
```

---

## Performance Optimization

### Request Coalescing

**Problem**: Multiple simultaneous requests for the same data cause redundant API calls.

**Solution**: Request coalescing (deduplication).

```mermaid
sequenceDiagram
    participant C1 as Client 1
    participant C2 as Client 2
    participant C3 as Client 3
    participant G as Gateway
    participant E as External API

    Note over C1,C3: All request same summoner<br/>at same time

    C1->>G: GET /summoner/by-name/euw1/Player
    C2->>G: GET /summoner/by-name/euw1/Player
    C3->>G: GET /summoner/by-name/euw1/Player

    Note over G: Detect duplicate in-flight request<br/>Coalesce into single API call

    G->>E: Single API call
    E-->>G: Response

    Note over G: Fan out response to all waiters

    G-->>C1: Response (from shared call)
    G-->>C2: Response (from shared call)
    G-->>C3: Response (from shared call)

    Note over C1,C3: Saved 2 API calls!
```

### Compression

**Response Compression**: Reduce bandwidth for large responses.

```http
# Request
GET /lol/champion/all
Accept-Encoding: gzip, deflate

# Response
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: gzip
Content-Length: 15234 (original: 68451)
```

**Compression Savings**:
- Champion data: `~78% reduction` (68KB → 15KB)
- Match details: `~65% reduction` (120KB → 42KB)
- Match lists: `~70% reduction` (50KB → 15KB)

### Connection Pooling

```mermaid
flowchart LR
    subgraph Gateway["Gateway Application"]
        router1[Router 1]
        router2[Router 2]
        router3[Router 3]
    end

    subgraph Pool["HTTP Connection Pool"]
        conn1[Connection 1]
        conn2[Connection 2]
        conn3[Connection 3]
        conn4[Connection 4]
    end

    subgraph External["External APIs"]
        riot[Riot API]
        dragon[Data Dragon]
    end

    router1 -.->|Reuse| Pool
    router2 -.->|Reuse| Pool
    router3 -.->|Reuse| Pool

    Pool -->|Keep-Alive| External

    style Pool fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

**Configuration**:
```python
# httpx client configuration
httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30.0
    )
)
```

**Benefits**:
- Eliminates TCP handshake overhead (`~50ms`)
- Reuses SSL/TLS sessions
- Reduces server load

---

## Cross-References

### Related Documentation

- **[System Overview](./system-overview.md)** - High-level architecture
- **[Routing Architecture](./routing.md)** - API endpoint organization
- **[Caching Strategy](caching.md)** - Detailed cache configuration
- **[Provider Documentation](providers.md)** - Provider implementations
- **[Rate Limiting](../rate-limiting/)** - Rate limit configuration

### Implementation Files

- `app/main.py` - FastAPI application and middleware
- `app/routers/` - Router implementations
- `app/providers/` - Provider implementations
- `app/core/cache.py` - Cache logic
- `app/core/rate_limiter.py` - Rate limiting
- `app/middleware/` - Custom middleware

---

## Monitoring Checklist

Use this checklist to monitor data flow health:

- [ ] **Cache Hit Rate**: Should be `>70%` in steady state
- [ ] **Response Time P95**: Should be `<50ms` for cache hits, `<300ms` for cache misses
- [ ] **Error Rate**: Should be `<1%` overall
- [ ] **Rate Limit Errors**: Should be `<0.1%` (indicates proper cache usage)
- [ ] **External API Latency**: Monitor for degradation
- [ ] **Redis Connection**: Check for connection pool exhaustion
- [ ] **Request Coalescing**: Verify deduplication is working

---

**Last Updated**: 2025-01-24

**Next Steps**:
1. Review [Routing Architecture](./routing.md) for endpoint organization
2. Explore [Caching Strategy](caching.md) for detailed TTL configuration
3. Check [Provider Documentation](providers.md) for implementation details
