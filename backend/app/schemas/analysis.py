"""
Analysis and campaign Pydantic schemas.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BCGClass(str, Enum):
    """BCG Matrix classifications."""

    STAR = "star"
    CASH_COW = "cash_cow"
    QUESTION_MARK = "question_mark"
    DOG = "dog"


class ThoughtSignature(BaseModel):
    """
    Thought Signature for transparent AI reasoning.
    This provides verifiable traces of the agent's decision-making process.
    """

    plan: List[str]  # Steps the agent plans to take
    observations: List[str]  # Key observations from data
    reasoning: str  # Main reasoning chain
    assumptions: List[str]  # Assumptions made
    confidence: float = Field(..., ge=0, le=1)
    verification_checks: List[Dict[str, Any]]  # Self-verification results
    corrections_made: List[str] = []  # Any corrections during processing


class ProductProfileResponse(BaseModel):
    """Product profile with BCG classification."""

    id: int
    item_name: str
    bcg_class: BCGClass
    bcg_label: str  # Human-readable label

    # Metrics
    market_share: float = Field(..., ge=0, le=1)
    growth_rate: float
    avg_margin: Optional[float]
    popularity_score: float = Field(..., ge=0, le=1)
    image_attractiveness: Optional[float]
    overall_score: float

    # Insights
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

    # Visual position for BCG chart
    bcg_x: float  # Market share axis
    bcg_y: float  # Growth rate axis


class BCGAnalysisResponse(BaseModel):
    """Complete BCG analysis response."""

    session_id: str
    analysis_timestamp: datetime

    # Summary
    total_items_analyzed: int
    star_count: int
    cash_cow_count: int
    question_mark_count: int
    dog_count: int

    # Profiles
    profiles: List[ProductProfileResponse]

    # Strategic insights
    portfolio_health_score: float = Field(..., ge=0, le=1)
    strategic_recommendations: List[str]
    rebalancing_suggestions: List[str]

    # Thought signature
    thought_signature: ThoughtSignature


class ScenarioConfig(BaseModel):
    """Configuration for a prediction scenario."""

    name: str
    price_change_percent: float = 0.0
    promotion_active: bool = False
    promotion_discount: float = 0.0
    marketing_boost: float = 1.0  # Multiplier


class PredictionRequest(BaseModel):
    """Request for sales prediction."""

    session_id: str
    horizon_days: int = Field(14, ge=1, le=90)
    target_items: Optional[List[str]] = None  # None = all items
    scenarios: List[ScenarioConfig] = [ScenarioConfig(name="baseline")]


class ItemPrediction(BaseModel):
    """Prediction for a single item."""

    item_name: str
    baseline_prediction: List[float]  # Daily predictions
    scenario_predictions: Dict[str, List[float]]
    predicted_total_units: int
    predicted_revenue: float
    confidence_interval: Dict[str, float]  # {"lower": x, "upper": y}


class PredictionResponse(BaseModel):
    """Sales prediction response."""

    session_id: str
    prediction_generated_at: datetime
    horizon_days: int

    # Predictions
    item_predictions: List[ItemPrediction]

    # Aggregates
    total_predicted_units: Dict[str, int]  # By scenario
    total_predicted_revenue: Dict[str, float]

    # Model info
    model_type: str
    model_accuracy_mae: float
    features_used: List[str]

    # Thought signature
    thought_signature: ThoughtSignature


class CampaignGenerationRequest(BaseModel):
    """Request for campaign generation."""

    session_id: str
    num_campaigns: int = Field(3, ge=1, le=5)
    campaign_duration_days: int = Field(14, ge=7, le=30)
    focus_items: Optional[List[str]] = None
    budget_constraint: Optional[float] = None
    channels: List[str] = ["social_media", "in_store", "email"]
    objectives: List[str] = ["increase_sales", "reduce_waste", "attract_new_customers"]


class CampaignResponse(BaseModel):
    """Generated campaign proposal."""

    id: int
    title: str
    objective: str
    target_audience: str

    # Timing
    start_date: date
    end_date: date
    schedule: Dict[str, List[str]]  # {"Monday": ["12:00", "18:00"], ...}

    # Content
    channels: List[str]
    key_messages: List[str]
    promotional_items: List[str]
    discount_strategy: Optional[str]

    # Generated assets
    social_post_copy: str
    image_prompt: str
    generated_image_url: Optional[str]

    # Predictions
    expected_uplift_percent: float
    expected_revenue_increase: Optional[float]
    confidence_level: float

    # Rationale
    rationale: str
    why_these_items: str
    why_this_timing: str


class FullAnalysisResponse(BaseModel):
    """Complete analysis response with all components."""

    session_id: str
    session_name: Optional[str]
    status: str

    # Timestamps
    started_at: datetime
    completed_at: Optional[datetime]
    processing_time_ms: Optional[int]

    # Input summary
    input_summary: Dict[
        str, int
    ]  # {"menu_images": 1, "dish_images": 5, "sales_records": 1000}

    # Results
    menu_extraction: Optional[MenuExtractionResponse] = None
    bcg_analysis: Optional[BCGAnalysisResponse] = None
    predictions: Optional[PredictionResponse] = None
    campaigns: List[CampaignResponse] = []

    # Master thought signature
    thought_signature: ThoughtSignature

    # Gemini API usage
    gemini_calls: int
    tokens_used: Optional[int]


# Import for type hint
