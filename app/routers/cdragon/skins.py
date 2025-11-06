"""
Community Dragon skins router.

Provides endpoints for accessing skin data and chroma information.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.community_dragon import SkinIdParams
from app.providers.base import ProviderType
from app.providers.community_dragon import CommunityDragonProvider
from app.providers.registry import get_provider

router = APIRouter(prefix="/cdragon", tags=["community-dragon"])


class SkinsQuery(BaseModel):
    """Query parameters for skins endpoints."""

    version: Annotated[
        str,
        Field(
            default="latest",
            description="Data version (e.g., 'latest', '13.24', or specific patch)",
        ),
    ]
    force: Annotated[
        bool,
        Field(default=False, description="Force refresh from repository"),
    ]


@router.get("/skins", summary="Get all skins")
async def get_skins(
    query: Annotated[SkinsQuery, Depends()],
):
    """
    Get data for all champion skins from Community Dragon.

    Provides comprehensive skin information including:
    - Skin name and description
    - Rarity and pricing
    - Chroma variants
    - Splash art paths
    - Loading screen art
    - In-game assets

    Example response:
    ```json
    [
      {
        "id": 1000,
        "name": "Original Annie",
        "splashPath": "/path/to/splash.jpg",
        "chromas": [...],
        "rarity": "kNoRarity",
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:skins:{version}",
        resource_name="Skins",
        fetch_fn=lambda: provider.get_skins(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/skins/{skin_id}", summary="Get skin details")
async def get_skin(
    params: Annotated[SkinIdParams, Depends()],
    query: Annotated[SkinsQuery, Depends()],
):
    """
    Get detailed data for a specific skin.

    Provides comprehensive information about a single skin including:
    - Full skin metadata
    - All chroma variants
    - Asset paths for splash arts and icons
    - Pricing and availability information
    - Skin line and theme information

    Args:
        skin_id: Numeric skin ID

    Example response:
    ```json
    {
      "id": 103001,
      "name": "Dynasty Ahri",
      "splashPath": "/lol-game-data/assets/...",
      "chromas": [
        {
          "id": 103001001,
          "name": "Obsidian",
          "chromaPath": "/path/to/chroma.png",
          ...
        },
        ...
      ],
      ...
    }
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:skin:{params.skin_id}:{version}",
        resource_name="Skin Details",
        fetch_fn=lambda: provider.get_skin(skin_id=params.skin_id, version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"skin_id": params.skin_id, "version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )
