from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.api.deps import load_session, save_session, sessions
from app.services.gemini.vibe_engineering import VibeEngineeringAgent
from loguru import logger

router = APIRouter()
vibe_agent = VibeEngineeringAgent()

class VerifyRequest(BaseModel):
    session_id: str
    analysis_type: str
    auto_verify: bool = True
    auto_improve: bool = True
    quality_threshold: float = 0.85
    max_iterations: int = 3

@router.post("/vibe-engineering/verify", tags=["Vibe Engineering"])
async def verify_analysis(request: VerifyRequest, background_tasks: BackgroundTasks):
    """
    Trigger autonomous verification and improvement loop.
    """
    session_id = request.session_id
    session = load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Determine what data to verify based on analysis_type
    analysis_result = None
    source_data = {}

    if request.analysis_type == 'bcg_classification':
        analysis_result = session.get('bcg_analysis')
        source_data = {
            "menu_items": session.get('menu_items', []),
            "sales_data": session.get('sales_data', [])
        }
    elif request.analysis_type == 'competitive_analysis':
        analysis_result = session.get('competitor_analysis')
        source_data = {
            "our_menu": session.get('menu_items', []),
            "competitors": session.get('competitors_discovered', [])
        }
    elif request.analysis_type == 'campaign_generation':
        analysis_result = session.get('campaigns')
        source_data = {
            "bcg_analysis": session.get('bcg_analysis'),
            "business_context": session.get('business_context')
        }
    
    if not analysis_result:
        raise HTTPException(status_code=400, detail=f"No analysis found for type {request.analysis_type}")

    # Set initial status
    sessions[session_id]["vibe_status"] = {
        "status": "verifying",
        "iterations_required": 0,
        "quality_achieved": 0,
        "verification_history": [],
        "improvement_iterations": [],
        "final_analysis": None,
        "auto_improved": False,
        "total_duration_ms": 0
    }
    save_session(session_id)

    # Run in background
    background_tasks.add_task(
        _run_verification_task,
        session_id,
        request.analysis_type,
        analysis_result,
        source_data,
        request.auto_improve,
        request.quality_threshold,
        request.max_iterations
    )

    return sessions[session_id]["vibe_status"]

async def _run_verification_task(
    session_id: str,
    analysis_type: str,
    analysis_result: Dict,
    source_data: Dict,
    auto_improve: bool,
    quality_threshold: float,
    max_iterations: int
):
    try:
        import time
        start_time = time.time()
        
        # Instantiate agent per task for thread safety
        task_agent = VibeEngineeringAgent()
        task_agent.quality_threshold = quality_threshold
        task_agent.max_iterations = max_iterations
        
        result = await task_agent.verify_and_improve_analysis(
            analysis_type=analysis_type,
            analysis_result=analysis_result,
            source_data=source_data,
            auto_improve=auto_improve
        )
        
        duration = int((time.time() - start_time) * 1000)
        result["total_duration_ms"] = duration
        result["status"] = "completed"
        
        # Update session
        sessions[session_id]["vibe_status"] = result
        
        # If improved, update the main analysis in session
        if result.get("auto_improved") and result.get("final_analysis"):
            if analysis_type == 'bcg_classification':
                sessions[session_id]['bcg_analysis'] = result['final_analysis']
            elif analysis_type == 'competitive_analysis':
                sessions[session_id]['competitor_analysis'] = result['final_analysis']
            elif analysis_type == 'campaign_generation':
                sessions[session_id]['campaigns'] = result['final_analysis']
        
        save_session(session_id)
        
    except Exception as e:
        logger.error(f"Vibe verification task failed: {e}")
        sessions[session_id]["vibe_status"] = {
            "status": "failed",
            "error": str(e)
        }
        save_session(session_id)

@router.get("/vibe-engineering/status", tags=["Vibe Engineering"])
async def get_verification_status(session_id: str):
    session = load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.get("vibe_status", None)

@router.post("/vibe-engineering/cancel", tags=["Vibe Engineering"])
async def cancel_verification(session_id: str):
    session = load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Simple cancellation by flag (in a real system might need task cancellation)
    if session.get("vibe_status", {}).get("status") == "verifying":
        sessions[session_id]["vibe_status"]["status"] = "cancelled"
        save_session(session_id)
    
    return {"status": "cancelled"}
