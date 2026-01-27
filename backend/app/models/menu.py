"""
Menu-related database models.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MenuCategory(Base):
    """Category for menu items."""

    __tablename__ = "menu_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem", back_populates="category"
    )


class MenuItem(Base):
    """Individual menu item with pricing and metadata."""

    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("menu_categories.id"), nullable=True
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Pricing
    price: Mapped[float] = mapped_column(Float)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Image analysis
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # 0-1 attractiveness

    # Extracted attributes
    is_vegetarian: Mapped[bool] = mapped_column(default=False)
    is_vegan: Mapped[bool] = mapped_column(default=False)
    is_gluten_free: Mapped[bool] = mapped_column(default=False)
    spice_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-5

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    category: Mapped[Optional["MenuCategory"]] = relationship(
        "MenuCategory", back_populates="items"
    )

    @property
    def margin(self) -> Optional[float]:
        """Calculate profit margin if cost is available."""
        if self.cost is not None and self.cost > 0:
            return (self.price - self.cost) / self.price
        return None

    @property
    def profit(self) -> Optional[float]:
        """Calculate absolute profit per unit."""
        if self.cost is not None:
            return self.price - self.cost
        return None
