"""
Provider abstraction layer for API Gateway.

Supports multiple API providers:
- Riot API (Developer Portal)
- Data Dragon (Static CDN)
- Community Dragon (Enhanced static data)
"""

from app.providers.base import BaseProvider, ProviderType
from app.providers.registry import ProviderRegistry, get_provider

__all__ = [
    "BaseProvider",
    "ProviderType",
    "ProviderRegistry",
    "get_provider",
]
