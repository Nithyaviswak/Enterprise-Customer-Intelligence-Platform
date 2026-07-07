"""
Regression Tracking - Compares model versions and detects performance regressions.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from .types import EvaluationResult, ComparisonResult
from .config import EvaluationConfig

logger = logging.getLogger(__name__)


class RegressionTracker:
    """Tracks model performance across versions and detects regressions."""

    def __init__(self, config: Optional[EvaluationConfig] = None):
        self.config = config or EvaluationConfig.from_env()
        self.history: List[EvaluationResult] = []
        self._load_history()

    def register_result(self, result: EvaluationResult):
        """Register a new evaluation result and save to history."""
        self.history.append(result)
        self._persist_history()
        logger.info(f"Registered result for {result.model_name} v{result.model_version}")

    def compare(
        self,
        baseline_version: str,
        candidate_version: str,
        model_name: str,
    ) -> ComparisonResult:
        """Compare two model versions and detect regressions."""
        baseline = self._find_result(model_name, baseline_version)
        candidate = self._find_result(model_name, candidate_version)

        if baseline is None:
            raise ValueError(f"Baseline {model_name} v{baseline_version} not found")
        if candidate is None:
            raise ValueError(f"Candidate {model_name} v{candidate_version} not found")

        deltas = {}
        regression_flags = []
        metric_keys = ["mAP50", "mAP50_95", "precision", "recall", "f1_score", "fps"]

        for key in metric_keys:
            b_val = getattr(baseline.metrics, key, 0)
            c_val = getattr(candidate.metrics, key, 0)
            delta = round(c_val - b_val, 4)
            deltas[key] = delta

            threshold = self.config.regression_thresholds.get(key, 0)
            if delta < threshold:
                regression_flags.append(key)

        is_regression = len(regression_flags) > 0
        summary = self._generate_summary(
            baseline, candidate, deltas, regression_flags, is_regression
        )

        return ComparisonResult(
            baseline=baseline,
            candidate=candidate,
            metric_deltas=deltas,
            regression_flags=regression_flags,
            is_regression=is_regression,
            summary=summary,
        )

    def compare_all_versions(
        self, model_name: str
    ) -> List[ComparisonResult]:
        """Compare all consecutive versions of a model."""
        versions = self._get_versions(model_name)
        comparisons = []
        for i in range(1, len(versions)):
            comp = self.compare(versions[i - 1], versions[i], model_name)
            comparisons.append(comp)
        return comparisons

    def get_history(self, model_name: Optional[str] = None) -> List[EvaluationResult]:
        """Get evaluation history, optionally filtered by model name."""
        if model_name:
            return [r for r in self.history if r.model_name == model_name]
        return self.history

    def generate_comparison_report(
        self, comparisons: List[ComparisonResult], output_path: Optional[Path] = None
    ) -> str:
        """Generate formatted comparison report text."""
        lines = ["=" * 80]
        lines.append("MODEL REGRESSION COMPARISON REPORT")
        lines.append(f"Generated: {datetime.utcnow().isoformat()}")
        lines.append("=" * 80)

        for i, comp in enumerate(comparisons):
            lines.append(f"\n--- Comparison {i + 1} ---")
            lines.append(f"Baseline:  {comp.baseline.model_name} v{comp.baseline.model_version}")
            lines.append(f"Candidate: {comp.candidate.model_name} v{comp.candidate.version}")
            lines.append(f"Status:    {'REGRESSION' if comp.is_regression else 'PASS'}")
            lines.append(f"\nMetric Deltas (Candidate - Baseline):")
            lines.append(f"  {'Metric':<20} {'Baseline':<12} {'Candidate':<12} {'Delta':<12}")
            lines.append(f"  {'-'*56}")

            for key, delta in comp.metric_deltas.items():
                b_val = getattr(comp.baseline.metrics, key, 0)
                c_val = getattr(comp.candidate.metrics, key, 0)
                flag = " <<< REGRESSION" if key in comp.regression_flags else ""
                lines.append(f"  {key:<20} {b_val:<12} {c_val:<12} {delta:<+12}{flag}")

            if comp.regression_flags:
                lines.append(f"\n  Regression Flags: {', '.join(comp.regression_flags)}")
            lines.append(f"\n  Summary: {comp.summary}")

        report = "\n".join(lines)

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report)
            logger.info(f"Comparison report saved to {output_path}")

        return report

    def _find_result(
        self, model_name: str, version: str
    ) -> Optional[EvaluationResult]:
        for r in self.history:
            if r.model_name == model_name and r.model_version == version:
                return r
        return None

    def _get_versions(self, model_name: str) -> List[str]:
        return [
            r.model_version
            for r in self.history
            if r.model_name == model_name
        ]

    def _generate_summary(
        self,
        baseline: EvaluationResult,
        candidate: EvaluationResult,
        deltas: Dict[str, float],
        flags: List[str],
        is_regression: bool,
    ) -> str:
        if is_regression:
            parts = [f"REGRESSION detected in {', '.join(flags)}"]
            for key in flags:
                parts.append(
                    f"  {key}: {getattr(baseline.metrics, key):.4f} -> "
                    f"{getattr(candidate.metrics, key):.4f} "
                    f"({deltas[key]:+.4f})"
                )
            return "\n".join(parts)
        improving = [k for k, v in deltas.items() if v > 0]
        if improving:
            return f"All metrics passed. Improvements in {', '.join(improving[:3])}."
        return "All metrics within acceptable thresholds."

    def _load_history(self):
        history_file = self.config.registry_path
        if history_file.exists():
            try:
                with open(history_file) as f:
                    data = json.load(f)
                self.history = [EvaluationResult(**item) for item in data]
                logger.info(f"Loaded {len(self.history)} results from history")
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")

    def _persist_history(self):
        history_file = self.config.registry_path
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, "w") as f:
            json.dump(
                [r.to_dict() for r in self.history],
                f, indent=2, default=str,
            )
