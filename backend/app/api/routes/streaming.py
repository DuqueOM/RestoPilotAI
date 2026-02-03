"""
Streaming Analysis Endpoints - Real-time Thought Visualization.

Provides Server-Sent Events (SSE) endpoints for streaming analysis
with visible chain-of-thought reasoning.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from loguru import logger

from app.services.gemini.streaming_reasoning import (
    StreamingReasoningAgent,
    stream_analysis_to_sse
)


router = APIRouter(prefix="/streaming", tags=["streaming"])


# ==================== Request/Response Models ====================

class StreamingAnalysisRequest(BaseModel):
    """Request for streaming BCG analysis."""
    sales_data: List[Dict[str, Any]]
    menu_data: List[Dict[str, Any]]
    market_context: Optional[Dict[str, Any]] = None
    enable_multi_perspective: bool = True


# ==================== Endpoints ====================

@router.post("/analysis/bcg")
async def stream_bcg_analysis(request: StreamingAnalysisRequest):
    """
    🌊 Stream BCG analysis with real-time thought visualization.
    
    Returns Server-Sent Events (SSE) stream showing the AI's reasoning
    process as it happens.
    
    **WOW Factor**: Users see the AI "thinking" in real-time.
    
    Example usage:
    ```javascript
    const eventSource = new EventSource('/api/v1/streaming/analysis/bcg');
    eventSource.onmessage = (event) => {
        const thought = JSON.parse(event.data);
        console.log(thought.content);
    };
    ```
    """
    
    try:
        # Validate input
        if not request.sales_data:
            raise HTTPException(status_code=400, detail="sales_data is required")
        
        if not request.menu_data:
            raise HTTPException(status_code=400, detail="menu_data is required")
        
        logger.info(
            "streaming_analysis_started",
            products=len(request.sales_data),
            multi_perspective=request.enable_multi_perspective
        )
        
        # Initialize streaming agent
        agent = StreamingReasoningAgent()
        
        # Stream analysis
        return StreamingResponse(
            stream_analysis_to_sse(
                agent=agent,
                sales_data=request.sales_data,
                menu_data=request.menu_data,
                market_context=request.market_context
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        logger.error("streaming_analysis_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def streaming_health():
    """Health check for streaming endpoints."""
    return {
        "status": "healthy",
        "streaming_enabled": True,
        "features": [
            "bcg_analysis_streaming",
            "thought_visualization",
            "real_time_reasoning"
        ]
    }
