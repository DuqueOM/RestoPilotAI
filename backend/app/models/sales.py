"""
Sales data models.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SalesRecord(Base):
    """Individual sales record for a menu item."""

    __tablename__ = "sales_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)

    # Reference to menu item (by name for flexibility)
    item_name: Mapped[str] = mapped_column(String(200), index=True)
    menu_item_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("menu_items.id"), nullable=True
    )

    # Sales data
    sale_date: Mapped[date] = mapped_column(Date, index=True)
    units_sold: Mapped[int] = mapped_column(Integer)
    revenue: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Context
    day_of_week: Mapped[int] = mapped_column(Integer)  # 0=Monday, 6=Sunday
    is_weekend: Mapped[bool] = mapped_column(default=False)
    is_holiday: Mapped[bool] = mapped_column(default=False)
    had_promotion: Mapped[bool] = mapped_column(default=False)
    promotion_discount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Weather context (optional)
    weather_condition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.sale_date:
            self.day_of_week = self.sale_date.weekday()
            self.is_weekend = self.day_of_week >= 5
