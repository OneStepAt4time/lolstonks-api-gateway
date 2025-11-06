"""
Community Dragon provider implementation.

Provides access to enhanced static data and assets from the community-driven
data repository, including high-quality images, TFT data, and more.
"""

from typing import Any

import httpx
from loguru import logger

from app.config import settings
from app.providers.base import BaseProvider, ProviderCapability, ProviderType


class CommunityDragonProvider(BaseProvider):
    """
    Provider for Community Dragon data repository.

    Community Dragon provides enhanced static data including:
    - High-quality champion data and assets
    - Skin information with chromas
    - TFT (Teamfight Tactics) data
    - Augments and traits
    - Champion voice lines and quotes
    - Loot and hextech crafting data
    - Mission and quest data

    No authentication required. Community-maintained repository.

    Repository: https://github.com/CommunityDragon/
    API Base: https://raw.communitydragon.org
    """

    def __init__(self, version: str = "latest"):
        """
        Initialize Community Dragon provider.

        Args:
            version: Data version (e.g., "latest", "13.24", or specific patch)
        """
        super().__init__(name="Community Dragon", base_url="https://raw.communitydragon.org")

        self.version = version
        self.client = httpx.AsyncClient(
            timeout=settings.riot_request_timeout,
            follow_redirects=True,
        )

        logger.info(f"Initialized {self.name} provider [version={version}]")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.COMMUNITY_DRAGON

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
        Fetch data from Community Dragon.

        Args:
            path: API path (e.g., "/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions.json")
            params: Query parameters
            headers: Additional HTTP headers

        Returns:
            Response data (JSON parsed)

        Raises:
            httpx.HTTPStatusError: On HTTP errors
            httpx.RequestError: On network errors
        """
        url = f"{self.base_url}{path}"

        logger.debug(f"CommunityDragonProvider: GET {path}")

        response = await self.client.get(
            url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    async def health_check(self) -> bool:
        """
        Check Community Dragon health.

        Returns:
            True if service is accessible
        """
        try:
            # Try to fetch champion summary
            await self.get(
                f"/{self.version}/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
            )
            logger.info(f"{self.name} health check: OK")
            return True
        except Exception as e:
            logger.error(f"{self.name} health check failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info(f"{self.name} provider closed")

    # Helper methods for common Community Dragon endpoints

    async def get_champions(self, version: str | None = None) -> list[dict]:
        """
        Get all champion data.

        Note: champions.json endpoint doesn't exist in Community Dragon.
        Use champion-summary.json instead which provides similar lightweight data.
        For detailed champion data, use get_champion() for individual champions.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of champion data dictionaries (from champion-summary)
        """
        v = version or self.version
        return await self.get_champion_summary(version=v)

    async def get_champion_summary(self, version: str | None = None) -> list[dict]:
        """
        Get champion summary (lightweight version).

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of champion summaries
        """
        v = version or self.version
        return await self.get(
            f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
        )  # type: ignore[return-value]

    async def get_champion(self, champion_id: int, version: str | None = None) -> dict:
        """
        Get detailed data for a specific champion.

        Args:
            champion_id: Champion ID (numeric, e.g., 103 for Ahri)
            version: Data version (defaults to provider version)

        Returns:
            Champion detail data
        """
        v = version or self.version
        return await self.get(
            f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/champions/{champion_id}.json"
        )  # type: ignore[return-value]

    async def get_skins(self, version: str | None = None) -> list[dict]:
        """
        Get all skin data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of skin data dictionaries
        """
        v = version or self.version
        return await self.get(f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/skins.json")  # type: ignore[return-value]

    async def get_skin(self, skin_id: int, version: str | None = None) -> dict:
        """
        Get detailed data for a specific skin.

        Args:
            skin_id: Skin ID (numeric)
            version: Data version (defaults to provider version)

        Returns:
            Skin detail data
        """
        v = version or self.version
        return await self.get(
            f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/skins/{skin_id}.json"
        )  # type: ignore[return-value]

    async def get_items(self, version: str | None = None) -> list[dict]:
        """
        Get all item data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of item data dictionaries
        """
        v = version or self.version
        return await self.get(f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/items.json")  # type: ignore[return-value]

    async def get_perks(self, version: str | None = None) -> list[dict]:
        """
        Get all perk/rune data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of perk data dictionaries
        """
        v = version or self.version
        return await self.get(f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/perks.json")  # type: ignore[return-value]

    async def get_summoner_spells(self, version: str | None = None) -> list[dict]:
        """
        Get all summoner spell data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of summoner spell data dictionaries
        """
        v = version or self.version
        return await self.get(
            f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells.json"
        )  # type: ignore[return-value]

    # TFT-specific methods

    async def get_tft_champions(self, version: str | None = None) -> list[dict]:
        """
        Get TFT champion data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of TFT champion data
        """
        v = version or self.version
        return await self.get(f"/{v}/cdragon/tft/en_us.json")  # type: ignore[return-value]

    async def get_tft_items(self, version: str | None = None) -> list[dict]:
        """
        Get TFT item data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of TFT item data
        """
        v = version or self.version
        data = await self.get(f"/{v}/cdragon/tft/en_us.json")

        # Handle case where data might be a list instead of dict
        if isinstance(data, list):
            return []

        items = data.get("items", [])
        return items if isinstance(items, list) else []

    async def get_tft_traits(self, version: str | None = None) -> list[dict]:
        """
        Get TFT trait data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of TFT trait data
        """
        v = version or self.version
        data = await self.get(f"/{v}/cdragon/tft/en_us.json")

        # Handle case where data might be a list instead of dict
        if isinstance(data, list):
            return []

        traits = data.get("traits", [])
        return traits if isinstance(traits, list) else []

    async def get_tft_augments(self, version: str | None = None) -> list[dict]:
        """
        Get TFT augment data.

        Note: tftaugments.json endpoint doesn't exist in Community Dragon.
        Augments are embedded within the main TFT data file instead.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of TFT augment data
        """
        v = version or self.version
        data = await self.get(f"/{v}/cdragon/tft/en_us.json")

        # Handle case where data might be a list instead of dict
        if isinstance(data, list):
            return []

        # Extract augment items from the TFT data
        # Filter items that have "Augment" in their API name or are marked as augments
        all_items = data.get("items", [])
        augments = []

        for item in all_items:
            api_name = item.get("apiName", "")
            if "Augment" in api_name or "augment" in api_name.lower():
                augments.append(item)

        return augments

    async def get_tft_tacticians(self, version: str | None = None) -> list[dict]:
        """
        Get TFT tactician (Little Legend) data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of TFT tactician data
        """
        v = version or self.version
        return await self.get(
            f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/companions.json"
        )  # type: ignore[return-value]

    # Additional data methods

    async def get_chromas(self, version: str | None = None) -> list[dict]:
        """
        Get all chroma data.

        Note: chromas.json doesn't exist in Community Dragon.
        Chroma data is embedded within skins.json as skin variants.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of chroma data dictionaries (extracted from skins)
        """
        v = version or self.version
        # Get all skins and extract chroma data
        skins = await self.get(f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/skins.json")

        # Extract chromas from skins data
        chromas = []
        if isinstance(skins, list):
            for skin in skins:
                if isinstance(skin, dict) and skin.get("chromas"):
                    chromas.extend(skin["chromas"])

        return chromas

    async def get_ward_skins(self, version: str | None = None) -> list[dict]:
        """
        Get ward skin data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of ward skin data dictionaries
        """
        v = version or self.version
        return await self.get(
            f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/ward-skins.json"
        )  # type: ignore[return-value]

    async def get_missions(self, version: str | None = None) -> list[dict]:
        """
        Get mission/quest data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of mission data dictionaries
        """
        v = version or self.version
        return await self.get(
            f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/mission-assets.json"
        )  # type: ignore[return-value]

    async def get_champion_choices(self, version: str | None = None) -> list[dict]:
        """
        Get champion select choice data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of champion choice data
        """
        v = version or self.version
        return await self.get(
            f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/champion-choices.json"
        )  # type: ignore[return-value]

    async def get_universes(self, version: str | None = None) -> list[dict]:
        """
        Get lore universe data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of universe/lore data
        """
        v = version or self.version
        return await self.get(f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/universes.json")  # type: ignore[return-value]

    async def get_loot(self, version: str | None = None) -> list[dict]:
        """
        Get loot/hextech crafting data.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of loot data dictionaries
        """
        v = version or self.version
        return await self.get(f"/{v}/plugins/rcp-be-lol-game-data/global/default/v1/loot.json")  # type: ignore[return-value]

    # Asset URL helpers

    def get_champion_icon_url(self, champion_id: int, version: str | None = None) -> str:
        """
        Get URL for champion icon/square image.

        Args:
            champion_id: Champion ID (numeric)
            version: Data version (defaults to provider version)

        Returns:
            Image URL
        """
        v = version or self.version
        return f"{self.base_url}/{v}/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{champion_id}.png"

    def get_champion_splash_url(
        self, champion_id: int, skin_id: int = 0, version: str | None = None
    ) -> str:
        """
        Get URL for champion splash art.

        Note: Splash art paths are not directly accessible by ID.
        You need to fetch skins.json to get actual splash paths.
        This method returns a placeholder - use get_skins() to get real splash paths.

        Args:
            champion_id: Champion ID (numeric)
            skin_id: Skin ID (0 for default)
            version: Data version (defaults to provider version)

        Returns:
            Placeholder URL (actual paths come from skins.json)
        """
        v = version or self.version
        # This is a fallback - actual splash paths come from skins.json data
        return f"{self.base_url}/{v}/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/{champion_id}/{skin_id}.jpg"

    def get_item_icon_url(self, item_id: int, version: str | None = None) -> str:
        """
        Get URL for item icon.

        Note: Item icons are not directly accessible by ID.
        You need to fetch items.json to get actual icon paths.
        This method returns a placeholder - use get_items() to get real icon paths.

        Args:
            item_id: Item ID (numeric)
            version: Data version (defaults to provider version)

        Returns:
            Placeholder URL (actual paths come from items.json)
        """
        v = version or self.version
        # This is a fallback - actual icon paths come from items.json data
        return f"{self.base_url}/{v}/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/{item_id}.png"

    def get_perk_icon_url(self, perk_id: int, version: str | None = None) -> str:
        """
        Get URL for perk/rune icon.

        Args:
            perk_id: Perk ID (numeric)
            version: Data version (defaults to provider version)

        Returns:
            Image URL
        """
        v = version or self.version
        return f"{self.base_url}/{v}/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/styles/{perk_id}.png"

    # Enhanced asset URL methods that extract actual paths from data

    async def get_item_data_with_icons(self, version: str | None = None) -> list[dict]:
        """
        Get item data with full icon URLs resolved.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            List of item data with resolved icon URLs
        """
        items = await self.get_items(version)
        v = version or self.version

        for item in items:
            icon_path = item.get("iconPath", "")
            if icon_path:
                # Convert relative path to full URL
                item["fullIconUrl"] = f"{self.base_url}/{v}{icon_path}"
            else:
                # Fallback to placeholder
                item_id = item.get("id", 0)
                item["fullIconUrl"] = self.get_item_icon_url(item_id, v)

        return items

    async def get_skin_data_with_splashes(self, version: str | None = None) -> dict:
        """
        Get skin data with full splash URLs resolved.

        Args:
            version: Data version (defaults to provider version)

        Returns:
            Skin data dictionary with resolved splash URLs
        """
        skins = await self.get_skins(version)
        v = version or self.version

        for skin_id, skin in enumerate(skins):
            splash_path = skin.get("splashPath", "")
            if splash_path:
                # Convert relative path to full URL
                skin["fullSplashUrl"] = f"{self.base_url}/{v}{splash_path}"
            else:
                # Fallback to placeholder
                skin["fullSplashUrl"] = self.get_champion_splash_url(skin_id, 0, v)

        return {"version": v, "skins": skins}

    def resolve_asset_url(self, asset_path: str, version: str | None = None) -> str:
        """
        Resolve any asset path from Community Dragon data to full URL.

        Args:
            asset_path: Relative asset path from data (e.g., "/lol-game-data/assets/v1/champion-icons/1.png")
            version: Data version (defaults to provider version)

        Returns:
            Full URL to the asset
        """
        v = version or self.version
        return f"{self.base_url}/{v}{asset_path}"
