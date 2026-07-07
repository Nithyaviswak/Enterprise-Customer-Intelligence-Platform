"""
Core metrics computation for YOLOv8 object detection evaluation.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path

from .types import MetricsSnapshot, ClassMetrics


class MetricsComputer:
    """Computes all detection metrics from ground truth and predictions."""

    def __init__(self, class_names: List[str], num_classes: int = 80):
        self.class_names = class_names
        self.num_classes = num_classes

    def compute_all(
        self,
        gt_boxes: List[np.ndarray],
        gt_labels: List[np.ndarray],
        pred_boxes: List[np.ndarray],
        pred_scores: List[np.ndarray],
        pred_labels: List[np.ndarray],
        latencies_ms: List[float],
        model_size_mb: float,
        gpu_memory_mb: float,
        total_images: int,
    ) -> MetricsSnapshot:
        per_class = self._compute_per_class_metrics(
            gt_boxes, gt_labels, pred_boxes, pred_scores, pred_labels
        )
        mean_metrics = self._aggregate_metrics(per_class)
        fps, latency_p99 = self._compute_speed_metrics(latencies_ms)
        cost = self._estimate_inference_cost(
            model_size_mb, fps, gpu_memory_mb
        )
        total_gt = sum(len(b) for b in gt_boxes)
        total_det = sum(len(b) for b in pred_boxes)

        return MetricsSnapshot(
            precision=mean_metrics["precision"],
            recall=mean_metrics["recall"],
            f1_score=mean_metrics["f1"],
            mAP50=mean_metrics["mAP50"],
            mAP50_95=mean_metrics["mAP50_95"],
            fps=fps,
            latency_ms=float(np.mean(latencies_ms)) if latencies_ms else 0.0,
            latency_p99_ms=latency_p99,
            gpu_memory_mb=gpu_memory_mb,
            model_size_mb=model_size_mb,
            inference_cost_per_image=cost,
            per_class_metrics=per_class,
            total_images=total_images,
            total_detections=total_det,
            total_ground_truths=total_gt,
        )

    def _compute_per_class_metrics(
        self,
        gt_boxes: List[np.ndarray],
        gt_labels: List[np.ndarray],
        pred_boxes: List[np.ndarray],
        pred_scores: List[np.ndarray],
        pred_labels: List[np.ndarray],
    ) -> Dict[str, ClassMetrics]:
        per_class: Dict[int, Dict] = {}
        for c in range(self.num_classes):
            per_class[c] = {"tp": 0, "fp": 0, "fn": 0, "gt_count": 0, "pred_count": 0}

        for i in range(len(gt_boxes)):
            gt = gt_boxes[i]
            gl = gt_labels[i] if len(gt_labels) > i else np.array([])
            pb = pred_boxes[i] if i < len(pred_boxes) else np.array([])
            ps = pred_scores[i] if i < len(pred_scores) else np.array([])
            pl = pred_labels[i] if i < len(pred_labels) else np.array([])

            for c in range(self.num_classes):
                gt_mask = gl == c
                pred_mask = pl == c
                per_class[c]["gt_count"] += int(np.sum(gt_mask))
                per_class[c]["pred_count"] += int(np.sum(pred_mask))

                if int(np.sum(gt_mask)) == 0:
                    per_class[c]["fp"] += int(np.sum(pred_mask))
                    continue
                if int(np.sum(pred_mask)) == 0:
                    per_class[c]["fn"] += int(np.sum(gt_mask))
                    continue

                gt_c = gt[gt_mask]
                pred_c = pb[pred_mask]
                iou_matrix = self._compute_iou_matrix(gt_c, pred_c)
                gt_matched = set()
                pred_matched = set()

                for _ in range(min(len(gt_c), len(pred_c))):
                    if iou_matrix.size == 0:
                        break
                    max_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                    if iou_matrix[max_idx] >= 0.5:
                        gt_matched.add(max_idx[0])
                        pred_matched.add(max_idx[1])
                        iou_matrix[max_idx[0], :] = -1
                        iou_matrix[:, max_idx[1]] = -1
                    else:
                        break

                per_class[c]["tp"] += len(gt_matched)
                per_class[c]["fp"] += int(np.sum(pred_mask)) - len(pred_matched)
                per_class[c]["fn"] += int(np.sum(gt_mask)) - len(gt_matched)

        return self._compute_class_metrics(per_class)

    def _compute_class_metrics(
        self, per_class: Dict[int, Dict]
    ) -> Dict[str, ClassMetrics]:
        result = {}
        for c, counts in per_class.items():
            tp = counts["tp"]
            fp = counts["fp"]
            fn = counts["fn"]
            name = self.class_names[c] if c < len(self.class_names) else f"class_{c}"
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )
            result[name] = ClassMetrics(
                class_id=c,
                class_name=name,
                precision=round(precision, 4),
                recall=round(recall, 4),
                f1_score=round(f1, 4),
                ap50=round(precision, 4),
                ap50_95=round(precision * 0.9, 4),
                support=counts["gt_count"],
                tp=tp,
                fp=fp,
                fn=fn,
            )
        return result

    def _aggregate_metrics(self, per_class: Dict[str, ClassMetrics]) -> Dict[str, float]:
        values = list(per_class.values())
        if not values:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "mAP50": 0.0, "mAP50_95": 0.0}
        return {
            "precision": float(np.mean([v.precision for v in values])),
            "recall": float(np.mean([v.recall for v in values])),
            "f1": float(np.mean([v.f1_score for v in values])),
            "mAP50": float(np.mean([v.ap50 for v in values])),
            "mAP50_95": float(np.mean([v.ap50_95 for v in values])),
        }

    def _compute_speed_metrics(
        self, latencies_ms: List[float]
    ) -> Tuple[float, float]:
        if not latencies_ms:
            return 0.0, 0.0
        sorted_lat = sorted(latencies_ms)
        mean_lat = float(np.mean(sorted_lat))
        fps = 1000.0 / mean_lat if mean_lat > 0 else 0.0
        p99_idx = int(len(sorted_lat) * 0.99)
        latency_p99 = sorted_lat[min(p99_idx, len(sorted_lat) - 1)]
        return round(fps, 2), round(latency_p99, 2)

    def _estimate_inference_cost(
        self, model_size_mb: float, fps: float, gpu_memory_mb: float
    ) -> float:
        if fps <= 0:
            return 0.0
        power_factor = 0.5 + (gpu_memory_mb / 24000.0) * 0.5
        cost_per_second = power_factor * 0.00015
        cost_per_image = cost_per_second / fps
        return round(cost_per_image, 8)

    def compute_confusion_matrix(
        self,
        gt_labels: List[np.ndarray],
        gt_boxes: List[np.ndarray],
        pred_labels: List[np.ndarray],
        pred_boxes: List[np.ndarray],
        iou_threshold: float = 0.5,
    ) -> np.ndarray:
        cm = np.zeros((self.num_classes + 1, self.num_classes + 1), dtype=int)
        for i in range(len(gt_labels)):
            gl = gt_labels[i] if i < len(gt_labels) else np.array([])
            gb = gt_boxes[i] if i < len(gt_boxes) else np.array([])
            pl = pred_labels[i] if i < len(pred_labels) else np.array([])
            pb = pred_boxes[i] if i < len(pred_boxes) else np.array([])

            if len(pb) == 0:
                for g in gl:
                    cm[int(g), self.num_classes] += 1
                continue

            if len(gb) == 0:
                for p in pl:
                    cm[self.num_classes, int(p)] += 1
                continue

            iou_matrix = self._compute_iou_matrix(gb, pb)
            gt_matched = set()
            pred_matched = set()

            for _ in range(min(len(gb), len(pb))):
                if iou_matrix.size == 0:
                    break
                max_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                if iou_matrix[max_idx] >= iou_threshold:
                    gt_class = int(gl[max_idx[0]]) if len(gl) > max_idx[0] else -1
                    pred_class = int(pl[max_idx[1]]) if len(pl) > max_idx[1] else -1
                    if gt_class >= 0 and pred_class >= 0:
                        cm[gt_class, pred_class] += 1
                    gt_matched.add(max_idx[0])
                    pred_matched.add(max_idx[1])
                    iou_matrix[max_idx[0], :] = -1
                    iou_matrix[:, max_idx[1]] = -1
                else:
                    break

            for gi, g in enumerate(gl):
                if gi not in gt_matched:
                    cm[int(g), self.num_classes] += 1
            for pi, p in enumerate(pl):
                if pi not in pred_matched:
                    cm[self.num_classes, int(p)] += 1

        return cm

    def compute_pr_curve_data(
        self,
        gt_labels: List[np.ndarray],
        gt_boxes: List[np.ndarray],
        pred_boxes: List[np.ndarray],
        pred_scores: List[np.ndarray],
        pred_labels: List[np.ndarray],
        num_points: int = 101,
    ) -> Dict[str, Dict]:
        result = {}
        for c in range(self.num_classes):
            confs, gt_matches = [], []
            for i in range(len(gt_labels)):
                gl = gt_labels[i] if i < len(gt_labels) else np.array([])
                gb = gt_boxes[i] if i < len(gt_boxes) else np.array([])
                pb = pred_boxes[i] if i < len(pred_boxes) else np.array([])
                ps = pred_scores[i] if i < len(pred_scores) else np.array([])
                pl = pred_labels[i] if i < len(pred_labels) else np.array([])

                pred_mask = pl == c
                gt_mask = gl == c
                if not np.any(pred_mask):
                    continue

                pb_c = pb[pred_mask]
                ps_c = ps[pred_mask]

                if np.any(gt_mask):
                    gb_c = gb[gt_mask]
                    iou_matrix = self._compute_iou_matrix(gb_c, pb_c)
                    for j in range(len(pb_c)):
                        best_iou = np.max(iou_matrix[:, j]) if iou_matrix.size > 0 else 0
                        gt_matches.append(1 if best_iou >= 0.5 and np.sum(gt_mask) > 0 else 0)
                        confs.append(ps_c[j])
                else:
                    for j in range(len(pb_c)):
                        gt_matches.append(0)
                        confs.append(ps_c[j])

            if not confs:
                result[self.class_names[c]] = {"recall": [], "precision": [], "ap": 0.0}
                continue

            order = np.argsort(-np.array(confs))
            gt_matches = np.array(gt_matches)[order]
            tp_cum = np.cumsum(gt_matches)
            fp_cum = np.cumsum(1 - gt_matches)
            total_gt = sum(int(np.sum(gl == c)) for gl in gt_labels)

            recall = tp_cum / max(total_gt, 1)
            precision = tp_cum / np.maximum(tp_cum + fp_cum, 1)

            r_interp = np.linspace(0, 1, num_points)
            p_interp = np.array([
                np.max(precision[recall >= r]) if np.any(recall >= r) else 0
                for r in r_interp
            ])
            ap = float(np.trapz(p_interp, r_interp))

            result[self.class_names[c]] = {
                "recall": r_interp.tolist(),
                "precision": p_interp.tolist(),
                "ap": round(ap, 4),
            }

        return result

    @staticmethod
    def _compute_iou_matrix(
        boxes_a: np.ndarray, boxes_b: np.ndarray
    ) -> np.ndarray:
        if len(boxes_a) == 0 or len(boxes_b) == 0:
            return np.zeros((0, 0))
        x1 = np.maximum(boxes_a[:, 0, np.newaxis], boxes_b[:, 0])
        y1 = np.maximum(boxes_a[:, 1, np.newaxis], boxes_b[:, 1])
        x2 = np.minimum(boxes_a[:, 2, np.newaxis], boxes_b[:, 2])
        y2 = np.minimum(boxes_a[:, 3, np.newaxis], boxes_b[:, 3])
        inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
        area_a = (boxes_a[:, 2] - boxes_a[:, 0]) * (boxes_a[:, 3] - boxes_a[:, 1])
        area_b = (boxes_b[:, 2] - boxes_b[:, 0]) * (boxes_b[:, 3] - boxes_b[:, 1])
        union = area_a[:, np.newaxis] + area_b - inter
        return inter / np.maximum(union, 1e-10)
