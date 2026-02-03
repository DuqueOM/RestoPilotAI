import pytest
import json
import base64
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.gemini.multimodal import MultimodalAgent

@pytest.fixture
def mock_settings():
    with patch("app.services.gemini.base_agent.get_settings") as mock:
        settings = MagicMock()
        settings.gemini_api_key = "test_key"
        settings.gemini_model_vision = "gemini-3-pro-preview"
        settings.enable_grounding = True
        mock.return_value = settings
        yield settings

@pytest.fixture
def multimodal_agent(mock_settings):
    agent = MultimodalAgent()
    # Mock the generate method to avoid actual API calls
    agent.generate = AsyncMock()
    return agent

@pytest.mark.asyncio
async def test_extract_menu_from_image_success(multimodal_agent):
    # Mock response data
    mock_response_data = {
        "items": [
            {
                "name": "Tacos",
                "price": 50.0,
                "category": "Mains",
                "description": "Delicious tacos"
            }
        ],
        "categories": [{"name": "Mains", "item_count": 1}],
        "extraction_quality": {"confidence": 0.9}
    }
    
    # Mock generate response - generate returns the TEXT string by default
    multimodal_agent.generate.return_value = json.dumps(mock_response_data)
    
    # Mock base64 encoding/decoding if needed, or just pass bytes
    image_bytes = b"fake_image_bytes"
    
    result = await multimodal_agent.extract_menu_from_image(
        image_source=image_bytes,
        additional_context="Mexican restaurant"
    )
    
    assert result["items"][0]["name"] == "Tacos"
    assert result["items"][0]["price"] == 50.0
    assert result["extraction_quality"]["confidence"] == 0.9
    
    # Verify generate called with correct arguments
    multimodal_agent.generate.assert_called_once()
    call_kwargs = multimodal_agent.generate.call_args[1]
    assert "Mexican restaurant" in call_kwargs["prompt"]
    assert call_kwargs["feature"] == "menu_extraction"

@pytest.mark.asyncio
async def test_analyze_dish_image_success(multimodal_agent):
    mock_response_data = {
        "visual_scores": {
            "overall_attractiveness": 8.5,
            "color_appeal": 9.0
        },
        "marketability": {
            "instagram_worthiness": 8.5
        },
        "overall_verdict": {
            "overall_score": 8.2
        }
    }
    
    multimodal_agent.generate.return_value = json.dumps(mock_response_data)
    
    result = await multimodal_agent.analyze_dish_image(
        image_source=b"fake_image",
        dish_name="Enchiladas"
    )
    
    assert result["visual_scores"]["overall_attractiveness"] == 8.5
    assert "attractiveness_score" in result
    
    call_kwargs = multimodal_agent.generate.call_args[1]
    assert "Enchiladas" in call_kwargs["prompt"]
    assert call_kwargs["feature"] == "dish_analysis"

@pytest.mark.asyncio
async def test_extract_competitor_menu_success(multimodal_agent):
    mock_response_data = {
        "competitor_info": {"name": "Comp1"},
        "items": [{"name": "CompItem1", "price": 100}],
        "extraction_confidence": 0.85
    }
    
    multimodal_agent.generate.return_value = json.dumps(mock_response_data)
    
    result = await multimodal_agent.extract_competitor_menu(
        image_source=b"fake_image",
        competitor_name="Competitor 1"
    )
    
    assert result["competitor_info"]["name"] == "Comp1"
    assert result["items"][0]["name"] == "CompItem1"
    assert result["source_type"] == "image"

@pytest.mark.asyncio
async def test_analyze_customer_photos_success(multimodal_agent):
    mock_response_data = {
        "photo_analyses": [
            {
                "photo_index": 0,
                "dish_identified": "Pizza",
                "sentiment_indicators": ["positive"]
            }
        ],
        "aggregate_insights": {
            "overall_visual_sentiment": "positive"
        }
    }
    
    multimodal_agent.generate.return_value = json.dumps(mock_response_data)
    
    photos = [b"photo1", b"photo2"]
    result = await multimodal_agent.analyze_customer_photos(
        photos=photos,
        menu_items=["Pizza", "Pasta"]
    )
    
    assert len(result["photo_analyses"]) == 1
    assert result["aggregate_insights"]["overall_visual_sentiment"] == "positive"
    
    call_kwargs = multimodal_agent.generate.call_args[1]
    assert "Pizza, Pasta" in call_kwargs["prompt"]

def test_validate_menu_extraction(multimodal_agent):
    raw_result = {
        "items": [
            {"name": "Item 1", "price": "10.50", "category": ""}, # String price, empty category
            {"name": "", "price": 5.0}, # Empty name, should be skipped
            {"name": "Item 2"} # No price
        ]
    }
    
    validated = multimodal_agent._validate_menu_extraction(raw_result)
    
    assert len(validated["items"]) == 2
    assert validated["items"][0]["name"] == "Item 1"
    assert validated["items"][0]["price"] == 10.50
    assert validated["items"][0]["category"] == "Uncategorized"
    
    assert validated["items"][1]["name"] == "Item 2"
    assert validated["items"][1]["price"] == 0.0

def test_generate_batch_summary(multimodal_agent):
    analyses = [
        {"attractiveness_score": 0.8},
        {"visual_scores": {"a": 4.0, "b": 6.0}}, # Avg 5.0 -> 0.5
        {"other": "data"} # Should be skipped
    ]
    
    summary = multimodal_agent._generate_batch_summary(analyses)
    
    assert summary["total_images"] == 3
    # Scores: 0.8 and 0.5. Avg: 0.65
    assert summary["average_attractiveness"] == 0.65
    assert summary["high_quality_count"] == 1 # 0.8 >= 0.7
    assert summary["needs_improvement_count"] == 0 # None < 0.5 (0.5 is not < 0.5)

@pytest.mark.asyncio
async def test_process_dispatch(multimodal_agent):
    multimodal_agent.extract_menu_from_image = AsyncMock(return_value="menu_result")
    multimodal_agent.analyze_dish_image = AsyncMock(return_value="dish_result")
    
    res1 = await multimodal_agent.process(task="extract_menu", image_source=b"img")
    assert res1 == "menu_result"
    
    res2 = await multimodal_agent.process(task="analyze_dish", image_source=b"img")
    assert res2 == "dish_result"
    
    with pytest.raises(ValueError):
        await multimodal_agent.process(task="unknown", image_source=b"img")
