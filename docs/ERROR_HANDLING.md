# Comprehensive Error Handling Implementation

## Overview

This document describes the comprehensive error handling implementation for lolstonks-api-gateway, conforming to the OpenAPI error specification with pure passthrough of Riot API error messages.

## OpenAPI Error Schema

All error responses follow this standardized format:

```json
{
  "status": {
    "status_code": 404,
    "message": "Data not found - No results found for player with riot id NonExistentPlayer99999#NA1"
  }
}
```

## Implementation Components

### 1. Error Models (`app/models/errors.py`)

#### ErrorStatus
Pydantic model representing error status details.

**Fields:**
- `status_code` (int): HTTP status code (100-599)
- `message` (str): Human-readable error message

#### ErrorResponse
Wrapper model containing the error status.

**Fields:**
- `status` (ErrorStatus): Error status details

### 2. Custom Exceptions (`app/exceptions.py`)

All custom exceptions inherit from `RiotAPIException`, which extends FastAPI's `HTTPException`.

#### Exception Classes

| Exception | Status Code | Use Case |
|-----------|-------------|----------|
| `BadRequestException` | 400 | Invalid request parameters |
| `UnauthorizedException` | 401 | Missing/invalid API key |
| `ForbiddenException` | 403 | API key lacks permissions |
| `NotFoundException` | 404 | Resource not found |
| `RateLimitException` | 429 | Rate limit exceeded |
| `InternalServerException` | 500 | Server/application error |
| `ServiceUnavailableException` | 503 | Service down/unavailable |

#### Helper Functions

- `get_exception_for_status_code()`: Factory function to create appropriate exception instances

### 3. Error Formatter Utility (`app/utils/error_formatter.py`)

#### Functions

**`format_error_response(status_code: int, message: str) -> dict`**
- Formats errors into OpenAPI error schema
- Returns dictionary conforming to ErrorResponse model

**`format_validation_error(validation_errors: list) -> dict`**
- Converts FastAPI/Pydantic validation errors to standardized format
- Extracts location and message from validation errors

**`get_standard_error_message(status_code: int, default: str) -> str`**
- Returns standardized error messages for common status codes
- Ensures consistency across the API

### 4. Exception Handlers (`app/main.py`)

Three exception handlers registered with FastAPI:

#### `riot_api_exception_handler`
- Handles all `RiotAPIException` instances
- Logs warning with status code and message
- Returns JSONResponse with OpenAPI error format

#### `validation_exception_handler`
- Handles `RequestValidationError` (422 → 400)
- Converts validation errors to 400 Bad Request
- Formats validation details into error message

#### `generic_exception_handler`
- Catches all unhandled exceptions
- Returns 500 Internal Server Error
- Logs error with full traceback

### 5. Riot Client Integration (`app/riot/client.py`)

The Riot API client implements pure passthrough error handling with custom exception mapping.

**Error Mapping:**
- 400 → `BadRequestException` (exact Riot message)
- 401 → `UnauthorizedException` (exact Riot message)
- 403 → `ForbiddenException` (exact Riot message)
- 404 → `NotFoundException` (exact Riot message)
- 429 → `RateLimitException` (exact Riot message with retry-after header)
- 500 → `InternalServerException` (exact Riot message)
- 503 → `ServiceUnavailableException` (exact Riot message)

**Pure Passthrough Implementation:**

The `_extract_riot_message()` helper method extracts exact error messages from Riot API responses:

```python
@staticmethod
def _extract_riot_message(response: httpx.Response, fallback: str = "") -> str:
    """
    Extract the exact error message from Riot API response.

    Riot API returns errors in format: {"status": {"message": "...", "status_code": ...}}
    This method extracts the message field exactly as provided by Riot.
    """
    try:
        error_data = response.json()
        if "status" in error_data and "message" in error_data["status"]:
            return error_data["status"]["message"]
        return response.text or fallback
    except Exception:
        return fallback
```

**Key Features:**
- Zero message modification - extracts and passes through exact Riot messages
- Preserves Riot's nested JSON-string format when applicable
- Retry-After header inclusion for 429 errors
- Key rotation before raising 429 exception
- Detailed error logging with exact Riot messages

### 6. Error Monitoring Middleware (`app/middleware/error_monitoring.py`)

Updated to use OpenAPI error format:
- Returns errors in `ErrorResponse` format
- Tracks all errors in monitoring metrics
- Preserves existing error tracking functionality

## Error Messages

### Pure Passthrough Approach

The gateway implements a **pure passthrough** strategy for error messages, returning the exact error message from the Riot API without any modification, wrapping, or prefixing.

**Implementation Details:**
- `_extract_riot_message()` helper method in `app/riot/client.py` extracts exact messages from Riot's JSON error format
- All exception classes accept and preserve Riot messages without modification
- No message templates or prefixes applied to Riot API errors
- Gateway-generated errors (e.g., internal failures, validation errors) use descriptive messages only when Riot message unavailable

