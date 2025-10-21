"""
Riot API HTTP client with rate limiting and automatic retries.

Provides a wrapper around httpx for making requests to Riot API with:
- Automatic rate limiting (via aiolimiter)
- Automatic retry on 429 (rate limited) responses
- Region-aware URL routing
- Authentication header management
"""

import asyncio

import httpx
from loguru import logger

from app.config import settings
from app.riot.rate_limiter import rate_limiter
from app.riot.regions import get_base_url


class RiotClient:
    """
    HTTP client for Riot API with rate limiting and retry logic.

    Automatically applies rate limiting before each request and retries
    on 429 responses according to Retry-After header.
    """

    def __init__(self):
        """Initialize HTTP client with authentication headers."""
        self.client = httpx.AsyncClient(
            timeout=settings.riot_request_timeout,
            headers={"X-Riot-Token": settings.riot_api_key},
        )
        logger.info("Riot API client initialized")

    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()
        logger.info("Riot API client closed")

    async def get(
        self,
        path: str,
        region: str,
        is_platform_endpoint: bool = False,
        params: dict | None = None,
    ) -> dict:
        """
        Make GET request to Riot API with rate limiting and retry.

        Args:
            path: API path (e.g., '/lol/summoner/v4/summoners/by-name/Faker')
            region: Region code (e.g., 'euw1', 'kr')
            is_platform_endpoint: True for Match API, False for Summoner/League/Mastery
            params: Optional query parameters

        Returns:
            JSON response as dictionary

        Raises:
            httpx.HTTPStatusError: On non-retryable HTTP errors
            ValueError: On invalid region

        Example:
            >>> await riot_client.get(
            ...     "/lol/summoner/v4/summoners/by-name/Faker",
            ...     region="kr",
            ...     is_platform_endpoint=False
            ... )
        """
        # Acquire rate limit tokens (blocks until available)
        await rate_limiter.acquire()

        # Build full URL
        base_url = get_base_url(region, is_platform_endpoint)
        url = f"{base_url}{path}"

        logger.debug("Requesting Riot API: {} [region={}]", path, region)

        # Make request
        response = await self.client.get(url, params=params)

        # Handle 429 (rate limited) - should be rare due to our rate limiter
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            logger.warning(
                "Rate limited by Riot API (429), retrying after {}s",
                retry_after,
            )
            await asyncio.sleep(retry_after)
            # Retry the request (recursive call)
            return await self.get(path, region, is_platform_endpoint, params)

        # Raise on other HTTP errors
        response.raise_for_status()

        # Return JSON response
        return response.json()


# Global client instance
riot_client = RiotClient()
