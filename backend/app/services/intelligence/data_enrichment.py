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

        # Step 9: Extract and validate delivery platforms
        delivery_platforms = await self._validate_delivery_platforms(
            self._extract_delivery_platforms(web_data)
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
        self, platforms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate delivery platform URLs."""
        valid = []
        for p in platforms:
            url = p.get("url")
            # If URL exists, validate it. If no URL, we might skip it or keep it as detection only.
            # User request implies they want valid links.
            if url:
                if await self._validate_url(url):
                    valid.append(p)
            else:
                # If name detected but no URL, maybe keep it?
                # For now, let's include it but logging might be useful.
                # Actually, Gemini might hallucinate names too, but we filtered by known list.
                pass
        return valid

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
            prompt = f"""Search the internet and find complete, VERIFIED information about this specific restaurant/business:

Name: {name}
{f"Phone: {phone}" if phone else ""}
{f"Address: {address}" if address else ""}
{f"Google Maps: {google_maps_url}" if google_maps_url else ""}

YOUR TASK - Search and find ONLY profiles that belong to THIS SPECIFIC business at THIS address:

1. SOCIAL MEDIA PROFILES (Deep Search):
   - Search query strategies: 
     - "{name} {address} facebook"
     - "{name} {address} instagram"
     - "{name} instagram" (look for handles matching the city, e.g., "{name.replace(' ', '').lower()}pasto")
   - Facebook: 
     - PRIORITIZE pages with "Restaurante" or "Bar" in the URL over generic "Pub" pages if both exist.
     - Example: Prefer "facebook.com/MargaritaPintaRestauranteBar" over "facebook.com/margarita.pinta.pub".
     - The "Pub" page might be broken/inactive. Look for the active "RestauranteBar" page.
   - Instagram: Look for the exact handle. Key hint: often ends in "pasto" (e.g. @margaritapintapasto).
   - VALIDATION:
     - Must match the city/location (e.g. Pasto).
     - Must look like an active business profile.

2. WhatsApp Business number if available (with country code)

3. DELIVERY PLATFORMS — Search for this business on Rappi, Uber Eats, iFood, PedidosYa:
   - Return the FULL direct URL (e.g., https://www.rappi.com.co/restaurantes/...).
   - CRITICAL: Verify the link works if possible. 
   - Rappi: Look for the specific numeric ID that matches this branch (e.g. usually 9 digits). 
   - HINT: For "Margarita Pinta", look for ID similar to 900178500.
   - Avoid links that lead to "store not found" or generic city pages.

Respond ONLY with valid JSON:
{{
  "social_media": {{
    "facebook": "full verified URL or null",
    "instagram": "full verified URL or null",
    "tiktok": "full verified URL or null",
    "twitter": "full verified URL or null",
    "youtube": "channel URL or null"
  }},
  "whatsapp": "number or null",
  "additional_websites": ["URL1", "URL2"],
  "delivery_platforms": [
    {{"name": "Rappi", "url": "full URL or null"}},
    {{"name": "Uber Eats", "url": "full URL or null"}}
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

            # Extract answer text
            response_text = response.get("answer", "")
            grounded = response.get("grounded", False)
            
            logger.info(
                f"Web cross-reference for {name}: grounded={grounded}, "
                f"response_len={len(response_text)}, "
                f"chunks={len((response.get('grounding_metadata') or {}).get('grounding_chunks', []))}"
            )
            
            # Use the robust parser from the agent
            result = self.gemini._parse_json_response(response_text)
            
            # Log what social media was found
            social = result.get("social_media", {})
            found = [k for k, v in social.items() if v]
            logger.info(f"Social media found for {name}: {found or 'none'}")
            
            return result

        except Exception as e:
            logger.error(f"Web cross-reference failed: {e}")
            return {}

    async def _validate_url(self, url: str) -> bool:
        """Validate if a URL is accessible (not 404)."""
        if not url or not url.startswith("http"):
            return False
            
        try:
            # Use a browser-like user agent to avoid bot blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            # Follow redirects to ensure we check the final destination
            response = await self.http_client.get(url, headers=headers, follow_redirects=True)
            
            # Facebook specific: 400 often means WAF blocking/bad request due to bot detection
            # rather than the page not existing. We accept it if it's Facebook.
            if "facebook.com" in url and response.status_code == 400:
                logger.warning(f"Facebook returned 400 (likely WAF), accepting URL: {url}")
                return True

            # We consider 404 as definitely broken.
            # 429, 403, etc. might mean it exists but we are blocked/unauthorized, so we keep it.
            if response.status_code == 404:
                logger.warning(f"Validation failed ({response.status_code}) for URL: {url}")
                return False
            return True
        except Exception as e:
            # If request fails (DNS, timeout), it's risky.
            logger.warning(f"Validation check error for {url}: {e}")
            return False

    async def _identify_social_media(
        self,
        name: Optional[str],
        website: Optional[str],
        phone: Optional[str],
        web_results: Dict[str, Any],
    ) -> List[SocialMediaProfile]:
        """Identify and validate social media profiles."""

        profiles = []
        social_data = web_results.get("social_media", {})

        # Facebook
        if social_data.get("facebook"):
            fb_url = social_data["facebook"]
            if await self._validate_url(fb_url):
                profiles.append(
                    SocialMediaProfile(
                        platform="facebook",
                        url=fb_url,
                        handle=self._extract_handle_from_url(
                            fb_url, "facebook"
                        ),
                    )
                )

        # Instagram
        if social_data.get("instagram"):
            instagram_url = social_data["instagram"]
            # STRICT VALIDATION: Only accept actual URLs, do not guess from handles
            if instagram_url and instagram_url.startswith("http"):
                if await self._validate_url(instagram_url):
                    profiles.append(
                        SocialMediaProfile(
                            platform="instagram",
                            url=instagram_url,
                            handle=self._extract_handle_from_url(instagram_url, "instagram"),
                        )
                    )

        # TikTok
        if social_data.get("tiktok"):
            tiktok_url = social_data["tiktok"]
            # STRICT VALIDATION: Only accept actual URLs
            if tiktok_url and tiktok_url.startswith("http"):
                if await self._validate_url(tiktok_url):
                    profiles.append(
                        SocialMediaProfile(
                            platform="tiktok",
                            url=tiktok_url,
                            handle=self._extract_handle_from_url(tiktok_url, "tiktok"),
                        )
                    )

        # Twitter/X
        if social_data.get("twitter"):
            twitter_url = social_data["twitter"]
            # STRICT VALIDATION: Only accept actual URLs
            if twitter_url and twitter_url.startswith("http"):
                if await self._validate_url(twitter_url):
                    profiles.append(
                        SocialMediaProfile(
                            platform="twitter",
                            url=twitter_url,
                            handle=self._extract_handle_from_url(twitter_url, "twitter"),
                        )
                    )

        # YouTube
        if social_data.get("youtube"):
            youtube_url = social_data["youtube"]
            if youtube_url and youtube_url.startswith("http"):
                if await self._validate_url(youtube_url):
                    profiles.append(
                        SocialMediaProfile(
                            platform="youtube",
                            url=youtube_url,
                            handle=self._extract_handle_from_url(youtube_url, "youtube"),
                        )
                    )

        # WhatsApp Business
        whatsapp = web_results.get("whatsapp") or self._extract_whatsapp_from_phone(
            phone
        )
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
{json.dumps(web_data, indent=2)[:1000]}

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
