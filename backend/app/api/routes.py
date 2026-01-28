"""
API Routes for MenuPilot.

Provides endpoints for:
- /ingest: Upload menu images and sales data
- /analyze: Run BCG analysis and generate product profiles
- /predict: Sales prediction for scenarios
- /campaigns: Generate marketing campaign proposals
"""

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import get_settings
from app.services.advanced_analytics import AdvancedAnalyticsService
from app.services.bcg_classifier import BCGClassifier
from app.services.campaign_generator import CampaignGenerator
from app.services.data_capability_detector import DataCapabilityDetector
from app.services.gemini_agent import GeminiAgent
from app.services.menu_extractor import DishImageAnalyzer, MenuExtractor
from app.services.menu_optimizer import MenuOptimizer
from app.services.neural_predictor import NeuralPredictor
from app.services.orchestrator import AnalysisOrchestrator
from app.services.sales_predictor import SalesPredictor
from app.services.verification_agent import ThinkingLevel, VerificationAgent

router = APIRouter()
settings = get_settings()

# Initialize services
agent = GeminiAgent()
menu_extractor = MenuExtractor(agent)
dish_analyzer = DishImageAnalyzer(agent)
bcg_classifier = BCGClassifier(agent)
sales_predictor = SalesPredictor()
campaign_generator = CampaignGenerator(agent)
verification_agent = VerificationAgent(agent)
neural_predictor = NeuralPredictor()
orchestrator = AnalysisOrchestrator()
data_capability_detector = DataCapabilityDetector()
menu_optimizer = MenuOptimizer()
advanced_analytics = AdvancedAnalyticsService()

# In-memory session storage (use Redis/DB in production)
sessions = {}


@router.post("/ingest/menu", tags=["Ingest"])
async def ingest_menu_image(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    business_context: Optional[str] = Form(None),
):
    """
    Upload and process menu images/PDFs (supports multiple files).

    Extracts menu items using OCR and Gemini multimodal analysis.
    """

    # Create or get session
    session_id = session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "menu_items": [],
            "sales_data": [],
        }

    upload_dir = Path("data/uploads") / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    all_items = []
    total_files_processed = 0

    for file in files:
        # Validate file
        ext = file.filename.split(".")[-1].lower() if file.filename else ""
        if ext not in settings.allowed_image_ext_list:
            logger.warning(f"Skipping invalid file type: {file.filename}")
            continue

        # Save file
        file_path = upload_dir / f"menu_{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract menu items
        try:
            # Use PDF-specific extraction for PDFs to handle multiple pages
            if ext == "pdf":
                result = await menu_extractor.extract_from_pdf_all_pages(
                    str(file_path), use_ocr=True, business_context=business_context
                )
            else:
                result = await menu_extractor.extract_from_image(
                    str(file_path), use_ocr=True, business_context=business_context
                )

            all_items.extend(result.get("items", []))
            total_files_processed += 1
        except Exception as e:
            logger.error(f"Failed to process {file.filename}: {e}")
            continue

    # Store in session - deduplicate items by name
    existing_names = {
        item["name"].lower() for item in sessions[session_id]["menu_items"]
    }
    new_items = [
        item for item in all_items if item["name"].lower() not in existing_names
    ]
    sessions[session_id]["menu_items"].extend(new_items)

    result = {"items": new_items, "item_count": len(new_items)}
    sessions[session_id]["menu_extraction"] = result

    # Create thought signature
    thought = await agent.create_thought_signature(
        "Extract menu items from uploaded files",
        {"files_processed": total_files_processed, "items_found": len(new_items)},
    )

    return {
        "session_id": session_id,
        "status": "success",
        "items_extracted": len(new_items),
        "files_processed": total_files_processed,
        "items": new_items,
        "thought_process": thought,
    }


@router.post("/ingest/dishes", tags=["Ingest"])
async def ingest_dish_images(
    files: List[UploadFile] = File(...), session_id: str = Form(...)
):
    """
    Upload and analyze dish photographs.

    Evaluates visual appeal and attractiveness of each dish.
    """

    if session_id not in sessions:
        raise HTTPException(404, "Session not found. Upload menu first.")

    upload_dir = Path("data/uploads") / session_id / "dishes"
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for file in files:
        ext = file.filename.split(".")[-1].lower() if file.filename else ""
        if ext not in settings.allowed_image_ext_list:
            continue

        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_paths.append(str(file_path))

    if not saved_paths:
        raise HTTPException(400, "No valid images uploaded")

    # Analyze dishes
    try:
        menu_item_names = [
            item["name"] for item in sessions[session_id].get("menu_items", [])
        ]
        result = await dish_analyzer.analyze_images(saved_paths, menu_item_names)

        # Store image scores
        sessions[session_id]["image_analyses"] = result["analyses"]
        sessions[session_id]["image_scores"] = {
            a.get("matched_menu_item", a.get("dish_name", f"dish_{i}")): a.get(
                "attractiveness_score", 0.5
            )
            for i, a in enumerate(result["analyses"])
        }

        return {
            "session_id": session_id,
            "status": "success",
            "images_analyzed": result["image_count"],
            "summary": result["summary"],
            "analyses": result["analyses"],
        }

    except Exception as e:
        logger.error(f"Dish analysis failed: {e}")
        raise HTTPException(500, f"Dish analysis failed: {str(e)}")


