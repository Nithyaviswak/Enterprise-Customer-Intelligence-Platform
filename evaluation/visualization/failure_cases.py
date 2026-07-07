"""
Failure Case Visualization - False Positive and False Negative galleries.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import cv2


class FailureCaseVisualizer:
    """Identifies and visualizes false positive/negative detections."""

    def __init__(
        self,
        class_names: List[str],
        output_dir: Path,
        iou_threshold: float = 0.5,
        confidence_threshold: float = 0.25,
    ):
        self.class_names = class_names
        self.output_dir = Path(output_dir)
        self.iou_threshold = iou_threshold
        self.confidence_threshold = confidence_threshold
        self.fp_cases: List[Dict] = []
        self.fn_cases: List[Dict] = []

    def analyze(
        self,
        image_paths: List[str],
        gt_boxes: List[np.ndarray],
        gt_labels: List[np.ndarray],
        pred_boxes: List[np.ndarray],
        pred_scores: List[np.ndarray],
        pred_labels: List[np.ndarray],
    ):
        """Analyze predictions and identify failure cases."""
        for idx in range(len(image_paths)):
            img_path = image_paths[idx]
            gb = gt_boxes[idx] if idx < len(gt_boxes) else np.empty((0, 4))
            gl = gt_labels[idx] if idx < len(gt_labels) else np.empty((0,), dtype=int)
            pb = pred_boxes[idx] if idx < len(pred_boxes) else np.empty((0, 4))
            ps = pred_scores[idx] if idx < len(pred_scores) else np.empty((0,))
            pl = pred_labels[idx] if idx < len(pred_labels) else np.empty((0,), dtype=int)

            gt_matched = set()
            pred_matched = set()

            if len(gb) > 0 and len(pb) > 0:
                iou_matrix = self._compute_iou(gb, pb)
                for _ in range(min(len(gb), len(pb))):
                    if iou_matrix.size == 0:
                        break
                    max_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                    if iou_matrix[max_idx] >= self.iou_threshold:
                        gt_matched.add(max_idx[0])
                        pred_matched.add(max_idx[1])
                        iou_matrix[max_idx[0], :] = -1
                        iou_matrix[:, max_idx[1]] = -1
                    else:
                        break

            for gi in range(len(gb)):
                if gi not in gt_matched:
                    self.fn_cases.append({
                        "image_path": img_path,
                        "bbox": gb[gi].tolist(),
                        "class_id": int(gl[gi]),
                        "class_name": self.class_names[int(gl[gi])]
                        if int(gl[gi]) < len(self.class_names)
                        else f"class_{int(gl[gi])}",
                    })

            for pi in range(len(pb)):
                if pi not in pred_matched:
                    self.fp_cases.append({
                        "image_path": img_path,
                        "bbox": pb[pi].tolist(),
                        "score": float(ps[pi]),
                        "class_id": int(pl[pi]),
                        "class_name": self.class_names[int(pl[pi])]
                        if int(pl[pi]) < len(self.class_names)
                        else f"class_{int(pl[pi])}",
                    })

    def generate_fp_gallery(
        self,
        output_path: Path,
        max_cases: int = 50,
        cols: int = 5,
        figsize: tuple = (20, 20),
    ):
        """Generate a gallery of false positive detections."""
        cases = sorted(self.fp_cases, key=lambda x: x["score"], reverse=True)[:max_cases]
        self._draw_gallery(cases, output_path, "False Positives", cols, figsize)

    def generate_fn_gallery(
        self,
        output_path: Path,
        max_cases: int = 50,
        cols: int = 5,
        figsize: tuple = (20, 20),
    ):
        """Generate a gallery of false negative (missed) detections."""
        cases = self.fn_cases[:max_cases]
        self._draw_gallery(cases, output_path, "False Negatives (Missed Detections)", cols, figsize)

    def generate_report(
        self,
        output_path: Path,
        max_fp: int = 30,
        max_fn: int = 30,
    ):
        """Generate combined failure analysis report with FP and FN galleries."""
        fp_path = output_path.parent / "false_positives.png"
        fn_path = output_path.parent / "false_negatives.png"
        self.generate_fp_gallery(fp_path, max_fp)
        self.generate_fn_gallery(fn_path, max_fn)

        lines = [
            "FAILURE CASE ANALYSIS REPORT",
            "=" * 60,
            f"Total False Positives: {len(self.fp_cases)}",
            f"Total False Negatives: {len(self.fn_cases)}",
            "",
            "Top False Positive Classes:",
        ]
        fp_counts = {}
        for c in self.fp_cases:
            fp_counts[c["class_name"]] = fp_counts.get(c["class_name"], 0) + 1
        for cls_name, count in sorted(fp_counts.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  {cls_name}: {count}")

        lines.extend(["", "Top False Negative Classes:"])
        fn_counts = {}
        for c in self.fn_cases:
            fn_counts[c["class_name"]] = fn_counts.get(c["class_name"], 0) + 1
        for cls_name, count in sorted(fn_counts.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  {cls_name}: {count}")

        text = "\n".join(lines)
        with open(output_path, "w") as f:
            f.write(text)

    def _draw_gallery(
        self,
        cases: List[Dict],
        output_path: Path,
        title: str,
        cols: int,
        figsize: tuple,
    ):
        if not cases:
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.text(0.5, 0.5, f"No {title} found", ha="center", va="center", fontsize=14)
            ax.axis("off")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, dpi=100, bbox_inches="tight")
            plt.close(fig)
            return

        rows = int(np.ceil(len(cases) / cols))
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        axes = axes.flatten() if rows > 1 else [axes] if cols == 1 else axes

        for i, ax in enumerate(axes):
            if i < len(cases):
                case = cases[i]
                img = cv2.imread(case["image_path"])
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w = img.shape[:2]
                    bbox = case["bbox"]
                    x1 = int(bbox[0] * w)
                    y1 = int(bbox[1] * h)
                    x2 = int(bbox[2] * w)
                    y2 = int(bbox[3] * h)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    ax.imshow(img)

                label = case.get("class_name", "unknown")
                if "score" in case:
                    label += f" ({case['score']:.2f})"
                ax.set_title(label, fontsize=8)
            ax.axis("off")

        for i in range(len(cases), len(axes)):
            axes[i].axis("off")

        fig.suptitle(title, fontsize=16, fontweight="bold", y=0.98)
        plt.tight_layout()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    @staticmethod
    def _compute_iou(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
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

    @staticmethod
    def _to_relative(bbox: List[float], img_w: int, img_h: int) -> Tuple[int, ...]:
        return (
            int(bbox[0] * img_w),
            int(bbox[1] * img_h),
            int(bbox[2] * img_w),
            int(bbox[3] * img_h),
        )
