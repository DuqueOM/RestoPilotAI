"""
Enhanced Gemini 3 Agent with Streaming, Grounding, Caching, and Validation.

This module extends the base agent with advanced features:
- Streaming generation for real-time UX
- Google Search grounding for accuracy
- Intelligent caching to reduce costs
- Pydantic validation for structured outputs
- Enhanced thought traces with grounding metadata
"""

import asyncio
import hashlib
import json
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from enum import Enum

from google import genai
from google.genai import types
from loguru import logger
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings, GeminiModel
from app.core.rate_limiter import get_rate_limiter
from app.core.model_fallback import get_fallback_handler


class ThinkingLevel(str, Enum):
    """Depth of AI reasoning with corresponding parameters."""
    QUICK = "quick"          # temperature=0.3, max_tokens=2048
    STANDARD = "standard"    # temperature=0.7, max_tokens=4096
    DEEP = "deep"            # temperature=0.9, max_tokens=8192
    EXHAUSTIVE = "exhaustive"  # temperature=1.0, max_tokens=16384


class ThoughtTrace(BaseModel):
    """Transparent reasoning trace with grounding metadata."""
    timestamp: datetime
    thinking_level: ThinkingLevel
    prompt_preview: str
    reasoning_steps: List[str]
    confidence_score: float
    data_sources: List[str]
    assumptions_made: List[str]
    grounded: bool = False


