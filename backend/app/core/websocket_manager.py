"""
WebSocket Manager Core Module.

Handles WebSocket connections and broadcasting of events.
Separated from api/websocket.py to avoid circular imports.
"""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket
from loguru import logger


class ThoughtType(str, Enum):
    """Types of thoughts that can be streamed to the frontend."""

    THINKING = "thinking"
    OBSERVATION = "observation"
    ACTION = "action"
    VERIFICATION = "verification"
    RESULT = "result"


class PipelineStage(str, Enum):
    """Stages of the analysis pipeline."""

    INITIALIZED = "initialized"
    DATA_INGESTION = "data_ingestion"
    MENU_EXTRACTION = "menu_extraction"
    COMPETITOR_DISCOVERY = "competitor_discovery"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    IMAGE_ANALYSIS = "image_analysis"
    VISUAL_GAP_ANALYSIS = "visual_gap_analysis"
    SALES_PROCESSING = "sales_processing"
    BCG_CLASSIFICATION = "bcg_classification"
    SALES_PREDICTION = "sales_prediction"
    CAMPAIGN_GENERATION = "campaign_generation"
    VERIFICATION = "verification"
    COMPLETED = "completed"
    FAILED = "failed"


class ConnectionManager:
    """Manages WebSocket connections for session-based updates."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

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


async def send_thought(
    session_id: str,
    thought_type: ThoughtType,
    content: str,
    step: Optional[str] = None,
    confidence: Optional[float] = None,
) -> None:
    """Send a thought to all WebSocket connections for a session."""
    thought_id = f"{thought_type.value}-{uuid.uuid4().hex[:8]}"

    message = {
        "type": "thought",
        "session_id": session_id,
        "thought": {
            "id": thought_id,
            "type": thought_type.value,
            "content": content,
            "step": step,
            "confidence": confidence,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.send_to_session(session_id, message)


async def send_progress_update(
    session_id: str,
    stage: str,
    progress: float,
    message: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Send progress update."""
    update = {
        "type": "progress",
        "session_id": session_id,
        "stage": stage,
        "progress": progress,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if data:
        update["data"] = data

    await manager.send_to_session(session_id, update)


async def send_stage_complete(
    session_id: str,
    stage: str,
    result: Dict[str, Any],
) -> None:
    """Send stage completion notification."""
    await manager.send_to_session(
        session_id,
        {
            "type": "stage_complete",
            "session_id": session_id,
            "stage": stage,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def send_error(
    session_id: str,
    stage: str,
    error: str,
) -> None:
    """Send error notification."""
    await manager.send_to_session(
        session_id,
        {
            "type": "error",
            "session_id": session_id,
            "stage": stage,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
