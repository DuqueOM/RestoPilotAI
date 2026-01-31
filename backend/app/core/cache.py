"""
Caching System for RestoPilotAI.

Provides:
- In-memory cache with TTL
- Redis-compatible cache interface
- Cache manager for multi-tier caching
- Gemini response caching
- Menu/competitor data caching
"""

import asyncio
import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from loguru import logger

from app.core.config import get_settings

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """A cache entry with metadata."""

    value: T
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    hit_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    tags: list = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def touch(self) -> None:
        """Update access metadata."""
        self.hit_count += 1
        self.last_accessed = time.time()


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "size": self.size,
            "max_size": self.max_size,
            "hit_rate": round(self.hit_rate, 4),
        }


class BaseCache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[list] = None,
    ) -> bool:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all entries."""
        pass

    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass

    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Generate cache key from arguments."""
        content = json.dumps(
            {"args": args, "kwargs": kwargs}, sort_keys=True, default=str
        )
        return hashlib.sha256(content.encode()).hexdigest()


class InMemoryCache(BaseCache):
    """
    In-memory cache with TTL and LRU eviction.

    Features:
    - Configurable max size
    - TTL support per entry
    - LRU eviction when full
    - Tag-based invalidation
    - Async-safe with locks
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        cleanup_interval: int = 60,
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval

        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._stats = CacheStats(max_size=max_size)

        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def _cleanup_loop(self) -> None:
        """Background task to clean expired entries."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")

    async def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired
            ]

            for key in expired_keys:
                del self._cache[key]
                self._stats.evictions += 1

            self._stats.size = len(self._cache)

            if expired_keys:
                logger.debug(
                    f"Cache cleanup: removed {len(expired_keys)} expired entries"
                )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats.misses += 1
                return None

            if entry.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                self._stats.size = len(self._cache)
                return None

            entry.touch()
            self._stats.hits += 1
            return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[list] = None,
    ) -> bool:
        """Set value in cache."""
        async with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()

            ttl = ttl if ttl is not None else self.default_ttl
            expires_at = time.time() + ttl if ttl > 0 else None

            self._cache[key] = CacheEntry(
                value=value,
                expires_at=expires_at,
                tags=tags or [],
            )

            self._stats.size = len(self._cache)
            return True

    async def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find LRU entry
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)

        del self._cache[lru_key]
        self._stats.evictions += 1
        self._stats.size = len(self._cache)

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.size = len(self._cache)
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired:
                del self._cache[key]
                self._stats.size = len(self._cache)
                return False
            return True

    async def clear(self) -> None:
        """Clear all entries."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats.size = 0
            self._stats.evictions += count
            logger.info(f"Cache cleared: {count} entries removed")

    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all entries with a specific tag."""
        async with self._lock:
            keys_to_delete = [
                key for key, entry in self._cache.items() if tag in entry.tags
            ]

            for key in keys_to_delete:
                del self._cache[key]

            self._stats.size = len(self._cache)
            self._stats.evictions += len(keys_to_delete)

            return len(keys_to_delete)

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats


