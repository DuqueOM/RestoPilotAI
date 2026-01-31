"""
Visual Gap Analyzer - Multimodal comparison using Gemini Vision.

Compares visual presentation of dishes between our restaurant and competitors:
- Food photography quality analysis
- Plating and presentation scoring
- Color vibrancy and appeal metrics
- Portion size perception
- Overall visual marketing effectiveness
"""

import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from app.services.gemini.base_agent import GeminiBaseAgent, GeminiModel


@dataclass
class VisualScore:
    """Visual scoring for a dish image."""

    overall_score: float  # 0-10
    plating_score: float
    color_vibrancy: float
    portion_appeal: float
    lighting_quality: float
    background_quality: float
    appetite_appeal: float  # "Does this make you want to eat it?"

    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "plating_score": self.plating_score,
            "color_vibrancy": self.color_vibrancy,
            "portion_appeal": self.portion_appeal,
            "lighting_quality": self.lighting_quality,
            "background_quality": self.background_quality,
            "appetite_appeal": self.appetite_appeal,
            "strengths": self.strengths,
            "improvements": self.improvements,
        }


@dataclass
class VisualComparison:
    """Comparison between our dish and competitor's."""

    our_dish_name: str
    competitor_dish_name: str
    competitor_name: str

    our_score: VisualScore
    competitor_score: VisualScore

    gap_analysis: Dict[str, float] = field(default_factory=dict)  # Dimension -> gap
    winning_dimensions: List[str] = field(default_factory=list)
    losing_dimensions: List[str] = field(default_factory=list)

    recommendations: List[str] = field(default_factory=list)
    priority: str = "medium"  # low, medium, high

    def to_dict(self) -> Dict[str, Any]:
        return {
            "our_dish_name": self.our_dish_name,
            "competitor_dish_name": self.competitor_dish_name,
            "competitor_name": self.competitor_name,
            "our_score": self.our_score.to_dict(),
            "competitor_score": self.competitor_score.to_dict(),
            "gap_analysis": self.gap_analysis,
            "winning_dimensions": self.winning_dimensions,
            "losing_dimensions": self.losing_dimensions,
            "recommendations": self.recommendations,
            "priority": self.priority,
        }


@dataclass
class VisualGapReport:
    """Complete visual gap analysis report."""

    our_average_score: float
    competitor_average_score: float
    overall_gap: float  # Positive = we're better, negative = they're better

    comparisons: List[VisualComparison] = field(default_factory=list)

    our_visual_strengths: List[str] = field(default_factory=list)
    our_visual_weaknesses: List[str] = field(default_factory=list)

    priority_improvements: List[Dict[str, Any]] = field(default_factory=list)
    quick_wins: List[str] = field(default_factory=list)

    thought_traces: List[Dict[str, Any]] = field(default_factory=list)
    processing_time_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "our_average_score": self.our_average_score,
            "competitor_average_score": self.competitor_average_score,
            "overall_gap": self.overall_gap,
            "comparisons": [c.to_dict() for c in self.comparisons],
            "our_visual_strengths": self.our_visual_strengths,
            "our_visual_weaknesses": self.our_visual_weaknesses,
            "priority_improvements": self.priority_improvements,
            "quick_wins": self.quick_wins,
            "thought_traces": self.thought_traces,
            "processing_time_ms": self.processing_time_ms,
        }


