"""
Sales Prediction Service - ML-based forecasting for menu items.
Uses XGBoost for time-series forecasting.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from loguru import logger
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

from app.config import get_settings


class SalesPredictor:
    """ML-based sales predictor for menu items using XGBoost."""

    MODEL_PATH = "data/models/sales_predictor.joblib"

    def __init__(self):
        self.settings = get_settings()
        self.model: Optional[xgb.XGBRegressor] = None
        self.feature_columns = [
            "day_of_week",
            "is_weekend",
            "price",
            "promo_flag",
            "promo_discount",
            "image_score",
            "rolling_avg_7d",
            "rolling_avg_30d",
            "lag_1d",
            "lag_7d",
        ]
        self.model_metrics: Dict[str, float] = {}
        self._load_model()

    def _load_model(self):
        """Load pre-trained model if exists."""
        if Path(self.MODEL_PATH).exists():
            try:
                data = joblib.load(self.MODEL_PATH)
                self.model = data["model"]
                self.model_metrics = data.get("metrics", {})
                logger.info("Loaded existing sales prediction model")
            except Exception as e:
                logger.warning(f"Could not load model: {e}")

    def _save_model(self):
        """Save trained model."""
        Path(self.MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "features": self.feature_columns,
                "metrics": self.model_metrics,
            },
            self.MODEL_PATH,
        )

    async def train(
        self,
        sales_data: List[Dict[str, Any]],
        menu_items: List[Dict[str, Any]],
        image_scores: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Train the prediction model on provided data."""

        logger.info(f"Training predictor with {len(sales_data)} records")

        price_lookup = {item["name"]: item.get("price", 0) for item in menu_items}
        df = self._prepare_training_data(sales_data, price_lookup, image_scores)

        if len(df) < 10:
            logger.warning("Insufficient data, generating synthetic data")
            df = self._generate_synthetic_data(menu_items, image_scores)

        X = df[self.feature_columns].fillna(0)
        y = df["units_sold"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective="reg:squarederror",
            random_state=42,
        )
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        self.model_metrics = {
            "mae": round(mean_absolute_error(y_test, y_pred), 2),
            "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
            "training_samples": len(X_train),
            "trained_at": datetime.utcnow().isoformat(),
        }

        self._save_model()

        return {
            "status": "trained",
            "metrics": self.model_metrics,
            "feature_importance": dict(
                zip(self.feature_columns, self.model.feature_importances_.tolist())
            ),
        }

    async def predict(
        self,
        item_name: str,
        horizon_days: int,
        base_features: Dict[str, Any],
        scenarios: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Predict sales for an item over a horizon."""

        if self.model is None:
            return {"error": "Model not trained", "predictions": []}

        scenarios = scenarios or [{"name": "baseline"}]
        results = {}
        start_date = datetime.utcnow().date()

        for scenario in scenarios:
            scenario_name = scenario.get("name", "baseline")
            predictions = []

            for day_offset in range(horizon_days):
                pred_date = start_date + timedelta(days=day_offset)
                features = self._build_features(
                    pred_date, base_features, scenario, predictions
                )
                X = pd.DataFrame([features])[self.feature_columns].fillna(0)
                pred = max(0, self.model.predict(X)[0])
                predictions.append(round(pred, 1))

            results[scenario_name] = {
                "daily_predictions": predictions,
                "total_units": round(sum(predictions)),
                "avg_daily": round(sum(predictions) / horizon_days, 1),
            }

        return {
            "item_name": item_name,
            "horizon_days": horizon_days,
            "predictions": results,
            "model_accuracy_mae": self.model_metrics.get("mae", 0),
        }

    def _prepare_training_data(self, sales_data, price_lookup, image_scores):
        """Prepare training DataFrame from sales records."""
        records = []
        for sale in sales_data:
            item_name = sale.get("item_name")
            sale_date = sale.get("sale_date")
            if not item_name or not sale_date:
                continue
            if isinstance(sale_date, str):
                try:
                    sale_date = datetime.fromisoformat(sale_date).date()
                except ValueError:
                    continue

            records.append(
                {
                    "item_name": item_name,
                    "date": sale_date,
                    "units_sold": sale.get("units_sold", 0),
                    "day_of_week": sale_date.weekday(),
                    "is_weekend": 1 if sale_date.weekday() >= 5 else 0,
                    "price": price_lookup.get(item_name, 0),
                    "promo_flag": 1 if sale.get("had_promotion") else 0,
                    "promo_discount": sale.get("promotion_discount", 0) or 0,
                    "image_score": (image_scores or {}).get(item_name, 0.5),
                }
            )

        df = pd.DataFrame(records)
        if len(df) == 0:
            return df

        df = df.sort_values(["item_name", "date"])
        df["rolling_avg_7d"] = df.groupby("item_name")["units_sold"].transform(
            lambda x: x.rolling(7, min_periods=1).mean()
        )
        df["rolling_avg_30d"] = df.groupby("item_name")["units_sold"].transform(
            lambda x: x.rolling(30, min_periods=1).mean()
        )
        df["lag_1d"] = df.groupby("item_name")["units_sold"].shift(1).fillna(0)
        df["lag_7d"] = df.groupby("item_name")["units_sold"].shift(7).fillna(0)
        return df

    def _generate_synthetic_data(self, menu_items, image_scores):
        """Generate synthetic training data for demo."""
        np.random.seed(42)
        records = []
        start_date = datetime.utcnow().date() - timedelta(days=90)

        for item in menu_items:
            item_name = item["name"]
            base_demand = np.random.uniform(5, 30)

            for day_offset in range(90):
                date = start_date + timedelta(days=day_offset)
                dow = date.weekday()
                dow_mult = 1.3 if dow >= 5 else 1.0
                price = item.get("price", 15)
                price_effect = max(0.5, 1.5 - (price / 50))
                promo = np.random.random() < 0.1
                img_score = (image_scores or {}).get(item_name, 0.5)

                units = int(
                    base_demand
                    * dow_mult
                    * price_effect
                    * (1.3 if promo else 1.0)
                    * (0.8 + img_score * 0.4)
                    * np.random.uniform(0.7, 1.3)
                )

                records.append(
                    {
                        "item_name": item_name,
                        "date": date,
                        "units_sold": max(0, units),
                        "day_of_week": dow,
                        "is_weekend": 1 if dow >= 5 else 0,
                        "price": price,
                        "promo_flag": 1 if promo else 0,
                        "promo_discount": 0.15 if promo else 0,
                        "image_score": img_score,
                    }
                )

        df = pd.DataFrame(records).sort_values(["item_name", "date"])
        df["rolling_avg_7d"] = df.groupby("item_name")["units_sold"].transform(
            lambda x: x.rolling(7, min_periods=1).mean()
        )
        df["rolling_avg_30d"] = df.groupby("item_name")["units_sold"].transform(
            lambda x: x.rolling(30, min_periods=1).mean()
        )
        df["lag_1d"] = df.groupby("item_name")["units_sold"].shift(1).fillna(0)
        df["lag_7d"] = df.groupby("item_name")["units_sold"].shift(7).fillna(0)
        return df

    def _build_features(self, date, base_features, scenario, previous_predictions):
        """Build feature dict for a single prediction."""
        price_change = scenario.get("price_change_percent", 0) / 100
        price = base_features.get("price", 15) * (1 + price_change)
        promo = scenario.get("promotion_active", False)
        discount = scenario.get("promotion_discount", 0) if promo else 0
        marketing_boost = scenario.get("marketing_boost", 1.0)
        image_score = min(1.0, base_features.get("image_score", 0.5) * marketing_boost)

        rolling_7d = (
            sum(previous_predictions[-7:]) / 7
            if len(previous_predictions) >= 7
            else base_features.get("rolling_avg_7d", 10)
        )
        rolling_30d = base_features.get("rolling_avg_30d", rolling_7d)
        lag_1d = previous_predictions[-1] if previous_predictions else rolling_7d
        lag_7d = (
            previous_predictions[-7] if len(previous_predictions) >= 7 else rolling_7d
        )

        return {
            "day_of_week": date.weekday() if hasattr(date, "weekday") else 0,
            "is_weekend": (
                1 if (hasattr(date, "weekday") and date.weekday() >= 5) else 0
            ),
            "price": price,
            "promo_flag": 1 if promo else 0,
            "promo_discount": discount,
            "image_score": image_score,
            "rolling_avg_7d": rolling_7d,
            "rolling_avg_30d": rolling_30d,
            "lag_1d": lag_1d,
            "lag_7d": lag_7d,
        }

    async def predict_batch(
        self,
        items: List[Dict[str, Any]],
        horizon_days: int,
        scenarios: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Predict sales for multiple items under various scenarios."""

        if self.model is None:
            return {
                "error": "Model not trained",
                "item_predictions": [],
                "scenario_totals": {},
            }

        item_predictions = []
        scenario_totals = {
            s.get("name", f"scenario_{i}"): 0 for i, s in enumerate(scenarios)
        }

        for item in items:
            base_features = {
                "price": item.get("price", 15),
                "image_score": item.get("image_score", 0.5),
                "rolling_avg_7d": item.get("avg_daily_units", 10),
                "rolling_avg_30d": item.get("avg_daily_units", 10),
            }

            prediction = await self.predict(
                item["name"], horizon_days, base_features, scenarios
            )

            item_predictions.append(
                {
                    "item_name": item["name"],
                    "predictions": prediction.get("predictions", {}),
                }
            )

            for scenario_name, data in prediction.get("predictions", {}).items():
                if scenario_name in scenario_totals:
                    scenario_totals[scenario_name] += data.get("total_units", 0)

        return {
            "item_predictions": item_predictions,
            "scenario_totals": scenario_totals,
            "horizon_days": horizon_days,
        }
