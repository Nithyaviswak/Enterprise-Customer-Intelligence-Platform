"""
Enterprise YOLOv8 Evaluation Platform
=====================================
Production-grade evaluation harness for retail object detection models.
"""

from .types import EvaluationResult, MetricsSnapshot, ComparisonResult, ClassMetrics
from .config import EvaluationConfig, YOLOConfig
from .metrics import MetricsComputer
from .harness import EvaluationHarness
from .regression import RegressionTracker

__version__ = "2.0.0"
__all__ = [
    "EvaluationResult",
    "MetricsSnapshot",
    "ComparisonResult",
    "ClassMetrics",
    "EvaluationConfig",
    "YOLOConfig",
    "MetricsComputer",
    "EvaluationHarness",
    "RegressionTracker",
]
