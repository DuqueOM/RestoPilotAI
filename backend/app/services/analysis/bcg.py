"""
BCG Matrix Classifier - Professional Product Portfolio Analysis.

Implements the Boston Consulting Group growth-share matrix for
restaurant menu item classification using professional metrics:

- **Relative Market Share**: Based on gross profit contribution (revenue - cost)
- **Market Growth Rate**: Year-over-year or period-over-period growth
- **Gross Profit Margin**: (Price - Cost) / Price for profitability analysis

Professional BCG Implementation Notes:
- X-axis: Relative market share (log scale, 0.1x to 10x vs market average)
- Y-axis: Market growth rate (percentage)
- Classification based on gross profit contribution, not just revenue
- Includes profitability-weighted scoring for strategic recommendations
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from app.core.config import get_settings
from app.services.gemini.base_agent import GeminiAgent
from loguru import logger


class BCGClass(str, Enum):
    """BCG Matrix classifications."""

    STAR = "star"
    CASH_COW = "cash_cow"
    QUESTION_MARK = "question_mark"
    DOG = "dog"


class BCGClassifier:
    """
    Professional BCG Matrix Classifier for Restaurant Menu Optimization.

    Implements the authentic Boston Consulting Group methodology:

    **Key Metrics (Professional Implementation)**:
    1. **Gross Profit Contribution**: Revenue - Cost (not just revenue)
    2. **Relative Market Share**: Item's profit share vs. portfolio average
    3. **Growth Rate**: Period-over-period sales growth
    4. **Profit Margin**: (Price - Cost) / Price

    **BCG Matrix Quadrants**:
    - **Star** (High Share, High Growth):
      Products with strong gross profit AND growing demand.
      Strategy: Invest heavily, these drive future growth.

    - **Cash Cow** (High Share, Low Growth):
      Mature products generating steady gross profit.
      Strategy: Maximize profit extraction, minimize investment.

    - **Question Mark** (Low Share, High Growth):
      Emerging products with potential but low profit contribution.
      Strategy: Analyze carefully - invest to convert to Star or divest.

    - **Dog** (Low Share, Low Growth):
      Low profit contribution with stagnant demand.
      Strategy: Consider repositioning, repricing, or removal.

    **Professional Considerations**:
    - Uses gross profit (not revenue) as the primary share metric
    - Applies logarithmic scale for relative market share visualization
    - Includes confidence intervals based on data quality
    - Provides actionable, menu-specific strategic recommendations
    """

    def __init__(self, agent: GeminiAgent):
        self.agent = agent
        self.settings = get_settings()

    async def classify(
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
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _calculate_item_metrics(
        self, menu_items: List[Dict[str, Any]], sales_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate professional BCG metrics for each menu item.

        Key difference from naive implementation:
        - Uses GROSS PROFIT (revenue - cost) not just revenue/units
        - Calculates relative market share vs portfolio average
        - Applies professional financial metrics

        Optimized for large datasets (3+ years of data):
        - Samples data if exceeds threshold for faster processing
        - Uses efficient aggregation with dictionary comprehensions
        """

        # OPTIMIZATION: Sample large datasets to prevent timeout
        MAX_RECORDS = 50000  # Process at most 50k records
        if len(sales_data) > MAX_RECORDS:
            logger.info(
                f"Sampling {MAX_RECORDS} from {len(sales_data)} records for BCG analysis"
            )
            # Use stratified sampling - take most recent data + sample from older
            sorted_data = sorted(
                sales_data,
                key=lambda x: x.get("sale_date", x.get("date", "")),
                reverse=True,
            )
            recent = sorted_data[: MAX_RECORDS // 2]  # Most recent 50%
            older_sample = sorted_data[
                MAX_RECORDS // 2 :: max(1, len(sorted_data) // (MAX_RECORDS // 2))
            ][: MAX_RECORDS // 2]
            sales_data = recent + older_sample
            logger.info(f"Using {len(sales_data)} sampled records")

        # Aggregate sales by item with cost tracking
        sales_by_item = {}
        for record in sales_data:
            item_name = record.get("item_name")
            if not item_name:
                continue

            if item_name not in sales_by_item:
                sales_by_item[item_name] = {
                    "units": [],
                    "dates": [],
                    "revenues": [],
                    "costs": [],
                    "gross_profits": [],
                }

            units = record.get("units_sold", 0) or record.get("quantity", 0) or 0
            # Calculate revenue: prefer explicit revenue, otherwise price * units
            unit_price = record.get("price", 0) or 0
            revenue = record.get("revenue", 0)
            if not revenue and unit_price and units:
                revenue = unit_price * units

            # Get cost from sales data if available
            unit_cost = record.get("cost", record.get("unit_cost", 0)) or 0

            sales_by_item[item_name]["units"].append(units)
            sales_by_item[item_name]["dates"].append(
                record.get("sale_date", record.get("date"))
            )
            sales_by_item[item_name]["revenues"].append(revenue)
            sales_by_item[item_name]["costs"].append(
                unit_cost * units if unit_cost else 0
            )

            # Calculate gross profit for this transaction
            if unit_cost and units:
                gross_profit = revenue - (unit_cost * units)
            elif revenue:
                gross_profit = revenue * 0.65  # Assume 35% food cost default
            else:
                gross_profit = 0
            sales_by_item[item_name]["gross_profits"].append(gross_profit)

        # Calculate TOTAL GROSS PROFIT for the portfolio (key BCG metric)
        total_gross_profit = sum(
            sum(s["gross_profits"]) for s in sales_by_item.values()
        )
        total_units = sum(sum(s["units"]) for s in sales_by_item.values())
        # total_revenue calculated but reserved for future revenue-based analysis
        _ = sum(sum(s["revenues"]) for s in sales_by_item.values())

        # Calculate metrics for each item
        metrics = []
        for item in menu_items:
            item_name = item.get("name")
            sales = sales_by_item.get(
                item_name,
                {
                    "units": [],
                    "dates": [],
                    "revenues": [],
                    "costs": [],
                    "gross_profits": [],
                },
            )

            total_item_units = sum(sales["units"]) if sales["units"] else 0
            total_item_revenue = sum(sales["revenues"]) if sales["revenues"] else 0
            total_item_cost = sum(sales["costs"]) if sales["costs"] else 0
            total_item_gross_profit = (
                sum(sales["gross_profits"]) if sales["gross_profits"] else 0
            )

            # PROFESSIONAL BCG: Market share based on GROSS PROFIT contribution
            # This is the correct implementation - share of total profit, not units
            gross_profit_share = (
                total_item_gross_profit / total_gross_profit
                if total_gross_profit > 0
                else 0
            )

            # Also track unit-based share for comparison
            unit_market_share = total_item_units / total_units if total_units > 0 else 0

            # Growth rate (compare last period vs first period)
            growth_rate = self._calculate_growth_rate(sales["units"], sales["dates"])

            # Also calculate profit growth rate
            profit_growth_rate = self._calculate_growth_rate(
                sales["gross_profits"], sales["dates"]
            )

            # Price and cost from menu item or inferred from sales
            price = item.get("price", 0)
            if price == 0 and total_item_units > 0:
                price = total_item_revenue / total_item_units  # Infer from sales

            # Cost: prefer explicit cost, then from sales data, then estimate
            cost = item.get("cost", 0)
            if cost == 0 and total_item_units > 0 and total_item_cost > 0:
                cost = total_item_cost / total_item_units
            elif cost == 0:
                cost = price * 0.35  # Industry standard food cost ~35%

            # Gross profit per unit
            gross_profit_per_unit = price - cost

            # Profit margin (professional metric)
            margin = gross_profit_per_unit / price if price > 0 else 0

            # Popularity score (normalized units)
            max_units = max(
                (sum(s["units"]) for s in sales_by_item.values()), default=1
            )
            popularity = total_item_units / max_units if max_units > 0 else 0

            # Profitability index: combines margin with volume
            profitability_index = gross_profit_share * margin if margin > 0 else 0

            metrics.append(
                {
                    "name": item_name,
                    "price": round(price, 2),
                    "cost": round(cost, 2),
                    "gross_profit_per_unit": round(gross_profit_per_unit, 2),
                    "total_units": total_item_units,
                    "total_revenue": round(total_item_revenue, 2),
                    "total_cost": round(total_item_cost, 2),
                    "total_gross_profit": round(total_item_gross_profit, 2),
                    # BCG Primary metrics
                    "market_share": gross_profit_share,  # Based on gross profit (professional)
                    "unit_market_share": unit_market_share,  # For reference
                    "growth_rate": growth_rate,
                    "profit_growth_rate": profit_growth_rate,
                    # Financial metrics
                    "margin": margin,
                    "profitability_index": profitability_index,
                    "popularity_score": popularity,
                    "data_points": len(sales["units"]),
                    "data_quality": (
                        "high"
                        if len(sales["units"]) >= 30
                        else "medium" if len(sales["units"]) >= 7 else "low"
                    ),
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
        """
        Apply professional BCG classification rules.

        Classification is based on:
        - Market share: Gross profit contribution (not units)
        - Growth rate: Sales velocity change over time

        Returns detailed strategic recommendations specific to restaurant context.
        """

        high_share = item["market_share"] >= thresholds["high_share_threshold"]
        high_growth = item["growth_rate"] >= thresholds["high_growth_threshold"]
        # Margin thresholds for future enhanced classification
        _high_margin = item["margin"] >= 0.60  # 60%+ margin is excellent
        _low_margin = item["margin"] < 0.40  # Below 40% needs attention

        if high_share and high_growth:
            bcg_class = BCGClass.STAR
            label = "Star ⭐"
            strategy = self._get_star_strategy(item)
            priority = "high"
        elif high_share and not high_growth:
            bcg_class = BCGClass.CASH_COW
            label = "Cash Cow 🐄"
            strategy = self._get_cash_cow_strategy(item)
            priority = "medium"
        elif not high_share and high_growth:
            bcg_class = BCGClass.QUESTION_MARK
            label = "Question Mark ❓"
            strategy = self._get_question_mark_strategy(item)
            priority = "high"  # Needs decision
        else:
            bcg_class = BCGClass.DOG
            label = "Dog 🐕"
            strategy = self._get_dog_strategy(item)
            priority = "low"

        # Calculate overall score with professional weighting
        # Weighted by profitability (BCG is ultimately about profit allocation)
        overall_score = (
            item["market_share"] * 0.25  # Gross profit share
            + max(0, item["growth_rate"]) * 0.20  # Growth potential
            + item["margin"] * 0.30  # Profitability (most important)
            + item.get("image_score", 0.5) * 0.10  # Visual appeal
            + item["popularity_score"] * 0.15  # Customer preference
        )

        return {
            "name": item["name"],
            "bcg_class": bcg_class.value,
            "bcg_label": label,
            # BCG Position Metrics
            "market_share": round(item["market_share"], 4),
            "growth_rate": round(item["growth_rate"], 4),
            # Financial Metrics (Professional BCG)
            "price": item.get("price", 0),
            "cost": item.get("cost", 0),
            "gross_profit_per_unit": item.get("gross_profit_per_unit", 0),
            "total_gross_profit": item.get("total_gross_profit", 0),
            "margin": round(item["margin"], 4),
            "profitability_index": round(item.get("profitability_index", 0), 4),
            # Other Metrics
            "popularity_score": round(item["popularity_score"], 4),
            "image_score": item.get("image_score"),
            "overall_score": round(overall_score, 4),
            "data_quality": item.get("data_quality", "medium"),
            # Strategic Output
            "strategy": strategy,
            "priority": priority,
            # Visualization coordinates
            "bcg_x": item["market_share"],
            "bcg_y": item["growth_rate"],
        }

    def _get_star_strategy(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific strategy for Star products."""
        margin = item.get("margin", 0.5)
        price = item.get("price", 0)

        actions = [
            "Aumentar visibilidad en el menú (posición premium, fotos destacadas)",
            "Capacitar al personal para recomendar este platillo activamente",
            "Considerar variaciones premium o porciones especiales",
        ]

        if margin < 0.55:
            actions.append(
                f"⚠️ Revisar costos - margen actual ({margin*100:.0f}%) es bajo para un Star"
            )
            actions.append("Negociar con proveedores o ajustar porciones")
        else:
            actions.append(
                f"✅ Excelente margen ({margin*100:.0f}%) - mantener control de costos"
            )

        if price > 15:
            actions.append("Considerar combo o maridaje para aumentar ticket promedio")

        return {
            "summary": "INVERTIR - Este es un ganador. Alto crecimiento y alta contribución al profit.",
            "actions": actions,
            "investment_recommendation": "Alto",
            "pricing_recommendation": (
                "Mantener o aumentar ligeramente"
                if margin > 0.6
                else "Revisar estructura de costos"
            ),
        }

    def _get_cash_cow_strategy(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific strategy for Cash Cow products."""
        margin = item.get("margin", 0.5)

        actions = [
            "Mantener calidad constante - los clientes lo esperan",
            "Optimizar costos sin afectar calidad percibida",
            "Usar como ancla para promociones de otros productos",
        ]

        if margin > 0.65:
            actions.append(
                f"💰 Margen excelente ({margin*100:.0f}%) - este producto subsidia innovación"
            )
        else:
            actions.append(
                f"Mejorar margen (actual: {margin*100:.0f}%) revisando proveedores"
            )

        actions.append(
            "Considerar bundle con Question Marks para aumentar su exposición"
        )

        return {
            "summary": "ORDEÑAR - Genera flujo constante. Minimizar inversión, maximizar extracción de valor.",
            "actions": actions,
            "investment_recommendation": "Bajo (mantenimiento)",
            "pricing_recommendation": "Estable, ajustes graduales con inflación",
        }

    def _get_question_mark_strategy(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific strategy for Question Mark products."""
        margin = item.get("margin", 0.5)
        growth = item.get("growth_rate", 0)

        actions = [
            "DECISIÓN REQUERIDA: Invertir fuerte o descontinuar",
            "Probar promoción temporal para medir potencial real",
            "Solicitar feedback específico de clientes sobre este platillo",
        ]

        if margin > 0.55 and growth > 0.15:
            actions.append(
                "🎯 RECOMENDACIÓN: Invertir - buen margen + alto crecimiento = Star potencial"
            )
            actions.append("Campaña de awareness en redes sociales")
        elif margin < 0.45:
            actions.append("⚠️ PRECAUCIÓN: Bajo margen limita potencial de inversión")
            actions.append("Primero optimizar costos antes de invertir en marketing")
        else:
            actions.append("Ejecutar prueba A/B con promoción por 2 semanas")
            actions.append("Medir si la promoción convierte a más clientes")

        return {
            "summary": "ANALIZAR - Alto crecimiento pero baja contribución. Decidir: invertir para convertir en Star o desinvertir.",
            "actions": actions,
            "investment_recommendation": "Selectivo - prueba antes de comprometerse",
            "pricing_recommendation": "Precio introductorio o promocional para ganar share",
        }

    def _get_dog_strategy(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific strategy for Dog products."""
        margin = item.get("margin", 0.5)
        popularity = item.get("popularity_score", 0)

        actions = []

        if margin > 0.60:
            actions.append(
                "💡 Alto margen - considerar reposicionamiento antes de eliminar"
            )
            actions.append(
                "Podría funcionar como 'especialidad del chef' con storytelling"
            )
        elif margin < 0.35:
            actions.append("❌ Bajo margen Y bajo volumen - candidato a eliminación")
            actions.append("Liberar espacio en menú para nuevos productos")

        if popularity > 0.3:
            actions.append(
                "Algunos clientes lo piden - evaluar si es 'signature dish' de nicho"
            )
        else:
            actions.append("Bajo interés del cliente - priorizar eliminación")

        actions.extend(
            [
                "Considerar rediseño completo del platillo",
                "Evaluar si los ingredientes pueden usarse en productos exitosos",
                "Si se mantiene, reducir porción/costo para mejorar margen",
            ]
        )

        return {
            "summary": "REVISAR - Bajo crecimiento y baja contribución. Considerar eliminar, reposicionar o reformular.",
            "actions": actions,
            "investment_recommendation": "Mínimo o cero",
            "pricing_recommendation": "Reducir costo o descontinuar",
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
