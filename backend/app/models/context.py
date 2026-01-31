"""
Thought Trace Models.

Stores AI reasoning traces for transparency and debugging.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class ThinkingLevel(str, Enum):
    """Depth of AI reasoning."""

    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"
    EXHAUSTIVE = "exhaustive"


class TraceStage(str, Enum):
    """Pipeline stage for the trace."""

    MENU_EXTRACTION = "menu_extraction"
    DISH_ANALYSIS = "dish_analysis"
    BCG_CLASSIFICATION = "bcg_classification"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SALES_PREDICTION = "sales_prediction"
    CAMPAIGN_GENERATION = "campaign_generation"
    VERIFICATION = "verification"
    EXECUTIVE_SUMMARY = "executive_summary"


class ThoughtTraceSession(Base):
    """
    Thought trace session.

    Groups all thought traces for an analysis session.
    """

    __tablename__ = "thought_trace_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True, unique=True)

    # Session metadata
    thinking_level: Mapped[str] = mapped_column(
        SQLEnum(ThinkingLevel), default=ThinkingLevel.STANDARD
    )

    # Aggregate metrics
    total_traces: Mapped[int] = mapped_column(Integer, default=0)
    average_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    total_thinking_time_ms: Mapped[int] = mapped_column(Integer, default=0)

    # Stage summary
    stages_completed: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Gemini usage
    total_gemini_calls: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    traces = relationship("ThoughtTrace", back_populates="session")


class ThoughtTrace(Base):
    """
    Individual thought trace.

    Records a single reasoning step in the AI's decision-making process.
    """

    __tablename__ = "thought_traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trace_session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("thought_trace_sessions.id"), index=True
    )

    # Step identification
    step_number: Mapped[int] = mapped_column(Integer)
    step_name: Mapped[str] = mapped_column(String(200))
    stage: Mapped[str] = mapped_column(SQLEnum(TraceStage))

    # Reasoning content
    reasoning: Mapped[str] = mapped_column(Text)
    observations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    decisions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    assumptions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Quality metrics
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Performance
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    # Input/Output summary
    input_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Error tracking
    had_error: Mapped[bool] = mapped_column(default=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ThoughtTraceSession", back_populates="traces")


class VerificationTrace(Base):
    """
    Verification step trace.

    Records the self-verification process for quality assurance.
    """

    __tablename__ = "verification_traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)

    # Verification round
    iteration: Mapped[int] = mapped_column(Integer, default=1)

    # Check results
    check_name: Mapped[str] = mapped_column(String(100))
    passed: Mapped[bool] = mapped_column(default=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)

    # Feedback
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggestions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Severity
    severity: Mapped[str] = mapped_column(String(20), default="info")

    # Improvement made
    improvement_applied: Mapped[bool] = mapped_column(default=False)
    improvement_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metrics
    score_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GeminiCallLog(Base):
    """
    Gemini API call log.

    Detailed log of all Gemini API calls for monitoring and cost tracking.
    """

    __tablename__ = "gemini_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)

    # Call identification
    request_id: Mapped[str] = mapped_column(String(36))
    agent_name: Mapped[str] = mapped_column(String(50))
    feature: Mapped[str] = mapped_column(String(50))

    # Model info
    model_name: Mapped[str] = mapped_column(String(50))

    # Token usage
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cached_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Performance
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    # Cost
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # Status
    success: Mapped[bool] = mapped_column(default=True)
    error_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Retry info
    was_retry: Mapped[bool] = mapped_column(default=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Cache info
    cache_hit: Mapped[bool] = mapped_column(default=False)

    # Timestamps
    called_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BusinessContext(Base):
    """
    Stores text and audio context provided by user.
    """
    __tablename__ = "business_contexts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    
    # Text contexts
    history_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    values_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unique_selling_points_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_audience_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    challenges_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    goals_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Audio transcriptions (Gemini multimodal)
    history_audio_transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    values_audio_transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Processed insights (by Gemini)
    processed_insights: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
