"""FastAPI application for League of Legends API Gateway."""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.cache.tracking import tracker
from app.config import settings
from app.providers.registry import get_registry, initialize_providers
from app.riot.client import riot_client
from app.routers import (
    health,
    summoner,
    match,
    league,
    league_exp,
    champion,
    champion_mastery,
    spectator,
    platform,
    account,
    clash,
    security,
    challenges,
)
from app.routers.ddragon import (
    additional as ddragon_additional,
    champions as ddragon_champions,
    items as ddragon_items,
    versions as ddragon_versions,
)
from app.routers.cdragon import (
    additional as cdragon_additional,
    champions as cdragon_champions,
    skins as cdragon_skins,
    tft as cdragon_tft,
)
from app.middleware.error_monitoring import ErrorMonitoringMiddleware


# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events.

    Handles application startup and shutdown events.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Yields control back to the application.
    """
    # Startup
    logger.info("Starting LOL API Gateway")
    logger.info(
        "Configuration loaded",
        region=settings.riot_default_region,
        host=settings.host,
        port=settings.port,
        enabled_providers=settings.enabled_providers,
    )

    # Initialize API providers
    initialize_providers()
    logger.info(f"Initialized {len(get_registry().get_all_providers())} API provider(s)")

    # Initialize Redis connection for tracking
    await tracker.connect()
    logger.success("Gateway started successfully")

    yield

    # Shutdown
    logger.info("Shutting down LOL API Gateway")
    await riot_client.close()

    # Close all providers
    await get_registry().close_all()
    logger.success("Gateway shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="LOL API Gateway",
    description="""
    Multi-provider API Gateway for League of Legends data.

    Supports:
    - Riot Games Developer API (live game data)
    - Data Dragon CDN (static game data)
    - Community Dragon (enhanced static data and assets)

    Features:
    - Intelligent caching with Redis
    - Rate limiting and key rotation
    - Match tracking to avoid reprocessing
    - Multi-provider fallback support
    - Comprehensive error monitoring and health checks
    """,
    version="2.0.0",
    lifespan=lifespan,
)

# Add error monitoring middleware
app.add_middleware(ErrorMonitoringMiddleware, max_error_history=1000, alert_threshold=10)

# Include routers - Health & Monitoring
app.include_router(health.router)  # Health monitoring (basic + detailed)

# Include routers - Riot API
app.include_router(account.router)  # Account API (Riot ID lookups)
app.include_router(summoner.router)  # Summoner-V4
app.include_router(match.router)  # Match-V5
app.include_router(league.router)  # League-V4
app.include_router(league_exp.router)  # League-EXP-V4 (experimental)
app.include_router(champion.router)  # Champion-V3 (rotations)
app.include_router(champion_mastery.router)  # Champion-Mastery-V4
app.include_router(spectator.router)  # Spectator-V5 (live games)
app.include_router(platform.router)  # Platform/Status-V4
app.include_router(clash.router)  # Clash-V1
app.include_router(challenges.router)  # Challenges-V1
app.include_router(security.router)  # Security monitoring

# Include routers - Data Dragon
app.include_router(ddragon_versions.router)  # Versions and languages
app.include_router(ddragon_champions.router)  # Champion static data
app.include_router(ddragon_items.router)  # Items, runes, summoner spells
app.include_router(
    ddragon_additional.router
)  # Maps, missions, stickers, language strings, bulk data

# Include routers - Community Dragon
app.include_router(cdragon_champions.router)  # Enhanced champion data
app.include_router(cdragon_skins.router)  # Skin and chroma data
app.include_router(cdragon_tft.router)  # TFT data
app.include_router(cdragon_additional.router)  # Chromas, ward skins, missions, lore, loot

logger.info(
    "FastAPI app initialized with all API endpoints (Riot API, Data Dragon, Community Dragon, Health Monitoring, Security)"
)
