"""
BCG Matrix Classifier - Product portfolio analysis.

Implements the Boston Consulting Group growth-share matrix for
restaurant menu item classification.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from loguru import logger

from app.config import get_settings
from app.services.gemini_agent import GeminiAgent


class BCGClass(str, Enum):
    """BCG Matrix classifications."""

    STAR = "star"
    CASH_COW = "cash_cow"
    QUESTION_MARK = "question_mark"
    DOG = "dog"


class BCGClassifier:
    """
    Classifies menu items according to the BCG Matrix.

    Uses a combination of:
    1. Rule-based classification using sales metrics
    2. AI-enhanced insights from Gemini

    BCG Matrix Quadrants:
    - Star: High market share, High growth (invest)
    - Cash Cow: High market share, Low growth (milk)
    - Question Mark: Low market share, High growth (analyze)
    - Dog: Low market share, Low growth (divest/reposition)
    """

    def __init__(self, agent: GeminiAgent):
        self.agent = agent
        self.settings = get_settings()

    async def classify_products(
        self,
        menu_items: List[Dict[str, Any]],
        sales_data: List[Dict[str, Any]],
        image_scores: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Classify all menu items according to BCG matrix.

        Args:
            menu_items: List of menu items with price and cost
            sales_data: Historical sales records
            image_scores: Optional image attractiveness scores by item name

        Returns:
            Complete BCG analysis with classifications and insights
        """

        logger.info(
            f"Classifying {len(menu_items)} items with {len(sales_data)} sales records"
        )

        # Calculate metrics for each item
        item_metrics = self._calculate_item_metrics(menu_items, sales_data)

        # Add image scores if available
        if image_scores:
            for item in item_metrics:
                item["image_score"] = image_scores.get(item["name"], 0.5)

        # Calculate thresholds based on percentiles
        thresholds = self._calculate_thresholds(item_metrics)

        # Apply BCG classification rules
        classifications = []
        for item in item_metrics:
            classification = self._classify_item(item, thresholds)
            classifications.append(classification)

        # Get AI-enhanced insights
        ai_insights = await self._get_ai_insights(classifications, item_metrics)

        # Calculate portfolio summary
        summary = self._calculate_portfolio_summary(classifications)

        return {
            "classifications": classifications,
            "thresholds": thresholds,
            "summary": summary,
            "ai_insights": ai_insights,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_item_metrics(
        self, menu_items: List[Dict[str, Any]], sales_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate sales metrics for each menu item."""

        # Aggregate sales by item
        sales_by_item = {}
        for record in sales_data:
            item_name = record.get("item_name")
            if not item_name:
                continue

            if item_name not in sales_by_item:
                sales_by_item[item_name] = {"units": [], "dates": [], "revenues": []}

            sales_by_item[item_name]["units"].append(record.get("units_sold", 0))
            sales_by_item[item_name]["dates"].append(record.get("sale_date"))
            sales_by_item[item_name]["revenues"].append(record.get("revenue", 0))

        # Calculate total units for market share calculation
        total_units = sum(sum(s["units"]) for s in sales_by_item.values())

        # Calculate metrics for each item
        metrics = []
        for item in menu_items:
            item_name = item.get("name")
            sales = sales_by_item.get(
                item_name, {"units": [], "dates": [], "revenues": []}
            )

            total_item_units = sum(sales["units"]) if sales["units"] else 0

            # Market share (relative)
            market_share = total_item_units / total_units if total_units > 0 else 0

            # Growth rate (compare last period vs first period)
            growth_rate = self._calculate_growth_rate(sales["units"], sales["dates"])

            # Margin
            price = item.get("price", 0)
            cost = item.get("cost", price * 0.3)  # Default 30% cost if not provided
            margin = (price - cost) / price if price > 0 else 0

            # Popularity score (normalized units)
            max_units = max(
                (sum(s["units"]) for s in sales_by_item.values()), default=1
            )
            popularity = total_item_units / max_units if max_units > 0 else 0

            metrics.append(
                {
                    "name": item_name,
                    "price": price,
                    "cost": cost,
                    "total_units": total_item_units,
                    "total_revenue": sum(sales["revenues"]) if sales["revenues"] else 0,
                    "market_share": market_share,
                    "growth_rate": growth_rate,
                    "margin": margin,
                    "popularity_score": popularity,
                    "data_points": len(sales["units"]),
                }
            )

        return metrics

    def _calculate_growth_rate(self, units: List[int], dates: List[Any]) -> float:
        """Calculate growth rate from sales data."""

        if len(units) < 2:
            return 0.0

        # Sort by date if dates available
        if dates and all(dates):
            try:
                sorted_data = sorted(zip(dates, units), key=lambda x: x[0])
                units = [u for _, u in sorted_data]
            except (TypeError, ValueError):
                pass

        # Split into first and second half
        mid = len(units) // 2
        if mid == 0:
            return 0.0

        first_half_avg = sum(units[:mid]) / mid
        second_half_avg = sum(units[mid:]) / (len(units) - mid)

        if first_half_avg == 0:
            return 1.0 if second_half_avg > 0 else 0.0

        growth = (second_half_avg - first_half_avg) / first_half_avg
        return round(growth, 3)

    def _calculate_thresholds(
        self, item_metrics: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate percentile-based thresholds for classification."""

        market_shares = [m["market_share"] for m in item_metrics]
        growth_rates = [m["growth_rate"] for m in item_metrics]

        high_share_pct = self.settings.bcg_high_share_percentile
        high_growth_pct = self.settings.bcg_high_growth_percentile

        return {
            "high_share_threshold": (
                np.percentile(market_shares, high_share_pct) if market_shares else 0.1
            ),
            "high_growth_threshold": (
                np.percentile(growth_rates, high_growth_pct) if growth_rates else 0.05
            ),
            "share_percentile_used": high_share_pct,
            "growth_percentile_used": high_growth_pct,
        }

    def _classify_item(
        self, item: Dict[str, Any], thresholds: Dict[str, float]
    ) -> Dict[str, Any]:
        """Apply BCG classification rules to a single item."""

        high_share = item["market_share"] >= thresholds["high_share_threshold"]
        high_growth = item["growth_rate"] >= thresholds["high_growth_threshold"]

        if high_share and high_growth:
            bcg_class = BCGClass.STAR
            label = "Star"
            strategy = "Invest - These are your winners. Increase marketing spend and ensure supply."
        elif high_share and not high_growth:
            bcg_class = BCGClass.CASH_COW
            label = "Cash Cow"
            strategy = "Maintain - Generate steady profits with minimal investment."
        elif not high_share and high_growth:
            bcg_class = BCGClass.QUESTION_MARK
            label = "Question Mark"
            strategy = "Analyze - Potential stars. Consider promotion or repositioning."
        else:
            bcg_class = BCGClass.DOG
            label = "Dog"
            strategy = "Review - Consider removing, repricing, or repositioning."

        # Calculate overall score (weighted combination)
        overall_score = (
            item["market_share"] * 0.3
            + max(0, item["growth_rate"]) * 0.25  # Penalize negative growth
            + item["margin"] * 0.25
            + item.get("image_score", 0.5) * 0.1
            + item["popularity_score"] * 0.1
        )

        return {
            "name": item["name"],
            "bcg_class": bcg_class.value,
            "bcg_label": label,
            "market_share": round(item["market_share"], 4),
            "growth_rate": round(item["growth_rate"], 4),
            "margin": round(item["margin"], 4),
            "popularity_score": round(item["popularity_score"], 4),
            "image_score": item.get("image_score"),
            "overall_score": round(overall_score, 4),
            "strategy": strategy,
            "bcg_x": item["market_share"],  # For visualization
            "bcg_y": item["growth_rate"],  # For visualization
        }

    async def _get_ai_insights(
        self, classifications: List[Dict[str, Any]], metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get AI-enhanced strategic insights."""

        # Prepare summary for Gemini
        summary_data = {
            "classifications": classifications,
            "total_items": len(classifications),
            "stars": [c["name"] for c in classifications if c["bcg_class"] == "star"],
            "cash_cows": [
                c["name"] for c in classifications if c["bcg_class"] == "cash_cow"
            ],
            "question_marks": [
                c["name"] for c in classifications if c["bcg_class"] == "question_mark"
            ],
            "dogs": [c["name"] for c in classifications if c["bcg_class"] == "dog"],
        }

        insights = await self.agent.generate_bcg_insights(classifications, summary_data)

        return insights

    def _calculate_portfolio_summary(
        self, classifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate portfolio-level summary statistics."""

        counts = {"star": 0, "cash_cow": 0, "question_mark": 0, "dog": 0}

        for c in classifications:
            counts[c["bcg_class"]] += 1

        total = len(classifications)

        # Portfolio health score (higher is better)
        # Ideal: balanced with more stars/cash cows than dogs
        if total > 0:
            health_score = (
                counts["star"] * 1.0
                + counts["cash_cow"] * 0.8
                + counts["question_mark"] * 0.5
                + counts["dog"] * 0.2
            ) / total
        else:
            health_score = 0

        return {
            "total_items": total,
            "counts": counts,
            "percentages": {
                k: round(v / total * 100, 1) if total > 0 else 0
                for k, v in counts.items()
            },
            "portfolio_health_score": round(health_score, 2),
            "is_balanced": counts["star"] > 0 and counts["cash_cow"] > 0,
            "needs_attention": counts["dog"] > total * 0.3,
        }
