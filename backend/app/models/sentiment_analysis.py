"""
Sentiment Analysis Models.

Stores customer sentiment data from reviews and customer photos.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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
    sources_used: Mapped[str] = mapped_column(JSON)  # List of SentimentSource
    
    # Overall metrics
    overall_sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)  # -1 to 1
    overall_nps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Net Promoter Score
    
    # Distribution
    sentiment_distribution: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Aggregate insights
    total_reviews_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    total_photos_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Common themes
    common_praises: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    common_complaints: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Key themes
    service_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    food_quality_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ambiance_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # AI recommendations
    recommendations: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
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
    common_descriptors: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Visual sentiment (from photos)
    visual_appeal_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0 to 10
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
    items_mentioned: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    themes_detected: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Competitor mentions
    competitor_mentions: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Key phrases
    positive_phrases: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    negative_phrases: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
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
    issues_noted: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    positive_aspects: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Sentiment
    sentiment_indicators: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Analysis metadata
    analysis_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("SentimentAnalysisSession", back_populates="photo_analyses")
