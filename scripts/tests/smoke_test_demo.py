import pytest
import json
import os
from pathlib import Path

# Paths
DEMO_DATA_DIR = Path("backend/data/demo")

def test_demo_files_exist():
    """Verify all critical demo files were generated."""
    required_files = [
        "menu.json",
        "bcg.json",
        "campaigns.json",
        "session.json",
        "sales.json",
        "restaurant_info.json"
    ]
    
    for filename in required_files:
        file_path = DEMO_DATA_DIR / filename
        assert file_path.exists(), f"Missing critical demo file: {filename}"
        
        # Verify valid JSON
        with open(file_path, "r") as f:
            data = json.load(f)
            assert data is not None, f"File {filename} is empty or invalid JSON"

def test_restaurant_identity():
    """Verify the demo data matches 'Margarita Pinta' identity."""
    with open(DEMO_DATA_DIR / "restaurant_info.json", "r") as f:
        info = json.load(f)
        assert info["name"] == "Margarita Pinta"
        assert "Pasto" in info["location"]
        assert "margaritapintapasto" in info["social_media"]["instagram"]

def test_menu_content():
    """Verify menu contains real items from the full CSV."""
    with open(DEMO_DATA_DIR / "menu.json", "r") as f:
        menu = json.load(f)
        items = {item["name"] for item in menu["items"]}
        
        # Should have significantly more items now
        assert len(items) > 100, f"Expected >100 items, found {len(items)}"
        
        # Check for specific real items from the CSV
        assert "Margarita Ardiente" in items
        assert "Costillas San Luis BBQ" in items
        
        # Check categories
        categories = {item["category"] for item in menu["items"]}
        assert "Coctelería" in categories
        assert "Costillas" in categories
        assert "Hamburguesas" in categories

def test_campaign_generation():
    """Verify campaigns are contextual to the restaurant."""
    with open(DEMO_DATA_DIR / "campaigns.json", "r") as f:
        campaigns = json.load(f)
        
        # Should have 3 campaigns now
        assert len(campaigns["campaigns"]) >= 3
        
        titles = [c["title"] for c in campaigns["campaigns"]]
        # We expect at least one dynamic title based on top stars
        assert any("Noches de" in t for t in titles)

def test_full_session_structure():
    """Verify the session.json contains all new analysis sections."""
    with open(DEMO_DATA_DIR / "session.json", "r") as f:
        session = json.load(f)
        
        assert "competitor_analysis" in session
        assert "sentiment_analysis" in session
        assert "predictions" in session
        assert len(session["competitor_analysis"]["competitors"]) >= 3
        assert session["sentiment_analysis"]["overall"]["score"] > 0


def test_sales_data_volume():
    """Verify sales data generation volume and structure."""
    with open(DEMO_DATA_DIR / "sales.json", "r") as f:
        sales = json.load(f)
        
        # Should have substantial data (90 days)
        assert len(sales) > 100
        
        # Check structure
        sample = sales[0]
        assert "date" in sample
        assert "item_name" in sample
        assert "revenue" in sample
