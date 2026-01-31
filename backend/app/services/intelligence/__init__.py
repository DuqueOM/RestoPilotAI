"""
Intelligence Services Package.

Contains advanced AI agents for autonomous intelligence gathering:
- ScoutAgent: Autonomous competitor discovery and analysis
- VisualGapAnalyzer: Visual comparison using Gemini Vision
- NeighborhoodAnalyzer: Location-based demographic analysis
"""

from app.services.intelligence.competitor_finder import (
    CompetitorProfile,
    ScoutAgent,
    ScoutThought,
)
from app.services.intelligence.neighborhood import (
    DemographicInsight,
    NeighborhoodAnalyzer,
    NeighborhoodProfile,
)
from app.services.intelligence.social_aesthetics import (
    VisualGapAnalyzer,
    VisualGapReport,
    VisualScore,
)

__all__ = [
    "ScoutAgent",
    "CompetitorProfile",
    "ScoutThought",
    "VisualGapAnalyzer",
    "VisualGapReport",
    "VisualScore",
    "NeighborhoodAnalyzer",
    "NeighborhoodProfile",
    "DemographicInsight",
]
