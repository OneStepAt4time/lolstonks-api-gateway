"""
Riot API HTTP client with rate limiting and automatic retries.

Provides a wrapper around httpx for making requests to Riot API with:
- Automatic rate limiting (via aiolimiter)
- Automatic retry on 429 (rate limited) responses
- Region-aware URL routing
- Authentication header management
"""

import asyncio
from typing import TYPE_CHECKING

import httpx
from loguru import logger

from app.config import settings
from app.riot.key_rotator import KeyRotator
from app.riot.rate_limiter import rate_limiter
from app.riot.regions import get_base_url

if TYPE_CHECKING:
    from app.config import Settings


class RiotClient:
    """
    HTTP client for Riot API with rate limiting and retry logic.

    Automatically applies rate limiting before each request and retries
    on 429 responses according to Retry-After header.

    Supports multiple API keys with round-robin rotation for load distribution.
    """

    def __init__(self, settings_override: "Settings | None" = None):
        """Initialize HTTP client with key rotation support.

        Args:
            settings_override: Optional Settings instance to use instead of global settings.
                             Useful for testing with custom configurations.
        """
        # Use provided settings or fall back to global settings
        config = settings_override if settings_override is not None else settings

        # Initialize key rotator with configured API keys
        api_keys = config.get_api_keys()
        self.key_rotator = KeyRotator(api_keys)

        # Create HTTP client without static auth header
        # (will be added per-request from key rotator)
        self.client = httpx.AsyncClient(
            timeout=config.riot_request_timeout,
        )

        key_count = len(api_keys)
        logger.info(
            f"Riot API client initialized with {key_count} API key{'s' if key_count > 1 else ''}"
        )

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
        _attempted_keys: int = 0,
    ) -> dict:
        """
        Makes a GET request to the Riot API with rate limiting and smart key fallback.

        This method handles the entire process of making a GET request, including
        acquiring a rate limit token, constructing the appropriate URL, and
        handling potential 429 (rate limited) responses by trying all available
        keys before waiting.

        If one key is rate limited, it immediately tries the next available key.
        Only if ALL keys are exhausted does it wait for the Retry-After period.

        Args:
            path (str): The API path for the request (e.g., "/lol/match/v5/matches/EUW1_123").
            region (str): The region to target for the request.
            is_platform_endpoint (bool): A flag indicating whether to use the platform-specific or regional endpoint.
            params (dict, optional): A dictionary of query parameters to include in the request. Defaults to None.
            _attempted_keys (int): Internal counter for tracking key fallback attempts. Do not set manually.

        Returns:
            dict: The JSON response from the API as a dictionary.

        Raises:
            httpx.HTTPStatusError: If the API returns a non-2xx and non-429 status code.
            ValueError: If an invalid region is provided.

        Example:
            >>> await riot_client.get(
            ...     "/lol/summoner/v4/summoners/by-name/Faker",
            ...     region="kr",
            ...     is_platform_endpoint=False
            ... )

        Key Fallback Example:
            Request for Match EUW1_123456789:
            1. Try Key 1 → 429 (rate limited)
            2. Try Key 2 immediately → 200 OK ✓ (no wait!)

            Same match ID is preserved across all retry attempts.
        """
        # Acquire rate limit tokens (blocks until available)
        await rate_limiter.acquire()

        # Get next API key from rotator
        api_key = self.key_rotator.get_next_key()

        # Build full URL
        base_url = get_base_url(region, is_platform_endpoint)
        url = f"{base_url}{path}"

        logger.debug("Requesting Riot API: {} [region={}]", path, region)

        # Make request with rotated API key
        headers = {"X-Riot-Token": api_key}
        response = await self.client.get(url, params=params, headers=headers)

        # Debug: Log status code for troubleshooting
        logger.info(f"Riot API status: {response.status_code} for {url}")

        # Handle 429 (rate limited) - try next key or wait if all exhausted
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            total_keys = self.key_rotator.get_key_count()

            # If we haven't tried all keys yet, try the next one immediately
            if _attempted_keys + 1 < total_keys:
                logger.warning(
                    f"Rate limited (429), trying next key ({_attempted_keys + 1}/{total_keys} keys attempted)"
                )
                # Immediately retry with next key (no sleep!)
                return await self.get(
                    path, region, is_platform_endpoint, params, _attempted_keys=_attempted_keys + 1
                )

            # All keys exhausted - wait before trying again
            logger.warning(
                f"All {total_keys} keys rate limited (429), waiting {retry_after}s before retry"
            )
            await asyncio.sleep(retry_after)

            # Reset counter and try again from first key
            return await self.get(path, region, is_platform_endpoint, params, _attempted_keys=0)

        # Handle 401 (Unauthorized) - API key invalid or expired
        if response.status_code == 401:
            error_msg = "API key is invalid or expired"
            logger.error(f"Authentication failed (401): {error_msg} [region={region}]")
            raise ValueError(error_msg)

        # Handle 403 (Forbidden) - API key doesn't have access or endpoint/region restriction
        if response.status_code == 403:
            error_msg = "API key doesn't have access to this endpoint or region"
            logger.error(f"Access forbidden (403): {error_msg} [region={region}]")
            raise ValueError(error_msg)

        # Raise on other HTTP errors
        response.raise_for_status()

        # Return JSON response
        return response.json()  # type: ignore[no-any-return]


# Global client instance
riot_client = RiotClient()
