"""
Campaign Generation Endpoints - Imagen 3 Integration.

Provides end-to-end campaign generation with image creation.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from loguru import logger

from app.services.imagen.campaign_generator import (
    CampaignImageGenerator,
    CampaignPackage,
    ImagePrompt,
    CampaignCopy
)


router = APIRouter(prefix="/campaigns", tags=["campaigns"])


# ==================== Endpoints ====================

@router.post("/generate", response_model=CampaignPackage)
async def generate_campaign(
    dish_name: str = Form(...),
    campaign_brief: str = Form(...),
    dish_description: Optional[str] = Form(None),
    dish_image: Optional[UploadFile] = File(None),
    style: str = Form("professional_food_photography"),
    platform: str = Form("instagram")
):
    """
    🎨 Generate complete campaign package.
    
    **End-to-end campaign generation:**
    1. Gemini analyzes dish
    2. Gemini creates strategy
    3. Gemini optimizes Imagen prompt
    4. Imagen generates images
    5. Gemini writes copy
    
    **ADVANTAGE**: Imagen 3 is superior to DALL-E 3 for food photography.
    
    Args:
        dish_name: Name of the dish
        campaign_brief: Campaign goals and objectives
        dish_description: Optional description
        dish_image: Optional image of the dish
        style: Image style (professional_food_photography, rustic, modern, etc.)
        platform: Target platform (instagram, facebook, tiktok, etc.)
    
    Returns:
        Complete campaign package with images, copy, and strategy
    """
    
    try:
        logger.info(
            "campaign_generation_requested",
            dish=dish_name,
            platform=platform
        )
        
        # Read dish image if provided
        dish_image_bytes = None
        if dish_image:
            dish_image_bytes = await dish_image.read()
        
        # Initialize generator
        generator = CampaignImageGenerator()
        
        # Generate complete campaign
        campaign = await generator.generate_complete_campaign(
            dish_name=dish_name,
            campaign_brief=campaign_brief,
            dish_description=dish_description,
            dish_image=dish_image_bytes,
            style=style,
            platform=platform
        )
        
        logger.info(
            "campaign_generation_complete",
            campaign_id=campaign.campaign_id,
            images=len(campaign.generated_images)
        )
        
        return campaign
        
    except Exception as e:
        logger.error("campaign_generation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate-images")
async def regenerate_images(
    campaign_id: str = Form(...),
    positive_prompt: str = Form(...),
    negative_prompt: str = Form(...),
    aspect_ratio: str = Form("1:1"),
    guidance_scale: float = Form(20.0),
    num_images: int = Form(4)
):
    """
    🔄 Regenerate images with modified prompt.
    
    Allows users to refine image generation.
    """
    
    try:
        generator = CampaignImageGenerator()
        
        image_prompt = ImagePrompt(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            guidance_scale=guidance_scale,
            num_images=num_images
        )
        
        images = await generator.regenerate_images(image_prompt)
        
        return JSONResponse(content={
            "campaign_id": campaign_id,
            "generated_images": images,
            "prompt_used": positive_prompt
        })
        
    except Exception as e:
        logger.error("image_regeneration_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refine-copy")
async def refine_copy(
    campaign_id: str = Form(...),
    original_caption: str = Form(...),
    original_hashtags: str = Form(...),  # Comma-separated
    original_cta: str = Form(...),
    feedback: str = Form(...)
):
    """
    ✍️ Refine campaign copy based on feedback.
    
    Uses Gemini to improve copy while maintaining core message.
    """
    
    try:
        generator = CampaignImageGenerator()
        
        # Parse original copy
        original_copy = CampaignCopy(
            caption=original_caption,
            hashtags=original_hashtags.split(","),
            call_to_action=original_cta,
            posting_schedule={},
            target_audience="",
            tone=""
        )
        
        # Refine based on feedback
        refined_copy = await generator.refine_copy(
            original_copy=original_copy,
            feedback=feedback
        )
        
        return JSONResponse(content={
            "campaign_id": campaign_id,
            "refined_copy": refined_copy.model_dump()
        })
        
    except Exception as e:
        logger.error("copy_refinement_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-campaign")
async def quick_campaign(
    dish_name: str = Form(...),
    platform: str = Form("instagram")
):
    """
    ⚡ Quick campaign generation.
    
    Fast campaign creation with minimal input.
    """
    
    try:
        generator = CampaignImageGenerator()
        
        # Use default brief
        brief = f"Create an engaging social media campaign to promote {dish_name}"
        
        campaign = await generator.generate_complete_campaign(
            dish_name=dish_name,
            campaign_brief=brief,
            platform=platform
        )
        
        return campaign
        
    except Exception as e:
        logger.error("quick_campaign_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def campaigns_health():
    """Health check for campaign generation endpoints."""
    return {
        "status": "healthy",
        "campaign_generation_enabled": True,
        "features": [
            "complete_campaign_package",
            "imagen_3_integration",
            "gemini_strategy",
            "copy_generation",
            "image_regeneration",
            "copy_refinement"
        ],
        "advantage": "Imagen 3 superior to DALL-E 3 for food photography"
    }
