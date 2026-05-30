"""Explainable AI Module - Phase 7"""

import pandas as pd
import numpy as np
import shap
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class ModelExplainer:
    """Generate SHAP explanations for model predictions."""

    def __init__(self, model, X_train, X_test=None):
        self.model = model
        self.X_train = X_train
        self.X_test = X_test
        self.explainer = None
        self.shap_values = None

    def create_explainer(self, method: str = "auto"):
        """Create SHAP explainer."""
        if method == "auto":
            # Auto-select best method based on model type
            if hasattr(self.model, "predict_proba"):
                try:
                    self.explainer = shap.TreeExplainer(self.model)
                except Exception:
                    self.explainer = shap.KernelExplainer(self.model.predict, self.X_train)
            else:
                self.explainer = shap.KernelExplainer(self.model.predict, self.X_train)
        elif method == "tree":
            self.explainer = shap.TreeExplainer(self.model)
        elif method == "kernel":
            self.explainer = shap.KernelExplainer(self.model.predict, self.X_train)

        logger.info(f"SHAP explainer created using {method} method")
        return self.explainer

    def compute_shap_values(self, X=None):
        """Compute SHAP values."""
        X = X if X is not None else self.X_test
        if X is None:
            raise ValueError("No data provided for SHAP computation")

        if self.explainer is None:
            self.create_explainer()

        self.shap_values = self.explainer.shap_values(X)

        if isinstance(self.shap_values, list):
            # For binary classification, use positive class
            self.shap_values = self.shap_values[1] if len(self.shap_values) > 1 else self.shap_values[0]

        logger.info(f"Computed SHAP values for {len(X)} samples")
        return self.shap_values

    def get_global_importance(self, top_n: int = 20) -> pd.DataFrame:
        """Get global feature importance."""
        if self.shap_values is None:
            self.compute_shap_values()

        importance = np.abs(self.shap_values).mean(axis=0)
        feature_names = self.X_train.columns if hasattr(self.X_train, "columns") else [f"feature_{i}" for i in range(len(importance))]

        importance_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importance,
        }).sort_values("importance", ascending=False)

        return importance_df.head(top_n)

    def get_local_explanation(self, customer_idx: int) -> pd.DataFrame:
        """Get local SHAP explanation for a single customer."""
        if self.shap_values is None:
            self.compute_shap_values()

        shap_vals = self.shap_values[customer_idx]
        feature_names = self.X_train.columns if hasattr(self.X_train, "columns") else [f"feature_{i}" for i in range(len(shap_vals))]

        explanation = pd.DataFrame({
            "feature": feature_names,
            "shap_value": shap_vals,
            "feature_value": self.X_train.iloc[customer_idx].values,
        }).sort_values("shap_value", key=abs, ascending=False)

        return explanation

    def get_churn_drivers(self, X) -> Dict:
        """Analyze top churn drivers."""
        if self.shap_values is None:
            self.compute_shap_values(X)

        # Get features with highest positive SHAP values (push toward churn)
        mean_shap = np.mean(self.shap_values, axis=0)
        feature_names = X.columns.tolist() if hasattr(X, "columns") else [f"feature_{i}" for i in range(len(mean_shap))]

        driver_df = pd.DataFrame({
            "feature": feature_names,
            "mean_shap": mean_shap,
        }).sort_values("mean_shap", ascending=False)

        return {
            "churn_drivers": driver_df.head(10).to_dict("records"),
            "retention_drivers": driver_df.tail(10).to_dict("records"),
        }

    def generate_waterfall_data(self, customer_idx: int) -> Dict:
        """Generate waterfall plot data for a customer."""
        local_exp = self.get_local_explanation(customer_idx)

        base_value = self.explainer.expected_value
        if isinstance(base_value, (list, np.ndarray)):
            base_value = base_value[1] if len(base_value) > 1 else base_value[0]

        cumulative = base_value
        steps = []

        for _, row in local_exp.iterrows():
            cumulative += row["shap_value"]
            steps.append({
                "feature": row["feature"],
                "value": row["feature_value"],
                "shap": row["shap_value"],
                "cumulative": cumulative,
            })

        return {
            "base_value": base_value,
            "prediction": cumulative,
            "steps": steps,
        }
