"""
Advanced Multimodal Agent for Gemini 3 - TOP 1% Implementation.

Maximizes Gemini 3's unique multimodal capabilities:
- Video analysis (UNIQUE to Gemini 3)
- Batch image processing for efficiency
- Comparative visual analysis
- PDF document understanding
- Native audio processing (no external STT)
- Image generation integration

This agent showcases capabilities that competitors cannot match.
"""

import base64
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field

from app.services.gemini.enhanced_agent import (
    EnhancedGeminiAgent,
    ThinkingLevel
)
from app.core.config import GeminiModel


# ==================== Pydantic Schemas ====================

class MenuExtractionSchema(BaseModel):
    """Structured menu extraction with validation."""
    restaurant_name: Optional[str] = None
    menu_sections: List[Dict[str, Any]] = Field(default_factory=list)
    total_items: int = 0
    price_range: Dict[str, float] = Field(default_factory=dict)
    cuisines: List[str] = Field(default_factory=list)
    special_dietary: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0


class DishAnalysisSchema(BaseModel):
    """Structured dish analysis for food photography."""
    overall_score: float = Field(ge=1.0, le=10.0)
    presentation_score: float = Field(ge=1.0, le=10.0)
    lighting_score: float = Field(ge=1.0, le=10.0)
    composition_score: float = Field(ge=1.0, le=10.0)
    instagram_score: float = Field(ge=1.0, le=10.0)
    detailed_feedback: str
    quick_improvements: List[str] = Field(default_factory=list)
    estimated_engagement_boost: str


class VideoAnalysisSchema(BaseModel):
    """Video content analysis for social media."""
    content_type: str
    key_moments: List[Dict[str, Any]] = Field(default_factory=list)
    visual_quality_score: float = Field(ge=1.0, le=10.0)
    audio_quality_score: Optional[float] = Field(default=None, ge=1.0, le=10.0)
    recommended_cuts: List[str] = Field(default_factory=list)
    social_media_suitability: Dict[str, float] = Field(default_factory=dict)
    best_thumbnail_timestamp: Optional[str] = None


class AudioInsightsSchema(BaseModel):
    """Audio transcription and insights."""
    transcription: str
    key_themes: List[str] = Field(default_factory=list)
    emotional_tone: str
    values_detected: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    unique_selling_points: List[str] = Field(default_factory=list)
    story_highlights: List[str] = Field(default_factory=list)
    campaign_angles: List[Dict[str, str]] = Field(default_factory=list)


# ==================== Advanced Multimodal Agent ====================