@router.post("/ingest/audio", tags=["Ingest"])
async def ingest_audio_context(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    context_type: str = Form(...),  # 'business' or 'competitor'
):
    """
    Upload audio file for multimodal analysis with Gemini.

    Audio is NOT transcribed locally - it's sent directly to Gemini
    for multimodal understanding, exploiting its native audio capabilities.

    Args:
        file: Audio file (mp3, wav, m4a, ogg, webm)
        session_id: Session identifier
        context_type: 'business' for company context, 'competitor' for competition context
    """
    if session_id not in sessions:
        raise HTTPException(404, "Session not found. Upload sales data first.")

    # Validate file type
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    allowed_audio = ["mp3", "wav", "m4a", "ogg", "webm", "flac", "aac"]
    if ext not in allowed_audio:
        raise HTTPException(400, f"Invalid audio format. Allowed: {allowed_audio}")

    if context_type not in ["business", "competitor"]:
        raise HTTPException(400, "context_type must be 'business' or 'competitor'")

    # Save audio file
    upload_dir = Path("data/uploads") / session_id / "audio"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{context_type}_{file.filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Store audio path in session for later Gemini processing
    if "audio_files" not in sessions[session_id]:
        sessions[session_id]["audio_files"] = {"business": [], "competitor": []}

    sessions[session_id]["audio_files"][context_type].append(str(file_path))

    logger.info(f"Audio uploaded for {context_type} context: {file.filename}")

    # Process audio with Gemini multimodal (native audio understanding)
    try:

        audio_bytes = Path(file_path).read_bytes()

        # Determine MIME type
        mime_types = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4",
            "ogg": "audio/ogg",
            "webm": "audio/webm",
            "flac": "audio/flac",
            "aac": "audio/aac",
        }
        mime_type = mime_types.get(ext, "audio/mpeg")

        # Analyze audio directly with Gemini (multimodal)
        prompt = f"""Analiza este audio que contiene información sobre {'el negocio/restaurante' if context_type == 'business' else 'la competencia del negocio'}.

Extrae:
1. Información clave mencionada
2. Tono y sentimiento general
3. Puntos importantes para el análisis de mercado
4. Cualquier dato específico (precios, ubicaciones, características)

Responde en JSON:
{{
    "summary": "Resumen breve del contenido",
    "key_points": ["punto 1", "punto 2"],
    "sentiment": "positive/neutral/negative",
    "market_insights": ["insight 1", "insight 2"],
    "raw_context": "Texto completo extraído del audio para contexto"
}}"""

        # Use Gemini multimodal for audio analysis
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)

        response = client.models.generate_content(
            model="gemini-3-flash-preview",  # Gemini 3 for hackathon
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type,
                                data=audio_bytes,
                            )
                        ),
                    ]
                )
            ],
        )

        # Parse response
        import json

        response_text = response.text
        # Try to extract JSON from response
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            audio_analysis = json.loads(response_text.strip())
        except json.JSONDecodeError:
            audio_analysis = {
                "summary": response_text[:500],
                "key_points": [],
                "sentiment": "neutral",
                "market_insights": [],
                "raw_context": response_text,
            }

        # Store analysis in session
        if "audio_analysis" not in sessions[session_id]:
            sessions[session_id]["audio_analysis"] = {"business": [], "competitor": []}

        sessions[session_id]["audio_analysis"][context_type].append(audio_analysis)

        # Add to context for future analysis
        context_key = f"{context_type}_context"
        existing_context = sessions[session_id].get(context_key, "")
        sessions[session_id][context_key] = (
            existing_context
            + "\n\n[Audio Context]:\n"
            + audio_analysis.get("raw_context", "")
        )

        return {
            "session_id": session_id,
            "status": "success",
            "context_type": context_type,
            "filename": file.filename,
            "analysis": audio_analysis,
            "message": "Audio analyzed directly by Gemini multimodal (no transcription)",
        }

    except Exception as e:
        logger.error(f"Audio analysis failed: {e}")
        # Still return success for upload, even if analysis failed
        return {
            "session_id": session_id,
            "status": "uploaded",
            "context_type": context_type,
            "filename": file.filename,
            "analysis": None,
            "warning": f"Audio saved but analysis pending: {str(e)}",
        }


