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

# YOLO Evaluation
EVAL_CONFIG = {
    "project_name": os.getenv("EVAL_PROJECT_NAME", "yolo-retail-intelligence"),
    "experiment_name": os.getenv("EVAL_EXPERIMENT_NAME", "model_evaluation"),
    "output_dir": os.getenv("EVAL_OUTPUT_DIR", "evaluation_output"),
    "dataset_dir": os.getenv("EVAL_DATASET_DIR", "data"),
}

YOLO_CONFIG = {
    "imgsz": int(os.getenv("YOLO_IMGSZ", "640")),
    "conf_threshold": float(os.getenv("YOLO_CONF_THRESHOLD", "0.25")),
    "iou_threshold": float(os.getenv("YOLO_IOU_THRESHOLD", "0.45")),
    "device": os.getenv("YOLO_DEVICE", "cpu"),
    "half": os.getenv("YOLO_HALF", "false").lower() == "true",
}
