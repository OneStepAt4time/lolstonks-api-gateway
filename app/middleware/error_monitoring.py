"""
Error monitoring middleware for tracking and analyzing HTTP errors.

This middleware provides comprehensive error tracking including:
- Error frequency by endpoint and provider
- Consecutive failure counting
- Alerting threshold monitoring
- Structured error logging

Example:
    ```python
    from fastapi import FastAPI
    from app.middleware import ErrorMonitoringMiddleware

    app = FastAPI()
    app.add_middleware(ErrorMonitoringMiddleware, max_error_history=1000)
    ```
"""

import time
from collections import defaultdict, deque
from typing import Awaitable, Callable, Dict, List, Optional, Set

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.common import ErrorMetrics, ErrorRecord
from app.utils.error_formatter import format_error_response


# Global instance reference for router access
_global_instance: "ErrorMonitoringMiddleware | None" = None


def get_global_error_monitor() -> "ErrorMonitoringMiddleware":
    """Get the global error monitoring instance.

    Provides access to the singleton error monitoring middleware instance
    for routers and handlers that need to access error metrics.

    Returns:
        The global ErrorMonitoringMiddleware instance.

    Raises:
        RuntimeError: If middleware has not been initialized yet.

    Example:
        ```python
        from app.middleware import get_global_error_monitor

        monitor = get_global_error_monitor()
        metrics = monitor.get_error_metrics()
        ```
    """
    global _global_instance
    if _global_instance is None:
        raise RuntimeError("Error monitoring middleware not initialized")
    return _global_instance


class ErrorMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive error monitoring and tracking.

    Tracks HTTP errors, exceptions, and provides detailed metrics
    for monitoring system health and detecting reliability issues.

    The middleware automatically:
    - Records all 4xx and 5xx errors
    - Tracks consecutive failures per endpoint
    - Generates alerts when thresholds are exceeded
    - Maintains error history with configurable retention
    - Detects provider from request path patterns

    Attributes:
        error_history: Deque of all error records (limited by max_error_history)
        error_counts: Error count per endpoint
        provider_error_counts: Error count per provider
        status_code_counts: Error count per HTTP status code
        recent_errors: Last 100 errors for quick access
        consecutive_failures: Current consecutive failure count per endpoint
        last_success_times: Timestamp of last successful request per endpoint
        active_alerts: Set of currently active alert keys

    Example:
        ```python
        app = FastAPI()
        app.add_middleware(
            ErrorMonitoringMiddleware,
            max_error_history=1000,
            alert_threshold=10
        )
        ```
    """

    def __init__(self, app, max_error_history: int = 1000, alert_threshold: int = 10):
        """
        Initialize error monitoring middleware.

        Args:
            app: FastAPI application instance
            max_error_history: Maximum number of error records to keep in memory.
                Oldest errors are automatically discarded when limit is reached.
            alert_threshold: Number of consecutive errors before triggering an alert.
                Alerts are logged at CRITICAL level and tracked in active_alerts.

        Example:
            ```python
            app.add_middleware(
                ErrorMonitoringMiddleware,
                max_error_history=2000,  # Store last 2000 errors
                alert_threshold=5        # Alert after 5 consecutive failures
            )
            ```
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

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process request and track any errors that occur.

        This is the main middleware entry point. It wraps each request
        and tracks success/failure outcomes, recording detailed error
        information when problems occur.

        Behavior:
        - 2xx-3xx: Track as success, reset consecutive failure counter
        - 4xx: Track as client error, log warning
        - 5xx or exception: Track as server error, increment failure counter, check alerts

        Args:
            request: Incoming HTTP request to process
            call_next: Next middleware or endpoint handler in the chain

        Returns:
            HTTP response from the handler (or error response if exception occurred)

        Example:
            This method is called automatically by FastAPI middleware system.
            No need to invoke it manually.
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
        """Extract the endpoint path from request.

        Creates a unique identifier for each endpoint combining
        HTTP method and URL path.

        Args:
            request: HTTP request to extract endpoint from

        Returns:
            Endpoint identifier in format "METHOD /path"

        Example:
            ```python
            # Returns "GET /api/summoner/by-name"
            endpoint = self._get_endpoint_path(request)
            ```
        """
        return f"{request.method} {request.url.path}"

    def _detect_provider(self, path: str) -> Optional[str]:
        """Detect which provider is likely handling the request based on path.

        Uses pattern matching against known provider URL patterns to determine
        which backend service (Riot API, Data Dragon, etc.) is handling the request.

        Args:
            path: URL path to analyze

        Returns:
            Provider name ("riot_api", "data_dragon", "community_dragon")
            or "unknown" if no pattern matches

        Example:
            ```python
            provider = self._detect_provider("/lol/summoner/v4/summoners/by-name")
            # Returns: "riot_api"
            ```
        """
        path_lower = path.lower()

        for provider, patterns in self.provider_patterns.items():
            if any(pattern in path_lower for pattern in patterns):
                return provider

        return "unknown"

    def _track_success(self, endpoint: str):
        """Track successful request to reset consecutive failure counter.

        Called on every 2xx/3xx response to clear failure tracking and
        update last success time.

        Side effects:
        - Resets consecutive_failures counter to 0
        - Updates last_success_times timestamp
        - Clears any active alerts for this endpoint

        Args:
            endpoint: Endpoint identifier to track success for

        Example:
            ```python
            # Called automatically on successful responses
            self._track_success("GET /api/summoner")
            ```
        """
        self.consecutive_failures[endpoint] = 0
        self.last_success_times[endpoint] = time.time()

        # Clear any existing alerts for this endpoint
        alert_key = f"consecutive_failures:{endpoint}"
        self.active_alerts.discard(alert_key)

    def _track_client_error(self, request: Request, response: Response, start_time: float):
        """Track client errors (4xx) with detailed logging.

        Records 4xx errors in error history and logs them as warnings.
        Client errors don't count toward consecutive failures since
        they typically indicate user mistakes rather than system problems.

        Args:
            request: HTTP request that caused the error
            response: Error response being returned
            start_time: Timestamp when request processing started

        Example:
            ```python
            # Called automatically for 4xx responses
            self._track_client_error(request, response, start_time)
            ```
        """
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
        """Handle server errors with comprehensive tracking.

        Creates error record, increments consecutive failure counter,
        checks for alert conditions, and returns standardized error response.

        Args:
            request: HTTP request that caused the error
            exc: Exception that was raised
            start_time: Timestamp when request processing started

        Returns:
            JSONResponse with 500 status and OpenAPI-compliant error format

        Example:
            ```python
            # Called automatically when exceptions occur
            response = await self._handle_server_error(request, exc, start_time)
            ```
        """
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

        # Return standardized error response in OpenAPI Error format
        error_content = format_error_response(
            status_code=500,
            message=f"Internal server error: {type(exc).__name__}",
        )

        return JSONResponse(
            status_code=500,
            content=error_content,
        )

    def _record_error(self, error_record: ErrorRecord):
        """Record error in tracking data structures.

        Adds error to history and updates all relevant counters.
        Automatically handles deque rotation when limits are reached.

        Args:
            error_record: Error record to store

        Example:
            ```python
            record = ErrorRecord(
                timestamp=time.time(),
                endpoint="GET /api/summoner",
                status_code=500,
                ...
            )
            self._record_error(record)
            ```
        """
        # Add to history
        self.error_history.append(error_record)
        self.recent_errors.append(error_record)

        # Update counters
        self.error_counts[error_record.endpoint] += 1
        self.status_code_counts[error_record.status_code] += 1

        if error_record.provider:
            self.provider_error_counts[error_record.provider] += 1

    def _check_alert_conditions(
        self, endpoint: str, provider: Optional[str], consecutive_failures: int
    ):
        """Check if error conditions warrant an alert.

        Triggers CRITICAL log alert when consecutive failures exceed threshold.
        Implements cooldown period to prevent alert spam.

        Args:
            endpoint: Endpoint experiencing failures
            provider: Provider handling the endpoint (or None if unknown)
            consecutive_failures: Current count of consecutive failures

        Example:
            ```python
            # Called automatically after server errors
            self._check_alert_conditions("GET /api/summoner", "riot_api", 10)
            ```
        """
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

        Aggregates error data across multiple dimensions:
        - Total errors (all-time within history limit)
        - Server vs client errors
        - Recent errors (5min and 1hour windows)
        - Breakdown by endpoint, provider, and status code
        - Consecutive failure tracking
        - Active alert status

        Returns:
            ErrorMetrics object with current error statistics

        Example:
            ```python
            from app.middleware import get_global_error_monitor

            monitor = get_global_error_monitor()
            metrics = monitor.get_error_metrics()
            print(f"Total errors: {metrics.total_errors}")
            print(f"Server errors: {metrics.server_errors}")
            print(f"Errors by provider: {metrics.error_rates_by_provider}")
            ```
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

        Retrieves the most recent errors from the error history,
        useful for debugging and displaying in admin dashboards.

        Args:
            limit: Maximum number of errors to return (defaults to 50)

        Returns:
            List of recent error records, newest first

        Example:
            ```python
            monitor = get_global_error_monitor()
            recent = monitor.get_recent_errors(limit=10)
            for error in recent:
                print(f"{error.endpoint} - {error.status_code}")
            ```
        """
        return list(self.recent_errors)[-limit:]

    def reset_metrics(self):
        """Reset all error tracking metrics.

        Clears all error history, counters, and active alerts.
        Useful for testing or after resolving system issues.

        Warning:
            This permanently deletes all tracked error data.
            Use with caution in production environments.

        Example:
            ```python
            monitor = get_global_error_monitor()
            monitor.reset_metrics()  # Clear all error history
            ```
        """
        self.error_history.clear()
        self.error_counts.clear()
        self.provider_error_counts.clear()
        self.status_code_counts.clear()
        self.recent_errors.clear()
        self.consecutive_failures.clear()
        self.last_success_times.clear()
        self.active_alerts.clear()
        logger.info("Error monitoring metrics reset")
