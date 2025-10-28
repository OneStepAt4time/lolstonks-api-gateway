# Configuration

This guide covers all configuration options available for the LOLStonks API Gateway.

## Environment Variables

The gateway uses environment variables for configuration. You can set these in a `.env` file or as system environment variables.

### Required Variables

```env
# Riot Games API Key
RIOT_API_KEY=RGAPI-your-api-key-here
```

Get your API key from the [Riot Developer Portal](https://developer.riotgames.com/).

### Optional Variables

#### Core Configuration

```env
# Default Riot API region (default: euw1)
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

# Redis connection pool settings
REDIS_POOL_SIZE=10
REDIS_POOL_TIMEOUT=30
```

#### Rate Limiting Configuration

```env
# Rate limiting settings
RATE_LIMIT_RPS=20           # Requests per second
RATE_LIMIT_BURST=100        # Burst capacity
RATE_LIMIT_PERIOD=120       # Period in seconds for burst refill
```

#### Caching Configuration

```env
# Cache TTL settings (in seconds)
CACHE_TTL_SUMMONER=3600     # 1 hour
CACHE_TTL_MATCH=86400       # 24 hours
CACHE_TTL_LEAGUE=1800       # 30 minutes
CACHE_TTL_MASTERY=7200      # 2 hours
CACHE_TTL_CHAMPION=604800   # 1 week

# Match tracking TTL
MATCH_TRACKING_TTL=604800   # 1 week
```

## Complete .env Example

```env
# =============================================================================
# Riot API Configuration
# =============================================================================
RIOT_API_KEY=RGAPI-your-actual-api-key-here
RIOT_DEFAULT_REGION=euw1

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
REDIS_POOL_SIZE=10
REDIS_POOL_TIMEOUT=30

# =============================================================================
# Rate Limiting Configuration
# =============================================================================
RATE_LIMIT_RPS=20
RATE_LIMIT_BURST=100
RATE_LIMIT_PERIOD=120

# =============================================================================
# Caching Configuration
# =============================================================================
CACHE_TTL_SUMMONER=3600
CACHE_TTL_MATCH=86400
CACHE_TTL_LEAGUE=1800
CACHE_TTL_MASTERY=7200
CACHE_TTL_CHAMPION=604800
MATCH_TRACKING_TTL=604800
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

You can customize rate limiting per endpoint or per region:

```python
# In your custom configuration
CUSTOM_RATE_LIMITS = {
    "summoner": {"rps": 30, "burst": 150},
    "match": {"rps": 10, "burst": 50},
    "league": {"rps": 20, "burst": 100}
}
```

### Redis Cluster Configuration

For production deployments, you can use Redis Cluster:

```env
# Redis Cluster configuration
REDIS_CLUSTER_ENABLED=true
REDIS_CLUSTER_NODES=redis-node1:6379,redis-node2:6379,redis-node3:6379
REDIS_CLUSTER_PASSWORD=your-cluster-password
```

### Custom Cache Keys

Customize cache key patterns:

```env
# Cache key patterns
CACHE_KEY_PREFIX=lolstonks
CACHE_KEY_VERSION=v1
```

## Environment-Specific Configuration

### Development

```env
# .env.development
LOG_LEVEL=DEBUG
REDIS_HOST=localhost
CACHE_TTL_SUMMONER=300      # 5 minutes for development
RATE_LIMIT_RPS=100          # Higher limits for testing
```

### Production

```env
# .env.production
LOG_LEVEL=WARNING
REDIS_HOST=redis-cluster.example.com
REDIS_PASSWORD=strong-redis-password
CACHE_TTL_SUMMONER=3600     # Longer cache for production
RATE_LIMIT_RPS=20           # Conservative limits
```

### Testing

```env
# .env.testing
LOG_LEVEL=ERROR
REDIS_HOST=localhost
CACHE_TTL_SUMMONER=1        # Very short cache for tests
RATE_LIMIT_RPS=1000         # Very high limits for tests
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
# For high-traffic applications
RATE_LIMIT_RPS=50
RATE_LIMIT_BURST=500
RATE_LIMIT_PERIOD=60

# For low-traffic applications
RATE_LIMIT_RPS=5
RATE_LIMIT_BURST=20
RATE_LIMIT_PERIOD=300
```

### Cache Optimization

```env
# Aggressive caching for better performance
CACHE_TTL_SUMMONER=7200     # 2 hours
CACHE_TTL_MATCH=172800      # 2 days
CACHE_TTL_LEAGUE=3600       # 1 hour

# Minimal caching for fresh data
CACHE_TTL_SUMMONER=300      # 5 minutes
CACHE_TTL_MATCH=1800        # 30 minutes
CACHE_TTL_LEAGUE=600        # 10 minutes
```

### Redis Performance

```env
# Connection pool optimization
REDIS_POOL_SIZE=20          # Increase for high concurrency
REDIS_POOL_TIMEOUT=10       # Lower timeout for faster failover

# Memory optimization
REDIS_MAXMEMORY=1gb
REDIS_MAXMEMORY_POLICY=allkeys-lru
```

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
   # Adjust rate limits based on your usage
   RATE_LIMIT_RPS=10
   RATE_LIMIT_BURST=50
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