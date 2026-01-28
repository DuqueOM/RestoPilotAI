"""
Campaign Generator Service - AI-powered marketing campaign creation.

Generates highly personalized, actionable marketing campaigns based on:
- BCG Matrix classification and gross profit analysis
- Business context provided by the user
- Industry best practices for restaurant marketing
- Specific product characteristics and performance data
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger

from app.services.gemini_agent import GeminiAgent


class CampaignGenerator:
    """
    Generates highly specific, personalized marketing campaign proposals using Gemini AI.

    Key differentiators from generic campaign generators:
    - Uses BCG classification with gross profit data for targeting
    - Provides specific, actionable recommendations (not generic advice)
    - Includes ready-to-use copy for social media, email, and in-store
    - Calculates expected ROI based on historical data
    - Considers business context (type of restaurant, target audience, location)

    Campaign Types by BCG Classification:
    - **Star products**: Amplification & premium positioning campaigns
    - **Question Marks**: Discovery, trial, and viral potential campaigns
    - **Cash Cows**: Loyalty programs & strategic bundling
    - **Dogs**: Repositioning, limited-time, or graceful exit strategies
    """

    def __init__(self, agent: GeminiAgent):
        self.agent = agent
        self.business_context = None

    async def generate_campaigns(
        self,
        bcg_analysis: Dict[str, Any],
        menu_items: List[Dict[str, Any]],
        num_campaigns: int = 3,
        duration_days: int = 14,
        channels: Optional[List[str]] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate marketing campaign proposals.

        Args:
            bcg_analysis: BCG classification results
            menu_items: Menu items with details
            num_campaigns: Number of campaigns to generate
            duration_days: Campaign duration
            channels: Marketing channels to use
            constraints: Budget and other constraints
        """

        logger.info(f"Generating {num_campaigns} campaigns")

        channels = channels or ["social_media", "in_store", "email"]
        start_date = date.today() + timedelta(days=3)

        # Generate campaigns using Gemini
        ai_campaigns = await self.agent.generate_campaigns(
            bcg_analysis, num_campaigns, constraints
        )

        # Post-process and enrich campaigns
        processed_campaigns = []
        for idx, campaign in enumerate(ai_campaigns[:num_campaigns]):
            processed = self._process_campaign(
                campaign, idx, start_date, duration_days, channels
            )
            processed_campaigns.append(processed)

        # Generate thought signature for the process
        thought_signature = await self.agent.create_thought_signature(
            "Generate marketing campaigns based on BCG analysis",
            {
                "num_campaigns": num_campaigns,
                "bcg_summary": bcg_analysis.get("summary", {}),
            },
        )

        return {
            "campaigns": processed_campaigns,
            "generation_timestamp": datetime.utcnow().isoformat(),
            "thought_signature": thought_signature,
            "total_generated": len(processed_campaigns),
        }

    def _process_campaign(
        self,
        raw_campaign: Dict[str, Any],
        index: int,
        start_date: date,
        duration_days: int,
        channels: List[str],
    ) -> Dict[str, Any]:
        """Process and validate a raw campaign from AI."""

        end_date = start_date + timedelta(days=duration_days)

        # Generate posting schedule
        schedule = self._generate_schedule(channels, duration_days)

        # Extract or generate key components
        campaign = {
            "id": index + 1,
            "title": raw_campaign.get("title", f"Campaign {index + 1}"),
            "objective": raw_campaign.get("objective", "Increase sales"),
            "target_audience": raw_campaign.get(
                "target_audience", "Restaurant customers"
            ),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration_days": duration_days,
            "channels": raw_campaign.get("channels", channels),
            "schedule": schedule,
            "key_messages": raw_campaign.get("key_messages", [])[:5],
            "promotional_items": raw_campaign.get("promotional_items", []),
            "discount_strategy": raw_campaign.get("discount_strategy"),
            "social_post_copy": raw_campaign.get("social_post_copy", ""),
            "image_prompt": self._generate_image_prompt(raw_campaign),
            "expected_uplift_percent": raw_campaign.get(
                "expected_uplift_percent", 10.0
            ),
            "expected_revenue_increase": raw_campaign.get("expected_revenue_increase"),
            "confidence_level": raw_campaign.get("confidence_level", 0.7),
            "rationale": raw_campaign.get("rationale", ""),
            "why_these_items": raw_campaign.get(
                "why_these_items", "Selected based on BCG analysis"
            ),
            "why_this_timing": raw_campaign.get(
                "why_this_timing", "Optimal timing for target audience"
            ),
        }

        return campaign

    def _generate_schedule(
        self, channels: List[str], duration_days: int
    ) -> Dict[str, List[str]]:
        """Generate posting schedule by day of week."""

        schedule = {
            "Monday": [],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": [],
            "Sunday": [],
        }

        if "social_media" in channels:
            schedule["Monday"].extend(["12:00", "18:00"])
            schedule["Wednesday"].extend(["12:00", "19:00"])
            schedule["Friday"].extend(["11:00", "17:00"])
            schedule["Saturday"].extend(["10:00", "14:00"])
            schedule["Sunday"].extend(["11:00", "16:00"])

        if "email" in channels:
            schedule["Tuesday"].append("09:00")
            schedule["Thursday"].append("09:00")

        if "in_store" in channels:
            for day in schedule:
                schedule[day].append("all_day")

        return schedule

    def _generate_image_prompt(self, campaign: Dict[str, Any]) -> str:
        """Generate a prompt for promotional image creation."""

        items = campaign.get("promotional_items", [])
        title = campaign.get("title", "Restaurant Promotion")

        items_str = ", ".join(items[:3]) if items else "delicious dishes"

        return f"""Professional restaurant promotional image for "{title}".
Feature: {items_str}.
Style: Modern, appetizing food photography with warm lighting.
Include: Clean typography space for promotional text.
Mood: Inviting, delicious, premium quality.
Colors: Warm tones, food-appropriate palette."""


async def generate_promotional_content(
    agent: GeminiAgent, campaign: Dict[str, Any], menu_items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate additional promotional content for a campaign."""

    prompt = f"""Generate promotional content for this restaurant campaign:

Campaign: {campaign.get('title')}
Objective: {campaign.get('objective')}
Featured Items: {campaign.get('promotional_items')}
Target Audience: {campaign.get('target_audience')}

Generate:
1. Three variations of social media posts (Instagram/Facebook)
2. Email subject line and preview text
3. In-store signage copy (short, impactful)
4. Hashtags to use

Keep the tone friendly, appetizing, and action-oriented."""

    response = await agent._call_gemini(prompt)

    try:
        return {"content": response.text, "generated_at": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return {"error": str(e)}
