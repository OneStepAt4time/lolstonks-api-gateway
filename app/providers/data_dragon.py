"""
Data Dragon CDN provider implementation.

Provides access to Riot's static data CDN including champion data,
items, runes, summoner spells, and profile icons.
"""

from typing import Any, Optional

import httpx
from loguru import logger

from app.config import settings
from app.providers.base import BaseProvider, ProviderCapability, ProviderType


class DataDragonProvider(BaseProvider):
    """
    Provider for Riot's Data Dragon CDN.

    Data Dragon provides static game data including:
    - Champion information
    - Item data
    - Rune data
    - Summoner spell data
    - Profile icons
    - Map data
    - Language/localization data

    No authentication required. All data is public.

    API Documentation: https://developer.riotgames.com/docs/lol#data-dragon
    Base URL: https://ddragon.leagueoflegends.com
    """

    def __init__(self, version: str = "latest", locale: str = "en_US"):
        """
        Initialize Data Dragon provider.

        Args:
            version: Game version (e.g., "13.24.1" or "latest")
            locale: Language locale (e.g., "en_US", "ko_KR", "ja_JP")
        """
        super().__init__(name="Data Dragon CDN", base_url="https://ddragon.leagueoflegends.com")

        self.version = version
        self.locale = locale
        self._latest_version_cache: Optional[str] = None  # Cache for latest version
        self.client = httpx.AsyncClient(
            timeout=settings.riot_request_timeout,
            follow_redirects=True,
        )

        logger.info(f"Initialized {self.name} provider [version={version}, locale={locale}]")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.DATA_DRAGON

    @property
    def requires_auth(self) -> bool:
        return False

    def get_capabilities(self) -> list[ProviderCapability]:
        return [
            ProviderCapability.STATIC_DATA,
            ProviderCapability.ASSETS,
            ProviderCapability.VERSIONED,
        ]

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Fetch data from Data Dragon CDN.

        Args:
            path: CDN path (e.g., "/cdn/13.24.1/data/en_US/champion.json")
            params: Query parameters (usually not needed for CDN)
            headers: Additional HTTP headers

        Returns:
            Response data (JSON parsed)

        Raises:
            httpx.HTTPStatusError: On HTTP errors
            httpx.RequestError: On network errors
        """
        url = f"{self.base_url}{path}"

        logger.debug(f"DataDragonProvider: GET {path}")

        try:
            response = await self.client.get(
                url,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            # Special handling for Data Dragon 403 errors (often due to "latest" version)
            if e.response.status_code == 403:
                logger.warning(
                    f"Data Dragon 403 Forbidden for path: {path}. "
                    f"This typically happens when using 'latest' version which is no longer supported."
                )
                # Add additional context to the error
                raise httpx.HTTPStatusError(
                    f"Data Dragon access forbidden for path '{path}'. "
                    f"The 'latest' version alias is no longer supported by Riot's CDN. "
                    f"Please specify an actual version number (e.g., '15.22.1').",
                    request=e.request,
                    response=e.response,
                ) from e
            raise

    async def _get_latest_version(self) -> str:
        """
        Get the actual latest version from Riot's API.

        Caches the result to avoid repeated API calls.

        Returns:
            The latest version string (e.g., "15.22.1")

        Raises:
            httpx.HTTPStatusError: If unable to fetch versions
        """
        if self._latest_version_cache is None:
            logger.info("Fetching latest Data Dragon version from API")
            versions = await self.get_versions()
            if not versions:
                raise httpx.HTTPStatusError(
                    "No versions available from Data Dragon API",
                    request=None,
                    response=None,
                )
            # Get the first version which is the latest
            self._latest_version_cache = versions[0]
            logger.info(f"Cached latest Data Dragon version: {self._latest_version_cache}")

        return self._latest_version_cache

    async def _resolve_version(self, version: str) -> str:
        """
        Resolve version string, handling 'latest' alias.

        Args:
            version: Version string ("latest" or actual version)

        Returns:
            Resolved version string
        """
        if version == "latest":
            try:
                return await self._get_latest_version()
            except Exception as e:
                logger.error(f"Failed to resolve latest version: {e}")
                # Fallback to a recent known version as emergency fallback
                fallback_version = "15.22.1"
                logger.warning(f"Using fallback version: {fallback_version}")
                return fallback_version
        return version

    async def health_check(self) -> bool:
        """
        Check Data Dragon CDN health.

        Returns:
            True if CDN is accessible
        """
        try:
            # Try to fetch versions list
            await self.get("/api/versions.json")
            logger.info(f"{self.name} health check: OK")
            return True
        except Exception as e:
            logger.error(f"{self.name} health check failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info(f"{self.name} provider closed")

    # Helper methods for common Data Dragon endpoints

    async def get_versions(self) -> list[str]:
        """
        Get list of available game versions.

        Returns:
            List of version strings (e.g., ["13.24.1", "13.23.1", ...])
        """
        return await self.get("/api/versions.json")  # type: ignore[return-value]

    async def get_champions(self, version: str | None = None, locale: str | None = None) -> dict:
        """
        Get all champion data.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Champion data dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/champion.json")  # type: ignore[return-value]

    async def get_champion(
        self, champion_id: str, version: str | None = None, locale: str | None = None
    ) -> dict:
        """
        Get detailed data for a specific champion.

        Args:
            champion_id: Champion ID (e.g., "Ahri", "LeeSin")
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Champion detail data
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/champion/{champion_id}.json")  # type: ignore[return-value]

    async def get_items(self, version: str | None = None, locale: str | None = None) -> dict:
        """
        Get all item data.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Item data dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/item.json")  # type: ignore[return-value]

    async def get_runes(self, version: str | None = None, locale: str | None = None) -> list[dict]:
        """
        Get all rune data.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            List of rune trees
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/runesReforged.json")  # type: ignore[return-value]

    async def get_summoner_spells(
        self, version: str | None = None, locale: str | None = None
    ) -> dict:
        """
        Get all summoner spell data.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Summoner spell data dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/summoner.json")  # type: ignore[return-value]

    async def get_profile_icons(
        self, version: str | None = None, locale: str | None = None
    ) -> dict:
        """
        Get profile icon data.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Profile icon data dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/profileicon.json")  # type: ignore[return-value]

    async def get_languages(self) -> list[str]:
        """
        Get list of available languages.

        Returns:
            List of language codes (e.g., ["en_US", "ko_KR", ...])
        """
        return await self.get("/cdn/languages.json")  # type: ignore[return-value]

    async def get_maps(self, version: str | None = None, locale: str | None = None) -> dict:
        """
        Get map data.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Map data dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/map.json")  # type: ignore[return-value]

    async def get_mission_assets(
        self, version: str | None = None, locale: str | None = None
    ) -> dict:
        """
        Get mission assets data.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Mission assets dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/mission-assets.json")  # type: ignore[return-value]

    async def get_stickers(self, version: str | None = None, locale: str | None = None) -> dict:
        """
        Get sticker/emote data.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Sticker data dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/sticker.json")  # type: ignore[return-value]

    async def get_language_strings(
        self, version: str | None = None, locale: str | None = None
    ) -> dict:
        """
        Get language/translation strings.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Language strings dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/language.json")  # type: ignore[return-value]

    async def get_champions_full(
        self, version: str | None = None, locale: str | None = None
    ) -> dict:
        """
        Get complete champion data in a single file.

        This endpoint provides all champion data including full details in one request.

        Args:
            version: Game version (defaults to provider version)
            locale: Language locale (defaults to provider locale)

        Returns:
            Complete champion data dictionary
        """
        v = await self._resolve_version(version or self.version)
        loc = locale or self.locale
        return await self.get(f"/cdn/{v}/data/{loc}/championFull.json")  # type: ignore[return-value]

    def get_champion_image_url(self, champion_id: str, version: str | None = None) -> str:
        """
        Get URL for champion loading screen image.

        Args:
            champion_id: Champion ID (e.g., "Ahri")
            version: Game version (defaults to provider version)

        Returns:
            Image URL

        Note: For "latest" version, this URL may not work until version resolution.
              Consider using async methods with version resolution when possible.
        """
        v = version or self.version
        if v == "latest":
            # Fallback to a recent version for synchronous use
            # This is a limitation since we can't resolve asynchronously
            v = "15.22.1"
        return f"{self.base_url}/cdn/{v}/img/champion/{champion_id}.png"

    def get_champion_splash_url(self, champion_id: str, skin_num: int = 0) -> str:
        """
        Get URL for champion splash art.

        Args:
            champion_id: Champion ID (e.g., "Ahri")
            skin_num: Skin number (0 for default)

        Returns:
            Image URL
        """
        return f"{self.base_url}/cdn/img/champion/splash/{champion_id}_{skin_num}.jpg"

    def get_item_image_url(self, item_id: str, version: str | None = None) -> str:
        """
        Get URL for item image.

        Args:
            item_id: Item ID (e.g., "3089")
            version: Game version (defaults to provider version)

        Returns:
            Image URL

        Note: For "latest" version, this URL may not work until version resolution.
              Consider using async methods with version resolution when possible.
        """
        v = version or self.version
        if v == "latest":
            # Fallback to a recent version for synchronous use
            v = "15.22.1"
        return f"{self.base_url}/cdn/{v}/img/item/{item_id}.png"

    def get_profile_icon_url(self, icon_id: int, version: str | None = None) -> str:
        """
        Get URL for profile icon image.

        Args:
            icon_id: Profile icon ID
            version: Game version (defaults to provider version)

        Returns:
            Image URL

        Note: For "latest" version, this URL may not work until version resolution.
              Consider using async methods with version resolution when possible.
        """
        v = version or self.version
        if v == "latest":
            # Fallback to a recent version for synchronous use
            v = "15.22.1"
        return f"{self.base_url}/cdn/{v}/img/profileicon/{icon_id}.png"
