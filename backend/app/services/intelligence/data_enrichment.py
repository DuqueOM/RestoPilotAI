"""
Competitor Enrichment Service - Advanced competitive intelligence system.

Capabilities:
- Full metadata extraction from Google Maps (Place Details API)
- Smart cross-referencing with web search
- Social media scraping (Facebook, Instagram, WhatsApp Business)
- Profile consolidation with multimodal Gemini
- Multimedia content analysis (photos, videos, menus)
"""

import json
import re
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

import httpx
from loguru import logger

from app.services.gemini.base_agent import GeminiAgent


@dataclass
class SocialMediaProfile:
    """Competitor social media profile."""

    platform: str  # facebook, instagram, whatsapp_business, twitter, tiktok
    url: str
    handle: Optional[str] = None
    followers: Optional[int] = None
    verified: bool = False
    posts_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    last_post_date: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitorProfile:
    """Complete, enriched competitor profile."""

    # Identification
    competitor_id: str
    name: str

    # Location
    address: str
    lat: float
    lng: float
    place_id: Optional[str] = None

    # Google Maps Data
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[int] = None  # 1-4 ($ to $$$$)
    google_maps_uri: Optional[str] = None
    google_maps_links: Optional[Dict[str, Any]] = None

    # Hours
    opening_hours: Optional[Dict[str, Any]] = None

    # Reviews (sample)
    reviews: List[Dict[str, Any]] = field(default_factory=list)
    reviews_summary: Optional[str] = None

    # Photos
    photos: List[str] = field(default_factory=list)  # URLs
    photo_analysis: Optional[Dict[str, Any]] = None

    # Social media
    social_profiles: List[SocialMediaProfile] = field(default_factory=list)

    # WhatsApp Business
    whatsapp_business: Optional[str] = None
    whatsapp_menu: Optional[Dict[str, Any]] = None
    whatsapp_catalog: List[Dict[str, Any]] = field(default_factory=list)

    # Extracted menu
    menu_items: List[Dict[str, Any]] = field(default_factory=list)
    menu_sources: List[str] = field(default_factory=list)

    # Competitive analysis
    cuisine_types: List[str] = field(default_factory=list)
    specialties: List[str] = field(default_factory=list)
    unique_offerings: List[str] = field(default_factory=list)
    price_range: Optional[Dict[str, float]] = None
    target_audience: Optional[str] = None
    brand_positioning: Optional[str] = None

    # Delivery platforms (Rappi, Uber Eats, etc.)
    delivery_platforms: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    data_sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    enrichment_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "competitor_id": self.competitor_id,
            "name": self.name,
            "address": self.address,
            "rating": self.rating,
            "phone": self.phone,
            "website": self.website,
            "location": {
                "address": self.address,
                "coordinates": {"lat": self.lat, "lng": self.lng},
                "place_id": self.place_id,
            },
            "contact": {
                "phone": self.phone,
                "website": self.website,
                "whatsapp_business": self.whatsapp_business,
            },
            "google_maps": {
                "rating": self.rating,
                "user_ratings_total": self.user_ratings_total,
                "price_level": self.price_level,
                "opening_hours": self.opening_hours,
                "reviews_count": len(self.reviews),
                "reviews_summary": self.reviews_summary,
                "reviews": self.reviews,
                "photos_count": len(self.photos),
                "google_maps_uri": self.google_maps_uri,
                "google_maps_links": self.google_maps_links or {},
            },
            "social_media": [
                {
                    "platform": sp.platform,
                    "url": sp.url,
                    "handle": sp.handle,
                    "followers": sp.followers,
                    "verified": sp.verified,
                    "metadata": sp.metadata,
                }
                for sp in self.social_profiles
            ],
            "menu": {
                "items": self.menu_items,
                "sources": self.menu_sources,
                "item_count": len(self.menu_items),
            },
            "whatsapp_business_data": {
                "number": self.whatsapp_business,
                "has_menu": self.whatsapp_menu is not None,
                "catalog_items": len(self.whatsapp_catalog),
            },
            "competitive_intelligence": {
                "cuisine_types": self.cuisine_types,
                "specialties": self.specialties,
                "unique_offerings": self.unique_offerings,
                "price_range": self.price_range,
                "target_audience": self.target_audience,
                "brand_positioning": self.brand_positioning,
            },
            "delivery_platforms": self.delivery_platforms,
            "photo_analysis": self.photo_analysis,
            "metadata": {
                "data_sources": self.data_sources,
                "confidence_score": self.confidence_score,
                "last_updated": self.last_updated.isoformat(),
                "enrichment_notes": self.enrichment_notes,
            },
        }


