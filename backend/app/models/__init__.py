"""
SQLAlchemy ORM models for RestoPilotAI.

Includes:
- Menu and product models
- Sales and analysis models
- Competitor intelligence models
- Sentiment analysis models
- Thought trace models for AI transparency
"""

from app.models.analysis import (
    AnalysisSession,
    BCGClassification,
    Campaign,
    CustomerPhotoAnalysis,
    ItemSentiment,
    PortionPerception,
    ProductProfile,
    ReviewAnalysis,
    SentimentAnalysisSession,
    SentimentCategory,
    SentimentSource,
)
from app.models.business import MenuCategory, MenuItem, SalesRecord

# Competitor Intelligence models
from app.models.competitor import (
    Competitor,
    CompetitorAnalysis,
    CompetitorMenuExtraction,
    CompetitorSourceType,
    PriceComparison,
    PricePositioning,
)

# Thought Trace models
from app.models.context import (
    BusinessContext,
    GeminiCallLog,
    ThinkingLevel,
    ThoughtTrace,
    ThoughtTraceSession,
    TraceStage,
    VerificationTrace,
)

__all__ = [
    # Menu models
    "MenuItem",
    "MenuCategory",
    "BusinessContext",
    # Sales models
    "SalesRecord",
    # Analysis models
    "ProductProfile",
    "Campaign",
    "AnalysisSession",
    "BCGClassification",
    # Competitor models
    "Competitor",
    "CompetitorMenuExtraction",
    "CompetitorAnalysis",
    "PriceComparison",
    "CompetitorSourceType",
    "PricePositioning",
    # Sentiment models
    "SentimentAnalysisSession",
    "ItemSentiment",
    "ReviewAnalysis",
    "CustomerPhotoAnalysis",
    "SentimentSource",
    "SentimentCategory",
    "PortionPerception",
    # Thought trace models
    "ThoughtTraceSession",
    "ThoughtTrace",
    "VerificationTrace",
    "GeminiCallLog",
    "ThinkingLevel",
    "TraceStage",
]
