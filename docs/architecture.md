# Architecture

LOLStonks API Gateway is an intelligent proxy for the Riot Games League of Legends APIs, implementing a multi-provider architecture with comprehensive caching, rate limiting, and observability.

## Technology Stack

- **Python 3.12+**: Core application language
- **FastAPI**: Async web framework for high-performance APIs
- **Uvicorn**: ASGI server implementation
- **Redis**: In-memory caching and data structure store
- **Docker**: Container platform for deployment
- **UV**: Fast Python package installer and resolver

## Core Components

The system consists of four primary layers:

1. **API Gateway Layer**: FastAPI application serving 76+ endpoints across three data providers
2. **Provider Layer**: Riot Games API, Data Dragon CDN, Community Dragon API
3. **Caching Layer**: Redis-backed intelligent caching with strategic TTL configuration
4. **Rate Limiting Layer**: Token bucket algorithm ensuring Riot API compliance

## Application Structure

```
app/
├── config.py              # Configuration management
├── main.py                # FastAPI application entry point
├── cache/                 # Redis cache and match tracking
├── riot/                  # Riot API client and rate limiter
├── providers/             # Multi-provider abstraction layer
├── routers/               # API endpoint definitions
└── models/                # Pydantic validation models
```

## Deployment

The application is containerized using Docker with Docker Compose orchestration. Production deployments require Redis 6.0+ and a valid Riot Developer API key.

## Detailed Documentation

For comprehensive architecture documentation, see:

- [Architecture Overview](architecture/overview.md) - Complete system design and component details
- [Caching Architecture](architecture/caching.md) - Cache strategy and implementation
- [Rate Limiting](architecture/rate-limiting.md) - Rate limiter design and configuration
- [Data Models](architecture/models.md) - Pydantic validation models
- [Implementation Details](architecture/implementation-details.md) - Actual code implementation and libraries

## Design Principles

- **Performance First**: Sub-100ms cached responses
- **Decoupling**: Client isolation from Riot API rate limits
- **Resilience**: Automatic retries and graceful degradation
- **Observability**: Comprehensive health checks and monitoring
