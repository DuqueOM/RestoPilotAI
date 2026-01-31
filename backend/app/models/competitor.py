"""
Competitor Intelligence Models.

Stores competitor data, menu extractions, and competitive analysis results.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, List

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class CompetitorSourceType(str, Enum):
    """Type of competitor data source."""

    URL = "url"
    IMAGE = "image"
    INSTAGRAM = "instagram"
    MANUAL = "manual"
    GOOGLE_MAPS = "google_maps"
    YELP = "yelp"


class PricePositioning(str, Enum):
    """Competitor price positioning category."""

    BUDGET = "budget"
    MID_RANGE = "mid_range"
    PREMIUM = "premium"
    LUXURY = "luxury"


class Competitor(Base):
    """
    Competitor restaurant profile.

    Stores basic information about a competitor restaurant
    for tracking and analysis.
    """

    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[str] = mapped_column(String(36), index=True)

    # Basic info
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_meters: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Online presence
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    instagram_handle: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    google_place_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    place_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, unique=True) # Alias/User Request
    yelp_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Classification
    cuisine_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    price_positioning: Mapped[Optional[str]] = mapped_column(
        SQLEnum(PricePositioning), nullable=True
    )
    price_range: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    avg_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Ratings
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    google_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    yelp_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Extended Data (Multimodal)
    google_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    instagram_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    photos: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)  # List of photo URLs/Analysis
    menu_items: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True) # Cached/Summary items
    social_aesthetic_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    data_quality: Mapped[Optional[float]] = mapped_column(Float, default=0.0)

    # Metadata
    is_active: Mapped[bool] = mapped_column(default=True)
    last_scraped: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    menu_extractions = relationship(
        "CompetitorMenuExtraction", back_populates="competitor"
    )


class CompetitorMenuExtraction(Base):
    """
    Extracted menu data from a competitor.

    Stores the result of menu extraction from competitor sources.
    """

    __tablename__ = "competitor_menu_extractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competitor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitors.id"), index=True
    )
    session_id: Mapped[str] = mapped_column(String(36), index=True)

    # Source info
    source_type: Mapped[str] = mapped_column(SQLEnum(CompetitorSourceType))
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Extracted data
    items: Mapped[List[Dict[str, Any]]] = mapped_column(JSON)  # List of menu items
    categories: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Pricing analysis
    price_range_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_range_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="MXN")

    # Quality metrics
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    items_count: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    extracted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="menu_extractions")


class CompetitorAnalysis(Base):
    """
    Competitive analysis results.

    Stores the AI-generated competitive insights comparing
    our restaurant with competitors.
    """

    __tablename__ = "competitor_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)

    # Analysis scope
    our_restaurant_id: Mapped[str] = mapped_column(String(36), index=True)
    competitor_ids: Mapped[List[int]] = mapped_column(JSON)  # List of competitor IDs analyzed

    # Competitive landscape
    market_position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    competitive_intensity: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    # Price analysis
    price_positioning_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    price_gaps: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Product analysis
    our_unique_items: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    competitor_unique_items: Mapped[Optional[Dict[str, List[str]]]] = mapped_column(JSON, nullable=True)
    category_gaps: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Strategic insights
    key_differentiators: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    competitive_threats: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    opportunities: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Recommendations
    strategic_recommendations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON, nullable=True
    )
    pricing_recommendations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Market positioning matrix
    positioning_matrix: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # AI metadata
    thinking_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    gemini_tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    # Thought trace
    thought_trace: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Timestamps
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PriceComparison(Base):
    """
    Item-level price comparison with competitors.

    Stores granular price comparisons for individual menu items
    against competitor offerings.
    """

    __tablename__ = "price_comparisons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitor_analyses.id"), index=True
    )

    # Our item
    our_item_name: Mapped[str] = mapped_column(String(200))
    our_price: Mapped[float] = mapped_column(Float)
    our_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Competitor comparison
    competitor_id: Mapped[int] = mapped_column(Integer, ForeignKey("competitors.id"))
    competitor_item_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    competitor_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Analysis
    price_difference: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_difference_percent: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    match_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Recommendation
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
