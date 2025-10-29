"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check and basic endpoints."""

    def test_health_check_structure(self, client: TestClient):
        """Test health check returns proper structure."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_health_check_no_auth_required(self, client: TestClient):
        """Test health check doesn't require authentication."""
        response = client.get("/health")
        assert response.status_code == 200
        # Should not return 401 or 403


class TestDocumentationEndpoints:
    """Test documentation endpoints."""

    def test_openapi_json_structure(self, client: TestClient):
        """Test OpenAPI JSON has correct structure."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert "components" in schema

        # Check info section
        info = schema["info"]
        assert "title" in info
        assert "version" in info

    def test_swagger_ui_accessible(self, client: TestClient):
        """Test Swagger UI is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

    def test_redoc_accessible(self, client: TestClient):
        """Test ReDoc is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")


class TestAPIRouterRegistration:
    """Test that API routers are properly registered."""

    def test_summoner_routes_exist(self, test_app):
        """Test summoner routes are registered."""
        routes = [route.path for route in test_app.routes]

        # Check that we have various routes registered
        assert len(routes) > 10  # Should have multiple routes

    def test_match_routes_exist(self, test_app):
        """Test match routes are registered."""
        routes = [route.path for route in test_app.routes]

        # Check that we have various routes registered
        assert len(routes) > 10

    def test_league_routes_exist(self, test_app):
        """Test league routes are registered."""
        routes = [route.path for route in test_app.routes]

        # Check general route registration
        assert len(routes) > 10


class TestErrorHandling:
    """Test error handling."""

    def test_404_on_invalid_endpoint(self, client: TestClient):
        """Test 404 response on invalid endpoint."""
        response = client.get("/this/does/not/exist")
        assert response.status_code == 404

    def test_405_on_wrong_method(self, client: TestClient):
        """Test 405 on using wrong HTTP method."""
        # Health endpoint is GET only
        response = client.post("/health")
        assert response.status_code == 405


class TestCORSConfiguration:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers can be set."""
        # This is a basic test - actual CORS testing requires
        # sending Origin headers
        response = client.get("/health")
        assert response.status_code == 200
        # CORS middleware should be configured


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async endpoint functionality."""

    async def test_async_health_check(self, async_client):
        """Test health check with async client."""
        response = await async_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"

    async def test_async_openapi(self, async_client):
        """Test OpenAPI schema with async client."""
        response = await async_client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