class VisualGapAnalyzer(GeminiBaseAgent):
    """
    Analyzes visual gaps between our restaurant's dish photos
    and competitor photos using Gemini Vision.

    Key capabilities:
    - Single dish scoring with detailed breakdown
    - Side-by-side comparison with competitors
    - Batch analysis of menu photography
    - Actionable improvement recommendations
    """

    def __init__(
        self,
        model: GeminiModel = GeminiModel.FLASH,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.thought_traces: List[Dict[str, Any]] = []

    async def process(self, *args, **kwargs) -> Any:
        """Main entry point."""
        return await self.analyze_visual_gaps(**kwargs)

    def _add_thought(
        self,
        step: str,
        reasoning: str,
        observations: List[str],
        confidence: float,
    ) -> None:
        """Add a thought trace for transparency."""
        self.thought_traces.append(
            {
                "step": step,
                "reasoning": reasoning,
                "observations": observations,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    async def analyze_single_dish(
        self,
        image_data: Union[str, bytes],
        dish_name: str = "Unknown Dish",
        context: Optional[str] = None,
    ) -> VisualScore:
        """
        Analyze a single dish image for visual quality.

        Args:
            image_data: Base64 encoded image or raw bytes
            dish_name: Name of the dish for context
            context: Additional context (e.g., "competitor", "our restaurant")

        Returns:
            VisualScore with detailed breakdown
        """
        # Convert to base64 if needed
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode("utf-8")
        else:
            image_base64 = image_data

        context_str = f"Context: {context}" if context else ""

        prompt = f"""You are a world-class food photographer and restaurant marketing expert.

Analyze this dish image for visual marketing effectiveness.

DISH: {dish_name}
{context_str}

Score each dimension from 0-10 and provide specific observations:

1. PLATING (0-10): Arrangement, composition, balance, use of negative space
2. COLOR VIBRANCY (0-10): Color saturation, contrast, visual appeal of ingredients
3. PORTION APPEAL (0-10): Does the portion look generous and appetizing?
4. LIGHTING (0-10): Quality of lighting, shadows, highlights
5. BACKGROUND (0-10): Clean, appropriate, enhances the dish
6. APPETITE APPEAL (0-10): Overall "I want to eat this" factor

RESPOND WITH VALID JSON:
{{
    "overall_score": 7.5,
    "plating_score": 8.0,
    "color_vibrancy": 7.0,
    "portion_appeal": 7.5,
    "lighting_quality": 6.5,
    "background_quality": 7.0,
    "appetite_appeal": 8.0,
    "strengths": [
        "Excellent color contrast between ingredients",
        "Clean white plate enhances presentation"
    ],
    "improvements": [
        "Add a garnish for height and visual interest",
        "Improve lighting to reduce shadows on left side"
    ],
    "professional_assessment": "Good amateur photography with room for improvement in lighting and composition"
}}

Be specific and actionable in your feedback."""

        try:
            response = await self._generate_multimodal(
                prompt=prompt,
                images=[image_base64],
                temperature=0.4,
                max_output_tokens=2048,
                feature="dish_visual_analysis",
                media_resolution="high",
            )

            result = self._parse_json_response(response)

            return VisualScore(
                overall_score=result.get("overall_score", 5.0),
                plating_score=result.get("plating_score", 5.0),
                color_vibrancy=result.get("color_vibrancy", 5.0),
                portion_appeal=result.get("portion_appeal", 5.0),
                lighting_quality=result.get("lighting_quality", 5.0),
                background_quality=result.get("background_quality", 5.0),
                appetite_appeal=result.get("appetite_appeal", 5.0),
                strengths=result.get("strengths", []),
                improvements=result.get("improvements", []),
            )

        except Exception as e:
            logger.error(f"Dish analysis failed: {e}")
            return VisualScore(
                overall_score=5.0,
                plating_score=5.0,
                color_vibrancy=5.0,
                portion_appeal=5.0,
                lighting_quality=5.0,
                background_quality=5.0,
                appetite_appeal=5.0,
                strengths=[],
                improvements=["Unable to analyze - please provide clearer image"],
            )

    async def compare_dishes(
        self,
        our_image: Union[str, bytes],
        competitor_image: Union[str, bytes],
        our_dish_name: str = "Our Dish",
        competitor_dish_name: str = "Competitor Dish",
        competitor_name: str = "Competitor",
    ) -> VisualComparison:
        """
        Compare our dish photo against a competitor's.

        Args:
            our_image: Our dish image (base64 or bytes)
            competitor_image: Competitor's dish image
            our_dish_name: Name of our dish
            competitor_dish_name: Name of competitor's dish
            competitor_name: Name of the competitor restaurant

        Returns:
            VisualComparison with detailed gap analysis
        """
        self._add_thought(
            step="Visual Comparison",
            reasoning=f"Comparing '{our_dish_name}' against '{competitor_dish_name}' from {competitor_name}",
            observations=[
                "Analyzing both images for visual quality",
                "Identifying dimensional gaps",
                "Generating improvement recommendations",
            ],
            confidence=0.85,
        )

        # Analyze both dishes
        our_score = await self.analyze_single_dish(
            our_image, our_dish_name, "our restaurant"
        )
        competitor_score = await self.analyze_single_dish(
            competitor_image, competitor_dish_name, f"competitor: {competitor_name}"
        )

        # Calculate gaps
        dimensions = [
            ("plating", our_score.plating_score, competitor_score.plating_score),
            (
                "color_vibrancy",
                our_score.color_vibrancy,
                competitor_score.color_vibrancy,
            ),
            (
                "portion_appeal",
                our_score.portion_appeal,
                competitor_score.portion_appeal,
            ),
            ("lighting", our_score.lighting_quality, competitor_score.lighting_quality),
            (
                "background",
                our_score.background_quality,
                competitor_score.background_quality,
            ),
            (
                "appetite_appeal",
                our_score.appetite_appeal,
                competitor_score.appetite_appeal,
            ),
        ]

        gap_analysis = {}
        winning = []
        losing = []

        for dim_name, our_val, comp_val in dimensions:
            gap = our_val - comp_val
            gap_analysis[dim_name] = round(gap, 2)
            if gap > 0.5:
                winning.append(dim_name)
            elif gap < -0.5:
                losing.append(dim_name)

        # Generate recommendations based on gaps
        recommendations = []
        if "lighting" in losing:
            recommendations.append(
                "Invest in better lighting equipment or shooting location"
            )
        if "plating" in losing:
            recommendations.append("Work with chef to improve plating techniques")
        if "color_vibrancy" in losing:
            recommendations.append(
                "Use fresher ingredients or adjust camera settings for saturation"
            )
        if "background" in losing:
            recommendations.append(
                "Use clean, consistent backgrounds for all food photography"
            )
        if "portion_appeal" in losing:
            recommendations.append(
                "Consider larger portions or better plate-to-food ratio"
            )

        # Determine priority
        overall_gap = our_score.overall_score - competitor_score.overall_score
        if overall_gap < -2:
            priority = "high"
        elif overall_gap < -0.5:
            priority = "medium"
        else:
            priority = "low"

        return VisualComparison(
            our_dish_name=our_dish_name,
            competitor_dish_name=competitor_dish_name,
            competitor_name=competitor_name,
            our_score=our_score,
            competitor_score=competitor_score,
            gap_analysis=gap_analysis,
            winning_dimensions=winning,
            losing_dimensions=losing,
            recommendations=recommendations,
            priority=priority,
        )

    async def analyze_visual_gaps(
        self,
        our_images: List[Dict[str, Any]],  # [{"image": bytes/str, "name": str}]
        competitor_images: List[
            Dict[str, Any]
        ],  # [{"image": bytes/str, "name": str, "competitor": str}]
        generate_report: bool = True,
    ) -> VisualGapReport:
        """
        Analyze visual gaps between our menu photos and competitors'.

        Args:
            our_images: List of our dish images with metadata
            competitor_images: List of competitor dish images with metadata
            generate_report: Whether to generate comprehensive report

        Returns:
            VisualGapReport with complete analysis
        """
        import time

        start_time = time.time()

        self.thought_traces = []
        comparisons = []
        our_scores = []
        competitor_scores = []

        self._add_thought(
            step="Initialization",
            reasoning="Starting visual gap analysis between our restaurant and competitors",
            observations=[
                f"Our images to analyze: {len(our_images)}",
                f"Competitor images to analyze: {len(competitor_images)}",
                "Will score each image and identify gaps",
            ],
            confidence=0.90,
        )

        # Analyze our images
        self._add_thought(
            step="Our Restaurant Analysis",
            reasoning="Analyzing our dish photography quality",
            observations=[
                "Scoring each dish for visual marketing effectiveness",
                "Identifying our visual strengths and weaknesses",
            ],
            confidence=0.85,
        )

        for item in our_images:
            score = await self.analyze_single_dish(
                item["image"], item.get("name", "Unknown"), "our restaurant"
            )
            our_scores.append(score)

        # Analyze competitor images
        self._add_thought(
            step="Competitor Analysis",
            reasoning="Analyzing competitor dish photography",
            observations=[
                "Benchmarking against competitor visual standards",
                "Identifying industry visual best practices",
            ],
            confidence=0.85,
        )

        for item in competitor_images:
            score = await self.analyze_single_dish(
                item["image"],
                item.get("name", "Unknown"),
                f"competitor: {item.get('competitor', 'Unknown')}",
            )
            competitor_scores.append(score)

        # Calculate averages
        our_avg = (
            sum(s.overall_score for s in our_scores) / len(our_scores)
            if our_scores
            else 5.0
        )
        comp_avg = (
            sum(s.overall_score for s in competitor_scores) / len(competitor_scores)
            if competitor_scores
            else 5.0
        )
        overall_gap = our_avg - comp_avg

        # Aggregate strengths and weaknesses
        all_our_strengths = []
        all_our_weaknesses = []

        for score in our_scores:
            all_our_strengths.extend(score.strengths)
            all_our_weaknesses.extend(score.improvements)

        # Deduplicate and count frequency
        strength_counts = {}
        for s in all_our_strengths:
            strength_counts[s] = strength_counts.get(s, 0) + 1

        weakness_counts = {}
        for w in all_our_weaknesses:
            weakness_counts[w] = weakness_counts.get(w, 0) + 1

        # Get top items
        top_strengths = sorted(
            strength_counts.keys(), key=lambda x: -strength_counts[x]
        )[:5]
        top_weaknesses = sorted(
            weakness_counts.keys(), key=lambda x: -weakness_counts[x]
        )[:5]

        # Generate priority improvements
        priority_improvements = []
        if overall_gap < 0:
            if any("lighting" in w.lower() for w in top_weaknesses):
                priority_improvements.append(
                    {
                        "area": "Lighting",
                        "impact": "high",
                        "recommendation": "Upgrade to professional lighting setup or shoot near windows",
                        "estimated_improvement": "+1.5 visual score",
                    }
                )
            if any(
                "plating" in w.lower() or "arrangement" in w.lower()
                for w in top_weaknesses
            ):
                priority_improvements.append(
                    {
                        "area": "Plating",
                        "impact": "high",
                        "recommendation": "Conduct plating training session with kitchen staff",
                        "estimated_improvement": "+1.0 visual score",
                    }
                )

        # Quick wins
        quick_wins = [
            "Clean camera lens before every photo session",
            "Use white plates for better food contrast",
            "Shoot from 45-degree angle for most dishes",
            "Add fresh herb garnishes for color pop",
            "Ensure consistent background across all photos",
        ]

        self._add_thought(
            step="Report Generation",
            reasoning=f"Visual gap analysis complete. Our avg: {our_avg:.1f}, Competitors avg: {comp_avg:.1f}",
            observations=[
                f"Overall gap: {overall_gap:+.1f} points",
                f"Key strengths: {len(top_strengths)} identified",
                f"Priority improvements: {len(priority_improvements)} recommended",
            ],
            confidence=0.88,
        )

        processing_time = int((time.time() - start_time) * 1000)

        return VisualGapReport(
            our_average_score=round(our_avg, 2),
            competitor_average_score=round(comp_avg, 2),
            overall_gap=round(overall_gap, 2),
            comparisons=comparisons,
            our_visual_strengths=top_strengths,
            our_visual_weaknesses=top_weaknesses,
            priority_improvements=priority_improvements,
            quick_wins=quick_wins,
            thought_traces=self.thought_traces,
            processing_time_ms=processing_time,
        )

    async def generate_visual_recommendations(
        self,
        gap_report: VisualGapReport,
    ) -> Dict[str, Any]:
        """
        Generate detailed recommendations based on gap analysis.

        Uses Gemini to synthesize insights and create actionable plan.
        """
        prompt = f"""You are a restaurant marketing consultant specializing in visual branding.

Based on this visual gap analysis, create a detailed improvement plan:

OUR VISUAL PERFORMANCE:
- Average Score: {gap_report.our_average_score}/10
- Gap vs Competitors: {gap_report.overall_gap:+.1f}
- Strengths: {', '.join(gap_report.our_visual_strengths[:3])}
- Weaknesses: {', '.join(gap_report.our_visual_weaknesses[:3])}

Create a 30-day visual improvement plan with:

1. IMMEDIATE ACTIONS (Days 1-7)
   - Quick fixes that can be implemented today
   - No-cost improvements

2. SHORT-TERM INVESTMENTS (Days 8-21)
   - Equipment or training needed
   - Estimated costs

3. ONGOING BEST PRACTICES
   - Standard procedures for food photography
   - Quality control checklist

RESPOND WITH VALID JSON:
{{
    "executive_summary": "One paragraph summary of visual brand status and priority actions",
    "immediate_actions": [
        {{
            "action": "Specific action",
            "impact": "Expected improvement",
            "cost": "$0",
            "time": "30 minutes"
        }}
    ],
    "short_term_investments": [
        {{
            "investment": "What to buy/do",
            "cost_range": "$50-100",
            "expected_roi": "Visual score improvement",
            "timeline": "Days 8-14"
        }}
    ],
    "photography_checklist": [
        "Always clean the plate edges before shooting",
        "Use natural light when possible"
    ],
    "projected_improvement": {{
        "current_score": {gap_report.our_average_score},
        "30_day_target": 8.0,
        "confidence": 0.85
    }}
}}"""

        try:
            response = await self._generate_content(
                prompt=prompt,
                temperature=0.6,
                max_output_tokens=4096,
                feature="visual_recommendations",
            )

            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return {
                "executive_summary": "Unable to generate recommendations",
                "error": str(e),
            }
