from datetime import datetime
import json
from typing import List
from pathlib import Path
import base64

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import load_session
from app.models.database import get_db
from app.models.analysis import Campaign, CampaignAsset, ProductProfile
from app.models.business import MenuItem
from app.services.gemini.creative_autopilot import CreativeAutopilotAgent
from app.services.intelligence.social_aesthetics import SocialAestheticsAnalyzer

router = APIRouter()

@router.get("/session/{session_id}/files", tags=["Session"])
async def list_session_files(session_id: str):
    """
    Lists all uploaded files in a session.
    Returns relative paths organized by type (menu, dishes, sales, competitors).
    """
    upload_dir = Path(f"data/uploads/{session_id}")
    
    if not upload_dir.exists():
        return {
            "menu": [],
            "dishes": [],
            "sales": [],
            "competitors": []
        }
    
    files = {
        "menu": [],
        "dishes": [],
        "sales": [],
        "competitors": []
    }
    
    # Scan subdirectories
    for subdir_name in ["menu", "dishes", "sales", "competitors"]:
        subdir = upload_dir / subdir_name
        if subdir.exists() and subdir.is_dir():
            for file_path in subdir.iterdir():
                if file_path.is_file():
                    files[subdir_name].append({
                        "path": f"{subdir_name}/{file_path.name}",
                        "name": file_path.name,
                        "type": file_path.suffix.lower(),
                        "size": file_path.stat().st_size,
                    })
    
    return files

