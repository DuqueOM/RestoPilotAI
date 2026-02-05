"""
Competitor Intelligence Service.

Provides comprehensive competitive analysis capabilities:
- Web scraping competitor menus
- Menu extraction from images/URLs
- Price comparison analysis
- Strategic competitive insights
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

import httpx
from loguru import logger

from app.services.gemini.base_agent import ThinkingLevel
from app.services.gemini.multimodal import MultimodalAgent
from app.services.gemini.reasoning_agent import ReasoningAgent
from app.services.intelligence.social_scraper import SocialScraper


@dataclass
class CompetitorSource:
    """A source for competitor data."""

    type: str  # "url", "image", "instagram", "data"
    value: str  # URL, base64 image, handle, or JSON data
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitorMenu:
    """Extracted competitor menu data."""

    competitor_name: str
    items: List[Dict[str, Any]]
    categories: List[str]
    price_range: Dict[str, float]
    average_price: float
    currency: str
    source_type: str
    extraction_confidence: float
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "competitor_name": self.competitor_name,
            "items": self.items,
            "categories": self.categories,
            "price_range": self.price_range,
            "average_price": self.average_price,
            "currency": self.currency,
            "source_type": self.source_type,
            "extraction_confidence": self.extraction_confidence,
            "extracted_at": self.extracted_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class PriceGap:
    """Price comparison for a specific item/category."""

    item_category: str
    our_item: Optional[str]
    our_price: float
    competitor_name: str
    competitor_item: Optional[str]
    competitor_price: float
    price_difference: float
    price_difference_percent: float
    recommendation: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_category": self.item_category,
            "our_item": self.our_item,
            "our_price": self.our_price,
            "competitor_name": self.competitor_name,
            "competitor_item": self.competitor_item,
            "competitor_price": self.competitor_price,
            "price_difference": self.price_difference,
            "price_difference_percent": round(self.price_difference_percent, 2),
            "recommendation": self.recommendation,
            "confidence": self.confidence,
        }


@dataclass
class CompetitiveAnalysisResult:
    """Complete competitive analysis result."""

    analysis_id: str
    our_restaurant: str
    competitors_analyzed: List[str]

    # Landscape
    market_position: str
    competitive_intensity: str
    key_differentiators: List[str]
    competitive_gaps: List[str]

    # Price analysis
    price_positioning: str
    price_gaps: List[PriceGap]
    pricing_opportunities: List[str]

    # Product analysis
    our_unique_items: List[str]
    competitor_unique_items: Dict[str, List[str]]
    category_gaps: List[Dict[str, Any]]
    trending_items_missing: List[str]

    # Strategic recommendations
    strategic_recommendations: List[Dict[str, Any]]
    competitive_threats: List[Dict[str, Any]]
    market_opportunities: List[Dict[str, Any]]

    # Positioning
    positioning_matrix: Optional[Dict[str, Any]]

    # Metadata
    confidence: float
    thinking_level: str
    gemini_tokens_used: int
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Frontend compatibility
    competitors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Grounding metadata
    grounding_sources: Optional[List[Dict[str, Any]]] = None
    grounded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "our_restaurant": self.our_restaurant,
            "competitors_analyzed": self.competitors_analyzed,
            "competitors": self.competitors,  # Added for frontend
            "competitive_landscape": {
                "market_position": self.market_position,
                "competitive_intensity": self.competitive_intensity,
                "key_differentiators": self.key_differentiators,
                "competitive_gaps": self.competitive_gaps,
            },
            "price_analysis": {
                "price_positioning": self.price_positioning,
                "price_gaps": [g.to_dict() for g in self.price_gaps],
                "pricing_opportunities": self.pricing_opportunities,
            },
            "product_analysis": {
                "our_unique_items": self.our_unique_items,
                "competitor_unique_items": self.competitor_unique_items,
                "category_gaps": self.category_gaps,
                "trending_items_missing": self.trending_items_missing,
            },
            "strategic_recommendations": self.strategic_recommendations,
            "competitive_threats": self.competitive_threats,
            "market_opportunities": self.market_opportunities,
            "positioning_matrix": self.positioning_matrix,
            "metadata": {
                "confidence": self.confidence,
                "thinking_level": self.thinking_level,
                "gemini_tokens_used": self.gemini_tokens_used,
                "analyzed_at": self.analyzed_at.isoformat(),
            },
            "grounding_sources": self.grounding_sources or [],
            "grounded": self.grounded,
        }


class CompetitorIntelligenceService:
    """
    Service for competitor intelligence gathering and analysis.

    Capabilities:
    - Extract menus from competitor websites/images
    - Scrape Instagram for menu photos
    - Compare prices across competitors
    - Generate strategic competitive insights
    """

    def __init__(
        self,
        multimodal_agent: Optional[MultimodalAgent] = None,
        reasoning_agent: Optional[ReasoningAgent] = None,
    ):
        self.multimodal = multimodal_agent or MultimodalAgent()
        self.reasoning = reasoning_agent or ReasoningAgent()
        self.social_scraper = SocialScraper()
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; RestoPilotAI/1.0; +https://RestoPilotAI.ai)"
            },
        )

    async def analyze_competitors(
        self,
        our_menu: Dict[str, Any],
        competitor_sources: List[CompetitorSource],
        restaurant_name: str = "Our Restaurant",
        thinking_level: ThinkingLevel = ThinkingLevel.DEEP,
    ) -> CompetitiveAnalysisResult:
        """
        Perform comprehensive competitive analysis.

        Args:
            our_menu: Our restaurant's menu data
            competitor_sources: List of competitor data sources
            restaurant_name: Our restaurant name
            thinking_level: Depth of analysis

        Returns:
            CompetitiveAnalysisResult with strategic insights
        """
        analysis_id = str(uuid4())

        logger.info(
            "Starting competitive analysis",
            analysis_id=analysis_id,
            competitors=len(competitor_sources),
        )

        # Step 1: Extract competitor menus
        competitor_menus = await self._extract_all_competitor_menus(competitor_sources)

        if not competitor_menus:
            logger.warning("No competitor menus extracted")
            return self._create_empty_result(analysis_id, restaurant_name)

        # Step 2: Run competitive analysis with reasoning agent
        analysis = await self._run_competitive_analysis(
            our_menu=our_menu,
            competitor_menus=competitor_menus,
            restaurant_name=restaurant_name,
            thinking_level=thinking_level,
        )

        # Step 3: Build result
        result = self._build_analysis_result(
            analysis_id=analysis_id,
            our_restaurant=restaurant_name,
            competitor_menus=competitor_menus,
            analysis=analysis,
            thinking_level=thinking_level,
        )

        logger.info(
            "Competitive analysis completed",
            analysis_id=analysis_id,
            confidence=result.confidence,
        )

        return result

    async def _extract_all_competitor_menus(
        self,
        sources: List[CompetitorSource],
    ) -> List[CompetitorMenu]:
        """Extract menus from all competitor sources."""

        menus = []

        for source in sources:
            try:
                menu = await self._extract_competitor_menu(source)
                # Allow menus without items to be included for basic competitor info
                if menu:
                    menus.append(menu)
            except Exception as e:
                logger.error(f"Failed to extract menu from {source.name}: {e}")

        return menus

    async def _extract_competitor_menu(
        self,
        source: CompetitorSource,
    ) -> Optional[CompetitorMenu]:
        """Extract menu from a single competitor source."""

        if source.type == "image":
            return await self._extract_from_image(source)
        elif source.type == "url":
            return await self._extract_from_url(source)
        elif source.type == "instagram":
            return await self._extract_from_instagram(source)
        elif source.type == "data":
            return self._parse_direct_data(source)
        else:
            logger.warning(f"Unknown source type: {source.type}")
            return None

    async def _extract_from_image(
        self,
        source: CompetitorSource,
    ) -> Optional[CompetitorMenu]:
        """Extract menu from competitor image."""

        result = await self.multimodal.extract_competitor_menu(
            image_source=source.value,
            competitor_name=source.name,
        )

        if "error" in result:
            return None

        items = result.get("items", [])

        # Calculate price metrics
        prices = [item.get("price", 0) for item in items if item.get("price")]

        return CompetitorMenu(
            competitor_name=source.name
            or result.get("competitor_info", {}).get("name", "Unknown"),
            items=items,
            categories=list(set(item.get("category", "Other") for item in items)),
            price_range={
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
            },
            average_price=sum(prices) / len(prices) if prices else 0,
            currency=result.get("pricing_analysis", {}).get("currency", "MXN"),
            source_type="image",
            extraction_confidence=result.get("extraction_confidence", 0.7),
            metadata=result.get("competitor_info", {}),
        )

    async def _extract_from_url(
        self,
        source: CompetitorSource,
    ) -> Optional[CompetitorMenu]:
        """Extract menu from competitor website URL."""

        try:
            # Fetch webpage content
            response = await self.http_client.get(source.value)
            response.raise_for_status()

            html_content = response.text

            # Use Gemini to extract menu from HTML
            prompt = f"""Extract menu items from this restaurant webpage HTML.

