"""SUMMONER-V4 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#summoner-v4
"""

from typing import Annotated

from pydantic import BaseModel, Field

from app.models.common import HasEncryptedPuuid, HasEncryptedSummonerId, RegionQuery


class SummonerByNameParams(BaseModel):
    """Path parameters for GET /lol/summoner/v4/summoners/by-name/{summonerName}."""

    summonerName: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Summoner name (URL encoded)"
        )
    ]


class SummonerByNameQuery(RegionQuery):
    """Query parameters for GET /lol/summoner/v4/summoners/by-name/{summonerName}."""

    pass


class SummonerByPuuidParams(HasEncryptedPuuid):
    """Path parameters for GET /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}."""

    pass


class SummonerByPuuidQuery(RegionQuery):
    """Query parameters for GET /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}."""

    pass


class SummonerByIdParams(HasEncryptedSummonerId):
    """Path parameters for GET /lol/summoner/v4/summoners/{encryptedSummonerId}."""

    pass


class SummonerByIdQuery(RegionQuery):
    """Query parameters for GET /lol/summoner/v4/summoners/{encryptedSummonerId}."""

    pass
