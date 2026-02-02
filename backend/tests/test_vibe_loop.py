
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.orchestrator import AnalysisOrchestrator, AnalysisState, PipelineStage
from app.services.gemini.base_agent import ThinkingLevel

@pytest.mark.asyncio
async def test_vibe_loop_integration_bcg():
    """Test that the Vibe Engineering loop is triggered during BCG classification."""
    
    # Mock dependencies
    with patch('app.services.orchestrator.BCGClassifier') as MockBCG, \
         patch('app.services.orchestrator.VibeEngineeringAgent') as MockVibe, \
         patch('app.services.orchestrator.get_settings') as MockSettings:
        
        # Setup mocks
        mock_bcg_instance = MockBCG.return_value
        mock_bcg_instance.classify = AsyncMock(return_value={
            "products": [{"name": "Burger", "classification": "star"}]
        })
        
        mock_vibe_instance = MockVibe.return_value
        mock_vibe_instance.verify_and_improve_analysis = AsyncMock(return_value={
            "final_analysis": {
                "products": [{"name": "Burger", "classification": "star", "verified": True}]
            },
            "quality_achieved": 0.95,
            "iterations_required": 1
        })
        
        # Initialize Orchestrator
        orchestrator = AnalysisOrchestrator()
        # Inject the mock vibe agent (since it's created in __init__)
        orchestrator.vibe_agent = mock_vibe_instance
        orchestrator.bcg_classifier = mock_bcg_instance
        
        # Create state
        state = AnalysisState(
            session_id="test-session",
            current_stage=PipelineStage.BCG_CLASSIFICATION,
            checkpoints=[],
            thought_traces=[],
            menu_items=[{"name": "Burger", "price": 10}],
            sales_data=[{"item": "Burger", "sales": 100}],
            auto_verify=True
        )
        
        # Run stage
        await orchestrator._run_bcg_classification(state, ThinkingLevel.STANDARD)
        
        # Verify Vibe Agent was called
        mock_vibe_instance.verify_and_improve_analysis.assert_called_once()
        call_args = mock_vibe_instance.verify_and_improve_analysis.call_args
        assert call_args.kwargs['analysis_type'] == "bcg_classification"
        assert call_args.kwargs['auto_improve'] is True
        
        # Verify state update
        assert state.vibe_status is not None
        assert state.vibe_status['quality_achieved'] == 0.95
        assert state.bcg_analysis['products'][0]['verified'] is True

@pytest.mark.asyncio
async def test_vibe_loop_integration_competitor():
    """Test Vibe loop in competitor analysis."""
    
    with patch('app.services.orchestrator.CompetitorIntelligenceService') as MockCompService, \
         patch('app.services.orchestrator.VibeEngineeringAgent') as MockVibe, \
         patch('app.services.orchestrator.get_settings'):
            
        mock_comp_service = MockCompService.return_value
        mock_comp_service.analyze_competitors = AsyncMock(return_value=MagicMock(to_dict=lambda: {"competitors": []}))
        
        mock_vibe_instance = MockVibe.return_value
        mock_vibe_instance.verify_and_improve_analysis = AsyncMock(return_value={
            "final_analysis": {"competitors": [], "verified": True},
            "quality_achieved": 0.92
        })
        
        orchestrator = AnalysisOrchestrator()
        orchestrator.vibe_agent = mock_vibe_instance
        orchestrator.competitor_intelligence = mock_comp_service
        
        state = AnalysisState(
            session_id="test-session",
            current_stage=PipelineStage.COMPETITOR_ANALYSIS,
            checkpoints=[],
            thought_traces=[],
            menu_items=[{"name": "Burger"}],
            discovered_competitors=[{"name": "Comp1", "website": "http://comp1.com"}],
            auto_verify=True
        )
        
        await orchestrator._run_competitor_analysis(state)
        
        mock_vibe_instance.verify_and_improve_analysis.assert_called_once()
        assert state.vibe_status['quality_achieved'] == 0.92
