# Quick Start

Get up and running with the LOLStonks API Gateway in minutes.

## Prerequisites

- ✅ Installation completed (see [Installation Guide](installation.md))
- ✅ Redis server running
- ✅ Riot API key configured in `.env`

## Start the Gateway

### Option 1: Development Mode

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Start the server
python -m app.main
```

### Option 2: Production Mode

```bash
# Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Using gunicorn (production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

### Option 3: Docker

```bash
# Using docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f api-gateway
```

## Verify Installation

### Health Check

```bash
curl http://localhost:8080/health
# Expected response: {"status":"ok"}
```

### Interactive Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Basic Usage Examples

### 1. Get Summoner Information

```bash
# Get summoner by name
curl "http://localhost:8080/summoner/by-name/Faker?region=kr"

# Response example
{
  "id": "KqOw12p4b3bLp5b6p7",
  "accountId": "3b3Lp5b6p7KqOw12p4b",
  "puuid": "p7KqOw12p4b3bLp5b6p7",
  "name": "Faker",
  "profileIconId": 3188,
  "revisionDate": 1678901234567,
  "summonerLevel": 523
}
```

### 2. Get Current Match

```bash
# Get active game for a summoner
curl "http://localhost:8080/spectator/active-game/KqOw12p4b3bLp5b6p7?region=kr"

# Response contains game information
{
  "gameId": 1234567890,
  "gameMode": "CLASSIC",
  "gameQueueConfigId": 420,
  "participants": [...],
  "gameLength": 542,
  "gameStartTime": 1678901234567
}
```

### 3. Get Match History

```bash
# Get recent match IDs
curl "http://localhost:8080/match/ids/by-puuid/p7KqOw12p4b3bLp5b6p7?region=kr&count=5"

# Response: Array of match IDs
["KR_1234567890", "KR_1234567891", "KR_1234567892", "KR_1234567893", "KR_1234567894"]
```

### 4. Get League Information

```bash
# Get challenger league
curl "http://localhost:8080/league/challenger/RANKED_SOLO_5x5?region=kr"

# Get master league
curl "http://localhost:8080/league/master/RANKED_SOLO_5x5?region=kr"
```

### 5. Get Champion Mastery

```bash
# Get top masteries for summoner
curl "http://localhost:8080/champion-mastery/top/KqOw12p4b3bLp5b6p7?region=kr&count=5"

# Get mastery for specific champion
curl "http://localhost:8080/champion-mastery/by-champion/KqOw12p4b3bLp5b6p7/157?region=kr"
```

## Python Client Examples

### Using httpx (Recommended)

```python
import httpx
import asyncio

async def get_summoner_data():
    """Get basic summoner information"""
    async with httpx.AsyncClient() as client:
        # Get summoner by name
        response = await client.get(
            "http://localhost:8080/summoner/by-name/Faker",
            params={"region": "kr"}
        )
        summoner = response.json()
        print(f"Summoner: {summoner['name']} (Level: {summoner['summonerLevel']})")

        # Get current match
        response = await client.get(
            f"http://localhost:8080/spectator/active-game/{summoner['id']}",
            params={"region": "kr"}
        )

        if response.status_code == 200:
            game = response.json()
            print(f"Currently in game: {game['gameMode']}")
        else:
            print("Not currently in a game")

# Run the example
asyncio.run(get_summoner_data())
```

### Using requests (Synchronous)

```python
import requests

def get_league_data():
    """Get challenger league information"""
    response = requests.get(
        "http://localhost:8080/league/challenger/RANKED_SOLO_5x5",
        params={"region": "euw1"}
    )

    if response.status_code == 200:
        league = response.json()
        print(f"League: {league['name']}")
        print(f"Tier: {league['tier']}")
        print(f"Number of players: {len(league['entries'])}")

        # Show top 3 players
        for i, entry in enumerate(league['entries'][:3], 1):
            print(f"{i}. {entry['summonerName']} - {entry['leaguePoints']} LP")

get_league_data()
```

## Common Operations

### Batch Operations

```python
import asyncio
import httpx

async def get_multiple_summoners(names, region="kr"):
    """Get data for multiple summoners concurrently"""
    async with httpx.AsyncClient() as client:
        tasks = []
        for name in names:
            task = client.get(
                "http://localhost:8080/summoner/by-name/" + name,
                params={"region": region}
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses if r.status_code == 200]

# Usage
summoners = asyncio.run(get_multiple_summoners(["Faker", "ShowMaker", "Canyon"]))
for summoner in summoners:
    print(f"{summoner['name']}: Level {summoner['summonerLevel']}")
```

### Error Handling

```python
import httpx

async def safe_api_call(endpoint, params=None):
    """Safe API call with error handling"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8080{endpoint}",
                params=params
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("Resource not found")
        elif e.response.status_code == 429:
            print("Rate limit exceeded - please wait")
        elif e.response.status_code == 503:
            print("Service temporarily unavailable")
        else:
            print(f"HTTP error: {e.response.status_code}")
        return None

    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return None

# Usage
data = await safe_api_call("/summoner/by-name/Faker", {"region": "kr"})
if data:
    print(f"Successfully retrieved: {data['name']}")
```

## Monitoring the Gateway

### Health Checks

```bash
# Basic health check
curl http://localhost:8080/health

# Check specific endpoints
curl http://localhost:8080/docs  # Should load Swagger UI
curl http://localhost:8080/redoc  # Should load ReDoc
```

### Log Monitoring

```bash
# View application logs
python -m app.main  # Logs will appear in console

# Or use docker logs if running with Docker
docker-compose logs -f api-gateway
```

## Performance Tips

1. **Use Appropriate Cache TTLs**: Configure cache durations based on data volatility
2. **Batch Requests**: Use concurrent requests for multiple API calls
3. **Region Selection**: Use the correct region parameter for optimal performance
4. **Error Handling**: Implement proper retry logic and error handling
5. **Rate Limit Awareness**: Be mindful of Riot's rate limits

## Next Steps

- Read the [Configuration Guide](configuration.md) for advanced settings
- Explore the complete [API Reference](../api/overview.md)
- Set up [development tools](../development/testing.md)
- Review the [Architecture Overview](../architecture/overview.md)

## Troubleshooting

If you encounter issues:

1. **Connection Refused**: Check if the gateway is running on the correct port
2. **401 Unauthorized**: Verify your Riot API key in the `.env` file
3. **404 Not Found**: Check the endpoint path and parameters
4. **429 Rate Limited**: The gateway handles this automatically, but you may need to wait
5. **503 Service Unavailable**: Riot API may be temporarily down

For more help, see the [Development Documentation](../development/testing.md#troubleshooting).
