"""
Grounded Intelligence Service - Google Search Integration.

This module provides competitive intelligence and market research
capabilities using Gemini 3's unique Google Search grounding feature.

UNIQUE TO GEMINI 3: Auto-citation of sources from Google Search.
OpenAI/Claude cannot match this level of integration.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field, HttpUrl

from app.services.gemini.enhanced_agent import (
    EnhancedGeminiAgent,
    ThinkingLevel
)
from app.core.config import GeminiModel


# ==================== Models ====================

class SourceType(str, Enum):
    """Types of grounding sources."""
    WEB_PAGE = "web_page"
    REVIEW_SITE = "review_site"
    SOCIAL_MEDIA = "social_media"
    NEWS_ARTICLE = "news_article"
    BUSINESS_LISTING = "business_listing"
    MENU_SITE = "menu_site"
    UNKNOWN = "unknown"


class GroundingSource(BaseModel):
    """A single grounding source with metadata."""
    url: str
    title: str
    snippet: Optional[str] = None
    source_type: SourceType = SourceType.UNKNOWN
    accessed_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    relevance_score: Optional[float] = None


class GroundedResult(BaseModel):
    """Result with grounding metadata."""
    data: Dict[str, Any]
    sources: List[GroundingSource] = Field(default_factory=list)
    grounding_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    grounded: bool = True
    query_used: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CompetitorIntelligence(BaseModel):
    """Competitive intelligence with sources."""
    competitor_name: str
    location: str
    avg_price: Optional[float] = None
    price_range: Optional[Dict[str, float]] = None
    recent_changes: List[str] = Field(default_factory=list)
    menu_highlights: List[str] = Field(default_factory=list)
    customer_sentiment: str = "neutral"
    sentiment_score: Optional[float] = None
    social_presence: Dict[str, str] = Field(default_factory=dict)
    recent_promotions: List[str] = Field(default_factory=list)
    sources: List[GroundingSource] = Field(default_factory=list)
    grounding_score: float = 0.0
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MarketTrend(BaseModel):
    """Market trend with grounded sources."""
    trend_name: str
    description: str
    growth_rate: Optional[float] = None
    time_period: str
    relevant_to_restaurant: bool = True
    actionable_insights: List[str] = Field(default_factory=list)
    sources: List[GroundingSource] = Field(default_factory=list)
    confidence: float = 0.0


# ==================== Grounded Intelligence Service ====================

class GroundedIntelligenceService(EnhancedGeminiAgent):
    """
    🔍 GROUNDED INTELLIGENCE SERVICE
    
    Leverages Gemini 3's unique Google Search grounding capability
    to provide competitive intelligence with automatic source citations.
    
    UNIQUE ADVANTAGE: Only Gemini 3 has this level of Google Search integration.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            model=GeminiModel.FLASH_PREVIEW,
            enable_grounding=True,  # Always enabled for this service
            enable_cache=True,
            **kwargs
        )
        logger.info("grounded_intelligence_service_initialized")
    
    # ==================== COMPETITIVE INTELLIGENCE ====================
    
    async def analyze_competitor_with_grounding(
        self,
        competitor_name: str,
        location: str,
        cuisine_type: Optional[str] = None
    ) -> CompetitorIntelligence:
        """
        🎯 Analyze competitor with real-time web research.
        
        Uses Google Search grounding to find:
        - Current menu prices
        - Recent reviews
        - Social media presence
        - Recent promotions
        - Customer sentiment
        
        ALL SOURCES ARE AUTOMATICALLY CITED.
        """
        
        cuisine_context = f" (specializing in {cuisine_type})" if cuisine_type else ""
        
        prompt = f"""Research this restaurant: **{competitor_name}** in {location}{cuisine_context}

You are a competitive intelligence analyst. Find the LATEST information from the web.

RESEARCH TASKS:

1. **Current Menu Prices** (most recent):
   - Average price per dish
   - Price range (min to max)
   - Any recent price changes

2. **Recent Reviews** (last 30-60 days):
   - Overall sentiment (positive/neutral/negative)
   - Common themes in reviews
   - Rating trends

3. **Social Media Presence**:
   - Instagram handle and follower count
   - Facebook page
   - TikTok presence
   - Recent posts/engagement

4. **Recent Promotions or Changes**:
   - New menu items
   - Special offers
   - Events or campaigns
   - Any major changes

5. **Customer Sentiment Trends**:
   - What customers love
   - Common complaints
   - Trending topics

6. **Menu Highlights**:
   - Signature dishes
   - Popular items
   - Unique offerings

IMPORTANT:
- Use ONLY current, verifiable information from the web
- Cite specific sources for each claim
- If information is not available, say so explicitly
- Focus on data from the last 3-6 months

RETURN AS JSON:
{{
    "competitor_name": "{competitor_name}",
    "location": "{location}",
    "avg_price": float or null,
    "price_range": {{"min": float, "max": float}} or null,
    "recent_changes": ["change 1", "change 2"],
    "menu_highlights": ["dish 1", "dish 2"],
    "customer_sentiment": "positive|neutral|negative",
    "sentiment_score": float (0-1) or null,
    "social_presence": {{
        "instagram": "handle or url",
        "facebook": "url",
        "tiktok": "handle or url"
    }},
    "recent_promotions": ["promo 1", "promo 2"]
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=True,
            enable_thought_trace=True
        )
        
        # Extract grounding sources
        sources = self._extract_grounding_sources(result)
        
        # Parse competitor data
        competitor_data = result["data"]
        competitor_data["sources"] = sources
        competitor_data["grounding_score"] = result.get("grounding_score", 0.0)
        
        try:
            return CompetitorIntelligence(**competitor_data)
        except Exception as e:
            logger.error("competitor_intelligence_parse_error", error=str(e))
            # Return minimal valid data
            return CompetitorIntelligence(
                competitor_name=competitor_name,
                location=location,
                sources=sources,
                grounding_score=result.get("grounding_score", 0.0)
            )
    
    async def research_market_trends(
        self,
        cuisine_type: str,
        location: str,
        time_period: str = "last 6 months"
    ) -> List[MarketTrend]:
        """
        📈 Research market trends with grounded sources.
        
        Finds trending topics, ingredients, dishes, and concepts
        in the specified market.
        """
        
        prompt = f"""Research current market trends for {cuisine_type} restaurants in {location}.

