"""
Cache helper utilities to reduce code duplication.

Provides a unified interface for cache-aware data fetching with
consistent logging across all endpoints.
"""

from typing import Any, Awaitable, Callable

from loguru import logger

from app.cache.redis_cache import cache


async def fetch_with_cache(
    cache_key: str,
    resource_name: str,
    fetch_fn: Callable[[], Awaitable[Any]],
    ttl: int,
    context: dict[str, Any] | None = None,
    force_refresh: bool = False,
) -> Any:
    """
    Fetch data with automatic caching and consistent logging.

    This helper eliminates code duplication across routers by providing
    a unified cache-aware fetch pattern with standardized logging.

    Args:
        cache_key: Redis cache key for storing the data
        resource_name: Human-readable resource name for logging (e.g., "Champion rotation", "Match data")
        fetch_fn: Async callable that fetches data from Riot API
        ttl: Time-to-live for the cached data in seconds
        context: Optional dict of context data to include in logs (e.g., {"region": "euw1", "match_id": "EUW1_123"})
        force_refresh: If True, bypass cache and force fetch from API

    Returns:
        The fetched or cached data

    Example:
        >>> async def fetch_rotations():
        ...     return await riot_client.get("/lol/platform/v3/champion-rotations", "euw1", False)
        >>> data = await fetch_with_cache(
        ...     cache_key="champion:rotation:euw1",
        ...     resource_name="Champion rotation",
        ...     fetch_fn=fetch_rotations,
        ...     ttl=86400,
        ...     context={"region": "euw1"}
        ... )
    """
    context = context or {}

    # Check cache (unless force refresh)
    if not force_refresh:
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info(f"{resource_name} retrieved from cache", **context, source="cache")
            return cached_data

    # Fetch from Riot API
    logger.info(f"{resource_name} retrieved from Riot API", **context, source="riot_api")
    data = await fetch_fn()

    # Store in cache
    await cache.set(cache_key, data, ttl=ttl)
    logger.success(f"{resource_name} fetched and cached", **context)

    return data