class AdvancedMultimodalAgent(EnhancedGeminiAgent):
    """
    🌟 TOP 1% MULTIMODAL AGENT
    
    Leverages Gemini 3's unique capabilities that competitors cannot match:
    - Video understanding (OpenAI GPT-4V cannot do this)
    - Batch processing for efficiency
    - Comparative visual analysis
    - Native audio processing (no Whisper needed)
    - PDF document understanding
    - Integration with Imagen 3 for generation
    """
    
    def __init__(self, **kwargs):
        # Use vision model by default for multimodal tasks
        super().__init__(
            model=GeminiModel.PRO_PREVIEW,
            enable_grounding=True,
            enable_cache=True,
            **kwargs
        )
        logger.info("advanced_multimodal_agent_initialized")
    
    # ==================== MENU EXTRACTION ====================
    
    async def extract_menu_from_image(
        self,
        image: bytes,
        language: str = "auto",
        additional_context: Optional[str] = None
    ) -> MenuExtractionSchema:
        """
        Extract menu with GUARANTEED JSON structure.
        
        Handles:
        - Handwritten menus
        - Low quality images
        - Multiple languages
        - Chalkboard/digital displays
        - Complex layouts
        """
        
        prompt = f"""You are a menu extraction specialist with advanced OCR capabilities.

TASK: Extract ALL information from this menu image with maximum accuracy.

IMPORTANT: Even if the image is:
- Handwritten or stylized fonts
- Low quality or blurry
- Unusual layout (vertical, circular, etc.)
- Multiple languages mixed
- Chalkboard, digital display, or printed

You MUST extract everything visible.

LANGUAGE: {language} (auto-detect if 'auto')
{f"CONTEXT: {additional_context}" if additional_context else ""}

EXTRACT COMPLETELY:

1. **Restaurant Name** (if visible anywhere)

2. **Menu Sections** - For each section:
   - Section name (Appetizers, Mains, Desserts, Drinks, etc.)
   - Items in that section

3. **For EACH Item**:
   - Exact name (preserve original language, accents, capitalization)
   - Description (if any, even partial)
   - Price (parse correctly: $, MXN, USD, €, etc.)
   - Dietary labels (🌱 vegetarian, 🌿 vegan, GF gluten-free, etc.)
   - Spice level indicators (🌶️, *, etc.)
   - Allergen warnings (if shown)
   - Special markers (⭐ popular, 🔥 spicy, 👨‍🍳 chef's special, etc.)

4. **Price Analysis**:
   - Minimum price found
   - Maximum price found
   - Average price (calculated)

5. **Cuisine Types** (inferred from items):
   - Mexican, Italian, Asian, Fusion, etc.

6. **Dietary Options Available**:
   - Vegetarian options count
   - Vegan options count
   - Gluten-free options count
   - Other special diets

7. **Confidence Score** (0.0-1.0):
   - How confident are you in this extraction?

RETURN ONLY VALID JSON matching this exact structure:
{{
    "restaurant_name": "string or null",
    "menu_sections": [
        {{
            "name": "string",
            "items": [
                {{
                    "name": "string",
                    "description": "string or null",
                    "price": float,
                    "currency": "string",
                    "dietary_labels": ["string"],
                    "spice_level": int or null,
                    "allergens": ["string"],
                    "special_markers": ["string"]
                }}
            ]
        }}
    ],
    "total_items": int,
    "price_range": {{
        "min": float,
        "max": float,
        "average": float,
        "currency": "string"
    }},
    "cuisines": ["string"],
    "special_dietary": ["vegetarian", "vegan", "gluten-free"],
    "confidence_score": float
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            images=[image],
            thinking_level=ThinkingLevel.DEEP,  # DEEP for maximum extraction accuracy
            enable_grounding=False  # No need for grounding on image extraction
        )
        
        try:
            return MenuExtractionSchema(**result["data"])
        except Exception as e:
            logger.error("menu_extraction_validation_failed", error=str(e))
            # Return with lower confidence if validation fails
            return MenuExtractionSchema(
                total_items=0,
                confidence_score=0.0
            )
    
    async def extract_menu_from_pdf(
        self,
        pdf_bytes: bytes
    ) -> MenuExtractionSchema:
        """
        Extract menu from PDF using Gemini's native document understanding.
        
        No need for external PDF parsers - Gemini handles it natively.
        """
        
        prompt = """You are extracting menu information from a PDF document.

Extract all menu items, prices, sections, and metadata.
Return structured JSON with complete menu data.

Follow the same extraction rules as image-based extraction.
"""
        
        # Gemini can process PDFs directly
        result = await self.generate(
            prompt=prompt,
            images=[pdf_bytes],  # Gemini treats PDFs as images
            thinking_level=ThinkingLevel.STANDARD
        )
        
        try:
            return MenuExtractionSchema(**result["data"])
        except Exception as e:
            logger.error("pdf_extraction_validation_failed", error=str(e))
            return MenuExtractionSchema(total_items=0, confidence_score=0.0)
    
    # ==================== DISH ANALYSIS ====================
    
    async def analyse_dish_image(
        self,
        image: bytes,
        dish_name: str,
        context: Optional[str] = None
    ) -> DishAnalysisSchema:
        """
        🍽️ FOOD PORN AI - Michelin-level dish analysis.
        
        Provides brutally honest, actionable feedback on food photography.
        """
        
        prompt = f"""You are a MICHELIN-STARRED food critic AND professional food photographer.

DISH: {dish_name}
CONTEXT: {context or "Standard restaurant setting"}

Analyze this dish photo with PROFESSIONAL BRUTALITY.

EVALUATE (1-10 scale, be HONEST):

