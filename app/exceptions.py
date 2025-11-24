"""
Custom exceptions for standardized HTTP error responses.

All exceptions inherit from FastAPI's HTTPException and include
appropriate status codes and error messages conforming to the
OpenAPI error specification.
"""

from typing import Any

from fastapi import HTTPException, status


class RiotAPIException(HTTPException):
    """
    Base exception for all Riot API-related errors.

    Provides common functionality for error handling and logging.
    All specific error types should inherit from this base class.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        headers: dict[str, Any] | None = None,
    ):
        """
        Initialize Riot API exception.

        Args:
            status_code: HTTP status code
            message: Human-readable error message
            headers: Optional HTTP headers to include in response
        """
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.message = message


class BadRequestException(RiotAPIException):
    """
    400 Bad Request - Invalid request parameters.

    Raised when the client sends malformed or invalid request data.
    Uses exact error message from Riot API without modification.
    """

    def __init__(self, message: str = "Bad Request", details: str | None = None):
        """
        Initialize BadRequestException.

        Args:
            message: Error message (default used only if no details provided)
            details: Exact error message from Riot API (preferred)
        """
        # Use details if provided (exact Riot message), otherwise use message
        final_message = details if details else message
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=final_message)


class UnauthorizedException(RiotAPIException):
    """
    401 Unauthorized - Missing or invalid API key.

    Raised when authentication credentials are missing or invalid.
    Uses exact error message from Riot API without modification.
    """

    def __init__(self, message: str = "Unauthorized"):
        """
        Initialize UnauthorizedException.

        Args:
            message: Exact error message from Riot API
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            headers={"WWW-Authenticate": "ApiKey"},
        )


class ForbiddenException(RiotAPIException):
    """
    403 Forbidden - API key does not have required permissions.

    Raised when the API key is valid but lacks access to the requested resource.
    Uses exact error message from Riot API without modification.
    """

    def __init__(self, message: str = "Forbidden"):
        """
        Initialize ForbiddenException.

        Args:
            message: Exact error message from Riot API
        """
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message)


class NotFoundException(RiotAPIException):
    """
    404 Not Found - Requested resource does not exist.

    Raised when the requested resource (summoner, match, etc.) cannot be found.
    Uses exact error message from Riot API without modification.
    """

    def __init__(self, resource_type: str = "Data not found"):
        """
        Initialize NotFoundException.

        Args:
            resource_type: Exact error message from Riot API (parameter name kept for compatibility)
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=resource_type,  # Use as-is, no wrapping
        )


class RateLimitException(RiotAPIException):
    """
    429 Too Many Requests - Rate limit exceeded.

    Raised when the API rate limit is exceeded. Includes Retry-After header
    indicating when the client can retry the request.
    Uses exact error message from Riot API when available.
    """

    def __init__(self, retry_after: int = 1, message: str | None = None):
        """
        Initialize RateLimitException.

        Args:
            retry_after: Number of seconds to wait before retrying
            message: Exact error message from Riot API (if None, uses default)
        """
        # Use exact Riot message if provided, otherwise use default
        final_message = (
            message if message else f"Rate limit exceeded. Retry after {retry_after} seconds"
        )
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=final_message,
            headers={"Retry-After": str(retry_after)},
        )
        self.retry_after = retry_after


class InternalServerException(RiotAPIException):
    """
    500 Internal Server Error - Unexpected server error.

    Raised when an unexpected error occurs during request processing.
    Uses exact error message from Riot API when available.
    """

    def __init__(self, error_type: str = "Internal server error", details: str | None = None):
        """
        Initialize InternalServerException.

        Args:
            error_type: Exact error message from Riot API (or error type if gateway-generated)
            details: Optional additional error details (only used for gateway-generated errors)
        """
        # For Riot API errors: use error_type as-is (exact message)
        # For gateway errors: combine error_type and details
        if details:
            message = f"{error_type}: {details}"
        else:
            message = error_type
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=message)


class ServiceUnavailableException(RiotAPIException):
    """
    503 Service Unavailable - External service is temporarily unavailable.

    Raised when the Riot API or another external service cannot be reached.
    """

    def __init__(self, message: str = "Service temporarily unavailable"):
        """
        Initialize ServiceUnavailableException.

        Args:
            message: Error message describing the service unavailability
        """
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            headers={"Retry-After": "60"},  # Suggest retrying after 1 minute
        )


# HTTP Status Code to Exception mapping for easy lookup
STATUS_CODE_TO_EXCEPTION: dict[int, type[RiotAPIException]] = {
    400: BadRequestException,
    401: UnauthorizedException,
    403: ForbiddenException,
    404: NotFoundException,
    429: RateLimitException,
    500: InternalServerException,
    503: ServiceUnavailableException,
}


def get_exception_for_status_code(
    status_code: int,
    message: str | None = None,
    **kwargs: Any,
) -> RiotAPIException:
    """
    Get the appropriate exception instance for a given status code.

    Args:
        status_code: HTTP status code
        message: Optional custom error message
        **kwargs: Additional keyword arguments to pass to exception constructor

    Returns:
        Instance of the appropriate exception class

    Example:
        >>> exc = get_exception_for_status_code(404, resource_type="summoner")
        >>> raise exc
    """
    # Handle different exception constructors with their specific signatures
    if status_code == 404 and "resource_type" in kwargs:
        return NotFoundException(resource_type=kwargs["resource_type"])
    elif status_code == 429 and "retry_after" in kwargs:
        return RateLimitException(retry_after=kwargs["retry_after"])
    elif status_code == 400:
        return BadRequestException(message=message or "Invalid request parameters")
    elif status_code == 401:
        return UnauthorizedException(message=message or "Unauthorized")
    elif status_code == 403:
        return ForbiddenException(message=message or "Forbidden")
    elif status_code == 500:
        return InternalServerException(error_type=message or "Internal server error")
    elif status_code == 503:
        return ServiceUnavailableException(message=message or "Service temporarily unavailable")
    else:
        # Default for unmapped status codes
        return InternalServerException(error_type=message or "An error occurred")
