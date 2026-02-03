"""
Grounding API Endpoints - Competitive Intelligence with Source Citations.

Provides endpoints for grounded research using Gemini 3's unique
Google Search integration capability.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from loguru import logger

from app.services.gemini.grounded_intelligence import (
    GroundedIntelligenceService,
    CompetitorIntelligence,
    MarketTrend,
    GroundedResult
)


router = APIRouter(prefix="/grounding", tags=["grounding"])


# ==================== Request/Response Models ====================

class CompetitorResearchRequest(BaseModel):
    """Request for competitor research."""
    competitor_name: str
    location: str
    cuisine_type: Optional[str] = None


class MultiCompetitorRequest(BaseModel):
    """Request for multiple competitor research."""
    competitors: List[dict]  # [{"name": "...", "cuisine_type": "..."}]
    location: str


class MarketTrendsRequest(BaseModel):
    """Request for market trends research."""
    cuisine_type: str
    location: str
    time_period: str = "last 6 months"


class VerifyClaimRequest(BaseModel):
    """Request to verify a claim."""
    claim: str
    context: Optional[str] = None


class PricingBenchmarkRequest(BaseModel):
    """Request for pricing benchmarks."""
    cuisine_type: str
    location: str
    dish_category: Optional[str] = None


# ==================== Endpoints ====================

@router.post("/competitor/analyze", response_model=CompetitorIntelligence)
async def analyze_competitor(request: CompetitorResearchRequest):
    """
    🔍 Analyze competitor with Google Search grounding.
    
    Returns real-time competitive intelligence with automatic
    source citations from the web.
    
    **UNIQUE TO GEMINI 3**: Auto-citation of sources.
    """
    
    try:
        logger.info(
            "competitor_analysis_started",
            competitor=request.competitor_name,
            location=request.location
        )
        
        service = GroundedIntelligenceService()
        
        result = await service.analyze_competitor_with_grounding(
            competitor_name=request.competitor_name,
            location=request.location,
            cuisine_type=request.cuisine_type
        )
        
        logger.info(
            "competitor_analysis_complete",
            competitor=request.competitor_name,
            sources_found=len(result.sources),
            grounding_score=result.grounding_score
        )
        
        return result
        
    except Exception as e:
        logger.error("competitor_analysis_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitor/batch", response_model=List[CompetitorIntelligence])
async def analyze_multiple_competitors(request: MultiCompetitorRequest):
    """
    🔍 Analyze multiple competitors in batch.
    
    Efficiently researches multiple competitors with grounding.
    """
    
    try:
        service = GroundedIntelligenceService()
        
        results = await service.analyze_multiple_competitors(
            competitors=request.competitors,
            location=request.location
        )
        
        return results
        
    except Exception as e:
        logger.error("batch_competitor_analysis_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends/research", response_model=List[MarketTrend])
async def research_market_trends(request: MarketTrendsRequest):
    """
    📈 Research market trends with grounded sources.
    
    Finds trending dishes, ingredients, concepts with citations.
    """
    
    try:
        logger.info(
            "market_trends_research_started",
            cuisine=request.cuisine_type,
            location=request.location
        )
        
        service = GroundedIntelligenceService()
        
        trends = await service.research_market_trends(
            cuisine_type=request.cuisine_type,
            location=request.location,
            time_period=request.time_period
        )
        
        logger.info(
            "market_trends_research_complete",
            trends_found=len(trends)
        )
        
        return trends
        
    except Exception as e:
        logger.error("market_trends_research_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=GroundedResult)
async def verify_claim(request: VerifyClaimRequest):
    """
    ✅ Verify a claim using Google Search grounding.
    
    Fact-checks claims with web sources.
    """
    
    try:
        service = GroundedIntelligenceService()
        
        result = await service.verify_claim_with_grounding(
            claim=request.claim,
            context=request.context
        )
        
        return result
        
    except Exception as e:
        logger.error("claim_verification_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pricing/benchmarks", response_model=GroundedResult)
async def get_pricing_benchmarks(request: PricingBenchmarkRequest):
    """
    💰 Get pricing benchmarks from real competitors.
    
    Uses grounding to find actual current prices.
    """
    
    try:
        service = GroundedIntelligenceService()
        
        result = await service.find_pricing_benchmarks(
            cuisine_type=request.cuisine_type,
            location=request.location,
            dish_category=request.dish_category
        )
        
        return result
        
    except Exception as e:
        logger.error("pricing_benchmarks_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def grounding_health():
    """Health check for grounding endpoints."""
    return {
        "status": "healthy",
        "grounding_enabled": True,
        "features": [
            "competitor_analysis",
            "market_trends",
            "claim_verification",
            "pricing_benchmarks",
            "source_citations"
        ],
        "unique_to_gemini": True
    }
