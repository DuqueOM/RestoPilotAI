import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.gemini.reasoning_agent import ReasoningAgent, ThinkingLevel, ThoughtTrace, ReasoningResult

@pytest.fixture
def mock_settings():
    with patch("app.services.gemini.base_agent.get_settings") as mock:
        settings = MagicMock()
        settings.gemini_api_key = "test_key"
        settings.gemini_model_reasoning = "gemini-3-reasoning-preview"
        settings.enable_grounding = True
        mock.return_value = settings
        yield settings

@pytest.fixture
def reasoning_agent(mock_settings):
    agent = ReasoningAgent()
    # Mock generation methods
    agent.generate = AsyncMock()
    agent.generate_with_grounding = AsyncMock()
    return agent

@pytest.mark.asyncio
async def test_create_thought_signature(reasoning_agent):
    mock_response = {
        "plan": ["Step 1", "Step 2"],
        "observations": ["Obs 1"],
        "reasoning": "Because X",
        "assumptions": ["Assume Y"],
        "confidence": 0.9
    }
    reasoning_agent.generate.return_value = json.dumps(mock_response)
    
    context = {"data": "test"}
    result = await reasoning_agent.create_thought_signature("Test Task", context)
    
    assert result["plan"] == ["Step 1", "Step 2"]
    assert len(reasoning_agent.thought_traces) == 1
    assert reasoning_agent.thought_traces[0].step == "Planning: Test Task"
    
    # Verify generate called with correct thinking level config
    reasoning_agent.generate.assert_called_once()
    call_kwargs = reasoning_agent.generate.call_args[1]
    assert call_kwargs["feature"] == "thought_signature"

@pytest.mark.asyncio
async def test_analyze_bcg_strategy_no_grounding(reasoning_agent):
    # Mock thought signature generation (it calls generate)
    # We need to handle multiple calls to generate: 1. thought signature, 2. analysis
    
    mock_thought_sig = {
        "plan": ["Step 1"],
        "reasoning": "Plan reasoning",
        "confidence": 0.8
    }
    
    mock_analysis = {
        "thinking_trace": {"market_analysis": "Market is good"},
        "portfolio_assessment": {"health_score": 8.0},
        "strategic_recommendations": [{"action": "Invest", "priority": 1}],
        "confidence_scores": {"overall": 0.85}
    }
    
    # Configure side_effect for generate
    reasoning_agent.generate.side_effect = [
        json.dumps(mock_thought_sig), # 1st call: thought signature
        json.dumps(mock_analysis)     # 2nd call: strategy analysis
    ]
    
    products = [{"name": "P1", "sales": 100}]
    
    result = await reasoning_agent.analyze_bcg_strategy(
        products=products,
        enable_grounding=False
    )
    
    assert isinstance(result, ReasoningResult)
    assert result.confidence == 0.85
    assert result.analysis["grounded"] is False
    assert len(result.thought_traces) == 2 # 1 planning, 1 execution
    assert result.thought_traces[1].step == "BCG Strategic Analysis"

@pytest.mark.asyncio
async def test_analyze_bcg_strategy_with_grounding(reasoning_agent):
    # Mock thought signature (calls generate)
    mock_thought_sig = {
        "plan": ["Step 1"],
        "reasoning": "Plan reasoning",
        "confidence": 0.8
    }
    reasoning_agent.generate.return_value = json.dumps(mock_thought_sig)
    
    # Mock grounded analysis (calls generate_with_grounding)
    mock_grounded_response = {
        "answer": json.dumps({
            "thinking_trace": {"market_analysis": "Grounded market analysis"},
            "strategic_recommendations": [{"action": "Invest", "priority": 1}],
            "confidence_scores": {"overall": 0.9}
        }),
        "grounding_metadata": {
            "grounding_chunks": [{"uri": "http://source.com"}]
        },
        "grounded": True
    }
    reasoning_agent.generate_with_grounding.return_value = mock_grounded_response
    
    products = [{"name": "P1", "sales": 100}]
    
    result = await reasoning_agent.analyze_bcg_strategy(
        products=products,
        enable_grounding=True
    )
    
    assert result.analysis["grounded"] is True
    assert len(result.analysis["grounding_sources"]) == 1
    assert result.analysis["grounding_sources"][0]["uri"] == "http://source.com"
    
    reasoning_agent.generate_with_grounding.assert_called_once()
    call_kwargs = reasoning_agent.generate_with_grounding.call_args[1]
    assert call_kwargs["enable_grounding"] is True

@pytest.mark.asyncio
async def test_analyze_competitive_position_grounded(reasoning_agent):
    # Mock grounded response
    mock_grounded_response = {
        "answer": json.dumps({
            "competitive_landscape": {"market_position": "Leader"},
            "strategic_recommendations": [{"recommendation": "Maintain prices"}],
            "confidence": 0.88
        }),
        "grounding_metadata": {
            "grounding_chunks": [{"uri": "http://competitor.com"}]
        },
        "grounded": True
    }
    reasoning_agent.generate_with_grounding.return_value = mock_grounded_response
    
    our_menu = {"name": "MyResto", "items": []}
    competitor_menus = [{"name": "Comp1", "items": []}]
    
    result = await reasoning_agent.analyze_competitive_position(
        our_menu=our_menu,
        competitor_menus=competitor_menus,
        enable_grounding=True
    )
    
    assert result.analysis["grounded"] is True
    assert result.analysis["grounding_sources"][0]["uri"] == "http://competitor.com"
    assert result.thought_traces[0].step == "Competitive Position Analysis (Grounded)"
    assert "Used 1 external sources" in result.thought_traces[0].observations

@pytest.mark.asyncio
async def test_generate_strategic_recommendations(reasoning_agent):
    mock_response = {
        "executive_summary": "Summary",
        "immediate_actions": [{"action": "Do this", "rationale": "Because"}],
        "short_term_initiatives": [],
        "long_term_strategy": {},
        "menu_recommendations": {},
        "pricing_strategy": {},
        "financial_projections": {},
        "risk_matrix": [],
        "confidence": 0.8
    }
    reasoning_agent.generate.return_value = json.dumps(mock_response)
    
    result = await reasoning_agent.generate_strategic_recommendations(
        bcg_analysis={},
        competitive_analysis={}
    )
    
    assert isinstance(result, ReasoningResult)
    assert result.analysis["executive_summary"] == "Summary"
    assert len(result.thought_traces) == 1
    assert result.thought_traces[0].step == "Strategic Recommendations"
    assert result.thought_traces[0].reasoning == "Summary"
    
@pytest.mark.asyncio
async def test_process_dispatch(reasoning_agent):
    reasoning_agent.analyze_bcg_strategy = AsyncMock(return_value="bcg_result")
    reasoning_agent.analyze_competitive_position = AsyncMock(return_value="comp_result")
    
    res1 = await reasoning_agent.process(task="bcg_analysis")
    assert res1 == "bcg_result"
    
    res2 = await reasoning_agent.process(task="competitive_analysis")
    assert res2 == "comp_result"
    
    with pytest.raises(ValueError):
        await reasoning_agent.process(task="unknown")