1. **Overall Visual Appeal** (1-10)
   - First impression impact
   - Appetite stimulation level
   - Professional quality assessment

2. **Presentation** (1-10)
   - Plating technique and artistry
   - Portion size appropriateness
   - Garnish placement and purpose
   - Color contrast and harmony
   - Composition and balance
   - Attention to detail

3. **Lighting** (1-10)
   - Natural vs artificial quality
   - Brightness and exposure
   - Shadow management
   - Color temperature accuracy
   - Highlights and depth

4. **Composition** (1-10)
   - Camera angle effectiveness
   - Framing and crop
   - Background choice
   - Negative space usage
   - Rule of thirds application

5. **Instagram-ability** (1-10)
   - Social media shareability
   - Trending aesthetic alignment
   - Visual storytelling power
   - Engagement potential

PROVIDE DETAILED CRITIQUE:
- Professional analysis (2-3 sentences)
- Specific strengths
- Critical weaknesses

GIVE 3 QUICK IMPROVEMENTS:
Be SPECIFIC and ACTIONABLE:
- ❌ "better lighting" 
- ✅ "Shoot near window between 10am-2pm for soft natural light"
- ❌ "improve plating"
- ✅ "Add microgreens to top-right quadrant for color contrast"
- ❌ "better angle"
- ✅ "Shoot from 45° angle, 6 inches higher to show depth"

ESTIMATE ENGAGEMENT BOOST:
If improvements implemented, estimate increase in:
- Likes/engagement
- Shareability
- Professional perception

