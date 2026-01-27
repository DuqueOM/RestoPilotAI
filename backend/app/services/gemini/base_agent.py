"""
Gemini Base Agent - Core infrastructure for all Gemini-powered agents.

Provides:
- Retry logic with exponential backoff
- Rate limiting (requests/minute)
- Token usage tracking
- Robust error handling
- Cost estimation
"""

import asyncio
import base64
import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from google import genai
from google.genai import types
from loguru import logger

from app.config import get_settings


class ThinkingLevel(str, Enum):
    """Depth of AI reasoning for analysis tasks."""
    
    QUICK = "quick"           # 2-5 seconds, surface-level
    STANDARD = "standard"     # 10-15 seconds, balanced
    DEEP = "deep"            # 30-45 seconds, multi-perspective
    EXHAUSTIVE = "exhaustive" # 60-90 seconds, full analysis


class GeminiModel(str, Enum):
    """Available Gemini models with their capabilities."""
    
    FLASH = "gemini-2.0-flash"
    FLASH_LITE = "gemini-2.0-flash-lite"
    PRO = "gemini-2.5-pro-preview-05-06"


@dataclass
class TokenUsage:
    """Track token usage for a single request."""
    
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    
    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            cached_tokens=self.cached_tokens + other.cached_tokens,
        )


@dataclass
class GeminiUsageStats:
    """Comprehensive usage statistics for Gemini API."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    retried_requests: int = 0
    
    total_tokens: TokenUsage = field(default_factory=TokenUsage)
    
    total_latency_ms: int = 0
    avg_latency_ms: float = 0.0
    
    # Cost estimation (approximate)
    estimated_cost_usd: float = 0.0
    
    # Per-model breakdown
    model_usage: Dict[str, int] = field(default_factory=dict)
    
    # Per-feature breakdown
    feature_usage: Dict[str, int] = field(default_factory=dict)
    
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "retried_requests": self.retried_requests,
            "tokens": {
                "input": self.total_tokens.input_tokens,
                "output": self.total_tokens.output_tokens,
                "total": self.total_tokens.total_tokens,
                "cached": self.total_tokens.cached_tokens,
            },
            "latency": {
                "total_ms": self.total_latency_ms,
                "avg_ms": round(self.avg_latency_ms, 2),
            },
            "estimated_cost_usd": round(self.estimated_cost_usd, 4),
            "model_usage": self.model_usage,
            "feature_usage": self.feature_usage,
            "session_duration_seconds": (datetime.utcnow() - self.started_at).total_seconds(),
        }


class RateLimiter:
    """Token bucket rate limiter for API calls."""
    
    def __init__(self, requests_per_minute: int = 60, tokens_per_minute: int = 1_000_000):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_tokens: List[float] = []
        self.token_counts: List[tuple] = []  # (timestamp, tokens)
        self._lock = asyncio.Lock()
    
    async def acquire(self, estimated_tokens: int = 1000) -> None:
        """Wait until rate limit allows the request."""
        async with self._lock:
            now = time.time()
            minute_ago = now - 60
            
            # Clean old entries
            self.request_tokens = [t for t in self.request_tokens if t > minute_ago]
            self.token_counts = [(t, c) for t, c in self.token_counts if t > minute_ago]
            
            # Check request limit
            while len(self.request_tokens) >= self.requests_per_minute:
                wait_time = self.request_tokens[0] - minute_ago
                logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time + 0.1)
                now = time.time()
                minute_ago = now - 60
                self.request_tokens = [t for t in self.request_tokens if t > minute_ago]
            
            # Check token limit
            current_tokens = sum(c for _, c in self.token_counts)
            while current_tokens + estimated_tokens > self.tokens_per_minute:
                wait_time = self.token_counts[0][0] - minute_ago
                logger.warning(f"Token limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time + 0.1)
                now = time.time()
                minute_ago = now - 60
                self.token_counts = [(t, c) for t, c in self.token_counts if t > minute_ago]
                current_tokens = sum(c for _, c in self.token_counts)
            
            # Record this request
            self.request_tokens.append(now)
            self.token_counts.append((now, estimated_tokens))
    
    def record_actual_tokens(self, tokens: int) -> None:
        """Update the last request with actual token count."""
        if self.token_counts:
            timestamp = self.token_counts[-1][0]
            self.token_counts[-1] = (timestamp, tokens)


class GeminiCache:
    """Simple in-memory cache for Gemini responses."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # key -> (response, timestamp)
        self._lock = asyncio.Lock()
    
    def _get_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key from prompt and parameters."""
        content = f"{prompt}{json.dumps(kwargs, sort_keys=True, default=str)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get(self, prompt: str, **kwargs) -> Optional[Any]:
        """Get cached response if available and not expired."""
        async with self._lock:
            key = self._get_cache_key(prompt, **kwargs)
            if key in self.cache:
                response, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    logger.debug(f"Cache hit for key {key[:16]}...")
                    return response
                else:
                    del self.cache[key]
            return None
    
    async def set(self, prompt: str, response: Any, **kwargs) -> None:
        """Cache a response."""
        async with self._lock:
            key = self._get_cache_key(prompt, **kwargs)
            
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[key] = (response, time.time())
    
    def clear(self) -> None:
        """Clear all cached responses."""
        self.cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
        }


T = TypeVar("T")


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
):
    """Decorator for retry logic with exponential backoff."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                        raise
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