@router.post("/ingest/sales", tags=["Ingest"])
async def ingest_sales_data(file: UploadFile = File(...), session_id: str = Form(None)):
    """
    Upload sales data CSV.

    Expected columns: date, item_name, units_sold, [revenue], [had_promotion], [promotion_discount]

    Note: session_id is optional. If not provided, a new session will be created.
    """

    # Create session if not exists (CSV can be uploaded first)
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "menu_items": [],
            "sales_data": [],
        }
        logger.info(f"Created new session from sales upload: {session_id}")

    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ["csv", "xlsx"]:
        raise HTTPException(400, "Invalid file type. Use CSV or XLSX.")

    # Save and parse file
    upload_dir = Path("data/uploads") / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)  # Create directory if not exists
    file_path = upload_dir / f"sales.{ext}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        if ext == "csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Normalize column names
        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

        # Required columns check
        required = ["date", "item_name", "units_sold"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            # Try alternative names
            alt_names = {
                "date": ["sale_date", "fecha"],
                "item_name": ["item", "producto", "plato"],
                "units_sold": ["units", "cantidad", "vendidos"],
            }
            for col in missing:
                for alt in alt_names.get(col, []):
                    if alt in df.columns:
                        df = df.rename(columns={alt: col})
                        break

        missing = [c for c in required if c not in df.columns]
        if missing:
            raise HTTPException(400, f"Missing required columns: {missing}")

        # Convert to records
        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        sales_records = df.to_dict("records")

        sessions[session_id]["sales_data"] = sales_records

        # Calculate summary
        total_units = df["units_sold"].sum()
        date_range = {"start": df["date"].min(), "end": df["date"].max()}
        unique_items = df["item_name"].nunique()

        thought = await agent.create_thought_signature(
            "Process uploaded sales data",
            {"records": len(sales_records), "date_range": date_range},
        )

        return {
            "session_id": session_id,
            "status": "success",
            "records_imported": len(sales_records),
            "date_range": date_range,
            "unique_items": unique_items,
            "total_units": int(total_units),
            "total_revenue": (
                float(df["revenue"].sum()) if "revenue" in df.columns else None
            ),
            "thought_process": thought,
            "warnings": [],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sales data processing failed: {e}")
        raise HTTPException(500, f"Sales data processing failed: {str(e)}")


@router.post("/analyze/bcg", tags=["Analyze"])
async def run_bcg_analysis(session_id: str):
    """
    Run BCG Matrix analysis on menu items.

    Classifies products as Star, Cash Cow, Question Mark, or Dog
    based on market share and growth metrics.
    """

    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]
    menu_items = session.get("menu_items", [])
    sales_data = session.get("sales_data", [])
    image_scores = session.get("image_scores", {})

    # MERGE menu items from both sources: menu extraction AND sales data
    # Primary source: sales_data (database), Complementary: menu extraction (visual)
    existing_menu_names = {item["name"].lower().strip() for item in menu_items}

    if sales_data:
        # Get unique items from sales data
        unique_sales_items = set(
            record.get("item_name", "")
            for record in sales_data
            if record.get("item_name")
        )

        # Add items from sales that aren't already in menu
        items_added_from_sales = 0
        for item_name in unique_sales_items:
            if item_name.lower().strip() not in existing_menu_names:
                # Calculate average price from sales if revenue available
                item_sales = [s for s in sales_data if s.get("item_name") == item_name]
                total_revenue = sum(s.get("revenue", 0) for s in item_sales)
                total_units = sum(s.get("units_sold", 0) for s in item_sales)
                avg_price = (
                    total_revenue / total_units
                    if total_units > 0 and total_revenue > 0
                    else 0.0
                )

                menu_items.append(
                    {
                        "name": item_name,
                        "price": round(avg_price, 2),
                        "description": "",
                        "category": "From Sales Data",
                        "source": "sales_data",
                    }
                )
                existing_menu_names.add(item_name.lower().strip())
                items_added_from_sales += 1

        if items_added_from_sales > 0:
            logger.info(f"Added {items_added_from_sales} items from sales data to menu")

    # Also add menu items that have no sales (they still need to be analyzed)
    if menu_items:
        for item in menu_items:
            if item.get("source") != "sales_data":
                # Mark items from menu extraction that have no sales
                item_sales = [
                    s
                    for s in sales_data
                    if s.get("item_name", "").lower().strip()
                    == item["name"].lower().strip()
                ]
                if not item_sales:
                    item["has_sales_data"] = False
                    item["analysis_note"] = "Item visible in menu but no sales recorded"
                else:
                    item["has_sales_data"] = True

        sessions[session_id]["menu_items"] = menu_items
        logger.info(
            f"Total menu items for BCG analysis: {len(menu_items)} (menu: {len([i for i in menu_items if i.get('source') != 'sales_data'])}, sales: {len([i for i in menu_items if i.get('source') == 'sales_data'])})"
        )

    if not menu_items:
        raise HTTPException(
            400, "No menu items found. Upload sales data or menu first."
        )

    try:
        result = await bcg_classifier.classify_products(
            menu_items, sales_data, image_scores
        )

        sessions[session_id]["bcg_analysis"] = result

        return {
            "session_id": session_id,
            "status": "success",
            "analysis_timestamp": result["analysis_timestamp"],
            "total_items_analyzed": len(result["classifications"]),
            "summary": result["summary"],
            "classifications": result["classifications"],
            "thresholds": result["thresholds"],
            "ai_insights": result["ai_insights"],
            "thought_signature": await agent.create_thought_signature(
                "BCG Matrix classification",
                {"items": len(menu_items), "summary": result["summary"]},
            ),
        }

    except Exception as e:
        logger.error(f"BCG analysis failed: {e}")
        raise HTTPException(500, f"BCG analysis failed: {str(e)}")


@router.post("/predict/sales", tags=["Predict"])
async def predict_sales(
    session_id: str, horizon_days: int = 14, scenarios: Optional[List[dict]] = None
):
    """
    Predict sales for menu items under different scenarios.
    """

    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]
    menu_items = session.get("menu_items", [])
    sales_data = session.get("sales_data", [])
    image_scores = session.get("image_scores", {})

    if not menu_items:
        raise HTTPException(400, "No menu items found")

    try:
        # Train model if needed
        if sales_predictor.model is None:
            await sales_predictor.train(sales_data, menu_items, image_scores)

        # Prepare items for prediction
        items_for_prediction = []
        for item in menu_items:
            item_sales = [s for s in sales_data if s.get("item_name") == item["name"]]
            avg_daily = sum(s.get("units_sold", 0) for s in item_sales) / max(
                len(item_sales), 1
            )
            items_for_prediction.append(
                {
                    "name": item["name"],
                    "price": item.get("price", 0),
                    "image_score": image_scores.get(item["name"], 0.5),
                    "avg_daily_units": avg_daily,
                }
            )

        scenarios = scenarios or [
            {"name": "baseline"},
            {
                "name": "10%_discount",
                "promotion_active": True,
                "promotion_discount": 0.1,
            },
            {"name": "marketing_boost", "marketing_boost": 1.3},
        ]

        result = await sales_predictor.predict_batch(
            items_for_prediction, horizon_days, scenarios
        )
        sessions[session_id]["predictions"] = result

        return {
            "session_id": session_id,
            "status": "success",
            "horizon_days": horizon_days,
            "scenario_totals": result["scenario_totals"],
            "item_predictions": result["item_predictions"],
            "model_metrics": sales_predictor.model_metrics,
            "thought_signature": await agent.create_thought_signature(
                "Sales prediction",
                {"horizon": horizon_days, "scenarios": len(scenarios)},
            ),
        }

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(500, f"Prediction failed: {str(e)}")


@router.post("/campaigns/generate", tags=["Campaigns"])
async def generate_campaigns(
    session_id: str,
    num_campaigns: int = 3,
    duration_days: int = 14,
    channels: Optional[List[str]] = None,
):
    """
    Generate marketing campaign proposals based on analysis.
    """

    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]
    bcg_analysis = session.get("bcg_analysis")
    menu_items = session.get("menu_items", [])

    if not bcg_analysis:
        raise HTTPException(400, "Run BCG analysis first")

    try:
        result = await campaign_generator.generate_campaigns(
            bcg_analysis, menu_items, num_campaigns, duration_days, channels
        )

        sessions[session_id]["campaigns"] = result["campaigns"]

        return {
            "session_id": session_id,
            "status": "success",
            "campaigns_generated": len(result["campaigns"]),
            "campaigns": result["campaigns"],
            "thought_signature": result["thought_signature"],
        }

    except Exception as e:
        logger.error(f"Campaign generation failed: {e}")
        raise HTTPException(500, f"Campaign generation failed: {str(e)}")


@router.get("/session/{session_id}", tags=["Session"])
async def get_session(session_id: str):
    """Get full session data including all analysis results."""

    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]

    return {
        "session_id": session_id,
        "created_at": session.get("created_at"),
        "menu_items_count": len(session.get("menu_items", [])),
        "sales_records_count": len(session.get("sales_data", [])),
        "has_bcg_analysis": "bcg_analysis" in session,
        "has_predictions": "predictions" in session,
        "campaigns_count": len(session.get("campaigns", [])),
        "data": session,
    }


