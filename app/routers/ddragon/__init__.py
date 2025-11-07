"""
Data Dragon router package.

Provides endpoints for accessing Riot's static game data via Data Dragon CDN.
"""

from app.routers.ddragon.additional import router as additional_router
from app.routers.ddragon.champions import router as champions_router
from app.routers.ddragon.items import router as items_router
from app.routers.ddragon.versions import router as versions_router

__all__ = [
    "champions_router",
    "items_router",
    "versions_router",
    "additional_router",
]
