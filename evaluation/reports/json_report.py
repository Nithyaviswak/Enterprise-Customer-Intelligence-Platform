"""
JSON Report Generator - Machine-readable evaluation results.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from ..types import EvaluationResult, ComparisonResult


class JSONReportGenerator:
    """Generates JSON-formatted reports for programmatic consumption."""

    def generate_result(self, result: EvaluationResult, output_path: Path):
        """Write single evaluation result as JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result.to_dict(), f, indent=2, default=str)

    def generate_results_batch(
        self, results: List[EvaluationResult], output_path: Path
    ):
        """Write multiple results as a JSON array."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(
                [r.to_dict() for r in results],
                f, indent=2, default=str,
            )

    def generate_leaderboard(
        self, results: List[EvaluationResult], output_path: Path
    ):
        """Generate leaderboard JSON sorted by mAP50 descending."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sorted_results = sorted(
            results, key=lambda r: r.metrics.mAP50, reverse=True
        )
        leaderboard = []
        for rank, r in enumerate(sorted_results, 1):
            m = r.metrics
            leaderboard.append({
                "rank": rank,
                "model_name": r.model_name,
                "model_version": r.model_version,
                "timestamp": r.timestamp.isoformat(),
                "dataset": r.dataset,
                "metrics": {
                    "mAP50": m.mAP50,
                    "mAP50_95": m.mAP50_95,
                    "precision": m.precision,
                    "recall": m.recall,
                    "f1_score": m.f1_score,
                    "fps": m.fps,
                    "latency_ms": m.latency_ms,
                    "model_size_mb": m.model_size_mb,
                },
            })
        with open(output_path, "w") as f:
            json.dump(leaderboard, f, indent=2)

    def generate_comparison(
        self, comparison: ComparisonResult, output_path: Path
    ):
        """Write comparison result as JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(comparison.to_dict(), f, indent=2, default=str)
