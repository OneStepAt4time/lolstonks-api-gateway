# LOLStonks API Gateway

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis-7.x-red.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A high-performance Riot Games API Gateway with intelligent caching, rate limiting, and match tracking capabilities.

![LOLStonks logo](../.github/logo.png)

## ✨ Features

- **🚀 High Performance**: Built with FastAPI for optimal speed and async operations
- **🔄 Intelligent Rate Limiting**: Automatic Riot API rate limit handling with token bucket algorithm
- **💾 Smart Caching**: Redis-based caching with configurable TTL for performance optimization
- **📊 Match Tracking**: Real-time match tracking and notifications to prevent duplicate processing
- **📡 Comprehensive API**: Full Riot Games API coverage with stable endpoint structure
- **🔍 Auto Documentation**: Interactive API documentation with Swagger UI and ReDoc
- **🌍 Multi-Region Support**: Support for all Riot API regions (EUW1, KR, NA1, BR1, etc.)
- **🔄 Automatic Retries**: Built-in retry logic with exponential backoff for 429 responses

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Redis server
- Riot Developer API key ([developer.riotgames.com](https://developer.riotgames.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/OneStepAt4time/lolstonks-api-gateway.git
cd lolstonks-api-gateway

# Install with pip
pip install -e ".[docs]"

# Or with uv (recommended)
uv install --extra docs
```

### Configuration

Copy the environment file and set your Riot API key:

```bash
cp .env.example .env
# Edit .env and set RIOT_API_KEY
```

### Running the Gateway

```bash
# Start the server
uvicorn app.main:app --reload

# Or use the provided script
python -m app.main
```

### Health Check

```bash
curl http://127.0.0.1:8080/health
# Response: {"status":"ok"}
```

The API is now available at `http://localhost:8080` with interactive docs at `/docs`.

## 📖 Documentation

- [Installation Guide](getting-started/installation.md) - Detailed setup instructions
- [Quick Start](getting-started/quick-start.md) - Basic usage examples
- [Configuration](getting-started/configuration.md) - Environment variables and settings
- [API Reference](api/overview.md) - Complete API documentation
- [Architecture](architecture/overview.md) - System design and components

## 🔗 Quick Links

- **Interactive API Docs**: [Swagger UI](http://localhost:8000/docs) | [ReDoc](http://localhost:8000/redoc)
- **Riot Developer Portal**: [developer.riotgames.com](https://developer.riotgames.com/)
- **GitHub Repository**: [github.com/OneStepAt4time/lolstonks-api-gateway](https://github.com/OneStepAt4time/lolstonks-api-gateway)

## 📊 Example Usage

### Get Summoner by Name

```python
import httpx

response = httpx.get("http://localhost:8000/summoner/by-name/Faker?region=kr")
summoner = response.json()
print(f"Summoner: {summoner['name']} (Level: {summoner['summonerLevel']})")
```

### Get Current Match

```python
summoner_id = "summoner-id-here"
response = httpx.get(f"http://localhost:8000/spectator/active-game/{summoner_id}?region=kr")
game = response.json()
print(f"Game mode: {game['gameMode']}, Game time: {game['gameLength']}s")
```

### Get Match History

```python
puuid = "player-puuid-here"
response = httpx.get(f"http://localhost:8000/match/ids/by-puuid/{puuid}?region=euw1&count=5")
match_ids = response.json()
print(f"Recent matches: {match_ids}")
```

## 🏗️ Architecture Overview

The LOLStonks API Gateway consists of several key components:

- **FastAPI Application**: Modern async web framework with automatic documentation
- **Riot Client**: HTTP client with rate limiting and retry logic
- **Redis Cache**: High-performance caching layer for API responses
- **Match Tracking**: Service to prevent duplicate match processing
- **Router Layer**: Organized API endpoints mirroring Riot's API structure

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔧 Development Status

- **Stable**: Core API Gateway functionality
- **Active Development**: Documentation system, monitoring, and additional features
- **Production Ready**: Suitable for production deployments with proper monitoring

---

**Built with ❤️ for the League of Legends developer community**