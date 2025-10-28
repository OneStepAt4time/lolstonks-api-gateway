"""ACCOUNT-V1 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#account-v1
"""

from typing import Annotated

from pydantic import BaseModel, Field

from app.models.common import HasPuuid, PlatformRegionQuery


class AccountByPuuidParams(HasPuuid):
    """Path parameters for GET /riot/account/v1/accounts/by-puuid/{puuid}."""

    pass


class AccountByPuuidQuery(PlatformRegionQuery):
    """Query parameters for GET /riot/account/v1/accounts/by-puuid/{puuid}."""

    pass


class AccountByRiotIdParams(BaseModel):
    """Path parameters for GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}."""

    gameName: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Riot ID game name (before the #)"
        )
    ]
    tagLine: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Riot ID tag line (after the #)"
        )
    ]


class AccountByRiotIdQuery(PlatformRegionQuery):
    """Query parameters for GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}."""

    pass


class ActiveShardParams(HasPuuid):
    """Path parameters for GET /riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}."""

    game: Annotated[
        str,
        Field(
            pattern=r"^(val|lor)$",
            description="Game identifier (val for Valorant, lor for Legends of Runeterra)"
        )
    ]


class ActiveShardQuery(PlatformRegionQuery):
    """Query parameters for GET /riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}."""

    pass