@router.get("/session/{session_id}/export", tags=["Session"])
async def export_session(session_id: str):
    """Export full analysis results as JSON."""

    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]

    # Compile final report
    report = {
        "session_id": session_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "menu_catalog": session.get("menu_items", []),
        "bcg_analysis": session.get("bcg_analysis"),
        "predictions": session.get("predictions"),
        "campaigns": session.get("campaigns", []),
        "gemini_usage": agent.get_stats(),
    }

    return JSONResponse(content=report, media_type="application/json")


# ============================================================================
# ENHANCED AGENTIC ENDPOINTS
# ============================================================================


@router.post("/orchestrator/run", tags=["Orchestrator"])
async def run_autonomous_pipeline(
    menu_image: Optional[UploadFile] = File(None),
    dish_images: Optional[List[UploadFile]] = File(None),
    sales_file: Optional[UploadFile] = File(None),
    thinking_level: str = Form("standard"),
    auto_verify: bool = Form(True),
):
    """
    Run the complete autonomous analysis pipeline.

    This endpoint orchestrates the entire MenuPilot workflow:
    1. Menu extraction from images
    2. Dish photo analysis
    3. Sales data processing
    4. BCG classification
    5. Sales prediction
    6. Campaign generation
    7. Autonomous verification and improvement

    Uses the Marathon Agent pattern with checkpoints for reliability.
    """

    try:
        level = ThinkingLevel(thinking_level)
    except ValueError:
        level = ThinkingLevel.STANDARD

    session_id = await orchestrator.create_session()

    menu_bytes = None
    dish_bytes = None
    sales_csv = None

    if menu_image:
        menu_bytes = [await menu_image.read()]

    if dish_images:
        dish_bytes = [await img.read() for img in dish_images]

    if sales_file:
        content = await sales_file.read()
        sales_csv = content.decode("utf-8")

    try:
        result = await orchestrator.run_full_pipeline(
            session_id=session_id,
            menu_images=menu_bytes,
            dish_images=dish_bytes,
            sales_csv=sales_csv,
            thinking_level=level,
            auto_verify=auto_verify,
        )

        return result

    except Exception as e:
        logger.error(f"Orchestrator pipeline failed: {e}")
        raise HTTPException(500, f"Pipeline failed: {str(e)}")


@router.get("/orchestrator/status/{session_id}", tags=["Orchestrator"])
async def get_orchestrator_status(session_id: str):
    """Get the status of an orchestrator session."""

    status = orchestrator.get_session_status(session_id)
    if not status:
        raise HTTPException(404, "Session not found")

    return status


@router.post("/verify/analysis", tags=["Verification"])
async def verify_analysis(
    session_id: str,
    thinking_level: str = "standard",
    auto_improve: bool = True,
):
    """
    Run the verification agent on an existing analysis.

    Implements the Vibe Engineering pattern:
    - Validates data completeness
    - Checks BCG classification accuracy
    - Verifies prediction reasonableness
    - Ensures campaign-BCG alignment
    - Assesses business viability
    - Auto-improves if quality thresholds not met
    """

    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]

    try:
        level = ThinkingLevel(thinking_level)
    except ValueError:
        level = ThinkingLevel.STANDARD

    analysis_data = {
        "products": session.get("menu_items", []),
        "bcg_analysis": session.get("bcg_analysis"),
        "predictions": session.get("predictions"),
        "campaigns": session.get("campaigns", []),
    }

    try:
        result = await verification_agent.verify_analysis(
            analysis_data,
            thinking_level=level,
            auto_improve=auto_improve,
        )

        sessions[session_id]["verification"] = {
            "status": result.status.value,
            "overall_score": result.overall_score,
            "iterations": result.iterations_used,
            "improvements": result.improvements_made,
        }

        return {
            "session_id": session_id,
            "status": result.status.value,
            "overall_score": result.overall_score,
            "iterations_used": result.iterations_used,
            "improvements_made": result.improvements_made,
            "checks": [
                {
                    "name": c.check_name,
                    "passed": c.passed,
                    "score": c.score,
                    "feedback": c.feedback,
                    "suggestions": c.suggestions,
                }
                for c in result.checks
            ],
            "final_recommendation": result.final_recommendation,
            "thinking_level": result.thinking_level.value,
        }

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(500, f"Verification failed: {str(e)}")


@router.post("/predict/neural", tags=["Predict"])
async def predict_with_neural_network(
    session_id: str,
    horizon_days: int = 14,
    use_ensemble: bool = True,
    uncertainty_samples: int = 10,
):
    """
    Run sales prediction using deep learning models.

    Uses LSTM and Transformer neural networks for:
    - More sophisticated pattern recognition
    - Uncertainty quantification via Monte Carlo Dropout
    - 95% confidence intervals on predictions
    - Ensemble predictions combining multiple architectures
    """

    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]
    menu_items = session.get("menu_items", [])
    sales_data = session.get("sales_data", [])
    image_scores = session.get("image_scores", {})

    if not menu_items:
        raise HTTPException(400, "No menu items found")

    try:
        # Train neural models if needed
        if not neural_predictor.is_trained:
            train_result = await neural_predictor.train(
                sales_data, menu_items, epochs=30
            )
            logger.info(f"Neural training: {train_result}")

        # Get predictions for each item
        predictions = {}
        for item in menu_items:
            base_features = {
                "price": item.get("price", 15),
                "avg_daily_units": 20,
                "image_score": image_scores.get(item["name"], 0.5),
            }

            scenarios = [
                {"name": "baseline"},
                {"name": "promotion", "promotion_active": True},
                {"name": "premium", "price_change_percent": 10},
            ]

            result = await neural_predictor.predict(
                item["name"],
                horizon_days,
                base_features,
                scenarios,
                use_ensemble=use_ensemble,
                uncertainty_samples=uncertainty_samples,
            )

            predictions[item["name"]] = result

        sessions[session_id]["neural_predictions"] = predictions

        return {
            "session_id": session_id,
            "status": "success",
            "model_info": neural_predictor.get_model_info(),
            "horizon_days": horizon_days,
            "use_ensemble": use_ensemble,
            "predictions": predictions,
            "thought_signature": await agent.create_thought_signature(
                "Neural network sales prediction",
                {
                    "models": ["LSTM", "Transformer"],
                    "ensemble": use_ensemble,
                    "uncertainty_quantified": True,
                },
            ),
        }

    except Exception as e:
        logger.error(f"Neural prediction failed: {e}")
        raise HTTPException(500, f"Neural prediction failed: {str(e)}")


