"""LEAGUE-EXP-V4 API input models (Experimental).

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#league-exp-v4

Note: This is an experimental API that provides paginated league entries.
It's similar to LEAGUE-V4 but with different pagination support.
"""

from typing import Annotated, Optional

from pydantic import BaseModel, Field

from app.models.common import Division, QueueType, RegionQuery, Tier


class LeagueExpEntriesParams(BaseModel):
    """Path parameters for GET /lol/league-exp/v4/entries/{queue}/{tier}/{division}."""

    queue: Annotated[
        QueueType,
        Field(description="Queue type")
    ]
    tier: Annotated[
        Tier,
        Field(description="Tier (IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND)")
    ]
    division: Annotated[
        Division,
        Field(description="Division (I, II, III, IV)")
    ]


class LeagueExpEntriesQuery(RegionQuery):
    """Query parameters for GET /lol/league-exp/v4/entries/{queue}/{tier}/{division}."""

    page: Annotated[
        Optional[int],
        Field(
            default=1,
            ge=1,
            description="Page number for pagination (starts at 1)"
        )
    ] = 1
