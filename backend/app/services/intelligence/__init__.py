"""
Intelligence Services Package.

Contains advanced AI agents for autonomous intelligence gathering:
- ScoutAgent: Autonomous competitor discovery and analysis
- SocialAestheticsAnalyzer: Visual comparison using Gemini Vision
- NeighborhoodAnalyzer: Location-based demographic analysis
"""

from app.services.intelligence.data_enrichment import (
    CompetitorEnrichmentService,
    CompetitorProfile,  # Re-exporting if needed, though usually distinct from finder's
)
from app.services.intelligence.competitor_finder import (
    CompetitorProfile as FinderCompetitorProfile, # Avoid conflict if names match
    ScoutAgent,
    ScoutThought,
)
from app.services.intelligence.neighborhood import (
    NeighborhoodAnalyzer,
)
from app.services.intelligence.social_aesthetics import (
    SocialAestheticsAnalyzer,
)

__all__ = [
    "ScoutAgent",
    "FinderCompetitorProfile",
    "ScoutThought",
    "SocialAestheticsAnalyzer",
    "NeighborhoodAnalyzer",
    "CompetitorEnrichmentService",
    "CompetitorProfile",
]
