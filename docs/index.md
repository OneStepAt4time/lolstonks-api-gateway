# LOLStonks API Gateway

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis-7.x-red.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://github.com/OneStepAt4time/lolstonks-api-gateway/workflows/CI/badge.svg)](https://github.com/OneStepAt4time/lolstonks-api-gateway/actions)
[![Documentation](https://img.shields.io/badge/Docs-Latest-brightgreen.svg)](https://onestepat4time.github.io/lolstonks-api-gateway/)

**Unified League of Legends API Gateway** engineered for high-performance applications with intelligent caching, automatic rate limiting, and comprehensive observability.

### What's New in v2.0.0
- **Comprehensive Data Source Architecture**: Support for Riot API, Data Dragon, and Community Dragon
- **Comprehensive API Coverage**: 76+ endpoints across all three data sources fully implemented
- **Enhanced Security**: Real-time security monitoring and status endpoints
- **Comprehensive Health Monitoring**: Detailed health checks for all data sources and components
- **Complete Input Validation**: Pydantic models for all endpoints and parameters

![LOLStonks logo](assets/logo.png)

## Enterprise Features

### Performance & Scalability
- **Sub-100ms Response Times**: Optimized for high-throughput applications
- **Async Architecture**: Built on FastAPI with full async/await support
- **Horizontal Scaling**: Stateless design enables multi-instance deployment
- **Connection Pooling**: Efficient resource management for high concurrency

### Reliability & Resilience
- **Intelligent Rate Limiting**: Token bucket algorithm ensures Riot API compliance
- **Automatic Retries**: Exponential backoff for 429 responses with configurable limits
- **Circuit Breaker Pattern**: Fault tolerance for external API dependencies
- **Graceful Degradation**: Continue operation during partial outages

### Intelligent Caching
- **Multi-Layer Caching**: Redis-based with strategic TTL configuration
- **High Cache Hit Rates**: Optimized caching strategy for frequently accessed data
- **Smart Invalidation**: Automatic cache updates based on data freshness
- **Memory Optimization**: Efficient cache key management and eviction policies

### Observability & Monitoring
- **Comprehensive Metrics**: Prometheus-compatible metrics for full stack monitoring
- **Structured Logging**: JSON-formatted logs with request tracing
- **Health Checks**: Multi-level health monitoring for all dependencies
- **Performance Analytics**: Real-time performance insights and alerting

### Developer Experience
- **Type-Safe API**: Full Pydantic model validation with comprehensive error handling
- **Interactive Documentation**: Auto-generated OpenAPI specs with Swagger UI and ReDoc
- **Multi-Region Support**: Complete coverage of all Riot API regions
- **UV Integration**: Modern Python package management with fast dependency resolution
- **Provider Abstraction**: Clean architecture for adding new data providers
- **Security Monitoring**: Built-in security status and monitoring endpoints

### Production Ready
- **Container-Native**: Docker support with optimized images
- **Security Hardened**: Input validation, CORS protection, and secure defaults
- **Configuration Management**: Environment-based configuration with validation
- **CI/CD Integration**: Automated testing, documentation generation, and deployment

## Quick Start

### System Requirements

- **Python 3.12+** with UV package manager
- **Redis 6.0+** for caching and session management
- **Riot Developer API key** from [developer.riotgames.com](https://developer.riotgames.com/)

### Installation with UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/OneStepAt4time/lolstonks-api-gateway.git
cd lolstonks-api-gateway

# Install dependencies with UV
uv pip install -e ".[docs]"

# Create environment configuration
cp .env.example .env
```

### Configuration

Edit your `.env` file with your settings:

```env
# Required: Riot API Configuration
RIOT_API_KEY=RGAPI-your-production-api-key
RIOT_DEFAULT_REGION=euw1

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO

# Optional: Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Optional: Performance Tuning
RIOT_RATE_LIMIT_PER_SECOND=20
RIOT_RATE_LIMIT_PER_2MIN=100
```

### Launch the Gateway

```bash
# Start with uvicorn (development)
uv run uvicorn app.main:app --reload

# Or with the provided script
uv run python -m app.main
```

### Verify Installation

```bash
# Health check endpoint
curl http://127.0.0.1:8080/health

# Expected response
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "2.0.0"
}

# Interactive documentation
# Open http://localhost:8080/docs in your browser
```

### Production Deployment

For production deployment, see our comprehensive [Deployment Guide](getting-started/deployment.md) which covers:
- Docker containerization
- Process management with systemd
- Nginx reverse proxy configuration
- SSL/TLS setup with Let's Encrypt
- Monitoring and alerting setup

## Documentation

- [Installation Guide](getting-started/installation.md) - Detailed setup instructions
- [Quick Start](getting-started/quick-start.md) - Basic usage examples
- [Configuration](getting-started/configuration.md) - Environment variables and settings
- [API Reference](api/overview.md) - Complete API documentation
- [Architecture](architecture/overview.md) - System design and components

## Quick Links

- **Interactive API Docs**: [Swagger UI](http://localhost:8080/docs) | [ReDoc](http://localhost:8080/redoc)
- **Riot Developer Portal**: [developer.riotgames.com](https://developer.riotgames.com/)
- **GitHub Repository**: [github.com/OneStepAt4time/lolstonks-api-gateway](https://github.com/OneStepAt4time/lolstonks-api-gateway)

## Example Usage

### Get Summoner by Name

```python
import httpx

response = httpx.get("http://localhost:8080/summoner/by-name/Faker?region=kr")
summoner = response.json()
print(f"Summoner: {summoner['name']} (Level: {summoner['summonerLevel']})")
```

### Get Current Match

```python
summoner_id = "summoner-id-here"
response = httpx.get(f"http://localhost:8080/spectator/active-game/{summoner_id}?region=kr")
game = response.json()
print(f"Game mode: {game['gameMode']}, Game time: {game['gameLength']}s")
```

### Get Match History

```python
puuid = "player-puuid-here"
response = httpx.get(f"http://localhost:8080/match/ids/by-puuid/{puuid}?region=euw1&count=5")
match_ids = response.json()
print(f"Recent matches: {match_ids}")
```

## Architecture Overview

The League of Legends API Gateway uses a **comprehensive data source architecture** to support multiple data sources:

### Core Components
- **FastAPI Application**: Modern async web framework with automatic documentation
- **Provider Registry**: Dynamic provider management and initialization
- **Redis Cache**: High-performance caching layer for API responses
- **Match Tracking**: Service to prevent duplicate match processing
- **Error Monitoring**: Real-time error tracking with alerting
- **Security Middleware**: Security monitoring and status reporting

### Supported Providers
1. **Riot Games Developer API** - Live game data, match history, summoner info
2. **Data Dragon CDN** - Static game data (champions, items, runes)
3. **Community Dragon** - Enhanced static data with additional assets

### Key Features
- **Provider Abstraction**: Clean interface for adding new data providers
- **Multi-Region Support**: Automatic routing based on region configuration
- **Intelligent Failover**: Graceful degradation when providers are unavailable
- **Comprehensive Monitoring**: Health checks and metrics for all components

## Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Development Status

- **Stable**: Core API Gateway functionality
- **Active Development**: Documentation system, monitoring, and additional features
- **Production Ready**: Suitable for production deployments with proper monitoring

---

**Built for the League of Legends developer community**
