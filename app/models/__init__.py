"""Pydantic models for API input validation.

This package contains all request models for the API Gateway.
Models are organized by Riot API service for easy maintenance.

Structure:
- common: Reusable base models and enums
- account: ACCOUNT-V1 models
- summoner: SUMMONER-V4 models
- match: MATCH-V5 models
- league: LEAGUE-V4 models
- champion_mastery: CHAMPION-MASTERY-V4 models
- challenges: CHALLENGES-V1 models
- clash: CLASH-V1 models
- spectator: SPECTATOR-V5 models
- platform: LOL-STATUS-V4 models
- champion: CHAMPION-V3 models
"""

# Common models
from app.models.common import (
    Division,
    EnumBaseModel,
    GameRegion,
    HasChallengeId,
    HasChampionId,
    HasEncryptedPuuid,
    HasEncryptedSummonerId,
    HasMatchId,
    HasPuuid,
    HasTeamId,
    HasTournamentId,
    PaginationQuery,
    PlatformRegion,
    PlatformRegionQuery,
    QueueType,
    RegionQuery,
    Tier,
)

# Account models
from app.models.account import (
    AccountByPuuidParams,
    AccountByPuuidQuery,
    AccountByRiotIdParams,
    AccountByRiotIdQuery,
    ActiveShardParams,
    ActiveShardQuery,
)

# Summoner models
from app.models.summoner import (
    SummonerByIdParams,
    SummonerByIdQuery,
    SummonerByNameParams,
    SummonerByNameQuery,
    SummonerByPuuidParams,
    SummonerByPuuidQuery,
)

# Match models
from app.models.match import (
    MatchIdsByPuuidParams,
    MatchIdsByPuuidQuery,
    MatchParams,
    MatchQuery,
    MatchTimelineParams,
    MatchTimelineQuery,
)

# League models
from app.models.league import (
    LeagueByQueueParams,
    LeagueByQueueQuery,
    LeagueEntriesBySummonerParams,
    LeagueEntriesBySummonerQuery,
    LeagueEntriesParams,
    LeagueEntriesQuery,
)

# League-EXP models
from app.models.league_exp import (
    LeagueExpEntriesParams,
    LeagueExpEntriesQuery,
)

# Champion Mastery models
from app.models.champion_mastery import (
    ChampionMasteryByPuuidByChampionParams,
    ChampionMasteryByPuuidByChampionQuery,
    ChampionMasteryByPuuidParams,
    ChampionMasteryByPuuidQuery,
    MasteryScoreParams,
    MasteryScoreQuery,
    TopChampionMasteriesParams,
    TopChampionMasteriesQuery,
)

# Challenges models
from app.models.challenges import (
    AllChallengesConfigQuery,
    ChallengeConfigParams,
    ChallengeConfigQuery,
    ChallengeLeaderboardParams,
    ChallengeLeaderboardQuery,
    ChallengePercentilesParams,
    ChallengePercentilesQuery,
    PlayerChallengesParams,
    PlayerChallengesQuery,
)

# Clash models
from app.models.clash import (
    ClashPlayerParams,
    ClashPlayerQuery,
    ClashTeamParams,
    ClashTeamQuery,
    ClashTournamentByTeamParams,
    ClashTournamentByTeamQuery,
    ClashTournamentParams,
    ClashTournamentQuery,
    ClashTournamentsQuery,
)

# Spectator models
from app.models.spectator import (
    ActiveGameParams,
    ActiveGameQuery,
    FeaturedGamesQuery,
)

# Platform models
from app.models.platform import PlatformStatusQuery

# Champion models
from app.models.champion import ChampionRotationsQuery

__all__ = [
    # Common
    "Division",
    "EnumBaseModel",
    "GameRegion",
    "HasChallengeId",
    "HasChampionId",
    "HasEncryptedPuuid",
    "HasEncryptedSummonerId",
    "HasMatchId",
    "HasPuuid",
    "HasTeamId",
    "HasTournamentId",
    "PaginationQuery",
    "PlatformRegion",
    "PlatformRegionQuery",
    "QueueType",
    "RegionQuery",
    "Tier",
    # Account
    "AccountByPuuidParams",
    "AccountByPuuidQuery",
    "AccountByRiotIdParams",
    "AccountByRiotIdQuery",
    "ActiveShardParams",
    "ActiveShardQuery",
    # Summoner
    "SummonerByIdParams",
    "SummonerByIdQuery",
    "SummonerByNameParams",
    "SummonerByNameQuery",
    "SummonerByPuuidParams",
    "SummonerByPuuidQuery",
    # Match
    "MatchIdsByPuuidParams",
    "MatchIdsByPuuidQuery",
    "MatchParams",
    "MatchQuery",
    "MatchTimelineParams",
    "MatchTimelineQuery",
    # League
    "LeagueByQueueParams",
    "LeagueByQueueQuery",
    "LeagueEntriesBySummonerParams",
    "LeagueEntriesBySummonerQuery",
    "LeagueEntriesParams",
    "LeagueEntriesQuery",
    # League-EXP
    "LeagueExpEntriesParams",
    "LeagueExpEntriesQuery",
    # Champion Mastery
    "ChampionMasteryByPuuidByChampionParams",
    "ChampionMasteryByPuuidByChampionQuery",
    "ChampionMasteryByPuuidParams",
    "ChampionMasteryByPuuidQuery",
    "MasteryScoreParams",
    "MasteryScoreQuery",
    "TopChampionMasteriesParams",
    "TopChampionMasteriesQuery",
    # Challenges
    "AllChallengesConfigQuery",
    "ChallengeConfigParams",
    "ChallengeConfigQuery",
    "ChallengeLeaderboardParams",
    "ChallengeLeaderboardQuery",
    "ChallengePercentilesParams",
    "ChallengePercentilesQuery",
    "PlayerChallengesParams",
    "PlayerChallengesQuery",
    # Clash
    "ClashPlayerParams",
    "ClashPlayerQuery",
    "ClashTeamParams",
    "ClashTeamQuery",
    "ClashTournamentByTeamParams",
    "ClashTournamentByTeamQuery",
    "ClashTournamentParams",
    "ClashTournamentQuery",
    "ClashTournamentsQuery",
    # Spectator
    "ActiveGameParams",
    "ActiveGameQuery",
    "FeaturedGamesQuery",
    # Platform
    "PlatformStatusQuery",
    # Champion
    "ChampionRotationsQuery",
]
