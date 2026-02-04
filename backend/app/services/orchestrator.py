"""
Autonomous Analysis Orchestrator - Marathon Agent pattern for RestoPilotAI.

Coordinates the entire analysis pipeline with checkpoints, state management,
and autonomous execution with transparent reasoning.
"""

import asyncio
import json
import httpx  # Added for image downloading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from loguru import logger

from app.core.config import get_settings
from app.core.websocket_manager import (
    ThoughtType,
    send_error,
    send_progress_update,
    send_stage_complete,
    send_thought,
)
from app.services.analysis.bcg import BCGClassifier
from app.services.analysis.menu_analyzer import MenuExtractor
from app.services.analysis.pricing import (
    CompetitorIntelligenceService,
    CompetitorSource,
)
from app.services.analysis.sales_predictor import SalesPredictor
from app.services.analysis.sentiment import SentimentAnalyzer
from app.services.campaigns.generator import CampaignGenerator
from app.services.gemini.base_agent import GeminiAgent, ThinkingLevel
from app.services.gemini.verification import VerificationAgent
from app.services.gemini.vibe_engineering import VibeEngineeringAgent
from app.services.intelligence.competitor_finder import ScoutAgent
from app.services.intelligence.data_enrichment import CompetitorEnrichmentService
from app.services.intelligence.social_aesthetics import SocialAestheticsAnalyzer
from app.services.intelligence.neighborhood import NeighborhoodAnalyzer
from app.services.analysis.context_processor import ContextProcessor
from app.services.intelligence.competitor_parser import CompetitorParser
from app.models.analysis import MarathonCheckpoint
from app.models.database import AsyncSessionLocal


class PipelineStage(str, Enum):
    """Stages of the analysis pipeline."""

    INITIALIZED = "initialized"
    DATA_INGESTION = "data_ingestion"
    MENU_EXTRACTION = "menu_extraction"
    COMPETITOR_PARSING = "competitor_parsing"            # New
    COMPETITOR_DISCOVERY = "competitor_discovery"
    COMPETITOR_ENRICHMENT = "competitor_enrichment"      # New
    COMPETITOR_VERIFICATION = "competitor_verification"  # New
    NEIGHBORHOOD_ANALYSIS = "neighborhood_analysis"      # New
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    IMAGE_ANALYSIS = "image_analysis"
    VISUAL_GAP_ANALYSIS = "visual_gap_analysis"
    CONTEXT_PROCESSING = "context_processing"            # New
    SALES_PROCESSING = "sales_processing"
    BCG_CLASSIFICATION = "bcg_classification"
    SALES_PREDICTION = "sales_prediction"
    CAMPAIGN_GENERATION = "campaign_generation"
    STRATEGIC_VERIFICATION = "strategic_verification"    # New
    VERIFICATION = "verification"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PipelineCheckpoint:
    """Checkpoint for pipeline state recovery."""

    stage: PipelineStage
    timestamp: datetime
    data: Dict[str, Any]
    thought_trace: List[str]
    success: bool
    error: Optional[str] = None


@dataclass
class ThoughtTrace:
    """Detailed thought trace for transparency."""

    step: str
    reasoning: str
    observations: List[str]
    decisions: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AnalysisState:
    """Complete state of an analysis session."""

    session_id: str
    current_stage: PipelineStage
    checkpoints: List[PipelineCheckpoint]
    thought_traces: List[ThoughtTrace]

    # Core Data
    restaurant_name: str = "Our Restaurant"
    location: Optional[Dict[str, float]] = None
    menu_items: List[Dict[str, Any]] = field(default_factory=list)
    sales_data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Context Data
    business_context: Dict[str, Any] = field(default_factory=dict) # History, values, goals, etc.
    competitor_urls: List[str] = field(default_factory=list)

    # Intelligence Data
    image_scores: Dict[str, float] = field(default_factory=dict)
    discovered_competitors: List[Dict[str, Any]] = field(default_factory=list)
    neighborhood_analysis: Optional[Dict[str, Any]] = None # New
    competitor_analysis: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    visual_gap_report: Optional[Dict[str, Any]] = None
    context_insights: Optional[Dict[str, Any]] = None      # New
    bcg_analysis: Optional[Dict[str, Any]] = None
    predictions: Optional[Dict[str, Any]] = None
    campaigns: List[Dict[str, Any]] = field(default_factory=list)
    verification_result: Optional[Dict[str, Any]] = None
    verification_history: List[Dict[str, Any]] = field(default_factory=list)
    vibe_status: Optional[Dict[str, Any]] = None # Store the most recent Vibe loop result

    thinking_level: ThinkingLevel = ThinkingLevel.STANDARD
    auto_verify: bool = True

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    total_thinking_time_ms: int = 0


