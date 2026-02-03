import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import json

from app.services.orchestrator import AnalysisOrchestrator, PipelineStage, ThinkingLevel

@pytest.fixture
def mock_agents():
    """Create mocks for all orchestrator agents."""
    mocks = {}
    
    # Gemini Base
    mocks['gemini'] = MagicMock()
    
    # Menu Extractor
    mocks['menu_extractor'] = MagicMock()
    mocks['menu_extractor'].extract_from_image = AsyncMock(return_value={
        "items": [{"name": "Tacos", "price": 10}],
        "confidence": 0.9
    })
    mocks['menu_extractor'].analyze_dish_image = AsyncMock(return_value={
        "item_name": "Tacos",
        "score": 8.5
    })
    
    # BCG Classifier
    mocks['bcg_classifier'] = MagicMock()
    mocks['bcg_classifier'].classify = AsyncMock(return_value={
        "products": [{"name": "Tacos", "classification": "star"}],
        "summary": "Good portfolio"
    })
    
    # Sales Predictor
    mocks['sales_predictor'] = MagicMock()
    # Note: process_sales_data is not async in the real class but orchestrator calls it as internal method
    # Wait, orchestrator calls self._process_sales_data which calls self.sales_predictor.analyze_sales
    # Let's check sales_predictor usage in orchestrator.
    # It calls: self.sales_predictor.process_csv(content) -> returns data
    # And: self.sales_predictor.predict_sales(...) -> returns predictions
    mocks['sales_predictor'].process_csv = MagicMock(return_value=[
        {"item": "Tacos", "sales": 100}
    ])
    mocks['sales_predictor'].predict_sales = AsyncMock(return_value={
        "predictions": [{"item": "Tacos", "predicted_sales": 110}]
    })
    
    # Campaign Generator
    mocks['campaign_generator'] = MagicMock()
    mocks['campaign_generator'].generate_campaigns = AsyncMock(return_value={
        "campaigns": [{"name": "Taco Tuesday", "type": "promo"}]
    })
    
    # Verification Agent
    mocks['verification_agent'] = MagicMock()
    
    # Create a mock object for the result that behaves like a class instance
    mock_verification_result = MagicMock()
    mock_verification_result.status.value = "verified"
    mock_verification_result.overall_score = 0.95
    mock_verification_result.iterations_used = 0
    mock_verification_result.improvements_made = []
    mock_verification_result.checks = []
    mock_verification_result.final_recommendation = "Go"
    
    mocks['verification_agent'].verify_analysis = AsyncMock(return_value=mock_verification_result)

    mocks['verification_agent'].verify_competitor_data = AsyncMock(return_value={
        "verified": True,
        "confidence_score": 0.9
    })
    mocks['verification_agent'].verify_analysis_logic = AsyncMock(return_value={
        "verified": True,
        "issues": []
    })
    
    # Vibe Agent
    mocks['vibe_agent'] = MagicMock()
    # Vibe agent is used inside _run_bcg_classification if auto_verify is True
    mocks['vibe_agent'].verify_and_improve_analysis = AsyncMock(return_value={
        "final_analysis": {"products": [], "verified": True},
        "quality_achieved": 0.95,
        "iterations_required": 0
    })
    mocks['vibe_agent'].verify_campaign_assets = AsyncMock(return_value={
        "verified_assets": []
    })
    
    # Scout Agent
    mocks['scout_agent'] = MagicMock()
    mocks['scout_agent'].run_scouting_mission = AsyncMock(return_value={
        "competitors": [
            {"name": "Comp1", "website": "http://comp1.com", "place_id": "123"}
        ],
        "summary": {"location_analyzed": {"lat": 10, "lng": 20}},
        "thought_traces": []
    })
    
    # Competitor Intelligence
    mocks['competitor_intelligence'] = MagicMock()
    mocks['competitor_intelligence'].analyze_competitors = AsyncMock(return_value=MagicMock(to_dict=lambda: {
        "market_position": "Leader",
        "strategic_recommendations": []
    }))
    
    # Sentiment Analyzer
    mocks['sentiment_analyzer'] = MagicMock()
    mocks['sentiment_analyzer'].analyze_customer_sentiment = AsyncMock(return_value=MagicMock(to_dict=lambda: {
        "overall_sentiment": "positive"
    }))
    
    # Visual Gap Analyzer (SocialAestheticsAnalyzer)
    mocks['visual_gap_analyzer'] = MagicMock()
    mocks['visual_gap_analyzer'].compare_visual_aesthetics = AsyncMock(return_value={
        "gap_score": 0.2
    })
    
    # Competitor Parser
    mocks['competitor_parser'] = MagicMock()
    mocks['competitor_parser'].parse_mixed_input = AsyncMock(return_value=[
        {"name": "ManualComp", "source": "manual"}
    ])
    
    # Neighborhood Analyzer
    mocks['neighborhood_analyzer'] = MagicMock()
    mocks['neighborhood_analyzer'].analyze_neighborhood = AsyncMock(return_value={
        "demographics": "Young"
    })
    
    # Context Processor
    mocks['context_processor'] = MagicMock()
    mocks['context_processor'].integrate_context_into_analysis = AsyncMock(return_value={
        "insights": "Good context"
    })
    mocks['context_processor'].process_audio_context = AsyncMock(return_value={
        "transcription": "Audio text"
    })
    
    # Enrichment Service
    mocks['enrichment_service'] = MagicMock()
    mocks['enrichment_service'].enrich_competitor_profile = AsyncMock(return_value=MagicMock(to_dict=lambda: {
        "name": "Comp1", "enriched": True
    }))

    # Sales Predictor
    mocks['sales_predictor'] = MagicMock()
    mocks['sales_predictor'].train = AsyncMock()
    mocks['sales_predictor'].predict_batch = AsyncMock(return_value={
        "predictions": [{"item": "Tacos", "predicted_sales": 110}]
    })
    
    return mocks