Time period: {time_period}

FIND TRENDING:

1. **Dish Trends**:
   - What dishes are gaining popularity?
   - New fusion concepts
   - Viral menu items

2. **Ingredient Trends**:
   - Trending ingredients
   - Seasonal focuses
   - Sustainable/local sourcing trends

3. **Pricing Trends**:
   - Average price changes
   - Value positioning trends
   - Premium vs budget trends

4. **Experience Trends**:
   - Dining format trends (fast casual, etc.)
   - Technology adoption (QR menus, apps)
   - Ambiance preferences

5. **Marketing Trends**:
   - Social media strategies
   - Influencer partnerships
   - Loyalty programs

For EACH trend, provide:
- Clear description
- Growth indicators (if available)
- Why it's relevant to restaurants
- Actionable insights

RETURN AS JSON ARRAY:
[
    {{
        "trend_name": "string",
        "description": "string",
        "growth_rate": float or null,
        "time_period": "{time_period}",
        "relevant_to_restaurant": bool,
        "actionable_insights": ["insight 1", "insight 2"]
    }}
]
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=True
        )
        
        # Extract sources
        sources = self._extract_grounding_sources(result)
        
        # Parse trends
        trends_data = result["data"] if isinstance(result["data"], list) else result["data"].get("trends", [])
        
        trends = []
        for trend_data in trends_data:
            trend_data["sources"] = sources
            trend_data["confidence"] = result.get("grounding_score", 0.0)
            try:
                trends.append(MarketTrend(**trend_data))
            except Exception as e:
                logger.error("market_trend_parse_error", error=str(e), trend=trend_data)
        
        return trends
    
    async def verify_claim_with_grounding(
        self,
        claim: str,
        context: Optional[str] = None
    ) -> GroundedResult:
        """
        ✅ Verify a claim using Google Search grounding.
        
        Useful for fact-checking competitor claims, market data, etc.
        """
        
        context_str = f"\n\nContext: {context}" if context else ""
        
        prompt = f"""Verify this claim using current web sources:

CLAIM: "{claim}"{context_str}

VERIFICATION TASKS:
1. Search for evidence supporting or refuting the claim
2. Find multiple independent sources
3. Assess credibility of sources
4. Provide verdict: TRUE, FALSE, PARTIALLY TRUE, or UNVERIFIABLE

RETURN AS JSON:
{{
    "claim": "{claim}",
    "verdict": "TRUE|FALSE|PARTIALLY_TRUE|UNVERIFIABLE",
    "confidence": float (0-1),
    "evidence_for": ["evidence 1", "evidence 2"],
    "evidence_against": ["evidence 1", "evidence 2"],
    "explanation": "string",
    "credibility_assessment": "string"
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=True
        )
        
        sources = self._extract_grounding_sources(result)
        
        return GroundedResult(
            data=result["data"],
            sources=sources,
            grounding_score=result.get("grounding_score", 0.0),
            confidence=result["data"].get("confidence", 0.0),
            query_used=claim
        )
    
    async def find_pricing_benchmarks(
        self,
        cuisine_type: str,
        location: str,
        dish_category: Optional[str] = None
    ) -> GroundedResult:
        """
        💰 Find pricing benchmarks from real competitors.
        
        Uses grounding to find actual current prices from menus.
        """
        
        category_str = f" for {dish_category}" if dish_category else ""
        
        prompt = f"""Find current pricing benchmarks for {cuisine_type} restaurants in {location}{category_str}.

