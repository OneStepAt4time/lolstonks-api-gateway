"""
Community Dragon champions router.

Provides endpoints for accessing enhanced champion data and assets.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.community_dragon import ChampionIdParams
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


@router.get("/champions", summary="Get all champions (enhanced)")
async def get_champions(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get enhanced data for all champions from Community Dragon.

    Provides more detailed champion information than Data Dragon including:
    - Enhanced champion stats
    - Detailed ability information
    - Skin data with chromas
    - Voice lines and quotes
    - Lore and biography

    Example response:
    ```json
    [
      {
        "id": 1,
        "name": "Annie",
        "alias": "Annie",
        "title": "the Dark Child",
        "roles": ["Mage"],
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:champions:{version}",
        resource_name="Champions (Community Dragon)",
        fetch_fn=lambda: provider.get_champions(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/champions/summary", summary="Get champion summary")
async def get_champion_summary(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get lightweight champion summary data.

    Returns basic champion information for all champions in a more compact format.

    Example response:
    ```json
    [
      {
        "id": 1,
        "name": "Annie",
        "alias": "Annie",
        "squarePortraitPath": "/path/to/icon.png",
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:champion_summary:{version}",
        resource_name="Champion Summary",
        fetch_fn=lambda: provider.get_champion_summary(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/champions/{champion_id}", summary="Get champion details (enhanced)")
async def get_champion(
    params: Annotated[ChampionIdParams, Depends()],
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get detailed enhanced data for a specific champion.

    Provides comprehensive champion information including:
    - Full ability descriptions with scaling
    - All skin variants with chromas
    - Voice lines and interactions
    - Detailed lore and biography
    - Splash art and asset paths

    Args:
        champion_id: Numeric champion ID (e.g., 103 for Ahri)

    Example response:
    ```json
    {
      "id": 103,
      "name": "Ahri",
      "alias": "Ahri",
      "title": "the Nine-Tailed Fox",
      "skins": [...],
      "spells": [...],
      ...
    }
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:champion:{params.champion_id}:{version}",
        resource_name="Champion Details",
        fetch_fn=lambda: provider.get_champion(champion_id=params.champion_id, version=version),
        ttl=settings.cache_ttl_ddragon,
        context={
            "champion_id": params.champion_id,
            "version": version,
            "source": "community_dragon",
        },
        force_refresh=query.force,
    )


@router.get("/items", summary="Get all items (enhanced)")
async def get_items(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get enhanced item data from Community Dragon.

    Provides detailed item information including:
    - Item stats and effects
    - Build paths
    - High-quality item icons
    - Item categories and tags

    Example response:
    ```json
    [
      {
        "id": 1001,
        "name": "Boots",
        "description": "...",
        "price": 300,
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:items:{version}",
        resource_name="Items (Community Dragon)",
        fetch_fn=lambda: provider.get_items(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/perks", summary="Get all perks/runes")
async def get_perks(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get perk/rune data from Community Dragon.

    Provides detailed rune information with enhanced descriptions and tooltips.

    Example response:
    ```json
    [
      {
        "id": 8005,
        "name": "Press the Attack",
        "iconPath": "/path/to/icon.png",
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:perks:{version}",
        resource_name="Perks",
        fetch_fn=lambda: provider.get_perks(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )


@router.get("/summoner-spells", summary="Get summoner spells")
async def get_summoner_spells(
    query: Annotated[CommunityDragonQuery, Depends()],
):
    """
    Get summoner spell data from Community Dragon.

    Provides detailed summoner spell information.

    Example response:
    ```json
    [
      {
        "id": 4,
        "name": "Flash",
        "description": "...",
        "summonerLevel": 7,
        ...
      },
      ...
    ]
    ```
    """
    provider: CommunityDragonProvider = get_provider(ProviderType.COMMUNITY_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version

    return await fetch_with_cache(
        cache_key=f"cdragon:summoner_spells:{version}",
        resource_name="Summoner Spells (Community Dragon)",
        fetch_fn=lambda: provider.get_summoner_spells(version=version),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "source": "community_dragon"},
        force_refresh=query.force,
    )
