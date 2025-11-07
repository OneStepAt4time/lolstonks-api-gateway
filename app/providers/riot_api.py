"""
Riot API provider implementation.

Wraps the existing RiotClient to provide the BaseProvider interface
for the Riot Games Developer Portal API.
"""

from typing import Any

from loguru import logger

from app.config import settings
from app.providers.base import BaseProvider, ProviderCapability, ProviderType
from app.riot.client import RiotClient


class RiotAPIProvider(BaseProvider):
    """
    Provider for Riot Games Developer Portal API.

    Provides access to live game data including:
    - Summoner information
    - Match history and details
    - League standings
    - Live game spectator data
    - Champion mastery
    - And more...

    Requires API key authentication and respects rate limits.
    """

    def __init__(self, settings_override=None):
        """
        Initialize Riot API provider.

        Args:
            settings_override: Optional Settings instance for testing
        """
        # Initialize with base URL (will be overridden by region routing)
        super().__init__(name="Riot Games Developer API", base_url="https://api.riotgames.com")

        # Wrap existing RiotClient
        self.client = RiotClient(settings_override=settings_override)

        logger.info(f"Initialized {self.name} provider")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.RIOT_API

    @property
    def requires_auth(self) -> bool:
        return True

    def get_capabilities(self) -> list[ProviderCapability]:
        return [
            ProviderCapability.LIVE_DATA,
            ProviderCapability.HISTORICAL_DATA,
        ]

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        region: str | None = None,
        is_platform_endpoint: bool = False,
    ) -> dict[str, Any] | list[Any]:
        """
        Fetch data from Riot API.

        Args:
            path: API endpoint path
            params: Query parameters
            headers: Additional headers (ignored - auth handled by client)
            region: Riot API region (required)
            is_platform_endpoint: Whether this is a platform endpoint

        Returns:
            Response data

        Raises:
            ValueError: If region is not provided
            httpx.HTTPStatusError: On HTTP errors
        """
        if region is None:
            region = settings.riot_default_region

        logger.debug(f"RiotAPIProvider: GET {path} [region={region}]")

        # Delegate to existing RiotClient
        return await self.client.get(
            path=path,
            region=region,
            is_platform_endpoint=is_platform_endpoint,
            params=params,
        )

    async def health_check(self) -> bool:
        """
        Check Riot API health.

        Returns:
            True if API is accessible
        """
        try:
            # Try to fetch platform status for a region
            await self.client.get(
                path="/lol/status/v4/platform-data",
                region=settings.riot_default_region,
                is_platform_endpoint=False,
            )
            logger.info(f"{self.name} health check: OK")
            return True
        except Exception as e:
            logger.error(f"{self.name} health check failed: {e}")
            return False

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.close()
        logger.info(f"{self.name} provider closed")
