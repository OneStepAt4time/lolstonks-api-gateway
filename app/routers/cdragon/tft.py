"""
Community Dragon TFT router.

Provides endpoints for accessing Teamfight Tactics data.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.providers.base import ProviderType
from app.providers.community_dragon import CommunityDragonProvider
from app.providers.registry import get_provider

router = APIRouter(prefix="/cdragon/tft", tags=["community-dragon", "tft"])


class TFTQuery(BaseModel):
    """Query parameters for TFT endpoints."""

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


@router.get("/champions", summary="Get TFT champions")
async def get_tft_champions(
    query: Annotated[TFTQuery, Depends()],
):
    """
    Get all TFT champion data from Community Dragon.

    Provides TFT-specific champion information including:
    - Champion stats (HP, armor, attack damage, etc.)
    - Origin and class traits
    - Ability information
    - Cost and rarity

    Example response:
    ```json
    [
      {
        "characterName": "TFT4_Ahri",
        "displayName": "Ahri",
        "cost": 4,
        "traits": ["Spirit", "Mage"],
        "ability": {...},
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:tft:champions:{version}",
        resource_name="TFT Champions",
        fetch_fn=lambda: provider.get_tft_champions(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon", "game_mode": "tft"},
        force_refresh=query.force,
    )


@router.get("/items", summary="Get TFT items")
async def get_tft_items(
    query: Annotated[TFTQuery, Depends()],
):
    """
    Get all TFT item data from Community Dragon.

    Provides TFT-specific item information including:
    - Item components
    - Combined items
    - Item effects and stats
    - Item descriptions

    Example response:
    ```json
    [
      {
        "id": 1,
        "name": "B.F. Sword",
        "description": "...",
        "effects": {...},
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:tft:items:{version}",
        resource_name="TFT Items",
        fetch_fn=lambda: provider.get_tft_items(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon", "game_mode": "tft"},
        force_refresh=query.force,
    )


@router.get("/traits", summary="Get TFT traits")
async def get_tft_traits(
    query: Annotated[TFTQuery, Depends()],
):
    """
    Get all TFT trait data from Community Dragon.

    Provides TFT trait (origin/class) information including:
    - Trait name and description
    - Breakpoints and bonuses
    - Champions with this trait
    - Trait effects

    Example response:
    ```json
    [
      {
        "key": "Spirit",
        "name": "Spirit",
        "description": "...",
        "effects": [
          {
            "minUnits": 2,
            "maxUnits": 4,
            "variables": {...}
          },
          ...
        ],
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:tft:traits:{version}",
        resource_name="TFT Traits",
        fetch_fn=lambda: provider.get_tft_traits(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon", "game_mode": "tft"},
        force_refresh=query.force,
    )


@router.get("/augments", summary="Get TFT augments")
async def get_tft_augments(
    query: Annotated[TFTQuery, Depends()],
):
    """
    Get all TFT augment data from Community Dragon.

    Provides TFT augment information including:
    - Augment name and description
    - Tier (Silver, Gold, Prismatic)
    - Effects and stats
    - Associated traits

    Example response:
    ```json
    [
      {
        "id": 1,
        "name": "Cybernetic Implants I",
        "description": "...",
        "tier": 1,
        "effects": {...},
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:tft:augments:{version}",
        resource_name="TFT Augments",
        fetch_fn=lambda: provider.get_tft_augments(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon", "game_mode": "tft"},
        force_refresh=query.force,
    )


@router.get("/tacticians", summary="Get TFT tacticians")
async def get_tft_tacticians(
    query: Annotated[TFTQuery, Depends()],
):
    """
    Get all TFT tactician (Little Legend) data from Community Dragon.

    Provides TFT tactician information including:
    - Tactician name and species
    - Rarity and pricing
    - Evolution stages
    - Visual assets

    Example response:
    ```json
    [
      {
        "id": 1,
        "name": "Silverwing",
        "species": "Silverwing",
        "rarity": 3,
        "upgrades": [...],
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:tft:tacticians:{version}",
        resource_name="TFT Tacticians",
        fetch_fn=lambda: provider.get_tft_tacticians(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon", "game_mode": "tft"},
        force_refresh=query.force,
    )
