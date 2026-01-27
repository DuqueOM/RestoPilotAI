"""
Menu-related Pydantic schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


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
