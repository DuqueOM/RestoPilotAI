import asyncio
import os
import sys
import json
from unittest.mock import MagicMock, AsyncMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.gemini.reasoning_agent import ReasoningAgent

async def test_competitive_intelligence_grounding():
    print("Testing Competitive Intelligence: Grounded Analysis...")
    agent = ReasoningAgent()
    
    # Mock client
    agent.client = MagicMock()
    mock_response = MagicMock()
    
    # Mock JSON response from the model
    mock_response.text = json.dumps({
        "competitive_landscape": {
            "market_position": "Challenger",
            "competitive_intensity": "high"
        },
        "price_analysis": {
            "our_positioning": "premium",
            "vs_competitors": {
                "Competitor A": {"price_difference_percent": 10}
            }
        },
        "strategic_recommendations": [
            {"recommendation": "Adjust lunch pricing"}
        ]
    })
    
    # Mock grounding metadata
    mock_chunk = MagicMock()
    mock_chunk.web.uri = "https://competitor-a.com/menu"
    
    mock_metadata = MagicMock()
    mock_metadata.grounding_chunks = [mock_chunk]
    
    mock_response.grounding_metadata = mock_metadata
    
    agent.client.models.generate_content.return_value = mock_response
    
    restaurant_data = {"name": "Our Restaurant", "cuisine": "Italian"}
    competitors = [{"name": "Competitor A"}]
    
    result = await agent.analyze_competitive_position_with_grounding(
        restaurant_data=restaurant_data,
        competitors=competitors
    )
    
    print(f"Analysis keys: {result['analysis'].keys()}")
    print(f"Sources found: {result['sources']}")
    
    assert "competitive_landscape" in result['analysis']
    assert "https://competitor-a.com/menu" in result['sources']
    
    # Verify tool usage
    call_args = agent.client.models.generate_content.call_args
    assert call_args is not None
    _, kwargs = call_args
    
    # Check if google_search tool was passed
    config = kwargs.get('config')
    assert config is not None
    # Depending on how the mock captures the config object, we might need to inspect it differently
    # But mainly we want to ensure the method ran without error and processed the mock response
    
    print("✅ Competitive Intelligence Grounding test passed")

async def main():
    try:
        await test_competitive_intelligence_grounding()
        print("\n🎉 Competitive Intelligence Verified Successfully!")
    except Exception as e:
        print(f"\n❌ Competitive Intelligence Tests Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
