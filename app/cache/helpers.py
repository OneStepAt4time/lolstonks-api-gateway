"""
Cache helper utilities to reduce code duplication.

Provides a unified interface for cache-aware data fetching with
consistent logging across all endpoints.
"""

from typing import Any, Awaitable, Callable

import httpx
from loguru import logger

from app.cache.redis_cache import cache
from app.exceptions import (
    RiotAPIException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    RateLimitException,
    InternalServerException,
)


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
            log_context = context.copy()
            log_context["source"] = "cache"
            logger.info(f"{resource_name} retrieved from cache", **log_context)
            return cached_data

    # Fetch from Riot API
    log_context = context.copy()
    log_context["source"] = "riot_api"
    logger.info(f"{resource_name} retrieved from Riot API", **log_context)

    try:
        data = await fetch_fn()
    except ValueError as e:
        # Handle authentication/authorization errors from Riot client
        error_msg = str(e)
        if "invalid or expired" in error_msg.lower():
            raise UnauthorizedException(message=error_msg)
        elif "access" in error_msg.lower():
            raise ForbiddenException(message=error_msg)
        else:
            raise InternalServerException(error_type="Authentication error", details=error_msg)
    except httpx.HTTPStatusError as e:
        # Handle HTTP errors from API calls
        error_msg = str(e)

        # Special handling for Data Dragon 403 errors
        if e.response.status_code == 403:
            if "ddragon" in str(e.request.url).lower():
                logger.error(
                    f"Data Dragon 403 error for {resource_name}: {error_msg}",
                    url=str(e.request.url),
                    **context,
                )
                # Provide more helpful error message for Data Dragon
                raise ForbiddenException(
                    message=f"Data Dragon access forbidden. The 'latest' version alias is no longer supported. Please specify an actual version number or contact support. URL: {e.request.url}"
                )
            else:
                raise ForbiddenException()

        # Handle other HTTP status codes
        if e.response.status_code == 404:
            raise NotFoundException(resource_type=resource_name)
        elif e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 1))
            raise RateLimitException(retry_after=retry_after)
        elif 500 <= e.response.status_code < 600:
            logger.error(
                f"Server error fetching {resource_name}: {error_msg}",
                status_code=e.response.status_code,
                url=str(e.request.url),
                **context,
            )
            raise InternalServerException(error_type="Upstream server error", details=error_msg)
        else:
            raise InternalServerException(error_type="HTTP error", details=error_msg)
    except RiotAPIException:
        # Re-raise our custom API exceptions without wrapping
        raise
    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error fetching {resource_name}: {e}", **context)
        raise InternalServerException(error_type="Unexpected error", details=str(e))

    # Store in cache
    await cache.set(cache_key, data, ttl=ttl)
    logger.success(f"{resource_name} fetched and cached", **context)

    return data
