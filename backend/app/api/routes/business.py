import asyncio
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import pandas as pd
from app.api.deps import load_session, save_session, sessions
from app.core.config import get_settings
from app.services.analysis.menu_analyzer import DishImageAnalyzer, MenuExtractor
from app.services.analysis.period_calculator import PeriodCalculator
from app.services.gemini.base_agent import GeminiAgent
from app.services.intelligence.data_enrichment import CompetitorEnrichmentService
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response
from loguru import logger

# Initialize router
router = APIRouter()
settings = get_settings()

# Initialize services
agent = GeminiAgent()
menu_extractor = MenuExtractor(agent)
dish_analyzer = DishImageAnalyzer(agent)

# ============================================================================
# INGESTION ENDPOINTS
# ============================================================================


@router.post("/ingest/menu", tags=["Ingest"])
async def ingest_menu_image(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    business_context: Optional[str] = Form(None),
):
    """
    Upload and process menu images/PDFs (supports multiple files).
    """
    from app.services.orchestrator import orchestrator

    # Create or get session using orchestrator to ensure state compatibility
    if not session_id or not load_session(session_id):
        session_id = await orchestrator.create_session()
        # Initialize business session in deps store (orchestrator saves to its own dir)
        sessions[session_id] = {
            "session_id": session_id,
            "menu_items": [],
            "menu_extraction": None,
            "sales_data": None,
            "restaurant_info": {},
            "competitors": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        save_session(session_id)

    session = load_session(session_id)
    if not session:
        raise HTTPException(500, "Failed to create or load session")

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

    # Calculate categories from new items
    categories = list(set(item.get("category", "Other") for item in new_items))

    result = {"items": new_items, "item_count": len(new_items), "categories": categories}
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
        "categories": categories,
        "thought_process": thought,
    }


