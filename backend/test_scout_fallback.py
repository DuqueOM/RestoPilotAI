
import asyncio
import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path.cwd()))

from app.services.intelligence.competitor_finder import ScoutAgent, ScoutAction
from app.services.intelligence.location import PlacesService, PlaceResult

# Mock PlacesService to force fallback
class MockPlacesService:
    async def search_nearby_restaurants(self, *args, **kwargs):
        print("   [Mock] Places API returned [] (Simulating failure)")
        return []

async def test_scout_fallback():
    print("--- Testing Scout Agent Fallback ---")
    
    agent = ScoutAgent()
    # Inject mock
    agent.places = MockPlacesService()
    
    address = "Paseo de la Reforma, Mexico City"
    print(f"1. Running scout mission for {address}...")
    
    try:
        # Mocking geocoding to avoid that call too if needed, but let's let it run if it can
        # actually, geocoding might need API key. Let's provide coordinates directly.
        
        result = await agent.run_scouting_mission(
            our_location={"lat": 19.4326, "lng": -99.1332}, # Zocalo
            our_cuisine_type="mexican",
            radius_meters=500,
            deep_analysis=False # Skip deep analysis for speed
        )
        
        print("2. Mission Complete. Checking results...")
        competitors = result.get("competitors", [])
        
        if competitors:
            print(f"   [OK] Found {len(competitors)} competitors via fallback.")
            print(f"   Sample: {competitors[0]['name']} - {competitors[0]['address']}")
            
            # Check for Gemini evidence
            traces = result.get("thought_traces", [])
            fallback_trace = next((t for t in traces if "Gemini Grounding" in t["reasoning"]), None)
            if fallback_trace:
                print("   [OK] Fallback thought trace found.")
            else:
                print("   [WARN] No explicit fallback trace found (maybe logic path differed?)")
                
        else:
            print("   [FAIL] No competitors found even with fallback.")
            
    except Exception as e:
        print(f"   [ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scout_fallback())