class RedisCache(BaseCache):
    """
    Redis-based cache implementation.

    Requires redis-py[hiredis] package.
    Falls back to InMemoryCache if Redis unavailable.
    """

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        prefix: str = "RestoPilotAI:",
        default_ttl: int = 3600,
    ):
        self.url = url
        self.prefix = prefix
        self.default_ttl = default_ttl

        self._client = None
        self._stats = CacheStats()
        self._fallback: Optional[InMemoryCache] = None

    async def connect(self) -> bool:
        """Connect to Redis server."""
        try:
            import redis.asyncio as redis

            self._client = redis.from_url(self.url, decode_responses=True)
            await self._client.ping()
            logger.info(f"Connected to Redis at {self.url}")
            return True

        except ImportError:
            logger.warning("redis package not installed, using in-memory fallback")
            self._fallback = InMemoryCache()
            await self._fallback.start()
            return False

        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory fallback")
            self._fallback = InMemoryCache()
            await self._fallback.start()
            return False

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None

        if self._fallback:
            await self._fallback.stop()
            self._fallback = None

    def _key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self._fallback:
            return await self._fallback.get(key)

        try:
            value = await self._client.get(self._key(key))

            if value is None:
                self._stats.misses += 1
                return None

            self._stats.hits += 1
            return json.loads(value)

        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self._stats.misses += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[list] = None,
    ) -> bool:
        """Set value in cache."""
        if self._fallback:
            return await self._fallback.set(key, value, ttl, tags)

        try:
            ttl = ttl if ttl is not None else self.default_ttl
            serialized = json.dumps(value, default=str)

            if ttl > 0:
                await self._client.setex(self._key(key), ttl, serialized)
            else:
                await self._client.set(self._key(key), serialized)

            # Store tags if provided
            if tags:
                for tag in tags:
                    await self._client.sadd(f"{self.prefix}tag:{tag}", key)
                    await self._client.expire(f"{self.prefix}tag:{tag}", ttl)

            return True

        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if self._fallback:
            return await self._fallback.delete(key)

        try:
            result = await self._client.delete(self._key(key))
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._fallback:
            return await self._fallback.exists(key)

        try:
            return await self._client.exists(self._key(key)) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    async def clear(self) -> None:
        """Clear all entries with prefix."""
        if self._fallback:
            await self._fallback.clear()
            return

        try:
            cursor = 0
            while True:
                cursor, keys = await self._client.scan(
                    cursor=cursor, match=f"{self.prefix}*", count=100
                )
                if keys:
                    await self._client.delete(*keys)
                if cursor == 0:
                    break

            logger.info("Redis cache cleared")

        except Exception as e:
            logger.error(f"Redis clear error: {e}")

    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all entries with a specific tag."""
        if self._fallback:
            return await self._fallback.invalidate_by_tag(tag)

        try:
            tag_key = f"{self.prefix}tag:{tag}"
            keys = await self._client.smembers(tag_key)

            if keys:
                full_keys = [self._key(k) for k in keys]
                await self._client.delete(*full_keys, tag_key)

            return len(keys)

        except Exception as e:
            logger.error(f"Redis invalidate_by_tag error: {e}")
            return 0

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        if self._fallback:
            return self._fallback.get_stats()
        return self._stats


class CacheManager:
    """
    Multi-tier cache manager.

    Features:
    - L1 (in-memory) + L2 (Redis) caching
    - Automatic fallback
    - Cache-aside pattern helpers
    - Gemini response caching
    """

    def __init__(
        self,
        l1_max_size: int = 500,
        l1_ttl: int = 300,
        redis_url: Optional[str] = None,
        redis_ttl: int = 3600,
    ):
        self.l1 = InMemoryCache(max_size=l1_max_size, default_ttl=l1_ttl)
        self.l2: Optional[RedisCache] = None

        if redis_url:
            self.l2 = RedisCache(url=redis_url, default_ttl=redis_ttl)

    async def start(self) -> None:
        """Initialize cache connections."""
        await self.l1.start()

        if self.l2:
            await self.l2.connect()

    async def stop(self) -> None:
        """Close cache connections."""
        await self.l1.stop()

        if self.l2:
            await self.l2.disconnect()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get from cache with L1 -> L2 fallback.
        """
        # Try L1 first
        value = await self.l1.get(key)
        if value is not None:
            return value

        # Try L2 if available
        if self.l2:
            value = await self.l2.get(key)
            if value is not None:
                # Populate L1
                await self.l1.set(key, value)
                return value

        return None

    async def set(
        self,
        key: str,
        value: Any,
        l1_ttl: Optional[int] = None,
        l2_ttl: Optional[int] = None,
        tags: Optional[list] = None,
    ) -> bool:
        """
        Set in both cache tiers.
        """
        # Set in L1
        l1_result = await self.l1.set(key, value, l1_ttl, tags)

        # Set in L2 if available
        l2_result = True
        if self.l2:
            l2_result = await self.l2.set(key, value, l2_ttl, tags)

        return l1_result and l2_result

    async def delete(self, key: str) -> bool:
        """Delete from both tiers."""
        l1_result = await self.l1.delete(key)
        l2_result = True

        if self.l2:
            l2_result = await self.l2.delete(key)

        return l1_result or l2_result

    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate entries by tag in both tiers."""
        count = await self.l1.invalidate_by_tag(tag)

        if self.l2:
            count += await self.l2.invalidate_by_tag(tag)

        return count

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
        tags: Optional[list] = None,
    ) -> Any:
        """
        Cache-aside pattern: get from cache or compute and store.
        """
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()

        # Store in cache
        await self.set(key, value, ttl, ttl, tags)

        return value

    def get_stats(self) -> Dict[str, Any]:
        """Get combined cache statistics."""
        stats = {
            "l1": self.l1.get_stats().to_dict(),
        }

        if self.l2:
            stats["l2"] = self.l2.get_stats().to_dict()

        return stats


def cached(
    ttl: int = 3600,
    key_prefix: str = "",
    tags: Optional[list] = None,
    cache_instance: Optional[BaseCache] = None,
):
    """
    Decorator for caching function results.

    Usage:
        @cached(ttl=300, key_prefix="menu_extraction")
        async def extract_menu(image_data: bytes) -> dict:
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        _cache = cache_instance or InMemoryCache()

        async def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            cache_key = f"{key_prefix}:{BaseCache.generate_key(*args, **kwargs)}"

            # Try cache
            cached_value = await _cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value

            # Compute value
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Cache result
            await _cache.set(cache_key, result, ttl, tags)

            return result

        return wrapper

    return decorator


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager

    if _cache_manager is None:
        settings = get_settings()
        _cache_manager = CacheManager(redis_url=settings.redis_url)
        await _cache_manager.start()

    return _cache_manager


async def shutdown_cache() -> None:
    """Shutdown global cache manager."""
    global _cache_manager

    if _cache_manager:
        await _cache_manager.stop()
        _cache_manager = None
