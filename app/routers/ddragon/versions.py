"""
Data Dragon versions router.

Provides endpoints for accessing game version and language information.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.data_dragon import RealmRegionParams
from app.providers.base import ProviderType
from app.providers.registry import get_provider

router = APIRouter(prefix="/ddragon", tags=["data-dragon"])


class VersionQuery(BaseModel):
    """Query parameters for version endpoints."""

    force: Annotated[
        bool,
        Field(default=False, description="Force refresh from CDN, bypassing cache"),
    ]


@router.get("/versions", summary="Get available game versions")
async def get_versions(
    query: Annotated[VersionQuery, Depends()],
):
    """
    Get list of all available League of Legends game versions.

    Returns versions in descending order (newest first).

    Example response:
    ```json
    ["13.24.1", "13.23.1", "13.22.1", ...]
    ```
    """
    provider = get_provider(ProviderType.DATA_DRAGON)

    return await fetch_with_cache(
        cache_key="ddragon:versions",
        resource_name="Versions",
        fetch_fn=lambda: provider.get("/api/versions.json"),
        ttl=settings.cache_ttl_ddragon,
        context={"endpoint": "versions"},
        force_refresh=query.force,
    )


@router.get("/languages", summary="Get available languages")
async def get_languages(
    query: Annotated[VersionQuery, Depends()],
):
    """
    Get list of all available language codes.

    Example response:
    ```json
    ["en_US", "ko_KR", "ja_JP", "es_ES", ...]
    ```
    """
    provider = get_provider(ProviderType.DATA_DRAGON)

    return await fetch_with_cache(
        cache_key="ddragon:languages",
        resource_name="Languages",
        fetch_fn=lambda: provider.get("/cdn/languages.json"),
        ttl=settings.cache_ttl_ddragon,
        context={"endpoint": "languages"},
        force_refresh=query.force,
    )


@router.get("/realms/{region}", summary="Get realm data for region")
async def get_realm(
    params: Annotated[RealmRegionParams, Depends()],
    query: Annotated[VersionQuery, Depends()],
):
    """
    Get realm data for a specific region.

    Realm data includes current version, CDN URLs, and other region-specific info.

    Args:
        params: Path parameters including region code (e.g., "na", "euw", "kr")
        query: Query parameters for cache control

    Example response:
    ```json
    {
      "n": {
        "champion": "13.24.1",
        "item": "13.24.1",
        ...
      },
      "v": "13.24.1",
      "l": "en_US",
      "cdn": "https://ddragon.leagueoflegends.com/cdn",
      ...
    }
    ```
    """
    provider = get_provider(ProviderType.DATA_DRAGON)

    return await fetch_with_cache(
        cache_key=f"ddragon:realm:{params.region}",
        resource_name="Realm",
        fetch_fn=lambda: provider.get(f"/realms/{params.region}.json"),
        ttl=settings.cache_ttl_ddragon,
        context={"endpoint": "realm", "region": params.region},
        force_refresh=query.force,
    )
