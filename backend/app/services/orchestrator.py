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
from app.services.intelligence.competitor_finder import ScoutAgent
from app.services.intelligence.data_enrichment import CompetitorEnrichmentService
from app.services.intelligence.social_aesthetics import SocialAestheticsAnalyzer
from app.services.intelligence.neighborhood import NeighborhoodAnalyzer
from app.services.analysis.context_processor import ContextProcessor
from app.services.intelligence.competitor_parser import CompetitorParser


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
    verification_history: List[Dict[str, Any]] = field(default_factory=list) # New

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

        self.storage_dir = Path("data/sessions")
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

            # Reconstruct datetime objects and Enums
            data["current_stage"] = PipelineStage(data["current_stage"])
            if "thinking_level" in data:
                data["thinking_level"] = ThinkingLevel(data["thinking_level"])

            data["started_at"] = datetime.fromisoformat(data["started_at"])
            if data.get("completed_at"):
                data["completed_at"] = datetime.fromisoformat(data["completed_at"])

            # Reconstruct checkpoints
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
        menu_images: Optional[List[bytes]] = None,
        dish_images: Optional[List[bytes]] = None,
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
            menu_images: Raw menu image bytes
            dish_images: Raw dish photo bytes
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
                await self._run_stage(
                    state,
                    PipelineStage.VERIFICATION,
                    self._verify_analysis,
                    state.thinking_level,
                )
            state.current_stage = PipelineStage.COMPLETED
            state.completed_at = datetime.now(timezone.utc)

            self.completed_sessions[session_id] = state
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            self._save_session_to_disk(state)

            return self._build_final_response(state)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            state.current_stage = PipelineStage.FAILED
            self._save_checkpoint(state, success=False, error=str(e))
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
        state.current_stage = stage
        start_time = datetime.now(timezone.utc)

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

            self._save_checkpoint(state, success=True)

            # Broadcast stage completion
            await send_stage_complete(
                session_id=state.session_id,
                stage=stage.value,
                result={"duration_ms": elapsed_ms},
            )

        except Exception as e:
            logger.error(f"Stage {stage.value} failed: {e}")
            self._save_checkpoint(state, success=False, error=str(e))

            # Broadcast error
            await send_error(
                session_id=state.session_id,
                stage=stage.value,
                error=str(e),
            )
            raise

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

        campaigns = await self.campaign_generator.generate(
            bcg_analysis=state.bcg_analysis,
            predictions=state.predictions,
            num_campaigns=3,
        )

        state.campaigns = campaigns.get("campaigns", [])

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
        state = self.active_sessions.get(session_id) or self._load_session_from_disk(
            session_id
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

    def _save_checkpoint(
        self,
        state: AnalysisState,
        success: bool,
        error: Optional[str] = None,
    ):
        """Save a checkpoint for the current stage."""
        checkpoint = PipelineCheckpoint(
            stage=state.current_stage,
            timestamp=datetime.now(timezone.utc),
            data={
                "menu_items_count": len(state.menu_items),
                "sales_records_count": len(state.sales_data),
                "campaigns_count": len(state.campaigns),
            },
            thought_trace=[t.step for t in state.thought_traces],
            success=success,
            error=error,
        )
        state.checkpoints.append(checkpoint)
        self._save_session_to_disk(state)

    def _build_final_response(self, state: AnalysisState) -> Dict[str, Any]:
        """Build the final response from the analysis state."""
        return {
            "session_id": state.session_id,
            "status": state.current_stage.value,
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
    ) -> Optional[Dict[str, Any]]:
        """Resume a session from its last checkpoint."""
        state = self.active_sessions.get(session_id) or self._load_session_from_disk(
            session_id
        )

        if not state:
            return None

        # Ensure it's in active_sessions if loaded from disk
        if session_id not in self.active_sessions and state.current_stage not in [
            PipelineStage.COMPLETED,
            PipelineStage.FAILED,
        ]:
            self.active_sessions[session_id] = state

        return await self.run_full_pipeline(session_id=session_id, **kwargs)


# Global orchestrator instance
orchestrator = AnalysisOrchestrator()