@router.post("/ingest/dishes", tags=["Ingest"])
async def ingest_dish_images(
    files: List[UploadFile] = File(...), session_id: str = Form(...)
):
    """
    Upload and analyze dish photographs and videos.
    """
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found. Upload menu first.")

    upload_dir = Path("data/uploads") / session_id / "dishes"
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_image_paths = []
    saved_video_paths = []

    # Extended media types
    allowed_images = settings.allowed_image_ext_list
    allowed_videos = ["mp4", "webm", "mov", "avi", "mkv"]

    for file in files:
        ext = file.filename.split(".")[-1].lower() if file.filename else ""

        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if ext in allowed_images:
            saved_image_paths.append(str(file_path))
            logger.info(f"Saved image: {file.filename}")
        elif ext in allowed_videos:
            saved_video_paths.append(str(file_path))
            logger.info(f"Saved video: {file.filename}")

    if not saved_image_paths and not saved_video_paths:
        raise HTTPException(400, "No valid images or videos uploaded")

    # Analyze dishes (images and videos)
    try:
        menu_item_names = [
            item["name"] for item in sessions[session_id].get("menu_items", [])
        ]

        all_analyses = []

        # Analyze images
        if saved_image_paths:
            logger.info(
                f"Analyzing {len(saved_image_paths)} images with Gemini Vision..."
            )
            image_result = await dish_analyzer.analyze_images(
                saved_image_paths, menu_item_names
            )
            all_analyses.extend(image_result["analyses"])

        # Analyze videos (extract frames and analyze)
        if saved_video_paths:
            logger.info(
                f"Analyzing {len(saved_video_paths)} videos with Gemini Vision..."
            )
            video_result = await dish_analyzer.analyze_videos(
                saved_video_paths, menu_item_names
            )
            all_analyses.extend(video_result.get("analyses", []))

        # Calculate combined summary
        combined_summary = dish_analyzer._calculate_summary(all_analyses)

        # Store analyses
        sessions[session_id]["image_analyses"] = all_analyses
        sessions[session_id]["image_scores"] = {
            a.get("matched_menu_item", a.get("dish_name", f"dish_{i}")): a.get(
                "attractiveness_score", 0.5
            )
            for i, a in enumerate(all_analyses)
        }

        return {
            "session_id": session_id,
            "status": "success",
            "images_analyzed": len(saved_image_paths),
            "videos_analyzed": len(saved_video_paths),
            "total_media_analyzed": len(all_analyses),
            "summary": combined_summary,
            "analyses": all_analyses,
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
    """
    session = load_session(session_id)
    if not session:
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

    # Store audio path in session
    if "audio_files" not in sessions[session_id]:
        sessions[session_id]["audio_files"] = {"business": [], "competitor": []}

    sessions[session_id]["audio_files"][context_type].append(str(file_path))
    save_session(session_id)

    logger.info(f"Audio uploaded for {context_type} context: {file.filename}")

    # Process audio with Gemini multimodal
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
        prompt = f"""Analyze this audio containing information about {'the business/restaurant' if context_type == 'business' else 'the business competition'}.

Extract:
1. Key information mentioned
2. Overall tone and sentiment
3. Important points for market analysis
4. Any specific data (prices, locations, features)

Respond in JSON:
{{
    "summary": "Brief summary of the content",
    "key_points": ["point 1", "point 2"],
    "sentiment": "positive/neutral/negative",
    "market_insights": ["insight 1", "insight 2"],
    "raw_context": "Full text extracted from audio for context"
}}"""

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)

        response = client.models.generate_content(
            model="gemini-3.0-flash",
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

        response_text = response.text
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

        # Add to context
        context_key = f"{context_type}_context"
        existing_context = sessions[session_id].get(context_key, "")
        sessions[session_id][context_key] = (
            existing_context
            + "\n\n[Audio Context]:\n"
            + audio_analysis.get("raw_context", "")
        )
        save_session(session_id)

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
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    session = load_session(session_id)
    if not session:
        session = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "menu_items": [],
            "sales_data": [],
        }
        sessions[session_id] = session
        save_session(session_id)

    logger.info(f"Ingesting sales for session: {session_id}")

    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ["csv", "xlsx"]:
        raise HTTPException(400, "Invalid file type. Use CSV or XLSX.")

    upload_dir = Path("data/uploads") / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"sales.{ext}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        if ext == "csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

        required = ["date", "item_name", "units_sold"]
        missing = [c for c in required if c not in df.columns]
        if missing:
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

        def parse_date(date_val):
            if pd.isna(date_val):
                return None
            date_str = str(date_val).strip()
            formats = [
                "%d-%m-%y",
                "%d-%m-%Y",
                "%Y-%m-%d",
                "%d/%m/%y",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%Y/%m/%d",
            ]
            for fmt in formats:
                try:
                    return pd.to_datetime(date_str, format=fmt).date()
                except (ValueError, TypeError):
                    continue
            try:
                return pd.to_datetime(date_str, dayfirst=True).date()
            except Exception:
                return None

        df["date"] = df["date"].apply(parse_date)
        invalid_dates = df["date"].isna().sum()
        df = df.dropna(subset=["date"])
        df["date"] = df["date"].astype(str)

        sales_records = df.to_dict("records")
        sessions[session_id]["sales_data"] = sales_records
        save_session(session_id)

        total_units = df["units_sold"].sum()
        date_range = {"start": df["date"].min(), "end": df["date"].max()}
        unique_items = df["item_name"].nunique()

        try:
            start_dt = pd.to_datetime(date_range["start"])
            end_dt = pd.to_datetime(date_range["end"])
            days_span = (end_dt - start_dt).days + 1
        except Exception:
            days_span = 0

        warnings = []
        if invalid_dates > 0:
            warnings.append(f"{invalid_dates} rows had invalid dates and were skipped")
        if days_span < 30:
            warnings.append(f"Only {days_span} days of data. Recommend 30-90 days.")
        if len(sales_records) < 100:
            warnings.append(
                f"Only {len(sales_records)} records. More data improves accuracy."
            )

        available_columns = list(df.columns)
        has_price = "price" in df.columns
        has_cost = "cost" in df.columns
        has_category = "categoria" in df.columns or "category" in df.columns

        thought = await agent.create_thought_signature(
            "Process uploaded sales data",
            {"records": len(sales_records), "date_range": date_range},
        )

        return {
            "session_id": session_id,
            "status": "success",
            "records_imported": len(sales_records),
            "date_range": date_range,
            "days_span": days_span,
            "unique_items": unique_items,
            "total_units": int(total_units),
            "total_revenue": (
                float(df["revenue"].sum()) if "revenue" in df.columns else None
            ),
            "available_columns": available_columns,
            "data_capabilities": {
                "has_price": has_price,
                "has_cost": has_cost,
                "has_category": has_category,
                "can_calculate_margin": has_price and has_cost,
            },
            "thought_process": thought,
            "warnings": warnings,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sales data processing failed: {e}")
        raise HTTPException(500, f"Sales data processing failed: {str(e)}")


# ============================================================================
# SESSION ENDPOINTS
# ============================================================================


@router.get("/demo/session", tags=["Demo"])
async def get_demo_session():
    """Get pre-loaded demo session data."""
    demo_file = Path("data/demo/session.json")
    if not demo_file.exists():
        raise HTTPException(
            404, "Demo data not found. Run scripts/seed_demo_data.py first."
        )

    with open(demo_file, "r") as f:
        demo_data = json.load(f)

    session_id = demo_data.get("session_id", "demo-session-001")
    
    sessions[session_id] = {
        "menu_items": demo_data["menu"]["items"],
        "bcg_analysis": demo_data["bcg"],
        "campaigns": demo_data["campaigns"]["campaigns"],
        "predictions": demo_data.get("predictions"),
        "competitor_analysis": demo_data.get("competitor_analysis"),
        "sentiment_analysis": demo_data.get("sentiment_analysis"),
        "thought_signature": demo_data.get("thought_signature"),
        "marathon_agent_context": demo_data.get("marathon_agent_context"),
        "restaurant_info": demo_data.get("restaurant_info"),
        "created_at": demo_data.get("created_at")
    }
    
    # Ensure sales data is loaded if available
    sales_file = Path("data/demo/sales.json")
    if sales_file.exists():
        with open(sales_file, "r") as f:
            sessions[session_id]["sales_data"] = json.load(f)
            
    save_session(session_id)

    campaigns_data = demo_data.get("campaigns", {})
    if isinstance(campaigns_data, dict) and "campaigns" in campaigns_data:
        campaigns_result = campaigns_data
    else:
        campaigns_result = {
            "campaigns": campaigns_data,
            "thought_process": "Demo campaign generation",
        }

    return {
        "session_id": session_id,
        "status": demo_data["status"],
        "created_at": demo_data["created_at"],
        "menu": demo_data["menu"],
        "bcg": demo_data["bcg"],
        "bcg_analysis": demo_data["bcg"],
        "campaigns": campaigns_result,
        "predictions": demo_data.get("predictions"),
        "competitor_analysis": demo_data.get("competitor_analysis"),
        "sentiment_analysis": demo_data.get("sentiment_analysis"),
        "thought_signature": demo_data.get("thought_signature"),
        "marathon_agent_context": demo_data.get("marathon_agent_context"),
        "restaurant_info": demo_data.get("restaurant_info"),
    }


@router.get("/demo/load", tags=["Demo"])
async def load_demo_into_session():
    """Load demo data into a new session for testing."""
    demo_file = Path("data/demo/session.json")
    if not demo_file.exists():
        raise HTTPException(
            404, "Demo data not found. Run scripts/seed_demo_data.py first."
        )

    with open(demo_file, "r") as f:
        demo_data = json.load(f)

    session_id = demo_data.get("session_id", "demo-session-001")
    
    # Clear any stale orchestrator state that could override demo data
    try:
        from app.services.orchestrator import orchestrator
        orchestrator.active_sessions.pop(session_id, None)
        orchestrator.completed_sessions.pop(session_id, None)
        orch_file = Path(f"data/orchestrator_states/{session_id}.json")
        if orch_file.exists():
            orch_file.unlink()
        logger.info(f"Cleared stale orchestrator state for demo session {session_id}")
    except Exception as e:
        logger.warning(f"Could not clear orchestrator state: {e}")
    
    sessions[session_id] = {
        "menu_items": demo_data["menu"]["items"],
        "categories": demo_data["menu"]["categories"],
        "bcg_analysis": demo_data["bcg"],
        "campaigns": demo_data["campaigns"]["campaigns"],
        "competitor_analysis": demo_data.get("competitor_analysis"),
        "sentiment_analysis": demo_data.get("sentiment_analysis"),
        "predictions": demo_data.get("predictions"),
        "created_at": demo_data["created_at"],
        "restaurant_info": demo_data.get("restaurant_info"),
        "status": "completed",
    }
    
    # Ensure sales data is loaded
    sales_file = Path("data/demo/sales.json")
    if sales_file.exists():
        with open(sales_file, "r") as f:
            sessions[session_id]["sales_data"] = json.load(f)
            
    save_session(session_id)

    return {
        "session_id": session_id,
        "status": "loaded",
        "items_count": len(demo_data["menu"]["items"]),
        "restaurant": demo_data.get("restaurant_info", {}).get("name"),
        "message": "Demo session loaded. Use this session_id with /session/{session_id} endpoint.",
    }


@router.get("/session/{session_id}", tags=["Session"])
async def get_session(session_id: str):
    """Get full session data including all analysis results."""
    from app.services.orchestrator import orchestrator
    
    # 1. Try loading legacy/business session (from data/sessions)
    session = load_session(session_id) or {}
    
    # 2. Check Orchestrator state (from memory or data/orchestrator_states)
    orch_state = orchestrator.get_session_status(session_id)
    
    if not session and not orch_state:
        raise HTTPException(404, "Session not found")

    # 3. Merge Orchestrator results into session (Orchestrator takes precedence for analysis)
    if orch_state:
        # Ensure we have the basic fields if session was empty
        if not session:
            session = {
                "session_id": session_id,
                "created_at": orch_state.get("started_at"),
                "status": orch_state.get("status"),
                "menu_items": [], 
                "sales_data": [],
            }
        
        # Update status and timestamps
        if orch_state.get("status"):
            session["status"] = orch_state.get("status")
        
        # Merge analysis results (only override if orchestrator data is substantive)
        analysis_keys = [
            "bcg_analysis", 
            "competitor_analysis", 
            "sentiment_analysis", 
            "predictions", 
            "campaigns", 
            "verification",
            "vibe_status"
        ]
        
        for key in analysis_keys:
            orch_val = orch_state.get(key)
            if not orch_val:
                continue
            # For BCG: only override if orchestrator has actual items/classifications
            if key == "bcg_analysis" and isinstance(orch_val, dict):
                has_items = len(orch_val.get("items", [])) > 0 or len(orch_val.get("classifications", [])) > 0
                if not has_items and session.get(key):
                    continue  # Keep existing session data (e.g. demo data)
            session[key] = orch_val
                
        # Embed full orchestrator state for debug/advanced usage
        session["data"] = orch_state

    sales_data = session.get("sales_data", [])
    
    # Safe period calculation
    try:
        period_calc = PeriodCalculator()
        available_periods_info = period_calc.calculate_available_periods(sales_data)
    except Exception as e:
        logger.error(f"Error calculating periods for session {session_id}: {e}")
        available_periods_info = {}

    # Extract analysis results to top level for frontend compatibility
    # Prioritize the merged values in 'session'
    bcg = session.get("bcg_analysis")
    competitor = session.get("competitor_analysis")
    sentiment = session.get("sentiment_analysis")
    predictions = session.get("predictions")
    campaigns = session.get("campaigns")

    return {
        "session_id": session_id,
        "created_at": session.get("created_at"),
        "status": session.get("status", "unknown"),
        "menu_items_count": len(session.get("menu_items", [])),
        "sales_records_count": len(sales_data),
        "has_bcg_analysis": bool(bcg),
        "has_predictions": bool(predictions),
        "campaigns_count": len(campaigns) if isinstance(campaigns, list) else len(campaigns.get("campaigns", [])) if isinstance(campaigns, dict) else 0,
        "available_periods": available_periods_info,
        
        # Flattened analysis results
        "bcg_analysis": bcg,
        "competitor_analysis": competitor,
        "sentiment_analysis": sentiment,
        "predictions": predictions,
        "campaigns": campaigns,
        
        # Business info and enrichment
        "restaurant_info": session.get("restaurant_info"),
        "business_context": session.get("business_context"),
        "business_profile_enriched": session.get("business_profile_enriched"),
        "competitors": session.get("competitors", []),
        "enriched_competitors": session.get("enriched_competitors", []),
        
        # Keep full data for debug/advanced usage
        "data": session,
    }


@router.get("/session/{session_id}/export", tags=["Session"])
async def export_session(session_id: str, format: str = "json"):
    """Export full analysis results as downloadable file."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    bcg_data = session.get("bcg_analysis") or session.get("menu_engineering", {})

    report = {
        "export_info": {
            "session_id": session_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "export_format": format,
            "RestoPilotAI_version": "1.0.0",
        },
        "data_summary": {
            "menu_items_count": len(session.get("menu_items", [])),
            "sales_records_count": len(session.get("sales_data", [])),
            "analysis_period": bcg_data.get("period", "unknown"),
            "date_range": bcg_data.get("date_range", {}),
        },
        "menu_catalog": session.get("menu_items", []),
        "sales_data_sample": session.get("sales_data", [])[:100],
        "bcg_analysis": {
            "methodology": bcg_data.get("methodology", "Menu Engineering"),
            "period": bcg_data.get("period"),
            "date_range": bcg_data.get("date_range"),
            "total_records_analyzed": bcg_data.get("total_records", 0),
            "items_analyzed": bcg_data.get("items_analyzed", 0),
            "thresholds": bcg_data.get("thresholds", {}),
            "summary": bcg_data.get("summary", {}),
            "classifications": bcg_data.get(
                "items", bcg_data.get("classifications", [])
            ),
        },
        "predictions": session.get("predictions", {}),
        "campaigns": session.get("campaigns", []),
        "location": session.get("location", {}),
        "competitors": session.get("competitors", []),
        "image_analyses": session.get("image_analyses", []),
        "audio_analysis": session.get("audio_analysis", {}),
        "business_context": session.get("business_context", ""),
        "competitor_context": session.get("competitor_context", ""),
        "thought_signatures": session.get("thought_signatures", []),
        "gemini_usage": agent.get_stats() if hasattr(agent, "get_stats") else {},
    }

    if format == "json":
        response = Response(
            content=json.dumps(report, indent=2, ensure_ascii=False, default=str),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=RestoPilotAI_analysis_{session_id[:8]}.json"
            },
        )
        return response
    else:
        return JSONResponse(content=report)


