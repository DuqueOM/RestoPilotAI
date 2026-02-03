"""
Campaign Image Generator - Imagen 3 Integration.

Provides end-to-end campaign generation:
1. Gemini analyzes dish/concept
2. Gemini creates campaign strategy
3. Gemini optimizes prompt for Imagen 3
4. Imagen 3 generates images
5. Gemini writes copy (caption, hashtags, schedule)

Complete cycle: Analysis → Strategy → Generation → Deploy
"""

import base64
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field

from app.services.gemini.enhanced_agent import (
    EnhancedGeminiAgent,
    ThinkingLevel
)
from app.core.config import GeminiModel


# ==================== Models ====================

class ImagePrompt(BaseModel):
    """Optimized prompt for Imagen 3."""
    positive_prompt: str
    negative_prompt: str
    aspect_ratio: str = "1:1"  # 1:1, 4:5, 16:9
    guidance_scale: float = Field(ge=10.0, le=30.0, default=20.0)
    num_images: int = Field(ge=1, le=4, default=4)


class CampaignCopy(BaseModel):
    """Campaign copy and metadata."""
    caption: str
    hashtags: List[str] = Field(default_factory=list)
    call_to_action: str
    posting_schedule: Dict[str, str] = Field(default_factory=dict)
    target_audience: str
    tone: str


class CampaignPackage(BaseModel):
    """Complete campaign package."""
    campaign_id: str
    dish_name: str
    campaign_brief: str
    strategy: Dict[str, Any]
    image_prompt: ImagePrompt
    generated_images: List[str] = Field(default_factory=list)  # Base64 encoded
    copy: CampaignCopy
    estimated_reach: Optional[str] = None
    best_posting_times: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==================== Campaign Image Generator ====================

