"""
Community Dragon additional endpoints router.

Provides endpoints for chromas, ward skins, missions, lore, and loot data.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.providers.base import ProviderType
from app.providers.community_dragon import CommunityDragonProvider
from app.providers.registry import get_provider

router = APIRouter(prefix="/cdragon", tags=["community-dragon"])


class CommunityDragonQuery(BaseModel):
    """Query parameters for Community Dragon endpoints."""

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


@router.get("/chromas", summary="Get all chromas")
async def get_chromas(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get all chroma data from Community Dragon.

    Provides detailed chroma information including:
    - Chroma name and ID
    - Associated skin
    - Color variations
    - Pricing and availability
    - Asset paths

    Example response:
    ```json
    [
      {
        "id": 103001001,
        "name": "Dynasty Ahri Obsidian",
        "chromaPath": "...",
        "colors": ["#1a1a1a", "#ff0000"],
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:chromas:{version}",
        resource_name="Chromas",
        fetch_fn=lambda: provider.get_chromas(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/ward-skins", summary="Get all ward skins")
async def get_ward_skins(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get all ward skin data from Community Dragon.

    Provides ward skin information including:
    - Ward name and description
    - Rarity and pricing
    - Visual assets
    - Availability

    Example response:
    ```json
    [
      {
        "id": 1,
        "name": "Poro Ward",
        "description": "...",
        "wardImagePath": "...",
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:ward_skins:{version}",
        resource_name="Ward Skins",
        fetch_fn=lambda: provider.get_ward_skins(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/missions", summary="Get missions/quests")
async def get_missions(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get mission and quest data from Community Dragon.

    Provides mission information including:
    - Mission title and description
    - Objectives and requirements
    - Rewards
    - Event association
    - Start and end times

    Example response:
    ```json
    [
      {
        "id": "mission_1",
        "title": "Welcome to League",
        "description": "...",
        "objectives": [...],
        "rewards": [...],
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:missions:{version}",
        resource_name="Missions",
        fetch_fn=lambda: provider.get_missions(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/champion-choices", summary="Get champion select choices")
async def get_champion_choices(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get champion select choice data from Community Dragon.

    Provides champion selection UI data including:
    - Champion positions
    - Role recommendations
    - Pick/ban phase information

    Example response:
    ```json
    [
      {
        "championId": 103,
        "position": "MIDDLE",
        "roles": ["MAGE", "ASSASSIN"],
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:champion_choices:{version}",
        resource_name="Champion Choices",
        fetch_fn=lambda: provider.get_champion_choices(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/universes", summary="Get lore universes")
async def get_universes(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get lore universe data from Community Dragon.

    Provides universe and lore information including:
    - Universe names and descriptions
    - Associated champions
    - Story lines
    - Skin lines

    Example response:
    ```json
    [
      {
        "id": 1,
        "name": "Runeterra",
        "description": "The main League of Legends universe",
        "champions": [...],
        "skinLines": [...],
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:universes:{version}",
        resource_name="Universes",
        fetch_fn=lambda: provider.get_universes(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/loot", summary="Get loot/crafting data")
async def get_loot(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get loot and hextech crafting data from Community Dragon.

    Provides loot system information including:
    - Loot items and recipes
    - Crafting costs
    - Drop rates
    - Hextech chest contents

    Example response:
    ```json
    [
      {
        "id": "loot_1",
        "name": "Hextech Chest",
        "description": "...",
        "contents": [...],
        "craftingCost": {...},
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:loot:{version}",
        resource_name="Loot",
        fetch_fn=lambda: provider.get_loot(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )
