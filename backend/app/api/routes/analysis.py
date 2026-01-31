from typing import Dict, List, Optional

import pandas as pd
from app.api.deps import load_session, save_session, sessions
from app.core.config import get_settings
from app.services.analysis.advanced_analytics import AdvancedAnalyticsService
from app.services.analysis.bcg import BCGClassifier
from app.services.analysis.data_capability import DataCapabilityDetector
from app.services.analysis.menu_engineering import (
    AnalysisPeriod,
    MenuEngineeringClassifier,
)
from app.services.analysis.menu_optimizer import MenuOptimizer
from app.services.analysis.neural_predictor import NeuralPredictor
from app.services.analysis.pricing import (
    CompetitorIntelligenceService,
    CompetitorSource,
)
from app.services.analysis.sales_predictor import SalesPredictor
from app.services.analysis.sentiment import (
    ReviewData,
    SentimentAnalyzer,
    SentimentSource,
)
from app.services.campaigns.generator import CampaignGenerator
from app.services.gemini.base_agent import GeminiAgent, ThinkingLevel
from app.services.gemini.multimodal import MultimodalAgent
from app.services.gemini.reasoning_agent import ReasoningAgent
from app.services.gemini.verification import VerificationAgent
from app.services.intelligence.competitor_finder import ScoutAgent
from app.services.orchestrator import orchestrator
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger

# Initialize router
router = APIRouter()
settings = get_settings()

# Initialize services
agent = GeminiAgent()
multimodal_agent = MultimodalAgent()
reasoning_agent = ReasoningAgent()

bcg_classifier = BCGClassifier(agent)
menu_engineering = MenuEngineeringClassifier()
sales_predictor = SalesPredictor()
campaign_generator = CampaignGenerator(agent)
verification_agent = VerificationAgent()
neural_predictor = NeuralPredictor()
data_capability_detector = DataCapabilityDetector()
menu_optimizer = MenuOptimizer()
advanced_analytics = AdvancedAnalyticsService()
competitor_intelligence = CompetitorIntelligenceService(
    multimodal_agent, reasoning_agent
)
sentiment_analyzer = SentimentAnalyzer(multimodal_agent, reasoning_agent)
scout_agent = ScoutAgent()


@router.post("/analyze/bcg", tags=["Analyze"])
async def run_bcg_analysis(session_id: str, period: str = "30d"):
    """Run Menu Engineering analysis on menu items."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    menu_items = session.get("menu_items", [])
    sales_data = session.get("sales_data", [])

    try:
        analysis_period = AnalysisPeriod(period)
    except ValueError:
        analysis_period = AnalysisPeriod.LAST_30_DAYS

    # Merge menu items logic
    existing_menu_names = {item["name"].lower().strip() for item in menu_items}
    if sales_data:
        unique_sales_items = set(
            record.get("item_name", "")
            for record in sales_data
            if record.get("item_name")
        )
        items_added = 0
        for item_name in unique_sales_items:
            if item_name.lower().strip() not in existing_menu_names:
                item_sales = [s for s in sales_data if s.get("item_name") == item_name]
                total_units = sum(
                    s.get("units_sold", 0) or s.get("quantity", 0) for s in item_sales
                )

                prices = [s.get("price", 0) for s in item_sales if s.get("price")]
                avg_price = sum(prices) / len(prices) if prices else 0.0
                if not prices:
                    total_rev = sum(s.get("revenue", 0) for s in item_sales)
                    avg_price = total_rev / total_units if total_units > 0 else 0.0

                costs = [s.get("cost", 0) for s in item_sales if s.get("cost")]
                avg_cost = sum(costs) / len(costs) if costs else 0.0

                category = "Sin Categoría"
                for s in item_sales:
                    if s.get("category"):
                        category = s.get("category")
                        break

                menu_items.append(
                    {
                        "name": item_name,
                        "price": round(avg_price, 2),
                        "cost": round(avg_cost, 2),
                        "category": category,
                        "source": "sales_data",
                    }
                )
                existing_menu_names.add(item_name.lower().strip())
                items_added += 1

        if items_added > 0:
            logger.info(f"Added {items_added} items from sales data")

    sessions[session_id]["menu_items"] = menu_items
    save_session(session_id)

    if not menu_items and not sales_data:
        raise HTTPException(400, "No menu items or sales data found")

    try:
        result = await menu_engineering.analyze(menu_items, sales_data, analysis_period)
        sessions[session_id]["bcg_analysis"] = result
        save_session(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "summary": result.get("summary", {}),
            "items": result.get("items", []),
            "thought_signature": await agent.create_thought_signature(
                "Menu Engineering analysis",
                {"items": len(menu_items), "period": period},
            ),
        }
    except Exception as e:
        logger.error(f"BCG analysis failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/predict/sales", tags=["Predict"])
async def predict_sales(
    session_id: str,
    horizon_days: int = 14,
    scenarios: Optional[List[Dict]] = None,
    period: str = "all",
):
    """Generate sales predictions."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    menu_items = session.get("menu_items", [])
    all_sales_data = session.get("sales_data", [])
    image_scores = session.get("image_scores", {})

    from app.services.analysis.menu_engineering import filter_sales_by_period

    try:
        analysis_period = AnalysisPeriod(period)
    except ValueError:
        analysis_period = AnalysisPeriod.ALL_TIME

    sales_data, _, _ = filter_sales_by_period(all_sales_data, analysis_period)

    if not menu_items:
        raise HTTPException(400, "No menu items found")

    try:
        if sales_predictor.model is None:
            await sales_predictor.train(sales_data, menu_items, image_scores)

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

        scenarios = scenarios or [{"name": "baseline"}]
        result = await sales_predictor.predict_batch(
            items_for_prediction, horizon_days, scenarios
        )

        sessions[session_id]["predictions"] = result
        save_session(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "scenario_totals": result["scenario_totals"],
            "item_predictions": result["item_predictions"],
            "thought_signature": await agent.create_thought_signature(
                "Sales prediction", {"horizon": horizon_days}
            ),
        }
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/campaigns/generate", tags=["Campaigns"])
async def generate_campaigns(
    session_id: str,
    num_campaigns: int = 3,
    duration_days: int = 14,
    channels: Optional[List[str]] = None,
):
    """Generate AI-powered marketing campaigns."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    bcg_analysis = session.get("bcg_analysis")
    if not bcg_analysis:
        raise HTTPException(400, "Run BCG analysis first")

    enriched_analysis = {
        **bcg_analysis,
        "predictions_available": "predictions" in session,
        "business_context": session.get("business_context", ""),
        "competitor_context": session.get("competitor_context", ""),
        "audio_insights": session.get("audio_analysis", {}),
    }

    try:
        result = await campaign_generator.generate_campaigns(
            enriched_analysis,
            session.get("menu_items", []),
            num_campaigns,
            duration_days,
            channels,
        )
        sessions[session_id]["campaigns"] = result["campaigns"]
        save_session(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "campaigns": result["campaigns"],
            "thought_signature": result["thought_signature"],
        }
    except Exception as e:
        logger.error(f"Campaign generation failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/analyze/competitors", tags=["Analyze"])
async def analyze_competitors(session_id: str):
    """Run comprehensive competitor analysis."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    enriched_competitors = session.get("enriched_competitors", [])
    basic_competitors = session.get("competitors", [])

    if not enriched_competitors and not basic_competitors:
        return {"status": "skipped", "message": "No competitor data available"}

    competitor_sources = []
    for comp in enriched_competitors:
        competitor_sources.append(
            CompetitorSource(
                type="data", value=comp, name=comp.get("name"), metadata=comp
            )
        )
    for comp in basic_competitors:
        competitor_sources.append(
            CompetitorSource(
                type="data", value=comp, name=comp.get("name"), metadata=comp
            )
        )

    try:
        result = await competitor_intelligence.analyze_competitors(
            our_menu={"items": session.get("menu_items", [])},
            competitor_sources=competitor_sources,
            restaurant_name=session.get("business_location", {}).get(
                "name", "Our Restaurant"
            ),
            thinking_level=ThinkingLevel.DEEP,
        )

        result_dict = result.to_dict()
        sessions[session_id]["competitor_analysis"] = result_dict
        save_session(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "competitor_analysis": result_dict,
            "thought_signature": await agent.create_thought_signature(
                "Competitor Analysis", {"competitors": len(competitor_sources)}
            ),
        }
    except Exception as e:
        logger.error(f"Competitor analysis failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/analyze/sentiment", tags=["Analyze"])
async def analyze_sentiment(session_id: str):
    """Run multi-modal sentiment analysis."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    reviews = []
    business_profile = session.get("business_profile_enriched", {})

    if business_profile.get("reviews"):
        for r in business_profile.get("reviews", []):
            reviews.append(
                ReviewData(
                    source=SentimentSource.GOOGLE,
                    text=r.get("text", ""),
                    rating=r.get("rating"),
                    reviewer=r.get("author_name"),
                    date=r.get("relative_time_description"),
                )
            )

    if not reviews:
        return {"status": "skipped", "message": "No reviews available"}

    try:
        result = await sentiment_analyzer.analyze_customer_sentiment(
            restaurant_id=session.get("business_location", {}).get(
                "place_id", "unknown"
            ),
            reviews=reviews,
            customer_photos=None,
            menu_items=[item["name"] for item in session.get("menu_items", [])],
            bcg_data=session.get("bcg_analysis"),
            sources=[SentimentSource.GOOGLE],
        )

        result_dict = result.to_dict()
        sessions[session_id]["sentiment_analysis"] = result_dict
        save_session(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "sentiment_analysis": result_dict,
            "thought_signature": await agent.create_thought_signature(
                "Sentiment Analysis", {"reviews": len(reviews)}
            ),
        }
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/intelligence/scout", tags=["Intelligence"])
async def run_scout_mission(
    session_id: str,
    latitude: float = Form(...),
    longitude: float = Form(...),
    cuisine_type: str = Form("mexican"),
    radius_meters: int = Form(1000),
    max_competitors: int = Form(10),
    deep_analysis: bool = Form(True),
):
    """Run autonomous Scout Agent."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    try:
        our_menu = None
        if session.get("menu_items"):
            our_menu = {
                "items": session["menu_items"],
                "price_range": "mid-range",
                "specialties": [item.get("name") for item in session["menu_items"][:5]],
            }

        result = await scout_agent.run_scouting_mission(
            our_location={"lat": latitude, "lng": longitude},
            our_cuisine_type=cuisine_type,
            radius_meters=radius_meters,
            max_competitors=max_competitors,
            our_menu=our_menu,
            deep_analysis=deep_analysis,
            session_id=session_id,
        )

        sessions[session_id]["scout_intelligence"] = result
        sessions[session_id]["competitors_discovered"] = result.get("competitors", [])
        save_session(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "competitors": result.get("competitors"),
            "comparative_analysis": result.get("comparative_analysis"),
        }
    except Exception as e:
        logger.error(f"Scout mission failed: {e}")
        raise HTTPException(500, str(e))


@router.get("/intelligence/scout/{session_id}", tags=["Intelligence"])
async def get_scout_results(session_id: str):
    session = load_session(session_id)
    if not session or "scout_intelligence" not in session:
        raise HTTPException(404, "Scout intelligence not found")
    return {
        "session_id": session_id,
        "scout_intelligence": session["scout_intelligence"],
    }


