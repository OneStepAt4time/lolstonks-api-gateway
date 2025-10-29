"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables and .env file.
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Riot API Configuration
    riot_api_key: str
    riot_default_region: str = "euw1"
    riot_request_timeout: int = 10

    # Rate Limits (Riot API compliance)
    riot_rate_limit_per_second: int = 20
    riot_rate_limit_per_2min: int = 100

    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # Cache TTL (seconds) - Organized by API service

    # ACCOUNT-V1: Account and active shard endpoints
    cache_ttl_account: int = 3600  # 1 hour - Account data (by puuid/riotId)
    cache_ttl_account_shard: int = 600  # 10 minutes - Active shard (can change)

    # SUMMONER-V4: Summoner profile data
    cache_ttl_summoner: int = 3600  # 1 hour

    # MATCH-V5: Match history and details
    cache_ttl_match: int = 86400  # 24 hours - Match data (immutable)
    cache_ttl_timeline: int = 86400  # 24 hours - Match timeline (immutable)

    # LEAGUE-V4: Ranked league data
    cache_ttl_league: int = 3600  # 1 hour

    # CHAMPION-MASTERY-V4: Champion mastery points
    cache_ttl_mastery: int = 3600  # 1 hour

    # CHALLENGES-V1: Player challenges and leaderboards
    cache_ttl_challenges_config: int = 86400  # 24 hours - Challenge configs (static)
    cache_ttl_challenges_leaderboard: int = 600  # 10 minutes - Leaderboards (dynamic)
    cache_ttl_challenges_percentiles: int = 3600  # 1 hour - Percentile data
    cache_ttl_challenges_player: int = 3600  # 1 hour - Player challenges

    # CLASH-V1: Clash tournament data
    cache_ttl_clash_player: int = 300  # 5 minutes - Player info (changes during tournaments)
    cache_ttl_clash_team: int = 300  # 5 minutes - Team info (changes during tournaments)
    cache_ttl_clash_tournament: int = 600  # 10 minutes - Tournament schedule

    # CHAMPION-V3: Champion rotation
    cache_ttl_champion_rotation: int = 86400  # 24 hours - Rotation changes weekly

    # LOL-STATUS-V4: Platform status
    cache_ttl_platform_status: int = 300  # 5 minutes - Status can change frequently

    # SPECTATOR-V5: Live game data
    cache_ttl_spectator_active: int = 30  # 30 seconds - Active game (very dynamic)
    cache_ttl_spectator_featured: int = 120  # 2 minutes - Featured games

    # Data Dragon: Static game data (champions, items, etc.)
    cache_ttl_ddragon: int = 604800  # 7 days - Static data updated per patch

    # Default TTL for any uncategorized cache
    cache_ttl_default: int = 3600  # 1 hour

    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8080
    log_level: str = "INFO"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # type: ignore[typeddict-unknown-key]
    )


# Global settings instance
settings = Settings()
