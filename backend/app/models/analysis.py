"""
Analysis and campaign models.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Date, DateTime, Float, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BCGClassification(str, Enum):
    """BCG Matrix classification categories."""

    STAR = "star"  # High share, high growth - invest
    CASH_COW = "cash_cow"  # High share, low growth - milk
    QUESTION_MARK = "question_mark"  # Low share, high growth - analyze
    DOG = "dog"  # Low share, low growth - divest/reposition


class AnalysisSession(Base):
    """Analysis session tracking for reproducibility."""

    __tablename__ = "analysis_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Session info
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")

    # Input tracking
    menu_image_count: Mapped[int] = mapped_column(Integer, default=0)
    dish_image_count: Mapped[int] = mapped_column(Integer, default=0)
    sales_record_count: Mapped[int] = mapped_column(Integer, default=0)

    # Thought signature for transparency
    thought_signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Processing metadata
    gemini_calls: Mapped[int] = mapped_column(Integer, default=0)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ProductProfile(Base):
    """Analyzed product profile with BCG classification."""

    __tablename__ = "product_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    menu_item_id: Mapped[int] = mapped_column(Integer, index=True)
    item_name: Mapped[str] = mapped_column(String(200))

    # BCG Classification
    bcg_class: Mapped[str] = mapped_column(SQLEnum(BCGClassification))

    # Metrics
    market_share: Mapped[float] = mapped_column(Float)  # Relative to other items
    growth_rate: Mapped[float] = mapped_column(Float)  # Period-over-period
    avg_margin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    popularity_score: Mapped[float] = mapped_column(Float)  # 0-1 normalized
    image_attractiveness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Computed scores
    overall_score: Mapped[float] = mapped_column(Float)  # Composite score

    # AI-generated insights
    strengths: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Campaign(Base):
    """Generated marketing campaign proposal."""

    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)

    # Campaign basics
    title: Mapped[str] = mapped_column(String(200))
    objective: Mapped[str] = mapped_column(Text)
    target_audience: Mapped[str] = mapped_column(Text)

    # Timing
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    schedule: Mapped[Optional[str]] = mapped_column(
        JSON, nullable=True
    )  # Hourly schedule

    # Content
    channels: Mapped[str] = mapped_column(JSON)  # List of channels
    key_messages: Mapped[str] = mapped_column(JSON)  # List of messages
    promotional_items: Mapped[str] = mapped_column(JSON)  # Featured items
    discount_strategy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Generated assets
    social_post_copy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_image_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    # Predictions
    expected_uplift_percent: Mapped[float] = mapped_column(Float)
    expected_revenue_increase: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    confidence_level: Mapped[float] = mapped_column(Float)  # 0-1

    # Rationale (Thought Signature component)
    rationale: Mapped[str] = mapped_column(Text)
    verification_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