@router.get("/models/info", tags=["Models"])
async def get_model_info():
    """Get information about all ML models."""

    return {
        "xgboost_predictor": {
            "trained": sales_predictor.model is not None,
            "metrics": sales_predictor.model_metrics,
        },
        "neural_predictor": neural_predictor.get_model_info(),
        "verification_agent": verification_agent.get_verification_summary(),
    }


# ============================================================================
# DEMO ENDPOINTS
# ============================================================================


@router.get("/demo/session", tags=["Demo"])
async def get_demo_session():
    """
    Get pre-loaded demo session data.

    Returns a complete session with:
    - 10 menu items (Mexican restaurant)
    - BCG classification for all items
    - 3 AI-generated marketing campaigns
    - Sales predictions with scenarios
    - Thought signature and Marathon Agent context
    """

    demo_file = Path("data/demo/session.json")
    if not demo_file.exists():
        raise HTTPException(
            404, "Demo data not found. Run scripts/seed_demo_data.py first."
        )

    with open(demo_file, "r") as f:
        demo_data = json.load(f)

    # Also load into sessions for further API calls
    sessions["demo-session-001"] = {
        "menu_items": demo_data["menu"]["items"],
        "bcg_analysis": demo_data["bcg"],
        "campaigns": demo_data["campaigns"]["campaigns"],
        "predictions": demo_data.get("predictions"),
        "thought_signature": demo_data.get("thought_signature"),
        "marathon_agent_context": demo_data.get("marathon_agent_context"),
    }

    # Return complete data including predictions
    # campaigns needs to be the full object with campaigns array for frontend
    campaigns_data = demo_data.get("campaigns", {})
    if isinstance(campaigns_data, dict) and "campaigns" in campaigns_data:
        campaigns_result = campaigns_data
    else:
        campaigns_result = {
            "campaigns": campaigns_data,
            "thought_process": "Demo campaign generation",
        }

    return {
        "session_id": demo_data["session_id"],
        "status": demo_data["status"],
        "created_at": demo_data["created_at"],
        "menu": demo_data["menu"],
        "bcg": demo_data["bcg"],
        "bcg_analysis": demo_data["bcg"],  # Alias for frontend compatibility
        "campaigns": campaigns_result,
        "predictions": demo_data.get("predictions"),
        "thought_signature": demo_data.get("thought_signature"),
        "marathon_agent_context": demo_data.get("marathon_agent_context"),
    }


@router.get("/demo/load", tags=["Demo"])
async def load_demo_into_session():
    """
    Load demo data into a new session for testing.

    Returns a session_id that can be used with all other endpoints.
    """

    demo_file = Path("data/demo/session.json")
    if not demo_file.exists():
        raise HTTPException(
            404, "Demo data not found. Run scripts/seed_demo_data.py first."
        )

    with open(demo_file, "r") as f:
        demo_data = json.load(f)

    session_id = "demo-session-001"

    # Load into sessions
    sessions[session_id] = {
        "menu_items": demo_data["menu"]["items"],
        "categories": demo_data["menu"]["categories"],
        "bcg_analysis": demo_data["bcg"],
        "campaigns": demo_data["campaigns"]["campaigns"],
        "created_at": demo_data["created_at"],
    }

    return {
        "session_id": session_id,
        "status": "loaded",
        "items_count": len(demo_data["menu"]["items"]),
        "message": "Demo session loaded. Use this session_id with /session/{session_id} endpoint.",
    }


# ============= ADVANCED ANALYTICS ENDPOINTS =============


@router.post("/analyze/capabilities", tags=["Advanced Analytics"])
async def analyze_data_capabilities(
    session_id: str = Form(...),
):
    """
    Analyze uploaded sales data to determine available analytics capabilities.

    This endpoint detects what columns are present in the data and returns
    a list of analytics features that can be performed.

    **Returns:**
    - Available capabilities (hourly demand, margin analysis, etc.)
    - Missing columns for advanced features
    - Data quality score
    - Recommendations to unlock more features
    """
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]
    sales_data = session.get("sales_data", [])

    if not sales_data:
        return {
            "session_id": session_id,
            "available_capabilities": ["bcg_analysis"],
            "missing_for_advanced": {
                "all_features": ["Upload sales CSV data to unlock advanced analytics"]
            },
            "data_quality_score": 0,
            "recommendations": [
                "📊 Upload a sales CSV file to enable demand prediction",
                "💰 Include cost data for margin analysis",
                "⏰ Include datetime for hourly patterns",
            ],
        }

    # Convert to DataFrame
    df = pd.DataFrame(sales_data)

    # Analyze capabilities
    report = data_capability_detector.analyze(df)

    # Store capability report in session
    session["capability_report"] = {
        "available": [cap.value for cap in report.available_capabilities],
        "column_mapping": {
            "date_col": report.column_mapping.date_col,
            "time_col": report.column_mapping.time_col,
            "datetime_col": report.column_mapping.datetime_col,
            "item_name_col": report.column_mapping.item_name_col,
            "quantity_col": report.column_mapping.quantity_col,
            "revenue_col": report.column_mapping.revenue_col,
            "cost_col": report.column_mapping.cost_col,
            "category_col": report.column_mapping.category_col,
        },
    }

    return {
        "session_id": session_id,
        "available_capabilities": [cap.value for cap in report.available_capabilities],
        "missing_for_advanced": report.missing_for_advanced,
        "data_quality_score": report.data_quality_score,
        "row_count": report.row_count,
        "date_range_days": report.date_range_days,
        "unique_items": report.unique_items,
        "unique_categories": report.unique_categories,
        "recommendations": report.recommendations,
        "detected_at": report.detected_at,
    }


