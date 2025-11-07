"""
Data Dragon items router.

Provides endpoints for accessing item, rune, and summoner spell data.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.providers.base import ProviderType
from app.providers.data_dragon import DataDragonProvider
from app.providers.registry import get_provider

router = APIRouter(prefix="/ddragon", tags=["data-dragon"])


class StaticDataQuery(BaseModel):
    """Query parameters for static data endpoints."""

    version: Annotated[
        str,
        Field(
            default="latest",
            description="Game version (e.g., '13.24.1' or 'latest')",
        ),
    ]
    locale: Annotated[
        str,
        Field(
            default="en_US",
            description="Language locale (e.g., 'en_US', 'ko_KR')",
        ),
    ]
    force: Annotated[
        bool,
        Field(default=False, description="Force refresh from CDN"),
    ]


@router.get("/items", summary="Get all items")
async def get_items(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get data for all items.

    Returns item information including:
    - Item name and description
    - Stats and gold cost
    - Build path (from/into items)
    - Shop categories

    Example response:
    ```json
    {
      "type": "item",
      "version": "13.24.1",
      "data": {
        "1001": {
          "name": "Boots",
          "description": "...",
          "gold": {"base": 300, "total": 300},
          "stats": {...},
          ...
        },
        ...
      }
    }
    ```
    """
    provider: DataDragonProvider = get_provider(ProviderType.DATA_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version
    locale = query.locale

    return await fetch_with_cache(
        cache_key=f"ddragon:items:{version}:{locale}",
        resource_name="Items",
        fetch_fn=lambda: provider.get_items(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )


@router.get("/runes", summary="Get all runes")
async def get_runes(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get data for all runes (Runes Reforged).

    Returns rune tree information including:
    - Rune paths (Precision, Domination, etc.)
    - Keystone and secondary runes
    - Rune descriptions and effects

    Example response:
    ```json
    [
      {
        "id": 8000,
        "key": "Precision",
        "icon": "...",
        "name": "Precision",
        "slots": [
          {
            "runes": [
              {
                "id": 8005,
                "key": "PressTheAttack",
                "name": "Press the Attack",
                ...
              },
              ...
            ]
          }
        ]
      },
      ...
    ]
    ```
    """
    provider: DataDragonProvider = get_provider(ProviderType.DATA_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version
    locale = query.locale

    return await fetch_with_cache(
        cache_key=f"ddragon:runes:{version}:{locale}",
        resource_name="Runes",
        fetch_fn=lambda: provider.get_runes(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )


@router.get("/summoner-spells", summary="Get all summoner spells")
async def get_summoner_spells(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get data for all summoner spells.

    Returns summoner spell information including:
    - Spell name and description
    - Cooldown and range
    - Spell effects

    Example response:
    ```json
    {
      "type": "summoner",
      "version": "13.24.1",
      "data": {
        "SummonerFlash": {
          "id": "SummonerFlash",
          "name": "Flash",
          "description": "...",
          "cooldown": [300],
          ...
        },
        ...
      }
    }
    ```
    """
    provider: DataDragonProvider = get_provider(ProviderType.DATA_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version
    locale = query.locale

    return await fetch_with_cache(
        cache_key=f"ddragon:summoner_spells:{version}:{locale}",
        resource_name="Summoner Spells",
        fetch_fn=lambda: provider.get_summoner_spells(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )


@router.get("/profile-icons", summary="Get all profile icons")
async def get_profile_icons(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get data for all profile icons.

    Returns profile icon metadata.

    Example response:
    ```json
    {
      "type": "profileicon",
      "version": "13.24.1",
      "data": {
        "1": {
          "id": 1,
          "image": {...}
        },
        ...
      }
    }
    ```
    """
    provider: DataDragonProvider = get_provider(ProviderType.DATA_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version
    locale = query.locale

    return await fetch_with_cache(
        cache_key=f"ddragon:profile_icons:{version}:{locale}",
        resource_name="Profile Icons",
        fetch_fn=lambda: provider.get_profile_icons(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )
