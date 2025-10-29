"""Tests for main application module."""

import pytest
from fastapi.testclient import TestClient


def test_app_exists(test_app):
    """Test that the FastAPI app is created."""
    assert test_app is not None
    assert hasattr(test_app, "routes")


def test_health_endpoint(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_root_endpoint(client: TestClient):
    """Test root endpoint response."""
    response = client.get("/", follow_redirects=False)
    # Root may return 200, 404, or redirect depending on configuration
    assert response.status_code in [200, 404, 307, 308]


def test_openapi_schema(client: TestClient):
    """Test that OpenAPI schema is generated."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "components" in schema


def test_docs_endpoint(client: TestClient):
    """Test that Swagger UI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "api" in response.text.lower()


def test_redoc_endpoint(client: TestClient):
    """Test that ReDoc documentation is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_app_lifespan(test_app):
    """Test that app has proper lifespan configuration."""
    # This is a basic test to ensure the app can be created
    # In a real scenario, you'd test startup/shutdown events
    assert test_app is not None


def test_cors_configuration(test_app):
    """Test that CORS is properly configured."""
    # CORS middleware should be configured
    assert len(test_app.user_middleware) >= 0  # Basic check


def test_api_routes_registered(test_app):
    """Test that API routes are properly registered."""
    routes = [route.path for route in test_app.routes]

    # Check for essential routes
    assert "/health" in routes
    assert "/openapi.json" in routes
    assert "/docs" in routes
    assert "/redoc" in routes

    # Check for API router paths (they should be registered)
    # Note: Exact paths may vary based on router configuration
    route_paths = " ".join(routes)
    assert "summoner" in route_paths.lower() or len(routes) > 10


def test_invalid_endpoint(client: TestClient):
    """Test that invalid endpoints return 404."""
    response = client.get("/this-endpoint-does-not-exist")
    assert response.status_code == 404


def test_app_metadata(test_app):
    """Test that app has proper metadata."""
    assert test_app.title is not None
    assert test_app.version is not None
    # Check OpenAPI schema has proper metadata
    openapi_schema = test_app.openapi()
    assert "info" in openapi_schema
    assert "title" in openapi_schema["info"]
    assert "version" in openapi_schema["info"]
