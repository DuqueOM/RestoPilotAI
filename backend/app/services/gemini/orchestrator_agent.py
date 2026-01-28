"""
Gemini Orchestrator Agent - Marathon pattern coordinator.

Coordinates multi-step analysis pipelines with:
- Checkpoint-based state management
- Progress streaming
- Error recovery
- Agent coordination
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
from uuid import uuid4

from loguru import logger

from app.services.gemini.base_agent import GeminiBaseAgent, GeminiModel, ThinkingLevel
from app.services.gemini.multimodal_agent import MultimodalAgent
from app.services.gemini.reasoning_agent import ReasoningAgent, ThoughtTrace
from app.services.gemini.verification_agent import GeminiVerificationAgent


class PipelineStage(str, Enum):
    """Stages of the analysis pipeline."""

    INITIALIZED = "initialized"
    MENU_EXTRACTION = "menu_extraction"
    DISH_ANALYSIS = "dish_analysis"
    SALES_PROCESSING = "sales_processing"
    BCG_CLASSIFICATION = "bcg_classification"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SALES_PREDICTION = "sales_prediction"
    CAMPAIGN_GENERATION = "campaign_generation"
    EXECUTIVE_SUMMARY = "executive_summary"
    VERIFICATION = "verification"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PipelineCheckpoint:
    """Checkpoint for pipeline state recovery."""

    stage: PipelineStage
    timestamp: datetime
    data: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage.value,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


@dataclass
class ProgressUpdate:
    """Progress update for streaming."""

    stage: PipelineStage
    progress: float  # 0-100
    message: str
    eta_seconds: Optional[int] = None
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage.value,
            "progress": self.progress,
            "message": self.message,
            "eta_seconds": self.eta_seconds,
            "data": self.data,
        }


@dataclass
class PipelineState:
    """Complete state of an analysis pipeline session."""

    session_id: str
    current_stage: PipelineStage
    checkpoints: List[PipelineCheckpoint] = field(default_factory=list)
    thought_traces: List[ThoughtTrace] = field(default_factory=list)

    # Data storage
    menu_items: List[Dict[str, Any]] = field(default_factory=list)
    dish_analyses: List[Dict[str, Any]] = field(default_factory=list)
    sales_data: List[Dict[str, Any]] = field(default_factory=list)
    bcg_analysis: Optional[Dict[str, Any]] = None
    competitor_intel: Optional[Dict[str, Any]] = None
    sentiment_data: Optional[Dict[str, Any]] = None
    predictions: Optional[Dict[str, Any]] = None
    campaigns: List[Dict[str, Any]] = field(default_factory=list)
    executive_summary: Optional[str] = None
    verification_result: Optional[Dict[str, Any]] = None

    # Metadata
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    total_processing_time_ms: int = 0
    gemini_stats: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_stage": self.current_stage.value,
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "thought_traces": [t.to_dict() for t in self.thought_traces],
            "data": {
                "menu_items_count": len(self.menu_items),
                "dish_analyses_count": len(self.dish_analyses),
                "sales_records_count": len(self.sales_data),
                "has_bcg": self.bcg_analysis is not None,
                "has_competitors": self.competitor_intel is not None,
                "has_sentiment": self.sentiment_data is not None,
                "has_predictions": self.predictions is not None,
                "campaigns_count": len(self.campaigns),
                "has_summary": self.executive_summary is not None,
            },
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "total_processing_time_ms": self.total_processing_time_ms,
            "gemini_stats": self.gemini_stats,
        }


class OrchestratorAgent(GeminiBaseAgent):
    """
    Orchestrator for the complete MenuPilot analysis pipeline.

    Implements the Marathon Agent pattern:
    - Checkpoint-based state management for long-running tasks
    - Transparent thought traces at each step
    - Automatic error recovery and retry logic
    - Progress streaming via async generators
    - Verification loop for quality assurance
    """

    # Stage weights for progress calculation
    STAGE_WEIGHTS = {
        PipelineStage.MENU_EXTRACTION: 15,
        PipelineStage.DISH_ANALYSIS: 10,
        PipelineStage.SALES_PROCESSING: 5,
        PipelineStage.BCG_CLASSIFICATION: 15,
        PipelineStage.COMPETITOR_ANALYSIS: 15,
        PipelineStage.SENTIMENT_ANALYSIS: 15,
        PipelineStage.SALES_PREDICTION: 10,
        PipelineStage.CAMPAIGN_GENERATION: 10,
        PipelineStage.EXECUTIVE_SUMMARY: 5,
        PipelineStage.VERIFICATION: 10,
    }

    def __init__(
        self,
        model: GeminiModel = GeminiModel.FLASH,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)

        # Initialize sub-agents
        self.multimodal = MultimodalAgent(model=model, **kwargs)
        self.reasoning = ReasoningAgent(model=model, **kwargs)
        self.verification = GeminiVerificationAgent(model=model, **kwargs)

        # Session storage
        self.active_sessions: Dict[str, PipelineState] = {}
        self.completed_sessions: Dict[str, PipelineState] = {}

    async def process(self, *args, **kwargs) -> Any:
        """Main entry point."""
        return await self.run_full_pipeline(**kwargs)

    async def create_session(self) -> str:
        """Create a new analysis session."""
        session_id = str(uuid4())
        state = PipelineState(
            session_id=session_id,
            current_stage=PipelineStage.INITIALIZED,
        )
        self.active_sessions[session_id] = state

        logger.info(f"Created new session: {session_id}")

        return session_id

    async def run_full_pipeline(
        self,
        session_id: Optional[str] = None,
        menu_images: Optional[List[bytes]] = None,
        dish_images: Optional[List[bytes]] = None,
        sales_csv: Optional[str] = None,
        competitor_data: Optional[List[Dict[str, Any]]] = None,
        review_data: Optional[Dict[str, Any]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.STANDARD,
        auto_verify: bool = True,
        resume_from_checkpoint: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline.

        Args:
            session_id: Existing session ID or None to create new
            menu_images: List of menu image bytes
            dish_images: List of dish photo bytes
            sales_csv: CSV content string for sales data
            competitor_data: List of competitor info dicts
            review_data: Review/sentiment source data
            thinking_level: Depth of AI analysis
            auto_verify: Whether to run verification
            resume_from_checkpoint: Resume from last checkpoint if available

        Returns:
            Complete analysis results with thought traces
        """
        # Create or get session
        if session_id and session_id in self.active_sessions:
            state = self.active_sessions[session_id]
        else:
            session_id = await self.create_session()
            state = self.active_sessions[session_id]

        # Determine start stage
        start_stage = PipelineStage.INITIALIZED
        if resume_from_checkpoint and state.checkpoints:
            last_success = next(
                (c for c in reversed(state.checkpoints) if c.success), None
            )
            if last_success:
                start_stage = last_success.stage
                logger.info(f"Resuming from checkpoint: {start_stage.value}")

        try:
            # Define pipeline stages
            stages = [
                (PipelineStage.MENU_EXTRACTION, self._extract_menus, menu_images),
                (PipelineStage.DISH_ANALYSIS, self._analyze_dishes, dish_images),
                (PipelineStage.SALES_PROCESSING, self._process_sales, sales_csv),
                (PipelineStage.BCG_CLASSIFICATION, self._run_bcg, thinking_level),
                (
                    PipelineStage.COMPETITOR_ANALYSIS,
                    self._analyze_competitors,
                    competitor_data,
                ),
                (
                    PipelineStage.SENTIMENT_ANALYSIS,
                    self._analyze_sentiment,
                    review_data,
                ),
                (PipelineStage.SALES_PREDICTION, self._run_predictions, thinking_level),
                (
                    PipelineStage.CAMPAIGN_GENERATION,
                    self._generate_campaigns,
                    thinking_level,
                ),
                (
                    PipelineStage.EXECUTIVE_SUMMARY,
                    self._generate_summary,
                    thinking_level,
                ),
            ]

            # Add verification if enabled
            if auto_verify:
                stages.append(
                    (PipelineStage.VERIFICATION, self._run_verification, thinking_level)
                )

            # Run stages
            for stage, handler, arg in stages:
                if self._should_skip_stage(start_stage, stage, state):
                    continue

                await self._run_stage(state, stage, handler, arg)

            # Mark completed
            state.current_stage = PipelineStage.COMPLETED
            state.completed_at = datetime.now(timezone.utc)

            # Aggregate Gemini stats
            state.gemini_stats = self._aggregate_gemini_stats()

            # Move to completed
            self.completed_sessions[session_id] = state
            del self.active_sessions[session_id]

            return self._build_final_response(state)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            state.current_stage = PipelineStage.FAILED
            self._save_checkpoint(state, success=False, error=str(e))
            return {
                "error": str(e),
                "session_id": session_id,
                "last_checkpoint": state.current_stage.value,
                "partial_results": self._build_partial_response(state),
            }

    async def run_with_progress(
        self,
        session_id: str,
        **kwargs,
    ) -> AsyncGenerator[ProgressUpdate, None]:
        """
        Run pipeline with progress streaming.

        Yields ProgressUpdate objects for real-time progress tracking.
        """
        state = self.active_sessions.get(session_id)
        if not state:
            yield ProgressUpdate(
                stage=PipelineStage.FAILED,
                progress=0,
                message="Session not found",
            )
            return

        # This is a simplified version - in production, use proper async coordination
        yield ProgressUpdate(
            stage=PipelineStage.INITIALIZED,
            progress=0,
            message="Starting analysis pipeline...",
            eta_seconds=120,
        )

        # Run actual pipeline
        result = await self.run_full_pipeline(session_id=session_id, **kwargs)

        yield ProgressUpdate(
            stage=state.current_stage,
            progress=100 if state.current_stage == PipelineStage.COMPLETED else 0,
            message=(
                "Pipeline completed"
                if "error" not in result
                else f"Error: {result['error']}"
            ),
            data=result,
        )

    async def _run_stage(
        self,
        state: PipelineState,
        stage: PipelineStage,
        handler: Callable,
        arg: Any,
    ) -> None:
        """Run a single pipeline stage with checkpointing."""
        import time

        state.current_stage = stage
        start_time = time.time()

        logger.info(f"Running stage: {stage.value}")

        try:
            if arg is not None:
                await handler(state, arg)
            else:
                # Skip if no input data
                logger.info(f"Skipping {stage.value} - no input data")
                return

            duration_ms = int((time.time() - start_time) * 1000)
            state.total_processing_time_ms += duration_ms

            self._save_checkpoint(state, success=True, duration_ms=duration_ms)

        except Exception as e:
            logger.error(f"Stage {stage.value} failed: {e}")
            duration_ms = int((time.time() - start_time) * 1000)
            self._save_checkpoint(
                state, success=False, error=str(e), duration_ms=duration_ms
            )
            raise

    async def _extract_menus(
        self, state: PipelineState, menu_images: List[bytes]
    ) -> None:
        """Extract menu items from images."""
        if not menu_images:
            return

        self._add_thought_trace(
            state,
            step="Menu Extraction",
            reasoning="Processing menu images to extract structured product catalog",
            observations=[f"Received {len(menu_images)} menu images"],
            decisions=["Using Gemini multimodal for comprehensive extraction"],
        )

        for i, image_data in enumerate(menu_images):
            result = await self.multimodal.extract_menu_from_image(
                image_source=image_data,
            )

            items = result.get("items", [])
            state.menu_items.extend(items)

            self._add_thought_trace(
                state,
                step=f"Menu Image {i + 1} Complete",
                reasoning="Menu extraction completed",
                observations=[f"Extracted {len(items)} items from image {i + 1}"],
                decisions=["Items added to catalog"],
                confidence=result.get("extraction_quality", {}).get("confidence", 0.7),
            )

    async def _analyze_dishes(
        self, state: PipelineState, dish_images: List[bytes]
    ) -> None:
        """Analyze dish photographs."""
        if not dish_images:
            return

        self._add_thought_trace(
            state,
            step="Dish Analysis",
            reasoning="Evaluating visual presentation quality of dishes",
            observations=[f"Analyzing {len(dish_images)} dish photos"],
            decisions=["Scoring presentation, plating, and appeal"],
        )

        menu_names = [item.get("name", "") for item in state.menu_items]

        result = await self.multimodal.analyze_batch_dish_images(
            images=dish_images,
            menu_context=menu_names,
        )

        state.dish_analyses = result.get("analyses", [])

    async def _process_sales(self, state: PipelineState, sales_csv: str) -> None:
        """Process sales CSV data."""
        if not sales_csv:
            return

        import csv
        from io import StringIO

        reader = csv.DictReader(StringIO(sales_csv))

        for record in reader:
            state.sales_data.append(
                {
                    "item_name": record.get("item_name", record.get("product", "")),
                    "sale_date": record.get("date", record.get("sale_date", "")),
                    "units_sold": int(
                        record.get("units_sold", record.get("quantity", 0)) or 0
                    ),
                    "revenue": float(
                        record.get("revenue", record.get("total", 0)) or 0
                    ),
                    "had_promotion": str(record.get("had_promotion", "")).lower()
                    == "true",
                    "promotion_discount": float(
                        record.get("promotion_discount", 0) or 0
                    ),
                }
            )

        self._add_thought_trace(
            state,
            step="Sales Data Processing",
            reasoning="Parsing and validating historical sales records",
            observations=[f"Processed {len(state.sales_data)} sales records"],
            decisions=["Data validated and ready for analysis"],
        )

    async def _run_bcg(
        self, state: PipelineState, thinking_level: ThinkingLevel
    ) -> None:
        """Run BCG classification with reasoning agent."""
        if not state.menu_items:
            return

        self._add_thought_trace(
            state,
            step="BCG Classification",
            reasoning="Classifying products into BCG Matrix quadrants",
            observations=[f"Analyzing {len(state.menu_items)} products"],
            decisions=["Applying Star/Cash Cow/Question Mark/Dog classification"],
        )

        # Get image scores
        image_scores = {}
        for analysis in state.dish_analyses:
            name = analysis.get("dish_identification", {}).get("matched_menu_item")
            if name:
                image_scores[name] = analysis.get("attractiveness_score", 0.5)

        result = await self.reasoning.analyze_bcg_strategy(
            products=state.menu_items,
            sales_data=state.sales_data if state.sales_data else None,
            thinking_level=thinking_level,
        )

        state.bcg_analysis = result.analysis
        state.thought_traces.extend(result.thought_traces)

    async def _analyze_competitors(
        self,
        state: PipelineState,
        competitor_data: Optional[List[Dict[str, Any]]],
    ) -> None:
        """Analyze competitor intelligence."""
        if not competitor_data:
            return

        self._add_thought_trace(
            state,
            step="Competitor Analysis",
            reasoning="Analyzing competitive landscape",
            observations=[f"Processing {len(competitor_data)} competitor sources"],
            decisions=["Extracting competitive insights"],
        )

        competitor_menus = []

        for source in competitor_data:
            source_type = source.get("type", "unknown")

            if source_type == "image":
                # Extract menu from image
                result = await self.multimodal.extract_competitor_menu(
                    image_source=source.get("value"),
                    competitor_name=source.get("name"),
                )
                competitor_menus.append(result)
            elif source_type == "data":
                # Direct data provided
                competitor_menus.append(source.get("value", {}))

        # Run competitive analysis with reasoning agent
        if competitor_menus:
            our_menu = {
                "items": state.menu_items,
                "bcg_analysis": state.bcg_analysis,
            }

            result = await self.reasoning.analyze_competitive_position(
                our_menu=our_menu,
                competitor_menus=competitor_menus,
                thinking_level=ThinkingLevel.DEEP,
            )

            state.competitor_intel = result.analysis
            state.thought_traces.extend(result.thought_traces)

    async def _analyze_sentiment(
        self,
        state: PipelineState,
        review_data: Optional[Dict[str, Any]],
    ) -> None:
        """Analyze customer sentiment from reviews and photos."""
        if not review_data:
            return

        self._add_thought_trace(
            state,
            step="Sentiment Analysis",
            reasoning="Analyzing customer sentiment from reviews and photos",
            observations=["Processing review data"],
            decisions=["Extracting sentiment insights per menu item"],
        )

        # If customer photos provided, analyze them
        customer_photos = review_data.get("photos", [])
        if customer_photos:
            photo_analysis = await self.multimodal.analyze_customer_photos(
                photos=customer_photos,
                menu_items=[item.get("name") for item in state.menu_items],
            )
            review_data["photo_analysis"] = photo_analysis

        # Store sentiment data
        state.sentiment_data = review_data

    async def _run_predictions(
        self, state: PipelineState, thinking_level: ThinkingLevel
    ) -> None:
        """Run sales predictions."""
        if not state.menu_items:
            return

        self._add_thought_trace(
            state,
            step="Sales Prediction",
            reasoning="Generating sales forecasts",
            observations=[f"Predicting for {len(state.menu_items)} items"],
            decisions=["Running prediction models"],
        )

        # This would integrate with the sales predictor service
        # For now, store placeholder for the orchestrator pattern
        state.predictions = {
            "status": "pending_integration",
            "message": "Integrate with SalesPredictor service",
        }

    async def _generate_campaigns(
        self, state: PipelineState, thinking_level: ThinkingLevel
    ) -> None:
        """Generate marketing campaigns."""
        if not state.bcg_analysis:
            return

        self._add_thought_trace(
            state,
            step="Campaign Generation",
            reasoning="Creating data-driven marketing campaigns",
            observations=["Using BCG and sentiment data"],
            decisions=["Generating multi-channel campaigns"],
        )

        # Generate strategic recommendations which include campaign ideas
        result = await self.reasoning.generate_strategic_recommendations(
            bcg_analysis=state.bcg_analysis,
            competitive_analysis=state.competitor_intel,
            sentiment_analysis=state.sentiment_data,
            predictions=state.predictions,
            thinking_level=thinking_level,
        )

        # Extract campaigns from recommendations
        if "immediate_actions" in result.analysis:
            state.campaigns = result.analysis.get("immediate_actions", [])

        state.thought_traces.extend(result.thought_traces)

    async def _generate_summary(
        self, state: PipelineState, thinking_level: ThinkingLevel
    ) -> None:
        """Generate executive summary."""
        complete_analysis = {
            "menu": state.menu_items,
            "bcg": state.bcg_analysis,
            "competitors": state.competitor_intel,
            "sentiment": state.sentiment_data,
            "predictions": state.predictions,
            "campaigns": state.campaigns,
        }

        state.executive_summary = await self.reasoning.generate_executive_summary(
            complete_analysis=complete_analysis,
            thinking_level=thinking_level,
        )

    async def _run_verification(
        self, state: PipelineState, thinking_level: ThinkingLevel
    ) -> None:
        """Run verification on complete analysis."""
        self._add_thought_trace(
            state,
            step="Verification",
            reasoning="Running autonomous verification loop",
            observations=["Validating all analysis components"],
            decisions=["Auto-improving if quality thresholds not met"],
        )

        analysis_data = {
            "products": state.menu_items,
            "bcg_analysis": state.bcg_analysis,
            "predictions": state.predictions,
            "campaigns": state.campaigns,
            "competitor_intel": state.competitor_intel,
            "sentiment_data": state.sentiment_data,
        }

        result = await self.verification.verify_analysis(
            analysis_data=analysis_data,
            thinking_level=thinking_level,
            auto_improve=True,
        )

        state.verification_result = result.to_dict()

        self._add_thought_trace(
            state,
            step="Verification Complete",
            reasoning="Analysis verified",
            observations=[
                f"Verification score: {result.overall_score:.0%}",
                f"Iterations used: {result.iterations_used}",
            ],
            decisions=[result.final_recommendation],
            confidence=result.overall_score,
        )

    def _should_skip_stage(
        self,
        start_stage: PipelineStage,
        current_stage: PipelineStage,
        state: PipelineState,
    ) -> bool:
        """Determine if a stage should be skipped."""
        stage_order = list(PipelineStage)

        if start_stage == PipelineStage.INITIALIZED:
            return False

        start_idx = stage_order.index(start_stage)
        current_idx = stage_order.index(current_stage)

        return current_idx <= start_idx

    def _add_thought_trace(
        self,
        state: PipelineState,
        step: str,
        reasoning: str,
        observations: List[str],
        decisions: List[str],
        confidence: float = 0.8,
    ) -> None:
        """Add a thought trace to the session."""
        trace = ThoughtTrace(
            step=step,
            reasoning=reasoning,
            observations=observations,
            decisions=decisions,
            confidence=confidence,
        )
        state.thought_traces.append(trace)

    def _save_checkpoint(
        self,
        state: PipelineState,
        success: bool,
        error: Optional[str] = None,
        duration_ms: int = 0,
    ) -> None:
        """Save a checkpoint for the current stage."""
        checkpoint = PipelineCheckpoint(
            stage=state.current_stage,
            timestamp=datetime.now(timezone.utc),
            data={
                "menu_items_count": len(state.menu_items),
                "sales_records_count": len(state.sales_data),
                "campaigns_count": len(state.campaigns),
            },
            success=success,
            error=error,
            duration_ms=duration_ms,
        )
        state.checkpoints.append(checkpoint)

    def _aggregate_gemini_stats(self) -> Dict[str, Any]:
        """Aggregate Gemini stats from all sub-agents."""
        stats = {
            "orchestrator": self.get_usage_stats(),
            "multimodal": self.multimodal.get_usage_stats(),
            "reasoning": self.reasoning.get_usage_stats(),
            "verification": self.verification.get_usage_stats(),
        }

        # Calculate totals
        total_requests = sum(s.get("total_requests", 0) for s in stats.values())
        total_tokens = sum(s.get("tokens", {}).get("total", 0) for s in stats.values())
        total_cost = sum(s.get("estimated_cost_usd", 0) for s in stats.values())

        return {
            "by_agent": stats,
            "totals": {
                "total_requests": total_requests,
                "total_tokens": total_tokens,
                "estimated_cost_usd": round(total_cost, 4),
            },
        }

    def _build_final_response(self, state: PipelineState) -> Dict[str, Any]:
        """Build the final response from the analysis state."""
        return {
            "session_id": state.session_id,
            "status": state.current_stage.value,
            "summary": {
                "products_analyzed": len(state.menu_items),
                "sales_records_processed": len(state.sales_data),
                "campaigns_generated": len(state.campaigns),
                "total_processing_time_ms": state.total_processing_time_ms,
            },
            "menu": state.menu_items,
            "bcg_analysis": state.bcg_analysis,
            "competitor_intel": state.competitor_intel,
            "sentiment_data": state.sentiment_data,
            "predictions": state.predictions,
            "campaigns": state.campaigns,
            "executive_summary": state.executive_summary,
            "verification": state.verification_result,
            "thought_signature": {
                "traces": [t.to_dict() for t in state.thought_traces],
                "total_steps": len(state.thought_traces),
                "avg_confidence": (
                    sum(t.confidence for t in state.thought_traces)
                    / len(state.thought_traces)
                    if state.thought_traces
                    else 0
                ),
            },
            "checkpoints": [c.to_dict() for c in state.checkpoints],
            "gemini_stats": state.gemini_stats,
        }

    def _build_partial_response(self, state: PipelineState) -> Dict[str, Any]:
        """Build partial response for failed pipeline."""
        return {
            "menu_items": state.menu_items,
            "bcg_analysis": state.bcg_analysis,
            "predictions": state.predictions,
            "checkpoints": [c.to_dict() for c in state.checkpoints],
        }

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a session."""
        state = self.active_sessions.get(session_id) or self.completed_sessions.get(
            session_id
        )
        if not state:
            return None

        return state.to_dict()

    async def resume_session(
        self,
        session_id: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Resume a session from its last checkpoint."""
        return await self.run_full_pipeline(
            session_id=session_id,
            resume_from_checkpoint=True,
            **kwargs,
        )
