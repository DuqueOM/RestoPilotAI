"""Application configuration management using Pydantic Settings.

Centralized configuration for RestoPilotAI backend with support for:
- Gemini 3 API settings
- Rate limiting and caching
- File upload constraints
- ML model parameters
"""

from functools import lru_cache
from typing import List
from enum import Enum

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeminiModel(str, Enum):
    """Available Gemini 3 models with fallback hierarchy."""
    FLASH_PREVIEW = "gemini-3-flash-preview"  # Primary - Fast & efficient
    PRO_PREVIEW = "gemini-3-pro-preview"  # Fallback - More capable
    PRO_IMAGE = "gemini-3-pro-image-preview"  # Image generation
    FLASH = "gemini-3.0-flash"  # Fast fallback (Gemini 3 Flash)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],  # Load from local .env or root .env
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== API Keys ====================
    gemini_api_key: str = ""
    google_maps_api_key: str = ""
    google_places_api_key: str = ""

    @model_validator(mode="after")
    def consolidate_keys(self) -> "Settings":
        """Consolidate API keys to ensure google_maps_api_key is populated."""
        if not self.google_maps_api_key and self.google_places_api_key:
            self.google_maps_api_key = self.google_places_api_key
        return self

    # ==================== Application ====================
    app_name: str = "RestoPilotAI"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ==================== Server ====================
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "*"

    # ==================== Database ====================
    database_url: str = "sqlite+aiosqlite:///./data/RestoPilotAI.db"
    redis_url: str = "redis://localhost:6379"

    # ==================== Gemini 3 Configuration ====================
    # CRITICAL: Use only Gemini 3 models
    
    # Model Selection with Fallbacks
    gemini_model_primary: str = GeminiModel.PRO_PREVIEW.value
    gemini_model_reasoning: str = GeminiModel.PRO_PREVIEW.value  # BCG, competitive intel — PRO for max quality
    gemini_model_vision: str = GeminiModel.PRO_PREVIEW.value  # Multimodal (menus, dishes)
    gemini_model_image_gen: str = GeminiModel.PRO_IMAGE.value  # Creative Autopilot
    gemini_fallback_model: str = GeminiModel.PRO_PREVIEW.value  # Fallback if primary fails
    gemini_emergency_model: str = GeminiModel.FLASH.value  # Last resort (Gemini 3 Flash)
    
    # Backward compatibility
    gemini_model: str = GeminiModel.PRO_PREVIEW.value
    gemini_model_pro: str = GeminiModel.PRO_PREVIEW.value
    
    # Rate Limiting (Gemini 3 free tier)
    gemini_max_retries: int = 3
    gemini_rate_limit_rpm: int = 15  # Requests per minute
    gemini_rate_limit_tpm: int = 1_000_000  # Tokens per minute
    gemini_rate_limit_window: int = 60  # Window in seconds
    gemini_max_concurrent_requests: int = 3  # Avoid throttling
    
    # Token Limits (differentiated by task)
    gemini_max_input_tokens: int = 128000  # Context window
    gemini_max_tokens_menu_extraction: int = 8192  # Increased to prevent truncated JSON on large menus
    gemini_max_tokens_analysis: int = 8192  # Default
    gemini_max_tokens_campaign: int = 8192  # Increased for richer campaign copy
    gemini_max_tokens_reasoning: int = 16384  # Deep analysis tasks
    gemini_max_output_tokens: int = 8192  # Flash model default
    gemini_max_output_tokens_reasoning: int = 16384
    
    # Timeouts optimized for Marathon Agent
    gemini_timeout_seconds: int = 120  # Normal requests
    gemini_marathon_timeout_seconds: int = 600  # Long tasks (10 min)
    gemini_connection_timeout: int = 30  # Handshake only
    gemini_retry_backoff_factor: float = 2.0  # Exponential backoff
    
    # Cost Tracking & Budget Control
    gemini_cost_per_1k_input_tokens: float = 0.00001  # $0.01 per 1M tokens
    gemini_cost_per_1k_output_tokens: float = 0.00003  # $0.03 per 1M tokens
    gemini_budget_limit_usd: float = 50.0  # Max spend per day
    gemini_enable_cost_tracking: bool = True
    
    # Caching
    gemini_enable_cache: bool = True
    gemini_cache_ttl_seconds: int = 604800  # 7 days
    gemini_cache_max_size_mb: int = 500
    
    # Safety & Quality
    gemini_enable_safety_checks: bool = True
    gemini_min_confidence_score: float = 0.7
    gemini_enable_hallucination_detection: bool = True
    
    # Features
    gemini_enable_grounding: bool = True
    gemini_enable_streaming: bool = True

    # ==================== Hackathon Features Flags ====================
    # Enable/disable strategic tracks
    enable_vibe_engineering: bool = True  # Track: Vibe Engineering
    enable_marathon_agent: bool = True  # Track: Marathon Agent
    enable_creative_autopilot: bool = True  # Active for Hackathon
    enable_grounding: bool = True  # Google Search grounding
    
    # ==================== Vibe Engineering Configuration ====================
    vibe_quality_threshold: float = 0.85  # Minimum acceptable score
    vibe_max_iterations: int = 3  # Maximum improvement cycles
    vibe_auto_improve_default: bool = True  # Auto-improve by default
    vibe_enable_thought_transparency: bool = True  # Show reasoning
    
    # ==================== Marathon Agent Configuration ====================
    marathon_checkpoint_interval: int = 60  # Save every 60 seconds
    marathon_max_retries_per_step: int = 3
    marathon_enable_recovery: bool = True
    marathon_enable_checkpoints: bool = True
    marathon_max_task_duration: int = 3600  # 1 hour max per task
    
    # ==================== Thought Signatures Configuration ====================
    # Transparent reasoning levels
    thinking_level_quick_temp: float = 0.3
    thinking_level_quick_tokens: int = 2048
    thinking_level_standard_temp: float = 0.5
    thinking_level_standard_tokens: int = 4096
    thinking_level_deep_temp: float = 0.7
    thinking_level_deep_tokens: int = 8192
    thinking_level_exhaustive_temp: float = 0.8
    thinking_level_exhaustive_tokens: int = 16384
    
    # ==================== Grounding Configuration ====================
    grounding_enabled_for_competitive: bool = True
    grounding_max_results: int = 5  # Max Google Search results
    grounding_include_sources: bool = True  # Always cite sources
    grounding_confidence_threshold: float = 0.7  # Minimum confidence
    
    # ==================== External APIs ====================
    places_rate_limit: int = 100

    # ==================== Analysis Configuration ====================
    max_competitors: int = 5
    competitor_search_radius: int = 1000 # meters
    max_images_per_competitor: int = 10
    
    # ==================== WebSocket ====================
    ws_heartbeat_interval: int = 30

    # ==================== File Upload ====================
    max_upload_size_mb: int = 50
    max_pdf_pages: int = 30
    allowed_image_extensions: str = "jpg,jpeg,png,webp,pdf"
    allowed_data_extensions: str = "csv,xlsx"
    allowed_audio_extensions: str = "mp3,wav,m4a,ogg,webm,flac,aac"

    # ==================== ML Model Settings ====================
    sales_prediction_horizon_days: int = 14
    bcg_high_share_percentile: int = 75
    bcg_high_growth_percentile: int = 75
    neural_predictor_epochs: int = 30
    neural_predictor_batch_size: int = 32

    @property
    def allowed_image_ext_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_image_extensions.split(",")]

    @property
    def allowed_data_ext_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_data_extensions.split(",")]

    @property
    def allowed_audio_ext_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_audio_extensions.split(",")]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
