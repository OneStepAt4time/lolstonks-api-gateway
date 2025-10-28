"""MATCH-V5 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#match-v5
"""

from typing import Annotated, Optional

from pydantic import Field

from app.models.common import HasMatchId, HasPuuid, PaginationQuery, PlatformRegionQuery


class MatchIdsByPuuidParams(HasPuuid):
    """Path parameters for GET /lol/match/v5/matches/by-puuid/{puuid}/ids."""

    pass


class MatchIdsByPuuidQuery(PlatformRegionQuery, PaginationQuery):
    """Query parameters for GET /lol/match/v5/matches/by-puuid/{puuid}/ids.

    Includes optional filtering parameters for match discovery.
    """

    startTime: Annotated[
        Optional[int],
        Field(
            default=None,
            ge=0,
            description="Epoch timestamp in seconds. Only matches after this time are returned."
        )
    ] = None

    endTime: Annotated[
        Optional[int],
        Field(
            default=None,
            ge=0,
            description="Epoch timestamp in seconds. Only matches before this time are returned."
        )
    ] = None

    queue: Annotated[
        Optional[int],
        Field(
            default=None,
            ge=0,
            description="Queue ID. Only matches from this queue are returned."
        )
    ] = None

    type: Annotated[
        Optional[str],
        Field(
            default=None,
            pattern=r"^(ranked|normal|tourney|tutorial)$",
            description="Match type filter (ranked, normal, tourney, tutorial)"
        )
    ] = None


class MatchParams(HasMatchId):
    """Path parameters for GET /lol/match/v5/matches/{matchId}."""

    pass


class MatchQuery(PlatformRegionQuery):
    """Query parameters for GET /lol/match/v5/matches/{matchId}."""

    force: Annotated[
        bool,
        Field(
            default=False,
            description="Force refresh from Riot API (bypass cache)"
        )
    ] = False


class MatchTimelineParams(HasMatchId):
    """Path parameters for GET /lol/match/v5/matches/{matchId}/timeline."""

    pass


class MatchTimelineQuery(PlatformRegionQuery):
    """Query parameters for GET /lol/match/v5/matches/{matchId}/timeline."""

    pass
