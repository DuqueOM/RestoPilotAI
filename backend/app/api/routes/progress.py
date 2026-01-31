"""
WebSocket Endpoints for Real-time Progress Updates.

Provides real-time communication for:
- Analysis pipeline progress
- Long-running task updates
- Live verification status
"""

import asyncio
import base64
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.core.websocket_manager import ThoughtType, manager, send_thought
from app.services.orchestrator import orchestrator
from app.services.gemini.base_agent import ThinkingLevel

router = APIRouter()


async def send_thinking_sequence(
    session_id: str,
    step: str,
    thoughts: List[Dict[str, Any]],
    delay_ms: int = 500,
) -> None:
    """
    Send a sequence of thoughts with delays for visual effect.

    Args:
        session_id: The session to send thoughts to
        step: The current analysis step name
        thoughts: List of dicts with 'type', 'content', and optional 'confidence'
        delay_ms: Delay between thoughts in milliseconds
    """
    for thought in thoughts:
        await send_thought(
            session_id=session_id,
            thought_type=ThoughtType(thought.get("type", "thinking")),
            content=thought["content"],
            step=step,
            confidence=thought.get("confidence"),
        )
        await asyncio.sleep(delay_ms / 1000)


@router.websocket("/ws/analysis/{session_id}")
async def analysis_progress_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time analysis progress updates.
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
                try:
                    await websocket.send_json(
                        {
                            "type": "heartbeat",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                except Exception:
                    break

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(websocket, session_id)


@router.websocket("/ws/live/{session_id}")
async def live_analysis_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for live analysis with real-time updates.
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
    try:
        # Decode images if present
        decoded_images = []
        for img_str in menu_images:
            if isinstance(img_str, str):
                if "," in img_str:
                    img_str = img_str.split(",")[1]
                decoded_images.append(base64.b64decode(img_str))

        # Parse thinking level
        try:
            level = ThinkingLevel(thinking_level)
        except ValueError:
            level = ThinkingLevel.STANDARD

        # Run pipeline
        result = await orchestrator.run_full_pipeline(
            session_id=session_id,
            menu_images=decoded_images if decoded_images else None,
            sales_csv=sales_data,
            thinking_level=level,
        )

        if "error" in result:
            await manager.send_to_session(
                session_id,
                {
                    "type": "error",
                    "session_id": session_id,
                    "message": result["error"],
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
        else:
            await manager.send_to_session(
                session_id,
                {
                    "type": "completed",
                    "session_id": session_id,
                    "progress": 100,
                    "message": "Analysis completed successfully",
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result,
                },
            )

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        await manager.send_to_session(
            session_id,
            {
                "type": "error",
                "session_id": session_id,
                "message": str(e),
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
