from typing import Dict, Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from datetime import datetime

from app.services.orchestrator import orchestrator, PipelineStage
from app.services.gemini.base_agent import ThinkingLevel
from loguru import logger

"""
Marathon Agent API Routes - Long-running task execution with checkpoints.

Includes WebSocket and SSE support for real-time progress updates.
"""

router = APIRouter(tags=["Marathon Agent"])

# === WEBSOCKET CONNECTION MANAGER ===

class ConnectionManager:
    """
    Manages WebSocket connections for Marathon Agent progress updates.
    
    Allows multiple clients to monitor different tasks simultaneously.
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self.active_connections[task_id] = websocket
        logger.info(f"WebSocket connected for task {task_id}")
    
    def disconnect(self, task_id: str):
        """Unregister a WebSocket connection."""
        if task_id in self.active_connections:
            del self.active_connections[task_id]
            logger.info(f"WebSocket disconnected for task {task_id}")
    
    async def send_progress(self, task_id: str, message: dict):
        """
        Send progress update to connected client.
        
        Falls back gracefully if connection is lost.
        """
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message to {task_id}: {e}")
                self.disconnect(task_id)

# Global connection manager instance
manager = ConnectionManager()

class MarathonTaskConfig(BaseModel):
    task_type: str  # 'full_analysis', 'competitive_intel', 'campaign_generation'
    session_id: Optional[str] = None
    input_data: Dict = {}
    enable_checkpoints: bool = True
    checkpoint_interval_seconds: int = 60
    max_retries_per_step: int = 3
    auto_verify: bool = True
    auto_improve: bool = True

@router.post("/marathon/start", tags=["Marathon Agent"])
async def start_marathon_task(
    config: MarathonTaskConfig, 
    background_tasks: BackgroundTasks
):
    """
    Start a long-running Marathon Agent task.
    """
    try:
        # Use provided session_id or create new one
        session_id = config.session_id
        if not session_id:
            session_id = await orchestrator.create_session()
        else:
            # For existing sessions (like demo), ensure orchestrator state is initialized
            # Force clean initialization - remove any stale completed states
            if session_id in orchestrator.completed_sessions:
                del orchestrator.completed_sessions[session_id]
                logger.info(f"Removed stale completed state for session {session_id}")
            
            if session_id in orchestrator.active_sessions:
                del orchestrator.active_sessions[session_id]
                logger.info(f"Removed stale active state for session {session_id}")
            
            # Initialize fresh orchestrator state for this session
            from app.services.orchestrator import AnalysisState, PipelineStage
            from app.api.deps import load_session
            
            # Load business session data if available
            business_session = load_session(session_id)
            
            restaurant_info = business_session.get("restaurant_info", {}) if business_session else {}
            state = AnalysisState(
                session_id=session_id,
                current_stage=PipelineStage.INITIALIZED,
                checkpoints=[],
                thought_traces=[],
                menu_items=business_session.get("menu_items", []) if business_session else [],
                sales_data=business_session.get("sales_data", []) if business_session else [],
                restaurant_name=restaurant_info.get("name", "Restaurant"),
                business_profile_enriched=business_session.get("business_profile_enriched") if business_session else None,
                social_media=restaurant_info.get("social_media", {}),
                auto_verify=config.auto_verify,
                auto_improve=config.auto_improve
            )
            orchestrator.active_sessions[session_id] = state
            orchestrator._save_session_to_disk(state)
            logger.info(f"Initialized fresh orchestrator state for session {session_id} with {len(state.menu_items)} menu items and {len(state.sales_data)} sales records")
        
        # Dispatch based on task_type
        if config.task_type == "full_analysis":
            # Extract parameters from input_data
            input_data = config.input_data
            
            logger.info(f"Starting full_analysis pipeline for session {session_id}")
            logger.info(f"Input data keys: {list(input_data.keys()) if input_data else 'None'}")
            
            # Start Orchestrator Pipeline in background
            background_tasks.add_task(
                orchestrator.run_full_pipeline,
                session_id=session_id,
                sales_csv=input_data.get("sales_csv") if input_data else None,
                thinking_level=ThinkingLevel.STANDARD, 
                auto_verify=config.auto_verify,
                auto_improve=config.auto_improve
            )
            
            logger.info(f"Background task added for session {session_id}")
            
        elif config.task_type == "competitive_intel":
            # TODO: Implement specialized sub-pipeline
            pass
            
        return {"task_id": session_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Failed to start marathon task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marathon/status/{task_id}", tags=["Marathon Agent"])
async def get_task_status(task_id: str):
    """Get status of a marathon task."""
    status = orchestrator.get_session_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Map orchestrator status to MarathonTaskState interface expected by frontend
    current_stage = status.get("current_stage")
    checkpoints_data = status.get("checkpoints", [])
    
    stages_completed = len(checkpoints_data)
    total_stages_est = 14 # Approximate
    
    progress = min(stages_completed / total_stages_est, 1.0)
    if current_stage == "completed":
        progress = 1.0
    
    # Map Checkpoints
    mapped_checkpoints = []
    for i, cp in enumerate(checkpoints_data):
        mapped_checkpoints.append({
            "checkpoint_id": f"{task_id}_cp_{i}",
            "task_id": task_id,
            "step_index": i,
            "timestamp": cp.get("timestamp"),
            "accumulated_results": {}, # Optimize payload size
            "state_snapshot": {"stage": cp.get("stage")}
        })

    # Map Steps (Synthetic based on checkpoints + current)
    # Ideally orchestrator would provide the full plan. 
    # For now we infer from history.
    steps = []
    for i, cp in enumerate(checkpoints_data):
        steps.append({
            "step_id": f"step_{i}",
            "name": cp.get("stage", "Unknown"),
            "description": "Stage completed",
            "status": "completed",
            "completed_at": cp.get("timestamp"),
            "retry_count": 0,
            "max_retries": 3
        })
    
    # Only add a running step if the pipeline is actually running (not completed, failed, or initialized)
    if current_stage not in ["completed", "failed", "initialized"]:
        steps.append({
            "step_id": f"step_{len(steps)}",
            "name": current_stage,
            "description": "Processing...",
            "status": "running",
            "started_at": status.get("started_at"), # Approximation
            "retry_count": 0,
            "max_retries": 3
        })

    # Format current_step_name for display
    display_step_name = current_stage
    if current_stage == "completed":
        display_step_name = "Analysis Complete"
    elif current_stage == "failed":
        display_step_name = "Failed"
    elif current_stage == "initialized":
        display_step_name = "Initializing..."
    
    return {
        "task_id": task_id,
        "status": map_status(current_stage),
        "progress": progress,
        "current_step": stages_completed + 1,
        "total_steps": total_stages_est,
        "current_step_name": display_step_name,
        "started_at": status.get("started_at"),
        "completed_at": status.get("completed_at"),
        "steps": steps, 
        "checkpoints": mapped_checkpoints,
        "accumulated_results": {}, 
        "can_recover": current_stage == "failed"
    }

def map_status(orchestrator_stage: str) -> str:
    if orchestrator_stage == "completed":
        return "completed"
    if orchestrator_stage == "failed":
        return "failed"
    if orchestrator_stage == "initialized":
        return "pending"
    return "running"

@router.post("/marathon/cancel/{task_id}", tags=["Marathon Agent"])
async def cancel_task(task_id: str):
    """Cancel a running task."""
    # Orchestrator doesn't seem to have explicit cancel method in the snippet 
    # but we can implement a basic one or just remove from active sessions.
    # For now, we'll try to mark it.
    
    # Check if active
    if task_id in orchestrator.active_sessions:
        state = orchestrator.active_sessions[task_id]
        state.current_stage = PipelineStage.FAILED # Or CANCELLED if enum existed
        # Ideally we'd signal the running loop to stop.
        # This is a placeholder for actual cancellation logic.
        return {"status": "cancelled"}
    
    raise HTTPException(status_code=404, detail="Task not found or already finished")

@router.post("/marathon/recover/{task_id}", tags=["Marathon Agent"])
async def recover_task(task_id: str, background_tasks: BackgroundTasks):
    """Recover a failed task from last checkpoint."""
    # First verify we can load the state
    success = await orchestrator.resume_session(task_id)
    if not success:
         raise HTTPException(status_code=400, detail="Could not recover task")
    
    # Trigger execution in background to continue from where it left off
    # Resume session loads state but doesn't auto-run. We need to call run_full_pipeline again.
    # The orchestrator logic now skips completed stages.
    background_tasks.add_task(
        orchestrator.run_full_pipeline,
        session_id=task_id,
        # We don't need to pass other args as they are loaded from state/context
        # But run_full_pipeline signature expects them as optional.
        # Orchestrator handles missing args by looking at state.
    )
    
    return {"task_id": task_id, "status": "recovering"}

@router.websocket("/ws/marathon/{task_id}")
async def marathon_progress(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time Marathon Agent progress.
    """
    await manager.connect(task_id, websocket)
    try:
        # Send initial status
        state = orchestrator.get_session_status(task_id)
        if state:
            await websocket.send_json({
                "type": "initial_state",
                "state": state
            })
        
        # Keep connection alive and listen for client messages (if any)
        # In this pattern, the server pushes updates via manager.broadcast/send_to_session
        while True:
            data = await websocket.receive_text()
            # Client might send "ping" or commands, handle if needed
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        manager.disconnect(task_id)
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        manager.disconnect(task_id)