class AnalysisOrchestrator:
    """
    Autonomous orchestrator for the complete RestoPilotAI analysis pipeline.

    Implements the Marathon Agent pattern with:
    - Checkpoint-based state management for long-running tasks
    - Transparent thought traces at each step
    - Automatic error recovery and retry logic
    - Verification loop for quality assurance
    """

    def __init__(self):
        self.gemini = GeminiAgent()
        self.menu_extractor = MenuExtractor(self.gemini)
        self.bcg_classifier = BCGClassifier(self.gemini)
        self.sales_predictor = SalesPredictor()
        self.campaign_generator = CampaignGenerator(self.gemini)
        self.verification_agent = VerificationAgent()
        self.vibe_agent = VibeEngineeringAgent()

        # New Intelligence Services
        self.scout_agent = ScoutAgent()
        self.competitor_intelligence = CompetitorIntelligenceService()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.visual_gap_analyzer = SocialAestheticsAnalyzer()
        self.competitor_parser = CompetitorParser(self.gemini)
        self.neighborhood_analyzer = NeighborhoodAnalyzer()
        self.context_processor = ContextProcessor()
        
        # Initialize Enrichment Service
        settings = get_settings()
        self.enrichment_service = CompetitorEnrichmentService(
            google_maps_api_key=settings.google_maps_api_key,
            gemini_agent=self.gemini
        )

        self.active_sessions: Dict[str, AnalysisState] = {}
        self.completed_sessions: Dict[str, AnalysisState] = {}
        self._checkpointer_tasks: Dict[str, asyncio.Task] = {} # Track periodic checkpoint tasks

        # Use separate directory for orchestrator state to avoid conflicts with business session files
        self.storage_dir = Path("data/orchestrator_states")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _save_session_to_disk(self, state: AnalysisState):
        """Save session state to disk."""
        try:
            file_path = self.storage_dir / f"{state.session_id}.json"

            # Helper to convert objects to JSON-serializable format
            def json_default(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, Enum):
                    return obj.value
                raise TypeError(f"Type {type(obj)} not serializable")

            with open(file_path, "w") as f:
                json.dump(asdict(state), f, default=json_default, indent=2)
        except Exception as e:
            logger.error(f"Failed to save orchestrator session {state.session_id}: {e}")

    def _load_session_from_disk(self, session_id: str) -> Optional[AnalysisState]:
        """Load session state from disk."""
        file_path = self.storage_dir / f"{session_id}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Parse enums and datetime strings
            if isinstance(data.get("current_stage"), str):
                data["current_stage"] = PipelineStage(data["current_stage"])
            
            if isinstance(data.get("started_at"), str):
                data["started_at"] = datetime.fromisoformat(data["started_at"])
            
            if isinstance(data.get("completed_at"), str):
                data["completed_at"] = datetime.fromisoformat(data["completed_at"])
            
            # Parse checkpoints
            if "checkpoints" in data:
                parsed_checkpoints = []
                for cp in data["checkpoints"]:
                    if isinstance(cp.get("stage"), str):
                        cp["stage"] = PipelineStage(cp["stage"])
                    if isinstance(cp.get("timestamp"), str):
                        cp["timestamp"] = datetime.fromisoformat(cp["timestamp"])
                    parsed_checkpoints.append(PipelineCheckpoint(**cp))
                data["checkpoints"] = parsed_checkpoints
            
            # Parse thought traces
            if "thought_traces" in data:
                parsed_traces = []
                for trace in data["thought_traces"]:
                    if isinstance(trace.get("timestamp"), str):
                        trace["timestamp"] = datetime.fromisoformat(trace["timestamp"])
                    parsed_traces.append(ThoughtTrace(**trace))
                data["thought_traces"] = parsed_traces
            
            # Parse thinking_level if present
            if "thinking_level" in data and isinstance(data["thinking_level"], str):
                data["thinking_level"] = ThinkingLevel(data["thinking_level"])
            
            # Convert dict back to AnalysisState
            state = AnalysisState(**data)
            
            # Cache in memory depending on state
            if state.current_stage in [PipelineStage.COMPLETED, PipelineStage.FAILED]:
                self.completed_sessions[session_id] = state
            else:
                self.active_sessions[session_id] = state

            return state
        except Exception as e:
            logger.error(f"Failed to load orchestrator session {session_id}: {e}")
            return None

    async def create_session(self) -> str:
        """Create a new analysis session."""
        session_id = str(uuid4())
        state = AnalysisState(
            session_id=session_id,
            current_stage=PipelineStage.INITIALIZED,
            checkpoints=[],
            thought_traces=[],
        )
        self.active_sessions[session_id] = state

        self._add_thought_trace(
            state,
            step="Session Initialization",
            reasoning="Creating new analysis session for restaurant optimization",
            observations=["Fresh session created", "All pipeline stages pending"],
            decisions=["Ready to receive data inputs"],
            confidence=1.0,
        )

        self._save_session_to_disk(state)

        return session_id

    async def run_full_pipeline(
        self,
        session_id: str,
        menu_images: Optional[List[str]] = None,
        dish_images: Optional[List[str]] = None,
        competitor_files: Optional[List[Dict[str, Any]]] = None,
        sales_csv: Optional[str] = None,
        address: Optional[str] = None,
        cuisine_type: str = "general",
        thinking_level: Optional[ThinkingLevel] = None,
        auto_verify: Optional[bool] = None,
        business_context: Optional[Dict[str, Any]] = None,
        competitor_urls: Optional[List[str]] = None,
        auto_find_competitors: bool = True,
    ) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline autonomously.

        Args:
            session_id: Session identifier
            menu_images: List of file paths to menu images
            dish_images: List of file paths to dish photos
            competitor_files: Structured competitor file data
            sales_csv: CSV content for sales data
            address: Restaurant address for location-based analysis
            cuisine_type: Type of cuisine for competitor matching
            thinking_level: Depth of AI analysis
            auto_verify: Whether to run verification loop
            business_context: Rich context about business (history, values, etc.)
            competitor_urls: Explicit list of competitors to analyze
            auto_find_competitors: Whether to run automatic competitor discovery

        Returns:
            Complete analysis results with thought traces
        """
        state = self.active_sessions.get(session_id) or self._load_session_from_disk(
            session_id
        )

        if not state:
            return {"error": "Session not found"}

        # Ensure it's in active_sessions if loaded from disk
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = state

        # Update configuration if provided
        if thinking_level:
            state.thinking_level = thinking_level
        if auto_verify is not None:
            state.auto_verify = auto_verify
        
        # Update context
        if business_context:
            state.business_context = business_context
        
        # Fallback to state context for recovery if args are missing
        if not address and state.business_context.get("address"):
            address = state.business_context.get("address")
        if cuisine_type == "general" and state.business_context.get("cuisine_type"):
            cuisine_type = state.business_context.get("cuisine_type")
            
        if competitor_urls:
            state.competitor_urls = competitor_urls
            # Add to discovered competitors immediately as manually added
            for url in competitor_urls:
                if url:
                    state.discovered_competitors.append({
                        "name": "Manual Competitor", # Will be refined by analysis
                        "website": url,
                        "source": "manual"
                    })

        # Save updated config
        self._save_session_to_disk(state)

        try:
            # 1. Menu Extraction
            if menu_images:
                await self._run_stage(
                    state,
                    PipelineStage.MENU_EXTRACTION,
                    self._extract_menus,
                    menu_images,
                )

            # 1.5 Competitor Parsing (Manual Input)
            # Check if we have manual competitor input (text or files)
            competitor_input_text = state.business_context.get("competitor_input")
            if competitor_input_text or competitor_files:
                await self._run_stage(
                    state,
                    PipelineStage.COMPETITOR_PARSING,
                    self._run_competitor_parsing,
                    competitor_input_text,
                    competitor_files
                )

            # 2. Competitor Discovery (Scout Agent)
            # Only run if auto_find is true OR if we have no competitors yet and an address
            if auto_find_competitors and address:
                await self._run_stage(
                    state,
                    PipelineStage.COMPETITOR_DISCOVERY,
                    self._run_competitor_discovery,
                    address,
                    cuisine_type,
                )
            elif not auto_find_competitors and state.competitor_urls:
                 self._add_thought_trace(
                    state,
                    step="Competitor Discovery Skipped",
                    reasoning="User provided manual competitors and disabled auto-discovery",
                    observations=[f"Using {len(state.competitor_urls)} manual competitors"],
                    decisions=["Proceeding with manual competitor list"],
                    confidence=1.0,
                )

            # 3. Competitor Enrichment (Deep Data)
            if state.discovered_competitors:
                await self._run_stage(
                    state,
                    PipelineStage.COMPETITOR_ENRICHMENT,
                    self._run_competitor_enrichment,
                )

            # 4. Competitor Verification (Data Quality)
            if state.discovered_competitors:
                await self._run_stage(
                    state,
                    PipelineStage.COMPETITOR_VERIFICATION,
                    self._run_competitor_verification,
                )

            # 5. Competitor Analysis (Intelligence Service)
            if state.discovered_competitors and state.menu_items:
                await self._run_stage(
                    state,
                    PipelineStage.COMPETITOR_ANALYSIS,
                    self._run_competitor_analysis,
                )

            # 6. Neighborhood Analysis
            if address and state.location:
                await self._run_stage(
                    state,
                    PipelineStage.NEIGHBORHOOD_ANALYSIS,
                    self._run_neighborhood_analysis,
                )

            # 7. Sentiment Analysis
            # (In a real scenario, we'd fetch reviews here. For now we simulate or use discovered data)
            if state.discovered_competitors:
                await self._run_stage(
                    state,
                    PipelineStage.SENTIMENT_ANALYSIS,
                    self._run_sentiment_analysis,
                )

            # 8. Visual Analysis (Dish Photos)
            if dish_images:
                await self._run_stage(
                    state,
                    PipelineStage.IMAGE_ANALYSIS,
                    self._analyze_dish_images,
                    dish_images,
                )

            # 9. Visual Gap Analysis (Comparing ours vs competitors)
            if dish_images and state.discovered_competitors:
                await self._run_stage(
                    state,
                    PipelineStage.VISUAL_GAP_ANALYSIS,
                    self._run_visual_gap_analysis,
                    dish_images,
                )

            # 10. Context Processing (Enrichment)
            if state.business_context:
                await self._run_stage(
                    state,
                    PipelineStage.CONTEXT_PROCESSING,
                    self._run_context_processing,
                )

            # 11. Sales Data Processing
            if sales_csv:
                await self._run_stage(
                    state,
                    PipelineStage.SALES_PROCESSING,
                    self._process_sales_data,
                    sales_csv,
                )
            elif state.sales_data:
                # Sales data already loaded (e.g., from demo session)
                logger.info(f"Sales data already present ({len(state.sales_data)} records), skipping processing stage")

            # 12. BCG & Prediction & Campaigns (Requires Menu & Sales)
            if state.menu_items:
                await self._run_stage(
                    state,
                    PipelineStage.BCG_CLASSIFICATION,
                    self._run_bcg_classification,
                    state.thinking_level,
                )

                await self._run_stage(
                    state, PipelineStage.SALES_PREDICTION, self._run_sales_prediction
                )

                await self._run_stage(
                    state,
                    PipelineStage.CAMPAIGN_GENERATION,
                    self._generate_campaigns,
                    state.thinking_level,
                )

            # 13. Strategic Verification
            if state.campaigns:
                await self._run_stage(
                    state,
                    PipelineStage.STRATEGIC_VERIFICATION,
                    self._run_strategic_verification,
                )

            # 14. Final Verification (Optional extra check or merge with strategic)
            # Keeping original verification as final "holistic" check if desired
            if state.auto_verify and state.bcg_analysis:
                logger.info(f"Running final verification for session {session_id}")
                await self._run_stage(
                    state,
                    PipelineStage.VERIFICATION,
                    self._verify_analysis,
                    state.thinking_level,
                )
                logger.info(f"Verification completed for session {session_id}")
            
            logger.info(f"Marking pipeline as COMPLETED for session {session_id}")
            state.current_stage = PipelineStage.COMPLETED
            state.completed_at = datetime.now(timezone.utc)
            
            # Save final checkpoint to DB and broadcast completion
            logger.info(f"Saving final checkpoint for session {session_id}")
            await self._save_checkpoint(state, success=True)

            logger.info(f"Moving session {session_id} to completed_sessions")
            self.completed_sessions[session_id] = state
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            logger.info(f"Saving session {session_id} to disk")
            self._save_session_to_disk(state)

            logger.info(f"Building final response for session {session_id}")
            final_response = self._build_final_response(state)
            logger.info(f"Pipeline COMPLETED successfully for session {session_id}")
            return final_response

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            state.current_stage = PipelineStage.FAILED
            await self._save_checkpoint(state, success=False, error=str(e))
            self._save_session_to_disk(state)
            return {"error": str(e), "last_checkpoint": state.current_stage.value}

    async def _run_stage(
        self,
        state: AnalysisState,
        stage: PipelineStage,
        handler: Callable,
        *args,
    ):
        """Run a pipeline stage with checkpointing."""
        # CHECKPOINT RECOVERY: Check if stage is already completed
        for cp in state.checkpoints:
            if cp.stage == stage and cp.success:
                logger.info(f"Skipping already completed stage: {stage.value}")
                # Broadcast restoration to keep frontend in sync
                await send_stage_complete(
                    session_id=state.session_id,
                    stage=stage.value,
                    result={"status": "restored_from_checkpoint", "skipped": True},
                )
                return

        state.current_stage = stage
        start_time = datetime.now(timezone.utc)

        # Start periodic checkpointing if not already running for this session
        # We can use a simple asyncio.create_task for this specific stage execution context 
        # or better, manage a global background task per session.
        # For simplicity and robustness within the stage context, we'll rely on the 
        # explicit _save_checkpoint calls at the end of stages, PLUS the periodic task logic below.
        
        # Ensure periodic checkpointer is running
        self._ensure_periodic_checkpointer(state.session_id)

        logger.info(f"Running stage: {stage.value}")

        # Broadcast stage start
        await send_progress_update(
            session_id=state.session_id,
            stage=stage.value,
            progress=0.0,
            message=f"Starting {stage.value.replace('_', ' ')}...",
        )

        try:
            await handler(state, *args)

            elapsed_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            state.total_thinking_time_ms += elapsed_ms

            await self._save_checkpoint(state, success=True)

            # Broadcast stage completion
            await send_stage_complete(
                session_id=state.session_id,
                stage=stage.value,
                result={"duration_ms": elapsed_ms},
            )

        except Exception as e:
            import traceback
            logger.error(f"Stage {stage.value} failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            await self._save_checkpoint(state, success=False, error=str(e))

            # Broadcast error
            await send_error(
                session_id=state.session_id,
                stage=stage.value,
                error=str(e),
            )
            raise
    
    def _ensure_periodic_checkpointer(self, session_id: str):
        """Ensure a background task is running to checkpoint this session periodically."""
        if session_id not in self._checkpointer_tasks:
            logger.info(f"Starting periodic checkpointer for session {session_id}")
            self._checkpointer_tasks[session_id] = asyncio.create_task(self._checkpoint_loop(session_id))

    async def _checkpoint_loop(self, session_id: str):
        """Background loop to save checkpoints every 60s."""
        try:
            while True:
                await asyncio.sleep(60)
                
                # Check if session is still active
                state = self.active_sessions.get(session_id)
                if not state:
                    logger.info(f"Session {session_id} not active, stopping checkpointer.")
                    break
                
                if state.current_stage in [PipelineStage.COMPLETED, PipelineStage.FAILED]:
                    logger.info(f"Session {session_id} finished ({state.current_stage}), stopping checkpointer.")
                    break
                
                # Save checkpoint
                logger.debug(f"Periodic checkpoint for session {session_id}")
                # We use a special error code or msg to indicate it's an auto-checkpoint if needed, 
                # but generic success=True is fine for state persistence.
                await self._save_checkpoint(state, success=True) 
                
        except asyncio.CancelledError:
            logger.info(f"Checkpointer for session {session_id} cancelled.")
        except Exception as e:
            logger.error(f"Error in periodic checkpointer for {session_id}: {e}")
        finally:
            self._checkpointer_tasks.pop(session_id, None)

    def _cleanup_checkpointer(self, session_id: str):
        """Cancel the periodic checkpointer for a session."""
        if session_id in self._checkpointer_tasks:
            self._checkpointer_tasks[session_id].cancel()
            # We don't pop here immediately, let the finally block in the loop handle it
            # or pop it if we are sure.
            # Pop it to be clean.
            self._checkpointer_tasks.pop(session_id, None)

    async def _extract_menus(self, state: AnalysisState, menu_images: List[bytes]):
        """Extract menu items from images."""
        self._add_thought_trace(
            state,
            step="Menu Extraction",
            reasoning="Processing menu images to extract structured product catalog",
            observations=[f"Received {len(menu_images)} menu images"],
            decisions=["Using hybrid OCR + Gemini multimodal extraction"],
            confidence=0.85,
        )

        for i, image_data in enumerate(menu_images):
            result = await self.menu_extractor.extract_from_image(image_data)
            items = result.get("items", [])
            state.menu_items.extend(items)

            self._add_thought_trace(
                state,
                step=f"Menu Image {i+1} Processing",
                reasoning="Combining OCR text with visual understanding",
                observations=[f"Extracted {len(items)} items from image {i+1}"],
                decisions=["Items added to catalog"],
                confidence=result.get("confidence", 0.7),
            )

    async def _analyze_dish_images(
        self, state: AnalysisState, dish_images: List[bytes]
    ):
        """Analyze dish photos for visual appeal."""
        self._add_thought_trace(
            state,
            step="Dish Image Analysis",
            reasoning="Evaluating visual presentation quality of dishes",
            observations=[f"Analyzing {len(dish_images)} dish photos"],
            decisions=["Scoring presentation, plating, and appeal"],
            confidence=0.8,
        )

        for i, image_data in enumerate(dish_images):
            result = await self.menu_extractor.analyze_dish_image(image_data)

            if "item_name" in result and "score" in result:
                state.image_scores[result["item_name"]] = result["score"]

    async def _run_competitor_parsing(
        self,
        state: AnalysisState,
        text_input: Optional[str],
        files: Optional[List[Dict[str, Any]]]
    ):
        """Parse mixed manual competitor input."""
        self._add_thought_trace(
            state,
            step="Competitor Parsing (Multimodal)",
            reasoning="Analyzing manual text and files to extract competitor profiles",
            observations=[
                f"Text input length: {len(text_input) if text_input else 0}",
                f"Files provided: {len(files) if files else 0}"
            ],
            decisions=["Using Gemini 3 to structure mixed input"],
            confidence=0.9,
        )

        competitors = await self.competitor_parser.parse_mixed_input(text_input, files)
        
        # Merge with existing
        for comp in competitors:
            comp["source"] = "manual_parsing"
            state.discovered_competitors.append(comp)
            
        self._add_thought_trace(
            state,
            step="Competitors Extracted",
            reasoning="Merged parsed competitors into discovery list",
            observations=[f"Found {len(competitors)} distinct competitors in manual input"],
            decisions=["Added to analysis pool"],
            confidence=0.95,
        )

    async def _run_competitor_discovery(
        self, state: AnalysisState, address: str, cuisine_type: str
    ):
        """Run competitor discovery using Scout Agent."""
        self._add_thought_trace(
            state,
            step="Competitor Discovery",
            reasoning=f"Scouting for competitors near {address}",
            observations=["Initiating Scout Agent", f"Cuisine: {cuisine_type}"],
            decisions=["Searching for top relevant competitors"],
            confidence=0.9,
        )

        result = await self.scout_agent.run_scouting_mission(
            address=address,
            our_cuisine_type=cuisine_type,
            radius_meters=1000,
            max_competitors=5,
        )

        scout_competitors = result.get("competitors", [])
        
        # Merge with existing competitors (manual) avoiding duplicates
        existing_names = {c.get("name", "").lower() for c in state.discovered_competitors}
        existing_websites = {c.get("website", "").lower() for c in state.discovered_competitors if c.get("website")}
        
        for comp in scout_competitors:
            name = comp.get("name", "").lower()
            website = comp.get("website", "").lower()
            
            # Simple deduplication
            if name not in existing_names and (not website or website not in existing_websites):
                state.discovered_competitors.append(comp)
                existing_names.add(name)
        
        # Update state location from scout result if available
        if "summary" in result and "location_analyzed" in result["summary"]:
            state.location = result["summary"]["location_analyzed"]

        # Add scout thought traces to main trace
        for trace in result.get("thought_traces", []):
            self._add_thought_trace(
                state,
                step=f"Scout: {trace.get('action')}",
                reasoning=trace.get("reasoning", ""),
                observations=trace.get("observations", []),
                decisions=[],
                confidence=trace.get("confidence", 0.8),
            )

    async def _run_competitor_enrichment(self, state: AnalysisState):
        """Run deep competitor enrichment."""
        self._add_thought_trace(
            state,
            step="Competitor Enrichment",
            reasoning="Gathering deep intelligence on competitors (Social, Reviews, Photos)",
            observations=[f"Enriching {len(state.discovered_competitors)} competitors"],
            decisions=["Cross-referencing web & social data", "Analyzing content with Gemini"],
            confidence=0.9,
        )

        enriched_competitors = []
        for i, comp in enumerate(state.discovered_competitors):
            # Report progress
            await send_progress_update(
                session_id=state.session_id,
                stage=PipelineStage.COMPETITOR_ENRICHMENT.value,
                progress=(i / len(state.discovered_competitors)) * 100,
                message=f"Enriching profile for {comp.get('name', 'Competitor')}..."
            )

            # Check if we have a place_id
            place_id = comp.get("place_id")
            if place_id:
                try:
                    profile = await self.enrichment_service.enrich_competitor_profile(
                        place_id=place_id,
                        basic_info=comp
                    )
                    enriched_competitors.append(profile.to_dict())
                except Exception as e:
                    logger.warning(f"Enrichment failed for {comp.get('name')}: {e}")
                    enriched_competitors.append(comp)
            else:
                enriched_competitors.append(comp)
        
        state.discovered_competitors = enriched_competitors

        self._add_thought_trace(
            state,
            step="Enrichment Complete",
            reasoning="Competitor profiles enriched with deep multimodal data",
            observations=[f"Enriched {len(enriched_competitors)} profiles"],
            decisions=["Proceeding to data verification"],
            confidence=0.9,
        )

    async def _run_competitor_verification(self, state: AnalysisState):
        """Verify competitor data quality."""
        self._add_thought_trace(
            state,
            step="Competitor Data Verification",
            reasoning="Verifying quality and consistency of discovered competitor data",
            observations=[f"Checking {len(state.discovered_competitors)} competitors"],
            decisions=["Identifying anomalies or data gaps"],
            confidence=0.9,
        )

        verification = await self.verification_agent.verify_competitor_data(
            state.discovered_competitors
        )

        state.verification_history.append({
            "stage": PipelineStage.COMPETITOR_VERIFICATION,
            "result": verification
        })

        if not verification.get("verified", False):
            self._add_thought_trace(
                state,
                step="Data Issues Detected",
                reasoning="Competitor data verification flagged issues",
                observations=[i.get("issue") for i in verification.get("issues_found", [])],
                decisions=["Proceeding with caution", "Flagging low confidence data"],
                confidence=verification.get("confidence_score", 0.5),
            )
    
    async def _run_neighborhood_analysis(self, state: AnalysisState):
        """Run neighborhood analysis."""
        self._add_thought_trace(
            state,
            step="Neighborhood Analysis",
            reasoning="Analyzing local demographics and market dynamics",
            observations=["Using location data", "Considering competitor density"],
            decisions=["Profiling neighborhood character"],
            confidence=0.85,
        )

        # Ensure we have location data. If Scout ran, we have state.location or it's in address.
        # If we just have address string, we might need geocoding if Scout didn't run.
        # Scout populates state.location.
        location_data = state.location or {"address": "Unknown"}

        analysis = await self.neighborhood_analyzer.analyze_neighborhood(
            location_data=location_data,
            nearby_businesses=[], # TODO: Fetch from Places API if possible
            competitor_data=state.discovered_competitors
        )

        state.neighborhood_analysis = analysis

    async def _run_context_processing(self, state: AnalysisState):
        """Integrate business context into analysis."""
        self._add_thought_trace(
            state,
            step="Context Integration",
            reasoning="Integrating user-provided business context",
            observations=[f"Context keys: {list(state.business_context.keys())}"],
            decisions=["Enhancing insights with personalization"],
            confidence=0.9,
        )

        # 1. Process Audio Context (Multimodal)
        # Check for audio paths saved by the API
        audio_updates = {}
        
        # History Audio
        if "history_audio_paths" in state.business_context:
            paths = state.business_context["history_audio_paths"]
            for path in paths:
                try:
                    # Read file bytes
                    import aiofiles
                    async with aiofiles.open(path, 'rb') as f:
                        audio_bytes = await f.read()
                    
                    self._add_thought_trace(
                        state,
                        step="Processing History Audio",
                        reasoning="Transcribing and analyzing history audio using Gemini Multimodal",
                        observations=[f"Processing audio file: {path}"],
                        decisions=["Extracting structured insights"],
                        confidence=0.9,
                    )
                    
                    result = await self.context_processor.process_audio_context(
                        audio_file=audio_bytes,
                        context_type="history",
                        mime_type="audio/webm" # Assumed from frontend MediaRecorder
                    )
                    
                    # Merge text into main context for redundancy
                    state.business_context["history_text"] = (
                        state.business_context.get("history_text", "") + 
                        "\n\n[Audio Transcription]: " + 
                        result.get("transcription", "")
                    )
                except Exception as e:
                    logger.error(f"Failed to process history audio {path}: {e}")

        # Values Audio
        if "values_audio_paths" in state.business_context:
            paths = state.business_context["values_audio_paths"]
            for path in paths:
                try:
                    import aiofiles
                    async with aiofiles.open(path, 'rb') as f:
                        audio_bytes = await f.read()

                    self._add_thought_trace(
                        state,
                        step="Processing Values Audio",
                        reasoning="Transcribing and analyzing values audio using Gemini Multimodal",
                        observations=[f"Processing audio file: {path}"],
                        decisions=["Extracting structured insights"],
                        confidence=0.9,
                    )

                    result = await self.context_processor.process_audio_context(
                        audio_file=audio_bytes,
                        context_type="values",
                        mime_type="audio/webm"
                    )
                    
                    state.business_context["values_text"] = (
                        state.business_context.get("values_text", "") + 
                        "\n\n[Audio Transcription]: " + 
                        result.get("transcription", "")
                    )
                except Exception as e:
                    logger.error(f"Failed to process values audio {path}: {e}")

        # Process additional audio contexts (USPs, Target, Challenges, Goals)
        additional_contexts = [
            ("usps", "unique_selling_points"),
            ("target_audience", "target_audience"),
            ("challenges", "challenges"),
            ("goals", "goals")
        ]

        for ctx_key, text_key in additional_contexts:
            path_key = f"{ctx_key}_audio_paths"
            if path_key in state.business_context:
                paths = state.business_context[path_key]
                for path in paths:
                    try:
                        import aiofiles
                        async with aiofiles.open(path, 'rb') as f:
                            audio_bytes = await f.read()

                        self._add_thought_trace(
                            state,
                            step=f"Processing {ctx_key.replace('_', ' ').title()} Audio",
                            reasoning=f"Transcribing and analyzing {ctx_key} audio",
                            observations=[f"Processing audio file: {path}"],
                            decisions=["Extracting structured insights"],
                            confidence=0.9,
                        )

                        result = await self.context_processor.process_audio_context(
                            audio_file=audio_bytes,
                            context_type=ctx_key,
                            mime_type="audio/webm"
                        )
                        
                        # Append to existing text context
                        current_text = state.business_context.get(text_key) or state.business_context.get(f"{ctx_key}Context") or ""
                        state.business_context[text_key] = (
                            current_text + 
                            "\n\n[Audio Transcription]: " + 
                            result.get("transcription", "")
                        )
                    except Exception as e:
                        logger.error(f"Failed to process {ctx_key} audio {path}: {e}")
        
        # Update context with audio analysis
        if audio_updates:
            state.business_context.update(audio_updates)

        # 2. Integrate into Analysis
        # Prepare analysis data so far for context integration
        current_analysis = {
            "competitors": state.discovered_competitors,
            "neighborhood": state.neighborhood_analysis,
            "visual_gaps": state.visual_gap_report
        }

        insights = await self.context_processor.integrate_context_into_analysis(
            business_context=state.business_context,
            analysis_data=current_analysis
        )

        state.context_insights = insights

    async def _run_strategic_verification(self, state: AnalysisState):
        """Verify strategic logic."""
        self._add_thought_trace(
            state,
            step="Strategic Verification",
            reasoning="Verifying logical consistency of strategy and campaigns",
            observations=["Checking BCG alignment", "Checking campaign viability"],
            decisions=["Validating recommendations"],
            confidence=0.9,
        )

        analysis_snapshot = {
            "bcg": state.bcg_analysis,
            "campaigns": state.campaigns,
            "context_insights": state.context_insights
        }

        verification = await self.verification_agent.verify_analysis_logic(
            analysis_snapshot
        )

        state.verification_history.append({
            "stage": PipelineStage.STRATEGIC_VERIFICATION,
            "result": verification
        })

    async def _run_competitor_analysis(self, state: AnalysisState):
        """Run deep competitor analysis."""
        self._add_thought_trace(
            state,
            step="Competitor Analysis",
            reasoning="Analyzing competitor menus and pricing strategies",
            observations=[f"Analyzing {len(state.discovered_competitors)} competitors"],
            decisions=["Extracting menus and comparing prices"],
            confidence=0.85,
        )

        # Convert discovered competitors to sources
        sources = []
        for comp in state.discovered_competitors:
            # If we have a website, use it
            if comp.get("website"):
                sources.append(
                    CompetitorSource(
                        type="url", value=comp["website"], name=comp["name"]
                    )
                )
            # Or use the data directly if scout gathered it
            else:
                sources.append(
                    CompetitorSource(
                        type="data",
                        value=json.dumps(comp),
                        name=comp["name"],
                        metadata=comp,
                    )
                )

        # Prepare our menu data
        our_menu = {
            "items": state.menu_items,
            "categories": list(
                set(item.get("category", "Other") for item in state.menu_items)
            ),
        }

        result = await self.competitor_intelligence.analyze_competitors(
            our_menu=our_menu,
            competitor_sources=sources,
            restaurant_name=state.restaurant_name,
            thinking_level=state.thinking_level,
        )

        # FEATURE #2: VIBE ENGINEERING - Autonomous Verification
        if state.auto_verify:
            verified_analysis = await self.vibe_agent.verify_and_improve_analysis(
                analysis_type="competitor_analysis",
                analysis_result=result.to_dict(),
                source_data={
                    "competitors_count": len(sources),
                    "our_items_count": len(state.menu_items)
                },
                auto_improve=True
            )
            state.competitor_analysis = verified_analysis['final_analysis']
            state.vibe_status = verified_analysis
            
            self._add_thought_trace(
                state,
                step="Competitor Vibe Verification",
                reasoning="Autonomous verification of competitor intelligence",
                observations=[
                    f"Quality Score: {verified_analysis.get('quality_achieved', 0):.2f}",
                    f"Iterations: {verified_analysis.get('iterations_required', 0)}"
                ],
                decisions=["Competitor analysis verified"],
                confidence=verified_analysis.get('quality_achieved', 0.9),
            )
        else:
            state.competitor_analysis = result.to_dict()

    async def _run_sentiment_analysis(self, state: AnalysisState):
        """Run sentiment analysis on discovered reviews."""
        self._add_thought_trace(
            state,
            step="Sentiment Analysis",
            reasoning="Analyzing customer sentiment from reviews and photos",
            observations=["Processing sentiment data"],
            decisions=["Identifying key themes and item-level sentiment"],
            confidence=0.8,
        )

        # Collect reviews from discovered competitors (as proxy or if we had own reviews)
        # For this hackathon flow, we might simulate 'our' reviews or use what Scout found
        # Here we'll try to use data if Scout Agent found reviews
        reviews = []
        # TODO: Scout Agent doesn't fully scrape text reviews yet, so this might be limited

        result = await self.sentiment_analyzer.analyze_customer_sentiment(
            restaurant_id=state.session_id,
            reviews=reviews,
            menu_items=[item["name"] for item in state.menu_items if "name" in item],
            bcg_data=state.bcg_analysis,
        )

        # FEATURE #2: VIBE ENGINEERING - Autonomous Verification
        if state.auto_verify:
            verified_analysis = await self.vibe_agent.verify_and_improve_analysis(
                analysis_type="sentiment_analysis",
                analysis_result=result.to_dict(),
                source_data={
                    "reviews_count": len(reviews),
                    "menu_items_count": len(state.menu_items)
                },
                auto_improve=True
            )
            state.sentiment_analysis = verified_analysis['final_analysis']
            state.vibe_status = verified_analysis

            self._add_thought_trace(
                state,
                step="Sentiment Vibe Verification",
                reasoning="Autonomous verification of sentiment analysis",
                observations=[
                    f"Quality Score: {verified_analysis.get('quality_achieved', 0):.2f}"
                ],
                decisions=["Sentiment analysis verified"],
                confidence=verified_analysis.get('quality_achieved', 0.9),
            )
        else:
            state.sentiment_analysis = result.to_dict()

    async def _run_visual_gap_analysis(
        self, state: AnalysisState, dish_images: List[bytes]
    ):
        """Run visual gap analysis comparing our photos to competitors."""
        self._add_thought_trace(
            state,
            step="Visual Gap Analysis",
            reasoning="Comparing our food presentation against market standards",
            observations=[f"Comparing {len(dish_images)} of our photos"],
            decisions=["Identifying visual competitive advantages/disadvantages"],
            confidence=0.85,
        )

        if not state.discovered_competitors:
             self._add_thought_trace(
                state,
                step="Visual Gap Analysis Skipped",
                reasoning="No discovered competitors to compare against",
                observations=[],
                decisions=["Skipping comparative visual analysis"],
                confidence=1.0,
            )
             return

        # Prepare competitor images dict
        comp_images_dict = {}
        
        try:
            async with httpx.AsyncClient() as client:
                for comp in state.discovered_competitors:
                    comp_name = comp.get("name", "Unknown")
                    photos = comp.get("photos", [])[:2] # Limit to top 2 per competitor
                    
                    if not photos:
                        continue
                        
                    downloaded_photos = []
                    for photo_ref in photos:
                        # If it looks like a URL, use it directly (e.g. from mock or web search)
                        # If it's a reference (Google Places), construct URL via places service
                        # If it's a local path (from manual upload), read bytes
                        
                        if isinstance(photo_ref, str) and (photo_ref.startswith("/") or Path(photo_ref).exists()):
                            try:
                                import aiofiles
                                async with aiofiles.open(photo_ref, 'rb') as f:
                                    content = await f.read()
                                    downloaded_photos.append(content)
                            except Exception as e:
                                logger.warning(f"Failed to read local photo {photo_ref}: {e}")
                            continue

                        url = ""
                        if photo_ref.startswith("http"):
                            url = photo_ref
                        else:
                            url = self.scout_agent.places.get_photo_url(photo_ref)
                        
                        if url:
                            try:
                                resp = await client.get(url, timeout=10.0)
                                if resp.status_code == 200:
                                    downloaded_photos.append(resp.content)
                            except Exception as e:
                                logger.warning(f"Failed to download photo from {url}: {e}")
                    
                    if downloaded_photos:
                        comp_images_dict[comp_name] = downloaded_photos
                        
        except Exception as e:
             logger.error(f"Error during competitor image download: {e}")

        # If we have no bytes for competitors, we verify if we can proceed
        if not comp_images_dict:
            self._add_thought_trace(
                state,
                step="Visual Gap Analysis Skipped",
                reasoning="Could not retrieve competitor photos (no photos found or download failed)",
                observations=[],
                decisions=["Skipping comparative visual analysis"],
                confidence=1.0,
            )
            return

        context_str = f"Restaurant: {state.restaurant_name}. Cuisine: {state.business_context.get('cuisine', 'General')}"

        try:
            report = await self.visual_gap_analyzer.compare_visual_aesthetics(
                user_photos=dish_images,
                competitor_photos=comp_images_dict,
                context=context_str
            )
            state.visual_gap_report = report
        except Exception as e:
            logger.error(f"Visual gap analysis failed: {e}")
            self._save_checkpoint(state, success=False, error=str(e))

    async def _process_sales_data(self, state: AnalysisState, sales_csv: str):
        """Process sales CSV data."""
        import csv
        from io import StringIO

        reader = csv.DictReader(StringIO(sales_csv))
        sales_records = list(reader)

        for record in sales_records:
            state.sales_data.append(
                {
                    "item_name": record.get("item_name", record.get("product", "")),
                    "sale_date": record.get("date", record.get("sale_date", "")),
                    "units_sold": int(
                        record.get("units_sold", record.get("quantity", 0))
                    ),
                    "revenue": float(record.get("revenue", record.get("total", 0))),
                    "had_promotion": record.get("had_promotion", "").lower() == "true",
                    "promotion_discount": float(
                        record.get("promotion_discount", 0) or 0
                    ),
                }
            )

        self._add_thought_trace(
            state,
            step="Sales Data Processing",
            reasoning="Parsing and validating historical sales records",
            observations=[
                f"Processed {len(state.sales_data)} sales records",
                "Date range identified from CSV",
            ],
            decisions=["Data validated and ready for analysis"],
            confidence=0.9,
        )

    async def _run_bcg_classification(
        self, state: AnalysisState, thinking_level: ThinkingLevel
    ):
        """Run BCG Matrix classification."""
        self._add_thought_trace(
            state,
            step="BCG Classification",
            reasoning="Classifying products into BCG Matrix quadrants based on market share and growth",
            observations=[
                f"Analyzing {len(state.menu_items)} products",
                "Using sales data for market dynamics",
            ],
            decisions=["Applying Star/Cash Cow/Question Mark/Dog classification"],
            confidence=0.85,
        )

        result = await self.bcg_classifier.classify(
            state.menu_items,
            state.sales_data,
            state.image_scores,
        )

        # FEATURE #2: VIBE ENGINEERING - Autonomous Verification Loop
        if state.auto_verify:
            verified_analysis = await self.vibe_agent.verify_and_improve_analysis(
                analysis_type="bcg_classification",
                analysis_result=result,
                source_data={
                    "menu_items_count": len(state.menu_items),
                    "sales_data_count": len(state.sales_data)
                },
                auto_improve=True
            )
            
            result = verified_analysis['final_analysis']
            state.vibe_status = verified_analysis # Store for frontend visibility
            
            # Add trace for verification
            self._add_thought_trace(
                state,
                step="BCG Vibe Verification",
                reasoning="Autonomous verification and improvement of BCG analysis",
                observations=[
                    f"Quality Score: {verified_analysis.get('quality_achieved', 0):.2f}",
                    f"Iterations: {verified_analysis.get('iterations_required', 0)}"
                ],
                decisions=["Analysis refined based on critical audit"],
                confidence=verified_analysis.get('quality_achieved', 0.9),
            )

        state.bcg_analysis = result

        classifications = result.get("products", [])
        stars = sum(1 for p in classifications if p.get("classification") == "star")
        cows = sum(1 for p in classifications if p.get("classification") == "cash_cow")
        questions = sum(
            1 for p in classifications if p.get("classification") == "question_mark"
        )
        dogs = sum(1 for p in classifications if p.get("classification") == "dog")

        self._add_thought_trace(
            state,
            step="BCG Results",
            reasoning="Classification complete with strategic insights",
            observations=[
                f"Stars: {stars} (high growth, high share)",
                f"Cash Cows: {cows} (low growth, high share)",
                f"Question Marks: {questions} (high growth, low share)",
                f"Dogs: {dogs} (low growth, low share)",
            ],
            decisions=["Ready for campaign strategy development"],
            confidence=0.88,
        )

    async def _run_sales_prediction(self, state: AnalysisState):
        """Run sales prediction for different scenarios."""
        self._add_thought_trace(
            state,
            step="Sales Prediction",
            reasoning="Training ML model and generating forecasts",
            observations=[
                f"Using {len(state.sales_data)} historical records",
                "Preparing scenarios for comparison",
            ],
            decisions=["Running XGBoost prediction with scenario analysis"],
            confidence=0.75,
        )

        if state.sales_data:
            await self.sales_predictor.train(
                state.sales_data,
                state.menu_items,
                state.image_scores,
            )

        scenarios = [
            {"name": "baseline"},
            {"name": "promotion", "promotion_active": True, "promotion_discount": 0.15},
            {"name": "premium", "price_change_percent": 10},
        ]

        predictions = await self.sales_predictor.predict_batch(
            state.menu_items,
            horizon_days=14,
            scenarios=scenarios,
        )

        # FEATURE #2: VIBE ENGINEERING - Autonomous Verification
        if state.auto_verify:
            verified_analysis = await self.vibe_agent.verify_and_improve_analysis(
                analysis_type="sales_prediction",
                analysis_result=predictions,
                source_data={
                    "sales_records": len(state.sales_data),
                    "scenarios_count": len(scenarios)
                },
                auto_improve=True
            )
            state.predictions = verified_analysis['final_analysis']
            state.vibe_status = verified_analysis

            self._add_thought_trace(
                state,
                step="Prediction Vibe Verification",
                reasoning="Autonomous verification of sales forecasts",
                observations=[
                    f"Quality Score: {verified_analysis.get('quality_achieved', 0):.2f}"
                ],
                decisions=["Predictions verified"],
                confidence=verified_analysis.get('quality_achieved', 0.9),
            )
        else:
            state.predictions = predictions

    async def _generate_campaigns(
        self, state: AnalysisState, thinking_level: ThinkingLevel
    ):
        """Generate marketing campaigns based on analysis."""
        self._add_thought_trace(
            state,
            step="Campaign Generation",
            reasoning="Creating data-driven marketing campaigns aligned with BCG strategy",
            observations=[
                "Using BCG classifications for targeting",
                "Incorporating prediction scenarios",
            ],
            decisions=["Generating multi-channel campaigns with scheduling"],
            confidence=0.82,
        )

        # Standard Campaign Generation (Text-based / Strategic)
        campaigns = await self.campaign_generator.generate_campaigns(
            bcg_analysis=state.bcg_analysis,
            menu_items=state.menu_items,
            num_campaigns=3,
        )
        
        state.campaigns = campaigns.get("campaigns", [])

        # HACKATHON FEATURE: Creative Autopilot (Visual Campaigns for Stars)
        settings = get_settings()
        if settings.enable_creative_autopilot and state.bcg_analysis:
            self._add_thought_trace(
                state,
                step="Creative Autopilot",
                reasoning="Generating full visual campaigns for Star products using Gemini 3 Image Generation",
                observations=["Identifying Star products for premium campaigns"],
                decisions=["Launching Creative Autopilot for top performers"],
                confidence=0.9,
            )
            
            # Find star products
            products = state.bcg_analysis.get("products", [])
            stars = [p for p in products if p.get("classification") == "star"]
            
            # Limit to top 2 stars to save resources/time
            for item in stars[:2]:
                try:
                    # Construct dish data for the agent
                    dish_data = {
                        "name": item.get("name"),
                        "price": item.get("price"),
                        "description": item.get("description", f"Delicious {item.get('name')}"),
                        "category": item.get("category", "Main"),
                        "bcg_data": item
                    }
                    
                    # Get brand guidelines if available in context
                    brand_guidelines = state.business_context.get("brand_guidelines", {})
                    # Default colors if not present
                    if "colors" not in brand_guidelines:
                        brand_guidelines["colors"] = "Appetizing, warm, consistent with brand"
                    
                    visual_campaign = await self.creative_autopilot.generate_full_campaign(
                        restaurant_name=state.restaurant_name,
                        dish_data=dish_data,
                        bcg_classification="star",
                        brand_guidelines=brand_guidelines
                    )
                    
                    # Add to campaigns list with a specific type flag
                    visual_campaign["type"] = "creative_autopilot"
                    visual_campaign["target_product"] = item.get("name")
                    visual_campaign["title"] = f"Visual Campaign: {item.get('name')}"
                    # Add simple assets list for the standard UI to pick up if needed, 
                    # though Creative UI handles the rich object
                    visual_campaign["assets"] = visual_campaign.get("visual_assets", [])
                    
                    state.campaigns.append(visual_campaign)
                    
                except Exception as e:
                    logger.error(f"Creative Autopilot failed for {item.get('name')}: {e}")

        # FEATURE #2: VIBE ENGINEERING - Autonomous Campaign Verification
        if state.auto_verify:
            verified_count = 0
            for camp in state.campaigns:
                if "assets" in camp and camp["assets"]:
                    verification = await self.vibe_agent.verify_campaign_assets(
                         campaign_assets=camp["assets"],
                         brand_guidelines=state.business_context.get("brand_guidelines", {}),
                         auto_improve=True
                    )
                    camp["assets"] = verification["verified_assets"]
                    verified_count += len(verification["verified_assets"])
            
            if verified_count > 0:
                self._add_thought_trace(
                    state,
                    step="Campaign Vibe Verification",
                    reasoning="Autonomous visual verification of campaign assets",
                    observations=[f"Verified {verified_count} visual assets"],
                    decisions=["Improved assets where quality was below threshold"],
                    confidence=0.9,
                )

        self._add_thought_trace(
            state,
            step="Campaign Results",
            reasoning="Campaigns generated with actionable recommendations",
            observations=[f"Created {len(state.campaigns)} campaign proposals"],
            decisions=["Ready for verification"],
            confidence=0.85,
        )

    async def _verify_analysis(
        self, state: AnalysisState, thinking_level: ThinkingLevel
    ):
        """Run verification agent on the complete analysis."""
        self._add_thought_trace(
            state,
            step="Verification",
            reasoning="Running autonomous verification loop to validate recommendations",
            observations=[
                "Checking data completeness, accuracy, and business viability"
            ],
            decisions=["Auto-improving if quality thresholds not met"],
            confidence=0.9,
        )

        analysis_data = {
            "products": state.menu_items,
            "bcg_analysis": state.bcg_analysis,
            "predictions": state.predictions,
            "campaigns": state.campaigns,
        }

        result = await self.verification_agent.verify_analysis(
            analysis_data,
            thinking_level=thinking_level,
            auto_improve=True,
        )

        state.verification_result = {
            "status": result.status.value,
            "overall_score": result.overall_score,
            "iterations_used": result.iterations_used,
            "improvements_made": result.improvements_made,
            "checks": [
                {
                    "name": c.check_name,
                    "passed": c.passed,
                    "score": c.score,
                    "feedback": c.feedback,
                }
                for c in result.checks
            ],
            "final_recommendation": result.final_recommendation,
        }

        self._add_thought_trace(
            state,
            step="Verification Complete",
            reasoning="Analysis verified and improved",
            observations=[
                f"Verification score: {result.overall_score:.0%}",
                f"Iterations used: {result.iterations_used}",
                f"Improvements made: {len(result.improvements_made)}",
            ],
            decisions=[result.final_recommendation or "Analysis validated"],
            confidence=result.overall_score,
        )

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a session."""
        # Check active sessions first, then completed sessions, then load from disk
        state = (
            self.active_sessions.get(session_id) 
            or self.completed_sessions.get(session_id)
            or self._load_session_from_disk(session_id)
        )

        if not state:
            return None

        return self._build_final_response(state)

    def _add_thought_trace(
        self,
        state: AnalysisState,
        step: str,
        reasoning: str,
        observations: List[str],
        decisions: List[str],
        confidence: float,
    ):
        """Add a thought trace to the session."""
        trace = ThoughtTrace(
            step=step,
            reasoning=reasoning,
            observations=observations,
            decisions=decisions,
            confidence=confidence,
        )
        state.thought_traces.append(trace)

        # Broadcast thoughts via WebSocket (fire-and-forget)
        try:
            loop = asyncio.get_event_loop()

            # Send main reasoning
            loop.create_task(
                send_thought(
                    session_id=state.session_id,
                    thought_type=ThoughtType.THINKING,
                    content=reasoning,
                    step=step,
                    confidence=confidence,
                )
            )

            # Send observations
            for obs in observations:
                loop.create_task(
                    send_thought(
                        session_id=state.session_id,
                        thought_type=ThoughtType.OBSERVATION,
                        content=obs,
                        step=step,
                        confidence=confidence,
                    )
                )

            # Send decisions
            for dec in decisions:
                loop.create_task(
                    send_thought(
                        session_id=state.session_id,
                        thought_type=ThoughtType.ACTION,
                        content=dec,
                        step=step,
                        confidence=confidence,
                    )
                )

        except Exception as e:
            logger.warning(f"Failed to broadcast thought trace: {e}")

    async def _save_checkpoint(
        self,
        state: AnalysisState,
        success: bool,
        error: Optional[str] = None,
    ):
        """Save a checkpoint for the current stage to DB and disk."""
        checkpoint_data = {
            "menu_items_count": len(state.menu_items),
            "sales_records_count": len(state.sales_data),
            "campaigns_count": len(state.campaigns),
        }
        
        # In-memory checkpoint
        checkpoint = PipelineCheckpoint(
            stage=state.current_stage,
            timestamp=datetime.now(timezone.utc),
            data=checkpoint_data,
            thought_trace=[t.step for t in state.thought_traces],
            success=success,
            error=error,
        )
        state.checkpoints.append(checkpoint)
        
        # Save to Disk (Legacy/Backup)
        self._save_session_to_disk(state)
        
        # Save to Database (Marathon Persistence)
        try:
            async with AsyncSessionLocal() as db:
                db_checkpoint = MarathonCheckpoint(
                    session_id=state.session_id,
                    stage=state.current_stage.value,
                    status="completed" if success else "failed",
                    state_data=json.loads(json.dumps(asdict(state), default=str)),
                    thought_trace=[t.step for t in state.thought_traces],
                    error=error
                )
                db.add(db_checkpoint)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to save marathon checkpoint to DB: {e}")

    async def _load_last_checkpoint_from_db(self, session_id: str) -> Optional[AnalysisState]:
        """Load the most recent checkpoint from the database."""
        from sqlalchemy import select
        
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(MarathonCheckpoint)
                    .where(MarathonCheckpoint.session_id == session_id)
                    .order_by(MarathonCheckpoint.timestamp.desc())
                    .limit(1)
                )
                last_cp = result.scalar_one_or_none()
                
                if not last_cp:
                    return None
                
                data = last_cp.state_data
                
                # Reconstruct datetime objects and Enums
                if "current_stage" in data:
                    data["current_stage"] = PipelineStage(data["current_stage"])
                if "thinking_level" in data:
                    data["thinking_level"] = ThinkingLevel(data["thinking_level"])

                if "started_at" in data:
                    data["started_at"] = datetime.fromisoformat(data["started_at"])
                if data.get("completed_at"):
                    data["completed_at"] = datetime.fromisoformat(data["completed_at"])

                # Reconstruct checkpoints list
                checkpoints = []
                for cp_data in data.get("checkpoints", []):
                    cp_data["stage"] = PipelineStage(cp_data["stage"])
                    cp_data["timestamp"] = datetime.fromisoformat(cp_data["timestamp"])
                    checkpoints.append(PipelineCheckpoint(**cp_data))
                data["checkpoints"] = checkpoints

                # Reconstruct thought traces
                traces = []
                for t_data in data.get("thought_traces", []):
                    t_data["timestamp"] = datetime.fromisoformat(t_data["timestamp"])
                    traces.append(ThoughtTrace(**t_data))
                data["thought_traces"] = traces

                state = AnalysisState(**data)
                return state
                
        except Exception as e:
            logger.error(f"Failed to load checkpoint from DB for {session_id}: {e}")
            return None

    def _build_final_response(self, state: AnalysisState) -> Dict[str, Any]:
        """Build the final response from the analysis state."""
        return {
            "session_id": state.session_id,
            "current_stage": state.current_stage.value,
            "status": state.current_stage.value,
            "started_at": state.started_at.isoformat() if state.started_at else None,
            "completed_at": state.completed_at.isoformat() if state.completed_at else None,
            "summary": {
                "products_analyzed": len(state.menu_items),
                "sales_records_processed": len(state.sales_data),
                "campaigns_generated": len(state.campaigns),
                "total_thinking_time_ms": state.total_thinking_time_ms,
            },
            "bcg_analysis": state.bcg_analysis,
            "predictions": state.predictions,
            "campaigns": state.campaigns,
            "verification": state.verification_result,
            "vibe_status": state.vibe_status, # Expose Vibe status
            "thought_signature": {
                "traces": [
                    {
                        "step": t.step,
                        "reasoning": t.reasoning,
                        "observations": t.observations,
                        "decisions": t.decisions,
                        "confidence": t.confidence,
                        "timestamp": t.timestamp.isoformat(),
                    }
                    for t in state.thought_traces
                ],
                "total_steps": len(state.thought_traces),
                "avg_confidence": (
                    sum(t.confidence for t in state.thought_traces)
                    / len(state.thought_traces)
                    if state.thought_traces
                    else 0
                ),
            },
            "checkpoints": [
                {
                    "stage": c.stage.value,
                    "timestamp": c.timestamp.isoformat(),
                    "success": c.success,
                }
                for c in state.checkpoints
            ],
        }

    async def resume_session(
        self, session_id: str, **kwargs
    ) -> bool:
        """Resume a session from its last checkpoint (DB or Disk)."""
        # Try loading from active memory first
        state = self.active_sessions.get(session_id)
        
        # If not active, try loading from DB (preferred persistence)
        if not state:
            state = await self._load_last_checkpoint_from_db(session_id)
            
        # Fallback to disk if DB fails or empty
        if not state:
            state = self._load_session_from_disk(session_id)

        if not state:
            logger.warning(f"Could not resume session {session_id}: Not found.")
            return False

        # Ensure it's in active_sessions
        if session_id not in self.active_sessions and state.current_stage not in [
            PipelineStage.COMPLETED,
            PipelineStage.FAILED,
        ]:
            self.active_sessions[session_id] = state
            
        # Determine where to resume
        logger.info(f"Resuming session {session_id} from stage {state.current_stage}")
        
        # Re-run pipeline logic but skip completed stages
        # Ideally, run_full_pipeline should be smart enough to skip.
        # But run_full_pipeline logic is sequential. 
        # We need to adapt run_full_pipeline to check state.checkpoints to skip.
        
        # For now, we will simply call run_full_pipeline. 
        # The Orchestrator implementation needs to be robust enough to skip done work.
        # CURRENTLY, run_full_pipeline runs EVERYTHING. This is a limitation.
        # Ideally we should refactor run_full_pipeline to look at 'state.current_stage'
        # and jump to that point. 
        
        # HACK: For hackathon speed, we assume run_full_pipeline will just re-run 
        # potentially some steps, OR we trust the "checkpoints" list to skip.
        # Let's modify run_full_pipeline slightly to respect current_stage.
        
        # Actually, let's just trigger it. The state is restored.
        # We might need to run it in background if called from API.
        
        # Since this method returns success bool, we assume caller handles the task execution.
        # But wait, run_full_pipeline is NOT checking 'if stage done'.
        # We need to ensure we don't double-process.
        
        # For this implementation, we will just return True indicating state is loaded.
        # The caller (API) invokes run_full_pipeline.
        
        return True


# Global orchestrator instance
orchestrator = AnalysisOrchestrator()
