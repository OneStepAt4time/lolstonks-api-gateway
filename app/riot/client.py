"""Riot API HTTP client with intelligent rate limiting and multi-key rotation.

This module provides a production-ready HTTP client for interacting with the Riot
Games API. It implements sophisticated request management including:

Core Features:
    - Automatic rate limiting using token bucket algorithm (aiolimiter)
    - Multi-key rotation with intelligent fallback on rate limits
    - Regional routing (platform vs regional endpoints)
    - Comprehensive error handling with custom exceptions
    - Structured logging with contextual information
    - Request timeout management

Rate Limiting Strategy:
    The client uses a two-layer approach to handle Riot's rate limits:

    1. Proactive Rate Limiting:
        - Token bucket algorithm prevents requests before hitting limits
        - Configurable requests-per-second limit
        - Blocks async tasks until tokens available
        - Prevents 429 errors in most cases

    2. Reactive Key Rotation:
        - If one key gets 429, immediately tries next key
        - Cycles through all available keys before waiting
        - Only waits for Retry-After when all keys exhausted
        - Dramatically reduces wait times for multi-key setups

Multi-Key Rotation:
    When multiple API keys are configured:
    - Keys are rotated round-robin for load distribution
    - Each key has independent rate limit tracking
    - On 429 response, next key is tried immediately
    - No waiting unless all keys are rate limited

    Example with 3 keys:
        Request 1 → Key A → 429
        Request 1 (retry) → Key B → 200 ✓ (instant, no wait!)
        Request 2 → Key C → 200 ✓
        Request 3 → Key A → 200 ✓

Regional Routing:
    Riot API has two types of endpoints:

    1. Platform Endpoints (is_platform_endpoint=False):
        - Specific game servers: na1, euw1, kr, etc.
        - Used for: Summoner, Champion, League, Spectator APIs
        - Format: https://{platform}.api.riotgames.com

    2. Regional Endpoints (is_platform_endpoint=True):
        - Routing regions: americas, europe, asia, esports
        - Used for: Account, Match APIs
        - Format: https://{region}.api.riotgames.com

Error Handling:
    All Riot API errors are mapped to custom exceptions:
    - 400: BadRequestException (invalid parameters)
    - 401: UnauthorizedException (invalid/expired API key)
    - 403: ForbiddenException (access denied/restriction)
    - 404: NotFoundException (resource doesn't exist)
    - 429: RateLimitException (rate limit exceeded)
    - 500: InternalServerException (Riot server error)
    - 503: ServiceUnavailableException (API down/maintenance)

    Each exception includes the exact error message from Riot API.

Authentication:
    - API keys are passed via X-Riot-Token header
    - Keys are rotated per-request
    - Keys are never logged or exposed
    - Invalid keys are detected immediately (401 response)

Usage:
    The module exports a global `riot_client` instance that should be used
    throughout the application. The client is async and must be used with await:

    ```python
    # Fetch summoner data
    data = await riot_client.get(
        path="/lol/summoner/v4/summoners/by-name/Faker",
        region="kr",
        is_platform_endpoint=False
    )

    # Fetch match data with query parameters
    data = await riot_client.get(
        path="/lol/match/v5/matches/EUW1_123456789",
        region="europe",
        is_platform_endpoint=True
    )
    ```

Configuration:
    All configuration is via app.config.Settings:
    - RIOT_API_KEY: Primary API key (required)
    - RIOT_API_KEY_2, RIOT_API_KEY_3: Additional keys (optional)
    - RIOT_REQUEST_TIMEOUT: Request timeout in seconds
    - Rate limits configured in app.riot.rate_limiter

Performance Considerations:
    - HTTP client uses connection pooling (httpx.AsyncClient)
    - Rate limiter is shared across all requests
    - Key rotation is lock-free (no contention)
    - Regional routing is cached (no repeated lookups)

See Also:
    app.riot.rate_limiter: Token bucket rate limiting implementation
    app.riot.key_rotator: Round-robin API key rotation
    app.riot.regions: Regional routing and URL construction
    app.exceptions: Custom exception classes for error handling
"""

