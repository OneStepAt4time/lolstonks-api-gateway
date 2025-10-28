"""Tests for configuration module."""

import os

import pytest


def test_config_imports():
    """Test that config module can be imported."""
    from app.config import settings

    assert settings is not None


def test_riot_api_key_loaded():
    """Test that Riot API key is loaded from environment."""
    from app.config import settings

    # Should be set by conftest.py
    assert settings.riot_api_key is not None
    assert settings.riot_api_key.startswith("RGAPI-")


def test_redis_configuration():
    """Test Redis configuration."""
    from app.config import settings

    assert settings.redis_host is not None
    assert settings.redis_port > 0
    assert settings.redis_port == 6379


def test_default_region():
    """Test that default region is set."""
    from app.config import settings

    assert settings.riot_default_region is not None
    assert len(settings.riot_default_region) > 0


def test_server_configuration():
    """Test server configuration values."""
    from app.config import settings

    # These should have defaults even if not set
    assert hasattr(settings, "host")
    assert hasattr(settings, "port")


def test_log_level_configuration():
    """Test log level configuration."""
    from app.config import settings

    # Should be set to ERROR by conftest.py
    assert settings.log_level is not None


def test_rate_limit_configuration():
    """Test rate limiting configuration."""
    from app.config import settings

    # Check that rate limit settings exist
    assert hasattr(settings, "riot_rate_limit_per_second")
    assert hasattr(settings, "riot_rate_limit_per_2min")

    # Values should be positive if set
    if settings.riot_rate_limit_per_second:
        assert settings.riot_rate_limit_per_second > 0
    if settings.riot_rate_limit_per_2min:
        assert settings.riot_rate_limit_per_2min > 0


def test_environment_override():
    """Test that environment variables override defaults."""
    # Set a new value
    os.environ["RIOT_DEFAULT_REGION"] = "kr"

    # Reimport settings (in real scenarios, use dependency injection)
    from importlib import reload
    from app import config
    reload(config)

    assert config.settings.riot_default_region == "kr"

    # Cleanup
    os.environ["RIOT_DEFAULT_REGION"] = "euw1"
    reload(config)


def test_config_validation():
    """Test that configuration validation works."""
    from app.config import settings

    # Config should be valid with test settings
    assert settings is not None

    # Required fields should be present
    assert settings.riot_api_key is not None
    assert settings.redis_host is not None
    assert settings.redis_port > 0
