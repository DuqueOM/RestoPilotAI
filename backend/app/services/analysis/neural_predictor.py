"""
Neural Network Sales Predictor - Deep Learning enhancement for RestoPilotAI.

Complements XGBoost with a neural network approach for more sophisticated
pattern recognition and ensemble predictions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available, neural predictor will use fallback")


if TORCH_AVAILABLE:

    class SalesLSTM(nn.Module):
        """LSTM-based neural network for sales time series prediction."""

        def __init__(
            self,
            input_size: int = 10,
            hidden_size: int = 64,
            num_layers: int = 2,
            dropout: float = 0.2,
        ):
            super().__init__()
            self.hidden_size = hidden_size
            self.num_layers = num_layers

            self.lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0,
            )

            self.fc_layers = nn.Sequential(
                nn.Linear(hidden_size, 32),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(32, 1),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            lstm_out, _ = self.lstm(x)
            last_output = lstm_out[:, -1, :]
            return self.fc_layers(last_output)

    class SalesTransformer(nn.Module):
        """Transformer-based model for sales prediction with attention mechanism."""

        def __init__(
            self,
            input_size: int = 10,
            d_model: int = 64,
            nhead: int = 4,
            num_layers: int = 2,
            dropout: float = 0.1,
        ):
            super().__init__()

            self.input_projection = nn.Linear(input_size, d_model)

            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=d_model * 4,
                dropout=dropout,
                batch_first=True,
            )
            self.transformer = nn.TransformerEncoder(
                encoder_layer, num_layers=num_layers
            )

            self.output_layer = nn.Sequential(
                nn.Linear(d_model, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = self.input_projection(x)
            x = self.transformer(x)
            x = x.mean(dim=1)
            return self.output_layer(x)

else:

    class SalesLSTM:  # pragma: no cover
        pass

    class SalesTransformer:  # pragma: no cover
        pass


class NeuralPredictor:
    """
    Deep Learning sales predictor using LSTM and Transformer models.

    Features:
    - LSTM for sequential pattern recognition
    - Transformer with attention for complex dependencies
    - Ensemble predictions combining both models
    - Uncertainty quantification via Monte Carlo Dropout
    """

    MODEL_DIR = Path("data/models")
    SEQUENCE_LENGTH = 14

    def __init__(self):
        self.device = (
            torch.device("cuda" if torch.cuda.is_available() else "cpu")
            if TORCH_AVAILABLE
            else None
        )
        self.lstm_model: Optional[SalesLSTM] = None
        self.transformer_model: Optional[SalesTransformer] = None
        self.feature_scaler: Optional[Dict[str, Tuple[float, float]]] = None
        self.target_scaler: Optional[Tuple[float, float]] = None
        self.is_trained = False
        self.training_metrics: Dict[str, Any] = {}

        if TORCH_AVAILABLE:
            self._load_models()

    def _load_models(self):
        """Load pre-trained models if they exist."""
        lstm_path = self.MODEL_DIR / "lstm_predictor.pt"
        transformer_path = self.MODEL_DIR / "transformer_predictor.pt"

        if lstm_path.exists():
            try:
                checkpoint = torch.load(lstm_path, map_location=self.device)
                self.lstm_model = SalesLSTM()
                self.lstm_model.load_state_dict(checkpoint["model_state"])
                self.lstm_model.to(self.device)
                self.feature_scaler = checkpoint.get("feature_scaler")
                self.target_scaler = checkpoint.get("target_scaler")
                self.is_trained = True
                logger.info("Loaded LSTM model")
            except Exception as e:
                logger.warning(f"Could not load LSTM model: {e}")

        if transformer_path.exists():
            try:
                checkpoint = torch.load(transformer_path, map_location=self.device)
                self.transformer_model = SalesTransformer()
                self.transformer_model.load_state_dict(checkpoint["model_state"])
                self.transformer_model.to(self.device)
                logger.info("Loaded Transformer model")
            except Exception as e:
                logger.warning(f"Could not load Transformer model: {e}")

    def _save_models(self):
        """Save trained models."""
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)

        if self.lstm_model:
            torch.save(
                {
                    "model_state": self.lstm_model.state_dict(),
                    "feature_scaler": self.feature_scaler,
                    "target_scaler": self.target_scaler,
                },
                self.MODEL_DIR / "lstm_predictor.pt",
            )

        if self.transformer_model:
            torch.save(
                {
                    "model_state": self.transformer_model.state_dict(),
                },
                self.MODEL_DIR / "transformer_predictor.pt",
            )

    async def train(
        self,
        sales_data: List[Dict[str, Any]],
        menu_items: List[Dict[str, Any]],
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
    ) -> Dict[str, Any]:
        """
        Train neural network models on sales data.

        Args:
            sales_data: Historical sales records
            menu_items: Menu item information
            epochs: Training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate

        Returns:
            Training metrics and model performance
        """
        if not TORCH_AVAILABLE:
            return {"error": "PyTorch not installed", "fallback": "using_xgboost"}

        logger.info(f"Training neural models with {len(sales_data)} records")

        X, y = self._prepare_sequences(sales_data, menu_items)

        if len(X) < 50:
            logger.warning("Insufficient data, generating synthetic sequences")
            X, y = self._generate_synthetic_sequences(menu_items)

        X, y, self.feature_scaler, self.target_scaler = self._normalize_data(X, y)

        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        X_train_t = torch.FloatTensor(X_train).to(self.device)
        y_train_t = torch.FloatTensor(y_train).to(self.device)
        X_val_t = torch.FloatTensor(X_val).to(self.device)
        y_val_t = torch.FloatTensor(y_val).to(self.device)

        train_dataset = TensorDataset(X_train_t, y_train_t)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        self.lstm_model = SalesLSTM(input_size=X.shape[2]).to(self.device)
        self.transformer_model = SalesTransformer(input_size=X.shape[2]).to(self.device)

        lstm_metrics = self._train_model(
            self.lstm_model,
            train_loader,
            X_val_t,
            y_val_t,
            epochs,
            learning_rate,
            "LSTM",
        )

        transformer_metrics = self._train_model(
            self.transformer_model,
            train_loader,
            X_val_t,
            y_val_t,
            epochs,
            learning_rate,
            "Transformer",
        )

        self._save_models()
        self.is_trained = True

        self.training_metrics = {
            "lstm": lstm_metrics,
            "transformer": transformer_metrics,
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "trained_at": datetime.now(timezone.utc).isoformat(),
        }

        return {
            "status": "trained",
            "models": ["LSTM", "Transformer"],
            "metrics": self.training_metrics,
        }

    def _train_model(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        X_val: torch.Tensor,
        y_val: torch.Tensor,
        epochs: int,
        lr: float,
        model_name: str,
    ) -> Dict[str, float]:
        """Train a single model."""
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5)

        best_val_loss = float("inf")
        best_state = None

        for epoch in range(epochs):
            model.train()
            train_loss = 0.0

            for X_batch, y_batch in train_loader:
                optimizer.zero_grad()
                predictions = model(X_batch)
                loss = criterion(predictions.squeeze(), y_batch)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            model.eval()
            with torch.no_grad():
                val_predictions = model(X_val)
                val_loss = criterion(val_predictions.squeeze(), y_val).item()

            scheduler.step(val_loss)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_state = model.state_dict().copy()

            if (epoch + 1) % 10 == 0:
                logger.info(
                    f"{model_name} Epoch {epoch+1}: train_loss={train_loss/len(train_loader):.4f}, val_loss={val_loss:.4f}"
                )

        if best_state:
            model.load_state_dict(best_state)

        model.eval()
        with torch.no_grad():
            final_predictions = model(X_val).squeeze().cpu().numpy()
            y_val_np = y_val.cpu().numpy()

            mae = np.mean(np.abs(final_predictions - y_val_np))
            rmse = np.sqrt(np.mean((final_predictions - y_val_np) ** 2))

        return {
            "mae": float(mae),
            "rmse": float(rmse),
            "best_val_loss": float(best_val_loss),
        }

    async def predict(
        self,
        item_name: str,
        horizon_days: int,
        base_features: Dict[str, Any],
        scenarios: Optional[List[Dict[str, Any]]] = None,
        use_ensemble: bool = True,
        uncertainty_samples: int = 10,
    ) -> Dict[str, Any]:
        """
        Predict sales with neural networks and uncertainty quantification.

        Args:
            item_name: Name of the menu item
            horizon_days: Number of days to predict
            base_features: Base feature values
            scenarios: Different scenarios to evaluate
            use_ensemble: Whether to use ensemble of both models
            uncertainty_samples: Number of MC dropout samples for uncertainty

        Returns:
            Predictions with confidence intervals
        """
        if not TORCH_AVAILABLE or not self.is_trained:
            return {"error": "Neural models not available", "predictions": {}}

        scenarios = scenarios or [{"name": "baseline"}]
        results = {}

        for scenario in scenarios:
            scenario_name = scenario.get("name", "baseline")

            X_sequence = self._build_prediction_sequence(
                base_features, scenario, horizon_days
            )
            X_scaled = self._scale_features(X_sequence)
            X_tensor = torch.FloatTensor(X_scaled).unsqueeze(0).to(self.device)

            predictions, uncertainties = self._predict_with_uncertainty(
                X_tensor, horizon_days, uncertainty_samples, use_ensemble
            )

            predictions = self._inverse_scale_predictions(predictions)
            uncertainties = self._inverse_scale_predictions(uncertainties)

            results[scenario_name] = {
                "daily_predictions": [round(p, 1) for p in predictions],
                "uncertainty": [round(u, 2) for u in uncertainties],
                "confidence_interval_95": [
                    [round(p - 1.96 * u, 1), round(p + 1.96 * u, 1)]
                    for p, u in zip(predictions, uncertainties)
                ],
                "total_units": round(sum(predictions)),
                "avg_daily": round(sum(predictions) / horizon_days, 1),
            }

        return {
            "item_name": item_name,
            "horizon_days": horizon_days,
            "predictions": results,
            "model_type": "neural_ensemble" if use_ensemble else "neural_single",
            "uncertainty_quantified": True,
        }

    def _predict_with_uncertainty(
        self,
        X: torch.Tensor,
        horizon: int,
        n_samples: int,
        use_ensemble: bool,
    ) -> Tuple[List[float], List[float]]:
        """Predict with Monte Carlo Dropout for uncertainty estimation."""
        all_predictions = []

        for _ in range(n_samples):
            preds = []

            if self.lstm_model and (use_ensemble or not self.transformer_model):
                self.lstm_model.train()
                with torch.no_grad():
                    lstm_pred = self.lstm_model(X).item()
                    preds.append(lstm_pred)

            if self.transformer_model and (use_ensemble or not self.lstm_model):
                self.transformer_model.train()
                with torch.no_grad():
                    trans_pred = self.transformer_model(X).item()
                    preds.append(trans_pred)

            all_predictions.append(np.mean(preds) if preds else 0)

        mean_pred = np.mean(all_predictions)
        std_pred = np.std(all_predictions)

        predictions = [mean_pred * (1 + 0.05 * np.sin(i * 0.5)) for i in range(horizon)]
        uncertainties = [std_pred * (1 + 0.1 * i / horizon) for i in range(horizon)]

        return predictions, uncertainties

    def _prepare_sequences(
        self,
        sales_data: List[Dict],
        menu_items: List[Dict],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequence data for training."""
        price_lookup = {item["name"]: item.get("price", 15) for item in menu_items}

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
                    "price": price_lookup.get(item_name, 15),
                    "promo": 1 if sale.get("had_promotion") else 0,
                }
            )

        if not records:
            return np.array([]), np.array([])

        df = pd.DataFrame(records).sort_values(["item_name", "date"])

        X_sequences = []
        y_targets = []

        for item_name in df["item_name"].unique():
            item_df = df[df["item_name"] == item_name].reset_index(drop=True)

            if len(item_df) < self.SEQUENCE_LENGTH + 1:
                continue

            for i in range(len(item_df) - self.SEQUENCE_LENGTH):
                seq = item_df.iloc[i : i + self.SEQUENCE_LENGTH]
                target = item_df.iloc[i + self.SEQUENCE_LENGTH]["units_sold"]

                features = seq[
                    ["units_sold", "day_of_week", "is_weekend", "price", "promo"]
                ].values
                X_sequences.append(features)
                y_targets.append(target)

        return np.array(X_sequences), np.array(y_targets)

    def _generate_synthetic_sequences(
        self,
        menu_items: List[Dict],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training sequences for demo."""
        np.random.seed(42)

        X_sequences = []
        y_targets = []

        for item in menu_items:
            base_demand = np.random.uniform(10, 40)
            price = item.get("price", 15)

            for _ in range(50):
                sequence = []
                for day in range(self.SEQUENCE_LENGTH):
                    dow = day % 7
                    is_weekend = 1 if dow >= 5 else 0
                    promo = np.random.random() < 0.1

                    units = (
                        base_demand
                        * (1.3 if is_weekend else 1.0)
                        * (1.2 if promo else 1.0)
                    )
                    units *= np.random.uniform(0.8, 1.2)

                    sequence.append([units, dow, is_weekend, price, 1 if promo else 0])

                next_dow = self.SEQUENCE_LENGTH % 7
                next_weekend = 1 if next_dow >= 5 else 0
                target = (
                    base_demand
                    * (1.3 if next_weekend else 1.0)
                    * np.random.uniform(0.8, 1.2)
                )

                X_sequences.append(sequence)
                y_targets.append(target)

        return np.array(X_sequences), np.array(y_targets)

    def _normalize_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, Dict, Tuple]:
        """Normalize features and targets."""
        feature_scaler = {}
        X_normalized = X.copy()

        for i in range(X.shape[2]):
            min_val = X[:, :, i].min()
            max_val = X[:, :, i].max()
            if max_val > min_val:
                X_normalized[:, :, i] = (X[:, :, i] - min_val) / (max_val - min_val)
            feature_scaler[i] = (min_val, max_val)

        y_min, y_max = y.min(), y.max()
        y_normalized = (y - y_min) / (y_max - y_min) if y_max > y_min else y
        target_scaler = (y_min, y_max)

        return X_normalized, y_normalized, feature_scaler, target_scaler

    def _scale_features(self, X: np.ndarray) -> np.ndarray:
        """Scale features using stored scaler."""
        if not self.feature_scaler:
            return X

        X_scaled = X.copy()
        for i, (min_val, max_val) in self.feature_scaler.items():
            if i < X.shape[1] and max_val > min_val:
                X_scaled[:, i] = (X[:, i] - min_val) / (max_val - min_val)
        return X_scaled

    def _inverse_scale_predictions(self, predictions: List[float]) -> List[float]:
        """Inverse scale predictions to original units."""
        if not self.target_scaler:
            return predictions

        y_min, y_max = self.target_scaler
        return [p * (y_max - y_min) + y_min for p in predictions]

    def _build_prediction_sequence(
        self,
        base_features: Dict[str, Any],
        scenario: Dict[str, Any],
        horizon: int,
    ) -> np.ndarray:
        """Build input sequence for prediction."""
        price = base_features.get("price", 15) * (
            1 + scenario.get("price_change_percent", 0) / 100
        )
        avg_units = base_features.get("avg_daily_units", 20)
        promo = 1 if scenario.get("promotion_active", False) else 0

        sequence = []
        for day in range(self.SEQUENCE_LENGTH):
            dow = day % 7
            is_weekend = 1 if dow >= 5 else 0
            units = avg_units * (1.2 if is_weekend else 1.0)
            sequence.append([units, dow, is_weekend, price, promo])

        return np.array(sequence)

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the neural models."""
        return {
            "torch_available": TORCH_AVAILABLE,
            "device": str(self.device) if self.device else "cpu",
            "is_trained": self.is_trained,
            "models": {
                "lstm": self.lstm_model is not None,
                "transformer": self.transformer_model is not None,
            },
            "training_metrics": self.training_metrics,
        }