from typing import TYPE_CHECKING

import httpx
from loguru import logger

from app.config import settings
from app.exceptions import (
    BadRequestException,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
    RateLimitException,
    ServiceUnavailableException,
    UnauthorizedException,
)
from app.riot.key_rotator import KeyRotator
from app.riot.rate_limiter import rate_limiter
from app.riot.regions import get_base_url

if TYPE_CHECKING:
    from app.config import Settings


class RiotClient:
    """Asynchronous HTTP client for Riot Games API with intelligent request management.

    This class provides the main interface for making HTTP requests to Riot's API
    endpoints. It handles rate limiting, API key rotation, regional routing, and
    comprehensive error handling automatically.

    The client is designed to be used as a singleton (via the global riot_client
    instance) and maintains a persistent HTTP connection pool for optimal performance.

    Key Features:
        - Automatic rate limiting to prevent 429 errors
        - Multi-key rotation with instant fallback
        - Regional and platform endpoint routing
        - Comprehensive error mapping to custom exceptions
        - Structured logging for debugging and monitoring
        - Connection pooling for efficient HTTP operations

    Architecture:
        The client delegates specific concerns to specialized components:
        - KeyRotator: Round-robin API key selection
        - RateLimiter: Token bucket rate limiting
        - RegionRouter: URL construction based on endpoint type
        - Custom Exceptions: Typed error handling

    Thread Safety:
        This class is designed for async/await usage and should be used within
        the same event loop. The rate limiter uses asyncio locks for thread-safe
        token acquisition.

    Lifecycle:
        1. Initialization: Creates HTTP client and key rotator
        2. Operation: Handles requests with automatic rate limiting
        3. Cleanup: close() method should be called on shutdown

    Attributes:
        key_rotator (KeyRotator): Manages round-robin API key rotation
        client (httpx.AsyncClient): Underlying async HTTP client with connection pooling

    Example:
        ```python
        # Use global instance
        from app.riot.client import riot_client

        # Make a request
        summoner_data = await riot_client.get(
            path="/lol/summoner/v4/summoners/by-name/Faker",
            region="kr",
            is_platform_endpoint=False
        )

        # Cleanup on application shutdown
        await riot_client.close()
        ```

    Note:
        - Always use the global riot_client instance, not create new instances
        - The client is initialized at module import time
        - Call close() during application shutdown for graceful cleanup
        - All methods are async and must be awaited

    See Also:
        riot_client: Global instance of this class
        app.riot.key_rotator.KeyRotator: API key rotation logic
        app.riot.rate_limiter: Rate limiting implementation
    """

    @staticmethod
    def _extract_riot_message(response: httpx.Response, fallback: str = "") -> str:
        """
        Extract the exact error message from Riot API response.

        Riot API returns errors in format: {"status": {"message": "...", "status_code": ...}}
        This method extracts the message field exactly as provided by Riot.

        Args:
            response: The httpx Response object from Riot API
            fallback: Fallback message if extraction fails

        Returns:
            The exact error message from Riot, or fallback if not found
        """
        try:
            error_data = response.json()
            if "status" in error_data and "message" in error_data["status"]:
                message = error_data["status"]["message"]
                return str(message) if message else fallback
            # Try response text as fallback
            return response.text or fallback
        except Exception:
            return fallback

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

        # Handle error responses with custom exceptions - use EXACT Riot messages
        # Handle 400 (Bad Request) - Invalid request parameters
        if response.status_code == 400:
            error_msg = self._extract_riot_message(response, "Bad Request")
            logger.warning(f"Bad request (400): {error_msg} [region={region}]")
            raise BadRequestException(details=error_msg)

        # Handle 401 (Unauthorized) - API key invalid or expired
        if response.status_code == 401:
            error_msg = self._extract_riot_message(response, "Unauthorized")
            logger.error(f"Authentication failed (401): {error_msg} [region={region}]")
            raise UnauthorizedException(message=error_msg)

        # Handle 403 (Forbidden) - API key doesn't have access or endpoint/region restriction
        if response.status_code == 403:
            error_msg = self._extract_riot_message(response, "Forbidden")
            logger.error(f"Access forbidden (403): {error_msg} [region={region}]")
            raise ForbiddenException(message=error_msg)

        # Handle 404 (Not Found) - Resource doesn't exist
        if response.status_code == 404:
            error_msg = self._extract_riot_message(response, "Data not found")
            logger.info(f"Resource not found (404): {error_msg} [region={region}]")
            raise NotFoundException(resource_type=error_msg)

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

            # All keys exhausted - raise rate limit exception with exact Riot message
            error_msg = self._extract_riot_message(response, "Rate limit exceeded")
            logger.warning(
                f"All {total_keys} keys rate limited (429): {error_msg} [retry_after={retry_after}s]"
            )
            raise RateLimitException(retry_after=retry_after, message=error_msg)

        # Handle 500 (Internal Server Error) - Riot API server error
        if response.status_code == 500:
            error_msg = self._extract_riot_message(response, "Internal server error")
            logger.error(f"Server error (500): {error_msg} [region={region}]")
            raise InternalServerException(error_type=error_msg)

        # Handle 503 (Service Unavailable) - Riot API is down or under maintenance
        if response.status_code == 503:
            error_msg = self._extract_riot_message(response, "Service unavailable")
            logger.error(f"Service unavailable (503): {error_msg} [region={region}]")
            raise ServiceUnavailableException(message=error_msg)

        # Handle other HTTP errors
        if response.status_code >= 400:
            error_msg = self._extract_riot_message(response, f"HTTP {response.status_code}")
            logger.error(f"{error_msg} [region={region}]")
            if response.status_code >= 500:
                raise InternalServerException(error_type=error_msg)
            else:
                raise BadRequestException(details=error_msg)

        # Return JSON response
        return response.json()  # type: ignore[no-any-return]

    async def post(
        self,
        path: str,
        region: str,
        data: dict,
        is_platform_endpoint: bool = False,
        _attempted_keys: int = 0,
    ) -> dict:
        """
        Makes a POST request to the Riot API with rate limiting and smart key fallback.

        This method handles the entire process of making a POST request, including
        acquiring a rate limit token, constructing the appropriate URL, and
        handling potential 429 (rate limited) responses by trying all available
        keys before waiting.

        If one key is rate limited, it immediately tries the next available key.
        Only if ALL keys are exhausted does it wait for the Retry-After period.

        Args:
            path (str): The API path for the request (e.g., "/lol/tournament/v4/codes").
            region (str): The region to target for the request.
            data (dict): The JSON body to send with the request.
            is_platform_endpoint (bool): A flag indicating whether to use the platform-specific or regional endpoint.
            _attempted_keys (int): Internal counter for tracking key fallback attempts. Do not set manually.

        Returns:
            dict: The JSON response from the API as a dictionary.

        Raises:
            httpx.HTTPStatusError: If the API returns a non-2xx and non-429 status code.
            ValueError: If an invalid region is provided.

        Example:
            >>> await riot_client.post(
            ...     "/lol/tournament/v4/codes",
            ...     region="americas",
            ...     data={"count": 10, "mapType": "SUMMONERS_RIFT"},
            ...     is_platform_endpoint=True
            ... )

        Key Fallback Example:
            POST request to create tournament codes:
            1. Try Key 1 → 429 (rate limited)
            2. Try Key 2 immediately → 200 OK ✓ (no wait!)
        """
        # Acquire rate limit tokens (blocks until available)
        await rate_limiter.acquire()

        # Get next API key from rotator
        api_key = self.key_rotator.get_next_key()

        # Build full URL
        base_url = get_base_url(region, is_platform_endpoint)
        url = f"{base_url}{path}"

        logger.debug("Posting to Riot API: {} [region={}]", path, region)

        # Make request with rotated API key
        headers = {"X-Riot-Token": api_key}
        response = await self.client.post(url, json=data, headers=headers)

        # Debug: Log status code for troubleshooting
        logger.info(f"Riot API status: {response.status_code} for {url}")

        # Handle error responses with custom exceptions - use EXACT Riot messages
        # Handle 400 (Bad Request) - Invalid request parameters
        if response.status_code == 400:
            error_msg = self._extract_riot_message(response, "Bad Request")
            logger.warning(f"Bad request (400): {error_msg} [region={region}]")
            raise BadRequestException(details=error_msg)

        # Handle 401 (Unauthorized) - API key invalid or expired
        if response.status_code == 401:
            error_msg = self._extract_riot_message(response, "Unauthorized")
            logger.error(f"Authentication failed (401): {error_msg} [region={region}]")
            raise UnauthorizedException(message=error_msg)

        # Handle 403 (Forbidden) - API key doesn't have access or endpoint/region restriction
        if response.status_code == 403:
            error_msg = self._extract_riot_message(response, "Forbidden")
            logger.error(f"Access forbidden (403): {error_msg} [region={region}]")
            raise ForbiddenException(message=error_msg)

        # Handle 404 (Not Found) - Resource doesn't exist
        if response.status_code == 404:
            error_msg = self._extract_riot_message(response, "Data not found")
            logger.info(f"Resource not found (404): {error_msg} [region={region}]")
            raise NotFoundException(resource_type=error_msg)

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
                return await self.post(
                    path, region, data, is_platform_endpoint, _attempted_keys=_attempted_keys + 1
                )

            # All keys exhausted - raise rate limit exception with exact Riot message
            error_msg = self._extract_riot_message(response, "Rate limit exceeded")
            logger.warning(
                f"All {total_keys} keys rate limited (429): {error_msg} [retry_after={retry_after}s]"
            )
            raise RateLimitException(retry_after=retry_after, message=error_msg)

        # Handle 500 (Internal Server Error) - Riot API server error
        if response.status_code == 500:
            error_msg = self._extract_riot_message(response, "Internal server error")
            logger.error(f"Server error (500): {error_msg} [region={region}]")
            raise InternalServerException(error_type=error_msg)

        # Handle 503 (Service Unavailable) - Riot API is down or under maintenance
        if response.status_code == 503:
            error_msg = self._extract_riot_message(response, "Service unavailable")
            logger.error(f"Service unavailable (503): {error_msg} [region={region}]")
            raise ServiceUnavailableException(message=error_msg)

        # Handle other HTTP errors
        if response.status_code >= 400:
            error_msg = self._extract_riot_message(response, f"HTTP {response.status_code}")
            logger.error(f"{error_msg} [region={region}]")
            if response.status_code >= 500:
                raise InternalServerException(error_type=error_msg)
            else:
                raise BadRequestException(details=error_msg)

        # Return JSON response
        return response.json()  # type: ignore[no-any-return]

    async def put(
        self,
        path: str,
        region: str,
        data: dict,
        is_platform_endpoint: bool = False,
        _attempted_keys: int = 0,
    ) -> dict:
        """
        Makes a PUT request to the Riot API with rate limiting and smart key fallback.

        This method handles the entire process of making a PUT request, including
        acquiring a rate limit token, constructing the appropriate URL, and
        handling potential 429 (rate limited) responses by trying all available
        keys before waiting.

        If one key is rate limited, it immediately tries the next available key.
        Only if ALL keys are exhausted does it wait for the Retry-After period.

        Args:
            path (str): The API path for the request (e.g., "/lol/tournament/v4/codes/{code}").
            region (str): The region to target for the request.
            data (dict): The JSON body to send with the request.
            is_platform_endpoint (bool): A flag indicating whether to use the platform-specific or regional endpoint.
            _attempted_keys (int): Internal counter for tracking key fallback attempts. Do not set manually.

        Returns:
            dict: The JSON response from the API as a dictionary.

        Raises:
            httpx.HTTPStatusError: If the API returns a non-2xx and non-429 status code.
            ValueError: If an invalid region is provided.

        Example:
            >>> await riot_client.put(
            ...     "/lol/tournament/v4/codes/TOURNAMENT_CODE123",
            ...     region="americas",
            ...     data={"pickType": "TOURNAMENT_DRAFT"},
            ...     is_platform_endpoint=True
            ... )

        Key Fallback Example:
            PUT request to update tournament codes:
            1. Try Key 1 → 429 (rate limited)
            2. Try Key 2 immediately → 200 OK ✓ (no wait!)
        """
        # Acquire rate limit tokens (blocks until available)
        await rate_limiter.acquire()

        # Get next API key from rotator
        api_key = self.key_rotator.get_next_key()

        # Build full URL
        base_url = get_base_url(region, is_platform_endpoint)
        url = f"{base_url}{path}"

        logger.debug("Putting to Riot API: {} [region={}]", path, region)

        # Make request with rotated API key
        headers = {"X-Riot-Token": api_key}
        response = await self.client.put(url, json=data, headers=headers)

        # Debug: Log status code for troubleshooting
        logger.info(f"Riot API status: {response.status_code} for {url}")

        # Handle error responses with custom exceptions - use EXACT Riot messages
        # Handle 400 (Bad Request) - Invalid request parameters
        if response.status_code == 400:
            error_msg = self._extract_riot_message(response, "Bad Request")
            logger.warning(f"Bad request (400): {error_msg} [region={region}]")
            raise BadRequestException(details=error_msg)

        # Handle 401 (Unauthorized) - API key invalid or expired
        if response.status_code == 401:
            error_msg = self._extract_riot_message(response, "Unauthorized")
            logger.error(f"Authentication failed (401): {error_msg} [region={region}]")
            raise UnauthorizedException(message=error_msg)

        # Handle 403 (Forbidden) - API key doesn't have access or endpoint/region restriction
        if response.status_code == 403:
            error_msg = self._extract_riot_message(response, "Forbidden")
            logger.error(f"Access forbidden (403): {error_msg} [region={region}]")
            raise ForbiddenException(message=error_msg)

        # Handle 404 (Not Found) - Resource doesn't exist
        if response.status_code == 404:
            error_msg = self._extract_riot_message(response, "Data not found")
            logger.info(f"Resource not found (404): {error_msg} [region={region}]")
            raise NotFoundException(resource_type=error_msg)

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
                return await self.put(
                    path, region, data, is_platform_endpoint, _attempted_keys=_attempted_keys + 1
                )

            # All keys exhausted - raise rate limit exception with exact Riot message
            error_msg = self._extract_riot_message(response, "Rate limit exceeded")
            logger.warning(
                f"All {total_keys} keys rate limited (429): {error_msg} [retry_after={retry_after}s]"
            )
            raise RateLimitException(retry_after=retry_after, message=error_msg)

        # Handle 500 (Internal Server Error) - Riot API server error
        if response.status_code == 500:
            error_msg = self._extract_riot_message(response, "Internal server error")
            logger.error(f"Server error (500): {error_msg} [region={region}]")
            raise InternalServerException(error_type=error_msg)

        # Handle 503 (Service Unavailable) - Riot API is down or under maintenance
        if response.status_code == 503:
            error_msg = self._extract_riot_message(response, "Service unavailable")
            logger.error(f"Service unavailable (503): {error_msg} [region={region}]")
            raise ServiceUnavailableException(message=error_msg)

        # Handle other HTTP errors
        if response.status_code >= 400:
            error_msg = self._extract_riot_message(response, f"HTTP {response.status_code}")
            logger.error(f"{error_msg} [region={region}]")
            if response.status_code >= 500:
                raise InternalServerException(error_type=error_msg)
            else:
                raise BadRequestException(details=error_msg)

        # Return JSON response
        return response.json()  # type: ignore[no-any-return]


# Global client instance
riot_client = RiotClient()
