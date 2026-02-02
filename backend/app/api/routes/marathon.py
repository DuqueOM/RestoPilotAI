from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.services.orchestrator import orchestrator, PipelineStage, AnalysisState
from app.services.gemini.base_agent import ThinkingLevel
from loguru import logger

"""
Marathon Agent API Routes - Long-running task execution with checkpoints.

Includes WebSocket support for real-time progress updates.
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
    input_data: Dict
    enable_checkpoints: bool = True
    checkpoint_interval_seconds: int = 60
    max_retries_per_step: int = 3

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
        
        # Dispatch based on task_type
        if config.task_type == "full_analysis":
            # Extract parameters from input_data
            input_data = config.input_data
            
            # Start Orchestrator Pipeline in background
            # Note: orchestrator.run_full_pipeline is async, so we wrap it or fire-and-forget
            # But run_full_pipeline is designed to run completely. 
            # Ideally we run it in a background task to not block response.
            
            # Map input_data to orchestrator arguments
            # This mapping depends on what the frontend sends.
            # Assuming input_data contains keys matching run_full_pipeline args roughly
            
            # For simplicity in this integration, we'll assume basic args for now
            # In a real app, strict mapping is needed.
            
            background_tasks.add_task(
                orchestrator.run_full_pipeline,
                session_id=session_id,
                sales_csv=input_data.get("sales_csv"),
                # We might need to handle file uploads differently if they aren't passed here
                # The frontend hook assumes input_data is JSON. 
                # If files are needed, they should have been uploaded previously 
                # and paths passed here, or separate endpoints used.
                thinking_level=ThinkingLevel.STANDARD, 
                auto_verify=True
            )
            
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
    
    if current_stage not in ["completed", "failed"] and current_stage != "initialized":
        steps.append({
            "step_id": f"step_{len(steps)}",
            "name": current_stage,
            "description": "Processing...",
            "status": "running",
            "started_at": status.get("started_at"), # Approximation
            "retry_count": 0,
            "max_retries": 3
        })

    return {
        "task_id": task_id,
        "status": map_status(current_stage),
        "progress": progress,
        "current_step": stages_completed + 1,
        "total_steps": total_stages_est,
        "current_step_name": current_stage,
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
    await manager.connect(websocket, task_id)
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
        manager.disconnect(websocket, task_id)
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        manager.disconnect(websocket, task_id)
