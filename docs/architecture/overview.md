# Architecture Overview

This section provides a comprehensive overview of the LOLStonks API Gateway architecture, its components, and design principles.

## High-Level Architecture

### Simplified Request Flow

```mermaid
flowchart LR
    Client -->|HTTP Request| Gateway[FastAPI Gateway]
    Gateway -->|Cache Lookup| Redis[Redis Cache]
    Gateway -->|Rate-Limited Request| Riot[Riot API]
    Riot -->|Response| Gateway
    Gateway -->|Store Processed Data| Redis
```

### Detailed System Architecture

```mermaid
graph TB
    Client[Client Applications] --> Gateway[LOLStonks API Gateway]
    Gateway --> RateLimiter[Rate Limiter]
    Gateway --> Cache[Redis Cache]
    Gateway --> RiotAPI[Riot Games API]

    subgraph "Gateway Components"
        Gateway --> FastAPI[FastAPI Application]
        Gateway --> Routers[API Routers]
        Gateway --> Client[Riot Client]
        Gateway --> MatchTracking[Match Tracking]
    end

    subgraph "External Services"
        Redis[(Redis Server)]
        Riot[Riot Developer Portal]
    end

    Cache --> Redis
    MatchTracking --> Redis
    Client --> Riot
    Client -.-> Riot
```

## Core Components

### 1. FastAPI Application (`app.main`)

The main entry point that provides:
- **Async HTTP server** with automatic documentation
- **Request routing** to appropriate API endpoints
- **Middleware** for request processing and error handling
- **OpenAPI specification** generation

**Key Features:**
- Automatic request/response validation
- Interactive API documentation (Swagger UI, ReDoc)
- High performance async request handling
- Built-in support for CORS, middleware, and dependency injection

### 2. Riot Client (`app.riot.client`)

Specialized HTTP client for Riot API communication:

```python
class RiotClient:
    """
    HTTP client for Riot API with rate limiting and retry logic.

    Features:
    - Automatic rate limiting before requests
    - Retry on 429 responses with exponential backoff
    - Region-aware URL routing
    - Authentication header management
    """
```

**Responsibilities:**
- **Rate Limiting**: Token bucket algorithm for request throttling
- **Retry Logic**: Automatic retry with `Retry-After` header handling
- **Region Management**: Dynamic URL construction per region
- **Authentication**: Automatic API key injection

### 3. Rate Limiter (`app.riot.rate_limiter`)

Implements sophisticated rate limiting using the token bucket algorithm:

```python
class RateLimiter:
    """
    Token bucket rate limiter for Riot API compliance.

    - Configurable requests per second (RPS)
    - Burst capacity handling
    - Automatic token refill
    """
```

**Algorithm:**
- **Tokens**: Available request capacity
- **Refill Rate**: Tokens added per second
- **Burst Capacity**: Maximum token accumulation
- **Wait Strategy**: Queue requests when tokens exhausted

### 4. Redis Cache (`app.cache.redis_cache`)

High-performance caching layer:

```python
class RedisCache:
    """
    Redis-based caching with TTL support.

    - Automatic TTL management
    - Connection pooling
    - Error handling and fallbacks
    """
```

**Cache Strategy:**
- **TTL-based Expiration**: Different TTLs per data type
- **Intelligent Key Generation**: Consistent cache key patterns
- **Connection Pooling**: Efficient Redis connection management
- **Graceful Degradation**: Continue operation when cache unavailable

### 5. Match Tracking (`app.cache.tracking`)

Prevents duplicate match processing:

```python
class MatchTracker:
    """
    Match tracking service to prevent duplicate processing.

    - TTL cache for recent matches
    - Persistent set for all processed matches
    - Automatic cleanup of expired entries
    """
```

**Dual Storage Approach:**
- **TTL Cache**: Fast lookup for recent matches (1 week)
- **Persistent Set**: Complete record of all processed matches
- **Automatic Cleanup**: Removal of expired TTL entries

## API Router Architecture

### Router Organization

