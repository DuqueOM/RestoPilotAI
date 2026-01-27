"""
API Routes for MenuPilot.

Provides endpoints for:
- /ingest: Upload menu images and sales data
- /analyze: Run BCG analysis and generate product profiles
- /predict: Sales prediction for scenarios
- /campaigns: Generate marketing campaign proposals
"""

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import get_settings
from app.services.bcg_classifier import BCGClassifier
from app.services.campaign_generator import CampaignGenerator
from app.services.gemini_agent import GeminiAgent
from app.services.menu_extractor import DishImageAnalyzer, MenuExtractor
from app.services.sales_predictor import SalesPredictor

router = APIRouter()
settings = get_settings()

# Initialize services
agent = GeminiAgent()
menu_extractor = MenuExtractor(agent)
dish_analyzer = DishImageAnalyzer(agent)
bcg_classifier = BCGClassifier(agent)
sales_predictor = SalesPredictor()
campaign_generator = CampaignGenerator(agent)

# In-memory session storage (use Redis/DB in production)
sessions = {}


@router.post("/ingest/menu", tags=["Ingest"])
async def ingest_menu_image(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    business_context: Optional[str] = Form(None),
):
    """
    Upload and process a menu image.

    Extracts menu items using OCR and Gemini multimodal analysis.
    """

    # Validate file
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in settings.allowed_image_ext_list:
        raise HTTPException(
            400, f"Invalid file type. Allowed: {settings.allowed_image_extensions}"
        )

    # Create or get session
    session_id = session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = {
            "created_at": datetime.utcnow().isoformat(),
            "menu_items": [],
            "sales_data": [],
        }

    # Save file
    upload_dir = Path("data/uploads") / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"menu_{file.filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract menu items
    try:
        result = await menu_extractor.extract_from_image(
            str(file_path), use_ocr=True, business_context=business_context
        )

        # Store in session
        sessions[session_id]["menu_items"].extend(result["items"])
        sessions[session_id]["menu_extraction"] = result

        # Create thought signature
        thought = await agent.create_thought_signature(
            "Extract menu items from uploaded image",
            {"filename": file.filename, "items_found": len(result["items"])},
        )

        return {
            "session_id": session_id,
            "status": "success",
            "items_extracted": len(result["items"]),
            "categories_found": [c["name"] for c in result["categories"]],
            "items": result["items"],
            "extraction_confidence": result["extraction_confidence"],
            "thought_process": thought,
            "warnings": result["warnings"],
        }

    except Exception as e:
        logger.error(f"Menu extraction failed: {e}")
        raise HTTPException(500, f"Menu extraction failed: {str(e)}")


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


@router.post("/ingest/sales", tags=["Ingest"])
async def ingest_sales_data(file: UploadFile = File(...), session_id: str = Form(...)):
    """
    Upload sales data CSV.

    Expected columns: date, item_name, units_sold, [revenue], [had_promotion], [promotion_discount]
    """

    if session_id not in sessions:
        raise HTTPException(404, "Session not found. Upload menu first.")

    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ["csv", "xlsx"]:
        raise HTTPException(400, "Invalid file type. Use CSV or XLSX.")

    # Save and parse file
    upload_dir = Path("data/uploads") / session_id
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

    if not menu_items:
        raise HTTPException(400, "No menu items found. Upload menu first.")

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
        "generated_at": datetime.utcnow().isoformat(),
        "menu_catalog": session.get("menu_items", []),
        "bcg_analysis": session.get("bcg_analysis"),
        "predictions": session.get("predictions"),
        "campaigns": session.get("campaigns", []),
        "gemini_usage": agent.get_stats(),
    }

    return JSONResponse(content=report, media_type="application/json")
