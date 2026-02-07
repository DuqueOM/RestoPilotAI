import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.gemini.creative_autopilot import CreativeAutopilotAgent
from app.services.intelligence.social_aesthetics import SocialAestheticsAnalyzer

async def test_menu_transformation():
    print("Testing Menu Transformation Studio...")
    agent = CreativeAutopilotAgent()
    
    # Mock client
    agent.client = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data.data = b"transformed_image_bytes"
    mock_response.parts = [mock_part]
    mock_chat.send_message.return_value = mock_response
    agent.client.chats.create.return_value = mock_chat
    
    result = await agent.transform_menu_visual_style(
        menu_image=b"fake_image_bytes",
        target_style="modern_minimalist"
    )
    
    print(f"Result keys: {result.keys()}")
    assert result["original_preserved"] == True
    assert result["style_applied"] == "modern_minimalist"
    assert result["transformed_menu"] == b"transformed_image_bytes"
    print("✅ Menu Transformation test passed")

async def test_instagram_prediction():
    print("\nTesting Instagram Performance Predictor...")
    analyzer = SocialAestheticsAnalyzer()
    
    # Mock client and response
    analyzer.client = MagicMock()
    mock_response = MagicMock()
    
    mock_json_response = """
    {
        "predicted_performance": {
            "likes_estimate": "100-200",
            "engagement_rate": "3.5%",
            "virality_score": 7,
            "confidence": 0.8
        },
        "scores": {
            "composition": 8,
            "lighting": 7,
            "appetizing": 9,
            "instagramability": 8,
            "timing": 9
        },
        "improvements": [],
        "optimal_posting_time": "18:00 Friday",
        "trending_hashtags": ["#foodie"],
        "comparison_to_trends": "Matches current trends"
    }
    """
    mock_response.text = mock_json_response
    analyzer.client.models.generate_content.return_value = mock_response
    
    result = await analyzer.predict_instagram_performance(
        dish_photo=b"fake_dish_bytes",
        restaurant_category="Mexican",
        posting_time=datetime.now()
    )
    
    print(f"Result keys: {result.keys()}")
    assert "predicted_performance" in result
    assert "scores" in result
    print("✅ Instagram Prediction test passed")

async def main():
    try:
        await test_menu_transformation()
        await test_instagram_prediction()
        print("\n🎉 All WOW features verified successfully!")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
