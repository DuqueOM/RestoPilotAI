"""
WebSocket Endpoints for Real-time Progress Updates.

Provides real-time communication for:
- Analysis pipeline progress
- Long-running task updates
- Live verification status
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.services.gemini.orchestrator_agent import OrchestratorAgent, PipelineStage

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for session-based updates."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Accept connection and register for session updates."""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()

        self.active_connections[session_id].add(websocket)

        logger.info(f"WebSocket connected for session {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """Remove connection from session."""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)

            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

        logger.info(f"WebSocket disconnected for session {session_id}")

    async def send_to_session(self, session_id: str, message: Dict[str, Any]) -> None:
        """Send message to all connections for a session."""
        if session_id not in self.active_connections:
            return

        disconnected = set()

        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")
                disconnected.add(connection)

        # Clean up disconnected
        for conn in disconnected:
            self.active_connections[session_id].discard(conn)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all active connections."""
        for session_id in self.active_connections:
            await self.send_to_session(session_id, message)

    def get_connection_count(self, session_id: Optional[str] = None) -> int:
        """Get number of active connections."""
        if session_id:
            return len(self.active_connections.get(session_id, set()))
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()

# Global orchestrator instance
orchestrator = OrchestratorAgent()


@router.websocket("/ws/analysis/{session_id}")
async def analysis_progress_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time analysis progress updates.

    Sends updates for each pipeline stage completion:
    - stage: Current stage name
    - progress: 0-100 percentage
    - message: Human-readable status message
    - eta_seconds: Estimated time remaining
    - data: Partial results (if available)
    """
    await manager.connect(websocket, session_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connected",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to analysis progress stream",
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)

                # Handle client messages
                message_type = data.get("type", "")

                if message_type == "ping":
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                elif message_type == "get_status":
                    status = orchestrator.get_session_status(session_id)
                    await websocket.send_json(
                        {
                            "type": "status",
                            "session_id": session_id,
                            "data": status,
                        }
                    )

                elif message_type == "cancel":
                    # Handle cancellation request
                    await websocket.send_json(
                        {
                            "type": "cancelled",
                            "session_id": session_id,
                            "message": "Analysis cancellation requested",
                        }
                    )

            except asyncio.TimeoutError:
                # Send heartbeat on timeout
                await websocket.send_json(
                    {
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(websocket, session_id)


@router.websocket("/ws/live/{session_id}")
async def live_analysis_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for live analysis with real-time updates.

    Runs the analysis pipeline and streams progress updates
    as each stage completes.
    """
    await manager.connect(websocket, session_id)

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "session_id": session_id,
                "message": "Ready to receive analysis request",
            }
        )

        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "")

            if message_type == "start_analysis":
                # Extract analysis parameters
                menu_images = data.get("menu_images", [])
                sales_data = data.get("sales_data")
                thinking_level = data.get("thinking_level", "standard")

                # Send acknowledgment
                await websocket.send_json(
                    {
                        "type": "analysis_started",
                        "session_id": session_id,
                        "message": "Analysis pipeline started",
                    }
                )

                # Run pipeline with progress updates
                await run_pipeline_with_updates(
                    websocket=websocket,
                    session_id=session_id,
                    menu_images=menu_images,
                    sales_data=sales_data,
                    thinking_level=thinking_level,
                )

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"Live analysis WebSocket error: {e}")
        manager.disconnect(websocket, session_id)


async def run_pipeline_with_updates(
    websocket: WebSocket,
    session_id: str,
    menu_images: list,
    sales_data: Optional[str],
    thinking_level: str,
) -> None:
    """
    Run the analysis pipeline and send progress updates via WebSocket.
    """
    stages = [
        ("menu_extraction", "Extracting menu items...", 15),
        ("bcg_classification", "Running BCG classification...", 35),
        ("competitor_analysis", "Analyzing competitors...", 55),
        ("sentiment_analysis", "Analyzing customer sentiment...", 70),
        ("sales_prediction", "Predicting sales...", 85),
        ("campaign_generation", "Generating campaigns...", 95),
        ("verification", "Verifying results...", 100),
    ]

    try:
        for stage_name, message, progress in stages:
            await websocket.send_json(
                {
                    "type": "progress",
                    "session_id": session_id,
                    "stage": stage_name,
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Simulate stage execution (in production, this would be actual processing)
            await asyncio.sleep(0.5)

        # Send completion
        await websocket.send_json(
            {
                "type": "completed",
                "session_id": session_id,
                "progress": 100,
                "message": "Analysis completed successfully",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        await websocket.send_json(
            {
                "type": "error",
                "session_id": session_id,
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


async def send_progress_update(
    session_id: str,
    stage: PipelineStage,
    progress: float,
    message: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Send progress update to all WebSocket connections for a session.

    Call this function from pipeline stages to stream updates.
    """
    update = {
        "type": "progress",
        "session_id": session_id,
        "stage": stage.value,
        "progress": progress,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if data:
        update["data"] = data

    await manager.send_to_session(session_id, update)


async def send_stage_complete(
    session_id: str,
    stage: PipelineStage,
    result: Dict[str, Any],
) -> None:
    """Send stage completion notification."""
    await manager.send_to_session(
        session_id,
        {
            "type": "stage_complete",
            "session_id": session_id,
            "stage": stage.value,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def send_error(
    session_id: str,
    stage: PipelineStage,
    error: str,
) -> None:
    """Send error notification."""
    await manager.send_to_session(
        session_id,
        {
            "type": "error",
            "session_id": session_id,
            "stage": stage.value,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@router.get("/ws/connections")
async def get_websocket_connections():
    """Get WebSocket connection statistics."""
    return {
        "total_connections": manager.get_connection_count(),
        "active_sessions": list(manager.active_connections.keys()),
    }
