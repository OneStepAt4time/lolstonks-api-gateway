"""
Data Dragon additional endpoints router.

Provides endpoints for maps, missions, stickers, language strings, and bulk champion data.
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


@router.get("/maps", summary="Get map data")
async def get_maps(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get map data including Summoner's Rift, ARAM, and other game modes.

    Example response:
    ```json
    {
      "type": "map",
      "version": "13.24.1",
      "data": {
        "11": {
          "mapName": "Summoner's Rift",
          "mapId": 11,
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
        cache_key=f"ddragon:maps:{version}:{locale}",
        resource_name="Maps",
        fetch_fn=lambda: provider.get_maps(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )


@router.get("/mission-assets", summary="Get mission assets")
async def get_mission_assets(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get mission and event assets data.

    Includes data for missions, events, and quest objectives.

    Example response:
    ```json
    {
      "type": "mission-assets",
      "version": "13.24.1",
      "data": {
        "mission_1": {
          "title": "Mission Title",
          "description": "...",
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
        cache_key=f"ddragon:mission_assets:{version}:{locale}",
        resource_name="Mission Assets",
        fetch_fn=lambda: provider.get_mission_assets(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )


@router.get("/stickers", summary="Get stickers/emotes")
async def get_stickers(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get sticker and emote data.

    Example response:
    ```json
    {
      "type": "sticker",
      "version": "13.24.1",
      "data": {
        "sticker_1": {
          "name": "Sticker Name",
          "description": "...",
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
        cache_key=f"ddragon:stickers:{version}:{locale}",
        resource_name="Stickers",
        fetch_fn=lambda: provider.get_stickers(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )


@router.get("/language-strings", summary="Get language/translation strings")
async def get_language_strings(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get language and translation strings for UI elements.

    Example response:
    ```json
    {
      "type": "language",
      "version": "13.24.1",
      "data": {
        "game_ui_champion_select": "Champion Select",
        "game_ui_loading": "Loading...",
        ...
      }
    }
    ```
    """
    provider: DataDragonProvider = get_provider(ProviderType.DATA_DRAGON)  # type: ignore

    version = query.version if query.version != "latest" else provider.version
    locale = query.locale

    return await fetch_with_cache(
        cache_key=f"ddragon:language_strings:{version}:{locale}",
        resource_name="Language Strings",
        fetch_fn=lambda: provider.get_language_strings(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )


@router.get("/champions-full", summary="Get complete champion data (bulk)")
async def get_champions_full(
    query: Annotated[StaticDataQuery, Depends()],
):
    """
    Get complete champion data for ALL champions in a single request.

    This endpoint provides full champion details (including spells, skins, stats, etc.)
    for all champions in one file. Useful for bulk operations and reducing API calls.

    **Note:** This returns significantly more data than `/champions`. Use this when
    you need full details for multiple champions at once.

    Example response:
    ```json
    {
      "type": "champion",
      "format": "standAloneComplex",
      "version": "13.24.1",
      "data": {
        "Aatrox": {
          "id": "Aatrox",
          "key": "266",
          "name": "Aatrox",
          "title": "the Darkin Blade",
          "spells": [
            {
              "id": "AatroxQ",
              "name": "The Darkin Blade",
              "description": "...",
              "cooldown": [14, 12, 10, 8, 6],
              ...
            },
            ...
          ],
          "passive": {...},
          "stats": {...},
          "skins": [...],
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
        cache_key=f"ddragon:champions_full:{version}:{locale}",
        resource_name="Champions (Full)",
        fetch_fn=lambda: provider.get_champions_full(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale, "type": "full"},
        force_refresh=query.force,
    )
