import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.gemini.base_agent import GeminiBaseAgent, ThinkingLevel

@pytest.fixture
def mock_settings():
    with patch("app.services.gemini.base_agent.get_settings") as mock:
        settings = MagicMock()
        settings.gemini_api_key = "test_key"
        settings.gemini_model_primary = "gemini-3-flash-preview"
        settings.gemini_model_vision = "gemini-3-pro-preview"
        settings.gemini_model_reasoning = "gemini-3-reasoning-preview"
        settings.gemini_model_image_gen = "gemini-3-image-preview"
        settings.thinking_level_quick_temp = 0.7
        settings.thinking_level_quick_tokens = 1000
        settings.thinking_level_standard_temp = 0.5
        settings.thinking_level_standard_tokens = 2000
        settings.thinking_level_deep_temp = 0.3
        settings.thinking_level_deep_tokens = 4000
        settings.thinking_level_exhaustive_temp = 0.1
        settings.thinking_level_exhaustive_tokens = 8000
        settings.gemini_timeout_seconds = 30
        settings.gemini_marathon_timeout_seconds = 60
        settings.enable_grounding = True
        mock.return_value = settings
        yield settings

@pytest.fixture
def mock_genai_client():
    with patch("app.services.gemini.base_agent.genai.Client") as mock:
        client_instance = MagicMock()
        mock.return_value = client_instance
        yield client_instance

@pytest.fixture
def base_agent(mock_settings, mock_genai_client):
    return GeminiBaseAgent()

def test_initialization(base_agent, mock_settings):
    assert base_agent.api_key == "test_key"
    assert base_agent.model_name == "gemini-3-flash-preview"
    assert base_agent.client is not None

def test_get_model_for_task(base_agent):
    assert base_agent.get_model_for_task("general") == "gemini-3-flash-preview"
    assert base_agent.get_model_for_task("vision") == "gemini-3-pro-preview"
    assert base_agent.get_model_for_task("reasoning") == "gemini-3-reasoning-preview"
    assert base_agent.get_model_for_task("image_gen") == "gemini-3-image-preview"

def test_create_thought_signature(base_agent):
    prompt = "Test prompt"
    enhanced = base_agent._create_thought_signature(prompt, "QUICK")
    assert "[THOUGHT SIGNATURE - Level: QUICK]" in enhanced
    assert "<thinking>" in enhanced
    assert "<answer>" in enhanced
    assert prompt in enhanced

def test_extract_thought_trace(base_agent):
    text = "<thinking>My reasoning</thinking><answer>The answer</answer>"
    trace = base_agent._extract_thought_trace(text)
    assert trace == "My reasoning"
    
    text_no_trace = "Just an answer"
    assert base_agent._extract_thought_trace(text_no_trace) is None

def test_extract_answer(base_agent):
    text = "<thinking>My reasoning</thinking><answer>The answer</answer>"
    answer = base_agent._extract_answer(text)
    assert answer == "The answer"
    
    text_no_tags = "Just an answer"
    assert base_agent._extract_answer(text_no_tags) == "Just an answer"

@pytest.mark.asyncio
async def test_generate_success(base_agent, mock_genai_client):
    mock_response = MagicMock()
    mock_response.text = "Generated text"
    mock_response.usage_metadata.total_token_count = 100
    
    # Mock the sync generate_content call
    mock_genai_client.models.generate_content.return_value = mock_response
    
    response = await base_agent.generate("Test prompt")
    
    assert response == "Generated text"
    assert base_agent.usage_stats["total_tokens"] == 100
    mock_genai_client.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_generate_with_grounding_success(base_agent, mock_genai_client):
    mock_response = MagicMock()
    mock_response.text = "Grounded answer"
    
    # Mock grounding metadata
    mock_candidate = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.web.uri = "http://example.com"
    mock_chunk.web.title = "Example"
    
    mock_candidate.grounding_metadata.grounding_chunks = [mock_chunk]
    mock_candidate.grounding_metadata.search_entry_point.rendered_content = "search query"
    mock_response.candidates = [mock_candidate]
    
    mock_genai_client.models.generate_content.return_value = mock_response
    
    result = await base_agent.generate_with_grounding("Test prompt")
    
    assert result["answer"] == "Grounded answer"
    assert result["grounded"] is True
    assert len(result["grounding_metadata"]["grounding_chunks"]) == 1
    assert result["grounding_metadata"]["grounding_chunks"][0]["uri"] == "http://example.com"

@pytest.mark.asyncio
async def test_generate_with_thought_signature(base_agent, mock_genai_client):
    mock_response = MagicMock()
    mock_response.text = "<thinking>Reasoning</thinking><answer>Final Answer</answer>"
    mock_genai_client.models.generate_content.return_value = mock_response
    
    result = await base_agent.generate_with_thought_signature("Prompt")
    
    assert result["answer"] == "Final Answer"
    assert result["thought_trace"] == "Reasoning"
    assert result["thinking_level"] == "STANDARD"
