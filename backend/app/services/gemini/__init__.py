"""
Gemini Agent Module for MenuPilot.

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
from app.services.gemini_agent import GeminiAgent

from .base_agent import (
    GeminiBaseAgent,
    GeminiCache,
    GeminiModel,
    GeminiUsageStats,
    RateLimiter,
    ThinkingLevel,
    TokenUsage,
    with_retry,
)
from .multimodal_agent import MultimodalAgent
from .orchestrator_agent import (
    OrchestratorAgent,
    PipelineCheckpoint,
    PipelineStage,
    PipelineState,
    ProgressUpdate,
)
from .reasoning_agent import ReasoningAgent, ReasoningResult, ThoughtTrace
from .verification_agent import (
    GeminiVerificationAgent,
    VerificationCheck,
    VerificationResult,
    VerificationStatus,
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
    "VerificationCheck",
    "VerificationResult",
    "VerificationStatus",
    # Orchestrator agent
    "OrchestratorAgent",
    "PipelineStage",
    "PipelineState",
    "PipelineCheckpoint",
    "ProgressUpdate",
    # Legacy
    "GeminiAgent",
]
