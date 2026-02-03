import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.orchestrator import AnalysisOrchestrator, AnalysisState, PipelineStage
from app.services.gemini.base_agent import ThinkingLevel

class TestPipelineIntegration:
    """Integration tests for full analysis pipeline."""
    
    @pytest.fixture
    def mock_all_agents(self):
        """Mock all AI agents and services for pipeline testing."""
        with patch.multiple(
            'app.services.orchestrator',
            GeminiAgent=MagicMock(),
            MenuExtractor=MagicMock(),
            BCGClassifier=MagicMock(),
            SalesPredictor=MagicMock(),
            CampaignGenerator=MagicMock(),
            VerificationAgent=MagicMock(),
            VibeEngineeringAgent=MagicMock(),
            ScoutAgent=MagicMock(),
            CompetitorIntelligenceService=MagicMock(),
            SentimentAnalyzer=MagicMock(),
            SocialAestheticsAnalyzer=MagicMock(),
            CompetitorParser=MagicMock(),
            NeighborhoodAnalyzer=MagicMock(),
            ContextProcessor=MagicMock(),
            CompetitorEnrichmentService=MagicMock()
        ) as mocks:
            yield mocks
    
    @pytest.mark.asyncio
    async def test_full_pipeline_stages(self, mock_all_agents):
        """Test that pipeline transitions through all stages."""
        orchestrator = AnalysisOrchestrator()
        
        # Mock all stage handlers to prevent actual execution
        orchestrator._extract_menus = AsyncMock()
        orchestrator._analyze_dish_images = AsyncMock()
        orchestrator._run_competitor_parsing = AsyncMock()
        orchestrator._run_competitor_discovery = AsyncMock()
        orchestrator._run_competitor_enrichment = AsyncMock()
        orchestrator._run_competitor_verification = AsyncMock()
        orchestrator._run_competitor_analysis = AsyncMock()
        orchestrator._run_neighborhood_analysis = AsyncMock()
        orchestrator._run_sentiment_analysis = AsyncMock()
        orchestrator._run_visual_gap_analysis = AsyncMock()
        orchestrator._run_context_processing = AsyncMock()
        orchestrator._process_sales_data = AsyncMock()
        orchestrator._run_bcg_classification = AsyncMock()
        orchestrator._run_sales_prediction = AsyncMock()
        orchestrator._generate_campaigns = AsyncMock()
        orchestrator._run_strategic_verification = AsyncMock()
        orchestrator._verify_analysis = AsyncMock()
        
        # Create a test session
        session_id = await orchestrator.create_session()
        state = orchestrator.active_sessions[session_id]
        
        # Verify initial state
        assert state.current_stage == PipelineStage.INITIALIZED
        assert len(state.checkpoints) == 0
        
        # Simulate minimal pipeline execution with menu data
        state.menu_items = [{"name": "Test Item", "price": 10.0}]
        
        # Test stage transition
        await orchestrator._run_stage(
            state,
            PipelineStage.MENU_EXTRACTION,
            orchestrator._extract_menus,
            []
        )
        
        assert orchestrator._extract_menus.called
        assert state.current_stage == PipelineStage.MENU_EXTRACTION
        assert len(state.checkpoints) > 0
        assert state.checkpoints[-1].stage == PipelineStage.MENU_EXTRACTION
        assert state.checkpoints[-1].success is True
    
    @pytest.mark.asyncio
    async def test_checkpoint_recovery(self, mock_all_agents):
        """Test pipeline recovery from checkpoint."""
        orchestrator = AnalysisOrchestrator()
        
        # Create a session with existing checkpoint
        session_id = await orchestrator.create_session()
        state = orchestrator.active_sessions[session_id]
        
        # Manually add a checkpoint for BCG_CLASSIFICATION
        from app.services.orchestrator import PipelineCheckpoint
        from datetime import datetime, timezone
        
        checkpoint = PipelineCheckpoint(
            stage=PipelineStage.BCG_CLASSIFICATION,
            timestamp=datetime.now(timezone.utc),
            data={"bcg_analysis": {"portfolio_assessment": {"health_score": 7.5}}},
            thought_trace=["BCG analysis completed"],
            success=True
        )
        state.checkpoints.append(checkpoint)
        state.current_stage = PipelineStage.BCG_CLASSIFICATION
        
        # Mock the stage handler
        orchestrator._run_bcg_classification = AsyncMock()
        
        # Try to run the same stage again
        await orchestrator._run_stage(
            state,
            PipelineStage.BCG_CLASSIFICATION,
            orchestrator._run_bcg_classification,
            ThinkingLevel.STANDARD
        )
        
        # Should skip execution due to checkpoint
        assert not orchestrator._run_bcg_classification.called
        assert state.current_stage == PipelineStage.BCG_CLASSIFICATION
    
    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, mock_all_agents):
        """Test pipeline error handling and checkpoint on failure."""
        orchestrator = AnalysisOrchestrator()
        
        # Create a test session
        session_id = await orchestrator.create_session()
        state = orchestrator.active_sessions[session_id]
        
        # Mock a stage handler that raises an exception
        async def failing_handler(state):
            raise ValueError("Simulated pipeline failure")
        
        orchestrator._extract_menus = failing_handler
        
        # Attempt to run the failing stage
        with pytest.raises(ValueError, match="Simulated pipeline failure"):
            await orchestrator._run_stage(
                state,
                PipelineStage.MENU_EXTRACTION,
                orchestrator._extract_menus
            )
        
        # Verify error checkpoint was created
        assert len(state.checkpoints) > 0
        assert state.checkpoints[-1].stage == PipelineStage.MENU_EXTRACTION
        assert state.checkpoints[-1].success is False
        assert "Simulated pipeline failure" in state.checkpoints[-1].error
    
    @pytest.mark.asyncio
    async def test_thought_trace_recording(self, mock_all_agents):
        """Test that thought traces are recorded during pipeline execution."""
        orchestrator = AnalysisOrchestrator()
        
        # Create a test session
        session_id = await orchestrator.create_session()
        state = orchestrator.active_sessions[session_id]
        
        # Verify initial thought trace from session creation
        assert len(state.thought_traces) > 0
        assert state.thought_traces[0].step == "Session Initialization"
        
        # Add a custom thought trace
        orchestrator._add_thought_trace(
            state,
            step="Test Step",
            reasoning="Testing thought trace recording",
            observations=["Observation 1", "Observation 2"],
            decisions=["Decision 1"],
            confidence=0.95
        )
        
        # Verify thought trace was added
        assert len(state.thought_traces) == 2
        assert state.thought_traces[1].step == "Test Step"
        assert state.thought_traces[1].reasoning == "Testing thought trace recording"
        assert state.thought_traces[1].confidence == 0.95
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, mock_all_agents):
        """Test session state persistence to disk."""
        orchestrator = AnalysisOrchestrator()
        
        # Create a test session
        session_id = await orchestrator.create_session()
        state = orchestrator.active_sessions[session_id]
        
        # Add some data to the state
        state.menu_items = [{"name": "Test Item", "price": 10.0}]
        state.restaurant_name = "Test Restaurant"
        
        # Save to disk
        orchestrator._save_session_to_disk(state)
        
        # Load from disk
        loaded_state = orchestrator._load_session_from_disk(session_id)
        
        # Verify loaded state matches
        assert loaded_state is not None
        assert loaded_state.session_id == session_id
        assert loaded_state.restaurant_name == "Test Restaurant"
        assert len(loaded_state.menu_items) == 1
        assert loaded_state.menu_items[0]["name"] == "Test Item"
    
    @pytest.mark.asyncio
    async def test_multimodal_capabilities_integration(self, mock_all_agents):
        """Test that pipeline leverages Gemini 3 multimodal capabilities."""
        orchestrator = AnalysisOrchestrator()
        
        # Verify that the orchestrator uses GeminiAgent (Gemini 3)
        assert orchestrator.gemini is not None
        
        # Verify that multimodal agents are initialized
        assert orchestrator.menu_extractor is not None
        assert orchestrator.competitor_parser is not None
        assert orchestrator.visual_gap_analyzer is not None
        
        # Create a test session
        session_id = await orchestrator.create_session()
        state = orchestrator.active_sessions[session_id]
        
        # Mock multimodal extraction
        orchestrator._extract_menus = AsyncMock()
        orchestrator._analyze_dish_images = AsyncMock()
        
        # Simulate multimodal pipeline stages
        await orchestrator._run_stage(
            state,
            PipelineStage.MENU_EXTRACTION,
            orchestrator._extract_menus,
            [b'fake_image_data']
        )
        
        await orchestrator._run_stage(
            state,
            PipelineStage.IMAGE_ANALYSIS,
            orchestrator._analyze_dish_images,
            [b'fake_dish_image']
        )
        
        # Verify multimodal stages were executed
        assert orchestrator._extract_menus.called
        assert orchestrator._analyze_dish_images.called
        
        # Verify checkpoints for multimodal stages
        checkpoint_stages = [cp.stage for cp in state.checkpoints]
        assert PipelineStage.MENU_EXTRACTION in checkpoint_stages
        assert PipelineStage.IMAGE_ANALYSIS in checkpoint_stages