@pytest.fixture
def orchestrator(mock_agents, tmp_path):
    """Create orchestrator with mocked agents and temp storage."""
    # Patch all the classes instantiated in __init__
    with patch('app.services.orchestrator.GeminiAgent', return_value=mock_agents['gemini']), \
         patch('app.services.orchestrator.MenuExtractor', return_value=mock_agents['menu_extractor']), \
         patch('app.services.orchestrator.BCGClassifier', return_value=mock_agents['bcg_classifier']), \
         patch('app.services.orchestrator.SalesPredictor', return_value=mock_agents['sales_predictor']), \
         patch('app.services.orchestrator.CampaignGenerator', return_value=mock_agents['campaign_generator']), \
         patch('app.services.orchestrator.VerificationAgent', return_value=mock_agents['verification_agent']), \
         patch('app.services.orchestrator.VibeEngineeringAgent', return_value=mock_agents['vibe_agent']), \
         patch('app.services.orchestrator.ScoutAgent', return_value=mock_agents['scout_agent']), \
         patch('app.services.orchestrator.CompetitorIntelligenceService', return_value=mock_agents['competitor_intelligence']), \
         patch('app.services.orchestrator.SentimentAnalyzer', return_value=mock_agents['sentiment_analyzer']), \
         patch('app.services.orchestrator.SocialAestheticsAnalyzer', return_value=mock_agents['visual_gap_analyzer']), \
         patch('app.services.orchestrator.CompetitorParser', return_value=mock_agents['competitor_parser']), \
         patch('app.services.orchestrator.NeighborhoodAnalyzer', return_value=mock_agents['neighborhood_analyzer']), \
         patch('app.services.orchestrator.ContextProcessor', return_value=mock_agents['context_processor']), \
         patch('app.services.orchestrator.CompetitorEnrichmentService', return_value=mock_agents['enrichment_service']), \
         patch('app.services.orchestrator.get_settings'):
        
        orch = AnalysisOrchestrator()
        orch.storage_dir = tmp_path / "sessions"
        orch.storage_dir.mkdir()
        
        # Mock the websocket manager calls to avoid errors
        with patch('app.services.orchestrator.send_progress_update', new_callable=AsyncMock), \
             patch('app.services.orchestrator.send_stage_complete', new_callable=AsyncMock), \
             patch('app.services.orchestrator.send_thought', new_callable=AsyncMock), \
             patch('app.services.orchestrator.send_error', new_callable=AsyncMock):
            yield orch

