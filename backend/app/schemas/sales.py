"""
Sales-related Pydantic schemas.
"""

from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SalesRecordCreate(BaseModel):
    """Schema for creating a sales record."""

    item_name: str = Field(..., min_length=1, max_length=200)
    sale_date: date
    units_sold: int = Field(..., ge=0)
    revenue: Optional[float] = Field(None, ge=0)
    had_promotion: bool = False
    promotion_discount: Optional[float] = Field(None, ge=0, le=1)


class SalesDataUploadResponse(BaseModel):
    """Response from sales data upload."""

    session_id: str
    status: str
    records_imported: int
    date_range: Dict[str, str]  # {"start": "2024-01-01", "end": "2024-01-31"}
    unique_items: int
    total_units: int
    total_revenue: Optional[float]
    warnings: List[str] = []
    thought_process: str


class ItemSalesMetrics(BaseModel):
    """Sales metrics for a single item."""

    item_name: str
    total_units: int
    total_revenue: float
    avg_daily_units: float
    peak_day: str  # Day of week
    growth_rate: float  # Percentage change
    trend: str  # "increasing", "stable", "decreasing"


class SalesAnalyticsResponse(BaseModel):
    """Comprehensive sales analytics response."""

    session_id: str
    analysis_period: Dict[str, str]
    total_revenue: float
    total_units: int
    avg_daily_revenue: float
    best_performing_items: List[ItemSalesMetrics]
    worst_performing_items: List[ItemSalesMetrics]
    day_of_week_pattern: Dict[str, float]  # {"Monday": 120.5, ...}
    seasonality_detected: bool
    insights: List[str]
    thought_process: str
