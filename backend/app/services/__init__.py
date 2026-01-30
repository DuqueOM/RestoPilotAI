"""
Business logic services for MenuPilot.

Includes core services and enhanced agentic capabilities:
- Verification Agent: Autonomous self-verification loop
- Neural Predictor: Deep learning sales forecasting
- Orchestrator: Marathon Agent pattern for pipeline coordination
- Competitor Intelligence: Competitive analysis and price comparison
- Sentiment Analyzer: Multi-modal customer sentiment analysis
"""

from app.services.bcg_classifier import BCGClassifier
from app.services.campaign_generator import CampaignGenerator

from app.services.competitor_enrichment import (
    CompetitorEnrichmentService,
    CompetitorProfile,
)

# New WOW factor services
from app.services.competitor_intelligence import (
    CompetitiveAnalysisResult,
    CompetitorIntelligenceService,
    CompetitorMenu,
    CompetitorSource,
    PriceGap,
)
from app.services.gemini_agent import GeminiAgent
from app.services.menu_extractor import MenuExtractor
from app.services.neural_predictor import NeuralPredictor
from app.services.orchestrator import AnalysisOrchestrator
from app.services.sales_predictor import SalesPredictor
from app.services.sentiment_analyzer import (
    ItemSentimentResult,
    ReviewData,
    SentimentAnalysisResult,
    SentimentAnalyzer,
    SentimentCategory,
    SentimentSource,
)
from app.services.verification_agent import ThinkingLevel, VerificationAgent

__all__ = [
    # Core services
    "GeminiAgent",
    "MenuExtractor",
    "BCGClassifier",
    "SalesPredictor",
    "CampaignGenerator",
    "VerificationAgent",
    "ThinkingLevel",
    "NeuralPredictor",
    "AnalysisOrchestrator",
    # Competitor Enrichment
    "CompetitorEnrichmentService",
    "CompetitorProfile",
    # Competitor Intelligence
    "CompetitorIntelligenceService",
    "CompetitorSource",
    "CompetitorMenu",
    "CompetitiveAnalysisResult",
    "PriceGap",
    # Sentiment Analysis
    "SentimentAnalyzer",
    "SentimentAnalysisResult",
    "ItemSentimentResult",
    "ReviewData",
    "SentimentSource",
    "SentimentCategory",
]
