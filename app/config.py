"""Application configuration management using Pydantic Settings.

This module provides type-safe configuration management for the gateway application.
It uses Pydantic's BaseSettings to automatically load and validate configuration
from environment variables and .env files, with sensible defaults for development.

Configuration Sources (in priority order):
    1. Environment variables (highest priority)
    2. .env file in project root
    3. Default values defined in Settings class

All configuration is centralized in the Settings class, which provides:
- Type validation and coercion
- Automatic environment variable loading
- IDE autocomplete support
- Clear documentation of all config options
- Runtime validation on application startup

Configuration Categories:
    - Riot API: API keys, timeouts, rate limits, default region
    - Redis Cache: Connection settings, DB selection, authentication
    - Cache TTLs: Per-endpoint TTL values for optimal caching
    - Data Providers: External data sources (Data Dragon, Community Dragon)
    - Server: Host, port, logging configuration

Environment Variables:
    All settings can be configured via environment variables using uppercase
    names. For example:
    - RIOT_API_KEY -> riot_api_key
    - REDIS_HOST -> redis_host
    - CACHE_TTL_MATCH -> cache_ttl_match

    For lists, use comma-separated values:
    - ENABLED_PROVIDERS="riot_api,data_dragon"

Security:
    - API keys should NEVER be committed to version control
    - Use .env file for local development (add to .gitignore)
    - Use environment variables in production
    - Redis password is optional but recommended for production

Usage:
    ```python
    from app.config import settings

    # Access configuration
    api_key = settings.riot_api_key
    redis_host = settings.redis_host

    # Get API keys with fallback logic
    keys = settings.get_api_keys()
    ```

See Also:
    pydantic_settings.BaseSettings: Base class providing auto-loading
    app.main: Application initialization using these settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    This class defines all the configuration parameters for the application.
    It uses Pydantic's BaseSettings to automatically load settings from
    environment variables and a .env file.

    Attributes:
        riot_api_key (str): The API key for accessing the Riot Games API.
        riot_api_keys (str): Comma-separated list of API keys for rotation.
        riot_default_region (str): The default region to use for API requests.
        riot_request_timeout (int): The timeout for HTTP requests to the Riot API.
        riot_rate_limit_per_second (int): The number of requests per second allowed by the rate limiter.
        riot_rate_limit_per_2min (int): The number of requests per 2 minutes allowed by the rate limiter.
        enabled_providers (list[str]): List of enabled API providers.
        data_dragon_version (str): Data Dragon game version or "latest".
        data_dragon_locale (str): Data Dragon language locale.
        community_dragon_version (str): Community Dragon data version or "latest".
        redis_host (str): The hostname of the Redis server.
        redis_port (int): The port of the Redis server.
        redis_db (int): The Redis database to use.
        redis_password (str): The password for the Redis server.
        cache_ttl_account (int): The cache TTL for account data.
        cache_ttl_account_shard (int): The cache TTL for active shard data.
        cache_ttl_summoner (int): The cache TTL for summoner data.
        cache_ttl_match (int): The cache TTL for match data.
        cache_ttl_timeline (int): The cache TTL for match timeline data.
        cache_ttl_league (int): The cache TTL for league data.
        cache_ttl_mastery (int): The cache TTL for champion mastery data.
        cache_ttl_challenges_config (int): The cache TTL for challenges config data.
        cache_ttl_challenges_leaderboard (int): The cache TTL for challenges leaderboard data.
        cache_ttl_challenges_percentiles (int): The cache TTL for challenges percentiles data.
        cache_ttl_challenges_player (int): The cache TTL for player challenges data.
        cache_ttl_clash_player (int): The cache TTL for Clash player data.
        cache_ttl_clash_team (int): The cache TTL for Clash team data.
        cache_ttl_clash_tournament (int): The cache TTL for Clash tournament data.
        cache_ttl_champion_rotation (int): The cache TTL for champion rotation data.
        cache_ttl_platform_status (int): The cache TTL for platform status data.
        cache_ttl_spectator_active (int): The cache TTL for active spectator data.
        cache_ttl_spectator_featured (int): The cache TTL for featured spectator data.
        cache_ttl_ddragon (int): The cache TTL for Data Dragon data.
        cache_ttl_tournament_code (int): The cache TTL for tournament code details.
        cache_ttl_tournament_lobby_events (int): The cache TTL for tournament lobby events.
        cache_ttl_default (int): The default cache TTL.
        host (str): The host to bind the server to.
        port (int): The port to bind the server to.
        log_level (str): The logging level for the application.
    """

    # Riot API Configuration
    riot_api_key: str | None = None  # Backward compatible - single key
    riot_api_keys: str | None = None  # New - comma-separated keys for rotation
    riot_default_region: str = "euw1"
    riot_request_timeout: int = 10

    # Provider Configuration
    enabled_providers: list[str] = ["riot_api", "data_dragon", "community_dragon"]

    # Data Dragon Configuration
    data_dragon_version: str = "latest"  # Game version or "latest"
    data_dragon_locale: str = "en_US"  # Language locale

    # Community Dragon Configuration
    community_dragon_version: str = "latest"  # Data version or specific patch

    def get_api_keys(self) -> list[str]:
        """
        Get list of API keys with priority: RIOT_API_KEYS > RIOT_API_KEY.

        Returns:
            list[str]: List of API keys for rotation

        Raises:
            ValueError: If no API keys are configured
        """
        # Priority 1: Multiple keys (comma-separated)
        # Handle both None and empty string as "not configured"
        if self.riot_api_keys and self.riot_api_keys.strip():
            keys = [k.strip() for k in self.riot_api_keys.split(",") if k.strip()]
            if keys:
                return keys

        # Priority 2: Single key (backward compatibility)
        # Handle both None and empty string as "not configured"
        if self.riot_api_key and self.riot_api_key.strip():
            return [self.riot_api_key.strip()]

        # No keys configured
        raise ValueError("No Riot API keys configured. Set RIOT_API_KEY or RIOT_API_KEYS")

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

    # TOURNAMENT-V5: Tournament management
    cache_ttl_tournament_code: int = 300  # 5 minutes - Tournament code details
    cache_ttl_tournament_lobby_events: int = 30  # 30 seconds - Lobby events (very dynamic)

    # Default TTL for any uncategorized cache
    cache_ttl_default: int = 3600  # 1 hour

    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8080
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