@router.post("/creative/menu-transform-from-session", tags=["Creative"])
async def transform_menu_from_session(
    session_id: str = Form(...),
    image_path: str = Form(...),  # e.g., "menu/menu_001.jpg"
    target_style: str = Form(...),
):
    """
    Transforms a menu image that already exists in the session.
    No re-upload required. Uses Gemini 3 Image Generation.
    """
    upload_dir = Path(f"data/uploads/{session_id}")
    image_file = upload_dir / image_path
    
    if not image_file.exists():
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")
    
    autopilot = CreativeAutopilotAgent()
    
    try:
        # Read image
        image_content = image_file.read_bytes()
        
        # Transform using Gemini 3
        result = await autopilot.transform_menu_visual_style(
            menu_image=image_content,
            target_style=target_style
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Save result
        output_dir = upload_dir / "transformed"
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"transformed_{image_file.stem}_{target_style}.png"
        output_path = output_dir / output_filename
        
        if result.get("transformed_menu"):
            output_path.write_bytes(result["transformed_menu"])
            
            # Return transformed file info
            return {
                "original_path": image_path,
                "transformed_path": f"transformed/{output_filename}",
                "style": target_style,
                "url": f"/api/v1/files/{session_id}/transformed/{output_filename}",
                "transformed_menu_base64": base64.b64encode(result["transformed_menu"]).decode('utf-8')
            }
        else:
            raise HTTPException(status_code=500, detail="No transformed image in result")
        
    except Exception as e:
        logger.error(f"Menu transform from session failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creative/menu-transform", tags=["Creative"])
async def transform_menu_style(
    target_style: str = Form(...),
    image: UploadFile = File(...),
):
    """
    Transforms the visual style of a menu while preserving the content (text/prices).
    Uses Gemini 3 Image Generation (Nano Banana Pro).
    """
    autopilot = CreativeAutopilotAgent()
    
    try:
        content = await image.read()
        result = await autopilot.transform_menu_visual_style(
            menu_image=content,
            target_style=target_style
        )
        
        if "error" in result:
             raise HTTPException(status_code=500, detail=result["error"])
             
        # Convert bytes back to base64 for JSON response if needed, 
        # or we could return StreamingResponse. 
        # For this API, returning base64 in JSON is easiest for frontend to display.
        import base64
        if result.get("transformed_menu"):
            result["transformed_menu_base64"] = base64.b64encode(result["transformed_menu"]).decode('utf-8')
            del result["transformed_menu"] # Remove raw bytes
            
        return result
        
    except Exception as e:
        logger.error(f"Menu transform failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creative/instagram-prediction", tags=["Creative"])
async def predict_instagram_engagement(
    restaurant_category: str = Form(...),
    posting_time_iso: str = Form(..., description="ISO 8601 datetime string"), 
    image: UploadFile = File(...),
):
    """
    Predicts engagement for an Instagram photo using Gemini Vision + Grounding.
    """
    analyzer = SocialAestheticsAnalyzer()
    
    try:
        content = await image.read()
        
        try:
            posting_time = datetime.fromisoformat(posting_time_iso.replace("Z", "+00:00"))
        except ValueError:
            posting_time = datetime.utcnow()
            
        result = await analyzer.predict_instagram_performance(
            dish_photo=content,
            restaurant_category=restaurant_category,
            posting_time=posting_time
        )
        
        if "error" in result:
             raise HTTPException(status_code=500, detail=result["error"])
             
        return result
        
    except Exception as e:
        logger.error(f"Instagram prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns/creative-autopilot", tags=["Creative"])
async def generate_creative_autopilot_campaign(
    restaurant_name: str,
    dish_id: int,
    session_id: str,
    target_languages: List[str] = Query(["es", "en"]),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a complete visual campaign using Creative Autopilot + Nano Banana Pro.
    
    This is a KEY DIFFERENTIATOR of the hackathon - it uses unique Gemini 3 capabilities:
    - 4K image generation with readable text
    - Multi-reference branding
    - Grounding with Google Search for trends
    - Automatic visual localization
    """
    
    autopilot = CreativeAutopilotAgent()

    session_data = load_session(session_id) or {}

    # Get dish data (DB first, then fall back to session menu list)
    result = await db.execute(select(MenuItem).where(MenuItem.id == dish_id))
    dish = result.scalar_one_or_none()

    dish_name: str
    dish_description: str
    dish_price: float
    dish_category: str

    if dish:
        dish_name = dish.name
        dish_description = dish.description or ""
        dish_price = dish.price
        dish_category = "General"
    else:
        # Fallback: interpret dish_id as a 1-based index into session_data['menu_items']
        menu_items = session_data.get("menu_items") or []
        dish_from_session = None

        # Primary: 1-based index
        idx = dish_id - 1
        if isinstance(menu_items, list) and 0 <= idx < len(menu_items):
            dish_from_session = menu_items[idx]
        else:
            # Secondary: match by explicit id field if present
            dish_from_session = next(
                (item for item in menu_items if isinstance(item, dict) and item.get("id") == dish_id),
                None,
            )

        if not isinstance(dish_from_session, dict) or not dish_from_session.get("name"):
            raise HTTPException(status_code=404, detail="Dish not found")

        dish_name = str(dish_from_session.get("name"))
        dish_description = str(dish_from_session.get("description") or "")
        dish_price = float(dish_from_session.get("price") or 0)
        dish_category = str(dish_from_session.get("category") or "General")

    # Get BCG classification (DB ProductProfile first, then fall back to session bcg_analysis)
    bcg_classification = "unknown"

    if dish:
        result_bcg = await db.execute(
            select(ProductProfile)
            .where(ProductProfile.session_id == session_id)
            .where(ProductProfile.menu_item_id == dish_id)
        )
        product_profile = result_bcg.scalar_one_or_none()
        if product_profile:
            bcg_classification = str(product_profile.bcg_class)

    if bcg_classification == "unknown":
        bcg_analysis = session_data.get("bcg_analysis")
        if isinstance(bcg_analysis, dict):
            items = bcg_analysis.get("items") or bcg_analysis.get("classifications") or []
            if isinstance(items, list):
                matched = next(
                    (
                        it
                        for it in items
                        if isinstance(it, dict)
                        and str(it.get("name", "")).strip().lower() == dish_name.strip().lower()
                    ),
                    None,
                )
                if isinstance(matched, dict):
                    bcg_classification = str(
                        matched.get("category")
                        or matched.get("bcg_category")
                        or matched.get("bcg_class")
                        or matched.get("category_label")
                        or "unknown"
                    )

    # Get brand guidelines if available
    brand_guidelines = {}
    if isinstance(session_data, dict) and "brand_guidelines" in session_data:
        brand_guidelines = session_data["brand_guidelines"]
    
    # GENERATE FULL CAMPAIGN
    try:
        campaign_data = await autopilot.generate_full_campaign(
            restaurant_name=restaurant_name,
            dish_data={
                "name": dish_name,
                "description": dish_description,
                "price": dish_price,
                "category": dish_category,
            },
            bcg_classification=str(bcg_classification),
            brand_guidelines=brand_guidelines
        )
        
        # LOCALIZE to multiple languages
        localized = await autopilot.localize_campaign(
            campaign_data['visual_assets'],
            target_languages
        )
        
        campaign_data['localized_versions'] = localized
        
        # Extract Strategy Fields
        strategy = campaign_data.get('strategy', {})
        concept = campaign_data.get('creative_concept', {})

        objective = next(
            (
                strategy.get(k)
                for k in (
                    "1. Main objective",
                    "1. Primary objective",
                    "1. Objetivo principal",
                    "objective",
                )
                if strategy.get(k)
            ),
            "Sales Growth",
        )

        target_audience = next(
            (
                strategy.get(k)
                for k in (
                    "2. Ideal target audience",
                    "2. Target audience",
                    "2. Público objetivo ideal",
                    "target_audience",
                )
                if strategy.get(k)
            ),
            "General Audience",
        )
        
        # Save to database
        db_campaign = Campaign(
            session_id=session_id,
            title=f"Creative Autopilot: {dish_name}",
            objective=objective,
            target_audience=target_audience,
            start_date=datetime.utcnow().date(),
            end_date=datetime.utcnow().date(),
            schedule={}, 
            channels=["Instagram", "Social Media"],
            key_messages=[concept.get('main_message', '')],
            promotional_items=[dish_name],
            discount_strategy=None,
            
            # Storing full structured data in rationale for now as Campaign model is strict
            rationale=json.dumps({
                "strategy": strategy,
                "creative_concept": concept,
                "impact_analysis": campaign_data.get("estimated_impact")
            }),
            
            social_post_copy=concept.get('headline', ''),
            image_prompt=concept.get('visual_description', ''),
            
            expected_uplift_percent=campaign_data.get('estimated_impact', 0.5) * 100,
            confidence_level=0.9
        )
        
        db.add(db_campaign)
        await db.commit()
        await db.refresh(db_campaign)
        
        # Save visual assets
        for asset in campaign_data['visual_assets']:
            db_asset = CampaignAsset(
                campaign_id=db_campaign.id,
                asset_type=asset.get('type', 'image'),
                format=asset.get('format', 'unknown'),
                image_data=asset.get('image_data'), # Assuming bytes
                reasoning=asset.get('reasoning'),
                concept=asset.get('concept'),
                language="es" # Original language
            )
            db.add(db_asset)
            
        # Save localized versions
        for lang, assets in localized.items():
            for asset in assets:
                db_asset = CampaignAsset(
                    campaign_id=db_campaign.id,
                    asset_type=asset.get('type', 'image'),
                    format=asset.get('format', 'unknown'),
                    image_data=asset.get('image_data'),
                    reasoning=asset.get('reasoning'),
                    concept=asset.get('concept'),
                    language=lang,
                    variant_type="localized"
                )
                db.add(db_asset)
        
        await db.commit()
        
        return {
            "campaign_id": db_campaign.id,
            "campaign": campaign_data,
            "demo_url": f"/campaigns/{db_campaign.id}/preview"
        }
        
    except Exception as e:
        logger.error(f"Creative Autopilot failed: {e}")
        # Log stack trace
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Creative Autopilot Generation Failed: {str(e)}")
