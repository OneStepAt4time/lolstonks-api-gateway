"""
Community Dragon router package.

Provides endpoints for accessing enhanced static data and assets from
the community-driven data repository.
"""

from app.routers.cdragon.additional import router as additional_router
from app.routers.cdragon.champions import router as champions_router
from app.routers.cdragon.skins import router as skins_router
from app.routers.cdragon.tft import router as tft_router

__all__ = [
    "champions_router",
    "skins_router",
    "tft_router",
    "additional_router",
]