class UsageStats(BaseModel):
    """Token usage and cost tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
    model_used: str
    cached: bool


class EnhancedGeminiAgent:
    """
    Enhanced Gemini 3 agent with streaming, grounding, caching, and validation.
    
    Features:
    - ✅ Streaming generation for real-time UX
    - ✅ Google Search grounding for accuracy
    - ✅ Intelligent caching to reduce costs
    - ✅ Pydantic validation for structured outputs
    - ✅ Enhanced thought traces with metadata
    - ✅ Automatic fallback between models
    - ✅ Rate limiting and cost tracking
    """
    
    def __init__(
        self,
        model: Optional[GeminiModel] = None,
        enable_streaming: bool = True,
        enable_grounding: bool = True,
        enable_cache: bool = True
    ):
        self.settings = get_settings()
        self.model_name = model or GeminiModel.PRO_PREVIEW
        self.enable_streaming = enable_streaming
        self.enable_grounding = enable_grounding and self.settings.gemini_enable_grounding
        self.enable_cache = enable_cache and self.settings.gemini_enable_cache
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=self.settings.gemini_api_key)
        
        # Get rate limiter and fallback handler
        self.rate_limiter = get_rate_limiter()
        self.fallback_handler = get_fallback_handler()
        
        # Stats tracking
        self.total_tokens_used = 0
        self.total_cost_usd = 0.0
        self.request_count = 0
        
        # Cache
        self._cache: Dict[str, Any] = {}
        
        logger.info(
            "enhanced_agent_initialized",
            model=self.model_name.value,
            streaming=enable_streaming,
            grounding=self.enable_grounding,
            caching=self.enable_cache
        )
    
    def _get_generation_config(
        self,
        thinking_level: ThinkingLevel,
        response_schema: Optional[type[BaseModel]] = None
    ) -> Dict[str, Any]:
        """Get generation config based on thinking level."""
        
        configs = {
            ThinkingLevel.QUICK: {
                "temperature": self.settings.thinking_level_quick_temp,
                "top_p": 0.8,
                "top_k": 20,
                "max_output_tokens": self.settings.gemini_max_tokens_campaign
            },
            ThinkingLevel.STANDARD: {
                "temperature": self.settings.thinking_level_standard_temp,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": self.settings.gemini_max_tokens_analysis
            },
            ThinkingLevel.DEEP: {
                "temperature": self.settings.thinking_level_deep_temp,
                "top_p": 0.95,
                "top_k": 60,
                "max_output_tokens": self.settings.gemini_max_tokens_analysis
            },
            ThinkingLevel.EXHAUSTIVE: {
                "temperature": self.settings.thinking_level_exhaustive_temp,
                "top_p": 1.0,
                "top_k": 80,
                "max_output_tokens": self.settings.gemini_max_tokens_reasoning
            }
        }
        
        config = configs.get(thinking_level, configs[ThinkingLevel.STANDARD])
        
        # Add JSON mode if schema provided
        if response_schema:
            config["response_mime_type"] = "application/json"
            # Note: response_schema requires specific format in Gemini API
            # For now, we'll validate after generation
        
        return config
    
    @staticmethod
    def _detect_mime_type(data: bytes) -> str:
        """Detect mime type from magic bytes header."""
        if len(data) < 12:
            return "image/jpeg"
        # MP4 / MOV: check for 'ftyp' box at offset 4
        if data[4:8] == b'ftyp':
            return "video/mp4"
        # WebM: starts with 0x1A45DFA3
        if data[:4] == b'\x1a\x45\xdf\xa3':
            return "video/webm"
        # AVI: starts with RIFF....AVI
        if data[:4] == b'RIFF' and data[8:12] == b'AVI ':
            return "video/avi"
        # PNG
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        # WebP
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            return "image/webp"
        # GIF
        if data[:6] in (b'GIF87a', b'GIF89a'):
            return "image/gif"
        # Default to JPEG
        return "image/jpeg"

    def _compute_cache_key(
        self,
        prompt: str,
        images: Optional[List[bytes]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.STANDARD
    ) -> str:
        """Generate cache key from inputs."""
        key_components = [
            prompt,
            self.model_name.value,
            thinking_level.value
        ]
        
        if images:
            for img in images:
                if isinstance(img, bytes):
                    key_components.append(hashlib.md5(img).hexdigest())
        
        combined = "|".join(str(c) for c in key_components)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def generate(
        self,
        prompt: str,
        images: Optional[List[Union[bytes, str]]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.STANDARD,
        response_schema: Optional[type[BaseModel]] = None,
        enable_thought_trace: bool = True,
        bypass_cache: bool = False,
        enable_grounding: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Enhanced generation with all advanced features.
        
        Features:
        - Automatic caching
        - Google Search grounding (optional)
        - Structured output with Pydantic validation
        - Thought traces for transparency
        - Cost tracking
        - Automatic fallback models
        
        Args:
            prompt: Text prompt
            images: Optional list of image bytes or URLs
            thinking_level: Depth of reasoning
            response_schema: Pydantic model for structured output
            enable_thought_trace: Include reasoning trace
            bypass_cache: Skip cache lookup
            enable_grounding: Override grounding setting
            
        Returns:
            Dict with data, usage, thought_trace, and metadata
        """
        start_time = datetime.now()
        
        # Use instance setting if not overridden
        use_grounding = enable_grounding if enable_grounding is not None else self.enable_grounding
        
        # Check cache
        if self.enable_cache and not bypass_cache:
            cache_key = self._compute_cache_key(prompt, images, thinking_level)
            if cache_key in self._cache:
                logger.info("cache_hit", key=cache_key[:16])
                cached_result = self._cache[cache_key]
                cached_result["cached"] = True
                return cached_result
        
        # Check rate limit
        estimated_tokens = len(prompt.split()) * 2  # Rough estimate
        await self.rate_limiter.acquire(estimated_tokens)
        
        try:
            # Prepare content parts
            parts = [types.Part(text=prompt)]
            
            if images:
                for img in images:
                    if isinstance(img, tuple) and len(img) == 2:
                        # Tuple of (bytes, mime_type) for explicit mime type
                        data, mime = img
                        parts.append(
                            types.Part(
                                inline_data=types.Blob(mime_type=mime, data=data)
                            )
                        )
                    elif isinstance(img, bytes):
                        # Auto-detect mime type from magic bytes
                        mime = self._detect_mime_type(img)
                        parts.append(
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime,
                                    data=img
                                )
                            )
                        )
                    elif isinstance(img, str) and img.startswith("http"):
                        # For URLs, we'd need to download first
                        # Skipping for now to keep it simple
                        logger.warning("url_images_not_supported", url=img)
            
            # Get generation config
            gen_config = self._get_generation_config(thinking_level, response_schema)
            
            # Prepare tools for grounding
            tools = []
            if use_grounding:
                tools.append(types.Tool(google_search=types.GoogleSearch()))
            
            # Generate with fallback
            async def _api_call(model: str, **kwargs):
                config = types.GenerateContentConfig(**gen_config)
                if tools:
                    config.tools = tools
                
                return await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=model,
                    contents=[types.Content(parts=parts)],
                    config=config
                )
            
            response = await self.fallback_handler.execute_with_fallback(
                _api_call,
                task_type="general"
            )
            
            # Extract result
            result_text = response.text or ""
            
            # Strip markdown code fences if present (Gemini often wraps JSON)
            stripped = result_text.strip()
            if stripped.startswith("```"):
                # Remove opening fence (```json or ```)
                first_nl = stripped.find("\n")
                if first_nl != -1:
                    stripped = stripped[first_nl + 1:]
                # Remove closing fence
                if stripped.rstrip().endswith("```"):
                    stripped = stripped.rstrip()[:-3].rstrip()
                result_text = stripped
            
            # Validate if schema provided
            if response_schema:
                try:
                    validated_data = response_schema.model_validate_json(result_text)
                    result_data = validated_data.model_dump()
                except ValidationError as e:
                    logger.error("validation_failed", error=str(e))
                    # Try to parse as JSON anyway
                    try:
                        result_data = json.loads(result_text)
                    except Exception:
                        result_data = {"text": result_text, "validation_error": str(e)}
            else:
                try:
                    result_data = json.loads(result_text)
                except Exception:
                    result_data = {"text": result_text}
            
            # Track usage
            usage = self._track_usage(response, start_time)
            
            # Build thought trace
            thought_trace = None
            if enable_thought_trace:
                thought_trace = self._build_thought_trace(
                    response, prompt, thinking_level, start_time
                )
            
            # Extract grounding sources
            grounding_sources = self._extract_grounding_sources(response) if use_grounding else []
            
            result = {
                "data": result_data,
                "usage": usage.model_dump(),
                "thought_trace": thought_trace.model_dump() if thought_trace else None,
                "grounding_sources": grounding_sources,
                "cached": False,
                "model_used": self.model_name.value,
                "grounding_used": use_grounding
            }
            
            # Cache result
            if self.enable_cache and not bypass_cache:
                self._cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error("generation_failed", error=str(e), model=self.model_name.value)
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        images: Optional[List[bytes]] = None,
        thinking_level: ThinkingLevel = ThinkingLevel.STANDARD,
        enable_grounding: Optional[bool] = None
    ) -> AsyncIterator[str]:
        """
        Streaming generation for real-time UX.
        
        Shows AI "thinking" in real-time, dramatically improving perceived speed.
        
        Args:
            prompt: Text prompt
            images: Optional list of image bytes
            thinking_level: Depth of reasoning
            enable_grounding: Override grounding setting
            
        Yields:
            Text chunks as they are generated
        """
        use_grounding = enable_grounding if enable_grounding is not None else self.enable_grounding
        
        # Check rate limit
        estimated_tokens = len(prompt.split()) * 2
        await self.rate_limiter.acquire(estimated_tokens)
        
        # Prepare content
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
        
        gen_config = self._get_generation_config(thinking_level)
        
        # Prepare tools
        tools = []
        if use_grounding:
            tools.append(types.Tool(google_search=types.GoogleSearch()))
        
        # Stream response
        config = types.GenerateContentConfig(**gen_config)
        if tools:
            config.tools = tools
        
        def _sync_stream():
            return self.client.models.generate_content_stream(
                model=self.model_name.value,
                contents=[types.Content(parts=parts)],
                config=config
            )
        
        response_stream = await asyncio.to_thread(_sync_stream)
        
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    
    def _track_usage(self, response, start_time: datetime) -> UsageStats:
        """Track token usage and costs."""
        
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
            completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
            total_tokens = getattr(response.usage_metadata, 'total_token_count', 0)
        else:
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
        
        # Calculate cost using rate limiter
        cost = self.rate_limiter.record_call(
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            model=self.model_name.value
        )
        
        # Update totals
        self.total_tokens_used += total_tokens
        self.total_cost_usd += cost
        self.request_count += 1
        
        latency = (datetime.now() - start_time).total_seconds() * 1000
        
        return UsageStats(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            latency_ms=latency,
            model_used=self.model_name.value,
            cached=False
        )
    
    def _build_thought_trace(
        self,
        response,
        prompt: str,
        thinking_level: ThinkingLevel,
        start_time: datetime
    ) -> ThoughtTrace:
        """Build thought trace from response."""
        
        reasoning_steps = self._extract_reasoning_steps(response)
        data_sources = self._extract_grounding_sources(response)
        confidence = self._compute_confidence(response)
        
        return ThoughtTrace(
            timestamp=start_time,
            thinking_level=thinking_level,
            prompt_preview=prompt[:200],
            reasoning_steps=reasoning_steps,
            confidence_score=confidence,
            data_sources=[s.get("uri", "") for s in data_sources if s.get("uri")],
            assumptions_made=[],
            grounded=len(data_sources) > 0
        )
    
    def _extract_reasoning_steps(self, response) -> List[str]:
        """Extract reasoning steps from grounded response."""
        steps = []
        
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    if hasattr(metadata, 'search_entry_point'):
                        entry_point = metadata.search_entry_point
                        if hasattr(entry_point, 'rendered_content'):
                            steps.append(f"Searched: {entry_point.rendered_content}")
        
        return steps
    
    def _extract_grounding_sources(self, response) -> List[Dict[str, str]]:
        """Extract grounding sources from response."""
        sources = []
        
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    if hasattr(metadata, 'grounding_chunks'):
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                sources.append({
                                    "uri": getattr(chunk.web, 'uri', ''),
                                    "title": getattr(chunk.web, 'title', ''),
                                    "grounded": True
                                })
        
        return sources
    
    def _compute_confidence(self, response) -> float:
        """Compute confidence score based on grounding."""
        
        # Base confidence
        confidence = 0.7
        
        # Boost if grounded
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    if hasattr(metadata, 'grounding_support'):
                        support = metadata.grounding_support
                        if hasattr(support, 'grounding_score'):
                            confidence = max(confidence, support.grounding_score)
        
        return confidence
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get usage statistics for transparency."""
        return {
            "total_requests": self.request_count,
            "total_tokens": self.total_tokens_used,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "avg_cost_per_request": round(
                self.total_cost_usd / max(self.request_count, 1), 4
            ),
            "cache_hit_rate": round(
                len(self._cache) / max(self.request_count, 1), 2
            ),
            "model_used": self.model_name.value,
            "cache_size": len(self._cache)
        }
    
    def clear_cache(self):
        """Clear the response cache."""
        self._cache.clear()
        logger.info("cache_cleared")
