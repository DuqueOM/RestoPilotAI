"""
Menu Engineering Classifier - Kasavana & Smith Methodology (Professional Edition).

Professional adaptation of BCG Matrix for restaurant menu optimization.
Uses Popularity (mix %) and Contribution Margin (CM) as primary axes.

Quadrants:
- **Stars** (High Popularity, High CM): Promote and protect
- **Plowhorses** (High Popularity, Low CM): Improve margin or reposition
- **Puzzles** (Low Popularity, High CM): Promote to increase sales
- **Dogs** (Low Popularity, Low CM): Consider removal or redesign

Professional Standards Applied:
- Minimum volume thresholds for statistical reliability (≥5 sales per item)
- Food cost benchmarks (industry standard: 28-35%)
- Data quality scoring and confidence levels
- Category-level analysis (by product type: Drinks, Food, etc.)
- Financial impact estimates for recommendations
- Seasonality and promotional period warnings
- Period recommendations: 30-90 days for operational, 12+ months for strategic

Key Formulas (Kasavana & Smith, 1982):
- Popularity (%) = (Units Sold / Total Units) × 100
- Unit CM = Selling Price - Cost per Portion
- Total Contribution = Unit CM × Units Sold
- Food Cost (%) = (Cost / Price) × 100
- Popularity Threshold = (100% / n_items) × 0.70
- CM Threshold = Weighted average CM across all items

Reference: Kasavana, M. L., & Smith, D. I. (1982). Menu Engineering.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import get_settings
from loguru import logger


class MenuCategory(str, Enum):
    """Menu Engineering classifications (Kasavana & Smith)."""

    STAR = "star"
    PLOWHORSE = "plowhorse"
    PUZZLE = "puzzle"
    DOG = "dog"


class AnalysisPeriod(str, Enum):
    """Available analysis periods."""

    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    LAST_180_DAYS = "180d"
    LAST_365_DAYS = "365d"
    ALL_TIME = "all"


def get_period_days(period: AnalysisPeriod) -> Optional[int]:
    """Convert period enum to number of days."""
    mapping = {
        AnalysisPeriod.LAST_30_DAYS: 30,
        AnalysisPeriod.LAST_90_DAYS: 90,
        AnalysisPeriod.LAST_180_DAYS: 180,
        AnalysisPeriod.LAST_365_DAYS: 365,
        AnalysisPeriod.ALL_TIME: None,
    }
    return mapping.get(period)


def parse_date_flexible(date_val) -> Optional[datetime]:
    """Parse date from various formats including DD-MM-YY."""
    if date_val is None:
        return None
    if isinstance(date_val, datetime):
        return date_val
    if not isinstance(date_val, str):
        date_val = str(date_val)

    date_str = date_val.strip()

    # Try multiple date formats
    formats = [
        "%Y-%m-%d",  # YYYY-MM-DD (ISO) - most common after conversion
        "%d-%m-%y",  # DD-MM-YY (sample data format)
        "%d-%m-%Y",  # DD-MM-YYYY
        "%d/%m/%y",  # DD/MM/YY
        "%d/%m/%Y",  # DD/MM/YYYY
        "%m/%d/%Y",  # MM/DD/YYYY (US)
        "%Y/%m/%d",  # YYYY/MM/DD
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue

    # Try ISO format with timezone
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        pass

    return None


def filter_sales_by_period(
    sales_data: List[Dict[str, Any]], period: AnalysisPeriod
) -> Tuple[List[Dict[str, Any]], Optional[datetime], Optional[datetime]]:
    """
    Filter sales data to only include records within the specified period.

    Returns:
        Tuple of (filtered_sales, start_date, end_date)
    """
    if not sales_data:
        return [], None, None

    dated_sales = []
    for sale in sales_data:
        sale_date = sale.get("sale_date") or sale.get("date")
        if not sale_date:
            continue

        parsed_date = parse_date_flexible(sale_date)
        if parsed_date is None:
            continue

        dated_sales.append({**sale, "_parsed_date": parsed_date})

    if not dated_sales:
        return sales_data, None, None

    max_date = max(s["_parsed_date"] for s in dated_sales)
    min_date = min(s["_parsed_date"] for s in dated_sales)

    days = get_period_days(period)
    if days is None:
        return sales_data, min_date, max_date

    cutoff_date = max_date - timedelta(days=days)

    filtered = [
        {k: v for k, v in s.items() if k != "_parsed_date"}
        for s in dated_sales
        if s["_parsed_date"] >= cutoff_date
    ]

    if filtered:
        filtered_dates = [
            s["_parsed_date"] for s in dated_sales if s["_parsed_date"] >= cutoff_date
        ]
        return filtered, min(filtered_dates), max(filtered_dates)

    return [], cutoff_date, max_date


class MenuEngineeringClassifier:
    """
    Professional Menu Engineering Classifier (Kasavana & Smith).

    Key Metrics:
    1. **Popularity (Mix %)**: Percentage of total units sold
    2. **Contribution Margin (CM)**: Profit per portion (Price - Cost)
    3. **Total Contribution**: CM × Units Sold
    4. **Food Cost %**: Cost / Price × 100 (benchmark: 28-35%)

    Classification Rules (Kasavana & Smith, 1982):
    - Popularity threshold: 70% of expected popularity (1/n × 0.70)
    - CM threshold: Weighted average CM of all items

    Data Quality Standards:
    - Minimum 30 days of data recommended
    - Minimum 5 sales per item for reliable classification
    - Items below threshold flagged with low confidence
    """

    # Kasavana & Smith standard factors
    POPULARITY_FACTOR = 0.70

    # Professional benchmarks (industry standards)
    MIN_SALES_FOR_CONFIDENCE = 5  # Minimum sales for reliable analysis
    MIN_SALES_FOR_HIGH_CONFIDENCE = 15  # High confidence threshold
    MIN_DAYS_RECOMMENDED = 30  # Minimum data span for operational analysis
    MIN_DAYS_STRATEGIC = 90  # Recommended for strategic decisions

    # Food cost benchmarks (restaurant industry)
    FOOD_COST_TARGET_LOW = 0.28  # 28% - excellent
    FOOD_COST_TARGET_MID = 0.32  # 32% - good
    FOOD_COST_TARGET_HIGH = 0.35  # 35% - acceptable maximum
    FOOD_COST_CRITICAL = 0.40  # 40%+ - needs attention

    # Margin benchmarks
    MARGIN_EXCELLENT = 0.65  # 65%+ margin is excellent
    MARGIN_GOOD = 0.50  # 50-65% is good
    MARGIN_ACCEPTABLE = 0.40  # 40-50% is acceptable
    MARGIN_POOR = 0.30  # Below 30% is poor

    def __init__(self):
        self.settings = get_settings()

    async def analyze(
        self,
        menu_items: List[Dict[str, Any]],
        sales_data: List[Dict[str, Any]],
        period: AnalysisPeriod = AnalysisPeriod.LAST_30_DAYS,
    ) -> Dict[str, Any]:
        """
        Perform Menu Engineering analysis on the given data.

        Args:
            menu_items: List of menu items with name, price, cost
            sales_data: List of sales records with item_name, quantity, sale_date
            period: Analysis period filter

        Returns:
            Complete analysis results with classifications and metrics
        """
        logger.info(f"Starting Menu Engineering analysis for period: {period.value}")

        # Filter data by period
        filtered_sales, start_date, end_date = filter_sales_by_period(
            sales_data, period
        )

        if not filtered_sales:
            logger.warning("No sales data found for the specified period")
            return self._empty_result(period, start_date, end_date)

        logger.info(f"Analyzing {len(filtered_sales)} sales records")

        # Assess data quality (professional requirement)
        data_quality = self._assess_data_quality(filtered_sales, start_date, end_date)

        # Calculate item metrics
        item_metrics = self._calculate_item_metrics(menu_items, filtered_sales)

        if not item_metrics:
            return self._empty_result(period, start_date, end_date)

        # Calculate thresholds
        thresholds = self._calculate_thresholds(item_metrics)

        # Classify items
        classified_items = self._classify_items(item_metrics, thresholds)

        # Generate summary with professional insights
        summary = self._generate_summary(classified_items, thresholds)

        # Generate category-level analysis (by product category)
        category_analysis = self._analyze_by_product_category(classified_items)

        return {
            "period": period.value,
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
            },
            "total_records": len(filtered_sales),
            "items_analyzed": len(classified_items),
            "data_quality": data_quality,
            "thresholds": thresholds,
            "items": classified_items,
            "summary": summary,
            "category_analysis": category_analysis,
            "methodology": "Kasavana & Smith Menu Engineering",
        }

    def _assess_data_quality(
        self,
        sales_data: List[Dict[str, Any]],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> Dict[str, Any]:
        """
        Assess data quality for professional analysis reliability.

        Professional standards:
        - Minimum 30 days of data for operational decisions
        - Minimum 90 days for strategic decisions
        - Flag promotional periods and seasonality
        """
        warnings = []
        recommendations = []

        # Calculate data span
        days_span = 0
        if start_date and end_date:
            days_span = (end_date - start_date).days + 1

        # Data span assessment
        if days_span < self.MIN_DAYS_RECOMMENDED:
            warnings.append(
                f"⚠️ Only {days_span} days of data. Minimum recommended: {self.MIN_DAYS_RECOMMENDED} days "
                f"for reliable operational analysis."
            )
            recommendations.append(
                "Collect more historical data to improve analysis precision."
            )
        elif days_span < self.MIN_DAYS_STRATEGIC:
            warnings.append(
                f"📊 {days_span} days of data is adequate for operational analysis, "
                f"but {self.MIN_DAYS_STRATEGIC}+ days are recommended for strategic decisions."
            )

        # Check for potential seasonality (December, holiday periods)
        if start_date and end_date:
            months_covered = set()
            current = start_date
            while current <= end_date:
                months_covered.add(current.month)
                current = current + timedelta(days=28)

            holiday_months = {12, 1, 6}  # December, January, special dates
            if months_covered & holiday_months:
                warnings.append(
                    "🎄 Data includes holiday periods (Dec/Jan). "
                    "Consider separating high season vs normal analysis."
                )

        # Calculate unique items and transactions
        unique_items = len(
            set(s.get("item_name", "") for s in sales_data if s.get("item_name"))
        )
        unique_transactions = len(
            set(
                s.get("id_transaccion", s.get("transaction_id", "")) for s in sales_data
            )
        )

        # Volume assessment
        avg_sales_per_item = len(sales_data) / unique_items if unique_items > 0 else 0
        if avg_sales_per_item < self.MIN_SALES_FOR_CONFIDENCE:
            warnings.append(
                f"📉 Average of {avg_sales_per_item:.1f} records per item. "
                f"Some items may have low statistical reliability."
            )

        # Determine overall quality score
        quality_score = 100
        if days_span < self.MIN_DAYS_RECOMMENDED:
            quality_score -= 30
        elif days_span < self.MIN_DAYS_STRATEGIC:
            quality_score -= 10
        if avg_sales_per_item < self.MIN_SALES_FOR_CONFIDENCE:
            quality_score -= 20

        quality_level = (
            "high"
            if quality_score >= 80
            else "medium" if quality_score >= 60 else "low"
        )

        return {
            "quality_score": max(0, quality_score),
            "quality_level": quality_level,
            "days_span": days_span,
            "total_records": len(sales_data),
            "unique_items": unique_items,
            "unique_transactions": unique_transactions,
            "avg_sales_per_item": round(avg_sales_per_item, 1),
            "min_days_recommended": self.MIN_DAYS_RECOMMENDED,
            "min_days_strategic": self.MIN_DAYS_STRATEGIC,
            "warnings": warnings,
            "recommendations": recommendations,
        }

    def _calculate_item_metrics(
        self,
        menu_items: List[Dict[str, Any]],
        sales_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Calculate key metrics for each menu item."""

        # Build price and cost lookup from menu_items
        item_info = {}
        for item in menu_items:
            name = item.get("name", "").strip().lower()
            if name:
                item_info[name] = {
                    "price": float(item.get("price", 0) or 0),
                    "cost": float(item.get("cost", 0) or item.get("food_cost", 0) or 0),
                    "category": item.get("category", ""),
                    "original_name": item.get("name", ""),
                }

        # Aggregate sales by item
        sales_by_item: Dict[str, Dict[str, Any]] = {}

        for sale in sales_data:
            item_name = (
                (sale.get("item_name") or sale.get("product_name") or "")
                .strip()
                .lower()
            )
            # Support both 'quantity' and 'units_sold' column names
            quantity = int(sale.get("quantity") or sale.get("units_sold") or 1)

            # Get price and cost from sales record (per-line item data)
            sale_price = float(sale.get("price") or 0)
            sale_cost = float(sale.get("cost") or sale.get("food_cost") or 0)

            # Calculate revenue: if not provided, compute from price * quantity
            revenue = float(sale.get("revenue") or sale.get("total") or 0)
            if revenue == 0 and sale_price > 0:
                revenue = sale_price * quantity

            if not item_name:
                continue

            if item_name not in sales_by_item:
                info = item_info.get(item_name, {})
                # Prefer price/cost from menu_items, but use sale data as fallback
                sales_by_item[item_name] = {
                    "name": info.get("original_name", item_name),
                    "units_sold": 0,
                    "total_revenue": 0,
                    "price": info.get("price", 0) or sale_price,
                    "cost": info.get("cost", 0) or sale_cost,
                    "category": info.get("category") or sale.get("categoria", ""),
                    "_price_samples": [],
                    "_cost_samples": [],
                }

            # Accumulate price/cost samples for averaging
            if sale_price > 0:
                sales_by_item[item_name]["_price_samples"].append(sale_price)
            if sale_cost > 0:
                sales_by_item[item_name]["_cost_samples"].append(sale_cost)

            sales_by_item[item_name]["units_sold"] += quantity
            sales_by_item[item_name]["total_revenue"] += revenue

        # Calculate total units for popularity %
        total_units = sum(item["units_sold"] for item in sales_by_item.values())

        if total_units == 0:
            return []

        # Calculate metrics for each item
        item_metrics = []

        for item_key, data in sales_by_item.items():
            units = data["units_sold"]

            # Calculate average price from samples, or use stored price, or infer from revenue
            price_samples = data.get("_price_samples", [])
            cost_samples = data.get("_cost_samples", [])

            if price_samples:
                price = sum(price_samples) / len(price_samples)
            elif data["price"] > 0:
                price = data["price"]
            elif units > 0 and data["total_revenue"] > 0:
                price = data["total_revenue"] / units
            else:
                price = 0

            # Calculate average cost from samples, or use stored cost
            if cost_samples:
                cost = sum(cost_samples) / len(cost_samples)
            else:
                cost = data["cost"]

            # Contribution Margin (CM) = Price - Cost
            cm_unitario = price - cost

            # Popularity (Mix %) = Units Sold / Total Units × 100
            popularity_pct = (units / total_units) * 100

            # Total Contribution = CM × Units Sold
            total_contribution = cm_unitario * units

            # Margin percentage (professional metric)
            margin_pct = (cm_unitario / price * 100) if price > 0 else 0

            # Food Cost % (industry benchmark: 28-35%)
            food_cost_pct = (cost / price * 100) if price > 0 else 0

            # Food cost rating based on industry benchmarks
            if food_cost_pct <= self.FOOD_COST_TARGET_LOW * 100:
                food_cost_rating = "excellent"
            elif food_cost_pct <= self.FOOD_COST_TARGET_MID * 100:
                food_cost_rating = "good"
            elif food_cost_pct <= self.FOOD_COST_TARGET_HIGH * 100:
                food_cost_rating = "acceptable"
            elif food_cost_pct <= self.FOOD_COST_CRITICAL * 100:
                food_cost_rating = "high"
            else:
                food_cost_rating = "critical"

            # Confidence score based on sample size
            if units >= self.MIN_SALES_FOR_HIGH_CONFIDENCE:
                confidence = "high"
                confidence_score = 1.0
            elif units >= self.MIN_SALES_FOR_CONFIDENCE:
                confidence = "medium"
                confidence_score = 0.7
            else:
                confidence = "low"
                confidence_score = 0.4

            item_metrics.append(
                {
                    "name": data["name"],
                    "category": data["category"],
                    "units_sold": units,
                    "price": round(price, 2),
                    "cost": round(cost, 2),
                    "cm_unitario": round(cm_unitario, 2),
                    "popularity_pct": round(popularity_pct, 2),
                    "total_contribution": round(total_contribution, 2),
                    "margin_pct": round(margin_pct, 1),
                    "total_revenue": round(data["total_revenue"], 2),
                    # Professional metrics
                    "food_cost_pct": round(food_cost_pct, 1),
                    "food_cost_rating": food_cost_rating,
                    "confidence": confidence,
                    "confidence_score": confidence_score,
                }
            )

        return item_metrics

    def _calculate_thresholds(
        self, item_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate classification thresholds."""

        n_items = len(item_metrics)
        if n_items == 0:
            return {"popularity_threshold": 0, "cm_threshold": 0}

        # Kasavana & Smith popularity threshold:
        # Expected popularity = 100% / n_items
        # Threshold = Expected × 0.70 (70% factor)
        expected_popularity = 100 / n_items
        popularity_threshold = expected_popularity * self.POPULARITY_FACTOR

        # CM threshold = Average CM of all items (weighted by units)
        total_units = sum(item["units_sold"] for item in item_metrics)
        if total_units > 0:
            weighted_cm = (
                sum(item["cm_unitario"] * item["units_sold"] for item in item_metrics)
                / total_units
            )
        else:
            weighted_cm = sum(item["cm_unitario"] for item in item_metrics) / n_items

        # Also calculate simple average CM for reference
        simple_avg_cm = sum(item["cm_unitario"] for item in item_metrics) / n_items

        return {
            "popularity_threshold": round(popularity_threshold, 2),
            "cm_threshold": round(weighted_cm, 2),
            "cm_average_simple": round(simple_avg_cm, 2),
            "expected_popularity": round(expected_popularity, 2),
            "n_items": n_items,
            "total_units": total_units,
        }

    def _classify_items(
        self,
        item_metrics: List[Dict[str, Any]],
        thresholds: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Classify each item into Menu Engineering quadrants."""

        pop_threshold = thresholds["popularity_threshold"]
        cm_threshold = thresholds["cm_threshold"]

        classified = []

        for item in item_metrics:
            pop = item["popularity_pct"]
            cm = item["cm_unitario"]

            # Classification logic
            high_popularity = pop >= pop_threshold
            high_cm = cm >= cm_threshold

            if high_popularity and high_cm:
                category = MenuCategory.STAR
                strategy = self._get_star_strategy(item)
            elif high_popularity and not high_cm:
                category = MenuCategory.PLOWHORSE
                strategy = self._get_plowhorse_strategy(item, cm_threshold)
            elif not high_popularity and high_cm:
                category = MenuCategory.PUZZLE
                strategy = self._get_puzzle_strategy(item)
            else:
                category = MenuCategory.DOG
                strategy = self._get_dog_strategy(item)

            classified.append(
                {
                    **item,
                    "product_category": item.get(
                        "category", ""
                    ),  # Preserve original (Vino, Cerveza, etc.)
                    "category": category.value,  # BCG category (star, dog, etc.)
                    "category_label": self._get_category_label(category),
                    "high_popularity": high_popularity,
                    "high_cm": high_cm,
                    "strategy": strategy,
                }
            )

        # Sort by total contribution (most valuable first)
        classified.sort(key=lambda x: x["total_contribution"], reverse=True)

        return classified

    def _get_category_label(self, category: MenuCategory) -> str:
        """Get display label for category."""
        labels = {
            MenuCategory.STAR: "⭐ Star",
            MenuCategory.PLOWHORSE: "🐴 Plowhorse",
            MenuCategory.PUZZLE: "🧩 Puzzle",
            MenuCategory.DOG: "🐕 Dog",
        }
        return labels.get(category, category.value)

    def _get_star_strategy(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for Star items (High Pop, High CM) - Professional recommendations."""
        # Calculate potential financial impact
        current_revenue = item["total_revenue"]
        potential_increase = current_revenue * 0.10  # 10% price increase potential

        return {
            "action": "MAINTAIN AND PROTECT",
            "priority": "high",
            "confidence_note": f"Confidence: {item.get('confidence', 'N/A')}",
            "recommendations": [
                "Maintain prominent location on the menu (top right zone)",
                "Do not modify the recipe without prior impact analysis",
                "Use as a flagship dish to attract customers",
                f"Consider 5-10% price increase (potential: +${potential_increase:,.0f})",
                "Ensure constant availability - no stockouts",
                "Document standard recipe for consistency",
            ],
            "pricing": "Maintain or increase slightly (5-10%)",
            "menu_position": "High visual impact zone (top right quadrant)",
            "financial_impact": {
                "current_contribution": round(item["total_contribution"], 2),
                "price_increase_potential": round(potential_increase, 2),
                "risk_level": "low",
            },
        }

    def _get_plowhorse_strategy(
        self, item: Dict[str, Any], cm_target: float
    ) -> Dict[str, Any]:
        """Strategy for Plowhorse items (High Pop, Low CM) - Professional recommendations."""
        cm_gap = cm_target - item["cm_unitario"]
        units = item["units_sold"]

        # Calculate financial impact of reaching CM target
        potential_gain = cm_gap * units
        price_increase_pct = (cm_gap / item["price"] * 100) if item["price"] > 0 else 0

        return {
            "action": "IMPROVE PROFITABILITY",
            "priority": "medium-high",
            "confidence_note": f"Confidence: {item.get('confidence', 'N/A')}",
            "recommendations": [
                f"Increase price by ${cm_gap:,.0f} (+{price_increase_pct:.1f}%) to reach target CM",
                "Reduce portion slightly (5-10%) without harming perceived value",
                "Negotiate better supplier costs (target: -10%)",
                "Substitute expensive ingredients with equally high-quality alternatives",
                "Offer as a bundle with high-CM items to increase average ticket",
                f"Potential impact: +${potential_gain:,.0f} in monthly contribution",
            ],
            "pricing": f"Increase by ${cm_gap:,.0f} gradually in 2-3 steps",
            "menu_position": "Keep visible, but not as the main highlight",
            "cm_gap": round(cm_gap, 2),
            "financial_impact": {
                "current_contribution": round(item["total_contribution"], 2),
                "target_contribution": round(
                    item["total_contribution"] + potential_gain, 2
                ),
                "potential_gain": round(potential_gain, 2),
                "price_increase_needed": f"+{price_increase_pct:.1f}%",
                "risk_level": "medium" if price_increase_pct > 15 else "low",
            },
        }

    def _get_puzzle_strategy(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for Puzzle items (Low Pop, High CM) - Professional recommendations."""
        # Calculate potential if popularity doubles
        potential_contribution = item["total_contribution"] * 2

        return {
            "action": "PROMOTE ACTIVELY",
            "priority": "medium",
            "confidence_note": f"Confidence: {item.get('confidence', 'N/A')}",
            "recommendations": [
                "Improve description: highlight premium ingredients and preparation",
                "Train servers with an upselling script",
                "Offer as 'Chef's Special' or 'Recommendation of the Day'",
                "Include a professional, appetizing photo on the menu",
                "Launch promotion: 15% off the first week",
                "Place next to popular dishes to increase visibility",
            ],
            "pricing": "Keep current price - margin is already strong",
            "menu_position": "Move to a higher-visibility zone (next to Stars)",
            "financial_impact": {
                "current_contribution": round(item["total_contribution"], 2),
                "potential_if_doubles": round(potential_contribution, 2),
                "opportunity_cost": round(
                    potential_contribution - item["total_contribution"], 2
                ),
                "risk_level": "low",
            },
        }

    def _get_dog_strategy(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy for Dog items (Low Pop, Low CM) - Professional recommendations."""
        return {
            "action": "EVALUATE ELIMINATION",
            "priority": "low",
            "confidence_note": f"Confidence: {item.get('confidence', 'N/A')}",
            "recommendations": [
                "Analyze if it has strategic value (variety, VIP customers, complement)",
                "Consider complete redesign: new recipe, presentation, name",
                "Increase price 20-30% - if it doesn't sell, confirm elimination",
                "Monitor for 30 additional days before deciding",
                "If eliminated: free up space for new dish or Puzzle promotion",
                "Evaluate cost of specific ingredients not used in other dishes",
            ],
            "pricing": "Increase significantly (+20-30%) or eliminate",
            "menu_position": "Low impact zone or eliminate completely",
            "financial_impact": {
                "current_contribution": round(item["total_contribution"], 2),
                "opportunity_cost": "Occupied space could generate more with another item",
                "elimination_impact": "Minimal if replaced with better performing item",
                "risk_level": "low on elimination",
            },
        }

    def _generate_summary(
        self,
        classified_items: List[Dict[str, Any]],
        thresholds: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analysis summary.

        Includes:
        - Category counts and distributions
        - Financial metrics (revenue, contribution, margins)
        - Portfolio health score
        - Top performers
        - Items needing attention
        """

        # Count by category
        category_counts = {cat.value: 0 for cat in MenuCategory}
        category_revenue = {cat.value: 0.0 for cat in MenuCategory}
        category_contribution = {cat.value: 0.0 for cat in MenuCategory}
        category_units = {cat.value: 0 for cat in MenuCategory}

        total_revenue = 0.0
        total_contribution = 0.0
        total_units = 0
        total_cost = 0.0

        for item in classified_items:
            cat = item["category"]
            category_counts[cat] += 1
            category_revenue[cat] += item["total_revenue"]
            category_contribution[cat] += item["total_contribution"]
            category_units[cat] += item["units_sold"]

            total_revenue += item["total_revenue"]
            total_contribution += item["total_contribution"]
            total_units += item["units_sold"]
            total_cost += item["cost"] * item["units_sold"]

        # Calculate percentages
        categories_summary = []
        for cat in MenuCategory:
            count = category_counts[cat.value]
            revenue = category_revenue[cat.value]
            contribution = category_contribution[cat.value]
            units = category_units[cat.value]

            categories_summary.append(
                {
                    "category": cat.value,
                    "label": self._get_category_label(cat),
                    "count": count,
                    "pct_items": (
                        round(count / len(classified_items) * 100, 1)
                        if classified_items
                        else 0
                    ),
                    "total_revenue": round(revenue, 2),
                    "pct_revenue": (
                        round(revenue / total_revenue * 100, 1)
                        if total_revenue > 0
                        else 0
                    ),
                    "total_contribution": round(contribution, 2),
                    "pct_contribution": (
                        round(contribution / total_contribution * 100, 1)
                        if total_contribution > 0
                        else 0
                    ),
                    "units_sold": units,
                    "pct_units": (
                        round(units / total_units * 100, 1) if total_units > 0 else 0
                    ),
                }
            )

        # Top performers
        top_by_contribution = sorted(
            classified_items, key=lambda x: x["total_contribution"], reverse=True
        )[:5]

        top_by_popularity = sorted(
            classified_items, key=lambda x: x["popularity_pct"], reverse=True
        )[:5]

        # Items needing attention (Dogs)
        dogs = [
            item
            for item in classified_items
            if item["category"] == MenuCategory.DOG.value
        ]

        # Calculate portfolio health score (0-1 scale)
        # Based on BCG distribution: Stars and Plowhorses are good, Dogs are bad
        # Puzzles are neutral (potential)
        star_count = category_counts[MenuCategory.STAR.value]
        plowhorse_count = category_counts[MenuCategory.PLOWHORSE.value]
        puzzle_count = category_counts[MenuCategory.PUZZLE.value]
        dog_count = category_counts[MenuCategory.DOG.value]

        total_items = len(classified_items)
        if total_items > 0:
            # Weighted score: Stars (1.0), Plowhorses (0.8), Puzzles (0.5), Dogs (0.0)
            portfolio_health_score = (
                (star_count * 1.0)
                + (plowhorse_count * 0.8)
                + (puzzle_count * 0.5)
                + (dog_count * 0.0)
            ) / total_items
        else:
            portfolio_health_score = 0.0

        # Financial metrics
        avg_revenue_per_item = total_revenue / total_items if total_items > 0 else 0
        profit_margin_pct = (
            (total_contribution / total_revenue * 100) if total_revenue > 0 else 0
        )
        food_cost_pct = (total_cost / total_revenue * 100) if total_revenue > 0 else 0

        return {
            "total_items": len(classified_items),
            "total_revenue": round(total_revenue, 2),
            "total_contribution": round(total_contribution, 2),
            "total_cost": round(total_cost, 2),
            "total_units": total_units,
            "avg_cm": (
                round(total_contribution / total_units, 2) if total_units > 0 else 0
            ),
            "avg_revenue_per_item": round(avg_revenue_per_item, 2),
            "profit_margin_pct": round(profit_margin_pct, 1),
            "food_cost_pct": round(food_cost_pct, 1),
            "portfolio_health_score": round(portfolio_health_score, 2),
            "counts": {
                "star": star_count,
                "cash_cow": plowhorse_count,  # Frontend uses cash_cow
                "plowhorse": plowhorse_count,
                "question_mark": puzzle_count,  # Frontend uses question_mark
                "puzzle": puzzle_count,
                "dog": dog_count,
            },
            "categories": categories_summary,
            "top_by_contribution": [
                {"name": item["name"], "contribution": item["total_contribution"]}
                for item in top_by_contribution
            ],
            "top_by_popularity": [
                {"name": item["name"], "popularity_pct": item["popularity_pct"]}
                for item in top_by_popularity
            ],
            "attention_needed": len(dogs),
            "dogs_list": [item["name"] for item in dogs],
        }

    def _empty_result(
        self,
        period: AnalysisPeriod,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "period": period.value,
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
            },
            "total_records": 0,
            "items_analyzed": 0,
            "thresholds": {},
            "items": [],
            "summary": {
                "total_items": 0,
                "categories": [],
                "attention_needed": 0,
            },
            "methodology": "Kasavana & Smith Menu Engineering",
            "error": "No sales data for the selected period",
        }

    def _analyze_by_product_category(
        self, classified_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze items grouped by product category (Drinks, Food, etc.).

        Professional requirement: separate analysis by category allows for
        more refined decisions since different categories have different
        cost structures and margin expectations.
        """
        if not classified_items:
            return {"categories": [], "insights": []}

        # Group by product category (Wine, Beer, Cocktails, etc.)
        by_product_cat: Dict[str, List[Dict[str, Any]]] = {}
        for item in classified_items:
            prod_cat = item.get("product_category", "Uncategorized") or "Uncategorized"
            if prod_cat not in by_product_cat:
                by_product_cat[prod_cat] = []
            by_product_cat[prod_cat].append(item)

        # Analyze each product category
        category_analysis = []
        insights = []

        for cat_name, items in sorted(by_product_cat.items(), key=lambda x: -len(x[1])):
            total_revenue = sum(i["total_revenue"] for i in items)
            total_contribution = sum(i["total_contribution"] for i in items)
            total_units = sum(i["units_sold"] for i in items)

            # Average metrics
            avg_price = sum(i["price"] for i in items) / len(items) if items else 0
            avg_cost = sum(i["cost"] for i in items) / len(items) if items else 0
            avg_margin = (
                sum(i["margin_pct"] for i in items) / len(items) if items else 0
            )
            avg_food_cost = (
                sum(i.get("food_cost_pct", 0) for i in items) / len(items)
                if items
                else 0
            )

            # BCG distribution within category
            bcg_dist = {
                "star": len([i for i in items if i["category"] == "star"]),
                "plowhorse": len([i for i in items if i["category"] == "plowhorse"]),
                "puzzle": len([i for i in items if i["category"] == "puzzle"]),
                "dog": len([i for i in items if i["category"] == "dog"]),
            }

            # Determine category health
            star_pct = bcg_dist["star"] / len(items) * 100 if items else 0
            dog_pct = bcg_dist["dog"] / len(items) * 100 if items else 0

            if star_pct >= 20 and dog_pct <= 30:
                health = "healthy"
                health_emoji = "✅"
            elif dog_pct > 50:
                health = "critical"
                health_emoji = "🔴"
            else:
                health = "moderate"
                health_emoji = "🟡"

            category_analysis.append(
                {
                    "category_name": cat_name,
                    "item_count": len(items),
                    "total_revenue": round(total_revenue, 2),
                    "total_contribution": round(total_contribution, 2),
                    "total_units": total_units,
                    "avg_price": round(avg_price, 2),
                    "avg_cost": round(avg_cost, 2),
                    "avg_margin_pct": round(avg_margin, 1),
                    "avg_food_cost_pct": round(avg_food_cost, 1),
                    "bcg_distribution": bcg_dist,
                    "health": health,
                    "health_emoji": health_emoji,
                    "top_item": (
                        max(items, key=lambda x: x["total_contribution"])["name"]
                        if items
                        else None
                    ),
                }
            )

            # Generate category-specific insights
            if dog_pct > 40:
                insights.append(
                    f"⚠️ '{cat_name}' has {dog_pct:.0f}% of items classified as Dogs. "
                    f"Consider restructuring this category's offering."
                )
            if avg_food_cost > 40:
                insights.append(
                    f"📊 '{cat_name}' has an average food cost of {avg_food_cost:.1f}% "
                    f"(above the 35% benchmark). Review ingredient costs."
                )
            if star_pct >= 30:
                insights.append(
                    f"⭐ '{cat_name}' is a strong category with {star_pct:.0f}% Stars. "
                    f"Maintain and leverage this line."
                )

        # Sort by contribution
        category_analysis.sort(key=lambda x: x["total_contribution"], reverse=True)

        return {
            "product_categories": category_analysis,
            "total_categories": len(category_analysis),
            "insights": insights,
            "top_category": (
                category_analysis[0]["category_name"] if category_analysis else None
            ),
        }
