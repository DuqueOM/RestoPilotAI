from datetime import datetime
from typing import Optional, List
from google import genai
from google.genai import types
from fastapi import WebSocket
from loguru import logger
from app.core.config import get_settings
from app.core.cache import get_cache_manager

class StreamingAgent:
    """
    Implements Gemini 3 response streaming for transparent model thinking.
    
    Features:
    - Real-time streaming of multimodal responses
    - Smart buffering for small chunks
    - Full-response caching
    - Robust error handling
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"
        self.chunk_buffer_size = 50  # Buffer small chunks for better UX

    async def stream_analysis(
        self,
        prompt: str,
        client_websocket: WebSocket,
        images: Optional[List[bytes]] = None,
        system_instruction: Optional[str] = None,
        cache_key: Optional[str] = None
    ):
        """
        Real-time analysis stream with multimodal support.
        The user SEES the model's thinking while it is being generated.
        
        Args:
            prompt: Prompt text
            client_websocket: WebSocket used to send chunks
            images: Optional images for multimodal analysis
            system_instruction: System instruction
            cache_key: Key to cache the complete response
        """
        full_response = []
        buffer = ""
        
        try:
            # Prepare multimodal content
            parts = [types.Part(text=prompt)]
            
            if images:
                for img_bytes in images:
                    parts.append(
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/jpeg",
                                data=img_bytes
                            )
                        )
                    )
            
            config_kwargs = {
                "temperature": 0.7,
                "max_output_tokens": 8192
            }
            
            if system_instruction:
                config_kwargs["system_instruction"] = system_instruction
            
            # Stream with Gemini 3
            response_stream = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(parts=parts)],
                config=types.GenerateContentConfig(**config_kwargs)
            )
            
            # Process chunks with smart buffering
            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    buffer += chunk.text
                    full_response.append(chunk.text)
                    
                    # Send when the buffer reaches the minimum size
                    if len(buffer) >= self.chunk_buffer_size:
                        await client_websocket.send_json({
                            "type": "thinking_chunk",
                            "content": buffer,
                            "timestamp": datetime.now().isoformat()
                        })
                        buffer = ""
            
            # Send remaining buffer
            if buffer:
                await client_websocket.send_json({
                    "type": "thinking_chunk",
                    "content": buffer,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Completion signal
            await client_websocket.send_json({
                "type": "thinking_complete",
                "timestamp": datetime.now().isoformat()
            })
            
            # Cache full response if cache_key is provided
            if cache_key:
                complete_text = "".join(full_response)
                cache_manager = await get_cache_manager()
                await cache_manager.set(
                    cache_key,
                    complete_text,
                    l1_ttl=1800,  # 30 min in L1
                    l2_ttl=3600,  # 1 hour in L2
                    tags=["gemini_stream"]
                )
                logger.info(f"Streamed response cached: {cache_key}")
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            await client_websocket.send_json({
                "type": "error",
                "content": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def stream_with_function_calling(
        self,
        prompt: str,
        client_websocket: WebSocket,
        tools: Optional[List[types.Tool]] = None
    ):
        """
        Stream with Gemini 3 function-calling support.
        Useful for agents that need to execute tools during streaming.
        """
        try:
            config_kwargs = {
                "temperature": 0.7,
                "max_output_tokens": 8192
            }
            
            if tools:
                config_kwargs["tools"] = tools
            
            response_stream = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs)
            )
            
            for chunk in response_stream:
                # Handle function calls
                if hasattr(chunk, 'candidates') and chunk.candidates:
                    for candidate in chunk.candidates:
                        if hasattr(candidate, 'content') and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'function_call'):
                                    await client_websocket.send_json({
                                        "type": "function_call",
                                        "function_name": part.function_call.name,
                                        "arguments": dict(part.function_call.args),
                                        "timestamp": datetime.now().isoformat()
                                    })
                
                # Handle text
                if hasattr(chunk, 'text') and chunk.text:
                    await client_websocket.send_json({
                        "type": "thinking_chunk",
                        "content": chunk.text,
                        "timestamp": datetime.now().isoformat()
                    })
            
            await client_websocket.send_json({
                "type": "thinking_complete",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Function calling stream error: {e}")
            await client_websocket.send_json({
                "type": "error",
                "content": str(e),
                "timestamp": datetime.now().isoformat()
            })


# Singleton instance
_streaming_agent: Optional[StreamingAgent] = None

def get_streaming_agent() -> StreamingAgent:
    """Get or create global streaming agent instance."""
    global _streaming_agent
    if _streaming_agent is None:
        _streaming_agent = StreamingAgent()
    return _streaming_agent
