"""
Match tracking service using Redis SETs.

Provides permanent tracking of processed matches to avoid reprocessing.
Uses Redis SETs with NO TTL - data persists across restarts via appendonly file.
"""

import redis.asyncio as redis
from loguru import logger

from app.config import settings


class MatchTracker:
    """
    Track processed matches in Redis using SET data structure.

    Key pattern: processed_matches:{region}
    No TTL - permanent storage backed by Redis appendonly file.
    """

    def __init__(self):
        """Initialize tracker (connection established on startup)."""
        self.redis: redis.Redis | None = None
        logger.info("Match tracker initialized (connection pending)")

    async def connect(self):
        """
        Establish Redis connection.

        Should be called during FastAPI startup event.
        """
        redis_url = f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
        if settings.redis_password:
            redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"

        self.redis = await redis.from_url(redis_url, decode_responses=True)
        logger.success("Match tracker connected to Redis")

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.aclose()  # type: ignore[attr-defined]
            logger.info("Match tracker connection closed")

    async def is_processed(self, region: str, match_id: str) -> bool:
        """
        Check if a match has already been processed.

        Args:
            region: Region code (e.g., 'euw1')
            match_id: Match ID (e.g., 'EUW1_123456789')

        Returns:
            True if match is in tracking set, False otherwise
        """
        if not self.redis:
            logger.warning("Redis not connected, assuming match not processed")
            return False

        key = f"processed_matches:{region}"
        is_member = await self.redis.sismember(key, match_id)
        return bool(is_member)

    async def mark_processed(self, region: str, match_id: str):
        """
        Mark a match as processed.

        Args:
            region: Region code (e.g., 'euw1')
            match_id: Match ID (e.g., 'EUW1_123456789')
        """
        if not self.redis:
            logger.warning("Redis not connected, cannot mark match as processed")
            return

        key = f"processed_matches:{region}"
        await self.redis.sadd(key, match_id)
        logger.debug("Marked match as processed: {}/{}", region, match_id)

    async def get_processed_count(self, region: str) -> int:
        """
        Get count of processed matches for a region.

        Args:
            region: Region code (e.g., 'euw1')

        Returns:
            Number of tracked matches for the region
        """
        if not self.redis:
            return 0

        key = f"processed_matches:{region}"
        return await self.redis.scard(key)


# Global tracker instance
tracker = MatchTracker()