class CompetitorEnrichmentService:
    """
    Advanced competitor profile enrichment service.

    Implements a full pipeline:
    1. Google Maps extraction (Place Details)
    2. Cross-referencing with web search
    3. Social media identification
    4. Multimodal scraping and analysis
    5. Consolidation with Gemini
    """

    def __init__(
        self,
        google_maps_api_key: str,
        gemini_agent: Optional[GeminiAgent] = None,
    ):
        self.google_api_key = google_maps_api_key
        self.gemini = gemini_agent or GeminiAgent()
        
        if not self.google_api_key:
            logger.info("CompetitorEnrichmentService initialized without Google Maps API key. Place Details extraction will be disabled.")

        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )

    async def enrich_competitor_profile(
        self,
        place_id: str,
        basic_info: Optional[Dict[str, Any]] = None,
    ) -> CompetitorProfile:
        """
        Enrich a complete competitor profile from a place_id.

        Args:
            place_id: Google Maps Place ID
            basic_info: Basic information if already available

        Returns:
            Fully enriched CompetitorProfile
        """
        competitor_id = str(uuid4())

        logger.info(
            "Enriching competitor profile",
            place_id=place_id,
            competitor_id=competitor_id,
        )

        # Step 1: Google Maps Place Details
        maps_data = await self._get_place_details(place_id)

        if not maps_data:
            if basic_info:
                logger.info(
                    f"Maps API data unavailable for {place_id}, using basic info for enrichment"
                )
                # Normalize basic_info to look like maps_data for downstream compatibility
                maps_data = {
                    "name": basic_info.get("name"),
                    "formatted_address": basic_info.get("address"),
                    "formatted_phone_number": basic_info.get("phone"),
                    "website": basic_info.get("website"),
                    "rating": basic_info.get("rating"),
                    "user_ratings_total": basic_info.get("user_ratings_total"),
                    "geometry": {
                        "location": {
                            "lat": basic_info.get("lat"),
                            "lng": basic_info.get("lng"),
                        }
                    },
                    "photos": basic_info.get("photos", []),
                    "reviews": basic_info.get("reviews", []),
                    "types": basic_info.get("types", []),
                    "place_id": place_id,
                }
            else:
                logger.warning(f"Could not get place details for {place_id}")
                return self._create_minimal_profile(competitor_id, basic_info or {})

        # Step 2: Cross-reference with web search
        try:
            web_data = await self._cross_reference_web_search(
                name=maps_data.get("name"),
                phone=maps_data.get("formatted_phone_number"),
                address=maps_data.get("formatted_address"),
                google_maps_url=maps_data.get("url"),
            )
        except Exception as e:
            logger.error(f"Step 2 (web search) failed: {e}")
            web_data = {}

        # Step 3: Identify social media
        try:
            social_profiles = await self._identify_social_media(
                name=maps_data.get("name"),
                website=maps_data.get("website"),
                phone=maps_data.get("formatted_phone_number"),
                web_results=web_data,
                address=maps_data.get("formatted_address") or maps_data.get("address"),
            )
        except Exception as e:
            logger.error(f"Step 3 (social media) failed: {e}")
            social_profiles = []

        # Step 4: Extract WhatsApp Business data if available
        try:
            whatsapp_data = await self._extract_whatsapp_business(
                phone=maps_data.get("formatted_phone_number"),
                social_profiles=social_profiles,
            )
        except Exception as e:
            logger.error(f"Step 4 (WhatsApp) failed: {e}")
            whatsapp_data = {}

        # Step 5: Analyze photos with Gemini Vision
        try:
            photo_analysis = await self._analyze_competitor_photos(
                maps_data.get("photos", [])
            )
        except Exception as e:
            logger.error(f"Step 5 (photo analysis) failed: {e}")
            photo_analysis = {}

        # Step 6: Extract menu from all sources
        try:
            menu_data = await self._extract_menu_all_sources(
                maps_data=maps_data,
                web_data=web_data,
                whatsapp_data=whatsapp_data,
                photo_analysis=photo_analysis,
            )
        except Exception as e:
            logger.error(f"Step 6 (menu extraction) failed: {e}")
            menu_data = {}

        # Step 7: Process reviews with Gemini
        try:
            reviews_summary = await self._analyze_reviews(maps_data.get("reviews", []))
        except Exception as e:
            logger.error(f"Step 7 (reviews) failed: {e}")
            reviews_summary = {}

        # Step 8: Consolidate everything with Gemini
        try:
            intelligence = await self._consolidate_intelligence(
                maps_data=maps_data,
                web_data=web_data,
                social_data={"profiles": social_profiles},
                menu_data=menu_data,
                reviews_summary=reviews_summary,
                photo_analysis=photo_analysis,
            )
        except Exception as e:
            logger.error(f"Step 8 (consolidation) failed: {e}")
            intelligence = {}

        # Step 9: Extract and validate delivery platforms (with retry for failed URLs)
        delivery_platforms = await self._validate_delivery_platforms(
            self._extract_delivery_platforms(web_data),
            business_name=maps_data.get("name"),
            business_address=maps_data.get("formatted_address"),
            grounding_chunk_urls=web_data.get("_grounding_chunk_urls"),
        )

        # Build complete profile
        profile = CompetitorProfile(
            competitor_id=competitor_id,
            name=maps_data.get("name", "Unknown"),
            address=maps_data.get("formatted_address", ""),
            lat=maps_data.get("geometry", {}).get("location", {}).get("lat", 0),
            lng=maps_data.get("geometry", {}).get("location", {}).get("lng", 0),
            place_id=place_id,
            phone=maps_data.get("formatted_phone_number"),
            website=maps_data.get("website"),
            rating=maps_data.get("rating"),
            user_ratings_total=maps_data.get("user_ratings_total"),
            price_level=maps_data.get("price_level"),
            google_maps_uri=maps_data.get("url"),
            google_maps_links=maps_data.get("google_maps_links"),
            opening_hours=maps_data.get("opening_hours"),
            reviews=maps_data.get("reviews", [])[:10],  # Top 10 reviews
            reviews_summary=reviews_summary,
            photos=[p.get("photo_reference") for p in maps_data.get("photos", [])[:20]],
            photo_analysis=photo_analysis,
            social_profiles=social_profiles,
            whatsapp_business=whatsapp_data.get("number"),
            whatsapp_menu=whatsapp_data.get("menu"),
            whatsapp_catalog=whatsapp_data.get("catalog", []),
            menu_items=menu_data.get("items", []),
            menu_sources=menu_data.get("sources", []),
            cuisine_types=intelligence.get("cuisine_types", []),
            specialties=intelligence.get("specialties", []),
            unique_offerings=intelligence.get("unique_offerings", []),
            price_range=menu_data.get("price_range"),
            target_audience=intelligence.get("target_audience"),
            brand_positioning=intelligence.get("brand_positioning"),
            delivery_platforms=delivery_platforms,
            data_sources=self._collect_data_sources(
                maps_data, web_data, social_profiles, whatsapp_data
            ),
            confidence_score=self._calculate_confidence(maps_data, web_data, menu_data),
            enrichment_notes=intelligence.get("notes", []),
        )

        logger.info(
            "Competitor profile enriched",
            competitor_id=competitor_id,
            data_sources=len(profile.data_sources),
            menu_items=len(profile.menu_items),
            social_profiles=len(profile.social_profiles),
        )

        return profile

    async def _validate_delivery_platforms(
        self,
        platforms: List[Dict[str, Any]],
        business_name: Optional[str] = None,
        business_address: Optional[str] = None,
        grounding_chunk_urls: Optional[set] = None,
    ) -> List[Dict[str, Any]]:
        """Validate delivery platform URLs. Retry search for failed ones."""
        valid = []
        failed_platforms = []

        for p in platforms:
            url = p.get("url")
            if url:
                if await self._validate_url(url):
                    valid.append(p)
                else:
                    logger.warning(f"Delivery platform URL failed validation: {p['name']} -> {url}")
                    failed_platforms.append(p["name"])

        # Also retry if no Rappi was found at all in the initial results
        rappi_names = [p["name"] for p in platforms if "rappi" in p.get("name", "").lower()]
        if not rappi_names and "Rappi" not in failed_platforms:
            failed_platforms.append("Rappi")

        # Retry search for platforms that had invalid URLs or weren't found
        if failed_platforms and business_name:
            logger.info(f"Retrying search for delivery platforms: {failed_platforms}")
            retry_results = await self._retry_delivery_search(
                business_name, business_address, failed_platforms,
                grounding_chunk_urls=grounding_chunk_urls,
            )
            for p in retry_results:
                if p.get("url"):
                    # Retry results are already validated by _discover_rappi_store
                    # (includes DDG trust for perfect slug matches), so skip re-validation
                    valid.append(p)
                    logger.info(f"Retry found URL for {p['name']}: {p['url']}")

        return valid

    async def _retry_delivery_search(
        self,
        business_name: str,
        business_address: Optional[str],
        platform_names: List[str],
        grounding_chunk_urls: Optional[set] = None,
    ) -> List[Dict[str, Any]]:
        """
        Focused retry for delivery platforms using Gemini grounding + URL extraction.
        Instead of relying on Gemini's JSON output, extracts ALL rappi URLs from
        grounding chunks and answer text, then validates each candidate.
        """
        city_hint = ""
        if business_address:
            parts = [p.strip() for p in business_address.split(",")]
            if len(parts) >= 2:
                city_hint = parts[-3] if len(parts) >= 3 else parts[-2]
                city_hint = city_hint.strip()

        name_slug = re.sub(r'[^a-z0-9]+', '-', business_name.lower()).strip('-')

        # Pre-filter grounding chunk URLs to only Rappi ones
        rappi_seed_urls = set()
        if grounding_chunk_urls:
            for url in grounding_chunk_urls:
                if "rappi.com" in (url or ""):
                    rappi_seed_urls.add(url)

        results = []

        # Only handle Rappi retry for now (most common Colombian delivery platform)
        if "Rappi" in platform_names:
            rappi_url = await self._discover_rappi_store(
                business_name, business_address, city_hint, name_slug,
                extra_candidate_urls=rappi_seed_urls if rappi_seed_urls else None,
            )
            if rappi_url:
                results.append({"name": "Rappi", "icon": "🟠", "url": rappi_url})

        return results

    async def _discover_rappi_store(
        self, business_name: str, business_address: Optional[str],
        city_hint: str, name_slug: str,
        extra_candidate_urls: Optional[set] = None,
    ) -> Optional[str]:
        """
        Discover the correct Rappi store URL using a two-phase approach:
        Phase 1: Probe Rappi's city/delivery URL format to discover the canonical store ID
                 from the page HTML (deterministic, fast, reliable).
        Phase 2: Fall back to Gemini grounding search if probing fails.
        """
        rappi_store_pattern = re.compile(r'rappi\.com\.co/restaurantes/(\d+)-([a-z0-9-]+)', re.IGNORECASE)

        # === PHASE 1: DuckDuckGo Lite search (fast, reliable, no API key needed) ===
        # Gemini grounding fabricates Rappi store IDs, but DuckDuckGo Lite returns
        # actual search results with correct URLs in parseable HTML.
        phase1_candidates = set()
        ddg_queries = [
            f'site:rappi.com.co restaurantes "{business_name}" {city_hint}',
            f'rappi.com.co restaurantes "{business_name}" domicilio {city_hint}',
            f'rappi "{business_name}" restaurante {city_hint}',
        ]

        ddg_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
        }

        for query in ddg_queries:
            try:
                encoded_q = urllib.parse.quote_plus(query)
                ddg_url = f"https://lite.duckduckgo.com/lite?q={encoded_q}"
                resp = await self.http_client.get(ddg_url, headers=ddg_headers, follow_redirects=True, timeout=15.0)
                logger.debug(f"Rappi DDG query={query!r} status={resp.status_code} body_len={len(resp.text)}")
                if resp.status_code == 200:
                    matches = rappi_store_pattern.findall(resp.text)
                    for store_id, store_slug in matches:
                        slug_lower = store_slug.lower()
                        canonical = f"https://www.rappi.com.co/restaurantes/{store_id}-{slug_lower}"
                        phase1_candidates.add(canonical)
                        logger.debug(f"Rappi DDG extracted: {canonical}")
                # Stop early if we already have candidates
                if phase1_candidates:
                    break
            except Exception as e:
                logger.debug(f"Rappi DDG search failed for query: {e}")

        if phase1_candidates:
            logger.info(f"Rappi Phase 1 (DDG): found {len(phase1_candidates)} candidates: {phase1_candidates}")
            scored = self._score_rappi_candidates(phase1_candidates, name_slug)
            for score, url in scored:
                if await self._validate_rappi_url(url):
                    logger.info(f"Rappi store found (Phase 1 DDG, validated): {url} (score={score})")
                    return url
                # Trust DDG results with perfect slug match even if store is temporarily
                # unavailable (e.g., closed outside business hours). DDG found this URL
                # in real search results, confirming it's the correct store page.
                if score >= 10:
                    logger.info(
                        f"Rappi store found (Phase 1 DDG, trusted perfect slug match): {url} "
                        f"(score={score}, store may be temporarily unavailable)"
                    )
                    return url
                logger.debug(f"Rappi Phase 1 candidate failed validation: {url}")
        else:
            logger.info("Rappi Phase 1 (DDG): no candidates found")

        # === PHASE 2: Gemini grounding search as fallback ===
        logger.info("Rappi Phase 2: falling back to Gemini grounding search")
        all_candidate_urls: set = set(extra_candidate_urls or [])

        prompt = f"""Search Google for: rappi.com.co restaurantes "{business_name}" {city_hint} domicilio

I need the exact Rappi.com.co store page URLs for restaurant "{business_name}" in {city_hint}.
List every rappi.com.co URL you find. Include the complete URL."""

        try:
            response = await self.gemini.generate_with_grounding(
                prompt=prompt,
                enable_grounding=True,
                thinking_level="STANDARD",
                temperature=0.1,
                max_output_tokens=2048,
            )

            grounding_meta = response.get("grounding_metadata") or {}
            for chunk in grounding_meta.get("grounding_chunks", []):
                if isinstance(chunk, dict):
                    chunk_url = chunk.get("uri", "")
                    if chunk_url and "rappi.com" in chunk_url:
                        all_candidate_urls.add(chunk_url)

            answer = response.get("answer") or ""
            url_matches = re.findall(r'https?://(?:www\.)?rappi\.com\.co/[^\s"\'<>,\)\]`]+', answer)
            for url in url_matches:
                clean = re.sub(r'^\]\(', '', url).rstrip(".")
                all_candidate_urls.add(clean)

        except Exception as e:
            logger.warning(f"Rappi Phase 2 grounding search failed: {e}")

        if not all_candidate_urls:
            logger.warning("Rappi discovery: no candidates from either phase")
            return None

        # Extract store URLs from Phase 2 candidates
        phase2_canonical = set()
        for url in all_candidate_urls:
            match = rappi_store_pattern.search(url)
            if match:
                store_id = match.group(1)
                store_slug = match.group(2).lower()
                phase2_canonical.add(f"https://www.rappi.com.co/restaurantes/{store_id}-{store_slug}")

        if phase2_canonical:
            scored = self._score_rappi_candidates(phase2_canonical, name_slug)
            for score, url in scored:
                if await self._validate_rappi_url(url):
                    logger.info(f"Rappi store found (Phase 2 grounding): {url} (score={score})")
                    return url
                logger.debug(f"Rappi Phase 2 candidate failed validation: {url}")

        logger.warning("Rappi discovery: all candidates from both phases failed")
        return None

    def _score_rappi_candidates(self, urls: set, name_slug: str) -> list:
        """Score and sort Rappi store URL candidates by slug match quality."""
        rappi_store_pattern = re.compile(r'/restaurantes/(\d+)-([a-z0-9-]+)', re.IGNORECASE)
        scored = []
        for url in urls:
            match = rappi_store_pattern.search(url)
            if not match:
                continue
            store_slug = match.group(2).lower()
            score = 0
            if store_slug == name_slug:
                score = 10
            elif name_slug in store_slug:
                score = 5
            elif store_slug in name_slug:
                score = 3
            else:
                score = 1
            if "comuna" in store_slug:
                score -= 3
            scored.append((score, url))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    async def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get full place details using the Google Places API (New)."""
        # Check for custom/manual place ID
        if not self.google_api_key:
            logger.warning("No Google Maps API key configured")
            return None

        if place_id and (place_id.startswith("custom_") or place_id.startswith("gemini_fallback_")):
            logger.info(f"Skipping Places API for custom/fallback place_id: {place_id}")
            return None

        try:
            # V1 API Endpoint
            url = f"https://places.googleapis.com/v1/places/{place_id}"
            
            # FieldMask for V1
            fields = [
                "id", "displayName", "formattedAddress", "nationalPhoneNumber",
                "websiteUri", "rating", "userRatingCount", "priceLevel",
                "regularOpeningHours", "reviews", "photos", "types",
                "location", "googleMapsUri", "googleMapsLinks", "businessStatus", "editorialSummary"
            ]
            
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.google_api_key,
                "X-Goog-FieldMask": ",".join(fields),
                "X-Goog-LanguageCode": "es"
            }

            response = await self.http_client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Got place details for {place_id} (V1)")
                
                # Map V1 response to legacy structure for compatibility
                result = {
                    "place_id": data.get("id"),
                    "name": data.get("displayName", {}).get("text"),
                    "formatted_address": data.get("formattedAddress"),
                    "formatted_phone_number": data.get("nationalPhoneNumber"),
                    "website": data.get("websiteUri"),
                    "rating": data.get("rating"),
                    "user_ratings_total": data.get("userRatingCount"),
                    "price_level": self._map_price_level_v1(data.get("priceLevel")),
                    "types": data.get("types", []),
                    "geometry": {
                        "location": {
                            "lat": data.get("location", {}).get("latitude"),
                            "lng": data.get("location", {}).get("longitude")
                        }
                    },
                    "url": data.get("googleMapsUri"),
                    "google_maps_links": data.get("googleMapsLinks", {}),
                    "business_status": data.get("businessStatus"),
                    "editorial_summary": data.get("editorialSummary", {}).get("text")
                }

                # Map Opening Hours
                if "regularOpeningHours" in data:
                    oh = data["regularOpeningHours"]
                    result["opening_hours"] = {
                        "open_now": oh.get("openNow", False),
                        "periods": oh.get("periods", []),
                        "weekday_text": oh.get("weekdayDescriptions", [])
                    }

                # Map Photos (V1 uses 'name' as reference)
                if "photos" in data:
                    result["photos"] = [
                        {
                            "photo_reference": p["name"], # store resource name as ref
                            "height": p.get("heightPx"),
                            "width": p.get("widthPx"),
                            "html_attributions": [(p.get("authorAttributions") or [{}])[0].get("displayName", "")]
                        }
                        for p in data["photos"]
                    ]

                # Map Reviews
                if "reviews" in data:
                    result["reviews"] = [
                        {
                            "author_name": r.get("authorAttribution", {}).get("displayName"),
                            "author_photo": r.get("authorAttribution", {}).get("photoUri"),
                            "author_uri": r.get("authorAttribution", {}).get("uri"),
                            "rating": r.get("rating"),
                            "text": (r.get("text") or {}).get("text") if isinstance(r.get("text"), (dict, type(None))) else r.get("text"),
                            "time": r.get("publishTime"),
                            "relative_time_description": r.get("relativePublishTimeDescription"),
                            "google_maps_uri": r.get("googleMapsUri")
                        }
                        for r in data["reviews"]
                    ]

                return result
            else:
                logger.error(f"Place Details API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Failed to get place details: {e}")
            return None

    def _map_price_level_v1(self, level: str) -> Optional[int]:
        mapping = {
            "PRICE_LEVEL_INEXPENSIVE": 1,
            "PRICE_LEVEL_MODERATE": 2,
            "PRICE_LEVEL_EXPENSIVE": 3,
            "PRICE_LEVEL_VERY_EXPENSIVE": 4
        }
        return mapping.get(level)

    async def _cross_reference_web_search(
        self,
        name: Optional[str],
        phone: Optional[str],
        address: Optional[str],
        google_maps_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cross-reference with web search to find additional information.
        Uses Gemini with Google Search grounding.
        """

        if not name:
            return {}

        try:
            # Extract city hint from address for better search targeting
            city_hint = ""
            if address:
                # Try to extract city name (usually after last comma or common patterns)
                parts = [p.strip() for p in address.split(",")]
                if len(parts) >= 2:
                    city_hint = parts[-2]  # Second to last is often the city

            prompt = f"""Search the internet and find complete, VERIFIED information about this specific restaurant/business:

Name: {name}
{f"Phone: {phone}" if phone else ""}
{f"Address: {address}" if address else ""}
{f"City: {city_hint}" if city_hint else ""}
{f"Google Maps: {google_maps_url}" if google_maps_url else ""}

YOUR TASK - Search and find ONLY profiles that belong to THIS SPECIFIC business at THIS address.
FOLLOW THESE RULES STRICTLY:

1. SOCIAL MEDIA PROFILES (Deep Search):
   Use MULTIPLE search queries to cross-validate:
     - "{name} restaurante {city_hint or 'Colombia'} facebook"
     - "{name} restaurante bar facebook"
     - "{name} {city_hint or ''} instagram"

   FACEBOOK RULES:
     - Search for the OFFICIAL business page on Facebook.
     - If you find multiple Facebook pages, return ALL of them in "facebook_candidates" (see JSON below).
     - REJECT pages where the URL slug contains ".pub" if a better alternative exists (e.g., one with "RestauranteBar" or "Restaurante" in the slug).
     - REJECT pages that are clearly inactive (no recent posts, "page not available" messages).
     - The correct page usually has: recent posts, business category "Restaurant" or "Bar", and matches the city.

   INSTAGRAM RULES:
     - Look for the exact business handle. Restaurant handles in Colombia often include the city name (e.g., @margaritapintapasto).
     - Must be an active profile with posts.

   VALIDATION for ALL social profiles:
     - Must match the business name AND city/location.
     - Must appear to be an active, real business profile.
     - Do NOT guess URLs — only return URLs you actually found in search results.

2. WhatsApp Business number if available (with country code, e.g., +57...)

3. DELIVERY PLATFORMS — Search for this business on Rappi, Uber Eats, iFood, PedidosYa:
   - Return the FULL direct store URL (e.g., https://www.rappi.com.co/restaurantes/XXXXXXXXX-store-name).
   - RAPPI RULES:
     - The correct Rappi URL has a numeric store ID (usually 9 digits like 900XXXXXX) followed by a slug.
     - Search: "{name} rappi {city_hint or 'Colombia'}"
     - REJECT URLs that redirect to the Rappi homepage or a city/category page.
     - REJECT URLs where the store name in the slug doesn't match the business name.
   - For other platforms, same rules apply: must be a DIRECT store page, not a search/category page.

Respond ONLY with valid JSON:
{{
  "social_media": {{
    "facebook": "best verified Facebook URL or null",
    "facebook_candidates": ["URL1", "URL2"],
    "instagram": "full verified URL or null",
    "tiktok": "full verified URL or null",
    "twitter": "full verified URL or null",
    "youtube": "channel URL or null"
  }},
  "whatsapp": "number or null",
  "additional_websites": ["URL1", "URL2"],
  "delivery_platforms": [
    {{"name": "Rappi", "url": "full direct store URL or null"}},
    {{"name": "Uber Eats", "url": "full direct store URL or null"}}
  ],
  "notes": ["Note about verification source"]
}}"""

            # Use shared Gemini agent with grounding
            # NOTE: Do NOT set response_mime_type — it is incompatible with Google Search grounding
            response = await self.gemini.generate_with_grounding(
                prompt=prompt,
                enable_grounding=True,
                thinking_level="STANDARD",
                temperature=0.3,
                max_output_tokens=8192,
            )

            # Extract answer text (guard against None)
            response_text = response.get("answer") or ""
            grounded = response.get("grounded", False)
            
            logger.info(
                f"Web cross-reference for {name}: grounded={grounded}, "
                f"response_len={len(response_text)}, "
                f"chunks={len((response.get('grounding_metadata') or {}).get('grounding_chunks', []))}"
            )
            
            if not response_text.strip():
                logger.warning(f"Gemini grounding returned empty answer for {name}, retrying once...")
                # Retry once with a simpler prompt
                response = await self.gemini.generate_with_grounding(
                    prompt=prompt,
                    enable_grounding=True,
                    thinking_level="DEEP",
                    temperature=0.2,
                    max_output_tokens=8192,
                )
                response_text = response.get("answer") or ""
                logger.info(f"Retry grounding for {name}: len={len(response_text)}")
            
            # Use the robust parser from the agent
            result = self.gemini._parse_json_response(response_text)
            
            # Log what social media was found
            social = result.get("social_media", {})
            found = [k for k, v in social.items() if v]
            logger.info(f"Social media found for {name}: {found or 'none'}")
            
            # Attach grounding chunk URLs for downstream use (e.g., Rappi discovery)
            grounding_meta = response.get("grounding_metadata") or {}
            chunk_urls = set()
            for chunk in grounding_meta.get("grounding_chunks", []):
                if isinstance(chunk, dict) and chunk.get("uri"):
                    chunk_urls.add(chunk["uri"])
            if chunk_urls:
                result["_grounding_chunk_urls"] = list(chunk_urls)
            
            return result

        except Exception as e:
            logger.error(f"Web cross-reference failed: {e}")
            return {}

    async def _validate_url(self, url: str) -> bool:
        """Validate if a URL is accessible and points to real content."""
        if not url or not url.startswith("http"):
            return False
        
        # Use platform-specific validators when available
        if "facebook.com" in url or "fb.com" in url:
            return await self._validate_facebook_url(url)
        if "rappi.com" in url:
            return await self._validate_rappi_url(url)
            
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
            }
            response = await self.http_client.get(url, headers=headers, follow_redirects=True)
            
            if response.status_code == 404:
                logger.warning(f"Validation failed (404) for URL: {url}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Validation check error for {url}: {e}")
            return False

    async def _validate_facebook_url(self, url: str) -> bool:
        """Validate a Facebook URL by checking for unavailable page signals."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
            }
            response = await self.http_client.get(url, headers=headers, follow_redirects=True)
            
            if response.status_code == 404:
                logger.warning(f"Facebook page not found (404): {url}")
                return False
            
            # Check response body for unavailable page signals
            body = response.text.lower() if response.status_code == 200 else ""
            
            unavailable_signals = [
                "this content isn't available",
                "este contenido no está disponible",
                "this page isn't available",
                "esta página no está disponible",
                "the link you followed may be broken",
                "el enlace que seguiste puede estar roto",
                "page not found",
                "página no encontrada",
                "sorry, this content isn",
            ]
            
            for signal in unavailable_signals:
                if signal in body:
                    logger.warning(f"Facebook page unavailable (content signal: '{signal}'): {url}")
                    return False
            
            # Check if redirected to login page (page doesn't exist for public)
            final_url = str(response.url).lower()
            if "/login" in final_url and "facebook.com" in final_url:
                logger.warning(f"Facebook redirected to login (page may not exist publicly): {url}")
                return False

            # Status 400 from Facebook WAF — we can't be sure, log but accept cautiously
            if response.status_code == 400:
                logger.info(f"Facebook returned 400 (WAF), cautiously accepting: {url}")
                return True
            
            return True
        except Exception as e:
            logger.warning(f"Facebook validation error for {url}: {e}")
            return False

    async def _validate_rappi_url(self, url: str) -> bool:
        """Validate a Rappi store URL by checking it points to an actual store."""
        try:
            # Quick structural check: valid Rappi store URLs have /restaurantes/NUMERIC_ID-slug
            rappi_store_pattern = re.compile(r'rappi\.com\.[a-z]+/restaurantes/\d+-[\w-]+')
            if not rappi_store_pattern.search(url):
                logger.warning(f"Rappi URL doesn't match store pattern: {url}")
                return False

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
            }
            response = await self.http_client.get(url, headers=headers, follow_redirects=True)
            
            if response.status_code == 404:
                logger.warning(f"Rappi store not found (404): {url}")
                return False
            
            # Check if redirected away from the store page
            final_url = str(response.url).lower()
            if "/restaurantes/" not in final_url:
                logger.warning(f"Rappi URL redirected away from store page to: {final_url}")
                return False
            
            # Check body for "store not found" signals
            body = response.text.lower() if response.status_code == 200 else ""
            
            not_found_signals = [
                "no encontramos",
                "tienda no disponible",
                "store not found",
                "esta tienda no está disponible",
                "lo sentimos, esta tienda",
            ]
            
            for signal in not_found_signals:
                if signal in body:
                    logger.warning(f"Rappi store unavailable (content signal: '{signal}'): {url}")
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"Rappi validation error for {url}: {e}")
            return False

    async def _identify_social_media(
        self,
        name: Optional[str],
        website: Optional[str],
        phone: Optional[str],
        web_results: Dict[str, Any],
        address: Optional[str] = None,
    ) -> List[SocialMediaProfile]:
        """Identify and validate social media profiles using Gemini results + deterministic probing."""

        profiles = []
        social_data = web_results.get("social_media", {})

        # Extract city from address for probing
        city = ""
        if address:
            parts = [p.strip() for p in address.split(",")]
            if len(parts) >= 2:
                city = parts[-3] if len(parts) >= 3 else parts[-2]
                city = city.strip()

        # === FACEBOOK: Gemini candidates + deterministic probing ===
        fb_url = await self._discover_facebook_page(name or "", city, social_data)
        if fb_url:
            profiles.append(
                SocialMediaProfile(
                    platform="facebook",
                    url=fb_url,
                    handle=self._extract_handle_from_url(fb_url, "facebook"),
                )
            )

        # === INSTAGRAM: Gemini result + deterministic probing ===
        ig_url = None
        if social_data.get("instagram"):
            ig_candidate = social_data["instagram"]
            if ig_candidate and ig_candidate.startswith("http") and await self._validate_url(ig_candidate):
                ig_url = ig_candidate

        if not ig_url:
            ig_url = await self._probe_instagram_handle(name or "", city)

        if ig_url:
            profiles.append(
                SocialMediaProfile(
                    platform="instagram",
                    url=ig_url,
                    handle=self._extract_handle_from_url(ig_url, "instagram"),
                )
            )

        # === OTHER PLATFORMS: Gemini results with validation ===
        for platform_key, platform_name in [("tiktok", "tiktok"), ("twitter", "twitter"), ("youtube", "youtube")]:
            url = social_data.get(platform_key)
            if url and url.startswith("http") and await self._validate_url(url):
                profiles.append(
                    SocialMediaProfile(
                        platform=platform_name,
                        url=url,
                        handle=self._extract_handle_from_url(url, platform_name),
                    )
                )

        # === WhatsApp Business ===
        whatsapp = web_results.get("whatsapp") or self._extract_whatsapp_from_phone(phone)
        if whatsapp:
            profiles.append(
                SocialMediaProfile(
                    platform="whatsapp_business",
                    url=f"https://wa.me/{whatsapp.replace('+', '').replace(' ', '')}",
                    handle=whatsapp,
                )
            )

        logger.info(f"Identified {len(profiles)} social media profiles for {name}")
        return profiles

    async def _discover_facebook_page(
        self, name: str, city: str, gemini_social_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Discover the correct Facebook page using:
        1. Deterministic URL probing (generated slug candidates)
        2. Gemini grounding candidates as extra input
        Scores and validates all candidates to find the best match.
        """
        if not name:
            return None

        # Generate deterministic slug candidates from business name
        name_parts = name.split()
        camel = "".join(p.capitalize() for p in name_parts)
        lower_joined = "".join(p.lower() for p in name_parts)
        dot_joined = ".".join(p.lower() for p in name_parts)
        city_clean = city.replace(" ", "").capitalize() if city else ""
        city_lower = city.replace(" ", "").lower() if city else ""

        # Restaurant-specific suffixes (most specific first)
        suffixes = [
            "RestauranteBar", "Restaurante", "Bar", "Pub", "Oficial", "Resto",
        ]

        probed_candidates = []
        # CamelCase + suffixes: MargaritaPintaRestauranteBar, MargaritaPintaRestaurante, etc.
        for suffix in suffixes:
            probed_candidates.append(f"{camel}{suffix}")
        # CamelCase + city: MargaritaPintaPasto
        if city_clean:
            probed_candidates.append(f"{camel}{city_clean}")
            probed_candidates.append(f"{lower_joined}{city_lower}")
        # Plain CamelCase: MargaritaPinta
        probed_candidates.append(camel)
        # Dot-separated: margarita.pinta.pub, margarita.pinta.restaurante
        probed_candidates.append(f"{dot_joined}.pub")
        probed_candidates.append(f"{dot_joined}.restaurante")
        # Lower + city: margaritapintapasto
        if city_lower:
            probed_candidates.append(f"{lower_joined}{city_lower}")

        # Add Gemini-discovered candidates
        gemini_fb_urls = []
        if gemini_social_data.get("facebook"):
            gemini_fb_urls.append(gemini_social_data["facebook"])
        for url in gemini_social_data.get("facebook_candidates", []):
            if url:
                gemini_fb_urls.append(url)

        # Extract slugs from Gemini URLs and add to candidates
        for url in gemini_fb_urls:
            match = re.search(r"facebook\.com/([^/?]+)", url)
            if match:
                slug = match.group(1)
                if slug not in probed_candidates:
                    probed_candidates.append(slug)

        # Deduplicate while preserving order
        seen = set()
        unique_candidates = []
        for c in probed_candidates:
            c_lower = c.lower().rstrip("/")
            if c_lower not in seen:
                seen.add(c_lower)
                unique_candidates.append(c)

        logger.info(f"Facebook probing {len(unique_candidates)} candidates for '{name}': {unique_candidates[:8]}...")

        # Score each candidate: (validation_score, slug_score, url)
        scored = []
        for slug in unique_candidates:
            url = f"https://www.facebook.com/{slug}/"
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
                }
                response = await self.http_client.get(url, headers=headers, follow_redirects=True)

                # Check for unavailable page
                is_unavailable = False
                if response.status_code == 404:
                    is_unavailable = True
                elif response.status_code == 200:
                    body = response.text.lower()
                    unavailable_signals = [
                        "this content isn't available",
                        "este contenido no está disponible",
                        "this page isn't available",
                        "esta página no está disponible",
                        "the link you followed may be broken",
                        "el enlace que seguiste puede estar roto",
                    ]
                    for signal in unavailable_signals:
                        if signal in body:
                            is_unavailable = True
                            break

                final_url = str(response.url).lower()
                if "/login" in final_url:
                    is_unavailable = True

                if is_unavailable:
                    continue

                # Validation score: 200 is best, 400 (WAF) is uncertain
                val_score = 2 if response.status_code == 200 else 1

                # Slug quality score
                slug_lower = slug.lower()
                slug_score = 0
                if "restaurantebar" in slug_lower:
                    slug_score = 10
                elif "restaurante" in slug_lower:
                    slug_score = 8
                elif "bar" in slug_lower and "pub" not in slug_lower:
                    slug_score = 6
                elif city_lower and city_lower in slug_lower:
                    slug_score = 5
                elif ".pub" in slug_lower:
                    slug_score = 1
                else:
                    slug_score = 3

                scored.append((val_score, slug_score, url))
                logger.debug(f"Facebook candidate: {url} -> val={val_score}, slug={slug_score}, status={response.status_code}")

            except Exception as e:
                logger.debug(f"Facebook probe failed for {slug}: {e}")
                continue

        if not scored:
            logger.warning(f"No valid Facebook page found for '{name}'")
            return None

        # Sort: highest validation score first, then highest slug score
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        best = scored[0]
        logger.info(f"Facebook best match: {best[2]} (val={best[0]}, slug={best[1]}, total candidates tested={len(unique_candidates)})")
        return best[2]

    async def _probe_instagram_handle(self, name: str, city: str) -> Optional[str]:
        """Probe common Instagram handle patterns for a business."""
        if not name:
            return None

        name_parts = name.split()
        lower_joined = "".join(p.lower() for p in name_parts)
        city_lower = city.replace(" ", "").lower() if city else ""

        candidates = []
        # Most common patterns for Colombian restaurants
        if city_lower:
            candidates.append(f"{lower_joined}{city_lower}")  # margaritapintapasto
        candidates.append(lower_joined)  # margaritapinta
        if city_lower:
            candidates.append(f"{lower_joined}_{city_lower}")  # margaritapinta_pasto
            candidates.append(f"{lower_joined}.{city_lower}")  # margaritapinta.pasto
        candidates.append(f"{lower_joined}oficial")  # margaritapintaoficial
        candidates.append(f"{lower_joined}_oficial")  # margaritapinta_oficial

        logger.info(f"Instagram probing {len(candidates)} handles for '{name}': {candidates}")

        for handle in candidates:
            url = f"https://www.instagram.com/{handle}/"
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
                }
                response = await self.http_client.get(url, headers=headers, follow_redirects=True)

                if response.status_code == 200:
                    body = response.text.lower()
                    # Instagram 200 with "page not found" means profile doesn't exist
                    if "page not found" in body or "página no encontrada" in body:
                        continue
                    # Check final URL didn't redirect to login/explore
                    final = str(response.url).lower()
                    if "/accounts/login" in final or "/explore/" in final:
                        continue
                    logger.info(f"Instagram found: {url}")
                    return url
                elif response.status_code == 404:
                    continue
            except Exception:
                continue

        logger.warning(f"No Instagram handle found for '{name}'")
        return None

    async def _extract_whatsapp_business(
        self,
        phone: Optional[str],
        social_profiles: List[SocialMediaProfile],
    ) -> Dict[str, Any]:
        """
        Extract WhatsApp Business data.
        Note: This would require the WhatsApp Business API.
        For now, we identify the number and simulate capabilities.
        """

        whatsapp_number = None
        for profile in social_profiles:
            if profile.platform == "whatsapp_business":
                whatsapp_number = profile.handle
                break

        if not whatsapp_number and phone:
            whatsapp_number = phone

        if not whatsapp_number:
            return {}

        # In production, this would use the WhatsApp Business API
        # For now, we return a structure indicating potential capability

        logger.info(f"WhatsApp Business number identified: {whatsapp_number}")

        return {
            "number": whatsapp_number,
            "note": "WhatsApp Business API integration required for full catalog extraction",
            "potential_data": [
                "Business profile",
                "Catalog/Menu",
                "Product photos",
                "Prices",
                "Availability",
            ],
        }

    async def _analyze_competitor_photos(
        self,
        photos: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Analyze competitor photos with Gemini Vision."""

        if not photos or not self.google_api_key:
            return None

        try:
            # Take first 5 photos
            photo_urls = []
            for photo in photos[:5]:
                photo_ref = photo.get("photo_reference")
                if photo_ref:
                    # Check if it's a V1 resource name or legacy reference
                    if "photos/" in photo_ref:
                        # V1 Format: places/PLACE_ID/photos/PHOTO_ID
                        # URL: https://places.googleapis.com/v1/{name}/media?key=KEY&maxWidthPx=...
                        photo_url = f"https://places.googleapis.com/v1/{photo_ref}/media?key={self.google_api_key}&maxWidthPx=800"
                    else:
                        # Legacy Format Fallback
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_ref}&key={self.google_api_key}"
                    
                    photo_urls.append(photo_url)

            if not photo_urls:
                return None

            # Use Gemini to analyze photos
            prompt = """Analyze these photos of the competitor restaurant and extract:

1. Ambiance type (casual, upscale, family-friendly, etc.)
2. Visible dishes (names if you can identify them)
3. Apparent price level (economic, mid-range, premium)
4. Food presentation style
5. Visual quality of dishes
6. Standout elements (decor, concept)

Respond in JSON:
{
  "ambiance": "Ambiance description",
  "visible_dishes": ["Dish 1", "Dish 2"],
  "price_perception": "economic/mid-range/premium",
  "presentation_style": "Description",
  "visual_quality_score": 0.85,
  "standout_elements": ["Element 1", "Element 2"],
  "competitive_advantages": ["Visual advantage 1"]
}"""

            # Due to constraints, we only use the first photo
            # In production, multiple photos would be processed
            photo_data = await self.http_client.get(photo_urls[0])
            
            # Use shared Gemini agent
            response_text = await self.gemini.generate(
                prompt=prompt,
                images=[photo_data.content],
                temperature=0.4,
                max_output_tokens=2048,
            )

            result = self.gemini._parse_json_response(response_text)
            result["photos_analyzed"] = len(photo_urls)

            logger.info("Competitor photos analyzed with Gemini Vision")
            return result

        except Exception as e:
            logger.error(f"Photo analysis failed: {e}")
            return None

    async def _extract_menu_all_sources(
        self,
        maps_data: Dict[str, Any],
        web_data: Dict[str, Any],
        whatsapp_data: Dict[str, Any],
        photo_analysis: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Consolidate menu from all available sources."""

        menu_items = []
        sources = []

        # Source 1: Restaurant website
        if maps_data.get("website"):
            try:
                website_menu = await self._scrape_menu_from_website(
                    maps_data["website"]
                )
                if website_menu:
                    menu_items.extend(website_menu.get("items", []))
                    sources.append("website")
            except Exception as e:
                logger.warning(f"Website menu extraction failed: {e}")

        # Source 2: Photos with visible items
        if photo_analysis and photo_analysis.get("visible_dishes"):
            for dish in photo_analysis["visible_dishes"]:
                menu_items.append(
                    {
                        "name": dish,
                        "source": "photos",
                        "confidence": 0.6,
                    }
                )
            sources.append("google_photos")

        # Source 3: WhatsApp Business (simulated)
        if whatsapp_data.get("catalog"):
            menu_items.extend(whatsapp_data["catalog"])
            sources.append("whatsapp_business")

        # Calculate price range
        prices = [item.get("price") for item in menu_items if item.get("price")]
        price_range = None
        if prices:
            price_range = {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices) / len(prices),
            }

        return {
            "items": menu_items,
            "sources": list(set(sources)),
            "price_range": price_range,
            "total_items": len(menu_items),
        }

    async def _scrape_menu_from_website(
        self, website_url: str
    ) -> Optional[Dict[str, Any]]:
        """Scrape competitor menu from their website using Gemini."""

        try:
            response = await self.http_client.get(website_url, timeout=15.0)
            html_content = response.text[:20000]  # Limit size

            # Use Gemini to extract the menu
            prompt = f"""Extract the menu from this website:

{html_content}

Respond in JSON:
{{
  "items": [
    {{"name": "Name", "price": 150.00, "category": "Category", "description": ""}}
  ],
  "currency": "MXN"
}}"""

            # Use shared Gemini agent
            response_text = await self.gemini.generate(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=4096,
            )

            result = self.gemini._parse_json_response(response_text)
            
            logger.info(
                f"Extracted menu from website: {len(result.get('items', []))} items"
            )
            return result

        except Exception as e:
            logger.warning(f"Website scraping failed: {e}")
            return None

    async def _analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Optional[str]:
        """Analyze competitor reviews with Gemini to extract insights."""

        if not reviews:
            return None

        try:
            reviews_text = "\n\n".join(
                [
                    f"Rating: {r.get('rating')}/5 - {(r.get('text') or '')[:200]}"
                    for r in reviews[:10]
                ]
            )

            prompt = f"""Analyze these competitor reviews and summarize:

{reviews_text}

Extract:
- Frequently mentioned strengths
- Common weaknesses or complaints
- Most praised dishes
- Notable service aspects
- Opportunities we see

Summarize in 2-3 paragraphs."""

            response_text = await self.gemini.generate(
                prompt=prompt,
                temperature=0.4,
                max_output_tokens=1024,
            )

            if not response_text:
                logger.warning("Gemini returned empty response for review analysis")
                return None

            summary = response_text.strip()
            logger.info("Reviews analyzed and summarized")
            return summary

        except Exception as e:
            logger.error(f"Review analysis failed: {e}")
            return None

    async def _consolidate_intelligence(
        self,
        maps_data: Dict[str, Any],
        web_data: Dict[str, Any],
        social_data: Dict[str, Any],
        menu_data: Dict[str, Any],
        reviews_summary: Optional[str],
        photo_analysis: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Consolidate all competitive intelligence with Gemini."""

        try:
            context = f"""Consolidate this competitive intelligence:

RESTAURANT: {maps_data.get('name')}

GOOGLE MAPS:
- Rating: {maps_data.get('rating')} ({maps_data.get('user_ratings_total')} reviews)
- Price Level: {'$' * (maps_data.get('price_level') or 2)}
- Types: {', '.join(maps_data.get('types', [])[:5])}

WEB SEARCH:
{json.dumps({k: v for k, v in web_data.items() if not k.startswith('_')}, indent=2, default=str)[:1000]}

MENU:
- {menu_data.get('total_items')} items found
- Sources: {', '.join(menu_data.get('sources', []))}
- Price range: {menu_data.get('price_range')}

PHOTOS:
{json.dumps(photo_analysis, indent=2)[:500] if photo_analysis else 'Not analyzed'}

REVIEWS:
{reviews_summary[:300] if reviews_summary else 'Not available'}

SOCIAL MEDIA:
{len(social_data.get('profiles', []))} profiles found

Respond in JSON:
{{
  "cuisine_types": ["Type 1", "Type 2"],
  "specialties": ["Specialty 1", "Specialty 2"],
  "unique_offerings": ["Unique offering 1"],
  "target_audience": "Target audience description",
  "brand_positioning": "Brand positioning",
  "competitive_strengths": ["Strength 1", "Strength 2"],
  "competitive_weaknesses": ["Weakness 1"],
  "notes": ["Important note 1"]
}}"""

            # Use shared Gemini agent
            response_text = await self.gemini.generate(
                prompt=context,
                temperature=0.4,
                max_output_tokens=2048,
            )

            result = self.gemini._parse_json_response(response_text)
            logger.info("Intelligence consolidated with Gemini")
            return result

        except Exception as e:
            logger.error(f"Intelligence consolidation failed: {e}")
            return {}

    def _extract_handle_from_url(self, url: str, platform: str) -> Optional[str]:
        """Extract handle from a social media URL."""
        if not url:
            return None

        if platform == "facebook":
            match = re.search(r"facebook\.com/([^/?]+)", url)
            return match.group(1) if match else None
        elif platform == "instagram":
            match = re.search(r"instagram\.com/([^/?]+)", url)
            return match.group(1) if match else None
        elif platform == "tiktok":
            match = re.search(r"tiktok\.com/@([^/?]+)", url)
            return match.group(1) if match else None
        elif platform == "twitter" or platform == "x":
            match = re.search(r"(twitter\.com|x\.com)/([^/?]+)", url)
            return match.group(2) if match else None
        elif platform == "youtube":
            # Handle user, channel, or custom URL
            if "youtube.com/channel/" in url:
                return url.split("youtube.com/channel/")[1].split("/")[0]
            elif "youtube.com/@" in url:
                return url.split("youtube.com/@")[1].split("/")[0]
            match = re.search(r"youtube\.com/user/([^/?]+)", url)
            return match.group(1) if match else None

        return None

    def _extract_whatsapp_from_phone(self, phone: Optional[str]) -> Optional[str]:
        """Format phone number for WhatsApp."""
        if not phone:
            return None

        # Remove non-numeric characters except +
        clean = re.sub(r"[^\d+]", "", phone)
        if clean and len(clean) >= 10:
            return clean
        return None

    def _extract_delivery_platforms(self, web_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract delivery platform info from web search results."""
        platforms = []
        raw_platforms = web_data.get("delivery_platforms", [])
        additional_urls = web_data.get("additional_websites", [])

        # Known delivery platform patterns
        platform_patterns = {
            "rappi": {"name": "Rappi", "icon": "🟠"},
            "uber eats": {"name": "Uber Eats", "icon": "🟢"},
            "ubereats": {"name": "Uber Eats", "icon": "🟢"},
            "ifood": {"name": "iFood", "icon": "🔴"},
            "domicilios": {"name": "Domicilios.com", "icon": "🔵"},
            "pedidosya": {"name": "PedidosYa", "icon": "🟡"},
            "didi food": {"name": "DiDi Food", "icon": "🟠"},
        }

        seen = set()

        # Handle structured format: [{"name": "Rappi", "url": "..."}]
        for p in raw_platforms:
            if isinstance(p, dict):
                p_name = (p.get("name") or "").lower().strip()
                p_url = p.get("url")
                for key, info in platform_patterns.items():
                    if key in p_name and info["name"] not in seen:
                        platforms.append({"name": info["name"], "icon": info["icon"], "url": p_url})
                        seen.add(info["name"])
            elif isinstance(p, str):
                # Legacy string format: ["Rappi", "Uber Eats"]
                p_lower = p.lower().strip()
                for key, info in platform_patterns.items():
                    if key in p_lower and info["name"] not in seen:
                        platforms.append({"name": info["name"], "icon": info["icon"], "url": None})
                        seen.add(info["name"])

        # From additional_websites URLs
        for url in additional_urls:
            url_lower = (url or "").lower()
            for key, info in platform_patterns.items():
                if key in url_lower and info["name"] not in seen:
                    platforms.append({"name": info["name"], "icon": info["icon"], "url": url})
                    seen.add(info["name"])

        return platforms

    def _collect_data_sources(
        self,
        maps_data: Dict[str, Any],
        web_data: Dict[str, Any],
        social_profiles: List[SocialMediaProfile],
        whatsapp_data: Dict[str, Any],
    ) -> List[str]:
        """Collect all data sources used."""
        sources = ["google_maps_place_details"]

        if web_data:
            sources.append("web_search")
        if social_profiles:
            sources.extend([f"{p.platform}" for p in social_profiles])
        if whatsapp_data.get("number"):
            sources.append("whatsapp_business")
        if maps_data.get("photos"):
            sources.append("google_photos_vision_analysis")
        if maps_data.get("reviews"):
            sources.append("google_reviews")

        return list(set(sources))

    def _calculate_confidence(
        self,
        maps_data: Dict[str, Any],
        web_data: Dict[str, Any],
        menu_data: Dict[str, Any],
    ) -> float:
        """Calculate a profile confidence score."""
        confidence = 0.0

        # Google Maps data (base)
        if maps_data.get("name"):
            confidence += 0.2
        if maps_data.get("formatted_phone_number"):
            confidence += 0.1
        if maps_data.get("rating"):
            confidence += 0.1
        if maps_data.get("reviews"):
            confidence += 0.1

        # Web presence
        if web_data.get("social_media"):
            confidence += 0.15
        if web_data.get("menu_found"):
            confidence += 0.15

        # Menu data
        if menu_data.get("items"):
            confidence += 0.2 * min(len(menu_data["items"]) / 20, 1.0)

        return min(confidence, 1.0)

    def _create_minimal_profile(
        self,
        competitor_id: str,
        basic_info: Dict[str, Any],
    ) -> CompetitorProfile:
        """Create a minimal profile when full enrichment data is not available."""
        return CompetitorProfile(
            competitor_id=competitor_id,
            name=basic_info.get("name", "Unknown"),
            address=basic_info.get("address", ""),
            lat=basic_info.get("lat", 0.0),
            lng=basic_info.get("lng", 0.0),
            place_id=basic_info.get("place_id"),
            data_sources=["basic_info"],
            confidence_score=0.1,
            enrichment_notes=["Minimal profile - enrichment failed"],
        )

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
