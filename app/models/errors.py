"""
Error models conforming to OpenAPI specification.

Provides standardized error response structures for all API endpoints.
"""

from pydantic import BaseModel, ConfigDict, Field


class ErrorStatus(BaseModel):
    """
    Error status details conforming to OpenAPI specification.

    Attributes:
        status_code: HTTP status code
        message: Human-readable error message
    """

    status_code: int = Field(
        ...,
        description="HTTP status code",
        ge=100,
        le=599,
        examples=[400, 404, 500],
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        min_length=1,
        examples=[
            "Invalid request parameters: missing required field",
            "Resource not found: summoner",
            "Rate limit exceeded: Retry after 1s",
        ],
    )


class ErrorResponse(BaseModel):
    """
    Standard error response wrapper conforming to OpenAPI specification.

    All API error responses use this format for consistency.

    Attributes:
        status: Error status details containing status_code and message
    """

    status: ErrorStatus = Field(
        ...,
        description="Error status details",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": {
                        "status_code": 404,
                        "message": "Resource not found: summoner",
                    }
                },
                {
                    "status": {
                        "status_code": 429,
                        "message": "Rate limit exceeded: Retry after 5s",
                    }
                },
                {
                    "status": {
                        "status_code": 500,
                        "message": "Internal server error: Database connection failed",
                    }
                },
            ]
        }
    )
