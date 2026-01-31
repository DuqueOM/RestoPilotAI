"""
Advanced Analytics Service for RestoPilotAI.
Provides demand prediction, seasonal trends, and product analytics.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TimeGranularity(str, Enum):
    """Time granularity for analysis."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class SeasonType(str, Enum):
    """Seasonal patterns detected."""
    WEEKDAY_WEEKEND = "weekday_weekend"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HOLIDAY = "holiday"


@dataclass
class HourlyDemandPattern:
    """Hourly demand pattern for an item or category."""
    hour: int
    avg_quantity: float
    avg_revenue: float
    peak_indicator: bool  # True if this is a peak hour
    staffing_recommendation: str


@dataclass
class DailyPattern:
    """Daily sales pattern."""
    day_of_week: int  # 0=Monday, 6=Sunday
    day_name: str
    avg_quantity: float
    avg_revenue: float
    avg_tickets: Optional[float]
    is_peak_day: bool


@dataclass
class SeasonalTrend:
    """Seasonal trend analysis."""
    season_type: SeasonType
    pattern_description: str
    peak_periods: List[str]
    low_periods: List[str]
    variance_pct: float  # How much variation from baseline


@dataclass
class ProductAnalytics:
    """Analytics for a single product."""
    item_name: str
    total_quantity: int
    total_revenue: float
    avg_daily_sales: float
    sales_trend: str  # "increasing", "decreasing", "stable"
    trend_pct: float
    best_selling_hour: Optional[int]
    best_selling_day: Optional[str]
    category: Optional[str]
    pair_suggestions: List[str]  # Items often bought together


@dataclass
class CategoryAnalytics:
    """Analytics for a category."""
    category: str
    item_count: int
    total_revenue: float
    revenue_share: float
    avg_item_price: float
    top_performer: str
    worst_performer: str
    growth_trend: str


@dataclass
class DemandForecast:
    """Demand forecast result."""
    period: str
    predicted_quantity: float
    predicted_revenue: float
    confidence_lower: float
    confidence_upper: float
    factors: List[str]  # Factors influencing the forecast


@dataclass
class AdvancedAnalyticsReport:
    """Complete advanced analytics report."""
    session_id: str
    generated_at: str
    capabilities_used: List[str]
    
    # Time-based analytics
    hourly_patterns: List[HourlyDemandPattern]
    daily_patterns: List[DailyPattern]
    seasonal_trends: List[SeasonalTrend]
    
    # Product analytics
    product_analytics: List[ProductAnalytics]
    category_analytics: List[CategoryAnalytics]
    
    # Forecasts
    demand_forecast: List[DemandForecast]
    
    # Insights
    key_insights: List[str]
    recommendations: List[str]
    data_quality_notes: List[str]


