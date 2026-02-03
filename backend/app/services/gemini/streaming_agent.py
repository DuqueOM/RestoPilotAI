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
    Implementa streaming de respuestas Gemini 3 para transparencia del pensamiento.
    
    Características:
    - Streaming en tiempo real de respuestas multimodales
    - Buffer inteligente para chunks pequeños
    - Caché de respuestas completas
    - Manejo robusto de errores
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"
        self.chunk_buffer_size = 50  # Buffer pequeños chunks para mejor UX

    async def stream_analysis(
        self,
        prompt: str,
        client_websocket: WebSocket,
        images: Optional[List[bytes]] = None,
        system_instruction: Optional[str] = None,
        cache_key: Optional[str] = None
    ):
        """
        Stream de análisis en tiempo real con soporte multimodal.
        El usuario VE el pensamiento del modelo mientras se genera.
        
        Args:
            prompt: Texto del prompt
            client_websocket: WebSocket para enviar chunks
            images: Imágenes opcionales para análisis multimodal
            system_instruction: Instrucción del sistema
            cache_key: Clave para cachear la respuesta completa
        """
        full_response = []
        buffer = ""
        
        try:
            # Preparar contenido multimodal
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
            
            # Stream con Gemini 3
            response_stream = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(parts=parts)],
                config=types.GenerateContentConfig(**config_kwargs)
            )
            
            # Procesar chunks con buffering inteligente
            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    buffer += chunk.text
                    full_response.append(chunk.text)
                    
                    # Enviar cuando el buffer alcanza el tamaño mínimo
                    if len(buffer) >= self.chunk_buffer_size:
                        await client_websocket.send_json({
                            "type": "thinking_chunk",
                            "content": buffer,
                            "timestamp": datetime.now().isoformat()
                        })
                        buffer = ""
            
            # Enviar buffer restante
            if buffer:
                await client_websocket.send_json({
                    "type": "thinking_chunk",
                    "content": buffer,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Señal de completado
            await client_websocket.send_json({
                "type": "thinking_complete",
                "timestamp": datetime.now().isoformat()
            })
            
            # Cachear respuesta completa si se proporciona cache_key
            if cache_key:
                complete_text = "".join(full_response)
                cache_manager = await get_cache_manager()
                await cache_manager.set(
                    cache_key,
                    complete_text,
                    l1_ttl=1800,  # 30 min en L1
                    l2_ttl=3600,  # 1 hora en L2
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
        Stream con soporte para function calling de Gemini 3.
        Útil para agentes que necesitan ejecutar herramientas durante el streaming.
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
                # Manejar function calls
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
                
                # Manejar texto
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
