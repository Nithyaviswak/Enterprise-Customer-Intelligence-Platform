"""
Confusion Matrix visualization for object detection evaluation.
"""

from typing import List, Optional
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    output_path: Path,
    title: str = "Confusion Matrix",
    normalize: bool = False,
    figsize: tuple = (20, 18),
    dpi: int = 150,
):
    """Generate a publication-quality confusion matrix heatmap.

    Args:
        cm: Confusion matrix array (num_classes+1 x num_classes+1).
        class_names: List of class names (excluding background).
        output_path: Where to save the figure.
        title: Plot title.
        normalize: Whether to normalize rows.
        figsize: Figure dimensions.
        dpi: Output resolution.
    """
    num_classes = len(class_names)
    labels = class_names + ["Background"]

    if normalize:
        row_sums = cm.sum(axis=1, keepdims=True)
        cm_display = np.divide(
            cm, row_sums, out=np.zeros_like(cm, dtype=float), where=row_sums != 0
        )
        fmt = ".2f"
        vmin, vmax = 0, 1
    else:
        cm_display = cm
        fmt = "d"
        vmin, vmax = 0, cm.max() if cm.max() > 0 else 1

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        cm_display,
        annot=True,
        fmt=fmt,
        xticklabels=labels,
        yticklabels=labels,
        cmap="Blues",
        vmin=vmin,
        vmax=vmax,
        cbar_kws={"shrink": 0.8, "label": "Count" if not normalize else "Proportion"},
        ax=ax,
    )

    ax.set_xlabel("Predicted", fontsize=14, fontweight="bold")
    ax.set_ylabel("Ground Truth", fontsize=14, fontweight="bold")
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.tick_params(axis="y", rotation=0, labelsize=8)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