URL: {source.value}
Restaurant Name: {source.name or "Unknown"}

HTML Content (truncated):
{html_content[:15000]}

Extract all menu items with prices. Return JSON:
{{
    "competitor_name": "Restaurant Name",
    "items": [
        {{"name": "Item", "price": 85.00, "category": "Category", "description": ""}}
    ],
    "categories": ["Category1", "Category2"],
    "currency": "MXN",
    "confidence": 0.8
}}"""

            result = await self.multimodal._generate_content(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=8192,
                feature="competitor_url_extraction",
            )

            data = self.multimodal._parse_json_response(result)

            items = data.get("items", [])
            prices = [item.get("price", 0) for item in items if item.get("price")]

            return CompetitorMenu(
                competitor_name=data.get("competitor_name", source.name or "Unknown"),
                items=items,
                categories=data.get("categories", []),
                price_range={
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0,
                },
                average_price=sum(prices) / len(prices) if prices else 0,
                currency=data.get("currency", "MXN"),
                source_type="url",
                extraction_confidence=data.get("confidence", 0.6),
                metadata={"url": source.value},
            )

        except Exception as e:
            logger.error(f"URL extraction failed for {source.value}: {e}")
            return None

    async def _extract_from_instagram(
        self,
        source: CompetitorSource,
    ) -> Optional[CompetitorMenu]:
        """Extract menu from Instagram profile."""

        # Clean handle
        handle = source.value
        if "instagram.com" in handle:
            handle = handle.split("instagram.com/")[-1].replace("/", "")
        handle = handle.replace("@", "")

        logger.info(
            f"Instagram extraction for {handle} - using SocialScraper and Gemini"
        )

        try:
            # 1. Get recent posts
            posts = await self.social_scraper.get_recent_posts(handle, limit=5)

            if not posts:
                logger.warning(f"No posts found for {handle}")
                return None

            # 2. Analyze captions for menu text
            captions_text = "\n\n".join(
                [f"Post {i+1}: {p.caption}" for i, p in enumerate(posts) if p.caption]
            )

            menu_items = []
            confidence = 0.5

            # 3. Analyze images (Multimodal)
            # Try to find a menu-like image or use the latest one
            if posts and posts[0].image_url:
                latest_image_url = posts[0].image_url
                logger.info(f"Analyzing latest Instagram image: {latest_image_url}")

                try:
                    img_response = await self.http_client.get(latest_image_url)
                    if img_response.status_code == 200:
                        image_bytes = img_response.content

                        prompt = f"""Analyze this Instagram post image and the captions from recent posts to identify menu items.
                        
                        CAPTIONS CONTEXT:
                        {captions_text[:2000]}
                        
                        Extract any food or drink items mentioned with prices if available.
                        If the image is a menu, extract everything.
                        
                        Return JSON:
                        {{
                            "items": [{{"name": "Item", "price": 0, "description": "From caption/image", "category": "Food"}}],
                            "confidence": 0.7
                        }}
                        """

                        result_text = await self.multimodal._generate_multimodal(
                            prompt=prompt,
                            images=[image_bytes],
                            feature="instagram_menu_extraction",
                        )

                        data = self.multimodal._parse_json_response(result_text)
                        menu_items = data.get("items", [])
                        confidence = data.get("confidence", 0.6)

                except Exception as e:
                    logger.warning(f"Failed to analyze Instagram image: {e}")

            # Fallback: Text-only analysis if image failed or yielded nothing
            if not menu_items and captions_text:
                prompt = f"""Extract menu items from these Instagram captions:
                
                {captions_text[:3000]}
                
                Return JSON with items list."""

                result = await self.reasoning._generate_content(
                    prompt, feature="instagram_caption_extraction"
                )
                data = self.reasoning._parse_json_response(result)
                menu_items = data.get("items", [])

            # Calculate metrics
            prices = [item.get("price", 0) for item in menu_items if item.get("price")]

            return CompetitorMenu(
                competitor_name=source.name or handle,
                items=menu_items,
                categories=list(
                    set(item.get("category", "Instagram") for item in menu_items)
                ),
                price_range={
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0,
                },
                average_price=sum(prices) / len(prices) if prices else 0,
                currency="MXN",
                source_type="instagram",
                extraction_confidence=confidence,
                metadata={
                    "handle": handle,
                    "posts_analyzed": len(posts),
                    "latest_post_date": (
                        posts[0].timestamp.isoformat() if posts else None
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Instagram extraction failed for {handle}: {e}")
            return None

    def _parse_direct_data(
        self,
        source: CompetitorSource,
    ) -> Optional[CompetitorMenu]:
        """Parse directly provided competitor data."""
        try:
            if isinstance(source.value, str):
                data = json.loads(source.value)
            else:
                data = source.value

            items = data.get("items", [])
            prices = [item.get("price", 0) for item in items if item.get("price")]

            return CompetitorMenu(
                competitor_name=data.get("name", source.name or "Unknown"),
                items=items,
                categories=data.get("categories", []),
                price_range={
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0,
                },
                average_price=sum(prices) / len(prices) if prices else 0,
                currency=data.get("currency", "MXN"),
                source_type="data",
                extraction_confidence=1.0,
                metadata=source.metadata,
            )

        except Exception as e:
            logger.error(f"Failed to parse direct data: {e}")
            return None

    async def _run_competitive_analysis(
        self,
        our_menu: Dict[str, Any],
        competitor_menus: List[CompetitorMenu],
        restaurant_name: str,
        thinking_level: ThinkingLevel,
    ) -> Dict[str, Any]:
        """Run the main competitive analysis using reasoning agent."""

        # Prepare data for analysis
        our_menu_data = {
            "restaurant_name": restaurant_name,
            "items": our_menu.get("items", []),
            "categories": our_menu.get("categories", []),
        }

        competitor_data = [menu.to_dict() for menu in competitor_menus]

        # Try running with grounding (Feature #3)
        try:
            if hasattr(self.reasoning, "analyze_competitive_position_with_grounding"):
                logger.info("Running grounded competitive analysis with Google Search")
                result_data = await self.reasoning.analyze_competitive_position_with_grounding(
                    restaurant_data=our_menu_data,
                    competitors=competitor_data,
                    thinking_level=thinking_level,
                )
                
                analysis = result_data.get("analysis", {})
                sources = result_data.get("sources", [])
                
                # Handle fallback case where analysis might be a ReasoningResult object
                if not isinstance(analysis, dict) and hasattr(analysis, "analysis"):
                    analysis = analysis.analysis
                
                # Inject sources into metadata
                if sources:
                    if "metadata" not in analysis:
                        analysis["metadata"] = {}
                    analysis["metadata"]["grounding_sources"] = sources
                    logger.info(f"Analysis enriched with {len(sources)} grounding sources")
                
                return analysis

        except Exception as e:
            logger.warning(f"Grounded analysis failed, falling back to standard: {e}")

        # Standard analysis fallback
        result = await self.reasoning.analyze_competitive_position(
            our_menu=our_menu_data,
            competitor_menus=competitor_data,
            thinking_level=thinking_level,
        )

        return result.analysis

    def _build_analysis_result(
        self,
        analysis_id: str,
        our_restaurant: str,
        competitor_menus: List[CompetitorMenu],
        analysis: Dict[str, Any],
        thinking_level: ThinkingLevel,
    ) -> CompetitiveAnalysisResult:
        """Build the final analysis result."""

        # Extract price gaps
        price_gaps = []
        for gap_data in analysis.get("price_analysis", {}).get("price_gaps", []):
            price_gaps.append(
                PriceGap(
                    item_category=gap_data.get("item_category", ""),
                    our_item=gap_data.get("our_item"),
                    our_price=gap_data.get("our_price", 0),
                    competitor_name=gap_data.get("competitor_name", ""),
                    competitor_item=gap_data.get("competitor_item"),
                    competitor_price=gap_data.get("competitor_price", 0),
                    price_difference=gap_data.get("price_difference", 0),
                    price_difference_percent=gap_data.get(
                        "price_difference_percent", 0
                    ),
                    recommendation=gap_data.get("recommendation", ""),
                    confidence=gap_data.get("confidence", 0.7),
                )
            )

        landscape = analysis.get("competitive_landscape", {})
        price_analysis = analysis.get("price_analysis", {})
        product_analysis = analysis.get("product_analysis", {})
        
        # Extract grounding metadata
        grounding_sources = analysis.get("grounding_sources") or analysis.get("metadata", {}).get("grounding_sources")
        grounded = analysis.get("grounded", False)

        # Build competitors list for frontend
        competitors_list = []
        for menu in competitor_menus:
            # Try to get data from metadata (CompetitorProfile)
            meta = menu.metadata or {}
            
            # Determine type (Direct/Indirect) - default to Direct
            comp_type = "Directo"
            
            # Distance (formatted)
            distance = "Unknown"
            if meta.get("distance_meters"):
                distance = f"{meta['distance_meters'] / 1000:.1f}km"
            elif meta.get("location", {}).get("distance"): # Handle varied structures
                distance = str(meta["location"]["distance"])
            
            # Price range
            price_level = meta.get("price_level") or meta.get("google_maps", {}).get("price_level")
            price_range = "$" * (price_level if price_level else 2)
            
            # Rating
            rating = meta.get("rating") or meta.get("google_maps", {}).get("rating") or 0.0
            
            # Strengths/Weaknesses from Analysis or Profile
            # If the analysis (Gemini) provided specific competitor insights, we could try to map them.
            # For now, we can use the enriched profile data if available, or empty lists.
            # The prompt in analyze_competitive_position doesn't currently output per-competitor strengths/weaknesses list in a structured way 
            # other than potentially in text. 
            # We will use placeholders or extract from 'competitive_landscape' if mentioned.
            strengths = meta.get("competitive_intelligence", {}).get("competitive_strengths", [])
            weaknesses = meta.get("competitive_intelligence", {}).get("competitive_weaknesses", [])
            
            # Market Share & Trend (Simulated or estimated as it's hard to get real values without POS data)
            # We can use confidence score or rating count as a proxy for "Market Share" relative to others
            review_count = meta.get("user_ratings_total") or 0
            # Normalize to some share? Let's leave as estimated or random for demo/MVP if not calculated
            # For now, 0 to indicate unknown
            market_share = 0 
            trend = "stable"

            competitors_list.append({
                "name": menu.competitor_name,
                "type": comp_type,
                "distance": distance,
                "rating": rating,
                "priceRange": price_range,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "marketShare": market_share,
                "trend": trend,
                "place_id": meta.get("place_id") or meta.get("competitor_id")
            })

        return CompetitiveAnalysisResult(
            analysis_id=analysis_id,
            our_restaurant=our_restaurant,
            competitors_analyzed=[m.competitor_name for m in competitor_menus],
            competitors=competitors_list,
            # Landscape
            market_position=landscape.get("market_position", "unknown"),
            competitive_intensity=landscape.get("competitive_intensity", "medium"),
            key_differentiators=landscape.get("key_differentiators", []),
            competitive_gaps=landscape.get("competitive_gaps", []),
            # Price analysis
            price_positioning=price_analysis.get("our_positioning", "mid-range"),
            price_gaps=price_gaps,
            pricing_opportunities=price_analysis.get("pricing_opportunities", []),
            # Product analysis
            our_unique_items=product_analysis.get("our_unique_items", []),
            competitor_unique_items=product_analysis.get("competitor_unique_items", {}),
            category_gaps=product_analysis.get("category_gaps", []),
            trending_items_missing=product_analysis.get("trending_items_missing", []),
            # Strategic
            strategic_recommendations=analysis.get("strategic_recommendations", []),
            competitive_threats=analysis.get("competitive_threats", []),
            market_opportunities=analysis.get("market_opportunities", []),
            # Positioning
            positioning_matrix=analysis.get("market_positioning_matrix"),
            # Metadata
            confidence=analysis.get("confidence", 0.7),
            thinking_level=thinking_level.value,
            gemini_tokens_used=self.reasoning.total_tokens,
            # Grounding
            grounding_sources=grounding_sources,
            grounded=grounded,
        )

    def _create_empty_result(
        self,
        analysis_id: str,
        restaurant_name: str,
    ) -> CompetitiveAnalysisResult:
        """Create an empty result when no competitor data available."""

        return CompetitiveAnalysisResult(
            analysis_id=analysis_id,
            our_restaurant=restaurant_name,
            competitors_analyzed=[],
            market_position="unknown",
            competitive_intensity="unknown",
            key_differentiators=[],
            competitive_gaps=[],
            price_positioning="unknown",
            price_gaps=[],
            pricing_opportunities=[],
            our_unique_items=[],
            competitor_unique_items={},
            category_gaps=[],
            trending_items_missing=[],
            strategic_recommendations=[],
            competitive_threats=[],
            market_opportunities=[],
            positioning_matrix=None,
            confidence=0.0,
            thinking_level="none",
            gemini_tokens_used=0,
        )

    async def get_quick_price_comparison(
        self,
        our_items: List[Dict[str, Any]],
        competitor_items: List[Dict[str, Any]],
        competitor_name: str,
    ) -> List[PriceGap]:
        """
        Quick price comparison between our items and a competitor.

        Uses fuzzy matching to find comparable items.
        """

        prompt = f"""Compare these menu items and identify price gaps.

