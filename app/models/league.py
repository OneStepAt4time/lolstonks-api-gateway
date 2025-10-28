"""LEAGUE-V4 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#league-v4
"""

from typing import Annotated, Optional

from pydantic import Field

from app.models.common import (
    Division,
    EnumBaseModel,
    HasEncryptedSummonerId,
    QueueType,
    RegionQuery,
    Tier,
)


class LeagueByQueueParams(EnumBaseModel):
    """Path parameters for challenger/grandmaster/master league endpoints."""

    queue: Annotated[
        QueueType, Field(description="Queue type (RANKED_SOLO_5x5, RANKED_FLEX_SR, RANKED_FLEX_TT)")
    ]


class LeagueByQueueQuery(RegionQuery):
    """Query parameters for challenger/grandmaster/master league endpoints."""

    pass


class LeagueEntriesBySummonerParams(HasEncryptedSummonerId):
    """Path parameters for GET /lol/league/v4/entries/by-summoner/{encryptedSummonerId}."""

    pass


class LeagueEntriesBySummonerQuery(RegionQuery):
    """Query parameters for GET /lol/league/v4/entries/by-summoner/{encryptedSummonerId}."""

    pass


class LeagueEntriesParams(EnumBaseModel):
    """Path parameters for GET /lol/league/v4/entries/{queue}/{tier}/{division}."""

    queue: Annotated[QueueType, Field(description="Queue type")]
    tier: Annotated[
        Tier, Field(description="Tier (IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND)")
    ]
    division: Annotated[Division, Field(description="Division (I, II, III, IV)")]


class LeagueEntriesQuery(RegionQuery):
    """Query parameters for GET /lol/league/v4/entries/{queue}/{tier}/{division}."""

    page: Annotated[
        Optional[int],
        Field(default=1, ge=1, description="Page number for pagination (starts at 1)"),
    ] = 1