# === SSE STREAMING ENDPOINT FOR THOUGHT BUBBLES ===

# Store for thought streams per task
thought_streams: Dict[str, list] = {}

def get_thought_type(stage: str) -> str:
    """Map pipeline stage to thought type."""
    stage_mapping = {
        "initialized": "analyzing",
        "menu_extraction": "analyzing",
        "sales_analysis": "calculating",
        "bcg_analysis": "calculating",
        "competitor_analysis": "comparing",
        "sentiment_analysis": "analyzing",
        "campaign_generation": "generating",
        "verification": "verifying",
        "completed": "concluding",
    }
    return stage_mapping.get(stage, "analyzing")

def get_stage_title(stage: str) -> str:
    """Get human-readable title for stage."""
    titles = {
        "initialized": "Inicializando análisis",
        "menu_extraction": "Extrayendo menú",
        "sales_analysis": "Analizando ventas",
        "bcg_analysis": "Calculando matriz BCG",
        "competitor_analysis": "Analizando competidores",
        "sentiment_analysis": "Analizando sentimiento",
        "campaign_generation": "Generando campañas",
        "verification": "Verificando resultados",
        "completed": "Análisis completado",
    }
    return titles.get(stage, stage.replace("_", " ").title())

async def generate_thought_stream(task_id: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Generate SSE stream of thought bubbles for a marathon task.
    
    Polls orchestrator status and emits thought events.
    """
    last_stage = None
    step_counter = 0
    start_time = datetime.now()
    
    # Estimate total steps
    total_steps = 8
    
    try:
        while True:
            # Get current status from orchestrator
            status = orchestrator.get_session_status(task_id)
            
            if not status:
                # Task not found, wait and retry
                await asyncio.sleep(1)
                continue
            
            current_stage = status.get("current_stage", "initialized")
            checkpoints = status.get("checkpoints", [])
            
            # Calculate progress
            progress = min(len(checkpoints) / total_steps, 0.99)
            if current_stage == "completed":
                progress = 1.0
            
            # Emit progress update
            progress_event = {
                "type": "progress",
                "progress": progress,
                "total_steps": total_steps,
                "current_step": len(checkpoints) + 1,
                "eta_seconds": int((1 - progress) * 120) if progress < 1 else 0,
            }
            yield f"data: {json.dumps(progress_event)}\n\n"
            
            # Emit thought bubble when stage changes
            if current_stage != last_stage:
                step_counter += 1
                
                # Get details from latest checkpoint if available
                details = []
                if checkpoints:
                    latest_cp = checkpoints[-1]
                    if "data" in latest_cp:
                        cp_data = latest_cp["data"]
                        if isinstance(cp_data, dict):
                            if "items_count" in cp_data:
                                details.append(f"Procesados {cp_data['items_count']} items")
                            if "confidence" in cp_data:
                                details.append(f"Confianza: {cp_data['confidence']*100:.0f}%")
                            if "summary" in cp_data:
                                details.append(cp_data["summary"])
                
                # Add stage-specific details
                if current_stage == "menu_extraction":
                    details.extend([
                        "Detectando items del menú",
                        "Extrayendo precios y categorías",
                        "Identificando descripciones"
                    ])
                elif current_stage == "bcg_analysis":
                    details.extend([
                        "Calculando popularidad por producto",
                        "Analizando márgenes de contribución",
                        "Clasificando en matriz BCG"
                    ])
                elif current_stage == "competitor_analysis":
                    details.extend([
                        "Buscando competidores cercanos",
                        "Comparando precios y oferta",
                        "Analizando posicionamiento"
                    ])
                elif current_stage == "sentiment_analysis":
                    details.extend([
                        "Procesando reseñas de clientes",
                        "Detectando temas recurrentes",
                        "Analizando tono emocional"
                    ])
                elif current_stage == "campaign_generation":
                    details.extend([
                        "Generando estrategias de marketing",
                        "Creando copy para redes sociales",
                        "Diseñando campañas por segmento"
                    ])
                
                thought_event = {
                    "type": "thought",
                    "id": f"thought-{task_id}-{step_counter}",
                    "step": step_counter,
                    "thought_type": get_thought_type(current_stage),
                    "title": get_stage_title(current_stage),
                    "details": details[:5],  # Limit details
                    "confidence": 0.85 + (step_counter * 0.02),  # Incremental confidence
                    "thinking_level": "STANDARD",
                    "model": "gemini-3-flash-preview",
                    "grounding_sources": [] if current_stage != "competitor_analysis" else ["Google Places", "Yelp"],
                }
                yield f"data: {json.dumps(thought_event)}\n\n"
                
                last_stage = current_stage
            
            # Check for completion
            if current_stage == "completed":
                # Get final results
                complete_event = {
                    "type": "complete",
                    "results": {
                        "session_id": task_id,
                        "status": "completed",
                        "duration_seconds": (datetime.now() - start_time).total_seconds(),
                    }
                }
                yield f"data: {json.dumps(complete_event)}\n\n"
                break
            
            # Check for failure
            if current_stage == "failed":
                error_event = {
                    "type": "error",
                    "error": status.get("error", "Pipeline failed")
                }
                yield f"data: {json.dumps(error_event)}\n\n"
                break
            
            # Poll interval
            await asyncio.sleep(2)
            
    except asyncio.CancelledError:
        logger.info(f"SSE stream cancelled for task {task_id}")
    except Exception as e:
        logger.error(f"SSE stream error for task {task_id}: {e}")
        error_event = {"type": "error", "error": str(e)}
        yield f"data: {json.dumps(error_event)}\n\n"


@router.get("/marathon/stream/{task_id}", tags=["Marathon Agent"])
async def stream_marathon_thoughts(task_id: str, session_id: Optional[str] = None):
    """
    🧠 SSE endpoint for streaming AI thoughts during marathon task execution.
    
    Returns Server-Sent Events (SSE) stream with:
    - `thought`: Individual thought bubbles showing AI reasoning
    - `progress`: Overall progress updates
    - `complete`: Final completion event with results
    - `error`: Error events if something fails
    
    Example usage:
    ```javascript
    const eventSource = new EventSource('/api/v1/marathon/stream/task-123');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'thought') {
            displayThoughtBubble(data);
        }
    };
    ```
    """
    # Verify task exists
    status = orchestrator.get_session_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    logger.info(f"Starting SSE stream for task {task_id}")
    
    return StreamingResponse(
        generate_thought_stream(task_id, session_id or task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.get("/marathon/thoughts/{task_id}", tags=["Marathon Agent"])
async def get_task_thoughts(task_id: str):
    """
    Get accumulated thought history for a task.
    
    Returns all thought bubbles generated during task execution.
    Useful for displaying thought history after SSE connection ends.
    """
    status = orchestrator.get_session_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Build thoughts from checkpoints
    thoughts = []
    checkpoints = status.get("checkpoints", [])
    
    for i, cp in enumerate(checkpoints):
        stage = cp.get("stage", "unknown")
        thoughts.append({
            "id": f"thought-{task_id}-{i+1}",
            "step": i + 1,
            "type": get_thought_type(stage),
            "title": get_stage_title(stage),
            "details": [],
            "confidence": 0.85 + (i * 0.02),
            "timestamp": cp.get("timestamp"),
            "status": "completed",
        })
    
    # Add current stage if not completed
    current_stage = status.get("current_stage")
    if current_stage and current_stage not in ["completed", "failed"]:
        thoughts.append({
            "id": f"thought-{task_id}-{len(thoughts)+1}",
            "step": len(thoughts) + 1,
            "type": get_thought_type(current_stage),
            "title": get_stage_title(current_stage),
            "details": [],
            "status": "active",
        })
    
    return {
        "task_id": task_id,
        "thoughts": thoughts,
        "total_thoughts": len(thoughts),
        "status": status.get("current_stage", "unknown"),
    }


# === MULTI-AGENT DEBATE ENDPOINTS ===

class DebateRequest(BaseModel):
    """Request for running a multi-agent debate."""
    topic: str
    item_data: Dict = {}
    context: Dict = {}


@router.post("/marathon/debate", tags=["Marathon Agent"])
async def run_debate(request: DebateRequest):
    """
    🤔 Run a multi-agent AI debate on a strategic decision.
    
    Three AI personas (CFO, Growth Strategist, Customer-Centric Marketer)
    debate the topic and reach a consensus.
    
    Example:
    ```json
    {
        "topic": "Should we remove 'Sopa del Día' from the menu?",
        "item_data": {"name": "Sopa del Día", "category": "dog", "margin": 0.15},
        "context": {"bcg_analysis": {...}}
    }
    ```
    """
    from app.services.gemini.reasoning_agent import ReasoningAgent
    
    try:
        agent = ReasoningAgent()
        debate = await agent.multi_agent_debate(
            topic=request.topic,
            item_data=request.item_data,
            context=request.context,
        )
        return debate
    except Exception as e:
        logger.error(f"Debate failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marathon/debates/bcg/{session_id}", tags=["Marathon Agent"])
async def run_bcg_debates(session_id: str, max_debates: int = 5):
    """
    🎯 Run multi-agent debates for BCG items that need strategic attention.
    
    Automatically identifies Dogs, Puzzles, and Plowhorses and runs
    debates to determine the best course of action.
    
    Returns a list of debate results with consensus recommendations.
    """
    from app.services.gemini.reasoning_agent import ReasoningAgent
    from app.api.deps import load_session
    
    try:
        # Load session data
        session_data = load_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get BCG items
        bcg_data = session_data.get("bcg_analysis") or session_data.get("bcg", {})
        bcg_items = bcg_data.get("items", [])
        
        if not bcg_items:
            return {
                "session_id": session_id,
                "debates": [],
                "message": "No BCG items found for debate"
            }
        
        # Run debates
        agent = ReasoningAgent()
        debates = await agent.run_bcg_debates(
            bcg_items=bcg_items,
            context={
                "session_id": session_id,
                "restaurant_name": session_data.get("restaurant_name", "Restaurant"),
            },
            max_debates=max_debates,
        )
        
        return {
            "session_id": session_id,
            "debates": debates,
            "total_debates": len(debates),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BCG debates failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marathon/debates/{session_id}", tags=["Marathon Agent"])
async def get_session_debates(session_id: str):
    """
    Get all debates stored for a session.
    
    Returns previously generated debate results.
    """
    from app.api.deps import load_session
    
    session_data = load_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    debates = session_data.get("debates", [])
    
    return {
        "session_id": session_id,
        "debates": debates,
        "total_debates": len(debates),
    }

