"""
Competitor Intelligence Service.

Provides comprehensive competitive analysis capabilities:
- Web scraping competitor menus
- Menu extraction from images/URLs
- Price comparison analysis
- Strategic competitive insights
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import httpx
from loguru import logger

from app.services.gemini.multimodal_agent import MultimodalAgent
from app.services.gemini.reasoning_agent import ReasoningAgent, ThinkingLevel


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
    extracted_at: datetime = field(default_factory=datetime.utcnow)
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
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "our_restaurant": self.our_restaurant,
            "competitors_analyzed": self.competitors_analyzed,
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
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; MenuPilot/1.0; +https://menupilot.ai)"
            }
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
            f"Starting competitive analysis",
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
            f"Competitive analysis completed",
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
                if menu and menu.items:
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
            competitor_name=source.name or result.get("competitor_info", {}).get("name", "Unknown"),
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
        
        # Note: In production, this would use Instagram's API or a scraping service
        # For the hackathon, we'll return a placeholder that indicates the capability
        
        logger.info(f"Instagram extraction for {source.value} - requires API integration")
        
        return CompetitorMenu(
            competitor_name=source.name or source.value,
            items=[],
            categories=[],
            price_range={"min": 0, "max": 0},
            average_price=0,
            currency="MXN",
            source_type="instagram",
            extraction_confidence=0.0,
            metadata={
                "handle": source.value,
                "note": "Instagram API integration required for production",
            },
        )
    
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
        
        # Run analysis
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
            price_gaps.append(PriceGap(
                item_category=gap_data.get("item_category", ""),
                our_item=gap_data.get("our_item"),
                our_price=gap_data.get("our_price", 0),
                competitor_name=gap_data.get("competitor_name", ""),
                competitor_item=gap_data.get("competitor_item"),
                competitor_price=gap_data.get("competitor_price", 0),
                price_difference=gap_data.get("price_difference", 0),
                price_difference_percent=gap_data.get("price_difference_percent", 0),
                recommendation=gap_data.get("recommendation", ""),
                confidence=gap_data.get("confidence", 0.7),
            ))
        
        landscape = analysis.get("competitive_landscape", {})
        price_analysis = analysis.get("price_analysis", {})
        product_analysis = analysis.get("product_analysis", {})
        
        return CompetitiveAnalysisResult(
            analysis_id=analysis_id,
            our_restaurant=our_restaurant,
            competitors_analyzed=[m.competitor_name for m in competitor_menus],
            
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
            gemini_tokens_used=self.reasoning.stats.total_tokens.total_tokens,
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
            price_gaps.append(PriceGap(
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
            ))
        
        return price_gaps
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()
