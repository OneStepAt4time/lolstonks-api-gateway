"""FastAPI application for LOL API Gateway."""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.cache.tracking import tracker
from app.config import settings
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
    challenges,
)


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
    )

    # Initialize Redis connection for tracking
    await tracker.connect()
    logger.success("Gateway started successfully")

    yield

    # Shutdown
    logger.info("Shutting down LOL API Gateway")
    await riot_client.close()
    logger.success("Gateway shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="LOL API Gateway",
    description="Intelligent proxy for Riot Games API with caching, rate limiting, and match tracking",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(health.router)
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

logger.info("FastAPI app initialized with all Riot LoL API endpoints")
