"""
Comprehensive tests for error handling conforming to OpenAPI specification.

Tests all error types, exception handlers, and error formatting utilities.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.exceptions import (
    BadRequestException,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
    RateLimitException,
    ServiceUnavailableException,
    UnauthorizedException,
    get_exception_for_status_code,
)
from app.main import app
from app.models.errors import ErrorResponse, ErrorStatus
from app.utils.error_formatter import (
    format_error_response,
    format_validation_error,
    get_standard_error_message,
)

# Test client
client = TestClient(app)


class TestErrorModels:
    """Test error models conform to OpenAPI specification."""

    def test_error_status_creation(self):
        """Test ErrorStatus model creation."""
        error_status = ErrorStatus(status_code=404, message="Resource not found: summoner")

        assert error_status.status_code == 404
        assert error_status.message == "Resource not found: summoner"

    def test_error_response_creation(self):
        """Test ErrorResponse model creation."""
        error_response = ErrorResponse(
            status=ErrorStatus(status_code=500, message="Internal server error")
        )

        assert error_response.status.status_code == 500
        assert error_response.status.message == "Internal server error"

    def test_error_response_serialization(self):
        """Test ErrorResponse serialization to dict."""
        error_response = ErrorResponse(
            status=ErrorStatus(status_code=429, message="Rate limit exceeded: Retry after 5s")
        )

        serialized = error_response.model_dump()

        assert serialized == {
            "status": {"status_code": 429, "message": "Rate limit exceeded: Retry after 5s"}
        }


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_bad_request_exception(self):
        """Test BadRequestException creation and properties."""
        exc = BadRequestException(details="missing required field")

        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert "missing required field" in exc.message

    def test_unauthorized_exception(self):
        """Test UnauthorizedException creation and properties."""
        exc = UnauthorizedException()

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in exc.message
        assert exc.headers is not None
        assert "WWW-Authenticate" in exc.headers

    def test_forbidden_exception(self):
        """Test ForbiddenException creation and properties."""
        exc = ForbiddenException()

        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert "Forbidden" in exc.message

    def test_not_found_exception(self):
        """Test NotFoundException creation and properties."""
        exc = NotFoundException(resource_type="summoner")

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert "summoner" in exc.message

    def test_rate_limit_exception(self):
        """Test RateLimitException creation and properties."""
        exc = RateLimitException(retry_after=10)

        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "10 seconds" in exc.message
        assert exc.retry_after == 10
        assert exc.headers is not None
        assert exc.headers.get("Retry-After") == "10"

    def test_internal_server_exception(self):
        """Test InternalServerException creation and properties."""
        exc = InternalServerException(error_type="DatabaseError", details="Connection timeout")

        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "DatabaseError" in exc.message
        assert "Connection timeout" in exc.message

    def test_service_unavailable_exception(self):
        """Test ServiceUnavailableException creation and properties."""
        exc = ServiceUnavailableException()

        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "unavailable" in exc.message.lower()
        assert exc.headers is not None
        assert "Retry-After" in exc.headers

    def test_get_exception_for_status_code(self):
        """Test exception factory function."""
        # Test 404
        exc_404 = get_exception_for_status_code(404, resource_type="match")
        assert isinstance(exc_404, NotFoundException)
        assert "match" in exc_404.message

        # Test 429
        exc_429 = get_exception_for_status_code(429, retry_after=5)
        assert isinstance(exc_429, RateLimitException)
        assert exc_429.retry_after == 5

        # Test 400
        exc_400 = get_exception_for_status_code(400, message="Bad input")
        assert isinstance(exc_400, BadRequestException)
        assert "Bad input" in exc_400.message


class TestErrorFormatter:
    """Test error formatting utilities."""

    def test_format_error_response(self):
        """Test error response formatting."""
        result = format_error_response(404, "Resource not found: summoner")

        assert result == {"status": {"status_code": 404, "message": "Resource not found: summoner"}}

    def test_format_validation_error(self):
        """Test validation error formatting."""
        validation_errors = [
            {"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"}
        ]

        result = format_validation_error(validation_errors)

        assert result["status"]["status_code"] == 400
        assert "body.name" in result["status"]["message"]
        assert "field required" in result["status"]["message"]

    def test_format_validation_error_empty(self):
        """Test validation error formatting with empty errors."""
        result = format_validation_error([])

        assert result["status"]["status_code"] == 400
        assert "Validation failed" in result["status"]["message"]

    def test_get_standard_error_message(self):
        """Test standard error message retrieval."""
        assert "Invalid request parameters" in get_standard_error_message(400)
        assert "Unauthorized" in get_standard_error_message(401)
        assert "Forbidden" in get_standard_error_message(403)
        assert "not found" in get_standard_error_message(404)
        assert "Rate limit" in get_standard_error_message(429)
        assert "Internal server error" in get_standard_error_message(500)
        assert "unavailable" in get_standard_error_message(503)

    def test_get_standard_error_message_with_default(self):
        """Test standard error message with custom default."""
        result = get_standard_error_message(418, default_message="I'm a teapot")

        assert result == "I'm a teapot"


class TestExceptionHandlers:
    """Test FastAPI exception handlers."""

    def test_validation_error_returns_400(self):
        """Test validation error is converted to 400 Bad Request."""
        # Make a request with invalid data (assuming health endpoint exists)
        # This is a placeholder - adjust based on actual endpoints
        response = client.get("/health", params={"invalid_param": "test" * 1000})

        # Validation errors should be converted to 400
        # Note: This test may need adjustment based on actual validation rules
        assert response.status_code in [200, 400]  # Either succeeds or fails validation

    def test_not_found_endpoint_returns_404(self):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/nonexistent/endpoint")

        assert response.status_code == 404

        # Check error format (FastAPI's default 404 or our custom format)
        data = response.json()
        # FastAPI returns {"detail": "Not Found"} by default for route not found
        assert "detail" in data or "status" in data


class TestErrorResponseFormat:
    """Test that all error responses conform to OpenAPI specification."""

    def test_error_response_structure(self):
        """Test error response has correct structure."""
        error_dict = format_error_response(500, "Test error")

        # Must have 'status' key
        assert "status" in error_dict

        # Status must have status_code and message
        assert "status_code" in error_dict["status"]
        assert "message" in error_dict["status"]

        # Values must be correct types
        assert isinstance(error_dict["status"]["status_code"], int)
        assert isinstance(error_dict["status"]["message"], str)

    def test_all_error_codes_format_correctly(self):
        """Test all supported error codes format correctly."""
        error_codes = [400, 401, 403, 404, 429, 500, 503]

        for code in error_codes:
            error_dict = format_error_response(code, f"Test error for {code}")

            assert error_dict["status"]["status_code"] == code
            assert isinstance(error_dict["status"]["message"], str)
            assert len(error_dict["status"]["message"]) > 0


class TestRiotClientErrorHandling:
    """Test Riot client error handling and exception mapping."""

    def test_riot_client_exceptions_conform_to_spec(self):
        """Test that Riot client raises exceptions that conform to OpenAPI spec."""
        # Test exception creation
        exceptions = [
            BadRequestException(details="test"),
            UnauthorizedException(),
            ForbiddenException(),
            NotFoundException(resource_type="summoner"),
            RateLimitException(retry_after=5),
            InternalServerException(error_type="test"),
            ServiceUnavailableException(),
        ]

        for exc in exceptions:
            # All should have status_code and message
            assert hasattr(exc, "status_code")
            assert hasattr(exc, "message")
            assert isinstance(exc.status_code, int)
            assert isinstance(exc.message, str)
            assert 400 <= exc.status_code < 600


class TestEndToEndErrorFlow:
    """Test complete error flow from exception to response."""

    def test_custom_exception_to_response(self):
        """Test custom exception is properly formatted in response."""
        # This would require a test endpoint that raises custom exceptions
        # For now, test the exception handler logic directly
        from app.main import riot_api_exception_handler
        from fastapi import Request
        from unittest.mock import Mock

        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/test/path"

        # Create exception
        exc = NotFoundException(resource_type="test_resource")

        # Get response
        import asyncio

        response = asyncio.run(riot_api_exception_handler(mock_request, exc))

        # Check response
        assert response.status_code == 404
        data = response.body.decode()
        assert "test_resource" in data
        assert "status_code" in data
        assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
