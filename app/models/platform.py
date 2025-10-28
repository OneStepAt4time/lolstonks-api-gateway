"""LOL-STATUS-V4 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#lol-status-v4
"""

from app.models.common import RegionQuery


class PlatformStatusQuery(RegionQuery):
    """Query parameters for GET /lol/status/v4/platform-data."""

    pass
