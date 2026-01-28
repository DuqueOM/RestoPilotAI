"""
Data Capability Detector for MenuPilot.
Analyzes uploaded CSV data to determine which analytics features are available.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class AnalyticsCapability(str, Enum):
    """Available analytics capabilities based on data columns."""
    # Core capabilities (always available with basic data)
    BCG_ANALYSIS = "bcg_analysis"
    BASIC_SALES = "basic_sales"
    
    # Time-based capabilities
    HOURLY_DEMAND = "hourly_demand"
    DAILY_PATTERNS = "daily_patterns"
    SEASONAL_TRENDS = "seasonal_trends"
    
    # Financial capabilities
    MARGIN_ANALYSIS = "margin_analysis"
    PRICE_OPTIMIZATION = "price_optimization"
    TICKET_FORECASTING = "ticket_forecasting"
    
    # Product capabilities
    CATEGORY_ANALYSIS = "category_analysis"
    PRODUCT_MIX = "product_mix"
    MENU_OPTIMIZATION = "menu_optimization"
    
    # Advanced capabilities
    STAFF_OPTIMIZATION = "staff_optimization"
    CUSTOMER_SEGMENTATION = "customer_segmentation"
    TIP_PREDICTION = "tip_prediction"
    SATISFACTION_MODEL = "satisfaction_model"


@dataclass
class ColumnMapping:
    """Maps detected columns to their semantic meaning."""
    date_col: Optional[str] = None
    time_col: Optional[str] = None
    datetime_col: Optional[str] = None
    item_name_col: Optional[str] = None
    quantity_col: Optional[str] = None
    revenue_col: Optional[str] = None
    cost_col: Optional[str] = None
    price_col: Optional[str] = None
    category_col: Optional[str] = None
    customer_id_col: Optional[str] = None
    ticket_id_col: Optional[str] = None
    tip_col: Optional[str] = None
    rating_col: Optional[str] = None
    staff_col: Optional[str] = None
    day_of_week_col: Optional[str] = None
    hour_col: Optional[str] = None


@dataclass
class DataCapabilityReport:
    """Report of available capabilities based on data analysis."""
    available_capabilities: List[AnalyticsCapability] = field(default_factory=list)
    missing_for_advanced: Dict[str, List[str]] = field(default_factory=dict)
    column_mapping: ColumnMapping = field(default_factory=ColumnMapping)
    data_quality_score: float = 0.0
    row_count: int = 0
    date_range_days: Optional[int] = None
    unique_items: int = 0
    unique_categories: int = 0
    recommendations: List[str] = field(default_factory=list)
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DataCapabilityDetector:
    """Detects available analytics capabilities from CSV data."""
    
    # Column name patterns for auto-detection
    DATE_PATTERNS = ['date', 'fecha', 'dia', 'day', 'sale_date', 'order_date', 'transaction_date']
    TIME_PATTERNS = ['time', 'hora', 'hour', 'sale_time', 'order_time']
    DATETIME_PATTERNS = ['datetime', 'timestamp', 'created_at', 'order_datetime']
    ITEM_PATTERNS = ['item', 'producto', 'product', 'item_name', 'product_name', 'nombre', 'dish', 'plato']
    QUANTITY_PATTERNS = ['quantity', 'cantidad', 'qty', 'units', 'count', 'sold']
    REVENUE_PATTERNS = ['revenue', 'ingreso', 'sales', 'total', 'amount', 'venta', 'subtotal']
    COST_PATTERNS = ['cost', 'costo', 'expense', 'gasto', 'unit_cost', 'food_cost']
    PRICE_PATTERNS = ['price', 'precio', 'unit_price', 'sale_price']
    CATEGORY_PATTERNS = ['category', 'categoria', 'type', 'tipo', 'group', 'grupo']
    CUSTOMER_PATTERNS = ['customer', 'cliente', 'customer_id', 'client_id', 'user_id']
    TICKET_PATTERNS = ['ticket', 'order', 'order_id', 'ticket_id', 'invoice', 'folio']
    TIP_PATTERNS = ['tip', 'propina', 'gratuity', 'tips']
    RATING_PATTERNS = ['rating', 'score', 'calificacion', 'stars', 'satisfaction']
    STAFF_PATTERNS = ['staff', 'waiter', 'mesero', 'employee', 'server', 'employee_id']
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.column_mapping = ColumnMapping()
    
    def analyze(self, df: pd.DataFrame) -> DataCapabilityReport:
        """Analyze DataFrame and return capability report."""
        self.df = df
        self.column_mapping = ColumnMapping()
        
        # Detect column mappings
        self._detect_columns()
        
        # Determine available capabilities
        capabilities = self._determine_capabilities()
        
        # Calculate data quality
        quality_score = self._calculate_quality_score()
        
        # Get missing columns for advanced features
        missing = self._get_missing_for_advanced()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Calculate metadata
        date_range = self._calculate_date_range()
        unique_items = self._count_unique_items()
        unique_categories = self._count_unique_categories()
        
        return DataCapabilityReport(
            available_capabilities=capabilities,
            missing_for_advanced=missing,
            column_mapping=self.column_mapping,
            data_quality_score=quality_score,
            row_count=len(df),
            date_range_days=date_range,
            unique_items=unique_items,
            unique_categories=unique_categories,
            recommendations=recommendations
        )
    
    def _detect_columns(self) -> None:
        """Auto-detect column mappings based on name patterns."""
        if self.df is None:
            return
        
        columns_lower = {col: col.lower().strip() for col in self.df.columns}
        
        for col, col_lower in columns_lower.items():
            # Date detection
            if any(p in col_lower for p in self.DATE_PATTERNS):
                self.column_mapping.date_col = col
            
            # Time detection
            if any(p in col_lower for p in self.TIME_PATTERNS) and 'datetime' not in col_lower:
                self.column_mapping.time_col = col
            
            # Datetime detection
            if any(p in col_lower for p in self.DATETIME_PATTERNS):
                self.column_mapping.datetime_col = col
            
            # Item name detection
            if any(p in col_lower for p in self.ITEM_PATTERNS):
                self.column_mapping.item_name_col = col
            
            # Quantity detection
            if any(p in col_lower for p in self.QUANTITY_PATTERNS):
                self.column_mapping.quantity_col = col
            
            # Revenue detection
            if any(p in col_lower for p in self.REVENUE_PATTERNS):
                self.column_mapping.revenue_col = col
            
            # Cost detection
            if any(p in col_lower for p in self.COST_PATTERNS):
                self.column_mapping.cost_col = col
            
            # Price detection
            if any(p in col_lower for p in self.PRICE_PATTERNS):
                self.column_mapping.price_col = col
            
            # Category detection
            if any(p in col_lower for p in self.CATEGORY_PATTERNS):
                self.column_mapping.category_col = col
            
            # Customer detection
            if any(p in col_lower for p in self.CUSTOMER_PATTERNS):
                self.column_mapping.customer_id_col = col
            
            # Ticket detection
            if any(p in col_lower for p in self.TICKET_PATTERNS):
                self.column_mapping.ticket_id_col = col
            
            # Tip detection
            if any(p in col_lower for p in self.TIP_PATTERNS):
                self.column_mapping.tip_col = col
            
            # Rating detection
            if any(p in col_lower for p in self.RATING_PATTERNS):
                self.column_mapping.rating_col = col
            
            # Staff detection
            if any(p in col_lower for p in self.STAFF_PATTERNS):
                self.column_mapping.staff_col = col
        
        # Try to extract hour from datetime if no time column
        if self.column_mapping.datetime_col and not self.column_mapping.time_col:
            try:
                self.df['_extracted_hour'] = pd.to_datetime(
                    self.df[self.column_mapping.datetime_col]
                ).dt.hour
                self.column_mapping.hour_col = '_extracted_hour'
            except Exception:
                pass
    
    def _determine_capabilities(self) -> List[AnalyticsCapability]:
        """Determine which analytics are available based on columns."""
        capabilities = []
        cm = self.column_mapping
        
        # Basic sales - needs item + quantity or revenue
        if cm.item_name_col and (cm.quantity_col or cm.revenue_col):
            capabilities.append(AnalyticsCapability.BASIC_SALES)
            capabilities.append(AnalyticsCapability.BCG_ANALYSIS)
        
        # Category analysis
        if cm.category_col and cm.item_name_col:
            capabilities.append(AnalyticsCapability.CATEGORY_ANALYSIS)
            capabilities.append(AnalyticsCapability.PRODUCT_MIX)
        
        # Time-based analysis
        if cm.date_col or cm.datetime_col:
            capabilities.append(AnalyticsCapability.DAILY_PATTERNS)
            
            # Check date range for seasonal
            date_range = self._calculate_date_range()
            if date_range and date_range >= 60:
                capabilities.append(AnalyticsCapability.SEASONAL_TRENDS)
        
        # Hourly demand
        if cm.time_col or cm.hour_col or cm.datetime_col:
            capabilities.append(AnalyticsCapability.HOURLY_DEMAND)
        
        # Financial analysis
        if cm.cost_col or (cm.price_col and cm.revenue_col):
            capabilities.append(AnalyticsCapability.MARGIN_ANALYSIS)
            capabilities.append(AnalyticsCapability.PRICE_OPTIMIZATION)
            capabilities.append(AnalyticsCapability.MENU_OPTIMIZATION)
        
        # Ticket forecasting
        if cm.ticket_id_col and (cm.date_col or cm.datetime_col):
            capabilities.append(AnalyticsCapability.TICKET_FORECASTING)
        
        # Staff optimization
        if cm.staff_col and (cm.time_col or cm.datetime_col):
            capabilities.append(AnalyticsCapability.STAFF_OPTIMIZATION)
        
        # Customer segmentation
        if cm.customer_id_col and cm.item_name_col:
            capabilities.append(AnalyticsCapability.CUSTOMER_SEGMENTATION)
        
        # Tip prediction
        if cm.tip_col and cm.revenue_col:
            capabilities.append(AnalyticsCapability.TIP_PREDICTION)
        
        # Satisfaction model
        if cm.rating_col:
            capabilities.append(AnalyticsCapability.SATISFACTION_MODEL)
        
        return capabilities
    
    def _calculate_quality_score(self) -> float:
        """Calculate data quality score (0-1)."""
        if self.df is None:
            return 0.0
        
        scores = []
        
        # Completeness - check for nulls in key columns
        key_cols = [
            self.column_mapping.item_name_col,
            self.column_mapping.quantity_col,
            self.column_mapping.revenue_col,
            self.column_mapping.date_col
        ]
        for col in key_cols:
            if col and col in self.df.columns:
                null_ratio = self.df[col].isnull().sum() / len(self.df)
                scores.append(1 - null_ratio)
        
        # Row count score
        if len(self.df) >= 1000:
            scores.append(1.0)
        elif len(self.df) >= 100:
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # Date range score
        date_range = self._calculate_date_range()
        if date_range:
            if date_range >= 90:
                scores.append(1.0)
            elif date_range >= 30:
                scores.append(0.7)
            else:
                scores.append(0.4)
        
        return round(sum(scores) / len(scores), 2) if scores else 0.0
    
    def _get_missing_for_advanced(self) -> Dict[str, List[str]]:
        """Get missing columns needed for advanced features."""
        missing = {}
        cm = self.column_mapping
        
        if not cm.cost_col:
            missing["margin_analysis"] = ["cost", "costo", "food_cost"]
        
        if not cm.time_col and not cm.datetime_col:
            missing["hourly_demand"] = ["time", "hora", "datetime"]
        
        if not cm.customer_id_col:
            missing["customer_segmentation"] = ["customer_id", "cliente"]
        
        if not cm.staff_col:
            missing["staff_optimization"] = ["staff", "waiter", "mesero"]
        
        if not cm.tip_col:
            missing["tip_prediction"] = ["tip", "propina"]
        
        if not cm.rating_col:
            missing["satisfaction_model"] = ["rating", "calificacion", "score"]
        
        return missing
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations to unlock more features."""
        recs = []
        cm = self.column_mapping
        
        if not cm.cost_col:
            recs.append("💰 Add a 'cost' column to enable margin analysis and price optimization")
        
        if not cm.time_col and not cm.datetime_col:
            recs.append("⏰ Add a 'time' or 'datetime' column to enable hourly demand prediction")
        
        if not cm.category_col:
            recs.append("📂 Add a 'category' column for product mix and category analysis")
        
        date_range = self._calculate_date_range()
        if date_range and date_range < 60:
            recs.append(f"📅 You have {date_range} days of data. Add more historical data (60+ days) for seasonal trends")
        
        if len(self.df) < 100:
            recs.append("📊 More data rows (100+) will improve prediction accuracy")
        
        return recs
    
    def _calculate_date_range(self) -> Optional[int]:
        """Calculate the date range in days."""
        if self.df is None:
            return None
        
        date_col = self.column_mapping.date_col or self.column_mapping.datetime_col
        if not date_col:
            return None
        
        try:
            dates = pd.to_datetime(self.df[date_col])
            return (dates.max() - dates.min()).days
        except Exception:
            return None
    
    def _count_unique_items(self) -> int:
        """Count unique menu items."""
        if self.df is None or not self.column_mapping.item_name_col:
            return 0
        return self.df[self.column_mapping.item_name_col].nunique()
    
    def _count_unique_categories(self) -> int:
        """Count unique categories."""
        if self.df is None or not self.column_mapping.category_col:
            return 0
        return self.df[self.column_mapping.category_col].nunique()


# Singleton instance
data_capability_detector = DataCapabilityDetector()
