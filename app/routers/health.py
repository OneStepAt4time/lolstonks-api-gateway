"""Health check endpoint for gateway monitoring."""

from fastapi import APIRouter
from loguru import logger

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Performs a health check of the application.

    This endpoint can be used to monitor the application's status. It
    returns a simple JSON response to indicate that the service is
    running.

    Returns:
        dict: A dictionary with a status of "ok".

    Example:
        >>> curl "http://127.0.0.1:8080/health"
    """
    logger.debug("Health check requested")
    return {"status": "ok"}
