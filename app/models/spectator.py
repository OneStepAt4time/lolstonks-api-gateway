"""SPECTATOR-V5 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#spectator-v5
"""

from app.models.common import HasPuuid, RegionQuery


class ActiveGameParams(HasPuuid):
    """Path parameters for GET /lol/spectator/v5/active-games/by-summoner/{puuid}."""

    pass


class ActiveGameQuery(RegionQuery):
    """Query parameters for GET /lol/spectator/v5/active-games/by-summoner/{puuid}."""

    pass


class FeaturedGamesQuery(RegionQuery):
    """Query parameters for GET /lol/spectator/v5/featured-games."""

    pass
