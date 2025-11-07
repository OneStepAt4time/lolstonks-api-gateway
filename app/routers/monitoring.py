"""
Monitoring dashboard endpoints for comprehensive error tracking.

Provides detailed monitoring including:
- Error statistics and trends
- Recent error logs
- Provider error rates
- System performance metrics
- Alert status and history
"""

from fastapi import APIRouter, Query
from loguru import logger

from app.middleware.error_monitoring import get_global_error_monitor
from app.models.common import ErrorMetrics

router = APIRouter(tags=["monitoring"])


def get_error_monitoring():
    """Get the error monitoring middleware instance."""
    return get_global_error_monitor()


@router.get("/monitoring/errors", response_model=ErrorMetrics)
async def get_error_metrics():
    """
    Get comprehensive error metrics for monitoring systems.

    Returns detailed error statistics including:
    - Total error counts by type
    - Error rates by endpoint and provider
    - Recent error trends (5min, 1hour)
    - Consecutive failure tracking
    - Active alerts

    Returns:
        ErrorMetrics object with current error statistics

    Example:
        >>> curl "http://127.0.0.1:8080/monitoring/errors"
    """
    logger.debug("Error metrics requested")

    error_monitor = get_error_monitoring()
    return error_monitor.get_error_metrics()


@router.get("/monitoring/errors/recent")
async def get_recent_errors(
    limit: int = Query(default=50, ge=1, le=1000, description="Maximum number of errors to return"),
    include_client_errors: bool = Query(default=False, description="Include 4xx client errors"),
):
    """
    Get recent error records for debugging and monitoring.

    Returns detailed information about recent errors including:
    - Timestamp and endpoint
    - Provider information
    - Error type and message
    - Request duration
    - HTTP status codes

    Args:
        limit: Maximum number of error records to return (1-1000)
        include_client_errors: Whether to include 4xx client errors in results

    Returns:
        List of ErrorRecord objects with detailed error information

    Example:
        >>> curl "http://127.0.0.1:8080/monitoring/errors/recent?limit=20"
    """
    logger.debug(f"Recent errors requested (limit={limit}, include_client={include_client_errors})")

    error_monitor = get_error_monitoring()
    all_errors = error_monitor.get_recent_errors(limit * 2)  # Get more to filter

    # Filter based on client error preference
    if include_client_errors:
        recent_errors = all_errors[:limit]
    else:
        # Only include server errors and critical issues
        server_errors = [
            error for error in all_errors if error.is_server_error or error.status_code >= 500
        ]
        recent_errors = server_errors[:limit]

    return [
        {
            "timestamp": error.timestamp,
            "endpoint": error.endpoint,
            "provider": error.provider,
            "status_code": error.status_code,
            "method": error.method,
            "path": error.path,
            "duration_ms": round(error.duration * 1000, 2),
            "error_type": error.error_type,
            "error_message": error.error_message,
            "is_client_error": error.is_client_error,
            "is_server_error": error.is_server_error,
        }
        for error in recent_errors
    ]


@router.get("/monitoring/errors/summary")
async def get_error_summary(
    time_window: str = Query(
        default="1h",
        pattern="^(5m|15m|1h|6h|24h)$",
        description="Time window for analysis (5m, 15m, 1h, 6h, 24h)",
    ),
):
    """
    Get summarized error statistics for a specific time window.

    Provides aggregated error statistics for monitoring dashboards and alerts:
    - Error rates by time window
    - Top error-producing endpoints
    - Provider-specific error rates
    - Error type distribution
    - Alert status

    Args:
        time_window: Time window for analysis (5m, 15m, 1h, 6h, 24h)

    Returns:
        Dict with summarized error statistics

    Example:
        >>> curl "http://127.0.0.1:8080/monitoring/errors/summary?time_window=1h"
    """
    logger.debug(f"Error summary requested for time window: {time_window}")

    error_monitor = get_error_monitoring()
    metrics = error_monitor.get_error_metrics()

    # Convert time window to seconds
    time_window_seconds = {"5m": 300, "15m": 900, "1h": 3600, "6h": 21600, "24h": 86400}.get(
        time_window, 3600
    )

    current_time = metrics.last_updated
    cutoff_time = current_time - time_window_seconds

    # Filter errors by time window
    recent_errors = [
        error for error in error_monitor.error_history if error.timestamp >= cutoff_time
    ]

    # Calculate statistics
    total_errors = len(recent_errors)
    server_errors = len([e for e in recent_errors if e.is_server_error])
    client_errors = len([e for e in recent_errors if e.is_client_error])

    # Top error endpoints
    endpoint_counts: dict[str, int] = {}
    for error in recent_errors:
        endpoint_counts[error.endpoint] = endpoint_counts.get(error.endpoint, 0) + 1

    top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Provider error rates
    provider_counts: dict[str, int] = {}
    provider_server_errors: dict[str, int] = {}
    for error in recent_errors:
        provider = error.provider or "unknown"
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
        if error.is_server_error:
            provider_server_errors[provider] = provider_server_errors.get(provider, 0) + 1

    provider_error_rates = {}
    for provider, total in provider_counts.items():
        server = provider_server_errors.get(provider, 0)
        provider_error_rates[provider] = {
            "total_errors": total,
            "server_errors": server,
            "error_rate_percent": round((server / total) * 100, 2) if total > 0 else 0,
        }

    # Status code distribution
    status_counts: dict[str, int] = {}
    for error in recent_errors:
        status = error.status_code
        status_counts[status] = status_counts.get(status, 0) + 1

    # Calculate error rate per minute
    error_rate_per_min = round(total_errors / (time_window_seconds / 60), 2)

    return {
        "time_window": time_window,
        "time_window_seconds": time_window_seconds,
        "current_time": current_time,
        "total_errors": total_errors,
        "server_errors": server_errors,
        "client_errors": client_errors,
        "error_rate_per_minute": error_rate_per_min,
        "top_error_endpoints": [
            {"endpoint": endpoint, "count": count} for endpoint, count in top_endpoints
        ],
        "provider_error_rates": provider_error_rates,
        "status_code_distribution": status_counts,
        "active_alerts": metrics.active_alerts,
        "consecutive_failures": {
            endpoint: failures
            for endpoint, failures in metrics.consecutive_failures.items()
            if failures > 0
        },
    }


