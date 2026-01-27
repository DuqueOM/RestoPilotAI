"""
SQLAlchemy ORM models for MenuPilot.

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
    ProductProfile,
)

# Competitor Intelligence models
from app.models.competitor import (
    Competitor,
    CompetitorAnalysis,
    CompetitorMenuExtraction,
    CompetitorSourceType,
    PriceComparison,
    PricePositioning,
)
from app.models.menu import MenuCategory, MenuItem
from app.models.sales import SalesRecord

# Sentiment Analysis models
from app.models.sentiment_analysis import (
    CustomerPhotoAnalysis,
    ItemSentiment,
    PortionPerception,
    ReviewAnalysis,
    SentimentAnalysisSession,
    SentimentCategory,
    SentimentSource,
)

# Thought Trace models
from app.models.thought_trace import (
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
