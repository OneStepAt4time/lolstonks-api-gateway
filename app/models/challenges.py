"""CHALLENGES-V1 API input models.

Riot Developer Portal API Reference:
https://developer.riotgames.com/apis#lol-challenges-v1
"""

from typing import Annotated, Optional

from pydantic import Field

from app.models.common import EnumBaseModel, HasChallengeId, HasPuuid, RegionQuery, Tier


class AllChallengesConfigQuery(RegionQuery):
    """Query parameters for GET /lol/challenges/v1/challenges/config."""

    pass


class ChallengeConfigParams(HasChallengeId):
    """Path parameters for GET /lol/challenges/v1/challenges/{challengeId}/config."""

    pass


class ChallengeConfigQuery(RegionQuery):
    """Query parameters for GET /lol/challenges/v1/challenges/{challengeId}/config."""

    pass


class ChallengeLeaderboardParams(EnumBaseModel, HasChallengeId):
    """Path parameters for GET /lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}.

    Note: Leaderboards are only available for top tiers (MASTER, GRANDMASTER, CHALLENGER).
    """

    level: Annotated[
        Tier,
        Field(description="Challenge leaderboard tier (MASTER, GRANDMASTER, or CHALLENGER only)"),
    ]


class ChallengeLeaderboardQuery(RegionQuery):
    """Query parameters for GET /lol/challenges/v1/challenges/{challengeId}/leaderboards/by-level/{level}."""

    limit: Annotated[
        Optional[int],
        Field(default=None, ge=1, description="Limit the number of results returned (optional)"),
    ] = None


class ChallengePercentilesParams(HasChallengeId):
    """Path parameters for GET /lol/challenges/v1/challenges/{challengeId}/percentiles."""

    pass


class ChallengePercentilesQuery(RegionQuery):
    """Query parameters for GET /lol/challenges/v1/challenges/{challengeId}/percentiles."""

    pass


class PlayerChallengesParams(HasPuuid):
    """Path parameters for GET /lol/challenges/v1/player-data/{puuid}."""

    pass


class PlayerChallengesQuery(RegionQuery):
    """Query parameters for GET /lol/challenges/v1/player-data/{puuid}."""

    pass