```mermaid
graph LR
    Gateway --> Routers
    Routers --> Summoner[Summoner Router]
    Routers --> Match[Match Router]
    Routers --> League[League Router]
    Routers --> Mastery[Champion Mastery Router]
    Routers --> Spectator[Spectator Router]
    Routers --> Account[Account Router]
    Routers --> Champion[Champion Router]
    Routers --> Clash[Clash Router]
    Routers --> Challenges[Challenges Router]
    Routers --> Platform[Platform Router]
```

### Router Responsibilities

Each router handles:
- **Path Parameter Validation**: Pydantic models for route parameters
- **Query Parameter Handling**: Optional parameters and defaults
- **Response Transformation**: Standardized response format
- **Error Handling**: Consistent error responses
- **Caching Integration**: Automatic cache integration per endpoint

### Example Router Structure

```python
# app/routers/summoner.py
router = APIRouter(prefix="/summoner", tags=["summoner"])

@router.get("/by-name/{summonerName}")
async def get_summoner_by_name(
    summonerName: str,
    region: str = Query(default="euw1"),
    riot_client: RiotClient = Depends(),
    cache: RedisCache = Depends()
) -> SummonerDto:
    """Get summoner by summoner name."""
    # Implementation with caching and error handling
```

## Data Flow Architecture

### Request Processing Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant G as Gateway
    participant RL as Rate Limiter
    participant Cache as Redis Cache
    participant RC as Riot Client
    participant R as Riot API

    C->>G: HTTP Request
    G->>RL: Check Rate Limit
    RL-->>G: Rate Limit OK
    G->>Cache: Check Cache
    alt Cache Hit
        Cache-->>G: Cached Response
        G-->>C: HTTP Response
    else Cache Miss
        G->>RC: Make API Request
        RC->>R: Riot API Call
        R-->>RC: API Response
        RC-->>G: Process Response
        G->>Cache: Store in Cache
        G-->>C: HTTP Response
    end
```

### Caching Strategy

**Cache Key Pattern:**
```
lolstonks:{endpoint}:{region}:{identifier}
```

**TTL Configuration:**
- **Summoner Data**: 1 hour (relatively stable)
- **Match Data**: 24 hours (historical data)
- **League Data**: 30 minutes (competitive data)
- **Champion Data**: 1 week (static data)

### Error Handling Flow

```mermaid
graph TD
    Request[Incoming Request] --> Validation[Request Validation]
    Validation --> RateCheck[Rate Limit Check]
    RateCheck --> CacheHit{Cache Hit?}

    CacheHit -->|Yes| CachedResponse[Return Cached Data]
    CacheHit -->|No| APIRequest[Make Riot API Request]

    APIRequest --> APISuccess{API Success?}
    APISuccess -->|Yes| StoreCache[Store in Cache]
    APISuccess -->|No| APIError{Error Type?}

    APIError -->|429| RetryWithBackoff[Retry with Exponential Backoff]
    APIError -->|404| NotFound[Return 404]
    APIError -->|Other| ServerError[Return 500]

    RetryWithBackoff --> APISuccess
    StoreCache --> SuccessResponse[Return Success Response]
    NotFound --> ErrorResponse[Return Error Response]
    ServerError --> ErrorResponse
```

## Configuration Architecture

### Configuration Hierarchy

1. **Environment Variables**: Primary configuration source
2. `.env` File: Local development configuration
3. **Defaults**: Built-in fallback values
4. **Runtime**: Dynamic configuration updates

### Configuration Management

```python
# app/config.py
class Settings(BaseSettings):
    """Configuration settings with environment variable support."""

    # Riot API Configuration
    riot_api_key: str
    riot_default_region: str = "euw1"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379

    class Config:
        env_file = ".env"
        case_sensitive = False
