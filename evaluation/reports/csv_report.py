"""
CSV Report Generator - Tabular evaluation results for analysis.
"""

import csv
from typing import Dict, List, Optional
from pathlib import Path

from ..types import EvaluationResult, MetricsSnapshot


class CSVReportGenerator:
    """Generates CSV reports for evaluation results."""

    def generate_summary(
        self, results: List[EvaluationResult], output_path: Path
    ):
        """Generate summary CSV with one row per model."""
        fieldnames = [
            "model_name", "model_version", "timestamp", "dataset",
            "precision", "recall", "f1_score", "mAP50", "mAP50_95",
            "fps", "latency_ms", "latency_p99_ms",
            "gpu_memory_mb", "model_size_mb", "inference_cost",
            "total_images", "total_detections", "total_ground_truths",
        ]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                m = r.metrics
                writer.writerow({
                    "model_name": r.model_name,
                    "model_version": r.model_version,
                    "timestamp": r.timestamp.isoformat(),
                    "dataset": r.dataset,
                    "precision": m.precision,
                    "recall": m.recall,
                    "f1_score": m.f1_score,
                    "mAP50": m.mAP50,
                    "mAP50_95": m.mAP50_95,
                    "fps": m.fps,
                    "latency_ms": m.latency_ms,
                    "latency_p99_ms": m.latency_p99_ms,
                    "gpu_memory_mb": m.gpu_memory_mb,
                    "model_size_mb": m.model_size_mb,
                    "inference_cost": m.inference_cost_per_image,
                    "total_images": m.total_images,
                    "total_detections": m.total_detections,
                    "total_ground_truths": m.total_ground_truths,
                })

    def generate_detailed(
        self, result: EvaluationResult, output_path: Path
    ):
        """Generate detailed per-class CSV for a single result."""
        fieldnames = [
            "class_name", "class_id", "precision", "recall",
            "f1_score", "ap50", "ap50_95", "support",
            "tp", "fp", "fn",
        ]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for name, cm in sorted(result.metrics.per_class_metrics.items()):
                writer.writerow({
                    "class_name": name,
                    "class_id": cm.class_id,
                    "precision": cm.precision,
                    "recall": cm.recall,
                    "f1_score": cm.f1_score,
                    "ap50": cm.ap50,
                    "ap50_95": cm.ap50_95,
                    "support": cm.support,
                    "tp": cm.tp,
                    "fp": cm.fp,
                    "fn": cm.fn,
                })

    def generate_comparison(
        self, comparisons: List, output_path: Path
    ):
        """Generate CSV for cross-version comparison."""
        fieldnames = [
            "comparison", "baseline_version", "candidate_version",
            "mAP50_delta", "mAP50_95_delta", "precision_delta",
            "recall_delta", "f1_delta", "fps_delta",
            "is_regression", "regression_flags",
        ]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i, comp in enumerate(comparisons):
                writer.writerow({
                    "comparison": i + 1,
                    "baseline_version": comp.baseline.model_version,
                    "candidate_version": comp.candidate.model_version,
                    "mAP50_delta": comp.metric_deltas.get("mAP50", 0),
                    "mAP50_95_delta": comp.metric_deltas.get("mAP50_95", 0),
                    "precision_delta": comp.metric_deltas.get("precision", 0),
                    "recall_delta": comp.metric_deltas.get("recall", 0),
                    "f1_delta": comp.metric_deltas.get("f1_score", 0),
                    "fps_delta": comp.metric_deltas.get("fps", 0),
                    "is_regression": comp.is_regression,
                    "regression_flags": "; ".join(comp.regression_flags),
                })
