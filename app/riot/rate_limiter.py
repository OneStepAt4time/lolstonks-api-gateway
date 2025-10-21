"""
Rate limiting for Riot API compliance.

Uses aiolimiter to enforce Riot's rate limits:
- Application-level: 20 requests/second, 100 requests/2 minutes
- Token bucket algorithm for smooth traffic distribution
"""

from aiolimiter import AsyncLimiter
from loguru import logger

from app.config import settings


class RiotRateLimiter:
    """
    Rate limiter for Riot API compliance.

    Enforces application-level rate limits using token bucket algorithm.
    Requests are blocked until tokens are available.
    """

    def __init__(self):
        """Initialize rate limiters with configured limits."""
        self.limiter_1s = AsyncLimiter(
            max_rate=settings.riot_rate_limit_per_second,
            time_period=1,
        )
        self.limiter_2min = AsyncLimiter(
            max_rate=settings.riot_rate_limit_per_2min,
            time_period=120,
        )
        logger.info(
            "Rate limiter initialized: {}/s, {}/2min",
            settings.riot_rate_limit_per_second,
            settings.riot_rate_limit_per_2min,
        )

    async def acquire(self):
        """
        Acquire rate limit tokens before making a request.

        Blocks until both rate limiters have available tokens.
        Uses nested context managers to ensure both limits are respected.
        """
        async with self.limiter_1s:
            async with self.limiter_2min:
                pass


# Global rate limiter instance
rate_limiter = RiotRateLimiter()
