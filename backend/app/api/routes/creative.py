from datetime import datetime
import json
from typing import List


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

@router.post("/creative/menu-transform", tags=["Creative"])
async def transform_menu_style(
    target_style: str = Form(...),
    image: UploadFile = File(...),
):
    """
    Transforma el estilo visual de un menú manteniendo el contenido (texto/precios).
    Usa Gemini 3 Image Generation (Nano Banana Pro).
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
    Predice el engagement de una foto en Instagram usando Gemini Vision + Grounding.
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
    Genera campaña visual completa usando Creative Autopilot + Nano Banana Pro.
    
    Este es un DIFERENCIADOR CLAVE del hackathon - usa capacidades únicas de Gemini 3:
    - Generación de imágenes 4K con texto legible
    - Multi-reference branding
    - Grounding con Google Search para tendencias
    - Localización visual automática
    """
    
    autopilot = CreativeAutopilotAgent()
    
    # Obtener datos del plato
    result = await db.execute(select(MenuItem).where(MenuItem.id == dish_id))
    dish = result.scalar_one_or_none()
    
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    # Obtener clasificación BCG
    result_bcg = await db.execute(
        select(ProductProfile)
        .where(ProductProfile.session_id == session_id)
        .where(ProductProfile.menu_item_id == dish_id)
    )
    product_profile = result_bcg.scalar_one_or_none()
    
    bcg_classification = product_profile.bcg_class if product_profile else "unknown"
    
    # Obtener brand guidelines si existen
    session_data = load_session(session_id)
    brand_guidelines = {}
    if session_data and "brand_guidelines" in session_data:
        brand_guidelines = session_data["brand_guidelines"]
    
    # GENERAR CAMPAÑA COMPLETA
    try:
        # Prepare dish data
        category_name = "General"
        if dish.category_id:
             # We could fetch category name but optimizing for speed, use generic or fetch if needed
             pass

        campaign_data = await autopilot.generate_full_campaign(
            restaurant_name=restaurant_name,
            dish_data={
                "name": dish.name,
                "description": dish.description or "",
                "price": dish.price,
                "category": category_name
            },
            bcg_classification=str(bcg_classification),
            brand_guidelines=brand_guidelines
        )
        
        # LOCALIZAR a múltiples idiomas
        localized = await autopilot.localize_campaign(
            campaign_data['visual_assets'],
            target_languages
        )
        
        campaign_data['localized_versions'] = localized
        
        # Extract Strategy Fields
        strategy = campaign_data.get('strategy', {})
        concept = campaign_data.get('creative_concept', {})
        
        # Guardar en base de datos
        db_campaign = Campaign(
            session_id=session_id,
            title=f"Creative Autopilot: {dish.name}",
            objective=strategy.get('1. Objetivo principal', 'Sales Growth'),
            target_audience=strategy.get('2. Público objetivo ideal', 'General Audience'),
            start_date=datetime.utcnow().date(),
            end_date=datetime.utcnow().date(),
            schedule={}, 
            channels=["Instagram", "Social Media"],
            key_messages=[concept.get('main_message', '')],
            promotional_items=[dish.name],
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
        
        # Guardar assets visuales
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