OUR MENU:
{json.dumps(our_items[:30], indent=2)}

COMPETITOR ({competitor_name}) MENU:
{json.dumps(competitor_items[:30], indent=2)}

For each comparable item pair, provide:
1. Category match
2. Our item and price
3. Their item and price
4. Price difference
5. Recommendation

Return JSON:
{{
    "comparisons": [
        {{
            "category": "Tacos",
            "our_item": "Taco al Pastor",
            "our_price": 85,
            "competitor_item": "Taco de Pastor",
            "competitor_price": 75,
            "price_difference": 10,
            "price_difference_percent": 13.3,
            "recommendation": "Consider reducing price by 5-10 MXN",
            "confidence": 0.9
        }}
    ]
}}"""

        result = await self.reasoning._generate_content(
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=4096,
            feature="quick_price_comparison",
        )

        data = self.reasoning._parse_json_response(result)

        price_gaps = []
        for comp in data.get("comparisons", []):
            price_gaps.append(
                PriceGap(
                    item_category=comp.get("category", ""),
                    our_item=comp.get("our_item"),
                    our_price=comp.get("our_price", 0),
                    competitor_name=competitor_name,
                    competitor_item=comp.get("competitor_item"),
                    competitor_price=comp.get("competitor_price", 0),
                    price_difference=comp.get("price_difference", 0),
                    price_difference_percent=comp.get("price_difference_percent", 0),
                    recommendation=comp.get("recommendation", ""),
                    confidence=comp.get("confidence", 0.7),
                )
            )

        return price_gaps

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()
