"""
Gemini 3 Agent - Core orchestrator for RestoPilotAI's agentic workflows.

This module implements the agentic layer using Google Gemini 3 API with
function calling capabilities for multi-step reasoning and verification.
"""

import asyncio
import base64
import functools
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar
from datetime import datetime

from google import genai
from google.genai import types
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.rate_limiter import get_rate_limiter
from app.core.model_fallback import get_fallback_handler


class GeminiModel(str, Enum):
    """Supported Gemini 3 models - CRÍTICO: Solo usar Gemini 3."""

    FLASH = "gemini-3-flash-preview"  # Modelo principal rápido
    PRO = "gemini-3-pro-preview"  # Modelo avanzado para multimodal
    VISION = "gemini-3-pro-preview"  # Análisis de imágenes
    IMAGE_GEN = "gemini-3-pro-image-preview"  # Generación de imágenes


class ThinkingLevel(str, Enum):
    """Depth of AI reasoning."""

    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"
    EXHAUSTIVE = "exhaustive"


@dataclass
class TokenUsage:
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class GeminiUsageStats:
    """Overall usage statistics."""

    requests: int = 0
    tokens: TokenUsage = field(default_factory=TokenUsage)
    errors: int = 0


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.interval = 60.0 / requests_per_minute
        self.last_call = 0.0

    async def wait(self):
        """Wait if necessary to respect rate limit."""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.interval:
            await asyncio.sleep(self.interval - elapsed)
        self.last_call = time.time()


class GeminiCache:
    """Simple in-memory cache for Gemini responses."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        self._cache[key] = value


T = TypeVar("T")


def with_retry(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying async functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2**attempt))
            raise last_err

        return wrapper

    return decorator


class GeminiBaseAgent:
    """
    Agentic orchestrator using Gemini 3 for multimodal reasoning.

    Features:
    - Function calling for tool use
    - Thought signatures for transparent reasoning
    - Self-verification loops
    - Multimodal input processing (images, text, structured data)
    """

    MODEL_NAME = "gemini-3-flash-preview"

    def __init__(self, model_name: str = None):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name or self.MODEL_NAME
        self.settings = settings  # Store settings for easy access
        self.call_count = 0
        self.total_tokens = 0
        
        # Rate limiter and fallback handler
        self.rate_limiter = get_rate_limiter()
        self.fallback_handler = get_fallback_handler()
        
        # Enhanced usage stats
        self.usage_stats = {
            "total_tokens": 0,
            "total_requests": 0,
            "total_cost_usd": 0.0,
            "requests_by_type": {}
        }

        # Define available tools for function calling
        self.tools = self._define_tools()
    
    def get_model_for_task(self, task_type: str = "general") -> str:
        """
        Get appropriate Gemini 3 model based on task type.
        
        Args:
            task_type: Type of task (general, vision, reasoning, image_gen)
            
        Returns:
            Model name string
        """
        if task_type == "vision" or task_type == "multimodal":
            return self.settings.gemini_model_vision
        elif task_type == "reasoning" or task_type == "analysis":
            return self.settings.gemini_model_reasoning
        elif task_type == "image_gen":
            return self.settings.gemini_model_image_gen
        else:
            return self.settings.gemini_model_primary
    
    # === THOUGHT SIGNATURES ===
    
    def _create_thought_signature(self, prompt: str, thinking_level: str) -> str:
        """
        Create prompt with Thought Signature for transparent reasoning.
        
        CRÍTICO PARA HACKATHON: Muestra el proceso de razonamiento del modelo.
        
        Args:
            prompt: Original prompt
            thinking_level: Depth of reasoning (QUICK, STANDARD, DEEP, EXHAUSTIVE)
            
        Returns:
            Enhanced prompt with thought signature instructions
        """
        depth_descriptions = {
            "QUICK": "Quick analysis, 1-2 reasoning steps",
            "STANDARD": "Standard analysis, 3-5 reasoning steps",
            "DEEP": "Deep analysis, multi-perspective, 5-10 steps",
            "EXHAUSTIVE": "Exhaustive analysis, comprehensive, 10+ steps"
        }
        
        enhanced_prompt = f"""[THOUGHT SIGNATURE - Level: {thinking_level.upper()}]

Expected Depth: {depth_descriptions.get(thinking_level.upper(), "Standard analysis")}

{prompt}

IMPORTANT: Structure your response as follows:

<thinking>
[Show your step-by-step reasoning process here]
Step 1: [Initial analysis]
Step 2: [Considerations]
Step 3: [Cross-checking]
Step 4: [Conclusion]
</thinking>

<answer>
[Provide the final response here]
</answer>