@pytest.mark.asyncio
async def test_run_full_pipeline_success(orchestrator):
    """Test the full pipeline execution with mocked agents."""
    
    # 1. Create Session
    session_id = await orchestrator.create_session()
    assert session_id is not None
    assert session_id in orchestrator.active_sessions
    
    # 2. Run Pipeline
    result = await orchestrator.run_full_pipeline(
        session_id=session_id,
        menu_images=["/tmp/menu.jpg"],
        dish_images=["/tmp/dish.jpg"],
        address="123 Main St",
        cuisine_type="Mexican",
        thinking_level=ThinkingLevel.STANDARD,
        auto_verify=True,
        auto_find_competitors=True
    )
    
    # 3. Verify Completion
    assert "error" not in result
    
    state = orchestrator.completed_sessions.get(session_id)
    assert state is not None
    assert state.current_stage == PipelineStage.COMPLETED
    
    # 4. Verify Stage Execution (via data presence)
    # Menu Extraction
    assert len(state.menu_items) > 0
    assert state.menu_items[0]["name"] == "Tacos"
    
    # Dish Analysis
    assert "Tacos" in state.image_scores
    
    # Competitor Discovery
    assert len(state.discovered_competitors) > 0
    assert state.discovered_competitors[0]["name"] == "Comp1"
    
    # Neighborhood Analysis
    assert state.neighborhood_analysis is not None
    
    # BCG
    assert state.bcg_analysis is not None
    
    # Campaigns
    assert len(state.campaigns) > 0
    
    # 5. Verify Persistence
    saved_file = orchestrator.storage_dir / f"{session_id}.json"
    assert saved_file.exists()
    
    with open(saved_file) as f:
        data = json.load(f)
        assert data["session_id"] == session_id
        assert data["current_stage"] == "completed"

@pytest.mark.asyncio
async def test_pipeline_recovery_from_checkpoint(orchestrator):
    """Test that pipeline skips completed stages."""
    
    session_id = await orchestrator.create_session()
    state = orchestrator.active_sessions[session_id]
    
    # Manually add a checkpoint for Menu Extraction
    from app.services.orchestrator import PipelineCheckpoint
    from datetime import datetime, timezone
    
    checkpoint = PipelineCheckpoint(
        stage=PipelineStage.MENU_EXTRACTION,
        timestamp=datetime.now(timezone.utc),
        data={"menu_items": [{"name": "Pre-extracted", "price": 20}]},
        thought_trace=[],
        success=True
    )
    state.checkpoints.append(checkpoint)
    # Also update state to reflect the checkpoint data (orchestrator usually loads from state, 
    # but the check in run_full_pipeline just checks for checkpoint existence to skip)
    
    # Run pipeline
    await orchestrator.run_full_pipeline(
        session_id=session_id,
        menu_images=["/tmp/menu.jpg"], # Should be skipped
    )
    
    # Orchestrator's _run_stage checks if stage is in checkpoints.
    # However, if it skips, it doesn't execute the handler. 
    # So menu_extractor.extract_from_image should NOT be called.
    
    # Access the mock from the fixture logic? 
    # We can access it via the orchestrator instance attributes since we mocked them.
    orchestrator.menu_extractor.extract_from_image.assert_not_called()

@pytest.mark.asyncio
async def test_pipeline_failure_handling(orchestrator):
    """Test that pipeline handles errors gracefully."""
    
    session_id = await orchestrator.create_session()
    
    # Make menu extraction fail
    orchestrator.menu_extractor.extract_from_image.side_effect = Exception("OCR Failed")
    
    result = await orchestrator.run_full_pipeline(
        session_id=session_id,
        menu_images=["/tmp/bad_image.jpg"]
    )
    
    assert "error" in result
    assert "OCR Failed" in result["error"]
    
    state = orchestrator.active_sessions[session_id]
    assert state.current_stage == PipelineStage.FAILED
    
    # Verify checkpoint saved with failure
    assert state.checkpoints[-1].success is False
    assert state.checkpoints[-1].error == "OCR Failed"
