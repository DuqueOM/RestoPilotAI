"""
API endpoint tests for MenuPilot.

Tests cover health checks and basic API functionality.
"""

import pytest


@pytest.mark.anyio
async def test_root_endpoint(client):
    """Test root endpoint returns API info."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "MenuPilot API"
    assert data["status"] == "operational"
    assert "docs" in data


@pytest.mark.anyio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "gemini_configured" in data


@pytest.mark.anyio
async def test_api_docs_accessible(client):
    """Test that OpenAPI docs are accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_openapi_schema(client):
    """Test OpenAPI schema is valid."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "MenuPilot API"
    assert "paths" in schema


@pytest.mark.anyio
async def test_ingest_menu_requires_file(client):
    """Test menu ingestion endpoint requires a file."""
    response = await client.post("/api/v1/ingest/menu")
    # Should return 422 (validation error) without file
    assert response.status_code == 422


@pytest.mark.anyio
async def test_bcg_analysis_requires_session(client):
    """Test BCG analysis requires valid session."""
    response = await client.post("/api/v1/analyze/bcg?session_id=invalid-session")
    # Should return 404 for invalid session
    assert response.status_code == 404
