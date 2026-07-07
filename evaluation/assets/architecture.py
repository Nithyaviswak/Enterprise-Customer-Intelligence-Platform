#!/usr/bin/env python3
"""
Architecture Diagram Generator for the YOLOv8 Evaluation Platform.
Generates ASCII architecture diagrams for documentation.

Usage:
    python -m evaluation.assets.architecture
"""

from pathlib import Path


def generate_overview_diagram() -> str:
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║              YOLOv8 Retail Intelligence Evaluation Platform                 ║
║                     Enterprise Model Evaluation Pipeline                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

                              ┌─────────────────┐
                              │   YOLO Model    │
                              │  (.pt file)     │
                              └────────┬────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EVALUATION HARNESS                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Load    │  │Inference │  │  Compute │  │ Compare  │  │  Generate    │  │
│  │  Model   │─▶│  Runner  │─▶│ Metrics  │─▶│Versions  │─▶│   Reports    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────┬───────┘  │
└──────────────────────────────────────────────────────────────────┼──────────┘
                                                                   │
                                   ┌───────────────────────────────┼───────────────────┐
                                   │                               │                   │
                                   ▼                               ▼                   ▼
                          ┌─────────────────┐          ┌─────────────────┐   ┌─────────────────┐
                          │  Visualizations  │          │    Reports      │   │     Tracking    │
                          │  ┌─────────────┐ │          │  ┌───────────┐  │   │  ┌───────────┐  │
                          │  │Confusion    │ │          │  │   HTML    │  │   │  │  MLflow   │  │
                          │  │  Matrix     │ │          │  └───────────┘  │   │  └───────────┘  │
                          │  └─────────────┘ │          │  ┌───────────┐  │   │  ┌───────────┐  │
                          │  ┌─────────────┐ │          │  │   CSV     │  │   │  │   WandB   │  │
                          │  │  PR Curves  │ │          │  └───────────┘  │   │  └───────────┘  │
                          │  └─────────────┘ │          │  ┌───────────┐  │   └─────────────────┘
                          │  ┌─────────────┐ │          │  │   JSON    │  │
                          │  │FP/FN Gallery│ │          │  └───────────┘  │
                          │  └─────────────┘ │          └─────────────────┘
                          └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         REGISTRY & PERSISTENCE                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────────────────────┐ │
│  │   SQLite DB    │  │   Experiment   │  │      Model Leaderboard        │ │
│  │  (registry.db) │  │   Registry     │  │  (JSON / multi-metric sort)   │ │
│  └────────────────┘  └────────────────┘  └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         CI/CD PIPELINE (GitHub Actions)                     │
│                                                                             │
│  Push/PR ──▶ Evaluate ──▶ Compare ──▶ Report ──▶ Leaderboard ──▶ Dashboard │
└─────────────────────────────────────────────────────────────────────────────┘
"""


def generate_data_flow_diagram() -> str:
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           DATA FLOW DIAGRAM                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

                          ┌───────────────────────┐
                          │    YOLO Model (.pt)    │
                          │  ┌─────────────────┐  │
                          │  │  Model Weights   │  │
                          │  └─────────────────┘  │
                          └───────────┬───────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      INFERENCE PIPELINE                               │  │
│  │                                                                       │  │
│  │  ┌──────────┐   ┌──────────┐   ┌───────────┐   ┌──────────────────┐  │  │
│  │  │  Image   │──▶│  Pre-    │──▶│  YOLO     │──▶│  Post-process    │  │  │
│  │  │  Loader  │   │  process │   │  Predict  │   │  (NMS, scaling)  │  │  │
│  │  └──────────┘   └──────────┘   └───────────┘   └────────┬─────────┘  │  │
│  └──────────────────────────────────────────────────────────┼────────────┘  │
└─────────────────────────────────────────────────────────────┼──────────────┘
                                                               │
                    ┌──────────────────────────────────────────┼──────────────┐
                    │                                          ▼              │
                    │  ┌──────────────────────────────────────────────────┐   │
                    │  │            METRICS COMPUTATION                  │   │
                    │  │                                                  │   │
                    │  │  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │   │
                    │  │  │Per-Class │  │ Speed    │  │  Confusion    │  │   │
                    │  │  │ Metrics  │  │ Metrics  │  │  Matrix       │  │   │
                    │  │  └──────────┘  └──────────┘  └───────────────┘  │   │
                    │  │                                                  │   │
                    │  │  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │   │
                    │  │  │    PR    │  │  Failure │  │  Model Size   │  │   │
                    │  │  │  Curves  │  │   Cases  │  │  & GPU Mem    │  │   │
                    │  │  └──────────┘  └──────────┘  └───────────────┘  │   │
                    │  └──────────────────────────────────────────────────┘   │
                    │                                                        │
                    │  METRICS OUTPUT:                                        │
                    │  ┌──────────────────────────────────────────────────┐   │
                    │  │ Precision │ Recall │ F1 │ mAP50 │ mAP50-95      │   │
                    │  │ FPS │ Latency │ GPU Mem │ Model Size │ Cost     │   │
                    │  └──────────────────────────────────────────────────┘   │
                    └────────────────────────────────────────────────────────┘

                    ┌────────────────────────────────────────────────────────┐
                    │              REPORT GENERATION                         │
                    │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
                    │  │   HTML   │  │   CSV    │  │   JSON   │            │
                    │  │ (full    │  │ (tabular │  │ (machine │            │
                    │  │  report) │  │  data)   │  │  readable)            │
                    │  └──────────┘  └──────────┘  └──────────┘            │
                    └────────────────────────────────────────────────────────┘
"""


def generate_module_structure() -> str:
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          MODULE STRUCTURE                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

evaluation/
├── __init__.py              # Package exports
├── config.py                # EvaluationConfig, YOLOConfig
├── types.py                 # Data classes for metrics and results
├── metrics.py               # MetricsComputer - core metric computation
├── harness.py               # EvaluationHarness - orchestration engine
├── regression.py            # RegressionTracker - version comparison
├── benchmark.py             # CLI entry point (python -m evaluation.benchmark)
│
├── visualization/
│   ├── __init__.py
│   ├── confusion_matrix.py  # plot_confusion_matrix()
│   ├── pr_curves.py         # plot_pr_curves(), plot_mean_pr_curve()
│   └── failure_cases.py     # FailureCaseVisualizer with FP/FN galleries
│
├── reports/
│   ├── __init__.py
│   ├── html_report.py       # HTMLReportGenerator
│   ├── csv_report.py        # CSVReportGenerator
│   └── json_report.py       # JSONReportGenerator
│
├── tracking/
│   ├── __init__.py
│   ├── mlflow_tracker.py    # MLflowEvaluationTracker
│   └── wandb_tracker.py     # WandBEvaluationTracker
│
├── registry/
│   ├── __init__.py
│   ├── experiment_registry.py  # ExperimentRegistry (SQLite)
│   └── leaderboard.py          # ModelLeaderboard
│
├── dashboard/
│   ├── __init__.py
│   └── app.py               # Streamlit dashboard
│
└── assets/
    └── architecture.py      # This file - diagram generator
"""


def write_diagrams(output_dir: Path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    diagrams = {
        "overview.txt": generate_overview_diagram,
        "data_flow.txt": generate_data_flow_diagram,
        "module_structure.txt": generate_module_structure,
    }

    for filename, generator in diagrams.items():
        path = output_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(generator())
        print(f"Generated: {path}")


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "docs/architecture"
    write_diagrams(output_dir)
    print(f"\nArchitecture diagrams written to {output_dir}/")
    print("Run: python -m evaluation.assets.architecture docs/architecture")
