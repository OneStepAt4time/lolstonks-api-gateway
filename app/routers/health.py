"""Health check endpoint for gateway monitoring."""

from fastapi import APIRouter
from loguru import logger

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Simple status response
    """
    logger.debug("Health check requested")
    return {"status": "ok"}
