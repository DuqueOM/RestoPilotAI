"""
Gemini 3 Integration Tests for MenuPilot.

Tests the Gemini 3 agent architecture and API integration.
These tests verify the hackathon requirements are met.
"""

# Tests for Gemini 3 integration - no mocks needed for structure tests


class TestGeminiModelConfiguration:
    """Test Gemini 3 model configuration meets hackathon requirements."""

    def test_gemini_agent_uses_gemini3_model(self):
        """Verify GeminiAgent uses Gemini 3 model."""
        from app.services.gemini_agent import GeminiAgent

        agent = GeminiAgent()
        assert (
            "gemini-3" in agent.MODEL_NAME
        ), f"Model should be Gemini 3, got {agent.MODEL_NAME}"

    def test_base_agent_model_enum_has_gemini3(self):
        """Verify GeminiModel enum has Gemini 3 models."""
        from app.services.gemini.base_agent import GeminiModel

        # Check FLASH model is Gemini 3
        assert (
            "gemini-3" in GeminiModel.FLASH.value
        ), f"FLASH should be Gemini 3, got {GeminiModel.FLASH.value}"

        # Check PRO model is Gemini 3
        assert (
            "gemini-3" in GeminiModel.PRO.value
        ), f"PRO should be Gemini 3, got {GeminiModel.PRO.value}"


class TestThinkingLevels:
    """Test Thought Signature thinking levels."""

    def test_thinking_levels_exist(self):
        """Verify all thinking levels are defined."""
        from app.services.gemini.base_agent import ThinkingLevel

        assert ThinkingLevel.QUICK.value == "quick"
        assert ThinkingLevel.STANDARD.value == "standard"
        assert ThinkingLevel.DEEP.value == "deep"
        assert ThinkingLevel.EXHAUSTIVE.value == "exhaustive"


class TestAgentArchitecture:
    """Test agent architecture components exist."""

    def test_base_agent_exists(self):
        """Verify GeminiBaseAgent class exists."""
        from app.services.gemini.base_agent import GeminiBaseAgent

        assert GeminiBaseAgent is not None

    def test_multimodal_agent_exists(self):
        """Verify MultimodalAgent class exists."""
        from app.services.gemini.multimodal_agent import MultimodalAgent

        assert MultimodalAgent is not None

    def test_reasoning_agent_exists(self):
        """Verify ReasoningAgent class exists."""
        from app.services.gemini.reasoning_agent import ReasoningAgent

        assert ReasoningAgent is not None

    def test_verification_agent_exists(self):
        """Verify GeminiVerificationAgent class exists."""
        from app.services.gemini.verification_agent import GeminiVerificationAgent

        assert GeminiVerificationAgent is not None

    def test_orchestrator_agent_exists(self):
        """Verify OrchestratorAgent class exists."""
        from app.services.gemini.orchestrator_agent import OrchestratorAgent

        assert OrchestratorAgent is not None


class TestRateLimiting:
    """Test rate limiting infrastructure."""

    def test_rate_limiter_exists(self):
        """Verify RateLimiter class exists."""
        from app.services.gemini.base_agent import RateLimiter

        limiter = RateLimiter(requests_per_minute=60)
        assert limiter.requests_per_minute == 60


class TestCaching:
    """Test caching infrastructure."""

    def test_cache_exists(self):
        """Verify GeminiCache class exists."""
        from app.services.gemini.base_agent import GeminiCache

        cache = GeminiCache(max_size=100, ttl_seconds=3600)
        assert cache.max_size == 100
        assert cache.ttl_seconds == 3600


class TestTokenTracking:
    """Test token usage tracking."""

    def test_token_usage_dataclass(self):
        """Verify TokenUsage dataclass works."""
        from app.services.gemini.base_agent import TokenUsage

        usage = TokenUsage(input_tokens=100, output_tokens=50)
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50

    def test_token_usage_addition(self):
        """Verify TokenUsage can be added."""
        from app.services.gemini.base_agent import TokenUsage

        usage1 = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)
        usage2 = TokenUsage(input_tokens=200, output_tokens=100, total_tokens=300)

        combined = usage1 + usage2
        assert combined.input_tokens == 300
        assert combined.output_tokens == 150
        assert combined.total_tokens == 450
