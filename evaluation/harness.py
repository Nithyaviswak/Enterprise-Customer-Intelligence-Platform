"""
Evaluation Harness - Orchestrates model loading, inference, metric computation,
and result persistence for YOLOv8 retail object detection models.
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import subprocess
import numpy as np
from dataclasses import asdict

from .types import EvaluationResult, MetricsSnapshot
from .config import EvaluationConfig, YOLOConfig
from .metrics import MetricsComputer

logger = logging.getLogger(__name__)


class EvaluationHarness:
    """Production evaluation harness for YOLO models."""

    def __init__(
        self,
        eval_config: Optional[EvaluationConfig] = None,
        yolo_config: Optional[YOLOConfig] = None,
    ):
        self.eval_config = eval_config or EvaluationConfig.from_env()
        self.yolo_config = yolo_config or YOLOConfig()
        self.eval_config.ensure_dirs()
        self._model = None
        self._model_path = None

    def load_model(self, model_path: str):
        """Load a YOLO model from path."""
        from ultralytics import YOLO
        self._model_path = model_path
        self._model = YOLO(model_path)
        logger.info(f"Loaded model from {model_path}")
        return self._model

    def unload_model(self):
        """Unload model to free GPU memory."""
        self._model = None
        self._model_path = None
        import gc
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except (ImportError, RuntimeError):
            pass

    def evaluate(
        self,
        model_path: str,
        dataset_path: str,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
    ) -> EvaluationResult:
        """Run full evaluation on a model and dataset."""
        model = self.load_model(model_path)
        model_name = model_name or Path(model_path).stem
        model_version = model_version or self._get_model_version(model_path)

        gt_boxes, gt_labels = self._load_ground_truth(dataset_path)
        pred_boxes, pred_scores, pred_labels, latencies = self._run_inference(
            model, dataset_path
        )
        model_size = self._get_model_size(model_path)
        gpu_memory = self._get_gpu_memory()
        num_images = len(gt_boxes)

        computer = MetricsComputer(
            class_names=self.eval_config.class_names,
            num_classes=len(self.eval_config.class_names),
        )

        metrics = computer.compute_all(
            gt_boxes, gt_labels,
            pred_boxes, pred_scores, pred_labels,
            latencies, model_size, gpu_memory, num_images,
        )

        cm = computer.compute_confusion_matrix(
            gt_labels, gt_boxes, pred_labels, pred_boxes
        )
        pr_data = computer.compute_pr_curve_data(
            gt_labels, gt_boxes, pred_boxes, pred_scores, pred_labels
        )

        result = EvaluationResult(
            model_name=model_name,
            model_version=model_version,
            timestamp=datetime.utcnow(),
            dataset=Path(dataset_path).name,
            metrics=metrics,
            confusion_matrix=cm,
            class_names=self.eval_config.class_names,
            pr_curve_data=pr_data,
            config=asdict(self.yolo_config),
        )

        self._save_results(result)
        self.unload_model()
        return result

    def evaluate_multiple(
        self,
        model_configs: List[Dict[str, str]],
        dataset_path: str,
    ) -> List[EvaluationResult]:
        """Evaluate multiple models sequentially and return all results."""
        results = []
        for cfg in model_configs:
            logger.info(f"Evaluating {cfg.get('path', 'unknown')}...")
            result = self.evaluate(
                model_path=cfg["path"],
                dataset_path=dataset_path,
                model_name=cfg.get("name"),
                model_version=cfg.get("version"),
            )
            results.append(result)
        return results

    def benchmark(
        self,
        model_path: str,
        dataset_path: str,
        model_name: Optional[str] = None,
    ) -> Dict:
        """Lightweight benchmark focused on speed metrics only."""
        model = self.load_model(model_path)
        model_name = model_name or Path(model_path).stem

        images = self._load_images(dataset_path)
        latencies = []

        warmup = self.yolo_config.warmup_iterations
        for i in range(min(warmup, len(images))):
            _ = model(images[i], imgsz=self.yolo_config.imgsz, verbose=False)

        num_runs = min(self.yolo_config.num_inference_runs, len(images))
        for i in range(num_runs):
            start = time.perf_counter()
            _ = model(images[i], imgsz=self.yolo_config.imgsz, verbose=False)
            latencies.append((time.perf_counter() - start) * 1000)

        mean_lat = float(np.mean(latencies))
        fps = 1000.0 / mean_lat if mean_lat > 0 else 0
        sorted_lat = sorted(latencies)
        p99 = sorted_lat[int(len(sorted_lat) * 0.99)]

        result = {
            "model_name": model_name,
            "fps": round(fps, 2),
            "latency_mean_ms": round(mean_lat, 2),
            "latency_p99_ms": round(p99, 2),
            "num_runs": num_runs,
            "model_size_mb": round(self._get_model_size(model_path), 2),
            "gpu_memory_mb": round(self._get_gpu_memory(), 2),
        }

        self.unload_model()
        return result

    def _run_inference(
        self, model, dataset_path: str
    ) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray], List[float]]:
        pred_boxes, pred_scores, pred_labels, latencies = [], [], [], []

        images = self._load_images(dataset_path)

        for img in images:
            start = time.perf_counter()
            results = model(img, imgsz=self.yolo_config.imgsz, verbose=False)
            latencies.append((time.perf_counter() - start) * 1000)

            r = results[0]
            if r.boxes is not None and len(r.boxes) > 0:
                pred_boxes.append(r.boxes.xyxy.cpu().numpy())
                pred_scores.append(r.boxes.conf.cpu().numpy())
                pred_labels.append(r.boxes.cls.cpu().numpy().astype(int))
            else:
                pred_boxes.append(np.empty((0, 4)))
                pred_scores.append(np.empty((0,)))
                pred_labels.append(np.empty((0,), dtype=int))

        return pred_boxes, pred_scores, pred_labels, latencies

    def _load_ground_truth(
        self, dataset_path: str
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        gt_boxes, gt_labels = [], []
        path = Path(dataset_path)

        if path.is_dir():
            label_dir = path / "labels"
            image_dir = path / "images"
            if not label_dir.exists():
                logger.warning(f"No labels directory found at {label_dir}")
                for img_file in sorted(image_dir.glob("*.*")):
                    gt_boxes.append(np.empty((0, 4)))
                    gt_labels.append(np.empty((0,), dtype=int))
                return gt_boxes, gt_labels

            for label_file in sorted(label_dir.glob("*.txt")):
                boxes, labels = self._parse_yolo_label(label_file)
                gt_boxes.append(boxes)
                gt_labels.append(labels)
        else:
            with open(path) as f:
                data = json.load(f)
            for item in data:
                boxes = np.array(item["boxes"], dtype=float).reshape(-1, 4)
                labels = np.array(item["labels"], dtype=int)
                gt_boxes.append(boxes)
                gt_labels.append(labels)

        return gt_boxes, gt_labels

    def _load_images(self, dataset_path: str) -> List:
        from ultralytics.utils import DEFAULT_CFG
        path = Path(dataset_path)
        images = []

        if path.is_dir():
            img_dir = path / "images" if (path / "images").exists() else path
            exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
            for f in sorted(img_dir.glob("*.*")):
                if f.suffix.lower() in exts:
                    images.append(str(f))
        return images

    def _save_results(self, result: EvaluationResult):
        output = self.eval_config.output_path
        result_file = output / f"eval_{result.model_name}_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2, default=str)
        logger.info(f"Results saved to {result_file}")

    def _get_model_size(self, model_path: str) -> float:
        return Path(model_path).stat().st_size / (1024 * 1024)

    def _get_gpu_memory(self) -> float:
        try:
            import torch
            if torch.cuda.is_available():
                return torch.cuda.memory_allocated() / (1024 * 1024)
        except (ImportError, RuntimeError):
            pass
        return 0.0

    def _get_model_version(self, model_path: str) -> str:
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-1", "--", model_path],
                capture_output=True, text=True, cwd=Path(model_path).parent
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split()[0]
        except Exception:
            pass
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def _parse_yolo_label(
        label_path: Path,
    ) -> Tuple[np.ndarray, np.ndarray]:
        boxes, labels = [], []
        if not label_path.exists():
            return np.empty((0, 4)), np.empty((0,), dtype=int)
        with open(label_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    labels.append(int(parts[0]))
                    cx, cy, w, h = map(float, parts[1:5])
                    x1 = cx - w / 2
                    y1 = cy - h / 2
                    x2 = cx + w / 2
                    y2 = cy + h / 2
                    boxes.append([x1, y1, x2, y2])
        return np.array(boxes) if boxes else np.empty((0, 4)), np.array(labels, dtype=int) if labels else np.empty((0,), dtype=int)
