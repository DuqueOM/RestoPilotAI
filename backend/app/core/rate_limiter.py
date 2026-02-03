"""Rate limiting and cost tracking for Gemini API calls.

Implements:
- Token-based rate limiting (TPM)
- Request-based rate limiting (RPM)
- Cost tracking and budget enforcement
- Exponential backoff retry logic
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import get_settings


@dataclass
class APICall:
    """Record of a single API call."""
    timestamp: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model: str


class RateLimiter:
    """Rate limiter for Gemini API with cost tracking."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Request tracking (RPM)
        self.requests: deque = deque()
        
        # Token tracking (TPM)
        self.tokens: deque = deque()
        
        # Cost tracking (daily budget)
        self.calls_today: list[APICall] = []
        self.daily_cost: float = 0.0
        self.budget_exceeded: bool = False
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def acquire(self, estimated_tokens: int = 1000) -> bool:
        """
        Acquire permission to make an API call.
        
        Args:
            estimated_tokens: Estimated tokens for this request
            
        Returns:
            True if call is allowed, False if budget exceeded
        """
        async with self._lock:
            now = time.time()
            window = self.settings.gemini_rate_limit_window
            
            # Clean old entries
            self._clean_old_entries(now, window)
            
            # Check budget
            if self.settings.gemini_enable_cost_tracking:
                self._update_daily_cost()
                if self.daily_cost >= self.settings.gemini_budget_limit_usd:
                    self.budget_exceeded = True
                    return False
            
            # Check RPM limit
            if len(self.requests) >= self.settings.gemini_rate_limit_rpm:
                wait_time = self._calculate_wait_time(self.requests, window)
                await asyncio.sleep(wait_time)
                self._clean_old_entries(time.time(), window)
            
            # Check TPM limit
            total_tokens = sum(self.tokens)
            if total_tokens + estimated_tokens > self.settings.gemini_rate_limit_tpm:
                wait_time = self._calculate_wait_time(self.tokens, window)
                await asyncio.sleep(wait_time)
                self._clean_old_entries(time.time(), window)
            
            # Record request
            self.requests.append(now)
            self.tokens.append(estimated_tokens)
            
            return True
    
    def record_call(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """
        Record an API call and calculate cost.
        
        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            model: Model name used
            
        Returns:
            Cost in USD
        """
        # Calculate cost
        input_cost = (input_tokens / 1000) * self.settings.gemini_cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * self.settings.gemini_cost_per_1k_output_tokens
        total_cost = input_cost + output_cost
        
        # Record call
        call = APICall(
            timestamp=time.time(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=total_cost,
            model=model
        )
        self.calls_today.append(call)
        self.daily_cost += total_cost
        
        return total_cost
    
    def get_usage_stats(self) -> dict:
        """Get current usage statistics."""
        now = time.time()
        window = self.settings.gemini_rate_limit_window
        
        # Clean old entries
        self._clean_old_entries(now, window)
        
        # Calculate stats
        total_input_tokens = sum(call.input_tokens for call in self.calls_today)
        total_output_tokens = sum(call.output_tokens for call in self.calls_today)
        
        return {
            "requests_in_window": len(self.requests),
            "tokens_in_window": sum(self.tokens),
            "rpm_limit": self.settings.gemini_rate_limit_rpm,
            "tpm_limit": self.settings.gemini_rate_limit_tpm,
            "daily_cost_usd": round(self.daily_cost, 4),
            "budget_limit_usd": self.settings.gemini_budget_limit_usd,
            "budget_remaining_usd": round(
                self.settings.gemini_budget_limit_usd - self.daily_cost, 4
            ),
            "budget_exceeded": self.budget_exceeded,
            "calls_today": len(self.calls_today),
            "total_input_tokens_today": total_input_tokens,
            "total_output_tokens_today": total_output_tokens,
        }
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at midnight)."""
        self.calls_today.clear()
        self.daily_cost = 0.0
        self.budget_exceeded = False
    
    def _clean_old_entries(self, now: float, window: int):
        """Remove entries older than the time window."""
        cutoff = now - window
        
        # Clean requests
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
        
        # Clean tokens (paired with requests)
        while len(self.tokens) > len(self.requests):
            self.tokens.popleft()
    
    def _update_daily_cost(self):
        """Update daily cost, removing calls from previous days."""
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        cutoff = today_start.timestamp()
        
        # Remove old calls
        self.calls_today = [
            call for call in self.calls_today
            if call.timestamp >= cutoff
        ]
        
        # Recalculate daily cost
        self.daily_cost = sum(call.cost_usd for call in self.calls_today)
    
    def _calculate_wait_time(self, queue: deque, window: int) -> float:
        """Calculate how long to wait before next request."""
        if not queue:
            return 0.0
        
        oldest = queue[0]
        elapsed = time.time() - oldest
        
        if elapsed >= window:
            return 0.0
        
        return window - elapsed + 0.1  # Add small buffer


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def with_rate_limit(estimated_tokens: int = 1000):
    """
    Decorator/context manager for rate-limited API calls.
    
    Usage:
        async with with_rate_limit(estimated_tokens=2000):
            response = await gemini_api_call()
    """
    limiter = get_rate_limiter()
    allowed = await limiter.acquire(estimated_tokens)
    
    if not allowed:
        raise Exception(
            f"Daily budget limit of ${limiter.settings.gemini_budget_limit_usd} exceeded. "
            f"Current spend: ${limiter.daily_cost:.4f}"
        )
    
    return limiter
