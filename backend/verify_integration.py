
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path.cwd()))

from app.services.orchestrator import orchestrator, AnalysisState, PipelineStage
from app.api.routes.business import get_session
from app.services.analysis.sentiment import SentimentAnalysisResult
from app.services.analysis.pricing import CompetitiveAnalysisResult

async def verify_session_flow():
    print("--- Verifying Session Data Flow ---")
    
    session_id = "test-session-integration"
    
    # 1. Create a dummy Orchestrator State
    print(f"1. Creating dummy orchestrator state for {session_id}")
    
    # Mock discovered competitors
    discovered = [
        {
            "name": "Test Competitor 1",
            "price_level": 2,
            "rating": 4.5,
            "distance_meters": 500,
            "place_id": "test_place_1"
        }
    ]
    
    # Create state
    state = AnalysisState(
        session_id=session_id,
        current_stage=PipelineStage.COMPLETED,
        checkpoints=[],
        thought_traces=[],
        discovered_competitors=discovered,
        menu_items=[{"name": "Taco", "price": 10}],
        sales_data=[]
    )
    
    # Add manual fallback competitor analysis
    # (Simulating what _build_final_response does internally if missing)
    # Actually, we rely on _build_final_response to do it dynamically
    
    # Save to orchestrator memory
    orchestrator.active_sessions[session_id] = state
    
    # 2. Call get_session via the route logic (simulated)
    # We can't call the route directly easily without mocking request context for some deps if any,
    # but the function `get_session` in business.py is clean enough.
    
    print("2. Calling get_session...")
    try:
        response = await get_session(session_id)
        
        print("3. Validating Response Structure")
        
        # Check Competitors
        comp_analysis = response.get("competitor_analysis")
        if comp_analysis:
            print("   [OK] competitor_analysis present")
            comps = comp_analysis.get("competitors")
            if comps and len(comps) > 0:
                print(f"   [OK] competitors list found: {len(comps)} items")
                print(f"   Sample: {comps[0].get('name')} - {comps[0].get('priceRange')}")
            else:
                print("   [FAIL] competitors list missing or empty")
        else:
            print("   [FAIL] competitor_analysis missing")
            
        # Check Sentiment (should be None as we didn't populate it)
        sent_analysis = response.get("sentiment_analysis")
        if sent_analysis is None:
             print("   [OK] sentiment_analysis is None (expected)")
        else:
             print("   [INFO] sentiment_analysis present")

    except Exception as e:
        print(f"   [ERROR] get_session failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_session_flow())
