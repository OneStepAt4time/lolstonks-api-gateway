"""
Data Dragon router package.

Provides endpoints for accessing Riot's static game data via Data Dragon CDN.
"""

from app.routers.ddragon import additional
from app.routers.ddragon import champions
from app.routers.ddragon import items
from app.routers.ddragon import versions

__all__ = [
    "additional",
    "champions",
    "items",
    "versions",
]
