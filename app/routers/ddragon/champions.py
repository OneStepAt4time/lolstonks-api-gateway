"""
Data Dragon champions router.

Provides endpoints for accessing champion static data.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.cache.helpers import fetch_with_cache
from app.config import settings
from app.models.data_dragon import ChampionIdParams
from app.providers.base import ProviderType
from app.providers.data_dragon import DataDragonProvider
from app.providers.registry import get_provider

router = APIRouter(prefix="/ddragon", tags=["data-dragon"])


class ChampionQuery(BaseModel):
    """Query parameters for champion endpoints."""

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


@router.get("/champions", summary="Get all champions")
async def get_all_champions(
    query: Annotated[ChampionQuery, Depends()],
):
    """
    Get data for all champions.

    Returns basic information for all champions including:
    - Champion ID, key, and name
    - Title and lore
    - Stats (HP, attack damage, armor, etc.)
    - Tags (Fighter, Mage, etc.)
    - Spells and passive

    Args:
        version: Game version (default: "latest")
        locale: Language locale (default: "en_US")
        force: Force refresh from CDN

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
          ...
        },
        ...
      }
    }
    ```
    """
    provider: DataDragonProvider = get_provider(ProviderType.DATA_DRAGON)  # type: ignore

    # The provider now handles version resolution automatically
    version = query.version
    locale = query.locale

    return await fetch_with_cache(
        cache_key=f"ddragon:champions:{version}:{locale}",
        resource_name="Champions",
        fetch_fn=lambda: provider.get_champions_full(version=version, locale=locale),
        ttl=settings.cache_ttl_ddragon,
        context={"version": version, "locale": locale},
        force_refresh=query.force,
    )


@router.get("/champions/{champion_id}", summary="Get champion details")
async def get_champion(
    params: Annotated[ChampionIdParams, Depends()],
    query: Annotated[ChampionQuery, Depends()],
):
    """
    Get detailed data for a specific champion.

    Returns comprehensive information including:
    - All champion stats and stat growth
    - Detailed spell information
    - Passive ability details
    - Skin information
    - Recommended items

    Args:
        champion_id: Champion ID (e.g., "Ahri", "LeeSin")
        version: Game version (default: "latest")
        locale: Language locale (default: "en_US")
        force: Force refresh from CDN

    Example response:
    ```json
    {
      "type": "champion",
      "format": "standAloneComplex",
      "version": "13.24.1",
      "data": {
        "Ahri": {
          "id": "Ahri",
          "key": "103",
          "name": "Ahri",
          "title": "the Nine-Tailed Fox",
          "spells": [...],
          "passive": {...},
          "skins": [...],
          ...
        }
      }
    }
    ```
    """
    provider: DataDragonProvider = get_provider(ProviderType.DATA_DRAGON)  # type: ignore

    # The provider now handles version resolution automatically
    version = query.version
    locale = query.locale

    return await fetch_with_cache(
        cache_key=f"ddragon:champion:{params.champion_id}:{version}:{locale}",
        resource_name="Champion",
        fetch_fn=lambda: provider.get_champion(
            champion_id=params.champion_id, version=version, locale=locale
        ),
        ttl=settings.cache_ttl_ddragon,
        context={"champion_id": params.champion_id, "version": version, "locale": locale},
        force_refresh=query.force,
    )
