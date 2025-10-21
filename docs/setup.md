# Setup & Quick Start

This document walks through running the gateway locally and with Docker.

Prerequisites

 - Python 3.12+
 - Docker & Docker Compose (recommended for local testing)
 - Riot API Key: [Riot Developer](https://developer.riotgames.com/)

Local (Docker) run

1. Copy environment file:

```powershell
cp .env.example .env
# Edit .env and add RIOT_API_KEY
```

1. Start services:

```powershell
docker-compose up -d
```

1. Health check:

```powershell
curl http://127.0.0.1:8080/health
```

Run with a virtual environment

1. Create and activate venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

1. Install (project uses `uv`/`pyproject.toml` — if you prefer pip, use `pip install -r requirements.txt`):

```powershell
pip install -U pip
pip install -r requirements.txt
```

1. Run:

```powershell
python -m app.main
```

Notes

- For production deployments, provide real environment variables (don't rely on `.env`).
- Ensure Redis is available and reachable via `REDIS_HOST`/`REDIS_PORT`.
