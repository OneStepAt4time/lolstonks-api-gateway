"""
Middleware package for API Gateway.

Provides various middleware components for request processing,
error monitoring, and health tracking.
"""

from app.middleware.error_monitoring import ErrorMonitoringMiddleware

__all__ = [
    "ErrorMonitoringMiddleware",
]
