"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables and .env file.
"""

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

    # Cache TTL (seconds)
    cache_ttl_summoner: int = 3600  # 1 hour
    cache_ttl_match: int = 86400  # 24 hours
    cache_ttl_timeline: int = 86400  # 24 hours
    cache_ttl_league: int = 3600  # 1 hour
    cache_ttl_mastery: int = 3600  # 1 hour
    cache_ttl_ddragon: int = 604800  # 7 days
    cache_ttl_default: int = 3600  # 1 hour

    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8080
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
