"""
Error response formatting utilities.

Provides functions to format error responses conforming to the OpenAPI
error specification.
"""

from typing import Any, Sequence

from app.models.errors import ErrorResponse, ErrorStatus


def format_error_response(status_code: int, message: str) -> dict[str, Any]:
    """
    Format an error response conforming to OpenAPI specification.

    Creates a standardized error response structure that can be returned
    by exception handlers and middleware.

    Args:
        status_code: HTTP status code (400-599)
        message: Human-readable error message

    Returns:
        Dictionary containing formatted error response in OpenAPI Error schema format

    Example:
        >>> format_error_response(404, "Resource not found: summoner")
        {
            "status": {
                "status_code": 404,
                "message": "Resource not found: summoner"
            }
        }
    """
    error_response = ErrorResponse(
        status=ErrorStatus(
            status_code=status_code,
            message=message,
        )
    )
    return error_response.model_dump()


def format_validation_error(
    validation_errors: Sequence[dict[str, Any]] | list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Format validation errors into standardized error response.

    Converts FastAPI/Pydantic validation errors into the OpenAPI error format.

    Args:
        validation_errors: List of validation error dictionaries from FastAPI

    Returns:
        Formatted error response with 400 status code

    Example:
        >>> errors = [{"loc": ["body", "name"], "msg": "field required"}]
        >>> format_validation_error(errors)
        {
            "status": {
                "status_code": 400,
                "message": "Invalid request parameters: field required at body.name"
            }
        }
    """
    # Extract first error for simple message (could be enhanced to include all errors)
    if validation_errors:
        first_error = validation_errors[0]
        location = ".".join(str(loc) for loc in first_error.get("loc", []))
        msg = first_error.get("msg", "Validation error")
        message = f"Invalid request parameters: {msg} at {location}"
    else:
        message = "Invalid request parameters: Validation failed"

    return format_error_response(400, message)


def get_standard_error_message(status_code: int, default_message: str | None = None) -> str:
    """
    Get standardized error message for a given status code.

    Provides consistent error messages across the API for common status codes.

    Args:
        status_code: HTTP status code
        default_message: Optional default message to use if no standard message exists

    Returns:
        Standardized error message for the status code

    Example:
        >>> get_standard_error_message(401)
        "Unauthorized: Invalid or missing API key"
    """
    standard_messages = {
        400: "Invalid request parameters",
        401: "Unauthorized: Invalid or missing API key",
        403: "Forbidden: API key does not have access",
        404: "Resource not found",
        429: "Rate limit exceeded",
        500: "Internal server error",
        503: "Service temporarily unavailable",
    }

    return standard_messages.get(status_code, default_message or "An error occurred")
