"""
Period Calculator - Calculate available analysis periods based on data.
"""

from datetime import timedelta
from typing import Any, Dict, List

from app.services.analysis.menu_engineering import parse_date_flexible
from loguru import logger


class PeriodCalculator:
    """Calculate which analysis periods are available based on sales data."""

    @staticmethod
    def calculate_available_periods(sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sales data and determine which periods have sufficient data.

        Returns:
            {
                "available_periods": ["30d", "90d", ...],
                "data_span_days": int,
                "earliest_date": "YYYY-MM-DD",
                "latest_date": "YYYY-MM-DD",
                "total_records": int,
                "period_info": {
                    "30d": {"available": bool, "records": int, "coverage_pct": float},
                    ...
                }
            }
        """
        if not sales_data:
            return {
                "available_periods": [],
                "data_span_days": 0,
                "earliest_date": None,
                "latest_date": None,
                "total_records": 0,
                "period_info": {},
            }

        # Parse all dates
        dated_sales = []
        for sale in sales_data:
            sale_date = sale.get("sale_date") or sale.get("date")
            if not sale_date:
                continue

            parsed_date = parse_date_flexible(sale_date)
            if parsed_date is None:
                continue

            dated_sales.append(parsed_date)

        if not dated_sales:
            return {
                "available_periods": [],
                "data_span_days": 0,
                "earliest_date": None,
                "latest_date": None,
                "total_records": len(sales_data),
                "period_info": {},
            }

        earliest = min(dated_sales)
        latest = max(dated_sales)
        data_span_days = (latest - earliest).days + 1

        logger.info(f"Data span: {data_span_days} days ({earliest} to {latest})")

        # Define periods with their requirements
        periods = [
            {
                "id": "30d",
                "label": "Last 30 Days",
                "days": 30,
                "min_days_required": 20,  # Need at least 20 days for 30d analysis
            },
            {
                "id": "90d",
                "label": "Last 90 Days",
                "days": 90,
                "min_days_required": 60,  # Need at least 60 days for 90d analysis
            },
            {
                "id": "180d",
                "label": "Last 6 Months",
                "days": 180,
                "min_days_required": 120,  # Need at least 120 days
            },
            {
                "id": "365d",
                "label": "Last Year",
                "days": 365,
                "min_days_required": 270,  # Need at least 270 days
            },
            {
                "id": "all",
                "label": "All Data",
                "days": None,
                "min_days_required": 1,  # Always available if there's any data
            },
        ]

        available_periods = []
        period_info = {}

        for period in periods:
            period_id = period["id"]
            min_required = period["min_days_required"]

            if data_span_days >= min_required:
                # Calculate how many records fall within this period
                if period["days"]:
                    cutoff_date = latest - timedelta(days=period["days"])
                    records_in_period = sum(1 for d in dated_sales if d >= cutoff_date)
                    coverage_pct = (
                        (records_in_period / len(dated_sales)) * 100
                        if dated_sales
                        else 0
                    )
                else:
                    # "all" period
                    records_in_period = len(dated_sales)
                    coverage_pct = 100.0

                available_periods.append(period_id)
                period_info[period_id] = {
                    "available": True,
                    "label": period["label"],
                    "records": records_in_period,
                    "coverage_pct": round(coverage_pct, 1),
                    "days_required": period["days"],
                }
            else:
                period_info[period_id] = {
                    "available": False,
                    "label": period["label"],
                    "records": 0,
                    "coverage_pct": 0.0,
                    "days_required": period["days"],
                    "reason": f"Need at least {min_required} days of data (have {data_span_days})",
                }

        return {
            "available_periods": available_periods,
            "data_span_days": data_span_days,
            "earliest_date": earliest.isoformat(),
            "latest_date": latest.isoformat(),
            "total_records": len(sales_data),
            "period_info": period_info,
        }

    @staticmethod
    def get_recommended_period(data_span_days: int) -> str:
        """Get the recommended analysis period based on data span."""
        if data_span_days >= 270:
            return "90d"  # Strategic analysis with quarterly data
        elif data_span_days >= 60:
            return "30d"  # Operational analysis
        elif data_span_days >= 20:
            return "30d"  # Limited operational analysis
        else:
            return "all"  # Use all available data