# ============================================================================
# LOCATION ENDPOINTS
# ============================================================================


@router.post("/location/search", tags=["Location"])
async def search_location(query: str = Form(...)):
    """Search for a restaurant location using address or name."""
    import httpx

    logger.info(f"Location search request: '{query}'")
    google_api_key = settings.google_maps_api_key

    if google_api_key:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
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
                        "source": "google",
                    }
        except Exception as e:
            logger.warning(f"Google geocoding failed: {e}")

    # Fallback to Nominatim
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                },
                headers={"User-Agent": "RestoPilotAI/1.0"},
            )
            data = response.json()
            if data:
                result = data[0]
                return {
                    "location": {
                        "lat": float(result["lat"]),
                        "lng": float(result["lon"]),
                        "address": result.get("display_name", query),
                        "place_id": f"osm_{result.get('osm_id', 'unknown')}",
                    },
                    "status": "ok",
                    "source": "nominatim",
                }
    except Exception as e:
        logger.error(f"Location search error: {e}")
        raise HTTPException(500, f"Location search error: {str(e)}")

    raise HTTPException(404, "Location not found")


@router.post("/location/nearby-restaurants", tags=["Location"])
async def get_nearby_restaurants(
    lat: float = Form(...),
    lng: float = Form(...),
    radius: int = Form(1500),
    address: str = Form(None),
    enrich: bool = Form(False),
    session_id: Optional[str] = Form(None),
):
    """Find nearby restaurants."""
    import httpx

    google_api_key = settings.google_maps_api_key
    found_restaurants = []
    source_used = "unknown"

    if google_api_key:
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
                for place in data.get("results", [])[:10]:
                    found_restaurants.append(
                        {
                            "name": place.get("name"),
                            "address": place.get("vicinity"),
                            "rating": place.get("rating"),
                            "userRatingsTotal": place.get("user_ratings_total"),
                            "placeId": place.get("place_id"),
                            "types": place.get("types", []),
                            "location": place.get("geometry", {}).get("location", {}),
                        }
                    )
                source_used = "google_places"
        except Exception as e:
            logger.warning(f"Google Places failed: {e}")

    if not found_restaurants:
        # Fallback to Gemini
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.gemini_api_key)
            location_context = f"coordinates {lat}, {lng}"
            if address:
                location_context = f"{address} ({lat}, {lng})"

            prompt = f"""Busca restaurantes reales cerca de {location_context} en radio {radius}m.
            Responde JSON: {{ "restaurants": [{{ "name": "", "address": "", "rating": 4.5, "userRatingsTotal": 100, "placeId": "gemini_1" }}] }}"""

            response = client.models.generate_content(
                model=agent.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3,
                ),
            )

            # Simple JSON parse (robust version in original)
            try:
                import json

                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                data = json.loads(text.strip())
                found_restaurants = data.get("restaurants", [])
                source_used = "gemini_grounded"
            except Exception:
                pass
        except Exception:
            pass

    if session_id and found_restaurants:
        session = load_session(session_id)
        if session:
            sessions[session_id]["competitors"] = found_restaurants
            save_session(session_id)

    if enrich and found_restaurants:
        enrichment_service = CompetitorEnrichmentService(
            google_maps_api_key=settings.google_maps_api_key,
            gemini_agent=agent,
        )
        enriched_profiles = []
        for restaurant in found_restaurants[:5]:
            try:
                profile = await enrichment_service.enrich_competitor_profile(
                    place_id=restaurant.get("placeId") or restaurant.get("place_id"),
                    basic_info=restaurant,
                )
                enriched_profiles.append(profile.to_dict())
            except Exception:
                enriched_profiles.append({"basic_info": restaurant})

        await enrichment_service.close()

        if session_id:
            sessions[session_id]["enriched_competitors"] = enriched_profiles
            save_session(session_id)

        return {
            "restaurants": enriched_profiles,
            "status": "ok",
            "source": f"{source_used}_enriched",
            "enriched": True,
        }

    return {
        "restaurants": found_restaurants,
        "status": "ok" if found_restaurants else "no_results",
        "source": source_used,
        "enriched": False,
    }


