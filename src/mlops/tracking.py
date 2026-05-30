"""MLOps Module - Phase 11"""

import mlflow
from mlflow.tracking import MlflowClient
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)


class MLflowTracker:
    """MLflow experiment tracking and model registry."""

    def __init__(self, tracking_uri: str = "http://localhost:5000"):
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()

    def start_run(self, run_name: str, experiment_name: str = "customer_intelligence"):
        """Start an MLflow run."""
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=run_name)
        return run

    def log_params(self, params: Dict[str, Any]):
        """Log parameters."""
        mlflow.log_params(params)

    def log_metrics(self, metrics: Dict[str, float]):
        """Log metrics."""
        mlflow.log_metrics(metrics)

    def log_model(self, model, model_name: str, artifact_path: str = "model"):
        """Log a model."""
        mlflow.sklearn.log_model(model, artifact_path)

    def log_feature_importance(self, importance_df: pd.DataFrame):
        """Log feature importance as a table."""
        importance_df.to_csv("feature_importance.csv", index=False)
        mlflow.log_artifact("feature_importance.csv")

    def register_model(self, model_name: str, version: int = None):
        """Register model to model registry."""
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
        model_version = mlflow.register_model(model_uri, model_name)
        return model_version

    def get_latest_model(self, model_name: str, stage: str = "Production") -> Optional[str]:
        """Get latest model URI from registry."""
        try:
            latest = mlflow.pyfunc.load_model(f"models:/{model_name}/{stage}")
            return latest
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            return None


class ModelRegistry:
    """Model versioning and management."""

    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)

    def save_model(self, model, model_name: str, version: str = "1.0.0"):
        """Save model to disk."""
        path = os.path.join(self.models_dir, f"{model_name}_{version}.pkl")
        joblib.dump(model, path)
        logger.info(f"Model saved to {path}")
        return path

    def load_model(self, model_name: str, version: str = "1.0.0"):
        """Load model from disk."""
        path = os.path.join(self.models_dir, f"{model_name}_{version}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model not found: {path}")
        return joblib.load(path)

    def list_models(self):
        """List all saved models."""
        models = []
        for f in os.listdir(self.models_dir):
            if f.endswith(".pkl"):
                models.append(f.replace(".pkl", ""))
        return models


def run_training_pipeline():
    """Example training pipeline with MLflow."""
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier

    tracker = MLflowTracker()

    with tracker.start_run("training_pipeline"):
        # Generate sample data
        X, y = make_classification(n_samples=1000, n_features=10)
        X_train, X_test, y_train, y_test = train_test_split(X, y)

        # Log parameters
        tracker.log_params({
            "n_estimators": 100,
            "max_depth": 10,
            "test_size": 0.2,
        })

        # Train model
        model = RandomForestClassifier(n_estimators=100, max_depth=10)
        model.fit(X_train, y_train)

        # Log metrics
        from sklearn.metrics import accuracy_score
        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))

        tracker.log_metrics({
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
        })

        # Log model
        tracker.log_model(model, "churn_model")

    logger.info("Training pipeline completed")
