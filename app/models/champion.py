"""CHAMPION-V3 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#champion-v3
"""

from app.models.common import RegionQuery


class ChampionRotationsQuery(RegionQuery):
    """Query parameters for GET /lol/platform/v3/champion-rotations."""

    pass
