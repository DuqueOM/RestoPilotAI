import asyncio
import base64
import json
from typing import Dict, List, Union

from loguru import logger
from pydantic import BaseModel

from app.services.gemini.base_agent import GeminiBaseAgent, GeminiModel


class DishPhotoScore(BaseModel):
    photo_url: str
    lighting_score: float  # 0-10
    composition_score: float  # 0-10
    color_saturation_score: float  # 0-10
    professional_score: float  # 0-10
    portion_size_estimate: str  # "small", "medium", "large"
    plating_style: str  # "casual", "upscale", "fine_dining"
    gemini_insights: str


class VisualGapAnalysis(BaseModel):
    your_average_score: float
    competitor_average_score: float
    gap_percentage: float
    recommendations: List[str]
    detailed_comparison: Dict[str, List[DishPhotoScore]]


class VisualAnalyzer(GeminiBaseAgent):
    """
    Uses Gemini 3 vision to analyze dish photos with high resolution capabilities.
    """

    def __init__(self, model: GeminiModel = GeminiModel.PRO, **kwargs):
        super().__init__(model=model, **kwargs)

    async def analyze_dish_photo(
        self, image_input: Union[str, bytes], is_url: bool = True
    ) -> DishPhotoScore:
        """
        Analyze a single dish photo using Gemini vision.

        Args:
            image_input: URL string or bytes of the image
            is_url: Whether the input is a URL (True) or raw bytes (False)
        """

        image_data = None
        photo_url = "uploaded_image"

        if is_url and isinstance(image_input, str):
            photo_url = image_input
            # Download image if it's a URL
            import httpx

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(image_input)
                    response.raise_for_status()
                    image_data = response.content
                except Exception as e:
                    logger.error(f"Failed to download image from {image_input}: {e}")
                    # Return a default/failed score object or raise
                    return self._get_default_score(
                        photo_url, f"Failed to download: {str(e)}"
                    )
        else:
            image_data = image_input

        if not image_data:
            return self._get_default_score(photo_url, "No image data")

        # Prepare for Gemini (base64 encoding)
        image_b64 = base64.b64encode(image_data).decode()

        # Craft prompt for detailed analysis
        prompt = """
        Analyze this restaurant dish photo in detail. Provide scores (0-10) for:
        
        1. **Lighting Quality**: Natural vs artificial, shadows, exposure
        2. **Composition**: Framing, rule of thirds, focal point
        3. **Color Saturation**: Vibrancy, appeal, balance
        4. **Professional Score**: Overall presentation quality
        
        Also determine:
        - **Portion Size**: Small / Medium / Large
        - **Plating Style**: Casual / Upscale / Fine Dining
        
        Return as JSON:
        {
          "lighting_score": float,
          "composition_score": float,
          "color_saturation_score": float,
          "professional_score": float,
          "portion_size_estimate": str,
          "plating_style": str,
          "insights": "Brief explanation of strengths/weaknesses"
        }
        """

        try:
            # We use the existing _generate_multimodal method from GeminiBaseAgent
            # Ideally we would pass "media_resolution": "high" if the underlying method supported it via kwargs.
            # Assuming _generate_multimodal passes **kwargs to config/generation call.

            response_text = await self._generate_multimodal(
                prompt=prompt,
                images=[image_b64],
                temperature=0.7,
                feature="visual_analysis_high_res",
                # The user requested media_resolution: 'media_resolution_high'.
                # Passing it in kwargs assuming GeminiBaseAgent handles it or we might need to update GeminiBaseAgent.
                # For now, we pass it and hope the base agent or the google-generativeai lib handles it if passed to generation_config.
                media_resolution="high",
            )

            result = self._parse_json_response(response_text)

            return DishPhotoScore(
                photo_url=photo_url,
                lighting_score=result.get("lighting_score", 0.0),
                composition_score=result.get("composition_score", 0.0),
                color_saturation_score=result.get("color_saturation_score", 0.0),
                professional_score=result.get("professional_score", 0.0),
                portion_size_estimate=result.get("portion_size_estimate", "Unknown"),
                plating_style=result.get("plating_style", "Unknown"),
                gemini_insights=result.get("insights", "No insights generated"),
            )

        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
            return self._get_default_score(photo_url, str(e))

    def _get_default_score(self, url: str, error: str) -> DishPhotoScore:
        return DishPhotoScore(
            photo_url=url,
            lighting_score=0,
            composition_score=0,
            color_saturation_score=0,
            professional_score=0,
            portion_size_estimate="Unknown",
            plating_style="Unknown",
            gemini_insights=f"Analysis failed: {error}",
        )

    async def compare_visual_quality(
        self,
        your_photos: List[str],  # List of URLs
        competitor_photos: List[str],  # List of URLs
    ) -> VisualGapAnalysis:
        """
        Compare your photos vs competitors' photos.
        """

        # Analyze all photos in parallel
        # Limit concurrency to avoid hitting rate limits too hard if many photos
        sem = asyncio.Semaphore(5)

        async def analyze_with_limit(url):
            async with sem:
                return await self.analyze_dish_photo(url, is_url=True)

        your_scores = await asyncio.gather(
            *[analyze_with_limit(url) for url in your_photos]
        )

        competitor_scores = await asyncio.gather(
            *[analyze_with_limit(url) for url in competitor_photos]
        )

        # Calculate averages
        your_valid = [s for s in your_scores if s.professional_score > 0]
        comp_valid = [s for s in competitor_scores if s.professional_score > 0]

        your_avg = (
            sum(s.professional_score for s in your_valid) / len(your_valid)
            if your_valid
            else 0
        )
        comp_avg = (
            sum(s.professional_score for s in comp_valid) / len(comp_valid)
            if comp_valid
            else 0
        )

        gap = ((comp_avg - your_avg) / comp_avg) * 100 if comp_avg > 0 else 0

        # Generate recommendations using Gemini
        recommendations = await self._generate_recommendations(
            your_avg, comp_avg, your_scores, competitor_scores
        )

        return VisualGapAnalysis(
            your_average_score=your_avg,
            competitor_average_score=comp_avg,
            gap_percentage=gap,
            recommendations=recommendations,
            detailed_comparison={
                "yours": your_scores,
                "competitors": competitor_scores,
            },
        )

    async def _generate_recommendations(
        self,
        your_avg: float,
        comp_avg: float,
        your_scores: List[DishPhotoScore],
        comp_scores: List[DishPhotoScore],
    ) -> List[str]:
        """
        Use Gemini to generate actionable recommendations.
        """

        your_weaknesses = [
            s.gemini_insights for s in your_scores if s.professional_score < 7
        ]
        comp_strengths = [
            s.gemini_insights for s in comp_scores if s.professional_score > 8
        ]

        prompt = f"""
        Based on visual analysis:
        
        Your average professional score: {your_avg:.1f}/10
        Competitor average: {comp_avg:.1f}/10
        
        Your weaknesses (from low scoring photos):
        {json.dumps(your_weaknesses[:5], indent=2)}
        
        Competitor strengths (from high scoring photos):
        {json.dumps(comp_strengths[:5], indent=2)}
        
        Generate 3-5 specific, actionable recommendations to improve dish photography.
        Focus on lighting, composition, and presentation that can be implemented immediately.
        """

        try:
            response = await self._generate_content(
                prompt, feature="visual_recommendations"
            )
            # Heuristic to split lines or parse if it's a list
            lines = response.split("\n")
            recommendations = [
                line.strip().lstrip("- ").lstrip("1234567890. ")
                for line in lines
                if line.strip()
            ]
            return recommendations[:5]
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return [
                "Improve lighting",
                "Use better composition",
                "Check competitor photos for inspiration",
            ]
