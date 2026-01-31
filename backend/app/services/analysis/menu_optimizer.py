"""
Menu Optimizer Service for MenuPilot.
Provides AI-powered price and margin optimization recommendations.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OptimizationAction(str, Enum):
    """Recommended actions for menu items."""

    INCREASE_PRICE = "increase_price"
    DECREASE_PRICE = "decrease_price"
    PROMOTE = "promote"
    REMOVE = "remove"
    BUNDLE = "bundle"
    REPOSITION = "reposition"
    MAINTAIN = "maintain"


class PriorityLevel(str, Enum):
    """Priority level for recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ItemOptimization:
    """Optimization recommendation for a single menu item."""

    item_name: str
    current_price: float
    suggested_price: Optional[float]
    current_margin: Optional[float]
    suggested_margin: Optional[float]
    action: OptimizationAction
    priority: PriorityLevel
    reasoning: str
    expected_impact: str
    rotation_score: float  # 0-1, based on sales frequency
    margin_score: float  # 0-1, based on profit margin
    combined_score: float  # Weighted combination
    bcg_category: Optional[str] = None


@dataclass
class CategoryOptimization:
    """Optimization summary for a category."""

    category: str
    item_count: int
    avg_margin: float
    avg_rotation: float
    total_revenue: float
    recommendations: List[str]


@dataclass
class MenuOptimizationReport:
    """Complete menu optimization report."""

    session_id: str
    generated_at: str
    item_optimizations: List[ItemOptimization]
    category_summaries: List[CategoryOptimization]
    quick_wins: List[Dict[str, Any]]
    revenue_opportunity: float
    margin_improvement_potential: float
    items_to_promote: List[str]
    items_to_review: List[str]
    items_to_remove: List[str]
    price_adjustments: List[Dict[str, Any]]
    ai_insights: List[str]
    thought_process: str


