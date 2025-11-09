![LOLStonks logo](./assets/logo.png)

# LOLStonks — API Gateway

**A production-ready FastAPI gateway for Riot Games League of Legends APIs** with intelligent caching, automatic rate limiting, and multi-provider support.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-7.x-red.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

[Features](#features) · [Quick Start](#quick-start) · [Documentation](https://onestepat4time.github.io/lolstonks-api-gateway/) · [API Docs](#api-documentation)

---

## Overview

LOLStonks API Gateway is a high-performance proxy for League of Legends APIs featuring:

- **Fast**: Sub-100ms cached responses with Redis backend
- **Multi-Provider**: Riot API + Data Dragon + Community Dragon
- **Production-Ready**: Rate limiting, retries, health checks, security monitoring
- **76+ Endpoints**: Complete coverage across all data sources
- **Smart Key Rotation**: Round-robin distribution across multiple API keys
- **Docker Ready**: One-command deployment with Docker Compose

---

## What's New in v2.0.0

- **Three-Provider Architecture**: Riot API, Data Dragon, and Community Dragon
- **Enhanced Security**: Real-time monitoring and status endpoints
- **Comprehensive Health Checks**: Multi-provider health monitoring
- **API Key Rotation**: Load distribution across multiple keys
- **Complete Documentation**: Architecture guides, API reference, and operations manual

[**View Full Changelog**](./CHANGELOG.md)

---

## Features

### Performance & Reliability
- **Async Architecture**: Built on FastAPI with full async/await support
- **Intelligent Caching**: Redis-backed with strategic TTL per endpoint type
- **Automatic Retries**: Exponential backoff for 429 rate limit responses
- **Horizontal Scaling**: Stateless design for multi-instance deployment

### Multi-Provider Support
- **Riot Games API**: Live game data, match history, summoner info, rankings
- **Data Dragon**: Official static data (champions, items, runes)
- **Community Dragon**: Enhanced assets, TFT data, high-quality images

### Production Features
- **Rate Limiting**: Token bucket algorithm with Riot API compliance
- **API Key Rotation**: Round-robin across multiple keys
- **Security Monitoring**: Real-time security status and alerts
- **Health Checks**: Comprehensive provider and dependency monitoring
- **Input Validation**: Complete Pydantic model validation

[**See All Features →**](https://onestepat4time.github.io/lolstonks-api-gateway/)

---

## Quick Start

### Prerequisites

- Python 3.12+
- Redis 6.0+
- Riot Developer API key ([Get one here](https://developer.riotgames.com/))

### Docker Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/OneStepAt4time/lolstonks-api-gateway.git
cd lolstonks-api-gateway

# Configure environment
cp .env.example .env
# Edit .env and set your RIOT_API_KEY

# Start with Docker Compose
docker-compose up -d

# Verify it's running
curl http://127.0.0.1:8080/health
```

### Local Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure and run
cp .env.example .env
# Edit .env and set your RIOT_API_KEY
python -m app.main
```

**📖 Detailed Setup**: See [Installation Guide](https://onestepat4time.github.io/lolstonks-api-gateway/getting-started/installation/)

---

## Configuration

Minimal configuration in `.env`:

```env
# Required
RIOT_API_KEY=RGAPI-your-key-here

# Optional - Multiple keys for rotation
RIOT_API_KEYS=RGAPI-key1,RGAPI-key2,RGAPI-key3

# Optional - Provider selection
ENABLED_PROVIDERS=riot_api,data_dragon,community_dragon

# Optional - Server settings
HOST=127.0.0.1
PORT=8080
```

**⚙️ Full Configuration**: See [Configuration Guide](https://onestepat4time.github.io/lolstonks-api-gateway/getting-started/configuration/)

---

## Usage Examples

### Riot API - Live Data

```bash
# Get summoner by name
curl "http://127.0.0.1:8080/lol/summoner/v4/summoners/by-name/Faker?region=kr"

# Get match history
curl "http://127.0.0.1:8080/lol/match/v5/matches/by-puuid/{PUUID}/ids?region=euw1&count=5"

# Check active game
curl "http://127.0.0.1:8080/lol/spectator/v5/active-games/by-summoner/{ID}?region=kr"
```

### Data Dragon - Static Data

```bash
# Get all champions
curl "http://127.0.0.1:8080/ddragon/champions"

# Get specific champion
curl "http://127.0.0.1:8080/ddragon/champions/Ahri"

# Get items
curl "http://127.0.0.1:8080/ddragon/items"
```

### Community Dragon - Enhanced Assets

```bash
# Get champion skins
curl "http://127.0.0.1:8080/cdragon/skins"

# Get TFT data
curl "http://127.0.0.1:8080/cdragon/tft/champions"
```

**📚 More Examples**: See [Usage Guide](https://onestepat4time.github.io/lolstonks-api-gateway/getting-started/quick-start/)

---

## API Documentation

Once running, access interactive documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

---

## Documentation

Comprehensive documentation available at: **[onestepat4time.github.io/lolstonks-api-gateway](https://onestepat4time.github.io/lolstonks-api-gateway/)**

### Quick Links

- [**Installation Guide**](https://onestepat4time.github.io/lolstonks-api-gateway/getting-started/installation/) - Detailed setup instructions
- [**Configuration**](https://onestepat4time.github.io/lolstonks-api-gateway/getting-started/configuration/) - All configuration options
- [**API Reference**](https://onestepat4time.github.io/lolstonks-api-gateway/api/overview/) - Complete endpoint documentation
- [**Architecture**](https://onestepat4time.github.io/lolstonks-api-gateway/architecture/overview/) - System design and components
- [**Troubleshooting**](https://onestepat4time.github.io/lolstonks-api-gateway/operations/troubleshooting/) - Common issues and solutions

### For Developers

- [**Contributing Guide**](https://onestepat4time.github.io/lolstonks-api-gateway/development/contributing/)
- [**Changelog**](./CHANGELOG.md) - Version history
- [**Versioning Guide**](https://onestepat4time.github.io/lolstonks-api-gateway/development/versioning/)
- [**Release Process**](https://onestepat4time.github.io/lolstonks-api-gateway/development/releases/)

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│      FastAPI Application            │
│  ┌───────────────────────────────┐  │
│  │   Provider Registry           │  │
│  ├───────────┬──────────┬────────┤  │
│  │ Riot API  │ D-Dragon │ C-Dragon│ │
│  └───────────┴──────────┴────────┘  │
│  ┌───────────────────────────────┐  │
│  │   Rate Limiter & Retries      │  │
│  └───────────────────────────────┘  │
└─────────────┬───────────────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌─────────┐      ┌──────────────┐
│  Redis  │      │  Riot APIs   │
│  Cache  │      │ D-Dragon CDN │
└─────────┘      │ C-Dragon CDN │
                 └──────────────┘
```

**[Architecture Details →](https://onestepat4time.github.io/lolstonks-api-gateway/architecture/overview/)**

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://onestepat4time.github.io/lolstonks-api-gateway/development/contributing/) for:

- Development environment setup
- Code style guidelines
- Testing requirements
- Pull request process

---

## Support This Project

If you find LOLStonks API Gateway useful:

- **Star this repository**
- **Share** with others
- **Report issues** or contribute code
- **[Buy me a coffee](https://buymeacoffee.com/onestepat4time)**

---

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## Contact

- **Project**: [github.com/OneStepAt4time/lolstonks-api-gateway](https://github.com/OneStepAt4time/lolstonks-api-gateway)
- **Documentation**: [onestepat4time.github.io/lolstonks-api-gateway](https://onestepat4time.github.io/lolstonks-api-gateway/)
- **Issues**: [GitHub Issues](https://github.com/OneStepAt4time/lolstonks-api-gateway/issues)
- **Author**: OneStepAt4time

---

**Built for the League of Legends developer community**
