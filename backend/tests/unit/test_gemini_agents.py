import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.gemini.base_agent import GeminiAgent, ThinkingLevel
from app.services.gemini.multimodal import MultimodalAgent
from app.services.gemini.reasoning_agent import ReasoningAgent

class TestGeminiBaseAgent:
    """Unit tests for GeminiBaseAgent."""
    
    @pytest.fixture
    def mock_genai(self):
        with patch('app.services.gemini.base_agent.genai') as mock:
            yield mock
    
    @pytest.mark.asyncio
    async def test_generate_with_thought_signature(self, mock_genai):
        """Test thought signature generation."""
        mock_response = MagicMock()
        # Adjusted tags to match base_agent.py implementation (<thinking>, <answer>)
        mock_response.text = "<thinking>reasoning process</thinking>\n<answer>final result</answer>"
        # Ensure usage_metadata is present to avoid attribute errors during stats tracking
        mock_response.usage_metadata.total_token_count = 10
        
        # Setup the mock chain
        mock_genai.Client.return_value.models.generate_content.return_value = mock_response
        
        agent = GeminiAgent()
        result = await agent.generate_with_thought_signature(
            prompt="Test prompt",
            thinking_level=ThinkingLevel.STANDARD
        )
        
        assert "thought_trace" in result
        assert "answer" in result
        assert result["thought_trace"] == "reasoning process"
        assert result["answer"] == "final result"
    
    @pytest.mark.asyncio
    async def test_generate_with_grounding(self, mock_genai):
        """Test grounding with Google Search."""
        mock_response = MagicMock()
        mock_response.text = "Grounded response"
        mock_response.usage_metadata.total_token_count = 10
        
        # Mock candidates and grounding metadata
        mock_candidate = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.web.uri = "https://example.com"
        mock_chunk.web.title = "Example"
        
        mock_candidate.grounding_metadata.grounding_chunks = [mock_chunk]
        mock_candidate.grounding_metadata.search_entry_point.rendered_content = "search query"
        
        mock_response.candidates = [mock_candidate]
        
        mock_genai.Client.return_value.models.generate_content.return_value = mock_response
        
        agent = GeminiAgent()
        result = await agent.generate_with_grounding(prompt="Market trends")
        
        assert result.get("grounded") is True
        assert len(result.get("grounding_metadata", {}).get("grounding_chunks", [])) > 0
        assert result["grounding_metadata"]["grounding_chunks"][0]["uri"] == "https://example.com"


class TestMultimodalAgent:
    """Unit tests for MultimodalAgent."""
    
    @pytest.fixture
    def mock_genai(self):
        # Patching genai and types in base_agent
        with patch('app.services.gemini.base_agent.genai') as mock_genai, \
             patch('app.services.gemini.base_agent.types') as mock_types:
            # We need to return both or just genai, but the test uses mock_genai
            # We can attach types to mock_genai or just let it be mocked implicitly
            yield mock_genai

    @pytest.mark.asyncio
    async def test_extract_menu_from_image(self, mock_genai):
        """Test menu extraction from image."""
        mock_response = MagicMock()
        mock_response.text = '{"items": [{"name": "Taco", "price": 50}], "categories": [], "extraction_quality": {"confidence": 0.9}}'
        mock_response.usage_metadata.total_token_count = 100
        mock_genai.Client.return_value.models.generate_content.return_value = mock_response
        
        agent = MultimodalAgent()
        # Use a minimal test image
        test_image = b'fake_image_data'
        
        result = await agent.extract_menu_from_image(test_image)
        
        assert "items" in result
        assert len(result["items"]) > 0
        assert result["items"][0]["name"] == "Taco"
    
    @pytest.mark.asyncio
    async def test_analyze_dish_professional(self, mock_genai):
        """Test dish photo analysis."""
        mock_response = MagicMock()
        mock_response.text = '{"visual_scores": {"composition": 8.0}, "overall_score": 8.5, "professional_assessment": "Good"}'
        mock_response.usage_metadata.total_token_count = 100
        mock_genai.Client.return_value.models.generate_content.return_value = mock_response
        
        agent = MultimodalAgent()
        result = await agent.analyze_dish_professional(
            image_source=b'fake_image_data',
            dish_name="Taco",
            dish_category="Main"
        )
        
        assert "overall_score" in result
        assert result["overall_score"] == 8.5


class TestReasoningAgent:
    """Unit tests for ReasoningAgent."""
    
    @pytest.fixture
    def mock_genai(self):
        with patch('app.services.gemini.base_agent.genai') as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_analyze_bcg_strategy(self, mock_genai):
        """Test BCG strategy analysis."""
        # Use simple return values for the sequence of calls
        # 1. create_thought_signature -> returns JSON text
        # 2. generate (actual analysis) -> returns JSON text
        
        thought_sig_response = MagicMock()
        thought_sig_response.text = '{"plan": [], "observations": [], "reasoning": "Plan", "confidence": 0.9}'
        thought_sig_response.usage_metadata.total_token_count = 100
        
        bcg_response = MagicMock()
        bcg_response.text = '''
        {
            "portfolio_assessment": {"health_score": 7.5},
            "quadrant_analysis": {},
            "strategic_recommendations": [],
            "thinking_trace": {"market_analysis": "Good"},
            "confidence_scores": {"overall": 0.8}
        }
        '''
        bcg_response.usage_metadata.total_token_count = 500
        
        # Set side_effect to return these in order
        mock_genai.Client.return_value.models.generate_content.side_effect = [thought_sig_response, bcg_response]
        
        agent = ReasoningAgent()
        
        # Disable grounding to use standard generate path and avoid complexity of grounding mock here (covered in BaseAgent test)
        result = await agent.analyze_bcg_strategy(
            products=[{"name": "Burger", "price": 100}],
            sales_data=[{"item": "Burger", "units": 50}],
            enable_grounding=False
        )
        
        # analyze_bcg_strategy returns ReasoningResult object
        assert result is not None
        assert result.analysis is not None
        assert "portfolio_assessment" in result.analysis
        assert result.analysis["portfolio_assessment"]["health_score"] == 7.5
