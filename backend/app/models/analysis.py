"""
Analysis, campaign, and sentiment models.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


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
    strengths: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

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
    schedule: Mapped[Optional[Dict[str, List[str]]]] = mapped_column(
        JSON, nullable=True
    )  # Hourly schedule

    # Content
    channels: Mapped[List[str]] = mapped_column(JSON)  # List of channels
    key_messages: Mapped[List[str]] = mapped_column(JSON)  # List of messages
    promotional_items: Mapped[List[str]] = mapped_column(JSON)  # Featured items
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


class SentimentSource(str, Enum):
    """Source of sentiment data."""

    GOOGLE_REVIEWS = "google_reviews"
    YELP = "yelp"
    TRIPADVISOR = "tripadvisor"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    CUSTOMER_PHOTOS = "customer_photos"
    MANUAL = "manual"


class SentimentCategory(str, Enum):
    """Sentiment classification."""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class PortionPerception(str, Enum):
    """Customer perception of portion size."""

    VERY_SMALL = "very_small"
    SMALL = "small"
    ADEQUATE = "adequate"
    GENEROUS = "generous"
    VERY_GENEROUS = "very_generous"


class SentimentAnalysisSession(Base):
    """
    Sentiment analysis session.

    Groups all sentiment data collected and analyzed for a restaurant session.
    """

    __tablename__ = "sentiment_analysis_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    restaurant_id: Mapped[str] = mapped_column(String(36), index=True)

    # Sources analyzed
    sources_used: Mapped[List[str]] = mapped_column(JSON)  # List of SentimentSource

    # Overall metrics
    overall_sentiment_score: Mapped[float] = mapped_column(
        Float, default=0.0
    )  # -1 to 1
    overall_nps: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # Net Promoter Score

    # Distribution
    sentiment_distribution: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)

    # Aggregate insights
    total_reviews_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    total_photos_analyzed: Mapped[int] = mapped_column(Integer, default=0)

    # Common themes
    common_praises: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    common_complaints: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Key themes
    service_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    food_quality_sentiment: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    ambiance_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI recommendations
    recommendations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Gemini stats
    gemini_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    item_sentiments = relationship("ItemSentiment", back_populates="session")
    reviews = relationship("ReviewAnalysis", back_populates="session")
    photo_analyses = relationship("CustomerPhotoAnalysis", back_populates="session")


class ItemSentiment(Base):
    """
    Per-item sentiment aggregation.

    Combines text and visual sentiment for each menu item.
    """

    __tablename__ = "item_sentiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sentiment_session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sentiment_analysis_sessions.id"), index=True
    )

    # Item identification
    item_name: Mapped[str] = mapped_column(String(200))
    menu_item_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Text sentiment (from reviews)
    text_sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)  # -1 to 1
    text_mention_count: Mapped[int] = mapped_column(Integer, default=0)
    common_descriptors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Visual sentiment (from photos)
    visual_appeal_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # 0 to 10
    presentation_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    portion_perception: Mapped[Optional[str]] = mapped_column(
        SQLEnum(PortionPerception), nullable=True
    )
    portion_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    photo_count: Mapped[int] = mapped_column(Integer, default=0)

    # Combined analysis
    overall_sentiment: Mapped[str] = mapped_column(
        SQLEnum(SentimentCategory), default=SentimentCategory.NEUTRAL
    )
    sentiment_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Cross-reference with BCG
    bcg_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # AI insight
    actionable_insight: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("SentimentAnalysisSession", back_populates="item_sentiments")


class ReviewAnalysis(Base):
    """
    Individual review analysis.

    Stores analyzed review data from various sources.
    """

    __tablename__ = "review_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sentiment_session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sentiment_analysis_sessions.id"), index=True
    )

    # Source info
    source: Mapped[str] = mapped_column(SQLEnum(SentimentSource))
    source_review_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Review content
    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reviewer_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Original ratings
    original_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI analysis
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    sentiment_category: Mapped[str] = mapped_column(
        SQLEnum(SentimentCategory), default=SentimentCategory.NEUTRAL
    )

    # Extracted entities
    items_mentioned: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    themes_detected: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Competitor mentions
    competitor_mentions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Key phrases
    positive_phrases: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    negative_phrases: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Analysis metadata
    language: Mapped[str] = mapped_column(String(10), default="es")
    analysis_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("SentimentAnalysisSession", back_populates="reviews")


class CustomerPhotoAnalysis(Base):
    """
    Customer photo analysis results.

    Stores visual analysis of photos posted by customers.
    """

    __tablename__ = "customer_photo_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sentiment_session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sentiment_analysis_sessions.id"), index=True
    )

    # Source info
    source: Mapped[str] = mapped_column(SQLEnum(SentimentSource))
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    photo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Dish identification
    dish_identified: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    matched_menu_item: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    match_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Visual scores
    presentation_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-10
    portion_perception: Mapped[Optional[str]] = mapped_column(
        SQLEnum(PortionPerception), nullable=True
    )
    portion_score: Mapped[float] = mapped_column(Float, default=0.0)
    visual_appeal: Mapped[float] = mapped_column(Float, default=0.0)

    # Photo quality
    photo_quality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lighting_quality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Issues detected
    issues_noted: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    positive_aspects: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Sentiment
    sentiment_indicators: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Analysis metadata
    analysis_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("SentimentAnalysisSession", back_populates="photo_analyses")
