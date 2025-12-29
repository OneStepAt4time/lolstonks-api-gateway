"""Router module initialization.

This module exports all API routers for the gateway application.
Each router corresponds to a specific Riot API service and provides
endpoints for accessing that service's functionality.

Usage:
    from app.routers import (
        account_router,
        champion_router,
        clash_router,
        league_router,
        league_exp_router,
        match_router,
        spectator_router,
        summoner_router,
        tournament_router,
        tournament_stub_router,
        platform_router,
    )

    # Register routers in main app
    app.include_router(account_router)
    app.include_router(champion_router)
    # ... etc
"""

from app.routers.account import router as account_router
from app.routers.champion_mastery import router as champion_mastery_router
from app.routers.challenges import router as challenges_router
from app.routers.clash import router as clash_router
from app.routers.league import router as league_router
from app.routers.league_exp import router as league_exp_router
from app.routers.match import router as match_router
from app.routers.platform import router as platform_router
from app.routers.spectator import router as spectator_router
from app.routers.summoner import router as summoner_router
from app.routers.tournament import router as tournament_router
from app.routers.tournament_stub import router as tournament_stub_router

__all__ = [
    "account_router",
    "champion_mastery_router",
    "challenges_router",
    "clash_router",
    "league_router",
    "league_exp_router",
    "match_router",
    "platform_router",
    "spectator_router",
    "summoner_router",
    "tournament_router",
    "tournament_stub_router",
]
