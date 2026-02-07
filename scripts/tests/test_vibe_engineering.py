import asyncio
import os
import sys
import json
from unittest.mock import MagicMock, AsyncMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.gemini.vibe_engineering import VibeEngineeringAgent

async def test_verify_and_improve_analysis():
    print("Testing Vibe Engineering: Analysis Verification Loop...")
    agent = VibeEngineeringAgent()
    
    # Mock client
    agent.client = MagicMock()
    mock_response_1 = MagicMock()
    mock_response_2 = MagicMock()
    mock_response_3 = MagicMock()
    
    # 1. First verification: Low score
    mock_response_1.text = json.dumps({
        "quality_score": 0.6,
        "precision_score": 0.6,
        "completeness_score": 0.5,
        "applicability_score": 0.7,
        "clarity_score": 0.6,
        "identified_issues": [
            {"issue": "Missing profit margin analysis", "severity": "high", "suggestion": "Add margin calc"}
        ],
        "strengths": ["Good basic data"],
        "overall_assessment": "Needs improvement"
    })
    
    # 2. Improvement step
    mock_response_2.text = json.dumps({
        "analysis_content": "Improved analysis with margin calculation",
        "improvements_made": ["Added profit margin analysis"]
    })
    
    # 3. Second verification: High score
    mock_response_3.text = json.dumps({
        "quality_score": 0.9,
        "precision_score": 0.9,
        "completeness_score": 0.9,
        "applicability_score": 0.9,
        "clarity_score": 0.9,
        "identified_issues": [],
        "strengths": ["Excellent analysis", "Comprehensive"],
        "overall_assessment": "Great job"
    })
    
    # Configure side_effect for generate_content
    # Sequence: Verify 1 -> Improve -> Verify 2
    agent.client.models.generate_content.side_effect = [
        mock_response_1, # Verify 1
        mock_response_2, # Improve
        mock_response_3  # Verify 2
    ]
    
    initial_analysis = {"analysis_content": "Basic analysis"}
    source_data = {"sales": 1000, "costs": 800}
    
    result = await agent.verify_and_improve_analysis(
        analysis_type="Profitability",
        analysis_result=initial_analysis,
        source_data=source_data,
        auto_improve=True
    )
    
    print(f"Iterations required: {result['iterations_required']}")
    print(f"Final Quality Score: {result['quality_achieved']}")
    print(f"Auto Improved: {result['auto_improved']}")
    
    assert result['iterations_required'] == 2
    assert result['quality_achieved'] == 0.9
    assert result['auto_improved'] == True
    assert "improvements_made" in result['final_analysis']
    
    print("✅ Analysis Verification Loop test passed")

async def test_verify_campaign_assets():
    print("\nTesting Vibe Engineering: Asset Verification...")
    agent = VibeEngineeringAgent()
    agent.client = MagicMock()
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "quality_score": 0.95,
        "text_legibility": 0.9,
        "brand_adherence": 1.0,
        "technical_quality": 0.9,
        "message_effectiveness": 0.95,
        "issues": [],
        "assessment": "Perfect asset"
    })
    
    agent.client.models.generate_content.return_value = mock_response
    
    assets = [{
        "type": "instagram_post",
        "image_data": b"fake_image_bytes",
        "concept": "Test concept"
    }]
    
    brand_guidelines = {"colors": ["#000000"]}
    
    result = await agent.verify_campaign_assets(
        campaign_assets=assets,
        brand_guidelines=brand_guidelines
    )
    
    print(f"Overall Quality: {result['overall_quality']}")
    assert result['overall_quality'] == 0.95
    assert "verification" in result['verified_assets'][0]
    
    print("✅ Asset Verification test passed")

async def main():
    try:
        await test_verify_and_improve_analysis()
        await test_verify_campaign_assets()
        print("\n🎉 Vibe Engineering Verified Successfully!")
    except Exception as e:
        print(f"\n❌ Vibe Engineering Tests Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
