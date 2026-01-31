"""
Business-related Pydantic schemas.
Combines Menu and Sales schemas.
"""

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# MENU SCHEMAS
# ============================================================================

class MenuItemCreate(BaseModel):
    """Schema for creating a menu item manually."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    cost: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_gluten_free: bool = False
    spice_level: Optional[int] = Field(None, ge=0, le=5)


class MenuItemResponse(BaseModel):
    """Response schema for menu items."""

    id: int
    name: str
    description: Optional[str]
    price: float
    cost: Optional[float]
    category: Optional[str]
    image_url: Optional[str]
    image_score: Optional[float]
    margin: Optional[float]
    profit: Optional[float]
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    spice_level: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MenuCategoryResponse(BaseModel):
    """Response schema for menu categories."""

    id: int
    name: str
    description: Optional[str]
    display_order: int
    item_count: int

    class Config:
        from_attributes = True


class ExtractedMenuItem(BaseModel):
    """A menu item extracted from image analysis."""

    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    confidence: float = Field(..., ge=0, le=1)
    dietary_tags: List[str] = []


class MenuExtractionResponse(BaseModel):
    """Response from menu image extraction."""

    session_id: str
    status: str
    items_extracted: int
    categories_found: List[str]
    items: List[ExtractedMenuItem]
    extraction_confidence: float
    thought_process: str  # Gemini's reasoning trace
    warnings: List[str] = []


# ============================================================================
# SALES SCHEMAS
# ============================================================================

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
