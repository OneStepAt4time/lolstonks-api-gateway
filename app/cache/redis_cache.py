"""Redis cache configuration and management using aiocache library.

This module provides the Redis caching infrastructure for the gateway application.
It implements TTL-based (Time-To-Live) caching for Riot API responses to minimize
external API calls, reduce latency, and improve overall application performance.

Caching Strategy:
    The gateway uses Redis as a distributed cache layer between the application
    and the Riot API. Benefits include:
    - Reduced API calls to Riot (avoiding rate limits)
    - Faster response times for cached data
    - Consistent cache across multiple gateway instances
    - Configurable TTLs per endpoint type
    - Automatic expiration and memory management

Cache Key Structure:
    All cache keys follow a hierarchical pattern for organization:
    Format: "lol:{resource}:{region}:{identifier}..."

    Examples:
        - "lol:summoner:name:euw1:Faker"
        - "lol:match:na1:NA1_4567890123"
        - "lol:league:challenger:kr:RANKED_SOLO_5x5"

    The "lol" prefix (namespace) prevents key collisions with other applications
    sharing the same Redis instance.

TTL Configuration:
    Different data types have different staleness tolerances:
    - Static data (champion rotation): 24 hours
    - Semi-static data (summoner profiles): 1 hour
    - Dynamic data (league entries): 5-10 minutes
    - Live data (active games): 30 seconds

    TTLs are configured per-endpoint in app.config.Settings and passed to
    caching helper functions.

Redis Configuration:
    Connection settings from environment variables:
    - REDIS_HOST: Redis server hostname (default: localhost)
    - REDIS_PORT: Redis server port (default: 6379)
    - REDIS_DB: Database number (default: 0)
    - REDIS_PASSWORD: Optional authentication password

    The module creates a global cache instance at import time.

Serialization:
    - Uses JsonSerializer from aiocache for automatic JSON encoding/decoding
    - Handles Python dicts, lists, and primitives automatically
    - Response data from Riot API is already in JSON-compatible format

Error Handling:
    Redis failures are logged but don't crash the application:
    - Connection failures: Logged and bypass cache
    - Serialization errors: Logged and bypass cache
    - Timeout errors: Logged and bypass cache

    The gateway can operate without Redis (degraded performance mode).

Health Monitoring:
    The RedisCache class provides a ping() method for health checks:
    - Used by /health endpoint
    - Tests actual Redis connectivity
    - Returns boolean status

Performance Considerations:
    - Connection pooling handled by aiocache/aioredis
    - Async operations prevent blocking
    - Namespace prefix adds minimal overhead
    - JSON serialization is efficient for API responses

Usage:
    This module exports a global `cache` instance that should be used
    throughout the application:

    ```python
    from app.cache.redis_cache import cache

    # Set value with TTL
    await cache.set("summoner:euw1:Faker", data, ttl=3600)

    # Get value (returns None if not found or expired)
    data = await cache.get("summoner:euw1:Faker")

    # Delete value
    await cache.delete("summoner:euw1:Faker")
    ```

    For higher-level caching with automatic key generation and TTL management,
    use app.cache.helpers.fetch_with_cache instead.

See Also:
    app.cache.helpers: High-level caching utilities with automatic key generation
    app.cache.tracking: Permanent tracking for processed matches
    app.config: Redis configuration settings
"""

from aiocache import Cache
from aiocache.serializers import JsonSerializer
from loguru import logger

from app.config import settings


# Global cache instance configured for Redis
cache = Cache(
    Cache.REDIS,
    endpoint=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password if settings.redis_password else None,
    serializer=JsonSerializer(),
    namespace="lol",  # Prefix for all cache keys
)

logger.info(
    "Redis cache configured: {}:{}/{}",
    settings.redis_host,
    settings.redis_port,
    settings.redis_db,
)


class RedisCache:
    """Redis cache wrapper providing health monitoring and connectivity testing.

    This class wraps the global cache instance and adds health check functionality
    for monitoring and diagnostics. It's primarily used by the health endpoint
    to verify Redis availability.

    The wrapper is intentionally minimal, delegating most operations to the
    underlying aiocache instance while providing specific health monitoring
    capabilities.

    Attributes:
        cache (Cache): The underlying aiocache instance configured for Redis

    Example:
        ```python
        redis = RedisCache()

        # Test connectivity
        is_healthy = await redis.ping()
        if not is_healthy:
            logger.error("Redis is unavailable")
        ```

    See Also:
        cache: Global cache instance for direct caching operations
        app.routers.health: Health check endpoint using this class
    """

    def __init__(self):
        """Initialize Redis cache wrapper with global cache instance."""
        self.cache = cache

    async def ping(self) -> bool:
        """Tests Redis connectivity and basic operations.

        This method verifies that Redis is:
        - Reachable from the application
        - Accepting connections
        - Able to perform basic read/write operations

        The test performs a complete write-read-delete cycle to ensure
        full functionality rather than just TCP connectivity.

        Returns:
            bool: True if Redis is healthy and responsive, False if any
                error occurs during the test operations.

        Note:
            - This method never raises exceptions; failures return False
            - All errors are logged for debugging
            - Test uses a temporary key that is immediately deleted
            - 10-second TTL ensures cleanup even if delete fails

        Example:
            ```python
            redis = RedisCache()

            if await redis.ping():
                print("Redis is healthy")
            else:
                print("Redis is unavailable or experiencing issues")
            ```
        """
        try:
            # Use a simple GET operation as ping equivalent
            await self.cache.set("health_check", "ok", ttl=10)
            result: str | None = await self.cache.get("health_check")
            await self.cache.delete("health_check")
            return result == "ok"
        except Exception as exc:
            logger.error(f"Redis ping failed: {exc}")
            return False
