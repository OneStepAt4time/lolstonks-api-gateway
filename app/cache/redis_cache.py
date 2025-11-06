"""
Redis cache configuration using aiocache.

Provides temporary TTL-based caching for API responses.
Cache keys follow pattern: {resource}:{region}:{identifier}
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
    """Redis wrapper with health check capabilities."""

    def __init__(self):
        """Initialize Redis cache wrapper."""
        self.cache = cache

    async def ping(self) -> bool:
        """
        Test Redis connectivity.

        Returns:
            True if Redis is responsive, False otherwise
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