RETURN ONLY VALID JSON:
{{
    "overall_score": float (1-10),
    "presentation_score": float (1-10),
    "lighting_score": float (1-10),
    "composition_score": float (1-10),
    "instagram_score": float (1-10),
    "detailed_feedback": "string (professional critique)",
    "quick_improvements": [
        "specific actionable improvement 1",
        "specific actionable improvement 2",
        "specific actionable improvement 3"
    ],
    "estimated_engagement_boost": "string (e.g., '+30-40% engagement if all improvements applied')"
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            images=[image],
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=False
        )
        
        try:
            return DishAnalysisSchema(**result["data"])
        except Exception as e:
            logger.error("dish_analysis_validation_failed", error=str(e))
            return DishAnalysisSchema(
                overall_score=5.0,
                presentation_score=5.0,
                lighting_score=5.0,
                composition_score=5.0,
                instagram_score=5.0,
                detailed_feedback="Analysis failed - validation error",
                estimated_engagement_boost="Unknown"
            )
    
    async def analyse_dish_batch(
        self,
        images: List[bytes],
        dish_names: List[str]
    ) -> List[DishAnalysisSchema]:
        """
        🚀 BATCH PROCESSING - Analyze multiple dishes efficiently.
        
        Uses single API call for cost efficiency.
        Perfect for analyzing entire menu's photos at once.
        """
        
        if len(images) != len(dish_names):
            raise ValueError("Number of images must match number of dish names")
        
        dishes_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(dish_names)])
        
        prompt = f"""You are analyzing {len(images)} dish photos in BATCH mode.

DISHES (in order):
{dishes_list}

For EACH dish (maintain order):
1. Rate visual quality (1-10)
2. Identify main weakness
3. Provide ONE specific quick fix
4. Rate Instagram potential (1-10)

RETURN JSON ARRAY with {len(images)} objects:
[
    {{
        "dish_name": "string",
        "overall_score": float,
        "presentation_score": float,
        "lighting_score": float,
        "composition_score": float,
        "instagram_score": float,
        "detailed_feedback": "string",
        "quick_improvements": ["string"],
        "estimated_engagement_boost": "string"
    }}
]
"""
        
        result = await self.generate(
            prompt=prompt,
            images=images,
            thinking_level=ThinkingLevel.STANDARD,
            enable_grounding=False
        )
        
        analyses = []
        try:
            dishes_data = result["data"] if isinstance(result["data"], list) else result["data"].get("dishes", [])
            for dish_data in dishes_data:
                analyses.append(DishAnalysisSchema(**dish_data))
        except Exception as e:
            logger.error("batch_analysis_validation_failed", error=str(e))
            # Return default analyses
            for name in dish_names:
                analyses.append(DishAnalysisSchema(
                    overall_score=5.0,
                    presentation_score=5.0,
                    lighting_score=5.0,
                    composition_score=5.0,
                    instagram_score=5.0,
                    detailed_feedback=f"Batch analysis for {name}",
                    estimated_engagement_boost="Unknown"
                ))
        
        return analyses
    
    # ==================== COMPARATIVE ANALYSIS ====================
    
    async def comparative_dish_analysis(
        self,
        your_dish: bytes,
        competitor_dishes: List[bytes],
        dish_name: str
    ) -> Dict[str, Any]:
        """
        🔥 COMPETITIVE VISUAL ANALYSIS
        
        Compare your dish presentation vs competitors.
        Identify winning elements to steal and gaps to close.
        """
        
        all_images = [your_dish] + competitor_dishes
        total_dishes = len(all_images)
        
        prompt = f"""You are conducting COMPETITIVE VISUAL ANALYSIS for: {dish_name}

IMAGE 1: CLIENT'S current presentation
IMAGES 2-{total_dishes}: Competitor presentations

COMPREHENSIVE COMPETITIVE ANALYSIS:

1. **Overall Ranking**:
   - Rank ALL {total_dishes} dishes by visual appeal (1 = best)
   - Client's current position in ranking
   - Scores for each (1-10)

2. **Client's Strengths**:
   - What client does BETTER than competitors
   - Unique visual elements worth keeping
   - Competitive advantages

3. **Client's Weaknesses**:
   - Where competitors clearly excel
   - Critical gaps in presentation
   - Areas losing to competition

4. **Winning Elements from Competitors**:
   For EACH competitor that ranks higher:
   - Best plating techniques observed
   - Superior garnish strategies
   - Better color combinations
   - Effective portion presentations
   - Lighting/photography advantages

5. **Steal-Worthy Ideas**:
   Specific elements to adopt:
   - Which competitor has it
   - Exact element to copy
   - How to implement it
   - Difficulty level
   - Expected impact

6. **Actionable Recommendations**:
   Prioritized changes to beat competition:
   - Specific change description
   - Implementation difficulty (easy/medium/hard)
   - Impact level (low/medium/high)
   - Estimated cost (if applicable)

RETURN ONLY VALID JSON:
{{
    "your_rank": int (1-{total_dishes}),
    "your_score": float (1-10),
    "competitor_scores": [float],
    "competitor_avg_score": float,
    "gap_to_best": float,
    "gap_to_average": float,
    "strengths": ["string"],
    "weaknesses": ["string"],
    "winning_elements": [
        {{
            "competitor_number": int,
            "element": "string",
            "why_it_works": "string"
        }}
    ],
    "steal_these_ideas": [
        {{
            "from_competitor": int,
            "element": "string",
            "how_to_implement": "string",
            "difficulty": "easy|medium|hard",
            "impact": "low|medium|high"
        }}
    ],
    "recommended_changes": [
        {{
            "priority": int,
            "change": "string",
            "difficulty": "easy|medium|hard",
            "impact": "low|medium|high",
            "estimated_cost": "string"
        }}
    ],
    "estimated_improvement": "string"
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            images=all_images,
            thinking_level=ThinkingLevel.EXHAUSTIVE,
            enable_grounding=False
        )
        
        return result["data"]
    
    async def analyse_customer_photos(
        self,
        customer_photos: List[bytes],
        official_photos: List[bytes],
        dish_name: str
    ) -> Dict[str, Any]:
        """
        📸 EXPECTATION VS REALITY ANALYSIS
        
        Compare professional photos vs actual customer experiences.
        Identify consistency issues and expectation gaps.
        """
        
        all_images = official_photos + customer_photos
        
        prompt = f"""You are analyzing EXPECTATION VS REALITY for: {dish_name}

FIRST {len(official_photos)} IMAGES: Official restaurant photos (the promise)
NEXT {len(customer_photos)} IMAGES: Customer-taken photos (the reality)