```

## Performance Architecture

### Performance Optimizations

1. **Async Processing**: Non-blocking I/O throughout the stack
2. **Connection Pooling**: Efficient database and HTTP connections
3. **Intelligent Caching**: Multi-layer caching strategy
4. **Rate Limiting**: Protects against API abuse and ensures compliance
5. **Batch Operations**: Support for concurrent requests

### Scalability Considerations

- **Horizontal Scaling**: Stateless design allows multiple instances
- **Redis Cluster**: Support for distributed caching
- **Load Balancing**: Compatible with standard load balancers
- **Monitoring**: Built-in health checks and metrics

## Security Architecture

### Security Layers

1. **API Key Management**: Secure storage and rotation of Riot API keys
2. **Input Validation**: Comprehensive request validation using Pydantic
3. **Rate Limiting**: Protection against abuse and DoS attacks
4. **Error Sanitization**: Prevents information leakage in error messages
5. **CORS Configuration**: Configurable cross-origin resource sharing

### Best Practices

- **Principle of Least Privilege**: Minimal required permissions
- **Defense in Depth**: Multiple security layers
- **Secure Defaults**: Secure configuration out of the box
- **Audit Logging**: Comprehensive request and error logging

## Monitoring and Observability

### Health Checks

```python
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "dependencies": {
            "redis": await check_redis_health(),
            "riot_api": await check_riot_api_health()
        }
    }
```

### Logging Strategy

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Request Tracking**: Unique request IDs for tracing
- **Performance Metrics**: Request timing and cache hit rates
- **Error Tracking**: Comprehensive error logging and alerting

## Future Architecture Considerations

### Planned Enhancements

1. **Metrics Collection**: Prometheus metrics integration
2. **Distributed Tracing**: OpenTelemetry support
3. **API Versioning**: Versioned API endpoints
4. **Webhook Support**: Real-time event notifications
5. **Admin Interface**: Management dashboard for operations

### Scalability Roadmap

- **Multi-Region Deployment**: Geographic distribution
- **Circuit Breakers**: Fault tolerance for external dependencies
- **Event Streaming**: Kafka/Redis Streams for real-time data
- **GraphQL Support**: Alternative API interface

## Design Principles

The LOLStonks API Gateway follows these design principles:

1. **Performance First**: Optimized for high throughput and low latency
2. **Developer Experience**: Clear APIs and comprehensive documentation
3. **Reliability**: Graceful degradation and error handling
4. **Observability**: Built-in monitoring and debugging capabilities
5. **Security**: Secure by design with defense in depth
6. **Scalability**: Designed to scale horizontally and vertically

## Production Deployment

### Deployment Architecture

For production deployments, the API Gateway should be run behind a reverse proxy with proper process management:

```mermaid
graph TB
    Internet[Internet] --> LB[Load Balancer/Nginx]
    LB --> Gateway1[API Gateway Instance 1]
    LB --> Gateway2[API Gateway Instance 2]
    LB --> GatewayN[API Gateway Instance N]

    Gateway1 --> Redis[Redis Cluster]
    Gateway2 --> Redis
    GatewayN --> Redis

    Gateway1 --> Riot[Riot API]
    Gateway2 --> Riot
    GatewayN --> Riot

    subgraph "Monitoring"
        Prometheus[Prometheus]
        Grafana[Grafana]
        Alerts[Alert Manager]
    end

    Gateway1 --> Prometheus
    Gateway2 --> Prometheus
    GatewayN --> Prometheus
    Prometheus --> Grafana
    Prometheus --> Alerts
```

### Production Requirements

1. **Process Management**: Use systemd, supervisor, or similar process manager
2. **Reverse Proxy**: Nginx or similar for SSL termination and load balancing
3. **Environment Variables**: Secure configuration management for API keys
4. **Monitoring**: Health checks, metrics collection, and alerting
5. **Logging**: Centralized log aggregation and analysis
6. **Security**: Firewall, rate limiting, and access controls

### Scaling Considerations

- **Horizontal Scaling**: Stateless design enables multiple instances
- **Redis Cluster**: Distributed caching for high availability
- **Database Connection Pooling**: Efficient resource utilization
- **Circuit Breakers**: Fault tolerance for external dependencies

This architecture provides a solid foundation for a production-ready API Gateway that can handle high traffic while maintaining reliability and performance.