@router.post("/analyze/menu-optimization", tags=["Advanced Analytics"])
async def run_menu_optimization(
    session_id: str = Form(...),
):
    """
    Run AI-powered menu optimization analysis.

    Analyzes price, margin, and rotation to provide actionable recommendations:
    - Items to increase/decrease price
    - Items to promote or remove
    - Quick wins for immediate impact
    - Revenue opportunity estimation

    **Requires:** Sales data with item_name and revenue columns.
    **Enhanced by:** Cost data for margin analysis.
    """
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]
    sales_data = session.get("sales_data", [])
    menu_items = session.get("menu_items", [])
    bcg_results = session.get("bcg_analysis", {})

    if not sales_data:
        raise HTTPException(400, "No sales data available. Upload sales CSV first.")

    # Get column mapping from capability report or use defaults
    cap_report = session.get("capability_report", {})
    column_mapping = cap_report.get(
        "column_mapping",
        {
            "item_name": "item_name",
            "quantity": "quantity",
            "revenue": "revenue",
            "cost": "cost",
            "category": "category",
            "date": "date",
        },
    )

    # Convert to DataFrame
    df = pd.DataFrame(sales_data)

    try:
        # Run optimization
        report = await menu_optimizer.analyze(
            sales_df=df,
            menu_items=menu_items,
            session_id=session_id,
            column_mapping=column_mapping,
            bcg_results=bcg_results,
        )

        # Store in session
        session["menu_optimization"] = {
            "generated_at": report.generated_at,
            "quick_wins": report.quick_wins,
            "items_to_promote": report.items_to_promote,
            "items_to_remove": report.items_to_remove,
            "price_adjustments": report.price_adjustments,
        }

        # Convert dataclass to dict for JSON response
        return {
            "session_id": report.session_id,
            "generated_at": report.generated_at,
            "item_optimizations": [
                {
                    "item_name": opt.item_name,
                    "current_price": opt.current_price,
                    "suggested_price": opt.suggested_price,
                    "current_margin": opt.current_margin,
                    "action": opt.action.value,
                    "priority": opt.priority.value,
                    "reasoning": opt.reasoning,
                    "expected_impact": opt.expected_impact,
                    "rotation_score": opt.rotation_score,
                    "margin_score": opt.margin_score,
                    "combined_score": opt.combined_score,
                    "bcg_category": opt.bcg_category,
                }
                for opt in report.item_optimizations
            ],
            "category_summaries": [
                {
                    "category": cat.category,
                    "item_count": cat.item_count,
                    "avg_margin": cat.avg_margin,
                    "avg_rotation": cat.avg_rotation,
                    "total_revenue": cat.total_revenue,
                    "recommendations": cat.recommendations,
                }
                for cat in report.category_summaries
            ],
            "quick_wins": report.quick_wins,
            "revenue_opportunity": report.revenue_opportunity,
            "margin_improvement_potential": report.margin_improvement_potential,
            "items_to_promote": report.items_to_promote,
            "items_to_review": report.items_to_review,
            "items_to_remove": report.items_to_remove,
            "price_adjustments": report.price_adjustments,
            "ai_insights": report.ai_insights,
            "thought_process": report.thought_process,
        }

    except Exception as e:
        logger.error(f"Menu optimization error: {e}")
        raise HTTPException(500, f"Optimization failed: {str(e)}")


@router.post("/analyze/advanced", tags=["Advanced Analytics"])
async def run_advanced_analytics(
    session_id: str = Form(...),
    capabilities: Optional[str] = Form(None),
):
    """
    Run advanced analytics based on available data capabilities.

    Provides:
    - **Hourly demand patterns** (if time data available)
    - **Daily patterns** (if date data available)
    - **Seasonal trends** (if 60+ days of data)
    - **Product analytics** (sales trends, performance)
    - **Category analytics** (if category data available)
    - **Demand forecast** (7-day prediction)

    **Parameters:**
    - session_id: Session with uploaded data
    - capabilities: Optional comma-separated list of specific capabilities to run
    """
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]
    sales_data = session.get("sales_data", [])

    if not sales_data:
        raise HTTPException(400, "No sales data available. Upload sales CSV first.")

    # Convert to DataFrame
    df = pd.DataFrame(sales_data)

    # Get capabilities from request or detect automatically
    if capabilities:
        caps_list = [c.strip() for c in capabilities.split(",")]
    else:
        # Detect capabilities
        cap_report = data_capability_detector.analyze(df)
        caps_list = [cap.value for cap in cap_report.available_capabilities]

        # Store column mapping
        session["capability_report"] = {
            "available": caps_list,
            "column_mapping": {
                "date_col": cap_report.column_mapping.date_col,
                "time_col": cap_report.column_mapping.time_col,
                "datetime_col": cap_report.column_mapping.datetime_col,
                "item_name_col": cap_report.column_mapping.item_name_col,
                "quantity_col": cap_report.column_mapping.quantity_col,
                "revenue_col": cap_report.column_mapping.revenue_col,
                "cost_col": cap_report.column_mapping.cost_col,
                "category_col": cap_report.column_mapping.category_col,
                "hour_col": cap_report.column_mapping.hour_col,
            },
        }

    # Get column mapping
    cap_data = session.get("capability_report", {})
    column_mapping = cap_data.get("column_mapping", {})

    try:
        # Run advanced analytics
        report = await advanced_analytics.analyze(
            df=df,
            session_id=session_id,
            column_mapping=column_mapping,
            capabilities=caps_list,
        )

        # Store in session
        session["advanced_analytics"] = {
            "generated_at": report.generated_at,
            "capabilities_used": report.capabilities_used,
            "key_insights": report.key_insights,
        }

        # Convert to JSON-serializable format
        return {
            "session_id": report.session_id,
            "generated_at": report.generated_at,
            "capabilities_used": report.capabilities_used,
            "hourly_patterns": [
                {
                    "hour": p.hour,
                    "avg_quantity": p.avg_quantity,
                    "avg_revenue": p.avg_revenue,
                    "peak_indicator": p.peak_indicator,
                    "staffing_recommendation": p.staffing_recommendation,
                }
                for p in report.hourly_patterns
            ],
            "daily_patterns": [
                {
                    "day_of_week": p.day_of_week,
                    "day_name": p.day_name,
                    "avg_quantity": p.avg_quantity,
                    "avg_revenue": p.avg_revenue,
                    "avg_tickets": p.avg_tickets,
                    "is_peak_day": p.is_peak_day,
                }
                for p in report.daily_patterns
            ],
            "seasonal_trends": [
                {
                    "season_type": t.season_type.value,
                    "pattern_description": t.pattern_description,
                    "peak_periods": t.peak_periods,
                    "low_periods": t.low_periods,
                    "variance_pct": t.variance_pct,
                }
                for t in report.seasonal_trends
            ],
            "product_analytics": [
                {
                    "item_name": p.item_name,
                    "total_quantity": p.total_quantity,
                    "total_revenue": p.total_revenue,
                    "avg_daily_sales": p.avg_daily_sales,
                    "sales_trend": p.sales_trend,
                    "trend_pct": p.trend_pct,
                    "category": p.category,
                }
                for p in report.product_analytics[:20]  # Top 20 items
            ],
            "category_analytics": [
                {
                    "category": c.category,
                    "item_count": c.item_count,
                    "total_revenue": c.total_revenue,
                    "revenue_share": c.revenue_share,
                    "top_performer": c.top_performer,
                    "worst_performer": c.worst_performer,
                }
                for c in report.category_analytics
            ],
            "demand_forecast": [
                {
                    "period": f.period,
                    "predicted_quantity": f.predicted_quantity,
                    "predicted_revenue": f.predicted_revenue,
                    "confidence_lower": f.confidence_lower,
                    "confidence_upper": f.confidence_upper,
                    "factors": f.factors,
                }
                for f in report.demand_forecast
            ],
            "key_insights": report.key_insights,
            "recommendations": report.recommendations,
            "data_quality_notes": report.data_quality_notes,
        }

    except Exception as e:
        logger.error(f"Advanced analytics error: {e}")
        raise HTTPException(500, f"Analytics failed: {str(e)}")