class AdvancedAnalyticsService:
    """
    Advanced analytics engine for restaurant data.
    Provides demand prediction, seasonal analysis, and product insights.
    """
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.column_mapping: Dict[str, str] = {}
    
    async def analyze(
        self,
        df: pd.DataFrame,
        session_id: str,
        column_mapping: Dict[str, Optional[str]],
        capabilities: List[str]
    ) -> AdvancedAnalyticsReport:
        """
        Run advanced analytics based on available capabilities.
        
        Args:
            df: Sales DataFrame
            session_id: Session ID
            column_mapping: Mapping of semantic columns to actual column names
            capabilities: List of available analytics capabilities
        """
        self.df = df
        self.column_mapping = {k: v for k, v in column_mapping.items() if v}
        
        logger.info(f"Running advanced analytics for session {session_id}")
        logger.info(f"Available capabilities: {capabilities}")
        
        hourly_patterns = []
        daily_patterns = []
        seasonal_trends = []
        product_analytics = []
        category_analytics = []
        demand_forecast = []
        insights = []
        recommendations = []
        data_notes = []
        
        # Run analyses based on capabilities
        if 'hourly_demand' in capabilities:
            hourly_patterns = self._analyze_hourly_demand()
            insights.extend(self._generate_hourly_insights(hourly_patterns))
        
        if 'daily_patterns' in capabilities:
            daily_patterns = self._analyze_daily_patterns()
            insights.extend(self._generate_daily_insights(daily_patterns))
        
        if 'seasonal_trends' in capabilities:
            seasonal_trends = self._analyze_seasonal_trends()
            insights.extend(self._generate_seasonal_insights(seasonal_trends))
        
        if 'category_analysis' in capabilities or 'product_mix' in capabilities:
            product_analytics = self._analyze_products()
            category_analytics = self._analyze_categories()
            insights.extend(self._generate_product_insights(product_analytics))
        
        if 'basic_sales' in capabilities:
            demand_forecast = self._generate_demand_forecast()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            hourly_patterns, daily_patterns, product_analytics
        )
        
        # Data quality notes
        data_notes = self._generate_data_notes()
        
        return AdvancedAnalyticsReport(
            session_id=session_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            capabilities_used=capabilities,
            hourly_patterns=hourly_patterns,
            daily_patterns=daily_patterns,
            seasonal_trends=seasonal_trends,
            product_analytics=product_analytics,
            category_analytics=category_analytics,
            demand_forecast=demand_forecast,
            key_insights=insights,
            recommendations=recommendations,
            data_quality_notes=data_notes
        )
    
    def _analyze_hourly_demand(self) -> List[HourlyDemandPattern]:
        """Analyze demand patterns by hour."""
        patterns = []
        
        # Try to get hour from datetime or time column
        hour_col = None
        if 'hour_col' in self.column_mapping:
            hour_col = self.column_mapping['hour_col']
        elif 'datetime_col' in self.column_mapping:
            try:
                self.df['_hour'] = pd.to_datetime(self.df[self.column_mapping['datetime_col']]).dt.hour
                hour_col = '_hour'
            except Exception:
                pass
        elif 'time_col' in self.column_mapping:
            try:
                self.df['_hour'] = pd.to_datetime(self.df[self.column_mapping['time_col']], format='%H:%M:%S').dt.hour
                hour_col = '_hour'
            except Exception:
                pass
        
        if not hour_col:
            return patterns
        
        qty_col = self.column_mapping.get('quantity_col', 'quantity')
        rev_col = self.column_mapping.get('revenue_col', 'revenue')
        
        # Group by hour
        hourly = self.df.groupby(hour_col).agg({
            qty_col: 'mean' if qty_col in self.df.columns else 'count',
            rev_col: 'mean' if rev_col in self.df.columns else 'count'
        }).reset_index()
        
        # Identify peak hours (top 25%)
        qty_threshold = hourly[qty_col].quantile(0.75) if qty_col in hourly.columns else 0
        
        for _, row in hourly.iterrows():
            hour = int(row[hour_col])
            is_peak = row[qty_col] >= qty_threshold if qty_col in hourly.columns else False
            
            # Staffing recommendation
            if is_peak:
                staffing = "Maximum staffing recommended"
            elif hour < 11 or hour > 21:
                staffing = "Minimum staffing"
            else:
                staffing = "Standard staffing"
            
            patterns.append(HourlyDemandPattern(
                hour=hour,
                avg_quantity=round(row[qty_col], 1) if qty_col in hourly.columns else 0,
                avg_revenue=round(row[rev_col], 2) if rev_col in hourly.columns else 0,
                peak_indicator=is_peak,
                staffing_recommendation=staffing
            ))
        
        return sorted(patterns, key=lambda x: x.hour)
    
    def _analyze_daily_patterns(self) -> List[DailyPattern]:
        """Analyze patterns by day of week."""
        patterns = []
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        date_col = self.column_mapping.get('date_col') or self.column_mapping.get('datetime_col')
        if not date_col:
            return patterns
        
        qty_col = self.column_mapping.get('quantity_col', 'quantity')
        rev_col = self.column_mapping.get('revenue_col', 'revenue')
        ticket_col = self.column_mapping.get('ticket_id_col')
        
        try:
            self.df['_dow'] = pd.to_datetime(self.df[date_col]).dt.dayofweek
        except Exception:
            return patterns
        
        # Group by day of week
        daily = self.df.groupby('_dow').agg({
            qty_col: 'mean' if qty_col in self.df.columns else 'count',
            rev_col: 'mean' if rev_col in self.df.columns else 'count'
        }).reset_index()
        
        # Add ticket count if available
        if ticket_col and ticket_col in self.df.columns:
            ticket_daily = self.df.groupby('_dow')[ticket_col].nunique().reset_index()
            ticket_daily.columns = ['_dow', 'tickets']
            daily = daily.merge(ticket_daily, on='_dow', how='left')
        
        # Identify peak days
        qty_threshold = daily[qty_col].quantile(0.6) if qty_col in daily.columns else 0
        
        for _, row in daily.iterrows():
            dow = int(row['_dow'])
            patterns.append(DailyPattern(
                day_of_week=dow,
                day_name=day_names[dow],
                avg_quantity=round(row[qty_col], 1) if qty_col in daily.columns else 0,
                avg_revenue=round(row[rev_col], 2) if rev_col in daily.columns else 0,
                avg_tickets=round(row['tickets'], 1) if 'tickets' in daily.columns else None,
                is_peak_day=row[qty_col] >= qty_threshold if qty_col in daily.columns else False
            ))
        
        return sorted(patterns, key=lambda x: x.day_of_week)
    
    def _analyze_seasonal_trends(self) -> List[SeasonalTrend]:
        """Analyze seasonal patterns."""
        trends = []
        
        date_col = self.column_mapping.get('date_col') or self.column_mapping.get('datetime_col')
        if not date_col:
            return trends
        
        rev_col = self.column_mapping.get('revenue_col', 'revenue')
        
        try:
            self.df['_date'] = pd.to_datetime(self.df[date_col])
            self.df['_month'] = self.df['_date'].dt.month
            self.df['_is_weekend'] = self.df['_date'].dt.dayofweek >= 5
        except Exception:
            return trends
        
        # Weekday vs Weekend pattern
        if '_is_weekend' in self.df.columns and rev_col in self.df.columns:
            weekend_rev = self.df[self.df['_is_weekend']][rev_col].mean()
            weekday_rev = self.df[~self.df['_is_weekend']][rev_col].mean()
            
            if weekday_rev > 0:
                variance = abs(weekend_rev - weekday_rev) / weekday_rev * 100
                
                if weekend_rev > weekday_rev:
                    trends.append(SeasonalTrend(
                        season_type=SeasonType.WEEKDAY_WEEKEND,
                        pattern_description=f"Weekend sales are {variance:.0f}% higher than weekdays",
                        peak_periods=["Saturday", "Sunday"],
                        low_periods=["Monday", "Tuesday"],
                        variance_pct=round(variance, 1)
                    ))
                else:
                    trends.append(SeasonalTrend(
                        season_type=SeasonType.WEEKDAY_WEEKEND,
                        pattern_description=f"Weekday sales are {variance:.0f}% higher than weekends",
                        peak_periods=["Wednesday", "Thursday", "Friday"],
                        low_periods=["Saturday", "Sunday"],
                        variance_pct=round(variance, 1)
                    ))
        
        # Monthly pattern
        if '_month' in self.df.columns and rev_col in self.df.columns:
            monthly = self.df.groupby('_month')[rev_col].mean()
            if len(monthly) >= 3:
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                avg_monthly = monthly.mean()
                peak_months = monthly[monthly > avg_monthly * 1.1].index.tolist()
                low_months = monthly[monthly < avg_monthly * 0.9].index.tolist()
                
                if peak_months or low_months:
                    variance = (monthly.max() - monthly.min()) / avg_monthly * 100
                    trends.append(SeasonalTrend(
                        season_type=SeasonType.MONTHLY,
                        pattern_description=f"Monthly variation of {variance:.0f}% between high and low periods",
                        peak_periods=[month_names[m-1] for m in peak_months],
                        low_periods=[month_names[m-1] for m in low_months],
                        variance_pct=round(variance, 1)
                    ))
        
        return trends
    
    def _analyze_products(self) -> List[ProductAnalytics]:
        """Analyze individual product performance."""
        analytics = []
        
        item_col = self.column_mapping.get('item_name_col')
        if not item_col:
            return analytics
        
        qty_col = self.column_mapping.get('quantity_col', 'quantity')
        rev_col = self.column_mapping.get('revenue_col', 'revenue')
        cat_col = self.column_mapping.get('category_col')
        date_col = self.column_mapping.get('date_col') or self.column_mapping.get('datetime_col')
        
        # Basic aggregation
        agg_dict = {}
        if qty_col in self.df.columns:
            agg_dict[qty_col] = 'sum'
        if rev_col in self.df.columns:
            agg_dict[rev_col] = 'sum'
        
        if not agg_dict:
            return analytics
        
        product_data = self.df.groupby(item_col).agg(agg_dict).reset_index()
        
        # Calculate daily average if date available
        if date_col:
            try:
                days = (pd.to_datetime(self.df[date_col]).max() - 
                       pd.to_datetime(self.df[date_col]).min()).days + 1
            except Exception:
                days = 30
        else:
            days = 30
        
        # Add category
        if cat_col and cat_col in self.df.columns:
            cat_map = self.df.groupby(item_col)[cat_col].first().to_dict()
        else:
            cat_map = {}
        
        # Calculate trend (simplified - compare first half to second half)
        if date_col:
            try:
                median_date = pd.to_datetime(self.df[date_col]).median()
                first_half = self.df[pd.to_datetime(self.df[date_col]) < median_date]
                second_half = self.df[pd.to_datetime(self.df[date_col]) >= median_date]
                
                first_sales = first_half.groupby(item_col)[qty_col].sum() if qty_col in self.df.columns else {}
                second_sales = second_half.groupby(item_col)[qty_col].sum() if qty_col in self.df.columns else {}
            except Exception:
                first_sales = {}
                second_sales = {}
        else:
            first_sales = {}
            second_sales = {}
        
        for _, row in product_data.iterrows():
            item = row[item_col]
            
            # Calculate trend
            first = first_sales.get(item, 0) if isinstance(first_sales, dict) else first_sales.get(item, 0)
            second = second_sales.get(item, 0) if isinstance(second_sales, dict) else second_sales.get(item, 0)
            
            if first > 0:
                trend_pct = (second - first) / first * 100
                trend = "increasing" if trend_pct > 10 else "decreasing" if trend_pct < -10 else "stable"
            else:
                trend_pct = 0
                trend = "stable"
            
            analytics.append(ProductAnalytics(
                item_name=item,
                total_quantity=int(row[qty_col]) if qty_col in product_data.columns else 0,
                total_revenue=round(row[rev_col], 2) if rev_col in product_data.columns else 0,
                avg_daily_sales=round(row[qty_col] / days, 1) if qty_col in product_data.columns else 0,
                sales_trend=trend,
                trend_pct=round(trend_pct, 1),
                best_selling_hour=None,  # Would need hourly data per item
                best_selling_day=None,   # Would need daily data per item
                category=cat_map.get(item),
                pair_suggestions=[]  # Would need basket analysis
            ))
        
        # Sort by revenue
        analytics.sort(key=lambda x: x.total_revenue, reverse=True)
        return analytics[:50]  # Top 50 items
    
    def _analyze_categories(self) -> List[CategoryAnalytics]:
        """Analyze category performance."""
        analytics = []
        
        cat_col = self.column_mapping.get('category_col')
        item_col = self.column_mapping.get('item_name_col')
        rev_col = self.column_mapping.get('revenue_col', 'revenue')
        
        if not cat_col or cat_col not in self.df.columns:
            return analytics
        
        total_revenue = self.df[rev_col].sum() if rev_col in self.df.columns else 1
        
        for category in self.df[cat_col].dropna().unique():
            cat_data = self.df[self.df[cat_col] == category]
            
            cat_revenue = cat_data[rev_col].sum() if rev_col in cat_data.columns else 0
            item_count = cat_data[item_col].nunique() if item_col else len(cat_data)
            
            # Top and worst performers
            if item_col and item_col in cat_data.columns and rev_col in cat_data.columns:
                item_rev = cat_data.groupby(item_col)[rev_col].sum()
                top_performer = item_rev.idxmax() if len(item_rev) > 0 else "N/A"
                worst_performer = item_rev.idxmin() if len(item_rev) > 0 else "N/A"
            else:
                top_performer = "N/A"
                worst_performer = "N/A"
            
            analytics.append(CategoryAnalytics(
                category=category,
                item_count=item_count,
                total_revenue=round(cat_revenue, 2),
                revenue_share=round(cat_revenue / total_revenue * 100, 1) if total_revenue > 0 else 0,
                avg_item_price=round(cat_revenue / item_count, 2) if item_count > 0 else 0,
                top_performer=top_performer,
                worst_performer=worst_performer,
                growth_trend="stable"  # Would need historical comparison
            ))
        
        analytics.sort(key=lambda x: x.total_revenue, reverse=True)
        return analytics
    
    def _generate_demand_forecast(self) -> List[DemandForecast]:
        """Generate simple demand forecast for next 7 days."""
        forecasts = []
        
        date_col = self.column_mapping.get('date_col') or self.column_mapping.get('datetime_col')
        qty_col = self.column_mapping.get('quantity_col', 'quantity')
        rev_col = self.column_mapping.get('revenue_col', 'revenue')
        
        if not date_col:
            return forecasts
        
        try:
            # Calculate daily averages by day of week
            self.df['_date'] = pd.to_datetime(self.df[date_col])
            self.df['_dow'] = self.df['_date'].dt.dayofweek
            
            daily_avg = self.df.groupby('_dow').agg({
                qty_col: 'mean' if qty_col in self.df.columns else 'count',
                rev_col: 'mean' if rev_col in self.df.columns else 'count'
            })
            
            # Forecast next 7 days
            today = datetime.now(timezone.utc).date()
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for i in range(7):
                forecast_date = today + timedelta(days=i)
                dow = forecast_date.weekday()
                
                if dow in daily_avg.index:
                    pred_qty = daily_avg.loc[dow, qty_col] if qty_col in daily_avg.columns else 0
                    pred_rev = daily_avg.loc[dow, rev_col] if rev_col in daily_avg.columns else 0
                else:
                    pred_qty = daily_avg[qty_col].mean() if qty_col in daily_avg.columns else 0
                    pred_rev = daily_avg[rev_col].mean() if rev_col in daily_avg.columns else 0
                
                # Simple confidence interval (±20%)
                forecasts.append(DemandForecast(
                    period=f"{forecast_date.strftime('%Y-%m-%d')} ({day_names[dow]})",
                    predicted_quantity=round(pred_qty, 0),
                    predicted_revenue=round(pred_rev, 2),
                    confidence_lower=round(pred_rev * 0.8, 2),
                    confidence_upper=round(pred_rev * 1.2, 2),
                    factors=[f"Based on historical {day_names[dow]} averages"]
                ))
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
        
        return forecasts
    
    def _generate_hourly_insights(self, patterns: List[HourlyDemandPattern]) -> List[str]:
        """Generate insights from hourly patterns."""
        insights = []
        if not patterns:
            return insights
        
        peak_hours = [p for p in patterns if p.peak_indicator]
        if peak_hours:
            hours = ", ".join([f"{p.hour}:00" for p in peak_hours])
            insights.append(f"⏰ Peak hours identified: {hours}")
        
        # Find lunch and dinner rushes
        lunch_hours = [p for p in patterns if 11 <= p.hour <= 14]
        dinner_hours = [p for p in patterns if 18 <= p.hour <= 21]
        
        if lunch_hours and dinner_hours:
            lunch_avg = sum(p.avg_revenue for p in lunch_hours) / len(lunch_hours)
            dinner_avg = sum(p.avg_revenue for p in dinner_hours) / len(dinner_hours)
            
            if dinner_avg > lunch_avg * 1.2:
                insights.append("🍽️ Dinner service significantly outperforms lunch")
            elif lunch_avg > dinner_avg * 1.2:
                insights.append("☀️ Lunch service is your strongest daypart")
        
        return insights
    
    def _generate_daily_insights(self, patterns: List[DailyPattern]) -> List[str]:
        """Generate insights from daily patterns."""
        insights = []
        if not patterns:
            return insights
        
        peak_days = [p for p in patterns if p.is_peak_day]
        if peak_days:
            days = ", ".join([p.day_name for p in peak_days])
            insights.append(f"📅 Best performing days: {days}")
        
        # Weekend vs weekday
        weekend = [p for p in patterns if p.day_of_week >= 5]
        weekday = [p for p in patterns if p.day_of_week < 5]
        
        if weekend and weekday:
            weekend_avg = sum(p.avg_revenue for p in weekend) / len(weekend)
            weekday_avg = sum(p.avg_revenue for p in weekday) / len(weekday)
            
            diff_pct = abs(weekend_avg - weekday_avg) / weekday_avg * 100
            if diff_pct > 20:
                if weekend_avg > weekday_avg:
                    insights.append(f"🎉 Weekend revenue is {diff_pct:.0f}% higher than weekdays")
                else:
                    insights.append(f"💼 Weekday revenue is {diff_pct:.0f}% higher than weekends")
        
        return insights
    
    def _generate_seasonal_insights(self, trends: List[SeasonalTrend]) -> List[str]:
        """Generate insights from seasonal trends."""
        insights = []
        for trend in trends:
            if trend.variance_pct > 15:
                insights.append(f"📊 {trend.pattern_description}")
        return insights
    
    def _generate_product_insights(self, products: List[ProductAnalytics]) -> List[str]:
        """Generate insights from product analytics."""
        insights = []
        if not products:
            return insights
        
        # Top performers
        top_3 = products[:3]
        if top_3:
            names = ", ".join([p.item_name for p in top_3])
            insights.append(f"🏆 Top sellers: {names}")
        
        # Trending up
        trending_up = [p for p in products if p.sales_trend == "increasing" and p.trend_pct > 20]
        if trending_up:
            names = ", ".join([p.item_name for p in trending_up[:3]])
            insights.append(f"📈 Rising stars: {names}")
        
        # Declining
        declining = [p for p in products if p.sales_trend == "decreasing" and p.trend_pct < -20]
        if declining:
            insights.append(f"⚠️ {len(declining)} items showing declining sales - review needed")
        
        return insights
    
    def _generate_recommendations(
        self,
        hourly: List[HourlyDemandPattern],
        daily: List[DailyPattern],
        products: List[ProductAnalytics]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        
        # Staffing recommendations
        if hourly:
            peak_hours = [p for p in hourly if p.peak_indicator]
            if peak_hours:
                recs.append(f"👥 Schedule additional staff during peak hours: {', '.join([f'{p.hour}:00' for p in peak_hours])}")
        
        # Day recommendations
        if daily:
            low_days = [p for p in daily if not p.is_peak_day]
            if low_days:
                day_names = [p.day_name for p in low_days[:2]]
                recs.append(f"📢 Consider promotions on slow days: {', '.join(day_names)}")
        
        # Product recommendations
        if products:
            declining = [p for p in products if p.sales_trend == "decreasing"]
            if declining:
                recs.append("🔄 Review declining items for menu refresh or removal")
            
            stable_low = [p for p in products[-5:] if p.sales_trend == "stable"]
            if stable_low:
                recs.append("💡 Low performers may benefit from better menu placement or promotion")
        
        return recs
    
    def _generate_data_notes(self) -> List[str]:
        """Generate notes about data quality and limitations."""
        notes = []
        
        if self.df is not None:
            if len(self.df) < 100:
                notes.append("⚠️ Limited data sample - insights may have lower confidence")
            
            date_col = self.column_mapping.get('date_col') or self.column_mapping.get('datetime_col')
            if date_col:
                try:
                    days = (pd.to_datetime(self.df[date_col]).max() - 
                           pd.to_datetime(self.df[date_col]).min()).days
                    if days < 30:
                        notes.append(f"📅 Data covers {days} days - longer history improves accuracy")
                except Exception:
                    pass
        
        return notes


# Singleton instance
advanced_analytics = AdvancedAnalyticsService()
