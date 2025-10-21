# LOLStonks API Gateway

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-7.x-red.svg)](https://redis.io/)

An intelligent proxy gateway for the Riot Games League of Legends API with smart caching, rate limiting, and persistent match tracking.

## Features

- 🚀 **FastAPI-based REST API** - High-performance async proxy for Riot API
- ⚡ **Smart Caching** - Redis-based TTL caching (summoners: 1h, matches: 24h, leagues: 1h)
- 🎯 **Dual-Layer Match Tracking** - TTL cache + permanent SET for processed matches
- 🛡️ **Rate Limiting** - Token bucket algorithm (20 req/s, 100 req/2min)
- 🌍 **Multi-Region Support** - EUW1, KR, NA1, BR1, and all Riot regions
- 🔄 **Automatic Retry** - Handles 429 responses with exponential backoff
- 📊 **Complete API Coverage** - All 10 Riot LoL APIs (31 endpoints)
- 🐳 **Docker Ready** - Docker Compose orchestration with Redis

## Quick Start

### Prerequisites

- Python 3.12+
- [UV package manager](https://github.com/astral-sh/uv)
- Docker & Docker Compose (for containerized deployment)
- Riot API Key ([Get one here](https://developer.riotgames.com/))

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/OneStepAt4time/lolstonks-api-gateway.git
   cd lolstonks-api-gateway
   ```

2. Set up environment
   ```bash
   cp .env.example .env
   # Edit .env and add your RIOT_API_KEY
   ```

3. Start with Docker (recommended)
   ```bash
   docker-compose up -d
   ```

4. Verify it's running
   ```bash
   curl http://127.0.0.1:8080/health
   # Expected: {"status":"ok"}
   ```

## Configuration

Edit `.env` file:

```env
# Required
RIOT_API_KEY=RGAPI-your-key-here

# Optional (defaults shown)
RIOT_DEFAULT_REGION=euw1
REDIS_HOST=redis
REDIS_PORT=6379
HOST=127.0.0.1
PORT=8080
LOG_LEVEL=INFO
```

## Usage Examples

### Get Summoner by Name
```bash
curl "http://127.0.0.1:8080/lol/summoner/v4/summoners/by-name/Faker?region=kr"
```

### Fetch Challenger Players
```bash
curl "http://127.0.0.1:8080/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?region=euw1"
```

### Get Match History
```bash
PUUID="player-puuid-here"
curl "http://127.0.0.1:8080/lol/match/v5/matches/by-puuid/$PUUID/ids?region=euw1&count=10"
```

## Documentation

- Full API documentation available at `http://127.0.0.1:8080/docs` when running
- See [Riot API Docs](https://developer.riotgames.com/apis) for endpoint details

## Related Projects

- [lolstonks](https://github.com/OneStepAt4time/lolstonks) - Main application that consumes this gateway

## License

MIT License

---

Built with ❤️ using FastAPI and Redis