class GeminiBaseAgent(ABC):
    """
    Base class for all Gemini-powered agents.
    
    Provides common infrastructure:
    - Client initialization
    - Rate limiting
    - Token tracking
    - Caching
    - Retry logic
    - Error handling
    """
    
    # Cost per 1M tokens (approximate, Gemini 2.0 Flash pricing)
    COST_PER_1M_INPUT_TOKENS = 0.10
    COST_PER_1M_OUTPUT_TOKENS = 0.40
    
    def __init__(
        self,
        model: GeminiModel = GeminiModel.FLASH,
        enable_caching: bool = True,
        cache_ttl: int = 3600,
        requests_per_minute: int = 60,
        tokens_per_minute: int = 1_000_000,
    ):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = model
        self.model_name = model.value
        
        self.stats = GeminiUsageStats()
        self.rate_limiter = RateLimiter(requests_per_minute, tokens_per_minute)
        
        self.cache = GeminiCache(ttl_seconds=cache_ttl) if enable_caching else None
        self.enable_caching = enable_caching
    
    def _estimate_cost(self, usage: TokenUsage) -> float:
        """Estimate cost based on token usage."""
        input_cost = (usage.input_tokens / 1_000_000) * self.COST_PER_1M_INPUT_TOKENS
        output_cost = (usage.output_tokens / 1_000_000) * self.COST_PER_1M_OUTPUT_TOKENS
        return input_cost + output_cost
    
    def _extract_token_usage(self, response: Any) -> TokenUsage:
        """Extract token usage from Gemini response."""
        try:
            if hasattr(response, 'usage_metadata'):
                metadata = response.usage_metadata
                return TokenUsage(
                    input_tokens=getattr(metadata, 'prompt_token_count', 0) or 0,
                    output_tokens=getattr(metadata, 'candidates_token_count', 0) or 0,
                    total_tokens=getattr(metadata, 'total_token_count', 0) or 0,
                    cached_tokens=getattr(metadata, 'cached_content_token_count', 0) or 0,
                )
        except Exception as e:
            logger.warning(f"Failed to extract token usage: {e}")
        
        return TokenUsage()
    
    def _update_stats(
        self,
        success: bool,
        usage: TokenUsage,
        latency_ms: int,
        feature: str = "unknown",
        retried: bool = False,
    ) -> None:
        """Update usage statistics after a request."""
        self.stats.total_requests += 1
        
        if success:
            self.stats.successful_requests += 1
        else:
            self.stats.failed_requests += 1
        
        if retried:
            self.stats.retried_requests += 1
        
        self.stats.total_tokens = self.stats.total_tokens + usage
        self.stats.total_latency_ms += latency_ms
        
        if self.stats.successful_requests > 0:
            self.stats.avg_latency_ms = self.stats.total_latency_ms / self.stats.successful_requests
        
        self.stats.estimated_cost_usd += self._estimate_cost(usage)
        
        # Update model usage
        model_key = self.model_name
        self.stats.model_usage[model_key] = self.stats.model_usage.get(model_key, 0) + 1
        
        # Update feature usage
        self.stats.feature_usage[feature] = self.stats.feature_usage.get(feature, 0) + 1
    
    @with_retry(max_attempts=3, base_delay=2.0, max_delay=30.0)
    async def _generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 4096,
        feature: str = "text_generation",
        use_cache: bool = True,
        **kwargs,
    ) -> str:
        """
        Generate content with retry logic and rate limiting.
        
        Args:
            prompt: The prompt to send to Gemini
            temperature: Sampling temperature (0-1)
            max_output_tokens: Maximum tokens in response
            feature: Feature name for tracking
            use_cache: Whether to use caching
            **kwargs: Additional generation config parameters
            
        Returns:
            Generated text response
        """
        # Check cache first
        if self.enable_caching and use_cache and self.cache:
            cached = await self.cache.get(prompt, temperature=temperature, **kwargs)
            if cached:
                return cached
        
        # Rate limiting
        await self.rate_limiter.acquire(estimated_tokens=len(prompt) // 4 + max_output_tokens)
        
        start_time = time.time()
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    **kwargs,
                ),
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            usage = self._extract_token_usage(response)
            self.rate_limiter.record_actual_tokens(usage.total_tokens)
            
            self._update_stats(
                success=True,
                usage=usage,
                latency_ms=latency_ms,
                feature=feature,
            )
            
            result = response.text
            
            # Cache the result
            if self.enable_caching and use_cache and self.cache:
                await self.cache.set(prompt, result, temperature=temperature, **kwargs)
            
            logger.info(
                f"Gemini request completed",
                extra={
                    "feature": feature,
                    "tokens": usage.total_tokens,
                    "latency_ms": latency_ms,
                    "model": self.model_name,
                }
            )
            
            return result
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            self._update_stats(
                success=False,
                usage=TokenUsage(),
                latency_ms=latency_ms,
                feature=feature,
            )
            logger.error(f"Gemini request failed: {e}")
            raise
    
    @with_retry(max_attempts=3, base_delay=2.0, max_delay=30.0)
    async def _generate_multimodal(
        self,
        prompt: str,
        images: List[Union[str, bytes]],
        mime_type: str = "image/jpeg",
        temperature: float = 0.5,
        max_output_tokens: int = 4096,
        feature: str = "multimodal",
        **kwargs,
    ) -> str:
        """
        Generate content with images (multimodal).
        
        Args:
            prompt: Text prompt
            images: List of images (base64 strings or bytes)
            mime_type: MIME type of images
            temperature: Sampling temperature
            max_output_tokens: Maximum tokens in response
            feature: Feature name for tracking
            
        Returns:
            Generated text response
        """
        await self.rate_limiter.acquire(estimated_tokens=10000 + max_output_tokens)
        
        start_time = time.time()
        
        try:
            # Build content parts
            parts = [types.Part(text=prompt)]
            
            for image in images:
                if isinstance(image, str):
                    # Assume base64
                    image_bytes = base64.b64decode(image)
                else:
                    image_bytes = image
                
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=mime_type,
                            data=image_bytes,
                        )
                    )
                )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(parts=parts)],
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    **kwargs,
                ),
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            usage = self._extract_token_usage(response)
            self.rate_limiter.record_actual_tokens(usage.total_tokens)
            
            self._update_stats(
                success=True,
                usage=usage,
                latency_ms=latency_ms,
                feature=feature,
            )
            
            logger.info(
                f"Multimodal request completed",
                extra={
                    "feature": feature,
                    "images": len(images),
                    "tokens": usage.total_tokens,
                    "latency_ms": latency_ms,
                }
            )
            
            return response.text
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            self._update_stats(
                success=False,
                usage=TokenUsage(),
                latency_ms=latency_ms,
                feature=feature,
            )
            logger.error(f"Multimodal request failed: {e}")
            raise
    
    async def _generate_with_tools(
        self,
        prompt: str,
        tools: List[types.Tool],
        temperature: float = 0.7,
        max_output_tokens: int = 4096,
        feature: str = "function_calling",
        **kwargs,
    ) -> Any:
        """
        Generate content with function calling tools.
        
        Args:
            prompt: Text prompt
            tools: List of tool definitions
            temperature: Sampling temperature
            max_output_tokens: Maximum tokens
            feature: Feature name for tracking
            
        Returns:
            Full response object (may contain function calls)
        """
        await self.rate_limiter.acquire(estimated_tokens=len(prompt) // 4 + max_output_tokens)
        
        start_time = time.time()
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=tools,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    **kwargs,
                ),
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            usage = self._extract_token_usage(response)
            
            self._update_stats(
                success=True,
                usage=usage,
                latency_ms=latency_ms,
                feature=feature,
            )
            
            return response
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            self._update_stats(
                success=False,
                usage=TokenUsage(),
                latency_ms=latency_ms,
                feature=feature,
            )
            raise
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from Gemini response, handling markdown code blocks."""
        try:
            # Try direct parse first
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try extracting from code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {text[:500]}")
            return {"error": "Failed to parse response", "raw": text[:1000]}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return self.stats.to_dict()
    
    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self.stats = GeminiUsageStats()
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """Main processing method to be implemented by subclasses."""
        pass