# ============= AI CHAT ENDPOINT =============


@router.post("/chat", tags=["AI Chat"])
async def chat_with_ai(
    session_id: str = Form(...),
    message: str = Form(...),
    context: str = Form("general"),
):
    """
    Interactive chat with Gemini AI about the restaurant analysis.

    The AI has full context of:
    - Menu items and categories
    - BCG analysis results
    - Sales predictions
    - Campaign recommendations

    **Parameters:**
    - session_id: Current analysis session
    - message: User's question or request
    - context: Context hint (general, bcg, predictions, campaigns)
    """
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]

    # Build context from session data
    session_context = f"""
You are MenuPilot AI, an expert restaurant business consultant powered by Gemini 3.
You are helping analyze a restaurant with the following data:

MENU ITEMS: {len(session.get('menu_items', []))} products
Categories: {', '.join(session.get('categories', ['Unknown']))}

BCG ANALYSIS:
{_format_bcg_for_chat(session.get('bcg_analysis', {}))}

CURRENT CONTEXT: {context}

Be helpful, specific, and actionable in your responses.
Use the data available to give concrete recommendations.
Keep responses concise but informative.
"""

    try:
        # Use Gemini agent for chat
        response = await agent.generate_response(
            prompt=f"{session_context}\n\nUser Question: {message}",
            system_instruction="You are a friendly restaurant business consultant. Provide clear, actionable advice based on the data.",
        )

        return {"response": response, "session_id": session_id, "context": context}

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "session_id": session_id,
            "error": str(e),
        }


def _format_bcg_for_chat(bcg_data: dict) -> str:
    """Format BCG data for chat context."""
    if not bcg_data:
        return "No BCG analysis available yet."

    summary = bcg_data.get("summary", {})
    counts = summary.get("counts", {})

    return f"""
- Stars (high growth, high share): {counts.get('star', 0)} items
- Cash Cows (low growth, high share): {counts.get('cash_cow', 0)} items
- Question Marks (high growth, low share): {counts.get('question_mark', 0)} items
- Dogs (low growth, low share): {counts.get('dog', 0)} items
- Portfolio Health Score: {summary.get('portfolio_health_score', 0):.0%}
"""


# ============= LOCATION ENDPOINTS =============


@router.post("/location/search", tags=["Location"])
async def search_location(
    query: str = Form(...),
):
    """
    Search for a restaurant location using address or name.

    Returns coordinates and formatted address for mapping.
    Uses Nominatim (OpenStreetMap) as free fallback if no Google API key.
    """
    import httpx

    google_api_key = settings.google_maps_api_key

    # Try Google Maps first if API key available
    if google_api_key:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={"address": query, "key": google_api_key},
                )
                data = response.json()

                if data.get("results"):
                    result = data["results"][0]
                    location = result["geometry"]["location"]

                    return {
                        "location": {
                            "lat": location["lat"],
                            "lng": location["lng"],
                            "address": result["formatted_address"],
                            "place_id": result.get("place_id"),
                        },
                        "status": "ok",
                    }
        except Exception as e:
            logger.warning(f"Google geocoding failed, trying Nominatim: {e}")

    # Fallback to Nominatim (OpenStreetMap) - FREE, no API key required
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                },
                headers={"User-Agent": "MenuPilot/1.0"},
                timeout=10.0,
            )
            data = response.json()

            if data and len(data) > 0:
                result = data[0]
                return {
                    "location": {
                        "lat": float(result["lat"]),
                        "lng": float(result["lon"]),
                        "address": result.get("display_name", query),
                        "place_id": f"osm_{result.get('osm_id', 'unknown')}",
                    },
                    "status": "ok",
                }

            raise HTTPException(404, f"Location not found for: {query}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Location search error: {e}")
        raise HTTPException(500, f"Location search failed: {str(e)}")