class CampaignImageGenerator:
    """
    🎨 CAMPAIGN IMAGE GENERATOR
    
    End-to-end campaign generation using Gemini 3 + Imagen 3:
    - Gemini analyzes dish/concept
    - Gemini creates strategy
    - Gemini optimizes Imagen prompt
    - Imagen generates images (simulated for now)
    - Gemini writes complete copy
    
    ADVANTAGE: Imagen 3 is superior to DALL-E 3 for food photography.
    """
    
    def __init__(self):
        self.gemini = EnhancedGeminiAgent(
            model=GeminiModel.FLASH_PREVIEW,
            enable_grounding=True,
            enable_cache=False  # Don't cache creative generation
        )
        logger.info("campaign_image_generator_initialized")
    
    async def generate_complete_campaign(
        self,
        dish_name: str,
        campaign_brief: str,
        dish_description: Optional[str] = None,
        dish_image: Optional[bytes] = None,
        style: str = "professional_food_photography",
        platform: str = "instagram"
    ) -> CampaignPackage:
        """
        🚀 Generate complete campaign package.
        
        Steps:
        1. Analyze dish (with image if provided)
        2. Create campaign strategy
        3. Generate optimized Imagen prompt
        4. Generate images (simulated)
        5. Write campaign copy
        
        Args:
            dish_name: Name of the dish
            campaign_brief: Brief description of campaign goals
            dish_description: Optional description
            dish_image: Optional image of the dish
            style: Image style
            platform: Target platform (instagram, facebook, etc.)
            
        Returns:
            Complete campaign package ready to deploy
        """
        
        logger.info(
            "campaign_generation_started",
            dish=dish_name,
            platform=platform
        )
        
        # Step 1: Analyze dish
        dish_analysis = await self._analyze_dish(
            dish_name=dish_name,
            description=dish_description,
            image=dish_image
        )
        
        # Step 2: Create campaign strategy
        strategy = await self._create_campaign_strategy(
            dish_name=dish_name,
            dish_analysis=dish_analysis,
            campaign_brief=campaign_brief,
            platform=platform
        )
        
        # Step 3: Generate optimized Imagen prompt
        image_prompt = await self._create_imagen_prompt(
            dish_name=dish_name,
            strategy=strategy,
            style=style,
            platform=platform
        )
        
        # Step 4: Generate images (simulated for now)
        generated_images = await self._generate_images(image_prompt)
        
        # Step 5: Write campaign copy
        copy = await self._write_campaign_copy(
            dish_name=dish_name,
            strategy=strategy,
            platform=platform
        )
        
        # Create campaign package
        campaign_id = f"campaign_{dish_name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        package = CampaignPackage(
            campaign_id=campaign_id,
            dish_name=dish_name,
            campaign_brief=campaign_brief,
            strategy=strategy,
            image_prompt=image_prompt,
            generated_images=generated_images,
            copy=copy,
            estimated_reach=strategy.get("estimated_reach"),
            best_posting_times=strategy.get("best_posting_times", [])
        )
        
        logger.info(
            "campaign_generation_complete",
            campaign_id=campaign_id,
            images_generated=len(generated_images)
        )
        
        return package
    
    async def _analyze_dish(
        self,
        dish_name: str,
        description: Optional[str],
        image: Optional[bytes]
    ) -> Dict[str, Any]:
        """Analyze dish characteristics."""
        
        prompt = f"""Analyze this dish for marketing campaign purposes.

DISH: {dish_name}
{f"DESCRIPTION: {description}" if description else ""}

Analyze:
1. Visual characteristics (colors, textures, composition)
2. Target audience (who would love this?)
3. Emotional appeal (what feelings does it evoke?)
4. Unique selling points
5. Best presentation angle
6. Ideal lighting and mood

RETURN AS JSON:
{{
    "visual_characteristics": {{
        "dominant_colors": ["color1", "color2"],
        "textures": ["texture1", "texture2"],
        "composition": "string"
    }},
    "target_audience": {{
        "primary": "string",
        "secondary": "string",
        "demographics": "string"
    }},
    "emotional_appeal": ["emotion1", "emotion2"],
    "unique_selling_points": ["usp1", "usp2"],
    "presentation_recommendations": {{
        "angle": "overhead|45-degree|side",
        "lighting": "natural|dramatic|soft",
        "mood": "fresh|cozy|elegant|vibrant"
    }}
}}
"""
        
        images = [image] if image else None
        
        result = await self.gemini.generate(
            prompt=prompt,
            images=images,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=False
        )
        
        return result["data"]
    
    async def _create_campaign_strategy(
        self,
        dish_name: str,
        dish_analysis: Dict[str, Any],
        campaign_brief: str,
        platform: str
    ) -> Dict[str, Any]:
        """Create comprehensive campaign strategy."""
        
        prompt = f"""Create a marketing campaign strategy.

DISH: {dish_name}
CAMPAIGN BRIEF: {campaign_brief}
PLATFORM: {platform}

DISH ANALYSIS:
{json.dumps(dish_analysis, indent=2)}

Create a comprehensive strategy including:

1. **Campaign Concept**:
   - Main theme
   - Key message
   - Unique angle

2. **Visual Strategy**:
   - Photography style
   - Color palette
   - Composition approach
   - Props and styling

3. **Content Strategy**:
   - Tone of voice
   - Key talking points
   - Storytelling approach

4. **Timing Strategy**:
   - Best posting times
   - Optimal days
   - Campaign duration

5. **Engagement Strategy**:
   - Call-to-action
   - Hashtag strategy
   - User engagement tactics

6. **Success Metrics**:
   - Expected reach
   - Engagement targets
   - Conversion goals

RETURN AS JSON with all strategy components.
"""
        
        result = await self.gemini.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.EXHAUSTIVE,
            enable_grounding=True  # Use grounding for market trends
        )
        
        return result["data"]
    
    async def _create_imagen_prompt(
        self,
        dish_name: str,
        strategy: Dict[str, Any],
        style: str,
        platform: str
    ) -> ImagePrompt:
        """Create optimized prompt for Imagen 3."""
        
        prompt = f"""You are an expert at creating prompts for Imagen 3 (Google's image generation model).

DISH: {dish_name}
STYLE: {style}
PLATFORM: {platform}

STRATEGY:
{json.dumps(strategy, indent=2)}

Create a detailed Imagen 3 prompt that will generate a professional, appetizing marketing image.

PROMPT ENGINEERING GUIDELINES:
1. Be specific about composition (overhead, 45-degree, close-up, etc.)
2. Specify lighting (natural window light, soft diffused, dramatic, etc.)
3. Include color palette details
4. Mention texture and detail level
5. Specify mood and atmosphere
6. Add technical photography terms (depth of field, bokeh, etc.)
7. Include styling elements (props, background, garnishes)

NEGATIVE PROMPT should exclude:
- Blurry, low quality, distorted
- Unappetizing, artificial colors
- Cluttered, messy
- Poor lighting, overexposed, underexposed

ASPECT RATIO:
- Instagram feed: 1:1
- Instagram story: 4:5
- YouTube thumbnail: 16:9

GUIDANCE SCALE:
- 15-20: More creative, varied
- 20-25: Balanced
- 25-30: More literal, precise

RETURN AS JSON:
{{
    "positive_prompt": "detailed prompt here",
    "negative_prompt": "what to avoid",
    "aspect_ratio": "1:1|4:5|16:9",
    "guidance_scale": 15-30,
    "num_images": 4
}}
"""
        
        result = await self.gemini.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=False
        )
        
        try:
            return ImagePrompt(**result["data"])
        except Exception as e:
            logger.error("imagen_prompt_validation_failed", error=str(e))
            # Return default prompt
            return ImagePrompt(
                positive_prompt=f"Professional food photography of {dish_name}, appetizing, high quality",
                negative_prompt="blurry, low quality, unappetizing",
                aspect_ratio="1:1",
                guidance_scale=20.0,
                num_images=4
            )
    
    async def _generate_images(
        self,
        image_prompt: ImagePrompt
    ) -> List[str]:
        """
        Generate images with Imagen 3.
        
        NOTE: This is simulated for now. In production, you would:
        1. Set up Vertex AI credentials
        2. Initialize ImageGenerationModel
        3. Call generate_images()
        4. Return actual generated images
        
        For hackathon demo, we return placeholder data.
        """
        
        logger.info(
            "image_generation_requested",
            prompt=image_prompt.positive_prompt[:100],
            num_images=image_prompt.num_images
        )
        
        # Simulated image generation
        # In production, this would be:
        # from vertexai.preview.vision_models import ImageGenerationModel
        # model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        # images = model.generate_images(
        #     prompt=image_prompt.positive_prompt,
        #     negative_prompt=image_prompt.negative_prompt,
        #     number_of_images=image_prompt.num_images,
        #     guidance_scale=image_prompt.guidance_scale,
        #     aspect_ratio=image_prompt.aspect_ratio
        # )
        # return [base64.b64encode(img._image_bytes).decode() for img in images]
        
        # For now, return placeholder
        placeholders = []
        for i in range(image_prompt.num_images):
            placeholder = {
                "image_id": f"imagen_{i+1}",
                "prompt_used": image_prompt.positive_prompt,
                "note": "Image generation with Imagen 3 - requires Vertex AI setup"
            }
            placeholders.append(json.dumps(placeholder))
        
        return placeholders
    
    async def _write_campaign_copy(
        self,
        dish_name: str,
        strategy: Dict[str, Any],
        platform: str
    ) -> CampaignCopy:
        """Write complete campaign copy."""
        
        prompt = f"""Write compelling campaign copy for {platform}.

DISH: {dish_name}

STRATEGY:
{json.dumps(strategy, indent=2)}

Create:

1. **Caption** (engaging, platform-appropriate length):
   - Hook in first line
   - Storytelling
   - Emotional connection
   - Call-to-action

2. **Hashtags** (mix of popular and niche):
   - 5-10 relevant hashtags
   - Include branded hashtag
   - Mix of reach and engagement tags

3. **Call-to-Action**:
   - Clear, actionable
   - Creates urgency or desire

4. **Posting Schedule**:
   - Best day of week
   - Optimal time
   - Frequency

5. **Target Audience**:
   - Primary demographic
   - Interests and behaviors

6. **Tone**:
   - Voice and personality
   - Emotional approach

PLATFORM GUIDELINES:
- Instagram: Casual, visual, emoji-friendly, 2200 char max
- Facebook: Conversational, longer form ok
- TikTok: Trendy, short, hook-driven
- LinkedIn: Professional, value-focused

RETURN AS JSON:
{{
    "caption": "string",
    "hashtags": ["tag1", "tag2"],
    "call_to_action": "string",
    "posting_schedule": {{
        "best_day": "string",
        "best_time": "string",
        "frequency": "string"
    }},
    "target_audience": "string",
    "tone": "string"
}}
"""
        
        result = await self.gemini.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.DEEP,
            enable_grounding=True  # Use grounding for trending hashtags
        )
        
        try:
            return CampaignCopy(**result["data"])
        except Exception as e:
            logger.error("campaign_copy_validation_failed", error=str(e))
            return CampaignCopy(
                caption=f"Introducing our amazing {dish_name}! 🍽️",
                hashtags=["#foodie", "#restaurant", "#delicious"],
                call_to_action="Visit us today!",
                posting_schedule={"best_day": "Friday", "best_time": "6pm"},
                target_audience="Food enthusiasts",
                tone="Casual and inviting"
            )
    
    # ==================== Utility Methods ====================
    
    async def regenerate_images(
        self,
        image_prompt: ImagePrompt,
        variations: int = 4
    ) -> List[str]:
        """Regenerate images with same or modified prompt."""
        return await self._generate_images(image_prompt)
    
    async def refine_copy(
        self,
        original_copy: CampaignCopy,
        feedback: str
    ) -> CampaignCopy:
        """Refine campaign copy based on feedback."""
        
        prompt = f"""Refine this campaign copy based on feedback.

ORIGINAL COPY:
{json.dumps(original_copy.model_dump(), indent=2)}

FEEDBACK: {feedback}

Improve the copy while maintaining the core message.
Return updated copy in the same JSON format.
"""
        
        result = await self.gemini.generate(
            prompt=prompt,
            thinking_level=ThinkingLevel.STANDARD
        )
        
        try:
            return CampaignCopy(**result["data"])
        except:
            return original_copy