class MenuOptimizer:
    """
    AI-powered menu optimization engine.
    Analyzes price, margin, and rotation to provide actionable recommendations.
    """

    # Thresholds for classification
    HIGH_MARGIN_THRESHOLD = 0.65  # 65% margin
    LOW_MARGIN_THRESHOLD = 0.40  # 40% margin
    HIGH_ROTATION_PERCENTILE = 75
    LOW_ROTATION_PERCENTILE = 25

    # Price elasticity assumptions
    PRICE_INCREASE_DEMAND_DROP = 0.15  # 15% demand drop per 10% price increase
    PRICE_DECREASE_DEMAND_BOOST = 0.20  # 20% demand boost per 10% price decrease

    def __init__(self):
        self.settings = get_settings()

    async def analyze(
        self,
        sales_df: pd.DataFrame,
        menu_items: List[Dict],
        session_id: str,
        column_mapping: Optional[Dict] = None,
        bcg_results: Optional[Dict] = None,
    ) -> MenuOptimizationReport:
        """
        Analyze menu for optimization opportunities.

        Args:
            sales_df: DataFrame with sales data
            menu_items: List of menu item dictionaries
            session_id: Current session ID
            column_mapping: Mapping of column names
            bcg_results: Optional BCG classification results
        """
        logger.info(f"Starting menu optimization for session {session_id}")

        # Default column mapping
        if column_mapping is None:
            column_mapping = {
                "item_name": "item_name",
                "quantity": "quantity",
                "revenue": "revenue",
                "cost": "cost",
                "price": "price",
                "category": "category",
                "date": "date",
            }

        # Calculate item metrics
        item_metrics = self._calculate_item_metrics(sales_df, column_mapping)

        # Merge with menu items for additional info
        item_metrics = self._merge_with_menu(item_metrics, menu_items)

        # Add BCG categories if available
        if bcg_results:
            item_metrics = self._add_bcg_categories(item_metrics, bcg_results)

        # Generate item optimizations
        item_optimizations = self._generate_item_optimizations(item_metrics)

        # Generate category summaries
        category_summaries = self._generate_category_summaries(
            item_metrics, column_mapping
        )

        # Identify quick wins
        quick_wins = self._identify_quick_wins(item_optimizations)

        # Calculate opportunity metrics
        revenue_opp = self._calculate_revenue_opportunity(item_optimizations)
        margin_opp = self._calculate_margin_opportunity(item_optimizations)

        # Generate AI insights
        insights = await self._generate_ai_insights(
            item_optimizations, category_summaries
        )

        # Categorize items by action
        items_to_promote = [
            o.item_name
            for o in item_optimizations
            if o.action == OptimizationAction.PROMOTE
        ]
        items_to_review = [
            o.item_name
            for o in item_optimizations
            if o.action in [OptimizationAction.REPOSITION, OptimizationAction.BUNDLE]
        ]
        items_to_remove = [
            o.item_name
            for o in item_optimizations
            if o.action == OptimizationAction.REMOVE
        ]

        # Get price adjustments
        price_adjustments = [
            {
                "item": o.item_name,
                "current": o.current_price,
                "suggested": o.suggested_price,
                "change_pct": (
                    round(
                        (o.suggested_price - o.current_price) / o.current_price * 100, 1
                    )
                    if o.suggested_price
                    else 0
                ),
            }
            for o in item_optimizations
            if o.suggested_price and o.suggested_price != o.current_price
        ]

        # Generate thought process
        thought_process = self._generate_thought_process(
            item_metrics, item_optimizations
        )

        return MenuOptimizationReport(
            session_id=session_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            item_optimizations=item_optimizations,
            category_summaries=category_summaries,
            quick_wins=quick_wins,
            revenue_opportunity=revenue_opp,
            margin_improvement_potential=margin_opp,
            items_to_promote=items_to_promote,
            items_to_review=items_to_review,
            items_to_remove=items_to_remove,
            price_adjustments=price_adjustments,
            ai_insights=insights,
            thought_process=thought_process,
        )

    def _calculate_item_metrics(self, df: pd.DataFrame, col_map: Dict) -> pd.DataFrame:
        """Calculate key metrics for each item."""
        item_col = col_map.get("item_name", "item_name")
        qty_col = col_map.get("quantity", "quantity")
        rev_col = col_map.get("revenue", "revenue")
        cost_col = col_map.get("cost")

        # Group by item
        metrics = (
            df.groupby(item_col).agg({qty_col: "sum", rev_col: "sum"}).reset_index()
        )

        metrics.columns = ["item_name", "total_quantity", "total_revenue"]

        # Calculate average price
        metrics["avg_price"] = metrics["total_revenue"] / metrics["total_quantity"]

        # Calculate rotation score (percentile rank)
        metrics["rotation_score"] = metrics["total_quantity"].rank(pct=True)

        # Calculate revenue contribution
        total_rev = metrics["total_revenue"].sum()
        metrics["revenue_contribution"] = metrics["total_revenue"] / total_rev

        # Calculate margin if cost data available
        if cost_col and cost_col in df.columns:
            cost_agg = df.groupby(item_col)[cost_col].sum().reset_index()
            cost_agg.columns = ["item_name", "total_cost"]
            metrics = metrics.merge(cost_agg, on="item_name", how="left")
            metrics["margin"] = (
                metrics["total_revenue"] - metrics["total_cost"]
            ) / metrics["total_revenue"]
            metrics["margin_score"] = metrics["margin"].rank(pct=True)
        else:
            # Estimate margin based on industry averages
            metrics["margin"] = 0.60  # Default 60% margin assumption
            metrics["margin_score"] = 0.5

        # Combined score (weighted)
        metrics["combined_score"] = (
            metrics["rotation_score"] * 0.4
            + metrics["margin_score"] * 0.4
            + metrics["revenue_contribution"] * 0.2
        )

        return metrics

    def _merge_with_menu(
        self, metrics: pd.DataFrame, menu_items: List[Dict]
    ) -> pd.DataFrame:
        """Merge metrics with menu item information."""
        if not menu_items:
            return metrics

        menu_df = pd.DataFrame(menu_items)

        # Try to merge on name
        if "name" in menu_df.columns:
            menu_df = menu_df.rename(columns={"name": "item_name"})

        if "item_name" in menu_df.columns:
            # Keep only relevant columns
            keep_cols = ["item_name"]
            if "price" in menu_df.columns:
                keep_cols.append("price")
            if "category" in menu_df.columns:
                keep_cols.append("category")
            if "description" in menu_df.columns:
                keep_cols.append("description")

            menu_df = menu_df[keep_cols]
            metrics = metrics.merge(menu_df, on="item_name", how="left")

        return metrics

    def _add_bcg_categories(
        self, metrics: pd.DataFrame, bcg_results: Dict
    ) -> pd.DataFrame:
        """Add BCG categories to metrics."""
        if "items" not in bcg_results:
            return metrics

        bcg_map = {
            item["name"]: item.get("category", "UNKNOWN")
            for item in bcg_results["items"]
        }
        metrics["bcg_category"] = metrics["item_name"].map(bcg_map)

        return metrics

    def _generate_item_optimizations(
        self, metrics: pd.DataFrame
    ) -> List[ItemOptimization]:
        """Generate optimization recommendations for each item."""
        optimizations = []

        # Calculate thresholds
        rotation_high = metrics["rotation_score"].quantile(0.75)
        rotation_low = metrics["rotation_score"].quantile(0.25)

        for _, row in metrics.iterrows():
            action, priority, reasoning, expected_impact, suggested_price = (
                self._determine_action(row, rotation_high, rotation_low)
            )

            opt = ItemOptimization(
                item_name=row["item_name"],
                current_price=round(row.get("price", row["avg_price"]), 2),
                suggested_price=suggested_price,
                current_margin=(
                    round(row.get("margin", 0.6), 2) if "margin" in row else None
                ),
                suggested_margin=None,
                action=action,
                priority=priority,
                reasoning=reasoning,
                expected_impact=expected_impact,
                rotation_score=round(row["rotation_score"], 2),
                margin_score=round(row.get("margin_score", 0.5), 2),
                combined_score=round(row["combined_score"], 2),
                bcg_category=row.get("bcg_category"),
            )
            optimizations.append(opt)

        # Sort by priority and combined score
        priority_order = {
            PriorityLevel.CRITICAL: 0,
            PriorityLevel.HIGH: 1,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 3,
        }
        optimizations.sort(
            key=lambda x: (priority_order[x.priority], -x.combined_score)
        )

        return optimizations

    def _determine_action(
        self, row: pd.Series, rotation_high: float, rotation_low: float
    ) -> tuple:
        """Determine optimization action based on metrics."""
        rotation = row["rotation_score"]
        margin = row.get("margin", 0.6)
        margin_score = row.get("margin_score", 0.5)
        current_price = row.get("price", row["avg_price"])
        bcg = row.get("bcg_category", "")

        suggested_price = None

        # High margin, high rotation = STAR - maintain or slight price increase
        if margin > self.HIGH_MARGIN_THRESHOLD and rotation > rotation_high:
            suggested_price = round(current_price * 1.05, 2)  # 5% increase
            return (
                OptimizationAction.INCREASE_PRICE,
                PriorityLevel.MEDIUM,
                f"Star performer with {margin:.0%} margin and high rotation. Price increase potential.",
                "Expected 3-5% revenue increase with minimal volume impact",
                suggested_price,
            )

        # High margin, low rotation = premium item underperforming
        if margin > self.HIGH_MARGIN_THRESHOLD and rotation < rotation_low:
            return (
                OptimizationAction.PROMOTE,
                PriorityLevel.HIGH,
                f"High margin item ({margin:.0%}) with low visibility. Marketing opportunity.",
                "Promotion could increase volume 20-30% without margin sacrifice",
                None,
            )

        # Low margin, high rotation = volume driver, potential price increase
        if margin < self.LOW_MARGIN_THRESHOLD and rotation > rotation_high:
            suggested_price = round(current_price * 1.10, 2)  # 10% increase
            return (
                OptimizationAction.INCREASE_PRICE,
                PriorityLevel.CRITICAL,
                f"High-volume item with thin margin ({margin:.0%}). Critical for profitability.",
                "10% price increase could significantly improve overall margins",
                suggested_price,
            )

        # Low margin, low rotation = candidate for removal
        if margin < self.LOW_MARGIN_THRESHOLD and rotation < rotation_low:
            return (
                OptimizationAction.REMOVE,
                PriorityLevel.HIGH,
                f"Low margin ({margin:.0%}) and low sales. Consider removing from menu.",
                "Removal frees kitchen capacity and simplifies operations",
                None,
            )

        # Medium performers - various strategies
        if rotation < rotation_low:
            # Low rotation, medium margin - try bundling
            return (
                OptimizationAction.BUNDLE,
                PriorityLevel.MEDIUM,
                "Moderate margin but low sales. Bundle with popular items.",
                "Bundling could increase sales 15-25%",
                None,
            )

        if margin_score < 0.4:
            # Low margin score - reposition or recipe change
            return (
                OptimizationAction.REPOSITION,
                PriorityLevel.MEDIUM,
                "Margin below average. Consider portion adjustment or supplier negotiation.",
                "Cost optimization could improve margin 5-10 points",
                None,
            )

        # Default: maintain
        return (
            OptimizationAction.MAINTAIN,
            PriorityLevel.LOW,
            "Item performing within acceptable parameters.",
            "Monitor for changes in customer preference",
            None,
        )

    def _generate_category_summaries(
        self, metrics: pd.DataFrame, col_map: Dict
    ) -> List[CategoryOptimization]:
        """Generate category-level summaries."""
        summaries = []

        if "category" not in metrics.columns:
            return summaries

        for category in metrics["category"].dropna().unique():
            cat_data = metrics[metrics["category"] == category]

            avg_margin = cat_data["margin"].mean() if "margin" in cat_data else 0.6
            avg_rotation = cat_data["rotation_score"].mean()
            total_rev = cat_data["total_revenue"].sum()

            # Generate recommendations
            recs = []
            if avg_margin < 0.5:
                recs.append(
                    f"Category margin ({avg_margin:.0%}) below target. Review pricing."
                )
            if avg_rotation < 0.4:
                recs.append(
                    "Low category rotation. Consider menu placement or promotion."
                )
            if len(cat_data) > 10:
                recs.append("Large category. Consider consolidating similar items.")

            summaries.append(
                CategoryOptimization(
                    category=category,
                    item_count=len(cat_data),
                    avg_margin=round(avg_margin, 2),
                    avg_rotation=round(avg_rotation, 2),
                    total_revenue=round(total_rev, 2),
                    recommendations=recs,
                )
            )

        return summaries

    def _identify_quick_wins(
        self, optimizations: List[ItemOptimization]
    ) -> List[Dict[str, Any]]:
        """Identify quick wins - high impact, easy implementation."""
        quick_wins = []

        # Price increases on high-volume items
        for opt in optimizations:
            if opt.action == OptimizationAction.INCREASE_PRICE and opt.priority in [
                PriorityLevel.CRITICAL,
                PriorityLevel.HIGH,
            ]:
                quick_wins.append(
                    {
                        "type": "price_increase",
                        "item": opt.item_name,
                        "action": f"Increase price from ${opt.current_price:.2f} to ${opt.suggested_price:.2f}",
                        "impact": opt.expected_impact,
                        "difficulty": "Easy",
                    }
                )

        # Items to remove
        removal_candidates = [
            opt for opt in optimizations if opt.action == OptimizationAction.REMOVE
        ]
        if removal_candidates:
            quick_wins.append(
                {
                    "type": "menu_simplification",
                    "items": [opt.item_name for opt in removal_candidates[:3]],
                    "action": "Remove underperforming items",
                    "impact": "Reduced complexity, improved kitchen efficiency",
                    "difficulty": "Easy",
                }
            )

        return quick_wins[:5]  # Top 5 quick wins

    def _calculate_revenue_opportunity(
        self, optimizations: List[ItemOptimization]
    ) -> float:
        """Calculate potential revenue opportunity from price changes."""
        opportunity = 0
        for opt in optimizations:
            if opt.suggested_price and opt.suggested_price > opt.current_price:
                # Assume 5% of current revenue as opportunity
                opportunity += opt.current_price * 0.05 * opt.rotation_score * 1000
        return round(opportunity, 2)

    def _calculate_margin_opportunity(
        self, optimizations: List[ItemOptimization]
    ) -> float:
        """Calculate potential margin improvement."""
        low_margin_items = [
            o for o in optimizations if o.current_margin and o.current_margin < 0.5
        ]
        if not low_margin_items:
            return 0

        # Assume 5% margin improvement on average
        avg_improvement = 0.05
        return round(len(low_margin_items) * avg_improvement * 100, 1)

    async def _generate_ai_insights(
        self,
        optimizations: List[ItemOptimization],
        categories: List[CategoryOptimization],
    ) -> List[str]:
        """Generate AI-powered insights using Gemini."""
        insights = []

        # Analyze patterns
        high_priority = [
            o
            for o in optimizations
            if o.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]
        ]
        if high_priority:
            insights.append(
                f"🎯 {len(high_priority)} items require immediate attention for pricing optimization"
            )

        # Category insights
        low_margin_cats = [c for c in categories if c.avg_margin < 0.5]
        if low_margin_cats:
            cat_names = ", ".join([c.category for c in low_margin_cats[:3]])
            insights.append(f"📊 Categories with margin opportunities: {cat_names}")

        # BCG alignment
        stars = [o for o in optimizations if o.bcg_category == "STAR"]
        if stars:
            insights.append(
                f"⭐ {len(stars)} Star items identified - protect these with strategic pricing"
            )

        dogs = [o for o in optimizations if o.bcg_category == "DOG"]
        if dogs:
            insights.append(
                f"🐕 {len(dogs)} Dog items may be candidates for menu removal"
            )

        # Price increase opportunities
        increase_items = [
            o for o in optimizations if o.action == OptimizationAction.INCREASE_PRICE
        ]
        if increase_items:
            avg_increase = (
                sum(
                    (o.suggested_price - o.current_price) / o.current_price
                    for o in increase_items
                    if o.suggested_price
                )
                / len(increase_items)
                * 100
            )
            insights.append(
                f"💰 Average recommended price increase: {avg_increase:.1f}%"
            )

        return insights

    def _generate_thought_process(
        self, metrics: pd.DataFrame, optimizations: List[ItemOptimization]
    ) -> str:
        """Generate transparent thought process."""
        return f"""
## Menu Optimization Analysis

### Data Summary
- Analyzed {len(metrics)} menu items
- Total revenue in dataset: ${metrics['total_revenue'].sum():,.2f}
- Average item margin: {metrics['margin'].mean():.1%}

### Methodology
1. Calculated rotation score (sales frequency percentile)
2. Calculated margin score (profit margin percentile)
3. Combined scores with revenue contribution weighting
4. Applied optimization matrix based on margin x rotation quadrants

### Key Findings
- High-priority items: {len([o for o in optimizations if o.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]])}
- Price increase candidates: {len([o for o in optimizations if o.action == OptimizationAction.INCREASE_PRICE])}
- Removal candidates: {len([o for o in optimizations if o.action == OptimizationAction.REMOVE])}
- Promotion opportunities: {len([o for o in optimizations if o.action == OptimizationAction.PROMOTE])}

### Confidence
Analysis based on available sales data. Recommendations should be validated with:
- Customer feedback
- Competitor pricing
- Seasonal factors
"""


# Singleton instance
menu_optimizer = MenuOptimizer()
