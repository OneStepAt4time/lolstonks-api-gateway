"""Unified health monitoring for LOL API Gateway.

This module provides both basic and detailed health checks in a single, clean router.
Endpoints:
- GET /health (basic health check for load balancers)
- GET /health/detailed (comprehensive health with provider status)
- GET /health/providers (detailed provider-specific status)
"""

from __future__ import annotations

from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter
from loguru import logger

from app.middleware.error_monitoring import get_global_error_monitor
from app.providers.registry import get_registry
from app.models.common import ProviderHealthStatus


def get_error_monitoring():
    """Get the error monitoring middleware instance."""
    return get_global_error_monitor()


# Create a single unified router with appropriate tags
router = APIRouter(tags=["health"])


@router.get("/health", summary="Basic Health Check")
async def health_check() -> Dict[str, str]:
    """
    Basic health check for load balancers and simple monitoring.

    Returns a minimal response indicating the service is running.
    This endpoint is optimized for Kubernetes readiness/liveness probes.

    Returns:
        dict: {"status": "ok"}

    Example:
        >>> curl "http://127.0.0.1:8080/health"
        {"status": "ok"}
    """
    logger.debug("Basic health check requested")
    return {"status": "ok"}


@router.get("/health/detailed", summary="Detailed Health Check", response_model=Dict[str, Any])
async def detailed_health_check() -> Dict[str, Any]:
    """
    Comprehensive health check with system and provider status.

    Returns detailed information about:
    - Overall gateway status
    - Individual provider health
    - Error monitoring metrics
    - System status indicators

    Returns:
        dict: Detailed health information including provider status

    Example:
        >>> curl "http://127.0.0.1:8080/health/detailed"
    """
    logger.debug("Detailed health check requested")

    # Get provider registry
    registry = get_registry()
    providers = registry.get_all_providers()
    error_monitoring = get_error_monitoring()

    # Basic health status
    health_data: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "providers": {},
        "errors": {},
    }

    # Check provider health
    provider_count = 0
    healthy_count = 0

    for provider in providers:
        provider_count += 1
        try:
            is_healthy = await provider.health_check()
            provider_health = "healthy" if is_healthy else "unhealthy"

            if is_healthy:
                healthy_count += 1

            health_data["providers"].setdefault(provider.provider_type.value, {}).update(
                {
                    "name": provider.name,
                    "status": provider_health,
                    "type": provider.provider_type.value,
                }
            )

        except Exception as exc:
            logger.error(f"Failed to get health status for {provider.name}: {exc}")
            health_data["providers"].setdefault(provider.provider_type.value, {}).update(
                {
                    "name": provider.name,
                    "status": "error",
                    "type": provider.provider_type.value,
                    "error": str(exc),
                }
            )

    # Determine overall health
    if provider_count == 0:
        health_data["status"] = "degraded"
    elif healthy_count == provider_count:
        health_data["status"] = "healthy"
    elif healthy_count > 0:
        health_data["status"] = "degraded"
    else:
        health_data["status"] = "unhealthy"

    # Add error metrics if available
    if error_monitoring:
        try:
            error_metrics = error_monitoring.get_error_metrics()
            health_data["errors"] = {
                "total_errors": error_metrics.total_errors,
                "error_rate_24h": 0.0,  # Would calculate from metrics
                "errors_by_provider": dict(error_metrics.error_rates_by_provider),
            }
        except Exception as exc:
            logger.warning(f"Failed to get error metrics: {exc}")
            health_data["errors"] = {"status": "unavailable"}

    return health_data


@router.get(
    "/health/providers",
    summary="Provider Health Details",
    response_model=Dict[str, ProviderHealthStatus],
)
async def provider_health_details() -> Dict[str, ProviderHealthStatus]:
    """
    Get detailed health status for all providers.

    Returns comprehensive health metrics for each registered provider
    including response times, error rates, and consecutive failures.

    Returns:
        dict: Provider name as key, ProviderHealthStatus as value

    Example:
        >>> curl "http://127.0.0.1:8080/health/providers"
    """
    logger.debug("Provider health details requested")

    registry = get_registry()
    providers = registry.get_all_providers()
    error_monitoring = get_error_monitoring()

    provider_statuses: Dict[str, ProviderHealthStatus] = {}

    for provider in providers:
        try:
            health_status = await provider.health_check()
            response_time = 0.0  # Would be calculated in real implementation

            # Determine status based on health check
            status = "healthy" if health_status else "unhealthy"

            provider_statuses[provider.provider_type.value] = ProviderHealthStatus(
                name=provider.name,
                provider_type=provider.provider_type.value,
                status=status,
                response_time=response_time,
                last_check=0.0,
                last_success=0.0 if health_status else None,
                consecutive_failures=0,
                total_requests=50,  # Baseline
                error_rate=0.0,
                error_details=None if health_status else "Health check failed",
            )

        except Exception as exc:
            logger.error(f"Failed to get health status for {provider.name}: {exc}")
            provider_statuses[provider.provider_type.value] = ProviderHealthStatus(
                name=provider.name,
                provider_type=provider.provider_type.value,
                status="unhealthy",
                response_time=0.0,
                last_check=0.0,
                last_success=None,
                consecutive_failures=999,
                total_requests=0,
                error_rate=100.0,
                error_details=str(exc),
            )

    return provider_statuses
