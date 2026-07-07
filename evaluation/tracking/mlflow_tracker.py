"""
MLflow Evaluation Tracker - Logs metrics, artifacts, images, and checkpoints.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    _MLFLOW_AVAILABLE = True
except ImportError:
    _MLFLOW_AVAILABLE = False
    mlflow = None
    MlflowClient = None

from ..types import EvaluationResult, ComparisonResult

logger = logging.getLogger(__name__)


class MLflowEvaluationTracker:
    """MLflow integration for YOLO evaluation tracking."""

    def __init__(
        self,
        tracking_uri: str = "http://localhost:5000",
        experiment_name: str = "yolo-retail-evaluation",
        artifact_location: Optional[str] = None,
    ):
        if not _MLFLOW_AVAILABLE:
            logger.warning("mlflow not installed. Install with: pip install mlflow")
            self.client = None
            self.experiment_name = experiment_name
            self.experiment_id = None
            self._active_run = None
            return

        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()

        experiment = self.client.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(
                experiment_name,
                artifact_location=artifact_location,
            )
            logger.info(f"Created experiment '{experiment_name}' (id={experiment_id})")
        else:
            experiment_id = experiment.experiment_id

        self.experiment_name = experiment_name
        self.experiment_id = experiment_id
        mlflow.set_experiment(experiment_name)
        self._active_run = None

    def start_run(self, run_name: Optional[str] = None) -> Optional[str]:
        """Start a new MLflow run."""
        if not _MLFLOW_AVAILABLE or mlflow is None:
            logger.warning("MLflow not available")
            return None
        self._active_run = mlflow.start_run(run_name=run_name)
        return self._active_run.info.run_id

    def end_run(self):
        """End the active MLflow run."""
        if self._active_run and _MLFLOW_AVAILABLE and mlflow:
            mlflow.end_run()
            self._active_run = None

    def log_evaluation_result(
        self,
        result: EvaluationResult,
        artifact_paths: Optional[Dict[str, str]] = None,
    ):
        """Log full evaluation result as metrics, params, and artifacts."""
        if not _MLFLOW_AVAILABLE:
            logger.warning("MLflow not available. Install with: pip install mlflow")
            return None

        run_id = self.start_run(
            run_name=f"{result.model_name}_v{result.model_version}"
        )
        result.run_id = run_id

        params = {
            "model_name": result.model_name,
            "model_version": result.model_version,
            "dataset": result.dataset,
            "timestamp": result.timestamp.isoformat(),
        }
        if result.git_commit:
            params["git_commit"] = result.git_commit
        if result.config:
            params.update({f"config.{k}": str(v) for k, v in result.config.items()})
        mlflow.log_params(params)

        m = result.metrics
        metrics = {
            "precision": m.precision,
            "recall": m.recall,
            "f1_score": m.f1_score,
            "mAP50": m.mAP50,
            "mAP50_95": m.mAP50_95,
            "fps": m.fps,
            "latency_ms": m.latency_ms,
            "latency_p99": m.latency_p99_ms,
            "gpu_memory_mb": m.gpu_memory_mb,
            "model_size_mb": m.model_size_mb,
            "inference_cost": m.inference_cost_per_image,
            "total_images": m.total_images,
            "total_detections": m.total_detections,
            "total_ground_truths": m.total_ground_truths,
        }
        mlflow.log_metrics(metrics)

        for class_name, cm in m.per_class_metrics.items():
            prefix = f"class_{class_name}"
            mlflow.log_metrics({
                f"{prefix}_precision": cm.precision,
                f"{prefix}_recall": cm.recall,
                f"{prefix}_f1": cm.f1_score,
                f"{prefix}_ap50": cm.ap50,
                f"{prefix}_support": cm.support,
            })

        result_json = result.to_dict()
        local_path = f"_eval_result_{run_id}.json"
        with open(local_path, "w") as f:
            json.dump(result_json, f, indent=2, default=str)
        mlflow.log_artifact(local_path, "evaluation_results")
        Path(local_path).unlink(missing_ok=True)

        if artifact_paths:
            for name, filepath in artifact_paths.items():
                if filepath and Path(filepath).exists():
                    mlflow.log_artifact(filepath, "visualizations")

        if result.config and "model_path" in result.config:
            try:
                mlflow.ultralytics.log_model(
                    result.config["model_path"],
                    artifact_path="yolo_model",
                    registered_model_name=result.model_name,
                )
            except Exception as e:
                logger.warning(f"Could not log model: {e}")

        self.end_run()
        logger.info(f"Logged evaluation result to MLflow run {run_id}")
        return run_id

    def log_comparison(self, comparison: ComparisonResult):
        """Log a regression comparison as a separate MLflow run."""
        if not _MLFLOW_AVAILABLE:
            logger.warning("MLflow not available")
            return

        run_id = self.start_run(
            run_name=f"comparison_{comparison.baseline.model_version}_vs_{comparison.candidate.model_version}"
        )

        mlflow.log_params({
            "comparison_type": "regression",
            "baseline_version": comparison.baseline.model_version,
            "candidate_version": comparison.candidate.model_version,
            "model_name": comparison.baseline.model_name,
            "is_regression": str(comparison.is_regression),
        })

        mlflow.log_metrics(comparison.metric_deltas)

        local_path = f"_comparison_{run_id}.json"
        with open(local_path, "w") as f:
            json.dump(comparison.to_dict(), f, indent=2, default=str)
        mlflow.log_artifact(local_path, "comparisons")
        Path(local_path).unlink(missing_ok=True)

        self.end_run()

    def log_image(self, image_path: str, caption: str = ""):
        """Log a matplotlib figure or image to the active run."""
        if self._active_run and _MLFLOW_AVAILABLE:
            mlflow.log_artifact(image_path, "images")

    def get_best_model(
        self, metric: str = "mAP50", stage: str = "None"
    ) -> Optional[str]:
        """Get the best model URI based on a metric."""
        if not _MLFLOW_AVAILABLE:
            return None
        try:
            client = MlflowClient()
            experiment = client.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return None
            runs = client.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=[f"metrics.{metric} DESC"],
                max_results=1,
            )
            if runs:
                return runs[0].info.run_id
        except Exception as e:
            logger.warning(f"Failed to get best model: {e}")
        return None
