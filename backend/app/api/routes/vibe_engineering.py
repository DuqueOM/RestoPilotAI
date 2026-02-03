"""
Vibe Engineering API Routes - Auto-verification and improvement endpoints.

Implements the Vibe Engineering track from Gemini 3 Hackathon.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from loguru import logger

from app.services.gemini.vibe_engineering import VibeEngineeringAgent

router = APIRouter(prefix="/vibe-engineering", tags=["Vibe Engineering"])


class VerifyAnalysisRequest(BaseModel):
    """Request model for analysis verification."""
    
    analysis_type: str = Field(..., description="Type of analysis (bcg, competitive, sentiment, etc.)")
    analysis_result: Dict[str, Any] = Field(..., description="Analysis result to verify")
    source_data: Dict[str, Any] = Field(..., description="Original source data used for analysis")
    auto_improve: bool = Field(default=True, description="Whether to auto-improve if quality is low")
    quality_threshold: float = Field(default=0.85, description="Minimum quality score (0-1)")
    max_iterations: int = Field(default=3, description="Maximum improvement iterations")


class VerifyAnalysisResponse(BaseModel):
    """Response model for analysis verification."""
    
    final_analysis: Dict[str, Any]
    verification_history: List[Dict[str, Any]]
    iterations_required: int
    quality_achieved: float
    auto_improved: bool
    improvement_iterations: List[Dict[str, Any]]
    total_duration_ms: float


class VerifyCampaignAssetsRequest(BaseModel):
    """Request model for campaign assets verification."""
    
    campaign_assets: List[Dict[str, Any]] = Field(..., description="List of campaign assets to verify")
    brand_guidelines: Dict[str, Any] = Field(..., description="Brand guidelines for verification")
    auto_improve: bool = Field(default=True, description="Whether to auto-improve assets")


@router.post("/verify-analysis", response_model=VerifyAnalysisResponse)
async def verify_analysis(request: VerifyAnalysisRequest):
    """
    Verify and improve analysis quality using Vibe Engineering.
    
    HACKATHON TRACK: Vibe Engineering
    
    This endpoint implements autonomous verification and improvement:
    1. Verifies analysis quality across 4 dimensions
    2. Identifies specific issues
    3. Auto-improves if quality < threshold
    4. Iterates until quality threshold is met or max iterations reached
    
    Example:
    ```json
    {
        "analysis_type": "bcg",
        "analysis_result": {...},
        "source_data": {...},
        "auto_improve": true,
        "quality_threshold": 0.85,
        "max_iterations": 3
    }
    ```
    """
    try:
        logger.info(f"Vibe Engineering verification requested for {request.analysis_type}")
        
        # Initialize Vibe Engineering Agent
        vibe_agent = VibeEngineeringAgent()
        
        # Override default settings if provided
        if request.quality_threshold:
            vibe_agent.quality_threshold = request.quality_threshold
        if request.max_iterations:
            vibe_agent.max_iterations = request.max_iterations
        
        # Run verification and improvement loop
        result = await vibe_agent.verify_and_improve_analysis(
            analysis_type=request.analysis_type,
            analysis_result=request.analysis_result,
            source_data=request.source_data,
            auto_improve=request.auto_improve
        )
        
        logger.info(
            f"Vibe Engineering completed: {result['iterations_required']} iterations, "
            f"quality: {result['quality_achieved']:.2f}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Vibe Engineering verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-campaign-assets")
async def verify_campaign_assets(request: VerifyCampaignAssetsRequest):
    """
    Verify quality of campaign visual assets using Gemini Vision.
    
    HACKATHON TRACK: Vibe Engineering + Creative Autopilot
    
    Verifies:
    - Text legibility
    - Brand adherence
    - Technical quality
    - Message effectiveness
    
    Example:
    ```json
    {
        "campaign_assets": [
            {
                "image_data": "base64_encoded_image",
                "type": "instagram_post",
                "caption": "..."
            }
        ],
        "brand_guidelines": {
            "colors": ["#FF5733", "#C70039"],
            "fonts": ["Montserrat", "Open Sans"],
            "style": "modern_casual"
        },
        "auto_improve": true
    }
    ```
    """
    try:
        logger.info(f"Verifying {len(request.campaign_assets)} campaign assets")
        
        vibe_agent = VibeEngineeringAgent()
        
        result = await vibe_agent.verify_campaign_assets(
            campaign_assets=request.campaign_assets,
            brand_guidelines=request.brand_guidelines,
            auto_improve=request.auto_improve
        )
        
        logger.info(
            f"Campaign assets verified: overall quality {result['overall_quality']:.2f}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Campaign assets verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for Vibe Engineering service."""
    return {
        "status": "healthy",
        "service": "vibe-engineering",
        "features": [
            "autonomous_verification",
            "iterative_improvement",
            "visual_asset_verification"
        ]
    }
