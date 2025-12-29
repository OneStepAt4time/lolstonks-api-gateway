"""
Community Dragon router package.

Provides endpoints for accessing enhanced static data and assets from
the community-driven data repository.
"""

from app.routers.cdragon import additional
from app.routers.cdragon import champions
from app.routers.cdragon import skins
from app.routers.cdragon import tft

__all__ = [
    "additional",
    "champions",
    "skins",
    "tft",
]
