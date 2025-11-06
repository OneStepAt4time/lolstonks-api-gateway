![LOLStonks logo](./assets/logo.png)

# LOLStonks — API Gateway
An intelligent FastAPI-based gateway & proxy for Riot Games League of Legends APIs with smart caching, rate limiting, and match tracking.

Features · Quick Start · Usage · Configuration · Contributing · [Documentation](./docs/README.md)

---

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-7.x-red.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Quick Start](#quick-start)
   - [Prerequisites](#prerequisites)
   - [Local (Docker) Run](#local-docker-run)
   - [Run Locally (venv)](#run-locally-venv)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Architecture & Design](#architecture--design)
- [Development](#development)
- [Contributing](#contributing)
- [Support Development](#support-development)
- [License](#license)
- [Contact](#contact)

---

## About the Project

LOLStonks API Gateway is a focused, high-performance proxy for Riot's League of Legends HTTP APIs. It provides:

- A FastAPI front-end exposing to Riot endpoints with a stable surface for clients.
- Smart caching via Redis to reduce request volume and accelerate responses.
- Rate limiting using a token-bucket style algorithm to protect your Riot API key.
- Match tracking to persist processed match IDs and prevent double-processing.
- Automatic retry/backoff on 429s and useful metrics for observability.
- Multi-provider architecture with support for Data Dragon, Community Dragon, and Riot API providers.
- Comprehensive security documentation and API key rotation support.

This gateway is intended for use by any application interacting with Riot Games' League of Legends APIs. It can run standalone or alongside other services that need a robust, cache-aware Riot API proxy.

---

## Features

- FastAPI-based async proxy with modern Python 3.12+
- Multi-provider system: Data Dragon, Community Dragon, and Riot APIs
- Smart Redis caching (summoners, matches, leagues) with configurable TTL
- Dual-layer match tracking: TTL cache + Redis SET for permanent storage of processed match IDs
- Token bucket rate limiting (default: 20 req/s, 100 req/2min) with automatic 429 handling
- Automatic retry with exponential backoff on rate limit responses
- **API key rotation**: Round-robin load distribution across multiple keys
- Multi-region support (EUW1, KR, NA1, BR1, and others)
- Docker Compose ready for easy deployment
- Comprehensive router coverage for all Riot LoL endpoints
- Security-focused design with input validation and error monitoring

---

## API Endpoints

The gateway provides comprehensive coverage of Riot Games API for League of Legends through multiple providers:

### Core Riot API Endpoints
- **Account**: Manage player accounts and Riot IDs.
- **Challenges**: Track player progress in in-game challenges.
- **Champion**: Access champion-related data, including rotations.
- **Champion Mastery**: Retrieve champion mastery scores and levels.
- **Clash**: Get information about Clash tournaments, teams, and players.
- **League**: Fetch data on ranked leagues, divisions, and standings.
- **Match**: Access detailed match information, timelines, and histories.
- **Spectator**: View live game data and featured matches.
- **Summoner**: Look up summoner profiles by name, PUUID, or ID.
- **Platform**: Check status of League of Legends platform.

### Data Dragon Community Endpoints
- **Champions**: Static champion data with skins and information.
- **Items**: Complete item database with metadata.
- **TFT Items/Characters**: Teamfight Tactics game data.
- **TFT Traits/Augments**: TFT specific game elements.

For detailed endpoint documentation, refer to the interactive API docs at `/docs` or the [provider documentation](./docs/api/providers.md).

---

## Quick Start

### Prerequisites

1. Python 3.12+
1. Docker & Docker Compose (recommended)
1. A Riot Developer API key ([developer.riotgames.com](https://developer.riotgames.com/))
1. Optional: `uv` package manager (recommended)

### Local (Docker) Run

1. Copy `.env.example` to `.env` and set your Riot key:

```bash
cp .env.example .env
# Edit .env and set RIOT_API_KEY
```

2. Start services with Docker Compose:

```bash
docker-compose up -d
```

3. Health check:

```bash
curl http://127.0.0.1:8080/health
# Expect: {"status":"ok"}
```

4. Open interactive API docs at: http://127.0.0.1:8080/docs

### Run Locally (venv)

1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
pip install -U pip
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and run:

```bash
cp .env.example .env
# set RIOT_API_KEY in .env
python -m app.main
```

---

## Configuration

Copy `.env.example` to `.env` and edit values as needed:

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

# API Key Rotation (optional)
RIOT_API_KEYS=RGAPI-key1,RGAPI-key2,RGAPI-key3
```

Notes:

- The gateway reads environment variables from `.env` via the `app.config` module.
- For production, prefer providing real environment variables instead of file-backed `.env`.
- Multiple API keys can be provided for load distribution via `RIOT_API_KEYS`.

---

## Usage Examples

Get a summoner by name (region query param available):

```bash
curl "http://127.0.0.1:8080/lol/summoner/v4/summoners/by-name/Faker?region=kr"
```

Fetch Challenger players:

```bash
curl "http://127.0.0.1:8080/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?region=euw1"
```

Get champion data from Data Dragon:

```bash
curl "http://127.0.0.1:8080/cdragon/champions/v4/champions?region=na1"
```

Get match IDs by PUUID:

```bash
PUUID="player-puuid-here"
curl "http://127.0.0.1:8080/lol/match/v5/matches/by-puuid/$PUUID/ids?region=euw1&count=10"
```

---

## Architecture & Design

High-level components:

- `app.main`: FastAPI application entrypoint
- `app.config`: Environment configuration and defaults management
- `app.providers.*`: Multi-provider system (Riot API, Data Dragon, Community Dragon)
- `app.riot.client`: Request orchestration, retries, and rate limiting logic
- `app.cache.redis_cache`: TTL-based caching with Redis backend
- `app.cache.tracking`: Permanent match tracking set + processed cache
- `app.routers.*`: Individual API routers organized by provider
- `app.middleware.*`: Error monitoring and security middleware

Design principles:

- **Provider abstraction**: Common interface for different data sources
- **Cache-first strategy**: Reduce API calls and improve response times
- **Graceful degradation**: Fallback between providers when available
- **Security by design**: Input validation, rate limiting, and error monitoring
- **Observable**: Comprehensive logging and metrics for production monitoring

---

## Development

Recommended workflow:

1. Create a feature branch:

```bash
git checkout -b feat/your-feature
```

2. Run the app locally (see Quick Start)
3. Add tests under `tests/` and run them:

```bash
make test-quick    # Fast tests
make test-full     # Comprehensive tests with coverage
```

4. Code quality checks:

```bash
make lint          # Run ruff, mypy, and other checks
make format        # Format code with ruff
```

---

## Contributing

Contributions are welcome! Please read our [Contributing Guide](./docs/development/contributing.md) for details on:

1. Setting up your development environment
1. Code style guidelines and best practices
1. Testing requirements and coverage standards
1. Pull request process and review criteria

---

## Support Development

If you find LOLStonks API Gateway useful, consider supporting its development:

- ⭐ **Star this repository** on GitHub
- 💬 **Share** with others who might find it useful
- 🐛 **Report issues** or contribute code fixes
- ☕ **[Buy me a coffee](https://buymeacoffee.com/onestepat4time)** to support ongoing development

Your support helps cover API costs, server expenses, and dedicated development time. See [SUPPORT.md](./SUPPORT.md) for more ways to help.

---

## License

This project is licensed under the MIT License — see the `LICENSE` file for details.

---

## Contact

Project: [OneStepAt4time/lolstonks-api-gateway](https://github.com/OneStepAt4time/lolstonks-api-gateway)
Author: OneStepAt4time

For questions, contributions, or support, open an issue or PR on GitHub.
