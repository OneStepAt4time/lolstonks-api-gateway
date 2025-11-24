"""
Base provider interface for API Gateway.

Defines the contract that all API providers must implement for consistent
data fetching, health checking, and capability declaration.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class ProviderType(str, Enum):
    """Supported API provider types.

    Enum representing the different backend providers that can supply
    League of Legends data to the gateway.
    """

    RIOT_API = "riot_api"
    DATA_DRAGON = "data_dragon"
    COMMUNITY_DRAGON = "community_dragon"


class ProviderCapability(str, Enum):
    """Capabilities that providers may support.

    Defines the types of data and features that different providers
    can offer. Used for provider selection and routing decisions.
    """

    LIVE_DATA = "live_data"  # Real-time game data
    STATIC_DATA = "static_data"  # Champion, item, rune data
    HISTORICAL_DATA = "historical_data"  # Match history
    ASSETS = "assets"  # Images, icons, splash arts
    VERSIONED = "versioned"  # Supports multiple game versions


class BaseProvider(ABC):
    """
    Abstract base class for all API providers.

    Providers must implement the core methods to fetch data,
    check health, and declare their capabilities. This ensures
    a consistent interface across all backend services.

    Attributes:
        name: Human-readable provider name for logging and debugging
        base_url: Base URL for API requests (provider-specific)

    Example:
        ```python
        class MyProvider(BaseProvider):
            def __init__(self):
                super().__init__(name="My Provider", base_url="https://api.example.com")

            @property
            def provider_type(self) -> ProviderType:
                return ProviderType.RIOT_API

            @property
            def requires_auth(self) -> bool:
                return True

            # ... implement other abstract methods
        ```
    """

    def __init__(self, name: str, base_url: str):
        """
        Initialize the provider.

        Args:
            name: Human-readable provider name (e.g., "Riot Games Developer API")
            base_url: Base URL for API requests (e.g., "https://api.riotgames.com")

        Example:
            ```python
            super().__init__(
                name="Data Dragon CDN",
                base_url="https://ddragon.leagueoflegends.com"
            )
            ```
        """
        self.name = name
        self.base_url = base_url

    @abstractmethod
    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Fetch data from the provider.

        Core method for making HTTP requests to the provider's API.
        Implementations should handle authentication, error handling,
        and response parsing.

        Args:
            path: API endpoint path relative to base_url (e.g., "/lol/summoner/v4/...")
            params: Query parameters to include in the request
            headers: Additional HTTP headers to send with the request

        Returns:
            Response data parsed as JSON (dict or list depending on endpoint)

        Raises:
            httpx.HTTPStatusError: On HTTP errors (4xx, 5xx responses)
            httpx.RequestError: On network errors (connection failures, timeouts)

        Example:
            ```python
            data = await provider.get(
                path="/lol/summoner/v4/summoners/by-name/TestPlayer",
                params={"region": "na1"},
                headers={"X-Custom-Header": "value"}
            )
            ```
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and accessible.

        Performs a lightweight request to verify the provider is reachable
        and responding correctly. Used by health check endpoints and
        monitoring systems.

        Returns:
            True if provider is healthy and accessible, False otherwise

        Example:
            ```python
            if not await provider.health_check():
                logger.error(f"{provider.name} is unhealthy")
                # Take corrective action
            ```
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[ProviderCapability]:
        """
        Get the capabilities supported by this provider.

        Declares what types of data and features this provider offers.
        Used for routing requests to appropriate providers and generating
        API documentation.

        Returns:
            List of capability enum values

        Example:
            ```python
            caps = provider.get_capabilities()
            if ProviderCapability.LIVE_DATA in caps:
                # Can fetch real-time match data
                match_data = await provider.get("/lol/match/v5/...")
            ```
        """
        pass

    @property
    @abstractmethod
    def requires_auth(self) -> bool:
        """Check if this provider requires authentication.

        Indicates whether requests to this provider must include authentication
        credentials (API keys, tokens, etc.). Used by the gateway to determine
        if auth headers should be added to requests.

        Returns:
            True if authentication is required, False otherwise.

        Example:
            ```python
            if provider.requires_auth:
                headers["X-Riot-Token"] = settings.riot_api_key
            response = await provider.get(path, headers=headers)
            ```
        """
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Get the provider type enum value.

        Returns the type classification of this provider, used for routing
        and metrics tracking throughout the gateway.

        Returns:
            Provider type enum value (RIOT_API, DATA_DRAGON, or COMMUNITY_DRAGON).

        Example:
            ```python
            if provider.provider_type == ProviderType.RIOT_API:
                # Apply rate limiting
                await rate_limiter.acquire()
            data = await provider.get(path)
            ```
        """
        pass

    async def close(self):
        """
        Clean up provider resources.

        Override this method if your provider needs cleanup (closing HTTP clients,
        database connections, etc.). Called when the application shuts down.

        Example:
            ```python
            async def close(self):
                await self.client.aclose()
                logger.info(f"{self.name} provider closed")
            ```
        """
        pass

    def __repr__(self) -> str:
        """Return string representation of the provider.

        Provides a developer-friendly representation showing the provider's
        class name and configuration.

        Returns:
            String representation in format "<ClassName(name=..., base_url=...)>"

        Example:
            ```python
            >>> provider = RiotAPIProvider()
            >>> print(provider)
            <RiotAPIProvider(name=Riot Games Developer API, base_url=https://api.riotgames.com)>
            ```
        """
        return f"<{self.__class__.__name__}(name={self.name}, base_url={self.base_url})>"