@router.post("/location/identify-business", tags=["Location"])
async def identify_business(
    query: str = Form(...),
    lat: Optional[float] = Form(None),
    lng: Optional[float] = Form(None),
):
    """Identify a specific business in Google Maps."""
    import httpx

    google_api_key = settings.google_maps_api_key

    if not google_api_key:
        # Fallback to Gemini
        try:
            result = await agent.identify_business_from_query(
                query, location_hint=f"{lat},{lng}" if lat and lng else None
            )
            return {"status": "success", "candidates": result.get("candidates", [])}
        except Exception as e:
            raise HTTPException(500, str(e))

    try:
        logger.info(f"Using Google Maps API Key: {google_api_key[:5]}...{google_api_key[-4:] if google_api_key else 'None'}")
        
        async with httpx.AsyncClient() as client:
            params = {"query": query, "key": google_api_key, "language": "es"}
            if lat and lng:
                params["location"] = f"{lat},{lng}"
                params["radius"] = 500

            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/textsearch/json",
                params=params,
            )
            
            if response.status_code != 200:
                logger.error(f"Google Places API returned status {response.status_code}: {response.text}")
                raise HTTPException(502, f"Google Maps API error: {response.status_code} - {response.text[:200]}")

            try:
                data = response.json()
            except Exception as json_err:
                logger.error(f"Failed to parse Google API response: {response.text}")
                raise HTTPException(502, f"Invalid JSON from Google API: {str(json_err)}")
            
            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                error_msg = data.get("error_message", "Unknown Google API error")
                logger.error(f"Google Places API logic error: {data.get('status')} - {error_msg}")
                # If API is not authorized, fallback to Gemini or raise distinct error
                if data.get("status") in ["REQUEST_DENIED", "OVER_QUERY_LIMIT"]:
                     raise HTTPException(403, f"Google Maps API Error: {error_msg} (Status: {data.get('status')})")
                
            candidates = []
            
            # Process initial results
            for place in data.get("results", [])[:5]:
                loc = place.get("geometry", {}).get("location", {})
                types = place.get("types", [])
                
                # Add the direct match
                candidates.append(
                    {
                        "name": place.get("name"),
                        "address": place.get("formatted_address"),
                        "placeId": place.get("place_id"),
                        "lat": loc.get("lat"),
                        "lng": loc.get("lng"),
                        "rating": place.get("rating"),
                        "types": types,
                        "is_establishment": "establishment" in types or "point_of_interest" in types
                    }
                )

                # If the result is a generic location (address, route, locality) and not a specific business,
                # search for restaurants at this location to help the user find their business.
                generic_types = [
                    "street_address", "route", "locality", "sublocality", "postal_code", 
                    "intersection", "premise", "subpremise", "neighborhood",
                    "administrative_area_level_1", "administrative_area_level_2", "political"
                ]
                is_general_location = any(t in types for t in generic_types)
                
                # Also trigger if it's not explicitly an establishment (though premise is sometimes an establishment in G-Maps)
                # But if the name looks like an address, we should definitely look deeper.
                
                if is_general_location and loc.get("lat") and loc.get("lng"):
                    try:
                        # Search for businesses at this coordinate
                        nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                        nearby_params = {
                            "location": f"{loc['lat']},{loc['lng']}",
                            "radius": "50",  # Very tight radius to find businesses AT this address
                            "type": "restaurant", # Prioritize restaurants
                            "key": google_api_key,
                            "language": "es"
                        }
                        
                        nearby_res = await client.get(nearby_url, params=nearby_params)
                        if nearby_res.status_code == 200:
                            nearby_data = nearby_res.json()
                            for biz in nearby_data.get("results", [])[:5]:
                                # Avoid duplicates
                                if any(c["placeId"] == biz.get("place_id") for c in candidates):
                                    continue
                                    
                                biz_loc = biz.get("geometry", {}).get("location", {})
                                candidates.append({
                                    "name": biz.get("name"),
                                    "address": biz.get("vicinity"), # nearbysearch uses vicinity
                                    "placeId": biz.get("place_id"),
                                    "lat": biz_loc.get("lat"),
                                    "lng": biz_loc.get("lng"),
                                    "rating": biz.get("rating"),
                                    "types": biz.get("types", []),
                                    "is_establishment": True,
                                    "parent_address": place.get("formatted_address") # Link to the address searched
                                })
                    except Exception as nearby_err:
                        logger.warning(f"Failed to fetch businesses at address location: {nearby_err}")

            return {"status": "success", "candidates": candidates}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in identify_business")
        raise HTTPException(500, f"Internal Search Error: {repr(e)}")


