from datetime import datetime
from google import genai
from google.genai import types
from fastapi import WebSocket
from app.core.config import get_settings

class StreamingAgent:
    """
    Implementa streaming de respuestas para transparencia del pensamiento.
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"

    async def stream_analysis(
        self,
        prompt: str,
        client_websocket: WebSocket
    ):
        """
        Stream de análisis en tiempo real.
        El usuario VE el pensamiento del modelo mientras se genera.
        """
        
        try:
            # Note: The exact async iterator for streaming might depend on the SDK version.
            # Assuming standard generate_content_stream usage.
            # We use the lower level client model interaction.
            
            async for chunk in await self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt
            ):
                # Enviar chunk al frontend vía WebSocket
                if chunk.text:
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
            # Gracefully handle streaming errors
            await client_websocket.send_json({
                "type": "error",
                "content": str(e),
                "timestamp": datetime.now().isoformat()
            })
