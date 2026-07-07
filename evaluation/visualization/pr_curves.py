"""
Precision-Recall Curve visualization for object detection evaluation.
"""

from typing import Dict, List, Optional
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_pr_curves(
    pr_data: Dict[str, Dict],
    output_path: Path,
    title: str = "Precision-Recall Curves",
    figsize: tuple = (12, 10),
    dpi: int = 150,
    max_classes: int = 40,
):
    """Generate Precision-Recall curves per class and mean.

    Args:
        pr_data: Nested dict mapping class_name -> {recall, precision, ap}.
        output_path: Output file path.
        title: Plot title.
        figsize: Figure dimensions.
        dpi: Output resolution.
        max_classes: Max classes to show individually.
    """
    fig, ax = plt.subplots(figsize=figsize)

    mean_ap = np.mean([v["ap"] for v in pr_data.values()]) if pr_data else 0.0
    class_items = sorted(
        pr_data.items(), key=lambda x: x[1]["ap"], reverse=True
    )

    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    color_cycle = [colors[i % len(colors)] for i in range(len(class_items))]

    for i, (cls_name, data) in enumerate(class_items):
        if i >= max_classes:
            continue
        label = f"{cls_name} (AP={data['ap']:.3f})"
        ax.plot(
            data["recall"],
            data["precision"],
            color=color_cycle[i],
            alpha=0.6,
            linewidth=1.0,
            label=label,
        )

    ax.set_xlabel("Recall", fontsize=13, fontweight="bold")
    ax.set_ylabel("Precision", fontsize=13, fontweight="bold")
    ax.set_title(f"{title}\nMean AP = {mean_ap:.4f}", fontsize=14, fontweight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", fontsize=6, ncol=2, framealpha=0.8)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_mean_pr_curve(
    pr_data: Dict[str, Dict],
    output_path: Path,
    title: str = "Mean Precision-Recall Curve",
    figsize: tuple = (8, 6),
    dpi: int = 150,
):
    """Plot the mean PR curve across all classes with confidence interval."""
    if not pr_data:
        return

    recalls = np.linspace(0, 1, 101)
    precisions = []
    for cls_name, data in pr_data.items():
        if data["recall"]:
            interp = np.interp(recalls, data["recall"], data["precision"])
            precisions.append(interp)

    if not precisions:
        return

    precisions = np.array(precisions)
    mean_prec = np.mean(precisions, axis=0)
    std_prec = np.std(precisions, axis=0)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(recalls, mean_prec, "b-", linewidth=2, label="Mean PR")
    ax.fill_between(
        recalls,
        np.clip(mean_prec - std_prec, 0, 1),
        np.clip(mean_prec + std_prec, 0, 1),
        alpha=0.2,
        color="blue",
        label="±1 Std Dev",
    )
    ax.set_xlabel("Recall", fontsize=12)
    ax.set_ylabel("Precision", fontsize=12)
    ax.set_title(f"{title}\nmAP = {np.mean(mean_prec):.4f}", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