@router.post("/analysis/start", tags=["Orchestrator"])
async def start_new_analysis(
    # Basic Info
    location: str = Form(...),
    businessName: Optional[str] = Form(None),
    instagram: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    
    # Context (Text)
    historyContext: Optional[str] = Form(None),
    valuesContext: Optional[str] = Form(None),
    uspsContext: Optional[str] = Form(None),
    targetAudienceContext: Optional[str] = Form(None),
    challengesContext: Optional[str] = Form(None),
    goalsContext: Optional[str] = Form(None),
    
    # Competitors
    competitorUrls: Optional[List[str]] = Form(None),
    autoFindCompetitors: bool = Form(True),
    
    # Files
    menuFiles: List[UploadFile] = File(default=[]),
    salesFiles: List[UploadFile] = File(default=[]),
    photoFiles: List[UploadFile] = File(default=[]),
    
    # Audio
    historyAudio: Optional[UploadFile] = File(None),
    valuesAudio: Optional[UploadFile] = File(None),
):
    """Start a new comprehensive analysis session from the setup wizard."""
    
    # 1. Create Session first to get ID for file storage
    try:
        session_id = await orchestrator.create_session()
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(500, "Failed to initialize session")

    # 2. aggregate context
    business_context = {
        "name": businessName,
        "location_query": location,
        "instagram": instagram,
        "website": website,
        "history": historyContext,
        "values": valuesContext,
        "usps": uspsContext,
        "target_audience": targetAudienceContext,
        "challenges": challengesContext,
        "goals": goalsContext,
    }
    
    # 3. Process Files
    menu_bytes = []
    for file in menuFiles:
        menu_bytes.append(await file.read())
        
    dish_bytes = []
    for file in photoFiles:
        dish_bytes.append(await file.read())
        
    sales_csv = None
    if salesFiles:
        # Use the first sales file for now
        content = await salesFiles[0].read()
        try:
            sales_csv = content.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback for excel? For now assume CSV as per requirements, or handle error
            logger.warning("Could not decode sales file as UTF-8")
            
    # 4. Handle Audio (Save to disk)
    import aiofiles
    import os
    from pathlib import Path
    
    upload_dir = Path(f"data/uploads/{session_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    if historyAudio:
        file_path = upload_dir / f"history_audio_{historyAudio.filename}"
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await historyAudio.read()
            await out_file.write(content)
        business_context["history_audio_path"] = str(file_path)
        
    if valuesAudio:
        file_path = upload_dir / f"values_audio_{valuesAudio.filename}"
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await valuesAudio.read()
            await out_file.write(content)
        business_context["values_audio_path"] = str(file_path)

    # 5. Start Pipeline
    try:
        # Run in background via asyncio task
        asyncio.create_task(orchestrator.run_full_pipeline(
            session_id=session_id,
            menu_images=menu_bytes,
            dish_images=dish_bytes,
            sales_csv=sales_csv,
            address=location,
            business_context=business_context,
            competitor_urls=competitorUrls,
            auto_find_competitors=autoFindCompetitors,
            thinking_level=ThinkingLevel.STANDARD,
            auto_verify=True
        ))
        
        return {"analysis_id": session_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Failed to start analysis pipeline: {e}")
        # Session was created but pipeline failed to start
        raise HTTPException(500, f"Failed to start analysis pipeline: {str(e)}")

@router.post("/orchestrator/run", tags=["Orchestrator"])
async def run_autonomous_pipeline(
    menu_image: Optional[UploadFile] = File(None),
    dish_images: Optional[List[UploadFile]] = File(None),
    sales_file: Optional[UploadFile] = File(None),
    thinking_level: str = Form("standard"),
    auto_verify: bool = Form(True),
):
    """Run the complete autonomous analysis pipeline."""
    try:
        level = ThinkingLevel(thinking_level)
    except ValueError:
        level = ThinkingLevel.STANDARD

    session_id = await orchestrator.create_session()

    menu_bytes = [await menu_image.read()] if menu_image else None
    dish_bytes = [await img.read() for img in dish_images] if dish_images else None
    sales_csv = (await sales_file.read()).decode("utf-8") if sales_file else None

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
        logger.error(f"Orchestrator failed: {e}")
        raise HTTPException(500, str(e))


@router.get("/orchestrator/status/{session_id}", tags=["Orchestrator"])
async def get_orchestrator_status(session_id: str):
    status = orchestrator.get_session_status(session_id)
    if not status:
        raise HTTPException(404, "Session not found")
    return status


@router.post("/orchestrator/resume/{session_id}", tags=["Orchestrator"])
async def resume_orchestrator_session(
    session_id: str,
    thinking_level: Optional[str] = Form(None),
    auto_verify: Optional[bool] = Form(None),
):
    status = await orchestrator.resume_session(session_id)
    if not status:
        raise HTTPException(404, "Session not found")

    level = None
    if thinking_level:
        try:
            level = ThinkingLevel(thinking_level)
        except ValueError:
            pass

    try:
        result = await orchestrator.run_full_pipeline(
            session_id=session_id, thinking_level=level, auto_verify=auto_verify
        )
        return result
    except Exception as e:
        logger.error(f"Resume failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/verify/analysis", tags=["Verification"])
async def verify_analysis(
    session_id: str,
    thinking_level: str = "standard",
    auto_improve: bool = True,
):
    """Run verification agent on existing analysis."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

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
            analysis_data, thinking_level=level, auto_improve=auto_improve
        )

        sessions[session_id]["verification"] = {
            "status": result.status.value,
            "overall_score": result.overall_score,
            "improvements": result.improvements_made,
        }
        save_session(session_id)

        return {
            "session_id": session_id,
            "status": result.status.value,
            "overall_score": result.overall_score,
            "checks": [
                {"name": c.check_name, "passed": c.passed} for c in result.checks
            ],
            "final_recommendation": result.final_recommendation,
        }
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/predict/neural", tags=["Predict"])
async def predict_with_neural_network(
    session_id: str,
    horizon_days: int = 14,
    use_ensemble: bool = True,
    uncertainty_samples: int = 10,
):
    """Run deep learning sales prediction."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    menu_items = session.get("menu_items", [])
    sales_data = session.get("sales_data", [])
    image_scores = session.get("image_scores", {})

    if not menu_items:
        raise HTTPException(400, "No menu items found")

    try:
        if not neural_predictor.is_trained:
            await neural_predictor.train(sales_data, menu_items, epochs=30)

        predictions = {}
        for item in menu_items:
            base_features = {
                "price": item.get("price", 15),
                "avg_daily_units": 20,
                "image_score": image_scores.get(item["name"], 0.5),
            }
            scenarios = [{"name": "baseline"}]
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
        save_session(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "predictions": predictions,
        }
    except Exception as e:
        logger.error(f"Neural prediction failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/analyze/capabilities", tags=["Advanced Analytics"])
async def analyze_data_capabilities(session_id: str = Form(...)):
    """Analyze data capabilities."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    sales_data = session.get("sales_data", [])
    if not sales_data:
        return {"available_capabilities": ["bcg_analysis"]}

    df = pd.DataFrame(sales_data)
    report = data_capability_detector.analyze(df)

    session["capability_report"] = {
        "available": [cap.value for cap in report.available_capabilities],
        "column_mapping": {k: v for k, v in report.column_mapping.__dict__.items()},
    }
    save_session(session_id)

    return {
        "session_id": session_id,
        "available_capabilities": [cap.value for cap in report.available_capabilities],
        "recommendations": report.recommendations,
    }


@router.post("/analyze/menu-optimization", tags=["Advanced Analytics"])
async def run_menu_optimization(session_id: str = Form(...)):
    """Run menu optimization."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    sales_data = session.get("sales_data", [])
    if not sales_data:
        raise HTTPException(400, "No sales data")

    cap_report = session.get("capability_report", {})
    column_mapping = cap_report.get(
        "column_mapping",
        {"item_name": "item_name", "quantity": "quantity", "revenue": "revenue"},
    )

    try:
        report = await menu_optimizer.analyze(
            sales_df=pd.DataFrame(sales_data),
            menu_items=session.get("menu_items", []),
            session_id=session_id,
            column_mapping=column_mapping,
            bcg_results=session.get("bcg_analysis", {}),
        )

        session["menu_optimization"] = {"quick_wins": report.quick_wins}
        save_session(session_id)

        return {
            "session_id": report.session_id,
            "quick_wins": report.quick_wins,
            "revenue_opportunity": report.revenue_opportunity,
        }
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/analyze/advanced", tags=["Advanced Analytics"])
async def run_advanced_analytics(session_id: str = Form(...)):
    """Run advanced analytics."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    sales_data = session.get("sales_data", [])
    if not sales_data:
        raise HTTPException(400, "No sales data")

    cap_data = session.get("capability_report", {})
    column_mapping = cap_data.get("column_mapping", {})
    caps_list = cap_data.get("available", [])

    try:
        report = await advanced_analytics.analyze(
            df=pd.DataFrame(sales_data),
            session_id=session_id,
            column_mapping=column_mapping,
            capabilities=caps_list,
        )

        session["advanced_analytics"] = {"key_insights": report.key_insights}
        save_session(session_id)

        return {
            "session_id": report.session_id,
            "key_insights": report.key_insights,
            "hourly_patterns": [p.__dict__ for p in report.hourly_patterns],
        }
    except Exception as e:
        logger.error(f"Advanced analytics failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/chat", tags=["AI Chat"])
async def chat_with_ai(
    session_id: str = Form(...),
    message: str = Form(...),
    context: str = Form("general"),
):
    """Interactive chat with Gemini AI."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    def _format_bcg(bcg):
        if not bcg:
            return "No BCG analysis."
        counts = bcg.get("summary", {}).get("counts", {})
        return f"Stars: {counts.get('star', 0)}, Dogs: {counts.get('dog', 0)}"

    session_context = f"""
    You are RestoPilotAI AI. 
    Menu Items: {len(session.get('menu_items', []))}
    BCG: {_format_bcg(session.get('bcg_analysis', {}))}
    Context: {context}
    """

    try:
        response = await agent.generate_response(
            prompt=f"{session_context}\n\nUser: {message}",
            system_instruction="You are a helpful consultant.",
        )
        return {"response": response, "session_id": session_id}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"response": "Error processing request", "error": str(e)}