**Example Riot API Error Format:**
```json
{
  "status": {
    "message": "Bad Request - Exception decrypting INVALID_PUUID",
    "status_code": 400
  }
}
```

**Gateway Returns Exactly:**
```json
{
  "status": {
    "status_code": 400,
    "message": "Bad Request - Exception decrypting INVALID_PUUID"
  }
}
```

**Preserved Nested JSON Format:**

When Riot returns nested JSON as a string, the gateway preserves this format:

```json
{
  "status": {
    "status_code": 404,
    "message": "{\"httpStatus\":404,\"errorCode\":\"NOT_FOUND\",\"message\":\"Not Found\",\"implementationDetails\":\"spectator game info isn't found\"}"
  }
}
```

**Verification:** See `TEST_RESULTS.md` for pure passthrough verification with real Riot API responses.

## Usage Examples

### Raising Custom Exceptions with Exact Riot Messages

```python
from app.exceptions import NotFoundException, RateLimitException, BadRequestException
from app.riot.client import RiotAPIClient

# Extract exact Riot message from response
riot_message = RiotAPIClient._extract_riot_message(response)

# Pass exact message through without modification
raise NotFoundException(resource_type=riot_message)

# For rate limit errors with retry-after and optional Riot message
raise RateLimitException(retry_after=10, message=riot_message)

# For bad request errors with exact Riot details
raise BadRequestException(details=riot_message)
```

### Error Response Format - Pure Passthrough Examples

All endpoints return errors with exact Riot API messages:

```json
// 404 Response - Exact Riot Message
{
  "status": {
    "status_code": 404,
    "message": "Data not found - No results found for player with riot id NonExistentPlayer99999#NA1"
  }
}

// 400 Response - Exact Riot Message
{
  "status": {
    "status_code": 400,
    "message": "Bad Request - Exception decrypting INVALID_PUUID"
  }
}

// 404 Response - Preserves Riot's Nested JSON Format
{
  "status": {
    "status_code": 404,
    "message": "{\"httpStatus\":404,\"errorCode\":\"NOT_FOUND\",\"message\":\"Not Found\",\"implementationDetails\":\"spectator game info isn't found\"}"
  }
}

// 429 Response - With Retry-After header
{
  "status": {
    "status_code": 429,
    "message": "Rate limit exceeded"
  }
}
```
Headers: `Retry-After: 5`

**Note:** All messages are extracted directly from Riot API responses without modification.

## Testing

Comprehensive test suite in `tests/test_error_handling.py`:

**Test Coverage:**
- Error model creation and serialization
- Custom exception properties and behavior
- Error formatter utilities
- Exception handlers
- End-to-end error flow
- Pure passthrough verification

**Run Tests:**
```bash
cd lolstonks-api-gateway
uv run pytest tests/test_error_handling.py -v
```

## Validation Error Conversion

FastAPI validation errors (422) are automatically converted to 400 Bad Request with standardized format:

**Before (422 Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**After (400 Bad Request):**
```json
{
  "status": {
    "status_code": 400,
    "message": "Invalid request parameters: field required at body.name"
  }
}
```

**Note:** Validation errors are gateway-generated (not from Riot API), so they use standardized message formatting for clarity.

## Security Best Practices

1. **No sensitive data in error messages**: Error messages avoid exposing implementation details
2. **Pure passthrough**: Riot messages passed through without revealing gateway internals
3. **Rate limiting preserved**: 429 handling includes Retry-After headers
4. **Authentication headers**: 401 responses include WWW-Authenticate header
5. **Comprehensive logging**: All errors logged with appropriate severity levels

## Integration with Existing Systems

### Error Monitoring
- All errors tracked by `ErrorMonitoringMiddleware`
- Metrics preserved for monitoring endpoints
- Alert system continues to function

### Cache System
- Cache bypass on errors maintained
- Error responses never cached

### Rate Limiting
- Rate limiter integration preserved
- 429 responses include retry information

## Migration Notes

### Breaking Changes
None - backward compatible error format change

### Deprecations
- Old error response format deprecated (but still returned by middleware for backward compatibility)
- Clients should update to use new `status` object format

## Future Enhancements

Possible future improvements:
1. Request ID tracking in errors (without modifying Riot messages)
2. Detailed error context for debugging (separate metadata field)
3. Error analytics dashboard
4. Enhanced logging for error patterns

## References

- OpenAPI Specification: `D:\LoLProjects\openAPI.json`
- Riot API Documentation: https://developer.riotgames.com/
- FastAPI Exception Handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
- Pydantic Models: https://docs.pydantic.dev/

## Change Log

### 2025-01-23
- Implemented pure passthrough error handling
- Added `_extract_riot_message()` helper method
- Updated all exception classes to preserve exact Riot messages
- Removed message wrapping and prefixes
- Verified with real Riot API responses
- Created comprehensive test suite
- Updated documentation for pure passthrough approach
