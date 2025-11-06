"""
Error monitoring middleware for tracking and analyzing HTTP errors.

This middleware provides comprehensive error tracking including:
- Error frequency by endpoint and provider
- Consecutive failure counting
- Alerting threshold monitoring
- Structured error logging
"""

import time
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.common import ErrorMetrics, ErrorRecord


# Global instance reference for router access
_global_instance: "ErrorMonitoringMiddleware | None" = None


def get_global_error_monitor() -> "ErrorMonitoringMiddleware":
    """Get the global error monitoring instance."""
    global _global_instance
    if _global_instance is None:
        raise RuntimeError("Error monitoring middleware not initialized")
    return _global_instance


class ErrorMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive error monitoring and tracking.

    Tracks HTTP errors, exceptions, and provides detailed metrics
    for monitoring system health and detecting reliability issues.
    """

    def __init__(self, app, max_error_history: int = 1000, alert_threshold: int = 10):
        """
        Initialize error monitoring middleware.

        Args:
            app: FastAPI application
            max_error_history: Maximum number of error records to keep in memory
            alert_threshold: Number of errors before considering it an alert
        """
        super().__init__(app)
        global _global_instance
        _global_instance = self

        # Error tracking data structures
        self.error_history: deque[ErrorRecord] = deque(maxlen=max_error_history)
        self.error_counts: Dict[str, int] = defaultdict(int)  # endpoint -> count
        self.provider_error_counts: Dict[str, int] = defaultdict(int)  # provider -> count
        self.status_code_counts: Dict[int, int] = defaultdict(int)  # status -> count
        self.recent_errors: deque[ErrorRecord] = deque(maxlen=100)  # Last 100 errors
        self.consecutive_failures: Dict[str, int] = defaultdict(int)  # endpoint -> count
        self.last_success_times: Dict[str, float] = {}  # endpoint -> timestamp
        self.active_alerts: Set[str] = set()

        # Configuration
        self.alert_threshold = alert_threshold
        self.alert_cooldown = 300  # 5 minutes between same alert

        # Provider detection patterns
        self.provider_patterns = {
            "riot_api": [
                "/riot",
                "/lol",
                "/match",
                "/summoner",
                "/league",
                "/clash",
                "/challenges",
            ],
            "data_dragon": ["/ddragon", "/dragon", "/champion", "/item", "/rune"],
            "community_dragon": ["/cdragon", "/cdn", "/assets"],
        }

        logger.info("Error monitoring middleware initialized")

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and track any errors that occur.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain

        Returns:
            HTTP response (possibly modified if error occurred)
        """
        start_time = time.time()
        endpoint = self._get_endpoint_path(request)

        try:
            response = await call_next(request)

            # Track successful requests
            if 200 <= response.status_code < 400:
                self._track_success(endpoint)

            # Track client errors (4xx) as warnings
            elif 400 <= response.status_code < 500:
                self._track_client_error(request, response, start_time)

            return response

        except Exception as exc:
            # Track server errors (5xx and exceptions)
            return await self._handle_server_error(request, exc, start_time)

    def _get_endpoint_path(self, request: Request) -> str:
        """Extract the endpoint path from request."""
        return f"{request.method} {request.url.path}"

    def _detect_provider(self, path: str) -> Optional[str]:
        """Detect which provider is likely handling the request based on path."""
        path_lower = path.lower()

        for provider, patterns in self.provider_patterns.items():
            if any(pattern in path_lower for pattern in patterns):
                return provider

        return "unknown"

    def _track_success(self, endpoint: str):
        """Track successful request to reset consecutive failure counter."""
        self.consecutive_failures[endpoint] = 0
        self.last_success_times[endpoint] = time.time()

        # Clear any existing alerts for this endpoint
        alert_key = f"consecutive_failures:{endpoint}"
        self.active_alerts.discard(alert_key)

    def _track_client_error(self, request: Request, response: Response, start_time: float):
        """Track client errors (4xx) with detailed logging."""
        endpoint = self._get_endpoint_path(request)
        provider = self._detect_provider(request.url.path)
        duration = time.time() - start_time

        error_record = ErrorRecord(
            timestamp=time.time(),
            endpoint=endpoint,
            provider=provider,
            status_code=response.status_code,
            method=request.method,
            path=request.url.path,
            duration=duration,
            is_client_error=True,
        )

        self._record_error(error_record)

        # Log warning for client errors
        logger.warning(
            f"Client error: {endpoint} -> {response.status_code} "
            f"(provider: {provider}, duration: {duration:.3f}s)"
        )

    async def _handle_server_error(
        self, request: Request, exc: Exception, start_time: float
    ) -> JSONResponse:
        """Handle server errors with comprehensive tracking."""
        endpoint = self._get_endpoint_path(request)
        provider = self._detect_provider(request.url.path)
        duration = time.time() - start_time

        # Create error record
        error_record = ErrorRecord(
            timestamp=time.time(),
            endpoint=endpoint,
            provider=provider,
            status_code=500,
            method=request.method,
            path=request.url.path,
            duration=duration,
            error_type=type(exc).__name__,
            error_message=str(exc),
            is_server_error=True,
        )

        self._record_error(error_record)

        # Track consecutive failures
        self.consecutive_failures[endpoint] += 1
        failure_count = self.consecutive_failures[endpoint]

        # Check for alert conditions
        self._check_alert_conditions(endpoint, provider, failure_count)

        # Log error with context
        logger.error(
            f"Server error: {endpoint} -> {type(exc).__name__}: {exc} "
            f"(provider: {provider}, consecutive failures: {failure_count}, "
            f"duration: {duration:.3f}s)"
        )

        # Return standardized error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing your request.",
                "error_id": f"{int(error_record.timestamp)}_{hash(endpoint) % 10000:04d}",
                "timestamp": error_record.timestamp,
            },
        )

    def _record_error(self, error_record: ErrorRecord):
        """Record error in tracking data structures."""
        # Add to history
        self.error_history.append(error_record)
        self.recent_errors.append(error_record)

        # Update counters
        self.error_counts[error_record.endpoint] += 1
        self.status_code_counts[error_record.status_code] += 1

        if error_record.provider:
            self.provider_error_counts[error_record.provider] += 1

    def _check_alert_conditions(self, endpoint: str, provider: str, consecutive_failures: int):
        """Check if error conditions warrant an alert."""
        if consecutive_failures >= self.alert_threshold:
            alert_key = f"consecutive_failures:{endpoint}"
            current_time = time.time()

            # Check cooldown to avoid alert spam
            last_alert_time = getattr(self, f"_last_alert_{alert_key.replace(':', '_')}", 0)
            if current_time - last_alert_time > self.alert_cooldown:
                self.active_alerts.add(alert_key)
                setattr(self, f"_last_alert_{alert_key.replace(':', '_')}", current_time)

                logger.critical(
                    f"ALERT: Endpoint {endpoint} has {consecutive_failures} "
                    f"consecutive failures (provider: {provider})"
                )

    def get_error_metrics(self) -> ErrorMetrics:
        """
        Get comprehensive error metrics for monitoring.

        Returns:
            ErrorMetrics object with current error statistics
        """
        current_time = time.time()

        # Calculate error rates for different time windows
        recent_errors_5m = [e for e in self.recent_errors if current_time - e.timestamp <= 300]
        recent_errors_1h = [e for e in self.error_history if current_time - e.timestamp <= 3600]

        # Count server vs client errors
        server_errors = sum(1 for e in self.error_history if e.is_server_error)
        client_errors = sum(1 for e in self.error_history if e.is_client_error)

        return ErrorMetrics(
            total_errors=len(self.error_history),
            server_errors=server_errors,
            client_errors=client_errors,
            recent_errors_5min=len(recent_errors_5m),
            recent_errors_1hour=len(recent_errors_1h),
            error_rates_by_endpoint=dict(self.error_counts),
            error_rates_by_provider=dict(self.provider_error_counts),
            status_code_distribution=dict(self.status_code_counts),
            consecutive_failures=dict(self.consecutive_failures),
            last_success_times=dict(self.last_success_times),
            active_alerts=list(self.active_alerts),
            last_updated=current_time,
        )

    def get_recent_errors(self, limit: int = 50) -> List[ErrorRecord]:
        """
        Get recent error records.

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of recent error records
        """
        return list(self.recent_errors)[-limit:]

    def reset_metrics(self):
        """Reset all error tracking metrics."""
        self.error_history.clear()
        self.error_counts.clear()
        self.provider_error_counts.clear()
        self.status_code_counts.clear()
        self.recent_errors.clear()
        self.consecutive_failures.clear()
        self.last_success_times.clear()
        self.active_alerts.clear()
        logger.info("Error monitoring metrics reset")
