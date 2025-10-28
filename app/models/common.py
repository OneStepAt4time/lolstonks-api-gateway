"""Common reusable models for API inputs.

These models contain shared parameters used across multiple endpoints.
"""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.config import settings


# Region Enums
class PlatformRegion(str, Enum):
    """Platform regions for regional routing (ACCOUNT, MATCH APIs)."""

    AMERICAS = "americas"
    EUROPE = "europe"
    ASIA = "asia"
    SEA = "sea"


class GameRegion(str, Enum):
    """Game regions for platform-specific endpoints."""

    # Europe
    EUW1 = "euw1"
    EUN1 = "eun1"
    TR1 = "tr1"
    RU = "ru"

    # Americas
    NA1 = "na1"
    BR1 = "br1"
    LA1 = "la1"
    LA2 = "la2"

    # Asia
    KR = "kr"
    JP1 = "jp1"

    # SEA/Oceania
    OC1 = "oc1"
    PH2 = "ph2"
    SG2 = "sg2"
    TH2 = "th2"
    TW2 = "tw2"
    VN2 = "vn2"


class QueueType(str, Enum):
    """Queue types for League of Legends.

    Includes ranked, normal, and special game modes.
    """

    # Ranked Queues
    RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"
    RANKED_FLEX_SR = "RANKED_FLEX_SR"
    RANKED_FLEX_TT = "RANKED_FLEX_TT"
    RANKED_TFT = "RANKED_TFT"
    RANKED_TFT_TURBO = "RANKED_TFT_TURBO"
    RANKED_TFT_DOUBLE_UP = "RANKED_TFT_DOUBLE_UP"


class Tier(str, Enum):
    """League tier/rank levels.

    Used for:
    - Ranked league entries and progression (IRON → CHALLENGER)
    - Challenge progression (all tiers)
    - Challenge leaderboards (MASTER, GRANDMASTER, CHALLENGER only)
    """

    UNRANKED = "UNRANKED"
    IRON = "IRON"
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    EMERALD = "EMERALD"
    DIAMOND = "DIAMOND"
    MASTER = "MASTER"
    GRANDMASTER = "GRANDMASTER"
    CHALLENGER = "CHALLENGER"


class Division(str, Enum):
    """Division within a tier.

    Used for Iron through Diamond (and Emerald) tiers.
    Master, Grandmaster, and Challenger don't use divisions.
    """

    I = "I"
    II = "II"
    III = "III"
    IV = "IV"


# Base Model with enum configuration
class EnumBaseModel(BaseModel):
    """Base model that serializes enums as values."""

    model_config = ConfigDict(use_enum_values=True)


# Base Query Models
class RegionQuery(EnumBaseModel):
    """Standard region query parameter for game-specific endpoints."""

    region: Annotated[
        GameRegion,
        Field(
            default=settings.riot_default_region,
            description="Region code (e.g., euw1, kr, na1)"
        )
    ] = settings.riot_default_region


class PlatformRegionQuery(EnumBaseModel):
    """Regional routing parameter for platform endpoints (ACCOUNT, MATCH)."""

    region: Annotated[
        PlatformRegion,
        Field(
            default=PlatformRegion.AMERICAS,
            description="Regional routing value (americas, europe, asia, sea)"
        )
    ] = PlatformRegion.AMERICAS


class PaginationQuery(BaseModel):
    """Pagination parameters for list endpoints."""

    start: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description="Start index for pagination"
        )
    ] = 0

    count: Annotated[
        int,
        Field(
            default=20,
            ge=1,
            le=100,
            description="Number of items to return (1-100)"
        )
    ] = 20


# Reusable Path Parameter Mixins
# These can be inherited by endpoint-specific models to avoid duplication

class HasPuuid(BaseModel):
    """Mixin for models that include a PUUID path parameter."""

    puuid: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Player UUID"
        )
    ]


class HasEncryptedSummonerId(BaseModel):
    """Mixin for models that include an encrypted summoner ID path parameter."""

    encryptedSummonerId: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Encrypted summoner ID"
        )
    ]


class HasEncryptedPuuid(BaseModel):
    """Mixin for models that include an encrypted PUUID path parameter."""

    encryptedPUUID: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Encrypted Player UUID"
        )
    ]


class HasMatchId(BaseModel):
    """Mixin for models that include a match ID path parameter."""

    matchId: Annotated[
        str,
        Field(
            pattern=r"^[A-Z0-9]+_\d+$",
            description="Match ID (e.g., EUW1_123456789)"
        )
    ]


class HasChampionId(BaseModel):
    """Mixin for models that include a champion ID path parameter."""

    championId: Annotated[
        int,
        Field(
            ge=1,
            description="Champion ID"
        )
    ]


class HasChallengeId(BaseModel):
    """Mixin for models that include a challenge ID path parameter."""

    challengeId: Annotated[
        int,
        Field(
            ge=0,
            description="Challenge ID"
        )
    ]


class HasTeamId(BaseModel):
    """Mixin for models that include a team ID path parameter."""

    teamId: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Team ID"
        )
    ]


class HasTournamentId(BaseModel):
    """Mixin for models that include a tournament ID path parameter."""

    tournamentId: Annotated[
        int,
        Field(
            ge=0,
            description="Tournament ID"
        )
    ]
