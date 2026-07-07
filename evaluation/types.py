from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np


@dataclass
class ClassMetrics:
    class_id: int
    class_name: str
    precision: float
    recall: float
    f1_score: float
    ap50: float
    ap50_95: float
    support: int
    tp: int = 0
    fp: int = 0
    fn: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetricsSnapshot:
    precision: float
    recall: float
    f1_score: float
    mAP50: float
    mAP50_95: float
    fps: float
    latency_ms: float
    latency_p99_ms: float
    gpu_memory_mb: float
    model_size_mb: float
    inference_cost_per_image: float
    per_class_metrics: Dict[str, ClassMetrics] = field(default_factory=dict)
    total_images: int = 0
    total_detections: int = 0
    total_ground_truths: int = 0

    def to_dict(self) -> Dict[str, Any]:
        base = asdict(self)
        base["per_class_metrics"] = {
            k: v.to_dict() for k, v in self.per_class_metrics.items()
        }
        return base


@dataclass
class EvaluationResult:
    model_name: str
    model_version: str
    timestamp: datetime
    dataset: str
    metrics: MetricsSnapshot
    confusion_matrix: Optional[np.ndarray] = None
    class_names: List[str] = field(default_factory=list)
    pr_curve_data: Optional[Dict[str, Any]] = None
    failure_cases: Optional[Dict[str, List[str]]] = None
    config: Optional[Dict[str, Any]] = None
    run_id: Optional[str] = None
    git_commit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        if self.confusion_matrix is not None:
            d["confusion_matrix"] = self.confusion_matrix.tolist()
        return d


@dataclass
class ComparisonResult:
    baseline: EvaluationResult
    candidate: EvaluationResult
    metric_deltas: Dict[str, float]
    regression_flags: List[str] = field(default_factory=list)
    is_regression: bool = False
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline": self.baseline.to_dict(),
            "candidate": self.candidate.to_dict(),
            "metric_deltas": self.metric_deltas,
            "regression_flags": self.regression_flags,
            "is_regression": self.is_regression,
            "summary": self.summary,
        }
