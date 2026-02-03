"""Application configuration management using Pydantic Settings.

Centralized configuration for RestoPilotAI backend with support for:
- Gemini 3 API settings
- Rate limiting and caching
- File upload constraints
- ML model parameters
"""

from functools import lru_cache
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    # CRÍTICO: Usar solo modelos de Gemini 3
    gemini_model_primary: str = "gemini-3-flash-preview"  # Modelo principal
    gemini_model_reasoning: str = "gemini-3-flash-preview"  # BCG, competitive intel
    gemini_model_vision: str = "gemini-3-pro-preview"  # Multimodal (menús, platos)
    gemini_model_image_gen: str = "gemini-3-pro-image-preview"  # Creative Autopilot
    
    # Backward compatibility
    gemini_model: str = "gemini-3-flash-preview"
    gemini_model_pro: str = "gemini-3-pro-preview"
    
    # Rate limits alineados con Gemini 3 free tier
    gemini_max_retries: int = 3
    gemini_rate_limit_rpm: int = 15  # Free tier: 15 requests/min
    gemini_rate_limit_tpm: int = 1000000
    gemini_max_concurrent_requests: int = 3  # Evitar throttling
    
    # Timeouts optimizados para Marathon Agent
    gemini_timeout_seconds: int = 120  # Requests normales
    gemini_marathon_timeout_seconds: int = 600  # Tareas largas (10 min)
    gemini_connection_timeout: int = 30  # Solo handshake
    
    # Token limits de Gemini 3
    gemini_max_input_tokens: int = 128000  # Context window
    gemini_max_output_tokens: int = 8192  # Flash model
    gemini_max_output_tokens_reasoning: int = 16384  # Análisis profundos
    
    # Cache y features
    gemini_cache_ttl_seconds: int = 3600
    gemini_enable_grounding: bool = True
    gemini_enable_streaming: bool = True

    # ==================== Hackathon Features Flags ====================
    # Habilitar/deshabilitar tracks estratégicos
    enable_vibe_engineering: bool = True  # Track: Vibe Engineering
    enable_marathon_agent: bool = True  # Track: Marathon Agent
    enable_creative_autopilot: bool = True  # Activo para Hackathon
    enable_grounding: bool = True  # Google Search grounding
    
    # ==================== Vibe Engineering Configuration ====================
    vibe_quality_threshold: float = 0.85  # Score mínimo aceptable
    vibe_max_iterations: int = 3  # Máximo de ciclos de mejora
    vibe_auto_improve_default: bool = True  # Auto-mejora por defecto
    vibe_enable_thought_transparency: bool = True  # Mostrar razonamiento
    
    # ==================== Marathon Agent Configuration ====================
    marathon_checkpoint_interval: int = 60  # Guardar cada 60 segundos
    marathon_max_retries_per_step: int = 3
    marathon_enable_recovery: bool = True
    marathon_enable_checkpoints: bool = True
    marathon_max_task_duration: int = 3600  # 1 hora máximo por tarea
    
    # ==================== Thought Signatures Configuration ====================
    # Niveles de razonamiento transparente
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
    grounding_max_results: int = 5  # Máximo de resultados de Google Search
    grounding_include_sources: bool = True  # Siempre citar fuentes
    grounding_confidence_threshold: float = 0.7  # Mínimo de confianza
    
    # ==================== External APIs ====================
    places_rate_limit: int = 100

    # ==================== Analysis Configuration ====================
    max_competitors: int = 5
    competitor_search_radius: int = 1000 # meters
    max_images_per_competitor: int = 10
    
    # ==================== WebSocket ====================
    ws_heartbeat_interval: int = 30

    # ==================== File Upload ====================
    max_upload_size_mb: int = 10
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
