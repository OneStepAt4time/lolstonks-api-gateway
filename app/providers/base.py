"""
Base provider interface for API Gateway.

Defines the contract that all API providers must implement.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class ProviderType(str, Enum):
    """Supported API provider types."""

    RIOT_API = "riot_api"
    DATA_DRAGON = "data_dragon"
    COMMUNITY_DRAGON = "community_dragon"


class ProviderCapability(str, Enum):
    """Capabilities that providers may support."""

    LIVE_DATA = "live_data"  # Real-time game data
    STATIC_DATA = "static_data"  # Champion, item, rune data
    HISTORICAL_DATA = "historical_data"  # Match history
    ASSETS = "assets"  # Images, icons, splash arts
    VERSIONED = "versioned"  # Supports multiple game versions


class BaseProvider(ABC):
    """
    Abstract base class for all API providers.

    Providers must implement the core methods to fetch data,
    check health, and declare their capabilities.
    """

    def __init__(self, name: str, base_url: str):
        """
        Initialize the provider.

        Args:
            name: Human-readable provider name
            base_url: Base URL for API requests
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

        Args:
            path: API endpoint path (relative to base_url)
            params: Query parameters
            headers: Additional HTTP headers

        Returns:
            Response data (JSON parsed)

        Raises:
            httpx.HTTPStatusError: On HTTP errors
            httpx.RequestError: On network errors
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and accessible.

        Returns:
            True if provider is healthy, False otherwise
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[ProviderCapability]:
        """
        Get the capabilities supported by this provider.

        Returns:
            List of capabilities
        """
        pass

    @property
    @abstractmethod
    def requires_auth(self) -> bool:
        """
        Check if this provider requires authentication.

        Returns:
            True if authentication is required
        """
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """
        Get the provider type.

        Returns:
            Provider type enum value
        """
        pass

    async def close(self):
        """
        Clean up provider resources.

        Override this method if your provider needs cleanup.
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, base_url={self.base_url})>"
