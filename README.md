![LOLStonks logo](./assets/logo.png)

# LOLStonks — API Gateway
An intelligent FastAPI-based gateway & proxy for the Riot Games League of Legends APIs with smart caching, rate limiting, and match tracking.

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

- A FastAPI front-end exposing the Riot endpoints with a stable surface for clients.
- Smart caching via Redis to reduce request volume and accelerate responses.
- Rate limiting using a token-bucket style algorithm to protect your Riot API key.
- Match tracking to persist processed match IDs and prevent double-processing.
- Automatic retry/backoff on 429s and useful metrics for observability.

This gateway is intended for use by any application interacting with Riot Games' League of Legends APIs. It can run standalone or alongside other services that need a robust, cache-aware Riot API proxy.

---

## Features

- FastAPI-based async proxy
- Redis TTL caching (summoners, matches, leagues) with sensible defaults
- Dual-layer match tracking: TTL cache + Redis SET for permanent storage of processed match IDs
- Rate limiting: token bucket defaults (20 req/s, 100 req/2min)
- Automatic retry on 429 responses with exponential backoff
- **API key rotation**: Round-robin rotation across multiple keys for load distribution
- Multi-region support (EUW1, KR, NA1, BR1, and others)
- Docker Compose ready for easy deployment
- Comprehensive router coverage for Riot LoL endpoints

---

## API Endpoints

The gateway provides comprehensive coverage of the Riot Games API for League of Legends. The available endpoints are organized into the following routers:

- **Account**: Manage player accounts and Riot IDs.
- **Challenges**: Track player progress in in-game challenges.
- **Champion**: Access champion-related data, including rotations.
- **Champion Mastery**: Retrieve champion mastery scores and levels.
- **Clash**: Get information about Clash tournaments, teams, and players.
- **League**: Fetch data on ranked leagues, divisions, and standings.
- **Match**: Access detailed match information, timelines, and histories.
- **Spectator**: View live game data and featured matches.
- **Summoner**: Look up summoner profiles by name, PUUID, or ID.
- **Platform**: Check the status of the League of Legends platform.

For a detailed list of all available endpoints, please refer to the interactive API documentation at `/docs`.

---

## Quick Start

### Prerequisites

1. Python 3.12+
1. Docker & Docker Compose (recommended)
1. A Riot Developer API key ([developer.riotgames.com](https://developer.riotgames.com/))
1. Optional: `uv` package manager (recommended in project)

### Local (Docker) Run

1. Copy `.env` and set your Riot key:

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

1. Create virtualenv and install:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
pip install -U pip
pip install -r requirements.txt
```

2. Copy `.env` and run:

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
```

Notes:

- The gateway reads environment variables from `.env` via the `app.config` module.
- For production, prefer providing real environment variables instead of file-backed `.env`.

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

Get match IDs by PUUID:

```bash
PUUID="player-puuid-here"
curl "http://127.0.0.1:8080/lol/match/v5/matches/by-puuid/$PUUID/ids?region=euw1&count=10"
```

---

## Architecture & Design

High-level components:

- `app.main`: FastAPI app entrypoint
- `app.config`: Environment and defaults loader
- `app.riot.client`: Request orchestration, retries, and rate limiting logic
- `app.cache.redis_cache`: TTL caching primitives
- `app.cache.tracking`: Permanent match tracking set + TTL processed cache
- `app.routers.*`: Individual API routers that map to Riot endpoints

Design goals:

- Keep client callers decoupled from Riot's rate and cache concerns
- Let Redis provide the fast-path for repeated lookups
- Provide transparent retry behavior for 429s so clients don't need to re-implement it

---

## Development

Recommended workflow:

1. Create a feature branch:

```bash
git checkout -b feat/your-feature
```

1. Run the app locally (see Quick Start)
1. Add tests under `tests/` and run them via your preferred test runner

Linting & type checking:

- Project follows modern Python typing; run mypy/ruff/flake8 if configured in your environment

---

## Contributing

Contributions are welcome! Please read the [Contributing Guide](docs/development/contributing.md) for details on:

1. Setting up your development environment
1. Code style guidelines and best practices
1. Testing requirements
1. Pull request process

---

## Support This Project

If you find LOLStonks API Gateway useful, consider supporting its development:

- ⭐ **Star this repository** on GitHub
- 💬 **Share** with others who might find it useful
- 🐛 **Report issues** or contribute code
- ☕ **[Buy me a coffee](https://buymeacoffee.com/onestepat4time)** to support ongoing development

Your support helps cover API costs, server expenses, and dedicated development time. See [SUPPORT.md](SUPPORT.md) for more ways to help.

---

## Troubleshooting

- 401 from Riot: check `RIOT_API_KEY` is valid and not restricted.
- 429 frequently: verify the gateway is not misconfigured and your key isn't being used elsewhere; consider increasing rate limits if allowed by Riot or caching more responses.
- Redis connection errors: check `REDIS_HOST`/`REDIS_PORT` and that Redis is running.

If you hit problems you can't resolve locally, open an issue with logs and reproduction steps.

---

## Roadmap (ideas)

- Metrics (Prometheus) and tracing (OpenTelemetry)
- Admin endpoints to inspect/flush caches
- Pluggable storage backends for match tracking

---

## License

This project is licensed under the MIT License — see the `LICENSE` file for details.

---

## Contact

Project: [OneStepAt4time/lolstonks-api-gateway](https://github.com/OneStepAt4time/lolstonks-api-gateway)
Author: OneStepAt4time

If you want to contribute, open an issue or PR on GitHub.
