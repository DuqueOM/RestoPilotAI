"""
Core module for MenuPilot.

Contains cross-cutting concerns:
- Logging configuration
- Caching utilities
- Event system
- Metrics collection
"""

from app.core.logging_config import configure_logging, get_logger, LogContext
from app.core.cache import RedisCache, InMemoryCache, CacheManager

__all__ = [
    "configure_logging",
    "get_logger",
    "LogContext",
    "RedisCache",
    "InMemoryCache",
    "CacheManager",
]
