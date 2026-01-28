"""
Demo endpoint tests for MenuPilot.

Tests the demo functionality that judges will use to evaluate the project.
"""

import pytest


@pytest.mark.anyio
async def test_demo_session_endpoint(client):
    """Test demo session loads correctly for judges."""
    response = await client.get("/api/v1/demo/session")
    assert response.status_code == 200
    
    data = response.json()
    assert "session_id" in data
    assert "menu" in data
    assert "bcg" in data or "bcg_analysis" in data
    assert "campaigns" in data


@pytest.mark.anyio
async def test_demo_load_endpoint(client):
    """Test demo load creates a usable session."""
    response = await client.get("/api/v1/demo/load")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "loaded"
    assert "session_id" in data
    assert data["items_count"] > 0


@pytest.mark.anyio
async def test_demo_session_has_menu_items(client):
    """Test demo session has valid menu items."""
    response = await client.get("/api/v1/demo/session")
    assert response.status_code == 200
    
    data = response.json()
    menu = data.get("menu", {})
    items = menu.get("items", [])
    
    assert len(items) > 0, "Demo should have menu items"
    
    # Check item structure
    for item in items:
        assert "name" in item, "Menu item should have name"
        assert "price" in item, "Menu item should have price"


@pytest.mark.anyio
async def test_demo_session_has_bcg_analysis(client):
    """Test demo session has BCG analysis results."""
    response = await client.get("/api/v1/demo/session")
    assert response.status_code == 200
    
    data = response.json()
    bcg = data.get("bcg") or data.get("bcg_analysis", {})
    
    assert "classifications" in bcg or "summary" in bcg, "Demo should have BCG analysis"


@pytest.mark.anyio
async def test_demo_session_has_campaigns(client):
    """Test demo session has generated campaigns."""
    response = await client.get("/api/v1/demo/session")
    assert response.status_code == 200
    
    data = response.json()
    campaigns = data.get("campaigns", {})
    
    # Campaigns can be in different formats
    if isinstance(campaigns, dict):
        campaign_list = campaigns.get("campaigns", [])
    else:
        campaign_list = campaigns
    
    assert len(campaign_list) > 0, "Demo should have campaigns"


@pytest.mark.anyio
async def test_session_retrieval_after_demo_load(client):
    """Test that session can be retrieved after demo load."""
    # First load demo
    load_response = await client.get("/api/v1/demo/load")
    assert load_response.status_code == 200
    session_id = load_response.json()["session_id"]
    
    # Then retrieve session
    session_response = await client.get(f"/api/v1/session/{session_id}")
    assert session_response.status_code == 200
    
    data = session_response.json()
    assert data["session_id"] == session_id
    assert "data" in data