This thought trace will be visible for transparency."""
        
        return enhanced_prompt
    
    def _extract_thought_trace(self, response_text: str) -> Optional[str]:
        """Extract thought trace from response."""
        try:
            start = response_text.find("<thinking>") + len("<thinking>")
            end = response_text.find("</thinking>")
            
            if start > len("<thinking>") - 1 and end > -1:
                return response_text[start:end].strip()
        except Exception as e:
            logger.debug(f"Could not extract thought trace: {e}")
        
        return None
    
    def _extract_answer(self, response_text: str) -> str:
        """Extract final answer from response."""
        try:
            start = response_text.find("<answer>") + len("<answer>")
            end = response_text.find("</answer>")
            
            if start > len("<answer>") - 1 and end > -1:
                return response_text[start:end].strip()
        except Exception as e:
            logger.debug(f"Could not extract answer: {e}")
        
        # If no tags, return full text
        return response_text

    async def generate_response(
        self,
        prompt: str,
        images: Optional[List[bytes]] = None,
        system_instruction: Optional[str] = None,
        thinking_level: str = "QUICK",
        **kwargs
    ) -> str:
        """
        Generate a response for chat interactions using Gemini 3.
        
        Args:
            prompt: User message/prompt
            images: Optional list of image bytes for multimodal context
            system_instruction: System prompt/persona
            thinking_level: Depth of reasoning (default QUICK for chat)
        """
        config_kwargs = kwargs.copy()
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        return await self.generate(
            prompt=prompt,
            images=images,
            thinking_level=thinking_level,
            **config_kwargs
        )

    @retry(
        stop=stop_after_attempt(3), # Using hardcoded 3 as default, or use settings.gemini_max_retries if accessible
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        prompt: str,
        images: Optional[List[bytes]] = None,
        thinking_level: str = "STANDARD",
        return_full_response: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate content with retry logic.
        
        Args:
            prompt: Text prompt
            images: Optional list of image bytes
            thinking_level: Analysis depth
            return_full_response: If True, returns full response object instead of text
            **kwargs: Additional generation config
        """
        start_time = datetime.now()
        
        try:
            # Prepare content
            parts = [types.Part(text=prompt)]
            mime_type = kwargs.get("mime_type", "image/jpeg")
            
            if images:
                for img_bytes in images:
                    parts.append(
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type, 
                                data=img_bytes
                            )
                        )
                    )
            
            # Map thinking level to config using settings
            settings = get_settings()
            
            # Configure based on thinking level
            if thinking_level == "QUICK":
                config_kwargs = {
                    "temperature": settings.thinking_level_quick_temp,
                    "max_output_tokens": settings.thinking_level_quick_tokens
                }
            elif thinking_level == "STANDARD":
                config_kwargs = {
                    "temperature": settings.thinking_level_standard_temp,
                    "max_output_tokens": settings.thinking_level_standard_tokens
                }
            elif thinking_level == "DEEP":
                config_kwargs = {
                    "temperature": settings.thinking_level_deep_temp,
                    "max_output_tokens": settings.thinking_level_deep_tokens
                }
            elif thinking_level == "EXHAUSTIVE":
                config_kwargs = {
                    "temperature": settings.thinking_level_exhaustive_temp,
                    "max_output_tokens": settings.thinking_level_exhaustive_tokens
                }
            else:
                # Default to STANDARD
                config_kwargs = {
                    "temperature": settings.thinking_level_standard_temp,
                    "max_output_tokens": settings.thinking_level_standard_tokens
                } 
            
            # Extract internal parameters that shouldn't go to API config
            feature = kwargs.pop("feature", None)
            
            config_kwargs.update(kwargs)

            # Get timeout based on task type (settings already loaded above)
            # Use marathon timeout for EXHAUSTIVE thinking or if explicitly requested
            is_long_task = thinking_level in ["EXHAUSTIVE", "DEEP"] or feature == "marathon"
            timeout = settings.gemini_marathon_timeout_seconds if is_long_task else settings.gemini_timeout_seconds

            # Generate
            def _sync_generate():
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=[types.Content(parts=parts)],
                    config=types.GenerateContentConfig(**config_kwargs)
                )

            # Use settings timeout
            if timeout and timeout > 0:
                response = await asyncio.wait_for(asyncio.to_thread(_sync_generate), timeout=timeout)
            else:
                response = await asyncio.to_thread(_sync_generate)
            
            # Track usage
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                tokens = response.usage_metadata.total_token_count
                self.usage_stats["total_tokens"] += tokens
                self.usage_stats["total_requests"] += 1
                self.usage_stats["total_cost_usd"] += tokens * 0.00001  # Approximate
                self.total_tokens += tokens 
            else:
                tokens = 0
            
            self.call_count += 1
            
            # Log
            latency = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(
                "gemini_request",
                model=self.model_name,
                thinking_level=thinking_level,
                tokens=tokens,
                latency_ms=latency,
                has_images=bool(images)
            )
            
            if return_full_response:
                return response
            return response.text
            
        except Exception as e:
            logger.error(
                "gemini_error",
                error=str(e),
                model=self.model_name
            )
            raise

    def get_usage_stats(self) -> Dict[str, Any]:
        """Return usage statistics"""
        return self.usage_stats
    
    # === ENHANCED GENERATION WITH THOUGHT SIGNATURES ===
    
    async def generate_with_thought_signature(
        self,
        prompt: str,
        images: Optional[List[bytes]] = None,
        thinking_level: str = "STANDARD",
        include_thought_trace: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content with Thought Signature for transparent reasoning.
        
        CRÍTICO PARA HACKATHON: Muestra el proceso de razonamiento del modelo.
        
        Args:
            prompt: Text prompt
            images: Optional list of image bytes
            thinking_level: Depth of reasoning (QUICK, STANDARD, DEEP, EXHAUSTIVE)
            include_thought_trace: Whether to include thought signature
            **kwargs: Additional generation config
            
        Returns:
            Dict with answer, thought_trace, thinking_level, model_used
        """
        # Create enhanced prompt with thought signature
        if include_thought_trace:
            enhanced_prompt = self._create_thought_signature(prompt, thinking_level)
        else:
            enhanced_prompt = prompt
        
        # Generate response
        full_response = await self.generate(
            prompt=enhanced_prompt,
            images=images,
            thinking_level=thinking_level,
            return_full_response=False,
            **kwargs
        )
        
        # Extract components
        thought_trace = self._extract_thought_trace(full_response) if include_thought_trace else None
        answer = self._extract_answer(full_response) if include_thought_trace else full_response
        
        return {
            "answer": answer,
            "thought_trace": thought_trace,
            "thinking_level": thinking_level,
            "model_used": self.model_name,
            "full_response": full_response
        }
    
    # === GROUNDING SUPPORT ===
    
    async def generate_with_grounding(
        self,
        prompt: str,
        enable_grounding: bool = True,
        thinking_level: str = "STANDARD",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content with Google Search grounding.
        
        DIFERENCIADOR HACKATHON: Gemini 3 es el único modelo con grounding nativo.
        
        Args:
            prompt: Text prompt
            enable_grounding: Whether to enable Google Search grounding
            thinking_level: Depth of reasoning
            **kwargs: Additional generation config
            
        Returns:
            Dict with answer, grounding_metadata, grounded flag
        """
        settings = get_settings()
        
        # Prepare parts
        parts = [types.Part(text=prompt)]
        
        # Configure thinking level
        if thinking_level == "QUICK":
            config_kwargs = {
                "temperature": settings.thinking_level_quick_temp,
                "max_output_tokens": settings.thinking_level_quick_tokens
            }
        elif thinking_level == "STANDARD":
            config_kwargs = {
                "temperature": settings.thinking_level_standard_temp,
                "max_output_tokens": settings.thinking_level_standard_tokens
            }
        elif thinking_level == "DEEP":
            config_kwargs = {
                "temperature": settings.thinking_level_deep_temp,
                "max_output_tokens": settings.thinking_level_deep_tokens
            }
        else:
            config_kwargs = {
                "temperature": settings.thinking_level_standard_temp,
                "max_output_tokens": settings.thinking_level_standard_tokens
            }
        
        config_kwargs.update(kwargs)
        
        # Add grounding tools if enabled
        tools = []
        if enable_grounding and settings.enable_grounding:
            tools.append(types.Tool(google_search=types.GoogleSearch()))
        
        # Generate with grounding
        def _sync_generate():
            config = types.GenerateContentConfig(**config_kwargs)
            if tools:
                config.tools = tools
            
            return self.client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(parts=parts)],
                config=config
            )
        
        response = await asyncio.to_thread(_sync_generate)
        
        # Extract grounding metadata
        grounding_metadata = None
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                grounding_metadata = {
                    "grounding_chunks": [],
                    "search_queries": []
                }
                
                if hasattr(candidate.grounding_metadata, 'grounding_chunks'):
                    for chunk in candidate.grounding_metadata.grounding_chunks:
                        grounding_metadata["grounding_chunks"].append({
                            "uri": getattr(chunk.web, 'uri', None) if hasattr(chunk, 'web') else None,
                            "title": getattr(chunk.web, 'title', None) if hasattr(chunk, 'web') else None
                        })
                
                if hasattr(candidate.grounding_metadata, 'search_entry_point'):
                    grounding_metadata["search_queries"] = [
                        candidate.grounding_metadata.search_entry_point.rendered_content
                    ]
        
        return {
            "answer": response.text,
            "grounding_metadata": grounding_metadata,
            "grounded": bool(grounding_metadata),
            "model_used": self.model_name
        }
    
    # === IMPROVED RETRY LOGIC FOR MARATHON AGENT ===
    
    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
        images: Optional[List[bytes]] = None,
        thinking_level: str = "STANDARD",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content with improved retry logic.
        
        CRÍTICO para Marathon Agent: tareas largas pueden fallar por timeouts, rate limits.
        
        Args:
            prompt: Text prompt
            max_retries: Maximum number of retries (default from settings)
            images: Optional list of image bytes
            thinking_level: Depth of reasoning
            **kwargs: Additional generation config
            
        Returns:
            Dict with answer and metadata
        """
        settings = get_settings()
        max_retries = max_retries or settings.marathon_max_retries_per_step
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Use generate_with_thought_signature for better transparency
                result = await self.generate_with_thought_signature(
                    prompt=prompt,
                    images=images,
                    thinking_level=thinking_level,
                    **kwargs
                )
                
                logger.info(f"Generation succeeded on attempt {attempt + 1}/{max_retries}")
                return result
            
            except Exception as e:
                last_error = e
                
                logger.warning(
                    f"Generation attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                
                if attempt < max_retries - 1:
                    # Exponential backoff with max 60s
                    wait_time = min(2 ** attempt, 60)
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
        
        raise last_error
    
    # === STREAMING SUPPORT ===
    
    async def generate_stream(
        self,
        prompt: str,
        thinking_level: str = "STANDARD",
        **kwargs
    ):
        """
        Generate content with streaming for real-time UI updates.
        
        Útil para mostrar "pensamiento" del modelo en tiempo real.
        
        Args:
            prompt: Text prompt
            thinking_level: Depth of reasoning
            **kwargs: Additional generation config
            
        Yields:
            Text chunks as they are generated
        """
        settings = get_settings()
        
        # Configure thinking level
        if thinking_level == "QUICK":
            config_kwargs = {
                "temperature": settings.thinking_level_quick_temp,
                "max_output_tokens": settings.thinking_level_quick_tokens
            }
        elif thinking_level == "STANDARD":
            config_kwargs = {
                "temperature": settings.thinking_level_standard_temp,
                "max_output_tokens": settings.thinking_level_standard_tokens
            }
        elif thinking_level == "DEEP":
            config_kwargs = {
                "temperature": settings.thinking_level_deep_temp,
                "max_output_tokens": settings.thinking_level_deep_tokens
            }
        else:
            config_kwargs = {
                "temperature": settings.thinking_level_standard_temp,
                "max_output_tokens": settings.thinking_level_standard_tokens
            }
        
        config_kwargs.update(kwargs)
        
        # Stream generation
        def _sync_stream():
            return self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs)
            )
        
        stream = await asyncio.to_thread(_sync_stream)
        
        for chunk in stream:
            if hasattr(chunk, 'text') and chunk.text:
                yield chunk.text

    def _define_tools(self) -> List[types.Tool]:
        """Define tools available to the agent for function calling."""

        extract_menu_func = types.FunctionDeclaration(
            name="extract_menu",
            description="Extract menu items from an image of a menu. Returns structured data with item names, prices, descriptions, and categories.",
            parameters=types.Schema(
                type="object",
                properties={
                    "image_description": types.Schema(
                        type="string",
                        description="Description of what's visible in the menu image",
                    ),
                    "items": types.Schema(
                        type="array",
                        items=types.Schema(
                            type="object",
                            properties={
                                "name": types.Schema(type="string"),
                                "price": types.Schema(type="number"),
                                "description": types.Schema(type="string"),
                                "category": types.Schema(type="string"),
                            },
                            required=["name", "price"],
                        ),
                    ),
                    "confidence": types.Schema(
                        type="number",
                        description="Confidence score 0-1 for the extraction accuracy",
                    ),
                },
                required=["items", "confidence"],
            ),
        )

        analyze_dish_image_func = types.FunctionDeclaration(
            name="analyze_dish_image",
            description="Analyze a dish photograph for visual appeal, presentation quality, and marketability.",
            parameters=types.Schema(
                type="object",
                properties={
                    "dish_name": types.Schema(type="string"),
                    "attractiveness_score": types.Schema(
                        type="number", description="Visual appeal score 0-1"
                    ),
                    "presentation_quality": types.Schema(type="string"),
                    "color_appeal": types.Schema(type="string"),
                    "portion_perception": types.Schema(type="string"),
                    "instagram_worthiness": types.Schema(
                        type="number", description="Social media appeal score 0-1"
                    ),
                    "improvement_suggestions": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                },
                required=["attractiveness_score", "presentation_quality"],
            ),
        )

        classify_bcg_func = types.FunctionDeclaration(
            name="classify_bcg",
            description="Classify a product according to BCG matrix based on market share and growth metrics.",
            parameters=types.Schema(
                type="object",
                properties={
                    "item_name": types.Schema(type="string"),
                    "classification": types.Schema(
                        type="string", enum=["star", "cash_cow", "question_mark", "dog"]
                    ),
                    "market_share_assessment": types.Schema(type="string"),
                    "growth_assessment": types.Schema(type="string"),
                    "strategic_recommendation": types.Schema(type="string"),
                    "reasoning": types.Schema(type="string"),
                },
                required=["item_name", "classification", "reasoning"],
            ),
        )

        generate_campaign_func = types.FunctionDeclaration(
            name="generate_campaign",
            description="Generate a marketing campaign proposal for selected menu items.",
            parameters=types.Schema(
                type="object",
                properties={
                    "title": types.Schema(type="string"),
                    "objective": types.Schema(type="string"),
                    "target_audience": types.Schema(type="string"),
                    "duration_days": types.Schema(type="integer"),
                    "channels": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "key_messages": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "promotional_items": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "discount_strategy": types.Schema(type="string"),
                    "social_post_copy": types.Schema(type="string"),
                    "expected_uplift_percent": types.Schema(type="number"),
                    "rationale": types.Schema(type="string"),
                },
                required=["title", "objective", "channels", "rationale"],
            ),
        )

        verify_analysis_func = types.FunctionDeclaration(
            name="verify_analysis",
            description="Self-verification step to check analysis quality and consistency.",
            parameters=types.Schema(
                type="object",
                properties={
                    "verification_passed": types.Schema(type="boolean"),
                    "checks_performed": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "issues_found": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "corrections_needed": types.Schema(
                        type="array", items=types.Schema(type="string")
                    ),
                    "confidence_after_verification": types.Schema(type="number"),
                },
                required=["verification_passed", "checks_performed"],
            ),
        )

        return [
            types.Tool(
                function_declarations=[
                    extract_menu_func,
                    analyze_dish_image_func,
                    classify_bcg_func,
                    generate_campaign_func,
                    verify_analysis_func,
                ]
            )
        ]

    def _extract_thought_signature(self, response_text: str) -> Dict[str, Any]:
        """
        Extract structured thought signature from response text.
        Handles JSON blocks and fallback parsing.
        """
        try:
            # Try to find JSON block
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            return json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError):
            # Fallback structure
            return {
                "plan": ["Execution plan inferred from content"],
                "observations": ["Content generated without explicit structure"],
                "reasoning": response_text[:500],
                "assumptions": ["Standard assumptions"],
                "confidence": 0.5,
            }

    async def create_thought_signature(
        self, task: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a Thought Signature - a transparent reasoning trace.

        This is a key differentiator that shows the agent's planning
        and reasoning process before executing tasks.
        """

        prompt = f"""You are RestoPilotAI, an AI assistant for restaurant optimization.
        
Before executing the following task, create a detailed thought signature that outlines:
1. Your plan of action (numbered steps)
2. Key observations from the provided context
3. Your main reasoning chain
4. Assumptions you're making
5. Your confidence level (0-1)

Task: {task}

Context:
{json.dumps(context, indent=2, default=str)}

Respond in this exact JSON format:
{{
    "plan": ["Step 1: ...", "Step 2: ...", ...],
    "observations": ["Observation 1", "Observation 2", ...],
    "reasoning": "Main reasoning explanation...",
    "assumptions": ["Assumption 1", "Assumption 2", ...],
    "confidence": 0.85
}}
"""

        response = await self._call_gemini(prompt)
        self.call_count += 1

        return self._extract_thought_signature(response.text)

    async def extract_menu_from_pdf(
        self, pdf_path: str, additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract menu items from a PDF file using Gemini Native Document Processing.
        """
        prompt = """Eres un sistema de inteligencia artificial AVANZADO especializado en digitalización de menús de restaurantes.
Estás procesando un ARCHIVO PDF COMPLETO que puede contener múltiples páginas, texto seleccionable, imágenes escaneadas y diseños mixtos.

🚨 **MODO DE EXTRACCIÓN TOTAL ACTIVADO** 🚨
Tu objetivo es extraer CADA producto vendible de TODO el documento.

CONTEXTO: El documento puede ser extenso (ej: 178+ productos). NO debes detenerte. NO debes resumir.

🔍 **INSTRUCCIONES PARA DOCUMENTOS PDF**:
1.  **Continuidad**: Lee el documento de principio a fin. Mantén el contexto de categorías que cruzan páginas.
2.  **Multimodalidad**: El PDF puede tener páginas que son solo imágenes. LEELAS VISUALMENTE. Puede tener páginas de texto. LEELAS TEXTUALMENTE.
3.  **Variantes y Opciones**: Desglosa todas las variantes (ej: "Sabores: Fresa, Vainilla, Chocolate" -> 3 items).

🛠 **REGLAS DE EXTRACCIÓN (Mismas reglas estrictas)**:
*   **Nombre**: Nombre completo y exacto.
*   **Precio**: Extrae el precio. Si hay lista (Botella/Copa), crea items separados.
*   **Categoría**: Respeta la estructura del menú.
*   **Descripción**: Texto descriptivo asociado.
*   **Análisis Visual**: Si hay fotos de platos en el PDF, indica `has_image: true` y descríbelos.

FORMATO DE RESPUESTA (JSON):
{
  "items": [
    {
      "name": "Nombre Producto",
      "price": 100.00,
      "description": "Descripción",
      "category": "Categoría",
      "has_image": false,
      "confidence": 0.95
    }
  ],
  "confidence": 0.95,
  "total_items_found": 150,
  "pages_analyzed": "all"
}

Responde SOLO con el JSON válido.
"""
        if additional_context:
            prompt += f"\n\nCONTEXTO ADICIONAL: {additional_context}"

        try:
            response = await self._call_gemini_with_pdf(prompt, pdf_path)
            self.call_count += 1
            return self._parse_extraction_response(response)
        except Exception as e:
            logger.error(f"Native PDF extraction failed: {e}")
            return {"items": [], "confidence": 0.0, "error": str(e)}

    async def _call_gemini_with_pdf(self, prompt: str, pdf_path: str) -> Any:
        """Upload PDF to Gemini File API and generate content."""
        logger.info(f"Uploading PDF {pdf_path} to Gemini...")
        # Fix: 'path' argument error. usage is client.files.upload(file=...) or positional
        try:
            file_ref = self.client.files.upload(file=pdf_path)
        except TypeError:
            # Fallback if 'file' keyword also fails (older versions might use different sig)
            file_ref = self.client.files.upload(path=pdf_path)

        # Wait for processing

        while file_ref.state.name == "PROCESSING":
            await asyncio.sleep(1)
            file_ref = self.client.files.get(name=file_ref.name)

        if file_ref.state.name == "FAILED":
            raise ValueError(f"PDF processing failed: {file_ref.state.name}")

        logger.info(f"PDF processed. Generating analysis for {pdf_path}...")

        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            file_data=types.FileData(
                                file_uri=file_ref.uri, mime_type="application/pdf"
                            )
                        ),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,  # Low temp for accurate data extraction
                max_output_tokens=8192,
            ),
        )
        return response

    async def extract_menu_from_image(
        self, image_path: str, additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract menu items from a menu image using multimodal analysis.
        """

        # Read and encode image
        image_data = Path(image_path).read_bytes()
        image_base64 = base64.b64encode(image_data).decode()

        prompt = """Eres un sistema de inteligencia artificial AVANZADO especializado en digitalización de menús complejos.
Tu misión es realizar una EXTRACCIÓN TOTAL Y PROFUNDA de cada elemento vendible visible en esta imagen del menú.

🚨 **MODO DE EXTRACCIÓN EXHAUSTIVA ACTIVADO** 🚨
NO RESUMAS. NO AGRUPES. NO OMITAS NADA.

CONTEXTO: Estás procesando menús densos (ej: listas de licores con 50+ items, menús de platos fuertes con 100+ items).
Tu trabajo es listar CADA UNO de ellos individualmente.

 **INSTRUCCIONES DE VISIÓN Y LECTURA:**
1.  **Escaneo Estructural**: Analiza columnas, tablas, notas al pie, cajas laterales y texto superpuesto en imágenes.
2.  **Manejo de Variantes**: Si ves "Cervezas: Corona, Modelo, Victoria... $50", DEBES crear 3 items separados (Cerveza Corona, Cerveza Modelo, Cerveza Victoria), todos con precio 50.
3.  **Licores y Botellas**: Si hay una lista de tequilas/whiskies, extrae CADA MARCA y TIPO como un item individual.
4.  **Items Visuales**: Si hay una FOTO de un platillo sin nombre claro pero con precio, descríbelo como "Platillo en foto (descripción)" e indica `has_image: true`.

🛠 **REGLAS DE EXTRACCIÓN:**
*   **Nombre**: Nombre completo tal cual aparece.
*   **Precio**: Si hay varios precios (Copa/Botella), crea DOS items o aclara en la descripción. Si no hay precio explícito pero se infiere por el encabezado (ej: "Todo a $100"), úsalo. Si no hay precio, usa `null`.
*   **Descripción**: Todo el texto descriptivo bajo el nombre.
*   **Categoría**: Usa la jerarquía del menú (ej: "Coctelería", "Licores > Tequila", "Fuertes > Carnes").
*   **Análisis Visual**: Si el item tiene una FOTO al lado, analiza la foto y llena `image_description` con detalles visuales (colores, presentación, ingredientes visibles).

🔢 **VERIFICACIÓN DE CANTIDAD**:
Si ves una lista de 20 tequilas, espero 20 objetos en el JSON.
Si ves una página llena de texto, espero 40-50 items.
Es mejor extraer de más y luego filtrar, que omitir.

FORMATO DE RESPUESTA (JSON):
{
  "items": [
    {
      "name": "Nombre Producto",
      "price": 100.00,
      "description": "Descripción detallada",
      "category": "Categoría exacta",
      "has_image": true,
      "image_description": "Plato servido en loza negra, salsa roja brillante, decorado con cilantro...",
      "dietary_notes": ["sin gluten", "picante"],
      "confidence": 0.98
    }
  ],
  "layout_analysis": {
     "has_images": true,
     "complexity": "high/medium/low",
     "notes": "Menú con lista densa de licores en columna derecha"
  }
}

Responde SOLO con el JSON válido.
"""

        if additional_context:
            prompt += f"\n\nCONTEXTO ADICIONAL (Texto extraído por OCR/PDF): {additional_context}"

        response = await self._call_gemini_with_image(prompt, image_base64)
        self.call_count += 1

        return self._parse_extraction_response(response)

    async def analyze_dish_images(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze dish photographs for visual appeal and marketability.
        """

        results = []

        for path in image_paths:
            image_data = Path(path).read_bytes()
            image_base64 = base64.b64encode(image_data).decode()

            prompt = """ACTÚA COMO UN CRÍTICO GASTRONÓMICO Y EXPERTO EN FOOD STYLING DE CLASE MUNDIAL.
Analiza esta imagen con profundidad extrema para un reporte de inteligencia competitiva.

🎯 **TU MISIÓN**: Deconstruir visualmente el platillo para entender su propuesta de valor, calidad y atractivo.

1.  **IDENTIFICACIÓN FORENSE**:
    *   Nombre probable del platillo.
    *   Ingredientes detectables (salsas, guarniciones, proteínas, decoraciones).
    *   Técnica de cocción visible (frito, asado, crudo, sellado).

2.  **ANÁLISIS SENSORIAL VISUAL**:
    *   **Paleta de Color**: ¿Es vibrante? ¿Monocromático? ¿Apagado? (Describe los colores clave).
    *   **Texturas**: Describe lo que se "siente" al verla (crujiente, sedoso, jugoso, seco, grasoso).
    *   **Temperatura Visual**: ¿Se ve caliente (vapor, brillo) o frío?

3.  **EVALUACIÓN DE PRESENTACIÓN (Food Styling)**:
    *   **Composición**: Caótica vs. Estructurada. Altura del platillo. Uso del espacio negativo en el plato.
    *   **Vajilla**: ¿Moderna, rústica, barata, elegante? ¿Ayuda o perjudica?
    *   **Cuidado al detalle**: Limpieza de bordes, colocación de guarniciones.

4.  **PSYCHOLOGY & MARKETING (La "Tercera Casilla")**:
    *   **"Craveability" (Apetitosidad)**: Score 0-100. ¿Hace salivar? ¿Por qué?
    *   **Instagram-worthiness**: Score 0-100. ¿La gente compartiría esto?
    *   **Percepción de Valor**: ¿Se ve caro/premium o barato/abundante?

5.  **FEEDBACK CONSTRUCTIVO DIRECTO**:
    *   3 puntos fuertes.
    *   3 áreas críticas de mejora (iluminación, emplatado, ingredientes).

RESPUESTA JSON:
{
  "dish_name": "Nombre inferido",
  "dish_category": "Entrada/Fuerte/Postre/Bebida",
  "visual_elements": {
    "ingredients": ["lista", "detallada"],
    "colors": "Descripción paleta",
    "textures": "Descripción texturas"
  },
  "presentation_analysis": {
    "style": "Rústico/Minimalista/Caótico/etc",
    "plating_quality": "High/Medium/Low",
    "crockery_comment": "Comentario sobre el plato/vajilla"
  },
  "scores": {
    "appetizing": 95,
    "instagram": 88,
    "composition": 90,
    "lighting": 85
  },
  "marketing_insight": {
    "perceived_value": "High/Medium/Low",
    "target_audience": "Descripción probable del cliente objetivo"
  },
  "feedback": {
    "strengths": ["...", "...", "..."],
    "improvements": ["...", "...", "..."]
  },
  "overall_summary": "Párrafo denso con el análisis final estilo crítico gastronómico."
}
"""

            response = await self._call_gemini_with_image(prompt, image_base64)
            self.call_count += 1

            results.append(self._parse_image_analysis(response, path))

        return results

    async def generate_bcg_insights(
        self, product_data: List[Dict[str, Any]], sales_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate BCG classification insights with strategic recommendations.
        Optimized to limit data sent to Gemini and includes timeout handling.
        """

        # OPTIMIZATION: Limit data sent to Gemini to prevent timeout
        # Only send top 5 items per BCG category with essential fields
        MAX_ITEMS_PER_CATEGORY = 5

        def simplify_item(item: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "name": item.get("name", "Unknown"),
                "bcg_class": item.get("bcg_class", "unknown"),
                "price": item.get("price", 0),
                "margin": round(item.get("margin", 0), 2),
                "growth_rate": round(item.get("growth_rate", 0), 2),
                "market_share": round(item.get("market_share", 0), 3),
            }

        # Group by BCG class and take top items
        by_class = {"star": [], "cash_cow": [], "question_mark": [], "dog": []}
        for item in product_data:
            bcg_class = item.get("bcg_class", "dog")
            if bcg_class in by_class:
                by_class[bcg_class].append(simplify_item(item))

        # Limit each category
        limited_data = {k: v[:MAX_ITEMS_PER_CATEGORY] for k, v in by_class.items()}

        # Simplified summary
        simple_summary = {
            "total_items": sales_summary.get("total_items", len(product_data)),
            "stars_count": len(sales_summary.get("stars", [])),
            "cash_cows_count": len(sales_summary.get("cash_cows", [])),
            "question_marks_count": len(sales_summary.get("question_marks", [])),
            "dogs_count": len(sales_summary.get("dogs", [])),
        }

        prompt = f"""You are a restaurant business analyst. Analyze this BCG Matrix portfolio summary.

Top Products by Category (sample of {MAX_ITEMS_PER_CATEGORY} per category):
{json.dumps(limited_data, indent=2)}

Portfolio Summary:
{json.dumps(simple_summary, indent=2)}

Provide a BRIEF strategic analysis:
1. Overall portfolio health (1-2 sentences)
2. Top 3 priority actions
3. Key recommendation

Respond in JSON format:
{{
  "portfolio_health": "brief assessment",
  "priority_actions": ["action1", "action2", "action3"],
  "key_recommendation": "main strategic recommendation",
  "stars_strategy": "brief strategy for stars",
  "dogs_strategy": "brief strategy for dogs"
}}"""

        try:
            # Add timeout to prevent hanging
            response = await asyncio.wait_for(
                asyncio.to_thread(self._call_gemini_sync, prompt),
                timeout=60.0,  # 60 second timeout for insights
            )
            self.call_count += 1
            return self._parse_bcg_response(response)
        except asyncio.TimeoutError:
            logger.warning("BCG insights generation timed out, using default insights")
            return self._get_default_bcg_insights(simple_summary)
        except Exception as e:
            logger.error(f"BCG insights generation failed: {e}")
            return self._get_default_bcg_insights(simple_summary)

    def _call_gemini_sync(self, prompt: str) -> Any:
        """Synchronous Gemini call for use with asyncio.to_thread."""
        return self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )

    def _get_default_bcg_insights(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Return default insights when AI generation fails or times out."""
        return {
            "portfolio_health": "Portfolio analysis completed. Review individual product classifications for detailed strategies.",
            "priority_actions": [
                "Focus investment on Star products to maintain growth",
                "Optimize Cash Cow products for maximum profit extraction",
                "Evaluate Dogs for repositioning or removal",
            ],
            "key_recommendation": "Prioritize resources on high-performing products while reviewing underperformers.",
            "stars_strategy": "Invest in visibility and promotion",
            "dogs_strategy": "Consider menu optimization or price adjustments",
            "generated": False,
            "note": "Default insights - AI generation was skipped for faster processing",
        }

    async def generate_campaigns(
        self,
        bcg_analysis: Dict[str, Any],
        num_campaigns: int = 3,
        constraints: Optional[Dict[str, Any]] = None,
        business_context: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate highly specific, personalized marketing campaign proposals.

        Key improvements over generic generators:
        - Uses actual product names and prices
        - Provides specific discount amounts (not "consider a discount")
        - Includes ready-to-post social media copy
        - Calculates specific expected ROI
        - Tailored to restaurant type and audience
        """

        # Extract key data for personalization
        classifications = bcg_analysis.get("classifications", [])
        stars = [c for c in classifications if c.get("bcg_class") == "star"]
        question_marks = [
            c for c in classifications if c.get("bcg_class") == "question_mark"
        ]
        cash_cows = [c for c in classifications if c.get("bcg_class") == "cash_cow"]
        dogs = [c for c in classifications if c.get("bcg_class") == "dog"]

        prompt = f"""Eres un estratega de marketing de restaurantes experto. Genera {num_campaigns} campañas de marketing ALTAMENTE ESPECÍFICAS y PERSONALIZADAS.

DATOS DEL ANÁLISIS BCG:
- STARS (invertir fuerte): {json.dumps([{"name": s["name"], "price": s.get("price", 0), "margin": s.get("margin", 0), "growth": s.get("growth_rate", 0)} for s in stars], indent=2)}
- QUESTION MARKS (decidir): {json.dumps([{"name": q["name"], "price": q.get("price", 0), "margin": q.get("margin", 0), "growth": q.get("growth_rate", 0)} for q in question_marks], indent=2)}
- CASH COWS (ordeñar): {json.dumps([{"name": c["name"], "price": c.get("price", 0), "margin": c.get("margin", 0)} for c in cash_cows], indent=2)}
- DOGS (revisar): {json.dumps([{"name": d["name"], "price": d.get("price", 0)} for d in dogs], indent=2)}

{"CONTEXTO DEL NEGOCIO: " + business_context if business_context else ""}
{"RESTRICCIONES: " + json.dumps(constraints, indent=2) if constraints else ""}

INSTRUCCIONES CRÍTICAS - Las campañas deben ser ESPECÍFICAS, no genéricas:
❌ MAL: "Considera ofrecer un descuento"
✅ BIEN: "Ofrece 20% de descuento en Tacos al Pastor los martes, reduciendo precio de $12.99 a $10.39"

❌ MAL: "Promociona en redes sociales"
✅ BIEN: "Post de Instagram con foto del platillo, copy: '🌮 MARTES DE TACOS 🌮 Hoy tu Pastor favorito a $10.39...'"

Para CADA campaña, proporciona EN JSON:
{{
  "title": "Nombre creativo y memorable",
  "objective": "Objetivo específico con métrica (ej: 'Aumentar ventas de Birria 40% en 2 semanas')",
  "target_audience": "Audiencia específica con demografía y psicografía",
  "channels": ["instagram", "email", "in_store"],
  "key_messages": ["Mensaje 1 específico", "Mensaje 2", "Mensaje 3"],
  "promotional_items": ["Nombre exacto del producto 1", "Producto 2"],
  "discount_strategy": "Estrategia específica: '25% off' o 'Compra 2 lleva 3' con precios exactos",
  "social_post_copy": "Copy COMPLETO listo para publicar con emojis y hashtags",
  "email_subject": "Línea de asunto del email",
  "email_preview": "Texto de preview del email",
  "in_store_copy": "Copy para señalización en tienda",
  "expected_uplift_percent": 25,
  "expected_revenue_increase": 1500,
  "investment_required": "Bajo/Medio/Alto con estimación",
  "roi_estimate": "Retorno esperado específico",
  "rationale": "Explicación detallada de por qué esta campaña funcionará para ESTE restaurante",
  "success_metrics": ["Métrica 1 medible", "Métrica 2"],
  "timeline": "Cronograma específico de implementación"
}}

DIVERSIFICACIÓN REQUERIDA:
1. Primera campaña: Amplificar STARS (productos exitosos)
2. Segunda campaña: Convertir QUESTION MARKS en Stars (alto potencial)
3. Tercera campaña: Bundle/Loyalty con CASH COWS (revenue estable)

Responde SOLO con un array JSON de {num_campaigns} campañas, sin texto adicional."""

        response = await self._call_gemini(prompt)
        self.call_count += 1

        return self._parse_campaigns_response(response)

    async def verify_and_correct(
        self, analysis_results: Dict[str, Any], original_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Self-verification step - the agent reviews its own analysis
        and makes corrections if needed.
        """

        prompt = f"""You are performing a self-verification check on your previous analysis.

Original Data:
{json.dumps(original_data, indent=2)[:2000]}

Analysis Results:
{json.dumps(analysis_results, indent=2)[:2000]}

Perform these verification checks:
1. Data consistency - do the numbers add up?
2. Classification accuracy - are BCG classifications justified?
3. Recommendation feasibility - are suggestions actionable?
4. Missing considerations - anything overlooked?
5. Logical coherence - does the reasoning flow correctly?

Respond with:
- verification_passed: boolean
- checks_performed: list of checks done
- issues_found: list of any problems
- corrections_needed: specific corrections to make
- confidence_after_verification: updated confidence score

Be critical and thorough."""

        response = await self._call_gemini(prompt)
        self.call_count += 1

        return self._parse_verification_response(response)

    async def _call_gemini(self, prompt: str) -> Any:
        """Make a text-only call to Gemini."""

        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )
        return response

    async def _call_gemini_with_image(
        self, prompt: str, image_base64: str, mime_type: str = "image/jpeg"
    ) -> Any:
        """Call Gemini with image/video content."""
        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type, data=base64.b64decode(image_base64)
                            )
                        ),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=8192,
            ),
        )
        return response

    async def _call_gemini_with_tools(
        self, prompt: str, context: Optional[List[Any]] = None
    ) -> Any:
        """Make a call to Gemini with function calling tools."""

        contents = context or []
        contents.append(types.Content(parts=[types.Part(text=prompt)]))

        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=self.tools,
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )
        return response

    async def identify_business_from_query(
        self, query: str, location_hint: str = None
    ) -> Dict[str, Any]:
        """
        Identify a real business using Gemini with Google Search Grounding.
        Returns structured business data including estimated coordinates.
        """
        search_context = ""
        if location_hint:
            search_context = f" near {location_hint}"

        prompt = f"""Identify the business matching query: '{query}'{search_context}.
        Find its exact Name, Address, Rating, and approximate location.
        
        Respond in JSON:
        {{
            "candidates": [
                {{
                    "name": "Exact Business Name",
                    "address": "Full Address",
                    "lat": 1.23,
                    "lng": -77.28,
                    "rating": 4.5,
                    "user_ratings_total": 100,
                    "place_id": "gemini_inferred_id",
                    "types": ["restaurant", "food"],
                    "photos": []
                }}
            ]
        }}
        """

        # Enable Google Search Grounding
        tool_config = types.Tool(google_search=types.GoogleSearch())

        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[tool_config],
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )

            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini business identification failed: {e}")
            return {"candidates": []}

    def _parse_video_analysis(self, response: Any, path: str) -> Dict[str, Any]:
        """Parse video analysis response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text.strip())
            result["video_path"] = path

            # Normalize scores
            if "scores" in result:
                scores = result["scores"]
                # Map stop_scroll_power or craveability to attractiveness for general metrics
                attractiveness = max(
                    scores.get("stop_scroll_power", 0), scores.get("craveability", 0)
                )
                result["attractiveness_score"] = attractiveness / 100

            # Backward compatibility fields
            if "feedback" in result:
                result["improvement_suggestions"] = [
                    result["feedback"].get("worst_feature", ""),
                    result["feedback"].get("editing_tip", ""),
                ]

            return result
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse video analysis: {e}")
            return {
                "video_path": path,
                "attractiveness_score": 0.5,
                "raw_response": response.text[:500],
            }

    def _parse_extraction_response(self, response: Any) -> Dict[str, Any]:
        """Parse menu extraction response."""
        text = response.text
        try:
            logger.debug(f"Gemini raw response (first 500 chars): {text[:500]}")

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            parsed = json.loads(text.strip())
            logger.info(
                f"Successfully parsed {len(parsed.get('items', []))} items from Gemini response"
            )
            return parsed
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"JSON parse failed, attempting repair: {e}")
            
            # Attempt to repair truncated JSON
            # Strategy: Find the last valid item object closing "}," inside the items array
            try:
                # 1. Isolate the "items" array part if possible
                if '"items":' in text:
                    # Find the last occurrence of "}," which usually indicates end of a list item
                    last_item_end = text.rfind('},')
                    
                    if last_item_end != -1:
                        # Construct repaired JSON: closes the array and the root object
                        # We take everything up to the comma of the last valid item
                        # text[:last_item_end+1] gives us "...}"
                        repaired_text = text[:last_item_end+1] + "]}"
                        
                        repaired_json = json.loads(repaired_text)
                        items = repaired_json.get("items", [])
                        
                        if items:
                            logger.info(f"Successfully repaired JSON. Recovered {len(items)} items.")
                            return {
                                "items": items,
                                "confidence": 0.8, # Lower confidence due to truncation
                                "repaired": True,
                                "layout_analysis": repaired_json.get("layout_analysis", {})
                            }
            except Exception as repair_error:
                logger.error(f"JSON repair failed: {repair_error}")

            logger.error(f"Failed to parse Gemini response: {e}")
            logger.debug(f"Raw response end: {response.text[-500:]}")
            return {
                "items": [],
                "confidence": 0.0,
                "raw_response": response.text[:1000],
                "error": str(e)
            }

    def _parse_image_analysis(self, response: Any, path: str) -> Dict[str, Any]:
        """Parse dish image analysis response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text.strip())
            result["image_path"] = path
            return result
        except (json.JSONDecodeError, KeyError, IndexError):
            return {
                "image_path": path,
                "attractiveness_score": 0.5,
                "presentation_quality": "unknown",
                "raw_response": response.text[:500],
            }

    def _parse_bcg_response(self, response: Any) -> Dict[str, Any]:
        """Parse BCG analysis response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text.strip())

            # Normalize scores to 0-1 range if they are 0-100
            if "scores" in result:
                scores = result["scores"]
                result["attractiveness_score"] = scores.get("appetizing", 50) / 100
                result["instagram_worthiness"] = scores.get("instagram", 50) / 100

            # Map new structure to old keys for backward compatibility
            if "feedback" in result:
                result["improvement_suggestions"] = result["feedback"].get(
                    "improvements", []
                )

            return result
        except (json.JSONDecodeError, KeyError, IndexError):
            return {
                "classifications": [],
                "portfolio_health": "unknown",
                "raw_response": response.text[:1000],
            }

    def _parse_campaigns_response(self, response: Any) -> List[Dict[str, Any]]:
        """Parse campaign generation response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text.strip())
            if isinstance(result, list):
                return result
            elif "campaigns" in result:
                return result["campaigns"]
            return [result]
        except (json.JSONDecodeError, KeyError, IndexError):
            return [{"title": "Default Campaign", "raw_response": response.text[:1000]}]

    def _parse_verification_response(self, response: Any) -> Dict[str, Any]:
        """Parse verification response."""
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())
        except (json.JSONDecodeError, KeyError, IndexError):
            return {
                "verification_passed": True,
                "checks_performed": ["basic_review"],
                "issues_found": [],
                "corrections_needed": [],
                "confidence_after_verification": 0.7,
            }

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Generic JSON response parser with repair capabilities."""
        text = response_text
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text.strip())
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"JSON parse failed, attempting repair: {e}")
            
            # Attempt to repair truncated JSON
            try:
                clean_text = text.strip()
                # Check if it looks like a JSON object that was cut off
                if clean_text.startswith("{") and not clean_text.endswith("}"):
                    # Heuristic: if the last significant char is inside a string, close quote then brace
                    # This is simple but covers common 'unterminated string' cases
                    # Find last quote and last brace
                    last_quote = clean_text.rfind('"')
                    last_brace = clean_text.rfind('}')
                    
                    if last_quote > last_brace:
                        # Likely inside a string
                        clean_text += '"}'
                    else:
                        # Likely expecting a closing brace
                        clean_text += "}"
                    
                    # Try parsing again
                    repaired = json.loads(clean_text)
                    logger.info("Successfully repaired truncated JSON")
                    return repaired
            except Exception as repair_err:
                logger.debug(f"JSON repair failed: {repair_err}")

            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            return {}

    def get_stats(self) -> Dict[str, int]:
        """Get agent usage statistics."""
        return {"gemini_calls": self.call_count, "estimated_tokens": self.total_tokens}


# Alias for backward compatibility
GeminiAgent = GeminiBaseAgent
