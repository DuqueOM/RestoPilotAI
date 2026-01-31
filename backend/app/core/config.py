"""Application configuration management using Pydantic Settings.

Centralized configuration for MenuPilot backend with support for:
- Gemini 3 API settings
- Rate limiting and caching
- File upload constraints
- ML model parameters
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== API Keys ====================
    gemini_api_key: str = ""
    google_maps_api_key: str = ""

    # ==================== Application ====================
    app_name: str = "MenuPilot"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ==================== Server ====================
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "*"

    # ==================== Database ====================
    database_url: str = "sqlite+aiosqlite:///./data/menupilot.db"

    # ==================== Gemini 3 Configuration ====================
    gemini_model: str = "gemini-3-flash-preview"
    gemini_model_pro: str = "gemini-3-pro-preview"
    gemini_max_retries: int = 3
    gemini_rate_limit_rpm: int = 60
    gemini_rate_limit_tpm: int = 1000000
    gemini_cache_ttl_seconds: int = 3600
    gemini_timeout_seconds: int = 120

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
