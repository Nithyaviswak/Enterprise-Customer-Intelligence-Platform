"""Churn Prediction Module - Phase 5"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
import optuna
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ChurnPredictor:
    """Train and evaluate churn prediction models."""

    def __init__(self, df: pd.DataFrame, target_col: str = "churn"):
        self.df = df
        self.target_col = target_col
        self.models = {}
        self.best_model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def prepare_data(
        self, features: list, test_size: float = 0.2, random_state: int = 42
    ) -> Tuple:
        """Prepare train/test splits."""
        X = self.df[features].fillna(0)
        y = self.df[self.target_col]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        logger.info(f"Train size: {len(self.X_train)}, Test size: {len(self.X_test)}")
        return self.X_train, self.X_test, self.y_train, self.y_test

    def train_logistic_regression(self) -> Dict:
        """Train Logistic Regression baseline."""
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(self.X_train, self.y_train)

        self.models["logistic_regression"] = model
        return self._evaluate_model(model, "Logistic Regression")

    def train_random_forest(self, **kwargs) -> Dict:
        """Train Random Forest model."""
        model = RandomForestClassifier(
            n_estimators=kwargs.get("n_estimators", 100),
            max_depth=kwargs.get("max_depth", 10),
            random_state=kwargs.get("random_state", 42),
            n_jobs=-1,
        )
        model.fit(self.X_train, self.y_train)

        self.models["random_forest"] = model
        return self._evaluate_model(model, "Random Forest")

    def train_xgboost(self, **kwargs) -> Dict:
        """Train XGBoost model."""
        model = XGBClassifier(
            n_estimators=kwargs.get("n_estimators", 100),
            max_depth=kwargs.get("max_depth", 6),
            learning_rate=kwargs.get("learning_rate", 0.1),
            random_state=kwargs.get("random_state", 42),
            use_label_encoder=False,
            eval_metric="logloss",
            verbosity=0,
        )
        model.fit(self.X_train, self.y_train)

        self.models["xgboost"] = model
        return self._evaluate_model(model, "XGBoost")

    def train_lightgbm(self, **kwargs) -> Dict:
        """Train LightGBM model."""
        model = LGBMClassifier(
            n_estimators=kwargs.get("n_estimators", 100),
            max_depth=kwargs.get("max_depth", 6),
            learning_rate=kwargs.get("learning_rate", 0.1),
            random_state=kwargs.get("random_state", 42),
            verbose=-1,
        )
        model.fit(self.X_train, self.y_train)

        self.models["lightgbm"] = model
        return self._evaluate_model(model, "LightGBM")

    def train_catboost(self, **kwargs) -> Dict:
        """Train CatBoost model."""
        model = CatBoostClassifier(
            iterations=kwargs.get("iterations", 100),
            depth=kwargs.get("depth", 6),
            learning_rate=kwargs.get("learning_rate", 0.1),
            random_state=kwargs.get("random_state", 42),
            verbose=0,
        )
        model.fit(self.X_train, self.y_train)

        self.models["catboost"] = model
        return self._evaluate_model(model, "CatBoost")

    def _evaluate_model(self, model, name: str) -> Dict:
        """Evaluate model performance."""
        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]

        metrics = {
            "model": name,
            "accuracy": accuracy_score(self.y_test, y_pred),
            "precision": precision_score(self.y_test, y_pred, zero_division=0),
            "recall": recall_score(self.y_test, y_pred, zero_division=0),
            "f1_score": f1_score(self.y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(self.y_test, y_pred_proba),
            "pr_auc": average_precision_score(self.y_test, y_pred_proba),
        }

        logger.info(f"{name} - ROC-AUC: {metrics['roc_auc']:.4f}, F1: {metrics['f1_score']:.4f}")
        return metrics

    def compare_models(self) -> pd.DataFrame:
        """Compare all trained models."""
        results = []
        for name, model in self.models.items():
            metrics = self._evaluate_model(model, name)
            results.append(metrics)

        comparison = pd.DataFrame(results)
        comparison = comparison.sort_values("roc_auc", ascending=False)

        self.best_model = comparison.iloc[0]["model"]
        logger.info(f"Best model: {self.best_model}")

        return comparison

    def cross_validate(self, model_name: str, cv: int = 5) -> Dict:
        """Perform cross-validation on a model."""
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not found")

        cv_scores = cross_val_score(
            model, self.X_train, self.y_train, cv=cv, scoring="roc_auc"
        )

        return {
            "model": model_name,
            "cv_scores": cv_scores.tolist(),
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
        }

    def optimize_hyperparameters(
        self, model_name: str, n_trials: int = 50
    ) -> Dict:
        """Optimize hyperparameters using Optuna."""
        if model_name == "xgboost":
            return self._optimize_xgboost(n_trials)
        elif model_name == "lightgbm":
            return self._optimize_lightgbm(n_trials)
        else:
            logger.warning(f"Hyperparameter optimization not supported for {model_name}")
            return {}

    def _optimize_xgboost(self, n_trials: int) -> Dict:
        """Optimize XGBoost hyperparameters."""
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            }

            model = XGBClassifier(**params, random_state=42, verbosity=0, use_label_encoder=False)
            model.fit(self.X_train, self.y_train)

            y_pred_proba = model.predict_proba(self.X_test)[:, 1]
            return roc_auc_score(self.y_test, y_pred_proba)

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

        best_params = study.best_params
        best_score = study.best_value

        # Train with best params
        best_model = XGBClassifier(**best_params, random_state=42, verbosity=0, use_label_encoder=False)
        best_model.fit(self.X_train, self.y_train)
        self.models["xgboost_optimized"] = best_model

        return {
            "best_params": best_params,
            "best_roc_auc": best_score,
        }

    def _optimize_lightgbm(self, n_trials: int) -> Dict:
        """Optimize LightGBM hyperparameters."""
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
                "num_leaves": trial.suggest_int("num_leaves", 20, 100),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            }

            model = LGBMClassifier(**params, random_state=42, verbose=-1)
            model.fit(self.X_train, self.y_train)

            y_pred_proba = model.predict_proba(self.X_test)[:, 1]
            return roc_auc_score(self.y_test, y_pred_proba)

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

        best_params = study.best_params
        best_score = study.best_value

        # Train with best params
        best_model = LGBMClassifier(**best_params, random_state=42, verbose=-1)
        best_model.fit(self.X_train, self.y_train)
        self.models["lightgbm_optimized"] = best_model

        return {
            "best_params": best_params,
            "best_roc_auc": best_score,
        }

    def get_feature_importance(self, model_name: str) -> pd.DataFrame:
        """Get feature importance from a model."""
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not found")

        if hasattr(model, "feature_importances_"):
            importance = pd.DataFrame({
                "feature": self.X_train.columns,
                "importance": model.feature_importances_,
            }).sort_values("importance", ascending=False)
            return importance

        return pd.DataFrame()