@router.post("/location/nearby-restaurants", tags=["Location"])
async def get_nearby_restaurants(
    lat: float = Form(...),
    lng: float = Form(...),
    radius: int = Form(1500),
):
    """
    Find nearby restaurants (competitors) within radius.

    Uses Google Places API to find restaurants near the specified location.

    **Parameters:**
    - lat, lng: Coordinates of the restaurant
    - radius: Search radius in meters (default 1500m)
    """
    import httpx

    google_api_key = settings.google_maps_api_key

    if not google_api_key:
        # Return mock competitors for demo
        return {
            "restaurants": [
                {
                    "name": "El Rincón Mexicano",
                    "address": "Calle Ejemplo 123",
                    "rating": 4.5,
                    "userRatingsTotal": 234,
                    "placeId": "demo_1",
                    "distance": "200m",
                },
                {
                    "name": "Taquería Los Amigos",
                    "address": "Av. Principal 456",
                    "rating": 4.2,
                    "userRatingsTotal": 156,
                    "placeId": "demo_2",
                    "distance": "450m",
                },
                {
                    "name": "Restaurant La Casona",
                    "address": "Plaza Central 789",
                    "rating": 4.7,
                    "userRatingsTotal": 312,
                    "placeId": "demo_3",
                    "distance": "800m",
                },
            ],
            "status": "demo_mode",
        }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                params={
                    "location": f"{lat},{lng}",
                    "radius": radius,
                    "type": "restaurant",
                    "key": google_api_key,
                },
            )
            data = response.json()

            restaurants = []
            for place in data.get("results", [])[:10]:
                restaurants.append(
                    {
                        "name": place.get("name"),
                        "address": place.get("vicinity"),
                        "rating": place.get("rating"),
                        "userRatingsTotal": place.get("user_ratings_total"),
                        "placeId": place.get("place_id"),
                        "types": place.get("types", []),
                    }
                )

            return {"restaurants": restaurants, "status": "ok"}

    except Exception as e:
        logger.error(f"Nearby search error: {e}")
        return {"restaurants": [], "status": "error", "message": str(e)}


# ============= FEEDBACK ENDPOINT =============


@router.post("/analyze/feedback", tags=["Advanced Analytics"])
async def generate_feedback(
    session_id: str = Form(...),
):
    """
    Generate comprehensive AI feedback and recommendations for the restaurant.

    Analyzes all available data to provide:
    - Overall business health score
    - Key strengths and weaknesses
    - Prioritized action items
    - Revenue opportunities
    - Competitive positioning advice
    """
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    session = sessions[session_id]

    # Gather all session data for analysis
    menu_items = session.get("menu_items", [])
    bcg_analysis = session.get("bcg_analysis", {})
    campaigns = session.get("campaigns", [])
    predictions = session.get("predictions", {})
    location_data = session.get("location", {})
    competitors = session.get("competitors", [])

    # Calculate overall score based on available data
    score = 50  # Base score
    health_status = "needs_attention"

    # Adjust score based on BCG portfolio
    if bcg_analysis:
        summary = bcg_analysis.get("summary", {})
        portfolio_health = summary.get("portfolio_health_score", 0.5)
        score += int(portfolio_health * 30)

        counts = summary.get("counts", {})
        stars = counts.get("star", 0)
        dogs = counts.get("dog", 0)

        if stars >= 3 and dogs <= 2:
            health_status = "excellent"
            score += 10
        elif stars >= 2:
            health_status = "good"
            score += 5
        elif dogs >= 4:
            health_status = "critical"
            score -= 10

    # Cap score
    score = max(20, min(95, score))

    # Generate strengths based on data
    strengths = []
    if bcg_analysis:
        counts = bcg_analysis.get("summary", {}).get("counts", {})
        if counts.get("star", 0) > 0:
            strengths.append(f"You have {counts['star']} Star products driving growth")
        if counts.get("cash_cow", 0) > 0:
            strengths.append(f"{counts['cash_cow']} Cash Cows providing stable revenue")

    if len(menu_items) >= 10:
        strengths.append("Good menu diversity with multiple offerings")
    if campaigns:
        strengths.append("Marketing campaigns ready for execution")

    if not strengths:
        strengths = [
            "Data uploaded and ready for analysis",
            "Using AI-powered optimization",
        ]

    # Generate improvement areas
    improvements = []
    if bcg_analysis:
        counts = bcg_analysis.get("summary", {}).get("counts", {})
        if counts.get("dog", 0) > 2:
            improvements.append(
                f"Review {counts['dog']} underperforming products (Dogs)"
            )
        if counts.get("question_mark", 0) > 2:
            improvements.append(
                f"Make decisions on {counts['question_mark']} Question Mark items"
            )

    if not location_data:
        improvements.append("Add location data for competitive analysis")
    if len(menu_items) < 5:
        improvements.append("Upload more menu items for comprehensive analysis")

    if not improvements:
        improvements = [
            "Continue monitoring performance metrics",
            "Test new menu items periodically",
        ]

    # Generate actions
    actions = [
        {
            "action": "Review and optimize prices for Star products",
            "impact": "high",
            "effort": "easy",
        },
        {
            "action": "Run promotional campaign for Question Mark items",
            "impact": "medium",
            "effort": "moderate",
        },
        {
            "action": "Consider removing or rebranding Dog products",
            "impact": "medium",
            "effort": "moderate",
        },
    ]

    # Revenue opportunities
    revenue_opps = [
        {"description": "Optimize Star product pricing", "potential": "+5-10% revenue"},
        {
            "description": "Promote underperforming items",
            "potential": "+3-7% sales volume",
        },
        {
            "description": "Bundle complementary items",
            "potential": "+8-15% ticket size",
        },
    ]

    # AI recommendation
    ai_recommendation = (
        f"Based on the analysis, your restaurant has a health score of {score}/100. "
    )
    if health_status == "excellent":
        ai_recommendation += "Your portfolio is well-balanced. Focus on maintaining Stars and maximizing Cash Cows."
    elif health_status == "good":
        ai_recommendation += (
            "Good foundation! Invest in Question Marks and optimize underperformers."
        )
    elif health_status == "needs_attention":
        ai_recommendation += (
            "Focus on identifying clear winners and phasing out underperformers."
        )
    else:
        ai_recommendation += (
            "Urgent action needed. Prioritize menu restructuring and cost optimization."
        )

    return {
        "overall_score": score,
        "health_status": health_status,
        "key_strengths": strengths,
        "areas_for_improvement": improvements,
        "immediate_actions": actions,
        "revenue_opportunities": revenue_opps,
        "competitive_position": "Analysis shows opportunities to differentiate through menu optimization and targeted marketing.",
        "ai_recommendation": ai_recommendation,
    }