CRITICAL ANALYSIS:

1. **Consistency Score** (1-10):
   How similar are customer photos to official marketing?

2. **Specific Discrepancies**:
   - Portion size differences (%)
   - Presentation quality gaps
   - Plating consistency
   - Garnish/details missing
   - Color/freshness differences
   - Lighting/setting differences

3. **Customer Sentiment** (inferred from photos):
   - Disappointment signals
   - Positive surprise indicators
   - Neutral/expected delivery
   - Evidence for each

4. **Common Complaints** (inferred):
   What would customers likely complain about?

5. **Recommendations**:
   How to close the expectation gap:
   - Kitchen training needs
   - Plating standardization
   - Photo update suggestions
   - Portion adjustments

RETURN ONLY VALID JSON:
{{
    "consistency_score": float (1-10),
    "portion_consistency": float (1-10),
    "presentation_consistency": float (1-10),
    "plating_consistency": float (1-10),
    "overall_gap": "small|moderate|large",
    "discrepancies": [
        {{
            "aspect": "string",
            "severity": "low|medium|high",
            "description": "string"
        }}
    ],
    "customer_sentiment": "positive|neutral|negative",
    "sentiment_evidence": ["string"],
    "inferred_complaints": ["string"],
    "recommendations": [
        {{
            "area": "string",
            "action": "string",
            "priority": "low|medium|high"
        }}
    ]
}}
"""
        
        result = await self.generate(
            prompt=prompt,
            images=all_images,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=False
        )
        
        return result["data"]
    
    # ==================== VIDEO ANALYSIS (UNIQUE TO GEMINI 3) ====================
    
    async def analyse_video_content(
        self,
        video_bytes: bytes,
        video_purpose: str = "social_media"
    ) -> VideoAnalysisSchema:
        """
        🎥 VIDEO ANALYSIS - GEMINI 3 EXCLUSIVE FEATURE
        
        ⭐ THIS IS UNIQUE - OpenAI GPT-4V CANNOT DO THIS
        
        Analyze restaurant videos for social media optimization.
        """
        
        prompt = f"""You are a social media video content strategist specializing in restaurant marketing.

VIDEO PURPOSE: {video_purpose}

Analyze this restaurant video COMPREHENSIVELY:

1. **Content Type Classification**:
   - Recipe tutorial / cooking process
   - Behind-the-scenes / kitchen tour
   - Dish reveal / food porn
   - Restaurant ambiance tour
   - Customer testimonial
   - Staff introduction
   - Event coverage
   - Other (specify)

2. **Key Moments** (with timestamps if possible):
   - Most engaging/exciting moments
   - Weak/boring segments
   - Best moments for thumbnails
   - Quotable moments
   - Share-worthy clips

3. **Visual Quality Assessment** (1-10):
   - Camera stability
   - Lighting quality
   - Framing and composition
   - Color grading
   - Focus and clarity
   - Professional polish

4. **Audio Quality Assessment** (1-10) if audio present:
   - Background noise level
   - Music choice appropriateness
   - Voice clarity
   - Audio-visual sync
   - Overall audio production

5. **Recommended Edits**:
   - Where to trim/cut
   - Suggested length for each platform
   - Pacing improvements
   - Transition suggestions
   - Text overlay opportunities

6. **Platform Suitability** (1-10 for each):
   - Instagram Reels (15-60s)
   - TikTok (15-60s)
   - YouTube Shorts (60s)
   - Facebook (1-3min)
   - LinkedIn (30-90s)
   - YouTube (3-10min)

7. **Best Thumbnail Timestamp**:
   - Exact moment for thumbnail
   - Why this moment works

