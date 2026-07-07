"""
Weights & Biases Evaluation Tracker - Dashboard and experiment tracking.
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..types import EvaluationResult, ComparisonResult

try:
    import wandb
    _WANDB_AVAILABLE = True
except ImportError:
    _WANDB_AVAILABLE = False
    wandb = None

logger = logging.getLogger(__name__)


class WandBEvaluationTracker:
    """WandB integration for YOLO evaluation tracking and dashboarding."""

    def __init__(
        self,
        project: str = "yolo-retail-evaluation",
        entity: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        self.project = project
        self.entity = entity
        self.config = config or {}
        self._run = None

    def init(self, run_name: Optional[str] = None, **kwargs):
        """Initialize a new WandB run."""
        if not _WANDB_AVAILABLE:
            logger.warning("wandb not installed. Install with: pip install wandb")
            return
        try:
            self._run = wandb.init(
                project=self.project,
                entity=self.entity,
                name=run_name,
                config=self.config,
                **kwargs,
            )
            logger.info(f"Initialized WandB run: {self._run.name}")
        except Exception as e:
            logger.warning(f"Failed to initialize WandB: {e}")

    def finish(self):
        """Finish the WandB run."""
        if self._run and _WANDB_AVAILABLE:
            try:
                wandb.finish()
            except Exception:
                pass
            self._run = None

    def log_evaluation_result(
        self,
        result: EvaluationResult,
        artifact_paths: Optional[Dict[str, str]] = None,
    ):
        """Log evaluation result to WandB."""
        if not _WANDB_AVAILABLE:
            logger.warning("wandb not available")
            return
        if not self._run:
            self.init(run_name=f"{result.model_name}_v{result.model_version}")

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
        }

        for class_name, cm in m.per_class_metrics.items():
            metrics[f"class/{class_name}/precision"] = cm.precision
            metrics[f"class/{class_name}/recall"] = cm.recall
            metrics[f"class/{class_name}/f1"] = cm.f1_score
            metrics[f"class/{class_name}/ap50"] = cm.ap50

        try:
            wandb.log(metrics)
        except Exception as e:
            logger.warning(f"Failed to log metrics to WandB: {e}")

        if artifact_paths:
            for name, filepath in artifact_paths.items():
                if filepath and Path(filepath).exists():
                    try:
                        artifact = wandb.Artifact(
                            name=f"{result.model_name}_{name}",
                            type="visualization",
                        )
                        artifact.add_file(filepath)
                        wandb.log_artifact(artifact)
                    except Exception as e:
                        logger.warning(f"Failed to log artifact {name}: {e}")

        if result.confusion_matrix is not None:
            try:
                class_names = result.class_names + ["background"]
                cm_data = []
                for i, gt_name in enumerate(class_names):
                    for j, pred_name in enumerate(class_names):
                        cm_data.append([gt_name, pred_name, int(result.confusion_matrix[i, j])])
                cm_table = wandb.Table(data=cm_data, columns=["Actual", "Predicted", "Count"])
                wandb.log({"confusion_matrix": cm_table})
            except Exception as e:
                logger.warning(f"Failed to log confusion matrix: {e}")

        logger.info(f"Logged evaluation to WandB run {self._run.name if self._run else 'unknown'}")

    def log_comparison(self, comparison: ComparisonResult):
        """Log a regression comparison to WandB."""
        if not _WANDB_AVAILABLE:
            return
        if not self._run:
            self.init(run_name="regression_comparison")

        try:
            wandb.log({
                "comparison/baseline_version": comparison.baseline.model_version,
                "comparison/candidate_version": comparison.candidate.model_version,
                "comparison/is_regression": comparison.is_regression,
                **{f"delta/{k}": v for k, v in comparison.metric_deltas.items()},
            })
        except Exception as e:
            logger.warning(f"Failed to log comparison: {e}")

    def watch_model(self, model):
        """Watch a model during training."""
        if _WANDB_AVAILABLE:
            try:
                wandb.watch(model)
            except Exception:
                pass

    def log_model_summary(self, model_path: str, summary: Dict):
        """Log model architecture summary."""
        if self._run and _WANDB_AVAILABLE:
            try:
                artifact = wandb.Artifact(
                    name=Path(model_path).stem,
                    type="model",
                    metadata=summary,
                )
                artifact.add_file(model_path)
                wandb.log_artifact(artifact)
            except Exception as e:
                logger.warning(f"Failed to log model summary: {e}")
