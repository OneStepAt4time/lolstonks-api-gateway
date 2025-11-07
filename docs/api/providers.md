# API Providers

The LOLStonks API Gateway uses a provider abstraction pattern to support multiple data sources. Each provider implements a common interface and can be enabled/disabled independently.

## Supported Providers

### 1. Riot Games Developer API

**Provider ID**: `riot_api`

**Description**: Official Riot Games API providing live game data, match history, player statistics, and more.

**Coverage**: 40+ endpoints including:
- Account API (Riot ID lookups)
- Summoner API (profiles and masteries)
- Match API (match history and details)
- League API (ranked standings)
- Champion API (rotations and info)
- Spectator API (live games)
- Clash API (tournament data)
- Challenges API (player challenges)

**Rate Limits**:
- 20 requests per second
- 100 requests per 2 minutes

**Regions**: All official Riot regions supported

### 2. Data Dragon CDN

**Provider ID**: `data_dragon`

**Description**: Official Riot CDN for static game data including champions, items, runes, and summoner spells.

**Coverage**: 14 endpoints including:
- Champion data and splash arts
- Item information and icons
- Rune configurations
- Summoner spell details
- Profile icons
- Language strings and translations
- Version history

**Features**:
- Multi-language support
- Version-specific data access
- CDN-optimized assets

**Cache TTL**: 7 days (static data changes infrequently)

### 3. Community Dragon

**Provider ID**: `community_dragon`

**Description**: Community-maintained enhanced data source providing additional assets and detailed information not available in official APIs.

**Coverage**: 22+ endpoints including:
- Enhanced champion data with voice lines
- Comprehensive skin and chroma information
- TFT (Teamfight Tactics) data
- High-quality assets and images
- Lore and background information
- Mission and event data

**Features**:
- Additional asset types not in official APIs
- Higher resolution images
- Community-enhanced metadata
- TFT comprehensive support

## Provider Configuration

### Enable/Disable Providers

Use the `ENABLED_PROVIDERS` environment variable:

```bash
# Enable all providers (default)
ENABLED_PROVIDERS=riot_api,data_dragon,community_dragon

# Enable only Riot API
ENABLED_PROVIDERS=riot_api

# Disable a specific provider
ENABLED_PROVIDERS=riot_api,data_dragon  # Community Dragon disabled
```

### Provider-Specific Settings

#### Data Dragon Configuration
```bash
# Version settings
DATA_DRAGON_VERSION=latest    # or specific version like "13.24.1"
DATA_DRAGON_LOCALE=en_US      # Language for data strings
```

#### Community Dragon Configuration
```bash
# Version settings
COMMUNITY_DRAGON_VERSION=latest
COMMUNITY_DRAGON_LOCALE=en_US
```

## Provider Architecture

### Base Provider Interface

All providers implement the `BaseProvider` class with these methods:

```python
class BaseProvider:
    async def initialize(self) -> None:
        """Initialize provider connections and resources."""

    async def health_check(self) -> HealthStatus:
        """Check provider health and availability."""

    async def close(self) -> None:
        """Clean up provider resources."""

    def get_endpoints(self) -> List[Endpoint]:
        """Return list of available endpoints."""
```

### Provider Registry

The `ProviderRegistry` manages all active providers:

```python
# Get all active providers
providers = registry.get_all_providers()

# Get specific provider
riot_provider = registry.get_provider("riot_api")

# Check if provider is enabled
if registry.is_enabled("riot_api"):
    # Use Riot API
```

## Adding New Providers

To add a new data provider:

1. **Create Provider Class**:
   ```python
   # app/providers/your_provider.py
   from app.providers.base import BaseProvider

   class YourProvider(BaseProvider):
       def __init__(self, config: ProviderConfig):
           # Initialize provider

       async def fetch_data(self, endpoint: str, **kwargs):
           # Implement data fetching
   ```

2. **Register Provider**:
   ```python
   # app/providers/registry.py
   registry.register("your_provider", YourProvider)
   ```

3. **Add Configuration**:
   ```python
   # app/config.py
   @field_validator('enabled_providers')
   def validate_provider(cls, v):
       # Add validation for your provider
   ```

4. **Create Routers**:
   ```python
   # app/routers/your_provider.py
   from fastapi import APIRouter
   router = APIRouter(prefix="/your-provider", tags=["your-provider"])
   ```

5. **Update Environment Variables**:
   ```bash
   # .env.example
   YOUR_PROVIDER_API_KEY=your-key
   YOUR_PROVIDER_BASE_URL=https://api.your-provider.com
   ```

## Provider Health Monitoring

Each provider reports detailed health metrics:

- **Status**: Healthy, Degraded, or Unhealthy
- **Response Time**: Average response time in milliseconds
- **Error Rate**: Percentage of failed requests
- **Consecutive Failures**: Count of recent failures
- **Last Error**: Details of the most recent error

Access health status:
```bash
# Overall health
curl http://localhost:8080/health

# Detailed provider health
curl http://localhost:8080/health/providers

# Specific provider health
curl http://localhost:8080/health/providers?provider=riot_api
```

## Provider Fallback

When a provider becomes unhealthy:

1. **Immediate Detection**: Health checks detect failures
2. **Error Monitoring**: Errors are tracked and logged
3. **Graceful Degradation**: Requests fail fast with appropriate error messages
4. **Recovery**: Automatic retry when provider becomes healthy again

## Rate Limiting by Provider

Each provider can have independent rate limiting:

```python
# Riot API: 20 req/s, 100 req/2min
rate_limiter = TokenBucket(rate=20, capacity=100)

# Data Dragon: No rate limit (CDN)
# Community Dragon: 50 req/s (respectful usage)
```

## Best Practices

1. **Provider Selection**: Choose the right provider for your data needs
   - Live data → Riot API
   - Static game data → Data Dragon
   - Enhanced assets → Community Dragon

2. **Error Handling**: Always check provider health before making requests
3. **Caching**: Respect provider-specific cache TTL recommendations
4. **Rate Limits**: Monitor and respect provider rate limits
5. **Fallback**: Implement client-side fallback for critical data

## Troubleshooting

### Provider Not Available
```bash
# Check if provider is enabled
curl http://localhost:8080/health/providers

# Check environment variables
echo $ENABLED_PROVIDERS
```

### Provider Errors
```bash
# Check error details
curl http://localhost:8080/health/detailed

# View error logs
docker-compose logs gateway | grep ERROR
```

### Slow Provider Response
```bash
# Check response times
curl http://localhost:8080/health/providers

# Monitor performance
curl http://localhost:8080/metrics | grep provider_response_time
```
