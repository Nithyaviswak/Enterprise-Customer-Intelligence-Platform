"""Customer Lifetime Value Prediction Module - Phase 6"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CLVPredictor:
    """Predict Customer Lifetime Value."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.models = {}
        self.best_model = None

    def prepare_clv_data(
        self,
        customer_id_col: str,
        amount_col: str,
        date_col: str,
        prediction_months: int = 12,
    ) -> pd.DataFrame:
        """Prepare data for CLV prediction."""
        df = self.df.copy()
        df[date_col] = pd.to_datetime(df[date_col])

        # Calculate historical CLV
        clv_data = df.groupby(customer_id_col).agg({
            amount_col: ["sum", "mean", "count"],
            date_col: ["min", "max"],
        }).reset_index()

        clv_data.columns = [
            customer_id_col, "total_revenue", "avg_order_value",
            "order_count", "first_purchase", "last_purchase"
        ]

        # Calculate customer tenure
        clv_data["tenure_days"] = (
            clv_data["last_purchase"] - clv_data["first_purchase"]
        ).dt.days

        # Calculate historical CLV
        clv_data["historical_clv"] = clv_data["total_revenue"]

        # Project future CLV
        avg_monthly = clv_data["total_revenue"] / (clv_data["tenure_days"] / 30 + 1)
        clv_data["projected_clv_12m"] = avg_monthly * prediction_months

        self.df = clv_data
        return clv_data

    def train_regression_clv(
        self, features: list, target_col: str = "projected_clv_12m"
    ) -> Dict:
        """Train regression-based CLV model."""
        X = self.df[features].fillna(0)
        y = self.df[target_col]

        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        lr_pred = lr_model.predict(X_test)

        self.models["linear_regression"] = {
            "model": lr_model,
            "metrics": self._evaluate(y_test, lr_pred),
        }

        # Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)

        self.models["random_forest"] = {
            "model": rf_model,
            "metrics": self._evaluate(y_test, rf_pred),
        }

        # XGBoost
        xgb_model = XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
        xgb_model.fit(X_train, y_train)
        xgb_pred = xgb_model.predict(X_test)

        self.models["xgboost"] = {
            "model": xgb_model,
            "metrics": self._evaluate(y_test, xgb_pred),
        }

        return self.compare_models()

    def _evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Evaluate model predictions."""
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        # Calculate MAPE
        mask = y_true != 0
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

        r2 = r2_score(y_true, y_pred)

        return {
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape,
            "R2": r2,
        }

    def compare_models(self) -> pd.DataFrame:
        """Compare CLV model performance."""
        results = []
        for name, data in self.models.items():
            metrics = data["metrics"]
            metrics["model"] = name
            results.append(metrics)

        df = pd.DataFrame(results).sort_values("RMSE")
        self.best_model = df.iloc[0]["model"]
        return df

    def predict_clv(
        self, customer_ids: list, features: list
    ) -> pd.DataFrame:
        """Predict CLV for new customers."""
        if not self.models:
            raise ValueError("Train models first")

        model_data = self.models.get(self.best_model, self.models["xgboost"])
        model = model_data["model"]

        X = self.df[self.df["customer_id"].isin(customer_ids)][features].fillna(0)
        predictions = model.predict(X)

        return pd.DataFrame({
            "customer_id": customer_ids,
            "predicted_clv": predictions,
        })
