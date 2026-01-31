"""
Business logic services for MenuPilot.

Includes core services and enhanced agentic capabilities:
- Verification Agent: Autonomous self-verification loop
- Neural Predictor: Deep learning sales forecasting
- Orchestrator: Marathon Agent pattern for pipeline coordination
- Competitor Intelligence: Competitive analysis and price comparison
- Sentiment Analyzer: Multi-modal customer sentiment analysis
"""

from app.services.analysis.bcg import BCGClassifier
from app.services.analysis.menu_analyzer import MenuExtractor
from app.services.analysis.neural_predictor import NeuralPredictor

# New WOW factor services
from app.services.analysis.pricing import (
    CompetitiveAnalysisResult,
    CompetitorIntelligenceService,
    CompetitorMenu,
    CompetitorSource,
    PriceGap,
)
from app.services.analysis.sales_predictor import SalesPredictor
from app.services.analysis.sentiment import (
    ItemSentimentResult,
    ReviewData,
    SentimentAnalysisResult,
    SentimentAnalyzer,
    SentimentCategory,
    SentimentSource,
)
from app.services.campaigns.generator import CampaignGenerator
from app.services.gemini.base_agent import GeminiAgent
from app.services.gemini.verification import ThinkingLevel, VerificationAgent
from app.services.intelligence.data_enrichment import (
    CompetitorEnrichmentService,
    CompetitorProfile,
)
from app.services.orchestrator import AnalysisOrchestrator

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
