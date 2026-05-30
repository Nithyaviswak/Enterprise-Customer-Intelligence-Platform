import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
CONFIG_DIR = BASE_DIR / "config"

# Database
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "enterprise_ci"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# MLflow
MLFLOW_CONFIG = {
    "tracking_uri": os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"),
    "experiment_name": os.getenv("MLFLOW_EXPERIMENT_NAME", "customer_intelligence"),
}

# API
API_CONFIG = {
    "host": os.getenv("API_HOST", "0.0.0.0"),
    "port": int(os.getenv("API_PORT", 8000)),
    "debug": os.getenv("API_DEBUG", "true").lower() == "true",
}

# Model settings
MODEL_CONFIG = {
    "clv_prediction_months": int(os.getenv("CLV_PREDICTION_MONTHS", 12)),
    "default_model_version": os.getenv("DEFAULT_MODEL_VERSION", "1.0"),
}

# Dashboard
DASHBOARD_CONFIG = {
    "port": int(os.getenv("DASHBOARD_PORT", 8501)),
}

# Causal inference
CAUSAL_CONFIG = {
    "confidence": float(os.getenv("CAUSAL_EFFECT_CONFIDENCE", 0.95)),
}
