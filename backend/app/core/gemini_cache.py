"""
Intelligent Caching System for Gemini 3 API calls.

Reduces costs and improves performance by caching responses.
Uses Redis for distributed caching with TTL support.
"""

import hashlib
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from loguru import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - using in-memory cache fallback")


# ==================== Cache Statistics ====================

class CacheStatistics:
    """Track cache performance metrics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
        self.cost_saved = 0.0
        self.tokens_saved = 0
    
    def record_hit(self, tokens_saved: int = 0, cost_saved: float = 0.0):
        """Record a cache hit."""
        self.hits += 1
        self.total_requests += 1
        self.tokens_saved += tokens_saved
        self.cost_saved += cost_saved
    
    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1
        self.total_requests += 1
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": self.total_requests,
            "hit_rate": self.hit_rate,
            "tokens_saved": self.tokens_saved,
            "cost_saved_usd": self.cost_saved
        }


# ==================== Gemini Cache ====================

class GeminiCache:
    """
    🚀 INTELLIGENT CACHING FOR GEMINI 3
    
    Features:
    - Redis-backed distributed cache
    - Automatic cache key generation
    - TTL support (default 7 days)
    - Cache statistics tracking
    - In-memory fallback if Redis unavailable
    - Cost and token tracking
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        default_ttl: int = 604800  # 7 days
    ):
        self.default_ttl = default_ttl
        self.stats = CacheStatistics()
        
        # Initialize Redis or fallback to in-memory
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=False  # Handle bytes
                )
                # Test connection
                self.redis.ping()
                self.backend = "redis"
                logger.info("gemini_cache_initialized", backend="redis")
            except Exception as e:
                logger.warning("redis_connection_failed", error=str(e))
                self.redis = None
                self.backend = "memory"
                self._memory_cache: Dict[str, tuple] = {}  # (value, expiry)
                logger.info("gemini_cache_initialized", backend="memory_fallback")
        else:
            self.redis = None
            self.backend = "memory"
            self._memory_cache: Dict[str, tuple] = {}
            logger.info("gemini_cache_initialized", backend="memory_fallback")
    
    def generate_cache_key(
        self,
        prompt: str,
        model: str,
        thinking_level: Optional[str] = None,
        images: Optional[list] = None,
        **kwargs
    ) -> str:
        """
        Generate unique cache key from request parameters.
        
        Args:
            prompt: The prompt text
            model: Model name
            thinking_level: Thinking level if applicable
            images: List of images (will hash)
            **kwargs: Additional parameters
            
        Returns:
            SHA256 hash as cache key
        """
        
        # Build cache key components
        key_components = {
            "prompt": prompt,
            "model": model,
            "thinking_level": thinking_level,
            "enable_grounding": kwargs.get("enable_grounding", False),
            "response_schema": str(kwargs.get("response_schema")),
        }
        
        # Hash images if present
        if images:
            image_hashes = []
            for img in images:
                if isinstance(img, bytes):
                    img_hash = hashlib.md5(img).hexdigest()
                    image_hashes.append(img_hash)
            key_components["images"] = image_hashes
        
        # Create deterministic string
        key_string = json.dumps(key_components, sort_keys=True)
        
        # Generate SHA256 hash
        cache_key = hashlib.sha256(key_string.encode()).hexdigest()
        
        # Add prefix for namespacing
        return f"gemini:cache:{cache_key}"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        
        try:
            if self.backend == "redis" and self.redis:
                data = self.redis.get(key)
                if data:
                    result = json.loads(data)
                    
                    # Record hit
                    tokens_saved = result.get("usage", {}).get("total_tokens", 0)
                    cost_saved = result.get("usage", {}).get("cost_usd", 0.0)
                    self.stats.record_hit(tokens_saved, cost_saved)
                    
                    logger.debug("cache_hit", key=key[:16])
                    return result
            else:
                # Memory fallback
                if key in self._memory_cache:
                    value, expiry = self._memory_cache[key]
                    if datetime.utcnow() < expiry:
                        # Record hit
                        tokens_saved = value.get("usage", {}).get("total_tokens", 0)
                        cost_saved = value.get("usage", {}).get("cost_usd", 0.0)
                        self.stats.record_hit(tokens_saved, cost_saved)
                        
                        logger.debug("cache_hit", key=key[:16], backend="memory")
                        return value
                    else:
                        # Expired, remove
                        del self._memory_cache[key]
            
            # Cache miss
            self.stats.record_miss()
            logger.debug("cache_miss", key=key[:16])
            return None
            
        except Exception as e:
            logger.error("cache_get_error", error=str(e))
            self.stats.record_miss()
            return None
    
    def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 7 days)
            
        Returns:
            True if successful
        """
        
        ttl = ttl or self.default_ttl
        
        try:
            # Add cache metadata
            cached_value = {
                **value,
                "_cached_at": datetime.utcnow().isoformat(),
                "_cache_ttl": ttl
            }
            
            if self.backend == "redis" and self.redis:
                self.redis.setex(
                    key,
                    ttl,
                    json.dumps(cached_value)
                )
                logger.debug("cache_set", key=key[:16], ttl=ttl)
            else:
                # Memory fallback
                expiry = datetime.utcnow() + timedelta(seconds=ttl)
                self._memory_cache[key] = (cached_value, expiry)
                logger.debug("cache_set", key=key[:16], ttl=ttl, backend="memory")
            
            return True
            
        except Exception as e:
            logger.error("cache_set_error", error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        try:
            if self.backend == "redis" and self.redis:
                self.redis.delete(key)
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
            
            logger.debug("cache_delete", key=key[:16])
            return True
        except Exception as e:
            logger.error("cache_delete_error", error=str(e))
            return False
    
    def clear(self, pattern: str = "gemini:cache:*") -> int:
        """
        Clear cache entries matching pattern.
        
        Args:
            pattern: Redis pattern to match
            
        Returns:
            Number of keys deleted
        """
        try:
            if self.backend == "redis" and self.redis:
                keys = self.redis.keys(pattern)
                if keys:
                    deleted = self.redis.delete(*keys)
                    logger.info("cache_cleared", keys_deleted=deleted)
                    return deleted
            else:
                # Memory fallback - clear all
                count = len(self._memory_cache)
                self._memory_cache.clear()
                logger.info("cache_cleared", keys_deleted=count, backend="memory")
                return count
            
            return 0
        except Exception as e:
            logger.error("cache_clear_error", error=str(e))
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self.stats.to_dict()
        stats["backend"] = self.backend
        stats["default_ttl_seconds"] = self.default_ttl
        
        # Add size info if memory backend
        if self.backend == "memory":
            stats["cache_size"] = len(self._memory_cache)
        
        return stats
    
    def reset_stats(self):
        """Reset cache statistics."""
        self.stats = CacheStatistics()
        logger.info("cache_stats_reset")


# ==================== Global Cache Instance ====================

# Singleton instance
_cache_instance: Optional[GeminiCache] = None


def get_cache() -> GeminiCache:
    """Get or create global cache instance."""
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = GeminiCache()
    
    return _cache_instance


def clear_cache():
    """Clear global cache."""
    cache = get_cache()
    return cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get global cache statistics."""
    cache = get_cache()
    return cache.get_stats()