RESEARCH:
1. Find 5-10 comparable restaurants
2. Extract current menu prices
3. Calculate statistics:
   - Average price
   - Median price
   - Price range (min to max)
   - Standard deviation (if possible)

4. Identify pricing tiers:
   - Budget tier (bottom 25%)
   - Mid-range tier (25-75%)
   - Premium tier (top 25%)

5. Note any pricing patterns:
   - Common price points
   - Pricing strategies observed
   - Value propositions

RETURN AS JSON:
{{
    "cuisine_type": "{cuisine_type}",
    "location": "{location}",
    "dish_category": "{dish_category or 'general'}",
    "sample_size": int,
    "average_price": float,
    "median_price": float,
    "price_range": {{"min": float, "max": float}},
    "pricing_tiers": {{
        "budget": {{"min": float, "max": float}},
        "mid_range": {{"min": float, "max": float}},
        "premium": {{"min": float, "max": float}}
    }},
    "common_price_points": [float],
    "insights": ["insight 1", "insight 2"]
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=True
        )
        
        sources = self._extract_grounding_sources(result)
        
        return GroundedResult(
            data=result["data"],
            sources=sources,
            grounding_score=result.get("grounding_score", 0.0),
            confidence=result.get("confidence", 0.0),
            query_used=f"Pricing benchmarks for {cuisine_type} in {location}"
        )
    
    # ==================== SOURCE EXTRACTION ====================
    
    def _extract_grounding_sources(
        self,
        result: Dict[str, Any]
    ) -> List[GroundingSource]:
        """
        Extract grounding sources from Gemini API response.
        
        Gemini 3 provides grounding metadata in the response.
        """
        
        sources = []
        
        # Extract from thought trace
        thought_trace = result.get("thought_trace", {})
        data_sources = thought_trace.get("data_sources", [])
        
        for source in data_sources:
            if isinstance(source, str):
                # Simple URL string
                sources.append(GroundingSource(
                    url=source,
                    title=self._extract_domain(source),
                    source_type=self._classify_source_type(source)
                ))
            elif isinstance(source, dict):
                # Structured source data
                sources.append(GroundingSource(
                    url=source.get("url", source.get("uri", "")),
                    title=source.get("title", self._extract_domain(source.get("url", ""))),
                    snippet=source.get("snippet"),
                    source_type=self._classify_source_type(source.get("url", "")),
                    relevance_score=source.get("relevance_score")
                ))
        
        # Also check for grounding_metadata in response
        grounding_metadata = result.get("grounding_metadata", {})
        if grounding_metadata:
            web_search_queries = grounding_metadata.get("web_search_queries", [])
            search_entry_point = grounding_metadata.get("search_entry_point", {})
            
            # Extract rendered content sources
            rendered_content = search_entry_point.get("rendered_content", "")
            if rendered_content:
                # Parse URLs from rendered content
                import re
                urls = re.findall(r'https?://[^\s<>"]+', rendered_content)
                for url in urls:
                    if not any(s.url == url for s in sources):
                        sources.append(GroundingSource(
                            url=url,
                            title=self._extract_domain(url),
                            source_type=self._classify_source_type(url)
                        ))
        
        return sources
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www. prefix
            domain = domain.replace("www.", "")
            return domain
        except:
            return url
    
    def _classify_source_type(self, url: str) -> SourceType:
        """Classify source type based on URL."""
        url_lower = url.lower()
        
        if any(site in url_lower for site in ["yelp", "tripadvisor", "google.com/maps", "zomato"]):
            return SourceType.REVIEW_SITE
        elif any(site in url_lower for site in ["instagram", "facebook", "tiktok", "twitter"]):
            return SourceType.SOCIAL_MEDIA
        elif any(site in url_lower for site in ["news", "article", "blog"]):
            return SourceType.NEWS_ARTICLE
        elif any(site in url_lower for site in ["menu", "grubhub", "ubereats", "doordash"]):
            return SourceType.MENU_SITE
        elif any(site in url_lower for site in ["google.com/business", "bing.com/local"]):
            return SourceType.BUSINESS_LISTING
        else:
            return SourceType.WEB_PAGE
    
    # ==================== BATCH OPERATIONS ====================
    
    async def analyze_multiple_competitors(
        self,
        competitors: List[Dict[str, str]],
        location: str
    ) -> List[CompetitorIntelligence]:
        """
        Analyze multiple competitors efficiently.
        
        Args:
            competitors: List of dicts with 'name' and optional 'cuisine_type'
            location: Location for all competitors
        """
        
        results = []
        
        for competitor in competitors:
            try:
                intel = await self.analyze_competitor_with_grounding(
                    competitor_name=competitor["name"],
                    location=location,
                    cuisine_type=competitor.get("cuisine_type")
                )
                results.append(intel)
            except Exception as e:
                logger.error(
                    "competitor_analysis_failed",
                    competitor=competitor["name"],
                    error=str(e)
                )
        
        return results
