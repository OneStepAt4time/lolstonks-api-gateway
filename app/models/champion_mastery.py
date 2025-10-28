"""CHAMPION-MASTERY-V4 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#champion-mastery-v4
"""

from typing import Annotated

from pydantic import Field

from app.models.common import HasChampionId, HasPuuid, RegionQuery


class ChampionMasteryByPuuidParams(HasPuuid):
    """Path parameters for GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}."""

    pass


class ChampionMasteryByPuuidQuery(RegionQuery):
    """Query parameters for GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}."""

    pass


class ChampionMasteryByPuuidByChampionParams(HasPuuid, HasChampionId):
    """Path parameters for GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{championId}."""

    pass


class ChampionMasteryByPuuidByChampionQuery(RegionQuery):
    """Query parameters for GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{championId}."""

    pass


class TopChampionMasteriesParams(HasPuuid):
    """Path parameters for GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top."""

    pass


class TopChampionMasteriesQuery(RegionQuery):
    """Query parameters for GET /lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top."""

    count: Annotated[
        int,
        Field(
            default=3,
            ge=1,
            le=20,
            description="Number of top champions to return (1-20)"
        )
    ] = 3


class MasteryScoreParams(HasPuuid):
    """Path parameters for GET /lol/champion-mastery/v4/scores/by-puuid/{puuid}."""

    pass


class MasteryScoreQuery(RegionQuery):
    """Query parameters for GET /lol/champion-mastery/v4/scores/by-puuid/{puuid}."""

    pass
