"""Model fallback handler for Gemini API resilience.

Automatically switches to fallback models when primary model fails.
Tracks model health and implements circuit breaker pattern.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional, Any

from app.core.config import get_settings, GeminiModel

logger = logging.getLogger(__name__)


class ModelHealth(str, Enum):
    """Health status of a model."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class ModelStatus:
    """Status tracking for a model."""
    model: str
    health: ModelHealth
    consecutive_failures: int
    last_failure: Optional[datetime]
    last_success: Optional[datetime]
    total_calls: int
    total_failures: int


class ModelFallbackHandler:
    """Handles automatic fallback between Gemini models."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Model hierarchy for fallback
        self.model_hierarchy = [
            self.settings.gemini_model_primary,
            self.settings.gemini_fallback_model,
            self.settings.gemini_emergency_model,
        ]
        
        # Track model health
        self.model_status: dict[str, ModelStatus] = {}
        for model in self.model_hierarchy:
            self.model_status[model] = ModelStatus(
                model=model,
                health=ModelHealth.HEALTHY,
                consecutive_failures=0,
                last_failure=None,
                last_success=None,
                total_calls=0,
                total_failures=0,
            )
        
        # Circuit breaker settings
        self.max_consecutive_failures = 3
        self.recovery_timeout = timedelta(minutes=5)
        
        self._lock = asyncio.Lock()
    
    async def execute_with_fallback(
        self,
        api_call: Callable,
        task_type: str = "general",
        **kwargs
    ) -> Any:
        """
        Execute API call with automatic fallback to backup models.
        
        Args:
            api_call: Async function to call the API
            task_type: Type of task (for model selection)
            **kwargs: Arguments to pass to api_call
            
        Returns:
            API response
            
        Raises:
            Exception: If all models fail
        """
        # Select appropriate model based on task type
        primary_model = self._select_model_for_task(task_type)
        
        # Try models in order
        models_to_try = self._get_available_models(primary_model)
        
        last_error = None
        for model in models_to_try:
            try:
                logger.info(f"Attempting API call with model: {model}")
                
                # Execute API call with this model
                result = await api_call(model=model, **kwargs)
                
                # Record success
                await self._record_success(model)
                
                return result
                
            except Exception as e:
                logger.warning(f"Model {model} failed: {str(e)}")
                last_error = e
                
                # Record failure
                await self._record_failure(model)
                
                # Continue to next model
                continue
        
        # All models failed
        raise Exception(
            f"All models failed for task '{task_type}'. "
            f"Last error: {str(last_error)}"
        )
    
    def _select_model_for_task(self, task_type: str) -> str:
        """Select the best model for a specific task type."""
        task_model_map = {
            "vision": self.settings.gemini_model_vision,
            "image_generation": self.settings.gemini_model_image_gen,
            "reasoning": self.settings.gemini_model_reasoning,
            "general": self.settings.gemini_model_primary,
        }
        
        return task_model_map.get(task_type, self.settings.gemini_model_primary)
    
    def _get_available_models(self, preferred_model: str) -> list[str]:
        """
        Get list of models to try, starting with preferred model.
        Only includes healthy models.
        """
        # Start with preferred model if healthy
        models = []
        
        if self._is_model_available(preferred_model):
            models.append(preferred_model)
        
        # Add fallback models
        for model in self.model_hierarchy:
            if model != preferred_model and self._is_model_available(model):
                models.append(model)
        
        return models
    
    def _is_model_available(self, model: str) -> bool:
        """Check if a model is available (not in circuit breaker state)."""
        status = self.model_status.get(model)
        if not status:
            return True
        
        # Check if in failed state
        if status.health == ModelHealth.FAILED:
            # Check if recovery timeout has passed
            if status.last_failure:
                time_since_failure = datetime.now() - status.last_failure
                if time_since_failure > self.recovery_timeout:
                    # Try to recover
                    status.health = ModelHealth.DEGRADED
                    status.consecutive_failures = 0
                    logger.info(f"Model {model} recovered from failed state")
                    return True
                else:
                    return False
        
        return True
    
    async def _record_success(self, model: str):
        """Record a successful API call."""
        async with self._lock:
            status = self.model_status[model]
            status.total_calls += 1
            status.consecutive_failures = 0
            status.last_success = datetime.now()
            status.health = ModelHealth.HEALTHY
            
            logger.debug(f"Model {model} success recorded. Total calls: {status.total_calls}")
    
    async def _record_failure(self, model: str):
        """Record a failed API call."""
        async with self._lock:
            status = self.model_status[model]
            status.total_calls += 1
            status.total_failures += 1
            status.consecutive_failures += 1
            status.last_failure = datetime.now()
            
            # Update health status
            if status.consecutive_failures >= self.max_consecutive_failures:
                status.health = ModelHealth.FAILED
                logger.error(
                    f"Model {model} marked as FAILED after "
                    f"{status.consecutive_failures} consecutive failures"
                )
            elif status.consecutive_failures >= 1:
                status.health = ModelHealth.DEGRADED
                logger.warning(f"Model {model} marked as DEGRADED")
    
    def get_model_stats(self) -> dict:
        """Get statistics for all models."""
        return {
            model: {
                "health": status.health.value,
                "consecutive_failures": status.consecutive_failures,
                "total_calls": status.total_calls,
                "total_failures": status.total_failures,
                "success_rate": (
                    (status.total_calls - status.total_failures) / status.total_calls
                    if status.total_calls > 0 else 0.0
                ),
                "last_success": status.last_success.isoformat() if status.last_success else None,
                "last_failure": status.last_failure.isoformat() if status.last_failure else None,
            }
            for model, status in self.model_status.items()
        }


# Global fallback handler instance
_fallback_handler: Optional[ModelFallbackHandler] = None


def get_fallback_handler() -> ModelFallbackHandler:
    """Get or create the global fallback handler instance."""
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = ModelFallbackHandler()
    return _fallback_handler