@router.post("/location/set-business", tags=["Location"])
async def set_business_location(
    session_id: str = Form(...),
    place_id: str = Form(...),
    enrich_profile: bool = Form(True),
    name: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    lat: Optional[float] = Form(None),
    lng: Optional[float] = Form(None),
):
    """Set the business location."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    # If direct data provided
    if name and address and lat is not None:
        business_info = {
            "place_id": place_id,
            "name": name,
            "address": address,
            "lat": lat,
            "lng": lng,
        }
    else:
        # Google Maps API
        import httpx

        if not settings.google_maps_api_key:
            raise HTTPException(400, "API key missing")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={
                    "place_id": place_id,
                    "fields": "name,formatted_address,geometry,rating,user_ratings_total,formatted_phone_number,website",
                    "key": settings.google_maps_api_key,
                },
            )
            data = response.json()
            res = data.get("result", {})
            loc = res.get("geometry", {}).get("location", {})
            business_info = {
                "place_id": place_id,
                "name": res.get("name"),
                "address": res.get("formatted_address"),
                "lat": loc.get("lat"),
                "lng": loc.get("lng"),
                "phone": res.get("formatted_phone_number"),
                "website": res.get("website"),
            }

    sessions[session_id]["business_location"] = business_info
    sessions[session_id]["location"] = business_info
    save_session(session_id)

    if enrich_profile:
        enrichment = CompetitorEnrichmentService(
            google_maps_api_key=settings.google_maps_api_key, gemini_agent=agent
        )
        profile = await enrichment.enrich_competitor_profile(
            place_id, basic_info=business_info
        )
        await enrichment.close()
        sessions[session_id]["business_profile_enriched"] = profile.to_dict()
        save_session(session_id)

        return {
            "status": "success",
            "business": business_info,
            "enriched_profile": profile.to_dict(),
        }

    return {"status": "success", "business": business_info}


@router.post("/location/enrich-competitor", tags=["Location"])
async def enrich_competitor_profile(
    place_id: str = Form(...),
    session_id: Optional[str] = Form(None),
    business_name: Optional[str] = Form(None),
    business_address: Optional[str] = Form(None),
    business_rating: Optional[float] = Form(None),
):
    """Enrich competitor profile using Place Details + Gemini grounding search."""
    try:
        service = CompetitorEnrichmentService(
            google_maps_api_key=settings.google_maps_api_key, gemini_agent=agent
        )
        # Pass basic_info so enrichment can still work when Place Details fails
        basic_info = {}
        if business_name:
            basic_info["name"] = business_name
        if business_address:
            basic_info["address"] = business_address
        if business_rating:
            basic_info["rating"] = business_rating

        profile = await service.enrich_competitor_profile(
            place_id,
            basic_info=basic_info or None,
        )
        await service.close()

        if session_id:
            session = load_session(session_id)
            if session:
                if "enriched_competitors" not in session:
                    session["enriched_competitors"] = []
                session["enriched_competitors"].append(profile.to_dict())
                save_session(session_id)

        return {
            "status": "success",
            "profile": profile.to_dict(),
            "confidence": profile.confidence_score,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


# ============================================================================
# SETUP WIZARD ENDPOINT
# ============================================================================

@router.post("/business/setup-wizard", tags=["Business"])
async def setup_wizard(
    location: str = Form(""),
    place_id: Optional[str] = Form(None),
    business_name: Optional[str] = Form(None),
    context: Optional[str] = Form(None),
    menu_files: List[UploadFile] = File(default=[]),
    sales_files: List[UploadFile] = File(default=[]),
    photo_files: List[UploadFile] = File(default=[]),
    competitor_files: List[UploadFile] = File(default=[]),
    audio_files: List[UploadFile] = File(default=[]),
    video_files: List[UploadFile] = File(default=[]),
):
    """
    🧙 Progressive Disclosure Wizard - Complete setup in one request.
    
    Handles all wizard data including:
    - Location and business info
    - Menu files (PDF, images)
    - Sales data (CSV, Excel)
    - Product photos
    - Competitor info files
    - Audio recordings for context
    - Video files for ambience analysis
    
    Returns a session_id ready for analysis.
    """
    from app.services.orchestrator import orchestrator
    
    try:
        # Create new session directly in the sessions store
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "menu_items": [],
            "sales_data": [],
        }
        save_session(session_id)
        session = sessions[session_id]
        
        # Also register with orchestrator for pipeline compatibility
        try:
            await orchestrator.create_session(session_id)
        except Exception as e:
            logger.warning(f"Failed to register session with orchestrator: {e}")
            pass  # Non-critical, wizard can work without orchestrator state
        
        # Parse context JSON
        context_data = {}
        if context:
            try:
                context_data = json.loads(context)
            except json.JSONDecodeError:
                logger.warning("Failed to parse context JSON")
        
        # Store basic info
        session["restaurant_info"] = {
            "name": business_name or "My Restaurant",
            "location": location,
            "place_id": place_id,
            "social_media": context_data.get("social_media", {}),
            "phone": context_data.get("business_phone"),
            "website": context_data.get("business_website"),
            "rating": context_data.get("business_rating"),
            "user_ratings_total": context_data.get("business_user_ratings_total"),
        }
        
        # Store enriched profile from location selection (if available)
        enriched_profile = context_data.get("enriched_profile")
        if enriched_profile:
            session["business_profile_enriched"] = enriched_profile
        elif place_id:
            # Frontend enrichment didn't complete in time — schedule background enrichment
            async def _bg_enrich(sid: str, pid: str):
                try:
                    logger.info(f"Background enrichment for place_id={pid}")
                    svc = CompetitorEnrichmentService(
                        google_maps_api_key=settings.google_maps_api_key, gemini_agent=agent
                    )
                    prof = await svc.enrich_competitor_profile(pid)
                    await svc.close()
                    s = sessions.get(sid)
                    if s:
                        s["business_profile_enriched"] = prof.to_dict()
                        save_session(sid)
                        logger.info(f"Background enrichment completed: {prof.name}, social={len(prof.social_profiles)}")
                except Exception as e:
                    logger.warning(f"Background enrichment failed: {e}")
            asyncio.create_task(_bg_enrich(session_id, place_id))
        
        # Store nearby competitors found during location selection
        nearby_competitors = context_data.get("nearby_competitors", [])
        if nearby_competitors:
            session["competitors"] = nearby_competitors
            session["enriched_competitors"] = [
                c for c in nearby_competitors if c.get("competitive_intelligence")
            ] or nearby_competitors
        
        # Store context data
        session["business_context"] = {
            "history": context_data.get("history", ""),
            "values": context_data.get("values", ""),
            "usps": context_data.get("usps", ""),
            "target_audience": context_data.get("target_audience", ""),
            "challenges": context_data.get("challenges", ""),
            "goals": context_data.get("goals", ""),
            "competitors_input": context_data.get("competitors", ""),
            "auto_find_competitors": context_data.get("auto_find_competitors", True),
        }
        
        # Create upload directory
        upload_dir = Path("data/uploads") / session_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Process menu files
        all_menu_items = []
        for file in menu_files:
            if not file.filename:
                continue
            ext = file.filename.split(".")[-1].lower()
            if ext not in settings.allowed_image_ext_list:
                continue
            
            file_path = upload_dir / f"menu_{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            try:
                if ext == "pdf":
                    result = await menu_extractor.extract_from_pdf_all_pages(
                        str(file_path), use_ocr=True, 
                        business_context=context_data.get("history", "")
                    )
                else:
                    result = await menu_extractor.extract_from_image(
                        str(file_path), use_ocr=True,
                        business_context=context_data.get("history", "")
                    )
                all_menu_items.extend(result.get("items", []))
            except Exception as e:
                logger.error(f"Failed to process menu file {file.filename}: {e}")
        
        session["menu_items"] = all_menu_items
        
        # Process sales files
        all_sales_data = []
        for file in sales_files:
            if not file.filename:
                continue
            ext = file.filename.split(".")[-1].lower()
            if ext not in ["csv", "xlsx", "xls"]:
                continue
            
            file_path = upload_dir / f"sales_{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            try:
                if ext == "csv":
                    df = pd.read_csv(str(file_path))
                else:
                    df = pd.read_excel(str(file_path))
                all_sales_data.extend(df.to_dict(orient="records"))
            except Exception as e:
                logger.error(f"Failed to process sales file {file.filename}: {e}")
        
        session["sales_data"] = all_sales_data
        
        # Store photo file paths
        photo_paths = []
        for file in photo_files:
            if not file.filename:
                continue
            file_path = upload_dir / f"photo_{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            photo_paths.append(str(file_path))
        session["photo_files"] = photo_paths
        
        # Store competitor file paths
        competitor_paths = []
        for file in competitor_files:
            if not file.filename:
                continue
            file_path = upload_dir / f"competitor_{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            competitor_paths.append(str(file_path))
        session["competitor_files"] = competitor_paths
        
        # Store audio file paths
        audio_paths = []
        for file in audio_files:
            if not file.filename:
                continue
            file_path = upload_dir / f"audio_{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            audio_paths.append(str(file_path))
        session["audio_files"] = audio_paths
        
        # Store video file paths
        video_paths = []
        for file in video_files:
            if not file.filename:
                continue
            file_path = upload_dir / f"video_{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            video_paths.append(str(file_path))
        session["video_files"] = video_paths

        # Save session
        save_session(session_id)
        
        logger.info(f"Setup wizard completed for session {session_id}")
        logger.info(f"  - Menu items: {len(all_menu_items)}")
        logger.info(f"  - Sales records: {len(all_sales_data)}")
        logger.info(f"  - Photos: {len(photo_paths)}")
        logger.info(f"  - Audio files: {len(audio_paths)}")
        logger.info(f"  - Video files: {len(video_paths)}")
        
        return {
            "status": "success",
            "session_id": session_id,
            "summary": {
                "menu_items_extracted": len(all_menu_items),
                "sales_records": len(all_sales_data),
                "photos_uploaded": len(photo_paths),
                "audio_files": len(audio_paths),
                "video_files": len(video_paths),
                "location": location,
                "business_name": business_name,
            }
        }
        
    except Exception as e:
        logger.error(f"Setup wizard failed: {e}")
        raise HTTPException(500, f"Setup failed: {str(e)}")
