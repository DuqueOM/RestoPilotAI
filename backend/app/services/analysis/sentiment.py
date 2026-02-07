"""
Multi-Modal Sentiment Analysis Service.

Provides comprehensive customer sentiment analysis:
- Text review analysis from multiple sources
- Customer photo analysis for visual sentiment
- Item-level sentiment mapping
- Cross-reference with BCG classification
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.gemini.multimodal import MultimodalAgent
from app.services.gemini.reasoning_agent import ReasoningAgent
from loguru import logger


class SentimentSource(str, Enum):
    """Source of sentiment data."""

    GOOGLE = "google"
    YELP = "yelp"
    TRIPADVISOR = "tripadvisor"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    CUSTOMER_PHOTOS = "customer_photos"


class SentimentCategory(str, Enum):
    """Sentiment classification."""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class ReviewData:
    """Individual review data."""

    source: SentimentSource
    text: str
    rating: Optional[float] = None
    date: Optional[str] = None
    reviewer: Optional[str] = None
    review_id: Optional[str] = None


@dataclass
class ItemSentimentResult:
    """Sentiment analysis result for a single menu item."""

    item_name: str
    menu_item_id: Optional[int] = None

    # Text sentiment
    text_sentiment_score: float = 0.0  # -1 to 1
    text_mention_count: int = 0
    common_descriptors: List[str] = field(default_factory=list)

    # Visual sentiment
    visual_appeal_score: Optional[float] = None  # 0-10
    presentation_score: Optional[float] = None
    portion_perception: Optional[str] = None
    portion_score: Optional[float] = None
    photo_count: int = 0

    # Combined
    overall_sentiment: SentimentCategory = SentimentCategory.NEUTRAL
    bcg_category: Optional[str] = None

    # Insight
    actionable_insight: str = ""
    priority: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_name": self.item_name,
            "menu_item_id": self.menu_item_id,
            "text_sentiment": {
                "score": self.text_sentiment_score,
                "mention_count": self.text_mention_count,
                "common_descriptors": self.common_descriptors,
            },
            "visual_sentiment": {
                "appeal_score": self.visual_appeal_score,
                "presentation_score": self.presentation_score,
                "portion_perception": self.portion_perception,
                "portion_score": self.portion_score,
                "photo_count": self.photo_count,
            },
            "overall_sentiment": self.overall_sentiment.value,
            "bcg_category": self.bcg_category,
            "actionable_insight": self.actionable_insight,
            "priority": self.priority,
        }


@dataclass
class SentimentAnalysisResult:
    """Complete sentiment analysis result."""

    analysis_id: str
    restaurant_id: str

    # Overall metrics
    overall_sentiment_score: float  # -1 to 1
    overall_nps: Optional[float]  # Net Promoter Score
    sentiment_distribution: Dict[str, int]
    overall_label: str # Added for frontend
    overall_trend: str # Added for frontend

    # Counts
    total_reviews_analyzed: int
    total_photos_analyzed: int
    sources_used: List[str]
    
    # Frontend compatibility - Moved to end to avoid dataclass default value errors


    # Theme analysis
    common_praises: List[str]
    common_complaints: List[str]

    # Category sentiments
    service_sentiment: Optional[float]
    food_quality_sentiment: Optional[float]
    ambiance_sentiment: Optional[float]
    value_sentiment: Optional[float]

    # Item-level
    item_sentiments: List[ItemSentimentResult]

    # Recommendations
    recommendations: List[Dict[str, Any]]

    # Metadata
    confidence: float
    gemini_tokens_used: int

    # Frontend compatibility
    sources: List[Dict[str, Any]] = field(default_factory=list)
    topics: List[Dict[str, Any]] = field(default_factory=list)
    recent_reviews: List[Dict[str, Any]] = field(default_factory=list)

    grounding_sources: List[Dict[str, str]] = field(default_factory=list)
    grounded: bool = False
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    social_media_analysis: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "analysis_id": self.analysis_id,
            "restaurant_id": self.restaurant_id,
            "overall": {
                "score": self.overall_sentiment_score, # Mapped to 'score' for frontend
                "sentiment_score": self.overall_sentiment_score, # Keep original
                "nps": self.overall_nps,
                "sentiment_distribution": self.sentiment_distribution,
                "label": self.overall_label,
                "trend": self.overall_trend
            },
            "sources": self.sources,
            "topics": self.topics,
            "recentReviews": self.recent_reviews, # Mapped to camelCase for frontend
            "counts": {
                "reviews_analyzed": self.total_reviews_analyzed,
                "photos_analyzed": self.total_photos_analyzed,
                "sources_used": self.sources_used,
            },
            "themes": {
                "praises": self.common_praises,
                "complaints": self.common_complaints,
            },
            "category_sentiments": {
                "service": self.service_sentiment,
                "food_quality": self.food_quality_sentiment,
                "ambiance": self.ambiance_sentiment,
                "value": self.value_sentiment,
            },
            "item_sentiments": [item.to_dict() for item in self.item_sentiments],
            "recommendations": self.recommendations,
            "metadata": {
                "confidence": self.confidence,
                "gemini_tokens_used": self.gemini_tokens_used,
                "analyzed_at": self.analyzed_at.isoformat(),
            },
            "grounding_sources": self.grounding_sources,
            "grounded": self.grounded,
        }
        if self.social_media_analysis:
            result["social_media_analysis"] = self.social_media_analysis
        return result


class SentimentAnalyzer:
    """
    Multi-modal sentiment analysis service.

    Combines text review analysis with visual analysis of customer photos
    to provide comprehensive sentiment insights per menu item.
    """

    def __init__(
        self,
        multimodal_agent: Optional[MultimodalAgent] = None,
        reasoning_agent: Optional[ReasoningAgent] = None,
    ):
        self.multimodal = multimodal_agent or MultimodalAgent()
        self.reasoning = reasoning_agent or ReasoningAgent()

    async def analyze_customer_sentiment(
        self,
        restaurant_id: str,
        reviews: Optional[List[ReviewData]] = None,
        customer_photos: Optional[List[bytes]] = None,
        menu_items: Optional[List[str]] = None,
        bcg_data: Optional[Dict[str, Any]] = None,
        sources: List[SentimentSource] = None,
        social_media_urls: Optional[Dict[str, str]] = None,
        restaurant_name: Optional[str] = None,
    ) -> SentimentAnalysisResult:
        """
        Comprehensive sentiment analysis from reviews, photos, and social media.

        Args:
            restaurant_id: Restaurant identifier
            reviews: List of review data
            customer_photos: List of customer photo bytes
            menu_items: List of menu item names for matching
            bcg_data: BCG classification data for cross-reference
            sources: Sources to analyze
            social_media_urls: Dict of social media platform URLs (instagram, facebook, etc.)
            restaurant_name: Name of the restaurant for social media search

        Returns:
            SentimentAnalysisResult with comprehensive insights
        """
        analysis_id = str(uuid4())

        logger.info(
            "Starting sentiment analysis",
            analysis_id=analysis_id,
            reviews=len(reviews) if reviews else 0,
            photos=len(customer_photos) if customer_photos else 0,
            social_media=list(social_media_urls.keys()) if social_media_urls else [],
        )

        # Initialize results
        text_sentiment = {}
        visual_sentiment = {}
        social_sentiment = {}

        # Step 1: Analyze text reviews
        if reviews:
            text_sentiment = await self._analyze_text_reviews(reviews, menu_items)

        # Step 2: Analyze customer photos
        if customer_photos:
            visual_sentiment = await self._analyze_customer_photos(
                customer_photos, menu_items
            )

        # Step 3: Analyze social media sentiment (grounded search)
        if social_media_urls:
            social_sentiment = await self._analyze_social_media_sentiment(
                social_media_urls, restaurant_name or "restaurant"
            )
            # Merge social media sources into text_sentiment sources
            if social_sentiment.get("sources"):
                existing_sources = text_sentiment.get("sources", [])
                existing_sources.extend(social_sentiment["sources"])
                text_sentiment["sources"] = existing_sources
            # Add social media topics to existing topics
            if social_sentiment.get("topics"):
                existing_topics = text_sentiment.get("topics", [])
                existing_topics.extend(social_sentiment["topics"])
                text_sentiment["topics"] = existing_topics
            # Track social media sources
            for platform in social_media_urls:
                src = SentimentSource.INSTAGRAM if "instagram" in platform.lower() else (
                    SentimentSource.FACEBOOK if "facebook" in platform.lower() else None
                )
                if src and src not in (sources or []):
                    sources = (sources or []) + [src]

        # Step 4: Map sentiment to items
        item_sentiments = await self._map_sentiment_to_items(
            text_sentiment,
            visual_sentiment,
            menu_items or [],
            bcg_data,
        )

        # Step 5: Generate recommendations
        recommendations = await self._generate_recommendations(
            item_sentiments,
            text_sentiment,
            visual_sentiment,
        )

        # Build result
        result = self._build_result(
            analysis_id=analysis_id,
            restaurant_id=restaurant_id,
            text_sentiment=text_sentiment,
            visual_sentiment=visual_sentiment,
            item_sentiments=item_sentiments,
            recommendations=recommendations,
            reviews_count=len(reviews) if reviews else 0,
            photos_count=len(customer_photos) if customer_photos else 0,
            sources=sources or [],
        )

        # Attach social media analysis as separate section
        if social_sentiment:
            result.social_media_analysis = social_sentiment

        logger.info(
            "Sentiment analysis completed",
            analysis_id=analysis_id,
            overall_score=result.overall_sentiment_score,
            social_media_integrated=bool(social_sentiment),
        )

        return result

    async def _analyze_text_reviews(
        self,
        reviews: List[ReviewData],
        menu_items: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Analyze text reviews using Gemini NLP."""

        # Calculate source stats
        source_stats = {}
        for r in reviews:
            s_name = r.source.value if isinstance(r.source, SentimentSource) else str(r.source)
            # Normalize source names for display
            if "google" in s_name.lower():
                s_name = "Google Reviews"
            elif "tripadvisor" in s_name.lower():
                s_name = "TripAdvisor"
            elif "yelp" in s_name.lower():
                s_name = "Yelp"
            elif "instagram" in s_name.lower():
                s_name = "Instagram"
            elif "facebook" in s_name.lower():
                s_name = "Facebook"
            
            if s_name not in source_stats:
                source_stats[s_name] = {"count": 0, "sum_rating": 0, "rating_count": 0}
            source_stats[s_name]["count"] += 1
            if r.rating:
                source_stats[s_name]["sum_rating"] += r.rating
                source_stats[s_name]["rating_count"] += 1
        
        sources_list = []
        for name, stats in source_stats.items():
            avg = stats["sum_rating"] / stats["rating_count"] if stats["rating_count"] > 0 else None
            sources_list.append({
                "name": name,
                "count": stats["count"],
                "avgRating": round(avg, 1) if avg else None,
                "sentiment": 0.0 # Placeholder, updated from LLM
            })

        # Prepare reviews for analysis (Limit to 100 for LLM context window efficiency)
        reviews_text = []
        for review in reviews[:100]: 
            reviews_text.append(
                {
                    "text": review.text[:500],  # Truncate per review
                    "rating": review.rating,
                    "source": review.source.value if isinstance(review.source, SentimentSource) else str(review.source),
                }
            )

        # Recent reviews (top 5 from input list)
        recent_reviews = []
        for r in reviews[:5]:
             recent_reviews.append({
                 "text": r.text[:150] + "..." if len(r.text) > 150 else r.text,
                 "rating": r.rating,
                 "source": r.source.value if isinstance(r.source, SentimentSource) else str(r.source),
                 "date": r.date or "Reciente"
             })

        menu_context = ""
        if menu_items:
            menu_context = f"\nKnown menu items: {', '.join(menu_items[:50])}"

        prompt = f"""Analyze these restaurant reviews for sentiment and insights.

REVIEWS ({len(reviews)} total, showing sample of {len(reviews_text)}):
{json.dumps(reviews_text, indent=2)}

{menu_context}

Analyze comprehensively:

1. OVERALL SENTIMENT
   - Distribution (positive/neutral/negative percentages)
   - Net sentiment score (-1 to 1)
   - NPS estimation
   - Overall Label (e.g. "Excellent", "Good", "Mixed", "Poor")
   - Trend (improving/stable/declining) based on context

2. TOPICS & THEMES
   - Identify key topics (Service, Food, Ambiance, Price, Wait Time, etc.)
   - For each topic: sentiment score (0-1), estimated mentions, trend (up/down/stable)

3. CATEGORY SENTIMENT
   - Service (staff, speed, friendliness)
   - Food quality (taste, freshness, presentation)
   - Ambiance (atmosphere, cleanliness, decor)
   - Value (price vs quality perception)

4. ITEM-LEVEL SENTIMENT
   For each menu item mentioned:
   - Sentiment score (-1 to 1)
   - Mention frequency
   - Common descriptors (positive and negative)

5. COMPETITOR MENTIONS
   - Any competitor names mentioned
   - Context of mentions

6. SOURCE SENTIMENT ESTIMATION
   - Estimate sentiment score (0-1) for each source platform present in reviews (Google, TripAdvisor, etc.)

RESPOND WITH JSON:
{{
    "overall": {{
        "sentiment_score": 0.65,
        "nps": 45,
        "label": "Good",
        "trend": "stable",
        "distribution": {{
            "very_positive": 25,
            "positive": 40,
            "neutral": 20,
            "negative": 10,
            "very_negative": 5
        }}
    }},
    "topics": [
        {{"topic": "Service", "sentiment": 0.8, "mentions": 15, "trend": "up"}},
        {{"topic": "Food", "sentiment": 0.9, "mentions": 30, "trend": "stable"}}
    ],
    "source_sentiments": {{
        "Google": 0.85,
        "TripAdvisor": 0.7
    }},
    "themes": {{
        "praises": ["Fresh ingredients", "Friendly staff"],
        "complaints": ["Slow service on weekends", "Small portions"]
    }},
    "category_sentiment": {{
        "service": 0.6,
        "food_quality": 0.8,
        "ambiance": 0.5,
        "value": 0.4
    }},
    "item_sentiments": {{
        "Tacos al Pastor": {{
            "sentiment_score": 0.85,
            "mention_count": 45,
            "positive_descriptors": ["delicious", "authentic"],
            "negative_descriptors": ["small portion"]
        }}
    }},
    "competitor_mentions": [
        {{"name": "Competitor X", "context": "better prices"}}
    ],
    "confidence": 0.85
}}"""

        try:
            # Use grounding to get verifiable market insights
            response = await self.reasoning.generate_with_grounding(
                prompt=prompt,
                temperature=0.4,
                max_output_tokens=8192,
                enable_grounding=True
            )

            result = self.reasoning._parse_json_response(response.get("answer", response))
            
            # Enrich sources list with LLM sentiment
            source_sentiments = result.get("source_sentiments", {})
            for source in sources_list:
                # Fuzzy match or direct lookup
                for key, val in source_sentiments.items():
                    if key.lower() in source["name"].lower():
                        source["sentiment"] = val
                        break
                # Default to overall if not found
                if source["sentiment"] == 0.0:
                    source["sentiment"] = result.get("overall", {}).get("sentiment_score", 0.5)

            # Add calculated fields to result
            result["sources"] = sources_list
            result["recent_reviews"] = recent_reviews

            # Extract grounding info if available
            if response.get("grounded"):
                grounding_chunks = response.get("grounding_metadata", {}).get("grounding_chunks", [])
                result["grounding_sources"] = [
                    {"uri": chunk.get("uri"), "title": chunk.get("title")} 
                    for chunk in grounding_chunks 
                    if chunk.get("uri")
                ]
                result["grounded"] = True
            
            return result

        except Exception as e:
            logger.error(f"Text sentiment analysis failed: {e}")
            return {"error": str(e), "confidence": 0}

    async def _analyze_customer_photos(
        self,
        photos: List[bytes],
        menu_items: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Analyze customer photos for visual sentiment."""

        if not photos:
            return {}

        # Use multimodal agent to analyze photos
        result = await self.multimodal.analyze_customer_photos(
            photos=photos[:20],  # Limit to 20 photos
            menu_items=menu_items,
        )

        return result

    async def _analyze_social_media_sentiment(
        self,
        social_media_urls: Dict[str, str],
        restaurant_name: str,
    ) -> Dict[str, Any]:
        """
        Analyze social media sentiment using Gemini with Google Search grounding.
        
        Uses grounded search to find public sentiment signals about the restaurant
        from Instagram, Facebook, and other social platforms.
        """
        if not social_media_urls:
            return {}

        platforms_info = "\n".join(
            f"- {platform.capitalize()}: {url}"
            for platform, url in social_media_urls.items()
            if url
        )

        prompt = f"""Analyze the social media presence and public sentiment for this restaurant:

RESTAURANT: {restaurant_name}
SOCIAL MEDIA PROFILES:
{platforms_info}

Search for and analyze:
1. Public engagement patterns (likes, comments, shares trends)
2. Customer sentiment in comments and mentions
3. Content strategy effectiveness (food photos, stories, reels)
4. Community engagement and response patterns
5. Brand perception on social media
6. Notable mentions, reviews, or influencer coverage

RESPOND WITH JSON:
{{
    "platforms": [
        {{
            "platform": "instagram",
            "url": "...",
            "estimated_followers": null,
            "engagement_level": "high|medium|low",
            "content_quality": "excellent|good|average|poor",
            "posting_frequency": "daily|weekly|sporadic",
            "sentiment_score": 0.8,
            "key_observations": ["Active food photography", "Good community engagement"],
            "improvement_suggestions": ["Post more stories", "Use trending hashtags"]
        }}
    ],
    "overall_social_sentiment": 0.75,
    "brand_perception": "Trendy gastrobar with strong visual identity",
    "strengths": ["Strong food photography", "Active community"],
    "weaknesses": ["Inconsistent posting schedule"],
    "opportunities": ["Influencer collaborations", "User-generated content campaigns"],
    "sources": [
        {{
            "name": "Instagram",
            "count": 0,
            "avgRating": null,
            "sentiment": 0.8
        }}
    ],
    "topics": [
        {{
            "topic": "Social Media Presence",
            "sentiment": 0.75,
            "mentions": 0,
            "trend": "stable"
        }}
    ],
    "confidence": 0.7
}}"""

        try:
            response = await self.reasoning.generate_with_grounding(
                prompt=prompt,
                temperature=0.4,
                max_output_tokens=4096,
                enable_grounding=True,
            )

            result = self.reasoning._parse_json_response(
                response.get("answer", response)
            )

            # Extract grounding metadata
            if response.get("grounded"):
                grounding_chunks = response.get("grounding_metadata", {}).get(
                    "grounding_chunks", []
                )
                result["grounding_sources"] = [
                    {"uri": chunk.get("uri"), "title": chunk.get("title")}
                    for chunk in grounding_chunks
                    if chunk.get("uri")
                ]
                result["grounded"] = True

            logger.info(
                f"Social media sentiment analysis completed for {restaurant_name}: "
                f"score={result.get('overall_social_sentiment', 'N/A')}, "
                f"platforms={len(result.get('platforms', []))}"
            )

            return result

        except Exception as e:
            logger.error(f"Social media sentiment analysis failed: {e}")
            return {"error": str(e), "confidence": 0}

    async def _map_sentiment_to_items(
        self,
        text_sentiment: Dict[str, Any],
        visual_sentiment: Dict[str, Any],
        menu_items: List[str],
        bcg_data: Optional[Dict[str, Any]],
    ) -> List[ItemSentimentResult]:
        """Map sentiment data to individual menu items."""

        item_results = []

        # Get text-based item sentiments
        text_items = text_sentiment.get("item_sentiments", {})

        # Get visual-based item sentiments
        visual_items = visual_sentiment.get("per_dish_summary", {})

        # Get BCG classifications
        bcg_classifications = {}
        if bcg_data:
            for product in bcg_data.get(
                "products", bcg_data.get("classifications", [])
            ):
                name = product.get("name", product.get("item_name", ""))
                bcg_classifications[name.lower()] = product.get(
                    "classification", product.get("bcg_class", "")
                )

        # Process all known menu items
        all_items = set(menu_items)
        all_items.update(text_items.keys())
        all_items.update(visual_items.keys())

        for item_name in all_items:
            text_data = text_items.get(item_name, {})
            visual_data = visual_items.get(item_name, {})

            # Calculate combined sentiment
            text_score = text_data.get("sentiment_score", 0)
            visual_appeal = (
                visual_data.get("avg_presentation", 5) / 10
                if visual_data.get("avg_presentation")
                else None
            )

            # Determine overall sentiment category
            combined_score = text_score
            if visual_appeal is not None:
                # Weight visual slightly less than text
                combined_score = text_score * 0.6 + (visual_appeal * 2 - 1) * 0.4

            if combined_score >= 0.5:
                overall = SentimentCategory.VERY_POSITIVE
            elif combined_score >= 0.2:
                overall = SentimentCategory.POSITIVE
            elif combined_score >= -0.2:
                overall = SentimentCategory.NEUTRAL
            elif combined_score >= -0.5:
                overall = SentimentCategory.NEGATIVE
            else:
                overall = SentimentCategory.VERY_NEGATIVE

            # Generate actionable insight
            insight = self._generate_item_insight(
                item_name,
                text_data,
                visual_data,
                bcg_classifications.get(item_name.lower()),
            )

            item_results.append(
                ItemSentimentResult(
                    item_name=item_name,
                    text_sentiment_score=text_score,
                    text_mention_count=text_data.get("mention_count", 0),
                    common_descriptors=text_data.get("positive_descriptors", [])
                    + text_data.get("negative_descriptors", []),
                    visual_appeal_score=visual_data.get("avg_presentation"),
                    portion_perception=visual_data.get("portion_perception"),
                    portion_score=visual_data.get("avg_portion_score"),
                    photo_count=visual_data.get("photo_count", 0),
                    overall_sentiment=overall,
                    bcg_category=bcg_classifications.get(item_name.lower()),
                    actionable_insight=insight["insight"],
                    priority=insight["priority"],
                )
            )

        # Sort by priority and mention count
        item_results.sort(
            key=lambda x: (
                0 if x.priority == "high" else (1 if x.priority == "medium" else 2),
                -x.text_mention_count,
            )
        )

        return item_results

    def _generate_item_insight(
        self,
        item_name: str,
        text_data: Dict[str, Any],
        visual_data: Dict[str, Any],
        bcg_category: Optional[str],
    ) -> Dict[str, str]:
        """Generate actionable insight for an item based on sentiment data."""

        text_score = text_data.get("sentiment_score", 0)
        portion = (
            visual_data.get("portion_perception", "").lower() if visual_data else ""
        )
        presentation = visual_data.get("avg_presentation", 5) if visual_data else 5

        # High priority issues
        if bcg_category == "star" and text_score < 0.3:
            return {
                "insight": "⚠️ Star product with declining sentiment - investigate quality issues immediately",
                "priority": "high",
            }

        if bcg_category == "cash_cow" and text_score < 0:
            return {
                "insight": "⚠️ Cash Cow with negative sentiment - risk of revenue loss, investigate",
                "priority": "high",
            }

        if portion in ["small", "very_small"] and text_score > 0.5:
            return {
                "insight": "💡 Customers love taste but expect larger portions - consider 15-20% increase",
                "priority": "high",
            }

        # Medium priority
        if presentation < 6 and bcg_category == "star":
            return {
                "insight": "🎨 Star product with presentation issues - improve plating to match demand",
                "priority": "medium",
            }

        if text_score < 0 and text_data.get("mention_count", 0) > 10:
            negative_desc = text_data.get("negative_descriptors", [])
            desc_text = f" ({', '.join(negative_desc[:2])})" if negative_desc else ""
            return {
                "insight": f"📉 Frequently mentioned with negative sentiment{desc_text}",
                "priority": "medium",
            }

        # Low priority / positive
        if text_score > 0.7:
            return {
                "insight": "✅ Strong positive sentiment - consider featuring in marketing",
                "priority": "low",
            }

        if portion == "generous" and text_score > 0.5:
            return {
                "insight": "✅ Customers appreciate generous portions - maintain current sizing",
                "priority": "low",
            }

        return {"insight": "Continue monitoring", "priority": "low"}

    async def _generate_recommendations(
        self,
        item_sentiments: List[ItemSentimentResult],
        text_sentiment: Dict[str, Any],
        visual_sentiment: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate strategic recommendations based on sentiment analysis."""

        recommendations = []

        # High priority items
        high_priority = [i for i in item_sentiments if i.priority == "high"]
        for item in high_priority[:5]:
            recommendations.append(
                {
                    "priority": "high",
                    "type": "quality_issue",
                    "item": item.item_name,
                    "issue": item.actionable_insight,
                    "action": f"Investigate and address quality/portion issues for {item.item_name}",
                    "expected_impact": "Prevent customer churn, protect revenue",
                }
            )

        # Portion issues
        portion_issues = [
            i
            for i in item_sentiments
            if i.portion_perception in ["small", "very_small"]
            and i.text_sentiment_score > 0
        ]
        if portion_issues:
            recommendations.append(
                {
                    "priority": "medium",
                    "type": "portion_adjustment",
                    "items": [i.item_name for i in portion_issues[:5]],
                    "issue": "Multiple items perceived as small portions despite positive taste feedback",
                    "action": "Review and increase portion sizes by 15-20%",
                    "expected_impact": "Improved customer satisfaction and perceived value",
                }
            )

        # Presentation improvements
        presentation_issues = [
            i
            for i in item_sentiments
            if i.visual_appeal_score and i.visual_appeal_score < 6
        ]
        if presentation_issues:
            recommendations.append(
                {
                    "priority": "medium",
                    "type": "presentation_improvement",
                    "items": [i.item_name for i in presentation_issues[:5]],
                    "issue": "Items with below-average visual presentation in customer photos",
                    "action": "Improve plating and presentation standards",
                    "expected_impact": "Better social media presence, increased appeal",
                }
            )

        # Highlight strengths
        top_performers = [
            i
            for i in item_sentiments
            if i.text_sentiment_score > 0.7 and i.text_mention_count > 5
        ]
        if top_performers:
            recommendations.append(
                {
                    "priority": "low",
                    "type": "marketing_opportunity",
                    "items": [i.item_name for i in top_performers[:5]],
                    "issue": "Highly praised items with strong sentiment",
                    "action": "Feature in marketing campaigns and social media",
                    "expected_impact": "Leverage positive word-of-mouth",
                }
            )

        # Common complaints
        complaints = text_sentiment.get("themes", {}).get("complaints", [])
        if complaints:
            recommendations.append(
                {
                    "priority": "medium",
                    "type": "address_complaints",
                    "issues": complaints[:5],
                    "action": "Address recurring customer complaints",
                    "expected_impact": "Improved overall satisfaction scores",
                }
            )

        return recommendations

    def _build_result(
        self,
        analysis_id: str,
        restaurant_id: str,
        text_sentiment: Dict[str, Any],
        visual_sentiment: Dict[str, Any],
        item_sentiments: List[ItemSentimentResult],
        recommendations: List[Dict[str, Any]],
        reviews_count: int,
        photos_count: int,
        sources: List[SentimentSource],
    ) -> SentimentAnalysisResult:
        """Build the final sentiment analysis result."""

        overall = text_sentiment.get("overall", {})
        themes = text_sentiment.get("themes", {})
        category_sentiment = text_sentiment.get("category_sentiment", {})

        return SentimentAnalysisResult(
            analysis_id=analysis_id,
            restaurant_id=restaurant_id,
            overall_sentiment_score=overall.get("sentiment_score", 0),
            overall_nps=overall.get("nps"),
            sentiment_distribution=overall.get("distribution", {}),
            overall_label=overall.get("label", "Neutral"),
            overall_trend=overall.get("trend", "stable"),
            total_reviews_analyzed=reviews_count,
            total_photos_analyzed=photos_count,
            sources_used=[
                s.value if isinstance(s, SentimentSource) else s for s in sources
            ],
            sources=text_sentiment.get("sources", []),
            topics=text_sentiment.get("topics", []),
            recent_reviews=text_sentiment.get("recent_reviews", []),
            common_praises=themes.get("praises", []),
            common_complaints=themes.get("complaints", []),
            service_sentiment=category_sentiment.get("service"),
            food_quality_sentiment=category_sentiment.get("food_quality"),
            ambiance_sentiment=category_sentiment.get("ambiance"),
            value_sentiment=category_sentiment.get("value"),
            grounding_sources=text_sentiment.get("grounding_sources", []),
            grounded=text_sentiment.get("grounded", False),
            item_sentiments=item_sentiments,
            recommendations=recommendations,
            confidence=text_sentiment.get("confidence", 0.7),
            gemini_tokens_used=self.reasoning.total_tokens,
        )

    async def get_quick_sentiment(
        self,
        reviews: List[str],
    ) -> Dict[str, Any]:
        """
        Quick sentiment analysis for a batch of review texts.

        Returns overall sentiment without item-level breakdown.
        """

        prompt = f"""Analyze sentiment of these reviews quickly.

REVIEWS:
{json.dumps(reviews[:50], indent=2)}

Return JSON:
{{
    "overall_sentiment": 0.65,
    "distribution": {{"positive": 60, "neutral": 25, "negative": 15}},
    "top_praise": "Great food",
    "top_complaint": "Slow service",
    "confidence": 0.8
}}"""

        response = await self.reasoning._generate_content(
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=1024,
            feature="quick_sentiment",
        )

        return self.reasoning._parse_json_response(response)