@router.get("/monitoring/alerts")
async def get_active_alerts():
    """
    Get currently active alerts and warnings.

    Returns information about active alerts including:
    - Alert types and severity
    - Affected endpoints and providers
    - Alert duration
    - Recommended actions

    Returns:
        Dict with active alert information

    Example:
        >>> curl "http://127.0.0.1:8080/monitoring/alerts"
    """
    logger.debug("Active alerts requested")

    error_monitor = get_error_monitoring()
    metrics = error_monitor.get_error_metrics()

    # Parse active alerts
    alert_details = []
    for alert in metrics.active_alerts:
        if "consecutive_failures:" in alert:
            endpoint = alert.replace("consecutive_failures:", "")
            failure_count = metrics.consecutive_failures.get(endpoint, 0)

            alert_details.append(
                {
                    "type": "consecutive_failures",
                    "severity": "high"
                    if failure_count >= 20
                    else "medium"
                    if failure_count >= 10
                    else "low",
                    "endpoint": endpoint,
                    "failure_count": failure_count,
                    "message": f"Endpoint {endpoint} has {failure_count} consecutive failures",
                    "recommendation": "Check provider status and API configuration",
                }
            )

    # Check for high error rates by provider
    for provider, error_count in metrics.error_rates_by_provider.items():
        if error_count > 50:  # High error rate threshold
            alert_details.append(
                {
                    "type": "high_error_rate",
                    "severity": "high" if error_count > 100 else "medium",
                    "provider": provider,
                    "error_count": error_count,
                    "message": f"Provider {provider} has {error_count} errors",
                    "recommendation": "Monitor provider performance and consider fallback",
                }
            )

    # Check for unusual status code patterns
    for status_code, count in metrics.status_code_distribution.items():
        if status_code >= 500 and count > 20:  # Many server errors
            alert_details.append(
                {
                    "type": "server_error_spike",
                    "severity": "high",
                    "status_code": status_code,
                    "count": count,
                    "message": f"Detected {count} HTTP {status_code} errors",
                    "recommendation": "Check application logs and provider status",
                }
            )

    return {
        "timestamp": metrics.last_updated,
        "total_active_alerts": len(alert_details),
        "alerts": alert_details,
        "alert_summary": {
            "high_severity": len([a for a in alert_details if a.get("severity") == "high"]),
            "medium_severity": len([a for a in alert_details if a.get("severity") == "medium"]),
            "low_severity": len([a for a in alert_details if a.get("severity") == "low"]),
        },
    }


@router.post("/monitoring/reset")
async def reset_monitoring_metrics():
    """
    Reset all error monitoring metrics.

    WARNING: This will clear all error history and metrics.
    Use only for testing or maintenance purposes.

    Returns:
        Confirmation message

    Example:
        >>> curl -X POST "http://127.0.0.1:8080/monitoring/reset"
    """
    logger.warning("Monitoring metrics reset requested")

    error_monitor = get_error_monitoring()
    error_monitor.reset_metrics()

    return {
        "message": "Error monitoring metrics have been reset",
        "timestamp": error_monitor.get_error_metrics().last_updated,
    }


@router.get("/monitoring/status")
async def get_monitoring_status():
    """
    Get status of the monitoring system itself.

    Returns information about:
    - Monitoring middleware status
    - Data collection health
    - Storage capacity
    - Performance impact

    Returns:
        Dict with monitoring system status

    Example:
        >>> curl "http://127.0.0.1:8080/monitoring/status"
    """
    logger.debug("Monitoring status requested")

    error_monitor = get_error_monitoring()
    metrics = error_monitor.get_error_metrics()

    # Calculate storage usage
    max_history = 1000  # From middleware configuration
    current_usage = len(error_monitor.error_history)
    storage_percent = (current_usage / max_history) * 100

    # Recent data collection rate
    recent_5min = metrics.recent_errors_5min
    collection_rate_per_min = recent_5min / 5

    return {
        "monitoring_status": "active",
        "timestamp": metrics.last_updated,
        "data_collection": {
            "total_errors_recorded": metrics.total_errors,
            "recent_errors_5min": recent_5min,
            "collection_rate_per_min": round(collection_rate_per_min, 2),
            "storage_usage": {
                "current_records": current_usage,
                "max_records": max_history,
                "usage_percent": round(storage_percent, 2),
            },
        },
        "active_alerts_count": len(metrics.active_alerts),
        "consecutive_failures_count": len(
            [f for f in metrics.consecutive_failures.values() if f > 0]
        ),
        "monitoring_features": {
            "error_tracking": True,
            "provider_monitoring": True,
            "alerting": True,
            "rate_limiting": False,  # Could be added in future
            "performance_metrics": True,
        },
    }
