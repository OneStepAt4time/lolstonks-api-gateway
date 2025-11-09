# Configuration

This guide covers all configuration options available for the LOLStonks API Gateway.

## Environment Variables

The gateway uses environment variables for configuration. You can set these in a `.env` file or as system environment variables.

### Required Variables

```env
# Option 1: Single API key (backward compatible)
RIOT_API_KEY=RGAPI-your-api-key-here

# Option 2: Multiple API keys for rotation (recommended for production)
# Comma-separated list. Gateway will rotate through keys using round-robin.
# This helps distribute load and avoid hitting rate limits on a single key.
# If RIOT_API_KEYS is set, it takes priority over RIOT_API_KEY.
RIOT_API_KEYS=RGAPI-key1,RGAPI-key2,RGAPI-key3
```

Get your API keys from the [Riot Developer Portal](https://developer.riotgames.com/).

**Note**: Using multiple API keys (`RIOT_API_KEYS`) is recommended for production deployments as it:
- Distributes load across multiple keys using round-robin rotation
- Reduces risk of hitting rate limits on a single key
- Provides redundancy if one key becomes rate-limited
- Enables higher request throughput

### Optional Variables

#### Core Configuration

```env
# Default Riot API region (default: euw1)
# For all available regions, see architecture/models.md#regional-routing-models
RIOT_DEFAULT_REGION=euw1

# Server configuration
HOST=0.0.0.0
PORT=8080

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

#### Redis Configuration

```env
# Redis connection settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

> **Note**: Connection pooling is handled automatically by aiocache library.

#### Rate Limiting Configuration

```env
# Rate limiting settings (Riot API compliance)
RIOT_RATE_LIMIT_PER_SECOND=20    # Requests per second (short-term limit)
RIOT_RATE_LIMIT_PER_2MIN=100     # Requests per 2 minutes (long-term limit)
RIOT_REQUEST_TIMEOUT=10          # HTTP request timeout in seconds
```

> **Note**: These limits use a dual-layer token bucket algorithm. Both limits must be satisfied for a request to proceed.

#### Caching Configuration

```env
# Cache TTL settings (in seconds) - Organized by API service

# ACCOUNT-V1: Account and active shard endpoints
CACHE_TTL_ACCOUNT=3600              # 1 hour - Account data (by puuid/riotId)
CACHE_TTL_ACCOUNT_SHARD=600         # 10 minutes - Active shard (can change)

# SUMMONER-V4: Summoner profile data
CACHE_TTL_SUMMONER=3600             # 1 hour

# MATCH-V5: Match history and details
CACHE_TTL_MATCH=86400               # 24 hours - Match data (immutable)
CACHE_TTL_TIMELINE=86400            # 24 hours - Match timeline (immutable)

# LEAGUE-V4: Ranked league data
CACHE_TTL_LEAGUE=3600               # 1 hour

# CHAMPION-MASTERY-V4: Champion mastery points
CACHE_TTL_MASTERY=3600              # 1 hour

# CHALLENGES-V1: Player challenges and leaderboards
CACHE_TTL_CHALLENGES_CONFIG=86400   # 24 hours - Challenge configs (static)
CACHE_TTL_CHALLENGES_LEADERBOARD=600    # 10 minutes - Leaderboards (dynamic)
CACHE_TTL_CHALLENGES_PERCENTILES=3600   # 1 hour - Percentile data
CACHE_TTL_CHALLENGES_PLAYER=3600    # 1 hour - Player challenges

# CLASH-V1: Clash tournament data
CACHE_TTL_CLASH_PLAYER=300          # 5 minutes - Player info (changes during tournaments)
CACHE_TTL_CLASH_TEAM=300            # 5 minutes - Team info (changes during tournaments)
CACHE_TTL_CLASH_TOURNAMENT=600      # 10 minutes - Tournament schedule

# CHAMPION-V3: Champion rotation
CACHE_TTL_CHAMPION_ROTATION=86400   # 24 hours - Rotation changes weekly

# LOL-STATUS-V4: Platform status
CACHE_TTL_PLATFORM_STATUS=300       # 5 minutes - Status can change frequently

# SPECTATOR-V5: Live game data
CACHE_TTL_SPECTATOR_ACTIVE=30       # 30 seconds - Active game (very dynamic)
CACHE_TTL_SPECTATOR_FEATURED=120    # 2 minutes - Featured games

# DATA-DRAGON: Static game data (champions, items, etc.)
CACHE_TTL_DDRAGON=604800            # 7 days - Static data updated per patch

# Default TTL for any uncategorized cache
CACHE_TTL_DEFAULT=3600              # 1 hour
```

> **Note**: Match tracking uses Redis SET with NO TTL for permanent storage. These are separate from TTL cache entries.

## Complete .env Example

```env
# =============================================================================
# Riot API Configuration
# =============================================================================
# Option 1: Single key (development)
RIOT_API_KEY=RGAPI-your-actual-api-key-here

# Option 2: Multiple keys (production - recommended)
# RIOT_API_KEYS=RGAPI-key1,RGAPI-key2,RGAPI-key3

RIOT_DEFAULT_REGION=euw1
RIOT_REQUEST_TIMEOUT=10

# =============================================================================
# Server Configuration
# =============================================================================
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO

# =============================================================================
# Redis Configuration
# =============================================================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# =============================================================================
# Rate Limiting Configuration
# =============================================================================
RIOT_RATE_LIMIT_PER_SECOND=20
RIOT_RATE_LIMIT_PER_2MIN=100

# =============================================================================
# Caching Configuration (All TTL values in seconds)
# =============================================================================

# ACCOUNT-V1
CACHE_TTL_ACCOUNT=3600
CACHE_TTL_ACCOUNT_SHARD=600

# SUMMONER-V4
CACHE_TTL_SUMMONER=3600

# MATCH-V5
CACHE_TTL_MATCH=86400
CACHE_TTL_TIMELINE=86400

# LEAGUE-V4
CACHE_TTL_LEAGUE=3600

# CHAMPION-MASTERY-V4
CACHE_TTL_MASTERY=3600

# CHALLENGES-V1
CACHE_TTL_CHALLENGES_CONFIG=86400
CACHE_TTL_CHALLENGES_LEADERBOARD=600
CACHE_TTL_CHALLENGES_PERCENTILES=3600
CACHE_TTL_CHALLENGES_PLAYER=3600

# CLASH-V1
CACHE_TTL_CLASH_PLAYER=300
CACHE_TTL_CLASH_TEAM=300
CACHE_TTL_CLASH_TOURNAMENT=600

# CHAMPION-V3
CACHE_TTL_CHAMPION_ROTATION=86400

# LOL-STATUS-V4
CACHE_TTL_PLATFORM_STATUS=300

# SPECTATOR-V5
CACHE_TTL_SPECTATOR_ACTIVE=30
CACHE_TTL_SPECTATOR_FEATURED=120

# DATA-DRAGON
CACHE_TTL_DDRAGON=604800

# Default
CACHE_TTL_DEFAULT=3600
```

## Configuration Files

### .env File

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your configuration
nano .env  # or use your preferred editor
```

### Docker Compose Configuration

When using Docker Compose, you can override environment variables:

```yaml
# docker-compose.yml
version: '3.8'

services:
  api-gateway:
    build: .
    ports:
      - "8080:8080"
    environment:
      - RIOT_API_KEY=${RIOT_API_KEY}
      - REDIS_HOST=redis
      - LOG_LEVEL=DEBUG
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Advanced Configuration

### Custom Rate Limiting

You can customize rate limiting by modifying the environment variables:

```env
# For high-traffic production API key
RIOT_RATE_LIMIT_PER_SECOND=50
RIOT_RATE_LIMIT_PER_2MIN=500

# For development/testing with personal API key
RIOT_RATE_LIMIT_PER_SECOND=20
RIOT_RATE_LIMIT_PER_2MIN=100
```

> **Note**: Ensure your custom limits comply with your Riot API key tier restrictions.

### Redis Configuration Notes

For production deployments with Redis:

```env
# Standard Redis configuration (current implementation uses aiocache)
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-secure-password
```

> **Note**: The current implementation uses aiocache library which handles connection pooling automatically. Redis Cluster support would require custom implementation.

## Environment-Specific Configuration

### Development

```env
# .env.development
LOG_LEVEL=DEBUG
REDIS_HOST=localhost
CACHE_TTL_SUMMONER=300                 # 5 minutes for development
CACHE_TTL_MATCH=3600                   # 1 hour (faster refresh)
RIOT_RATE_LIMIT_PER_SECOND=100         # Higher limits for testing
RIOT_RATE_LIMIT_PER_2MIN=500
```

### Production

```env
# .env.production
LOG_LEVEL=WARNING
REDIS_HOST=redis.example.com
REDIS_PASSWORD=strong-redis-password
CACHE_TTL_SUMMONER=3600                # 1 hour
CACHE_TTL_MATCH=86400                  # 24 hours
RIOT_RATE_LIMIT_PER_SECOND=20          # Conservative limits
RIOT_RATE_LIMIT_PER_2MIN=100
```

### Testing

```env
# .env.testing
LOG_LEVEL=ERROR
REDIS_HOST=localhost
CACHE_TTL_SUMMONER=1                   # Very short cache for tests
CACHE_TTL_MATCH=1
RIOT_RATE_LIMIT_PER_SECOND=1000        # Very high limits for tests
RIOT_RATE_LIMIT_PER_2MIN=5000
```

## Configuration Validation

The gateway validates configuration on startup. Here are common validation checks:

### API Key Validation

```python
# The gateway will check if your API key is valid
# Invalid or expired keys will cause startup to fail
```

### Redis Connection Test

```python
# The gateway tests Redis connectivity during startup
# Connection failures will be logged but won't prevent startup
```

### Region Validation

```python
# Supported regions are validated
# Invalid regions will fall back to the default region
```

## Performance Tuning

### Rate Limiting Optimization

```env
# For high-traffic applications (production API key)
RIOT_RATE_LIMIT_PER_SECOND=50
RIOT_RATE_LIMIT_PER_2MIN=500

# For low-traffic applications (development API key)
RIOT_RATE_LIMIT_PER_SECOND=20
RIOT_RATE_LIMIT_PER_2MIN=100
```

### Cache Optimization

```env
# Aggressive caching for better performance (fewer API calls)
CACHE_TTL_SUMMONER=7200                    # 2 hours
CACHE_TTL_MATCH=172800                     # 2 days
CACHE_TTL_LEAGUE=7200                      # 2 hours
CACHE_TTL_SPECTATOR_ACTIVE=60              # 1 minute
CACHE_TTL_CHALLENGES_LEADERBOARD=1800      # 30 minutes

# Minimal caching for fresh data (more accurate, more API calls)
CACHE_TTL_SUMMONER=300                     # 5 minutes
CACHE_TTL_MATCH=3600                       # 1 hour
CACHE_TTL_LEAGUE=600                       # 10 minutes
CACHE_TTL_SPECTATOR_ACTIVE=10              # 10 seconds
CACHE_TTL_CHALLENGES_LEADERBOARD=60        # 1 minute
```

> **Note**: Longer cache TTL improves performance but may show slightly outdated data. Balance based on your application's needs.

## Security Configuration

### API Key Protection

```env
# Never commit API keys to version control
# Use environment variables or secret management systems
RIOT_API_KEY=${RIOT_API_KEY_SECRET}
```

### Network Security

```env
# Bind to specific interface in production
HOST=127.0.0.1              # Local access only
# or
HOST=10.0.0.1               # Specific network interface
```

### Logging Security

```env
# Sanitize logs to avoid logging sensitive data
LOG_SANITIZE_SECRETS=true
LOG_LEVEL=WARNING           # Reduce log verbosity in production
```

## Monitoring Configuration

### Health Checks

```env
# Enable detailed health checks
HEALTH_CHECK_DETAILED=true
HEALTH_CHECK_REDIS=true
HEALTH_CHECK_RIOT_API=true
```

### Metrics

```env
# Enable metrics collection
METRICS_ENABLED=true
METRICS_PORT=9090
METRICS_PATH=/metrics
```

## Troubleshooting Configuration

### Common Issues

1. **API Key Not Working**
   ```env
   # Check that your API key is valid and not expired
   # Verify it doesn't have IP restrictions
   RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

2. **Redis Connection Failed**
   ```env
   # Check Redis is running and accessible
   REDIS_HOST=localhost
   REDIS_PORT=6379
   # Verify network connectivity and firewall rules
   ```

3. **Rate Limiting Too Aggressive**
   ```env
   # Adjust rate limits based on your Riot API key tier
   RIOT_RATE_LIMIT_PER_SECOND=20
   RIOT_RATE_LIMIT_PER_2MIN=100
   ```

4. **Cache Not Working**
   ```env
   # Check Redis connection and cache TTL settings
   REDIS_HOST=localhost
   CACHE_TTL_SUMMONER=3600
   ```

### Configuration Debugging

Enable debug logging to troubleshoot configuration issues:

```env
LOG_LEVEL=DEBUG
```

This will show:
- Environment variable loading
- Redis connection attempts
- Rate limiting configuration
- Cache configuration details

## Next Steps

- Configure your [development environment](../development/testing.md)
- Set up [monitoring and logging](../architecture/rate-limiting.md)
- Review the [API Reference](../api/overview.md) for endpoint details

## Getting Help

If you need help with configuration:

1. Check the [GitHub Issues](https://github.com/OneStepAt4time/lolstonks-api-gateway/issues)
2. Review the [troubleshooting guide](../development/testing.md#troubleshooting)
3. Create a new issue with your configuration details (without sensitive data)
