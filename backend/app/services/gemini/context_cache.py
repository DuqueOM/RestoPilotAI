"""
Gemini Context Caching for RestoPilotAI.

Implements Google Gemini's Context Caching API to avoid re-sending large
content (menu images, employee manuals, historical data) on every request.

Benefits:
- 75% cost reduction on cached input tokens
- Lower latency for repeated queries on the same content
- Ideal for menu digitization pipelines where the same image is analyzed
  for extraction, allergen detection, pricing, and visual quality scoring

Usage:
    cache_manager = ContextCacheManager()
    cache = await cache_manager.cache_menu_content(session_id, menu_images, menu_text)
    # Subsequent calls referencing this cache skip re-uploading the images
    result = await cache_manager.query_cached_content(cache.name, "Extract all menu items as JSON")
"""

import asyncio
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from google import genai
from google.genai import types
from loguru import logger

from app.core.config import get_settings


class ContextCacheManager:
    """
    Manages Gemini Context Caches for large, reusable content.

    Caches are server-side resources that store tokenized content so it
    doesn't need to be re-processed on every API call.  Each cache has a
    TTL (default 30 min) and is scoped to a single model.
    """

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model_primary  # gemini-3-pro-preview
        self._active_caches: Dict[str, Any] = {}  # session_id -> cache object

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def cache_menu_content(
        self,
        session_id: str,
        menu_images: Optional[List[bytes]] = None,
        menu_text: Optional[str] = None,
        ttl_minutes: int = 30,
    ) -> Optional[Any]:
        """
        Create a context cache containing menu images and/or extracted text.

        This cache is then reused for:
        - Menu item extraction (OCR)
        - Allergen detection
        - Pricing analysis
        - Visual quality scoring
        - BCG data enrichment

        Returns the cache object (with `.name` for future reference), or
        None if caching failed.
        """
        cache_key = self._session_cache_key(session_id, "menu")
        if cache_key in self._active_caches:
            logger.info("context_cache_hit", session_id=session_id, scope="menu")
            return self._active_caches[cache_key]

        parts: List[types.Part] = []

        if menu_text:
            parts.append(types.Part(text=f"[MENU CONTENT]\n{menu_text}"))

        if menu_images:
            for idx, img_bytes in enumerate(menu_images):
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/jpeg",
                            data=img_bytes,
                        )
                    )
                )
            logger.info(
                "context_cache_creating",
                session_id=session_id,
                images=len(menu_images),
                has_text=bool(menu_text),
            )

        if not parts:
            logger.warning("context_cache_empty_content", session_id=session_id)
            return None

        try:
            cache = await asyncio.to_thread(
                self.client.caches.create,
                model=self.model,
                config=types.CreateCachedContentConfig(
                    display_name=f"restopilot-menu-{session_id[:20]}",
                    contents=[types.Content(parts=parts, role="user")],
                    ttl=f"{ttl_minutes * 60}s",
                    system_instruction="You are RestoPilotAI, an expert restaurant analytics assistant. Analyze the cached menu content when asked.",
                ),
            )

            self._active_caches[cache_key] = cache
            logger.info(
                "context_cache_created",
                session_id=session_id,
                cache_name=cache.name,
                ttl_minutes=ttl_minutes,
            )
            return cache

        except Exception as e:
            logger.warning(f"context_cache_creation_failed: {e}")
            return None

    async def cache_business_docs(
        self,
        session_id: str,
        documents: List[Dict[str, Any]],
        ttl_minutes: int = 60,
    ) -> Optional[Any]:
        """
        Cache large business documents (employee manuals, historical menus,
        supplier catalogues) for repeated querying.
        """
        cache_key = self._session_cache_key(session_id, "docs")
        if cache_key in self._active_caches:
            return self._active_caches[cache_key]

        parts: List[types.Part] = []
        for doc in documents:
            if doc.get("text"):
                parts.append(types.Part(text=f"[{doc.get('title', 'Document')}]\n{doc['text']}"))
            if doc.get("data") and doc.get("mime_type"):
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=doc["mime_type"],
                            data=doc["data"],
                        )
                    )
                )

        if not parts:
            return None

        try:
            cache = await asyncio.to_thread(
                self.client.caches.create,
                model=self.model,
                config=types.CreateCachedContentConfig(
                    display_name=f"restopilot-docs-{session_id[:20]}",
                    contents=[types.Content(parts=parts, role="user")],
                    ttl=f"{ttl_minutes * 60}s",
                    system_instruction="You are RestoPilotAI. Analyze the cached business documents to provide restaurant intelligence.",
                ),
            )
            self._active_caches[cache_key] = cache
            logger.info("context_cache_docs_created", session_id=session_id, doc_count=len(documents))
            return cache
        except Exception as e:
            logger.warning(f"context_cache_docs_failed: {e}")
            return None

    async def query_cached_content(
        self,
        cache_name: str,
        query: str,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        response_mime_type: Optional[str] = None,
    ) -> Optional[str]:
        """
        Query against cached content.  Input tokens from the cache are
        billed at 75 % discount.
        """
        try:
            config_kwargs: Dict[str, Any] = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "cached_content": cache_name,
            }
            if response_mime_type:
                config_kwargs["response_mime_type"] = response_mime_type

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=query,
                config=types.GenerateContentConfig(**config_kwargs),
            )

            logger.info("context_cache_query_ok", cache=cache_name[:30])
            return response.text
        except Exception as e:
            logger.error(f"context_cache_query_failed: {e}")
            return None

    async def get_or_create_menu_cache(
        self,
        session_id: str,
        menu_images: Optional[List[bytes]] = None,
        menu_text: Optional[str] = None,
    ) -> Optional[str]:
        """
        Convenience method: returns the cache *name* string ready for use
        in GenerateContentConfig.cached_content.  Creates the cache if it
        doesn't exist yet.
        """
        cache = await self.cache_menu_content(session_id, menu_images, menu_text)
        return cache.name if cache else None

    def invalidate(self, session_id: str, scope: str = "menu") -> None:
        """Remove a cache entry (e.g. when menu is re-uploaded)."""
        key = self._session_cache_key(session_id, scope)
        if key in self._active_caches:
            del self._active_caches[key]
            logger.info("context_cache_invalidated", session_id=session_id, scope=scope)

    def get_stats(self) -> Dict[str, Any]:
        """Return current cache statistics."""
        return {
            "active_caches": len(self._active_caches),
            "cache_keys": list(self._active_caches.keys()),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _session_cache_key(session_id: str, scope: str) -> str:
        return f"{session_id}:{scope}"


# Singleton
_cache_manager: Optional[ContextCacheManager] = None


def get_context_cache_manager() -> ContextCacheManager:
    """Get or create the singleton ContextCacheManager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = ContextCacheManager()
    return _cache_manager
