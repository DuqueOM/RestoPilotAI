"""
Gemini Agent Module for RestoPilotAI.

Provides modular, production-ready integration with Google Gemini 3 API.

Components:
- GeminiBaseAgent: Core functionality with retry logic, rate limiting, token tracking
- GeminiMultimodalAgent: Vision + text extraction capabilities
- GeminiReasoningAgent: Deep analysis & strategic thinking
- GeminiVerificationAgent: Self-verification loop for quality assurance
- GeminiOrchestratorAgent: Marathon pattern coordinator for complex pipelines
- GeminiCache: Response caching for cost optimization
"""

# Legacy import for backwards compatibility
from .base_agent import (
    GeminiAgent,
    GeminiBaseAgent,
    GeminiCache,
    GeminiModel,
    GeminiUsageStats,
    RateLimiter,
    ThinkingLevel,
    TokenUsage,
    with_retry,
)
from .multimodal import MultimodalAgent
from .reasoning_agent import ReasoningAgent, ReasoningResult, ThoughtTrace
from .verification import (
    GeminiVerificationAgent,
)

__all__ = [
    # Base infrastructure
    "GeminiBaseAgent",
    "GeminiModel",
    "GeminiUsageStats",
    "GeminiCache",
    "RateLimiter",
    "ThinkingLevel",
    "TokenUsage",
    "with_retry",
    # Multimodal agent
    "MultimodalAgent",
    # Reasoning agent
    "ReasoningAgent",
    "ReasoningResult",
    "ThoughtTrace",
    # Verification agent
    "GeminiVerificationAgent",
    # Legacy
    "GeminiAgent",
]
