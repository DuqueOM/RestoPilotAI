"""
Video Analysis Endpoints - Gemini 3 Exclusive Feature.

Provides video content analysis capabilities that ONLY Gemini 3 has.
OpenAI and Claude cannot process video natively.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from loguru import logger

from app.services.gemini.advanced_multimodal import (
    AdvancedMultimodalAgent,
    VideoAnalysisSchema
)


router = APIRouter(prefix="/video", tags=["video"])


# ==================== Endpoints ====================

@router.post("/analyze")
async def analyze_video(
    video: UploadFile = File(...),
    purpose: str = Form("social_media"),
    max_duration: Optional[int] = Form(None)
):
    """
    🎥 Analyze restaurant video content.
    
    **UNIQUE TO GEMINI 3**: Native video processing.
    OpenAI and Claude cannot do this.
    
    Analyzes:
    - Content type (cooking, tour, testimonial, etc.)
    - Key moments with timestamps
    - Visual and audio quality
    - Platform suitability (Instagram, TikTok, YouTube, etc.)
    - Recommended edits and cuts
    - Best thumbnail moment
    
    Args:
        video: Video file (mp4, mov, avi, etc.)
        purpose: Purpose of video (social_media, marketing, training, etc.)
        max_duration: Maximum duration in seconds (optional)
    
    Returns:
        Comprehensive video analysis with recommendations
    """
    
    try:
        # Validate file type
        if not video.content_type or not video.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {video.content_type}. Must be a video file."
            )
        
        # Read video bytes
        video_bytes = await video.read()
        
        # Check file size (limit to 100MB for now)
        max_size = 100 * 1024 * 1024  # 100MB
        if len(video_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Video file too large. Maximum size: {max_size / (1024*1024):.0f}MB"
            )
        
        logger.info(
            "video_analysis_started",
            filename=video.filename,
            size_mb=len(video_bytes) / (1024 * 1024),
            purpose=purpose
        )
        
        # Initialize multimodal agent
        agent = AdvancedMultimodalAgent()
        
        # Analyze video
        analysis = await agent.analyse_video_content(
            video_bytes=video_bytes,
            video_purpose=purpose
        )
        
        logger.info(
            "video_analysis_complete",
            filename=video.filename,
            content_type=analysis.content_type,
            key_moments=len(analysis.key_moments),
            visual_quality=analysis.visual_quality_score
        )
        
        # Format response
        response = {
            "filename": video.filename,
            "content_type": analysis.content_type,
            "key_moments": [
                {
                    "timestamp": moment.get("timestamp", ""),
                    "description": moment.get("description", ""),
                    "type": moment.get("type", ""),
                    "engagement_potential": moment.get("engagement_potential", "medium")
                }
                for moment in analysis.key_moments
            ],
            "quality_scores": {
                "visual": analysis.visual_quality_score,
                "audio": analysis.audio_quality_score,
                "overall": (
                    analysis.visual_quality_score + 
                    (analysis.audio_quality_score or analysis.visual_quality_score)
                ) / 2
            },
            "platform_suitability": analysis.social_media_suitability,
            "best_thumbnail_timestamp": analysis.best_thumbnail_timestamp,
            "recommended_cuts": analysis.recommended_cuts,
            "recommendations": {
                "optimal_length": _get_optimal_length(analysis.social_media_suitability),
                "best_platforms": _get_best_platforms(analysis.social_media_suitability),
                "improvements": analysis.recommended_cuts[:3]  # Top 3 improvements
            }
        }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("video_analysis_error", error=str(e), filename=video.filename)
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")


@router.post("/quick-check")
async def quick_video_check(
    video: UploadFile = File(...)
):
    """
    🎬 Quick video quality check.
    
    Fast analysis for basic quality metrics without deep analysis.
    """
    
    try:
        if not video.content_type or not video.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Must be a video file."
            )
        
        video_bytes = await video.read()
        
        # Quick check with basic analysis
        agent = AdvancedMultimodalAgent()
        
        # Use a simpler prompt for quick check
        from app.services.gemini.enhanced_agent import ThinkingLevel
        
        result = await agent.generate(
            prompt="""Quickly assess this video:
            1. Duration estimate
            2. Visual quality (1-10)
            3. Audio quality (1-10)
            4. Content type
            5. One-sentence recommendation
            
            Return as JSON.""",
            images=[video_bytes],
            thinking_level=ThinkingLevel.QUICK
        )
        
        return JSONResponse(content={
            "filename": video.filename,
            "quick_assessment": result["data"],
            "note": "For detailed analysis, use /video/analyze endpoint"
        })
        
    except Exception as e:
        logger.error("quick_video_check_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def video_health():
    """Health check for video analysis endpoints."""
    return {
        "status": "healthy",
        "video_analysis_enabled": True,
        "features": [
            "native_video_processing",
            "key_moments_detection",
            "platform_suitability",
            "quality_assessment",
            "thumbnail_recommendation"
        ],
        "unique_to_gemini": True,
        "competitors_cannot_do_this": ["OpenAI GPT-4V", "Claude 3"]
    }


# ==================== Helper Functions ====================

def _get_optimal_length(suitability: dict) -> dict:
    """Determine optimal video length based on platform suitability."""
    
    optimal_lengths = {
        "instagram_reels": "15-60 seconds",
        "tiktok": "15-60 seconds",
        "youtube_shorts": "30-60 seconds",
        "facebook": "1-3 minutes",
        "linkedin": "30-90 seconds",
        "youtube": "3-10 minutes"
    }
    
    # Find best platform
    best_platform = max(suitability.items(), key=lambda x: x[1])[0] if suitability else "instagram_reels"
    
    return {
        "recommended": optimal_lengths.get(best_platform, "30-60 seconds"),
        "based_on": best_platform
    }


def _get_best_platforms(suitability: dict) -> list:
    """Get top 3 best platforms for this video."""
    
    if not suitability:
        return []
    
    # Sort by score
    sorted_platforms = sorted(
        suitability.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Return top 3 with scores > 7.0
    return [
        {
            "platform": platform,
            "score": score,
            "recommendation": "excellent" if score >= 9 else "good" if score >= 7 else "fair"
        }
        for platform, score in sorted_platforms[:3]
        if score >= 6.0
    ]
