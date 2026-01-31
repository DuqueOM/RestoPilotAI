"""
Intelligence Services Package.

Contains advanced AI agents for autonomous intelligence gathering:
- ScoutAgent: Autonomous competitor discovery and analysis
- VisualGapAnalyzer: Visual comparison using Gemini Vision
- NeighborhoodAnalyzer: Location-based demographic analysis
"""

from app.services.intelligence.neighborhood_analyzer import (
    DemographicInsight,
    NeighborhoodAnalyzer,
    NeighborhoodProfile,
)
from app.services.intelligence.scout_agent import (
    CompetitorProfile,
    ScoutAgent,
    ScoutThought,
)
from app.services.intelligence.visual_gap_analyzer import (
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