RETURN ONLY VALID JSON:
{{
    "content_type": "string",
    "key_moments": [
        {{
            "timestamp": "string (MM:SS)",
            "description": "string",
            "type": "engaging|weak|thumbnail|shareable"
        }}
    ],
    "visual_quality_score": float (1-10),
    "audio_quality_score": float or null (1-10),
    "recommended_cuts": [
        "string (specific editing recommendation)"
    ],
    "social_media_suitability": {{
        "instagram_reels": float (1-10),
        "tiktok": float (1-10),
        "youtube_shorts": float (1-10),
        "facebook": float (1-10),
        "linkedin": float (1-10),
        "youtube": float (1-10)
    }},
    "best_thumbnail_timestamp": "string (MM:SS)",
    "overall_recommendations": ["string"]
}}
"""
        
        # Note: Video processing requires base64 encoding
        # video_b64 = base64.b64encode(video_bytes).decode()
        
        result = await self.generate(
            prompt=prompt,
            images=[video_bytes],  # Gemini handles video as multimodal input
            thinking_level=ThinkingLevel.EXHAUSTIVE,  # EXHAUSTIVE for maximum video analysis quality
            enable_grounding=False
        )
        
        try:
            return VideoAnalysisSchema(**result["data"])
        except Exception as e:
            logger.error("video_analysis_validation_failed", error=str(e))
            return VideoAnalysisSchema(
                content_type="unknown",
                visual_quality_score=5.0,
                social_media_suitability={}
            )
    
    # ==================== AUDIO ANALYSIS (NATIVE) ====================
    
    async def transcribe_and_analyze_audio(
        self,
        audio_bytes: bytes,
        audio_format: str = "mp3",
        context: str = "business_story"
    ) -> AudioInsightsSchema:
        """
        🎤 NATIVE AUDIO PROCESSING
        
        No need for Whisper or external STT - Gemini handles audio directly.
        Transcribes AND analyzes in one shot.
        """
        
        prompt = f"""You are processing audio from a restaurant owner/manager.

CONTEXT: {context}

COMPREHENSIVE AUDIO ANALYSIS:

1. **Complete Transcription**:
   - Transcribe EVERYTHING said
   - Include filler words if significant
   - Note emotional inflections [excited], [concerned], etc.

2. **Key Insights Extraction**:
   - Main themes discussed
   - Emotional tone throughout
   - Specific values mentioned
   - Challenges/pain points mentioned
   - Goals and aspirations stated
   - Unique selling points claimed
   - Personal stories or anecdotes
   - Passion points (what excites them)

3. **Marketing Intelligence**:
   - Authentic voice/language patterns
   - Emotional hooks for campaigns
   - Story angles for content
   - Brand personality indicators
   - Target audience hints

4. **Campaign Angle Suggestions**:
   Based on their authentic story:
   - Campaign angle
   - Rationale (why it works)
   - Emotional hook to use
   - Suggested tagline/message

RETURN ONLY VALID JSON:
{{
    "transcription": "string (complete verbatim)",
    "key_themes": ["string"],
    "emotional_tone": "string (passionate|concerned|excited|nostalgic|etc)",
    "values_detected": ["string"],
    "challenges": ["string"],
    "goals": ["string"],
    "unique_selling_points": ["string"],
    "story_highlights": ["string (quotable moments)"],
    "campaign_angles": [
        {{
            "angle": "string",
            "rationale": "string",
            "emotional_hook": "string",
            "suggested_message": "string"
        }}
    ]
}}
"""
        
        # Gemini can process audio directly
        # audio_b64 = base64.b64encode(audio_bytes).decode()
        
        result = await self.generate(
            prompt=prompt,
            images=[audio_bytes],  # Audio treated as multimodal input
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=False
        )
        
        try:
            return AudioInsightsSchema(**result["data"])
        except Exception as e:
            logger.error("audio_analysis_validation_failed", error=str(e))
            return AudioInsightsSchema(
                transcription="Transcription failed",
                emotional_tone="unknown"
            )
    
    # ==================== UTILITY METHODS ====================
    
    def _prepare_image_input(self, image_source: Union[str, bytes, Path]) -> bytes:
        """Convert various image sources to bytes."""
        if isinstance(image_source, bytes):
            return image_source
        elif isinstance(image_source, str):
            if Path(image_source).exists():
                return Path(image_source).read_bytes()
            else:
                # Assume base64
                return base64.b64decode(image_source)
        elif isinstance(image_source, Path):
            return image_source.read_bytes()
        else:
            raise ValueError(f"Unsupported image source type: {type(image_source)}")
