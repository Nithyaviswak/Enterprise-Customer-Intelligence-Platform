"""
Model Leaderboard - Rank and compare models by performance metrics.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from ..types import EvaluationResult

logger = logging.getLogger(__name__)


class ModelLeaderboard:
    """Ranks models by configurable metrics and generates leaderboards."""

    def __init__(self, registry, output_dir: str = "evaluation_output"):
        self.registry = registry
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        metric: str = "mAP50",
        descending: bool = True,
        top_k: int = 20,
        output_path: Optional[Path] = None,
    ) -> Dict:
        """Generate a leaderboard sorted by the given metric."""
        results = self.registry.query_experiments(limit=500)
        allowed_metrics = {
            "mAP50", "mAP50_95", "precision", "recall",
            "f1_score", "fps", "latency_ms", "model_size_mb",
        }
        if metric not in allowed_metrics:
            raise ValueError(f"Invalid metric. Choose from {allowed_metrics}")

        sorted_results = sorted(
            results,
            key=lambda r: r.get(metric, 0),
            reverse=descending,
        )[:top_k]

        entries = []
        for rank, r in enumerate(sorted_results, 1):
            entry = {
                "rank": rank,
                "model_name": r.get("model_name", "unknown"),
                "model_version": r.get("model_version", "unknown"),
                "timestamp": r.get("timestamp", ""),
                "dataset": r.get("dataset", ""),
                "sort_metric": metric,
                "sort_value": r.get(metric, 0),
            }
            for m in allowed_metrics:
                entry[m] = r.get(m, 0)
            entries.append(entry)

        leaderboard = {
            "generated_at": datetime.utcnow().isoformat(),
            "sort_metric": metric,
            "descending": descending,
            "total_entries": len(sorted_results),
            "entries": entries,
        }

        output = output_path or (self.output_dir / "leaderboard.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            json.dump(leaderboard, f, indent=2)
        logger.info(f"Leaderboard saved to {output}")

        return leaderboard

    def generate_multi_metric(
        self, top_k: int = 20, output_path: Optional[Path] = None
    ) -> Dict:
        """Generate a multi-metric leaderboard with composite scoring."""
        results = self.registry.query_experiments(limit=500)

        weighted_results = []
        for r in results:
            score = (
                r.get("mAP50", 0) * 0.30 +
                r.get("mAP50_95", 0) * 0.20 +
                r.get("precision", 0) * 0.15 +
                r.get("recall", 0) * 0.15 +
                r.get("f1_score", 0) * 0.10 +
                min(r.get("fps", 0) / 100, 1) * 0.10
            )
            weighted_results.append((score, r))

        weighted_results.sort(key=lambda x: x[0], reverse=True)

        entries = []
        for rank, (score, r) in enumerate(weighted_results[:top_k], 1):
            entries.append({
                "rank": rank,
                "model_name": r.get("model_name", "unknown"),
                "model_version": r.get("model_version", "unknown"),
                "composite_score": round(score, 4),
                "timestamp": r.get("timestamp", ""),
                "dataset": r.get("dataset", ""),
                "mAP50": r.get("mAP50", 0),
                "mAP50_95": r.get("mAP50_95", 0),
                "precision": r.get("precision", 0),
                "recall": r.get("recall", 0),
                "f1_score": r.get("f1_score", 0),
                "fps": r.get("fps", 0),
            })

        result = {
            "generated_at": datetime.utcnow().isoformat(),
            "sort_metric": "composite_score",
            "weighting": {"mAP50": 0.30, "mAP50_95": 0.20, "precision": 0.15,
                          "recall": 0.15, "f1_score": 0.10, "fps_normalized": 0.10},
            "total_entries": len(entries),
            "entries": entries,
        }

        output = output_path or (self.output_dir / "leaderboard_composite.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            json.dump(result, f, indent=2)
        logger.info(f"Multi-metric leaderboard saved to {output}")
        return result

    def format_markdown(self, leaderboard: Dict) -> str:
        """Format a leaderboard dict as a markdown table."""
        lines = [
            f"# Model Leaderboard",
            f"",
            f"Generated: {leaderboard.get('generated_at', '')}",
            f"Sorted by: **{leaderboard.get('sort_metric', 'mAP50')}**",
            f"",
            f"| Rank | Model | Version | {leaderboard['sort_metric']} | mAP50 | mAP50-95 | Precision | Recall | F1 | FPS |",
            f"|------|-------|---------|{'-'*12}|{'─'*8}|{'─'*10}|{'─'*11}|{'─'*8}|{'─'*5}|{'─'*5}|",
        ]
        for entry in leaderboard.get("entries", []):
            lines.append(
                f"| {entry['rank']} | {entry['model_name']} "
                f"| {entry['model_version']} "
                f"| {entry.get('sort_value', 0):.4f} "
                f"| {entry.get('mAP50', 0):.4f} "
                f"| {entry.get('mAP50_95', 0):.4f} "
                f"| {entry.get('precision', 0):.4f} "
                f"| {entry.get('recall', 0):.4f} "
                f"| {entry.get('f1_score', 0):.4f} "
                f"| {entry.get('fps', 0):.1f} |"
            )
        return "\n".join(lines)
