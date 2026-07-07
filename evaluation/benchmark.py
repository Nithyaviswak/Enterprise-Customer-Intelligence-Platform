#!/usr/bin/env python3
"""
YOLOv8 Retail Intelligence Benchmark Script
============================================
Automated evaluation pipeline for YOLO models.

Usage:
    python -m evaluation.benchmark evaluate --model models/yolov8n.pt --dataset data/val
    python -m evaluation.benchmark benchmark --model models/yolov8n.pt --dataset data/val
    python -m evaluation.benchmark compare --baseline v1 --candidate v2 --model-name retail_model
    python -m evaluation.benchmark leaderboard --metric mAP50
    python -m evaluation.benchmark all --model models/yolov8n.pt --dataset data/val
"""

import argparse
import logging
import sys
from pathlib import Path

from .config import EvaluationConfig, YOLOConfig
from .harness import EvaluationHarness
from .regression import RegressionTracker
from .registry import ExperimentRegistry, ModelLeaderboard
from .visualization import plot_confusion_matrix, plot_pr_curves, FailureCaseVisualizer
from .reports import HTMLReportGenerator, CSVReportGenerator, JSONReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("benchmark")


def cmd_evaluate(args):
    """Run full evaluation on a single model."""
    eval_config = EvaluationConfig.from_env()
    yolo_config = YOLOConfig(
        conf_threshold=args.confidence,
        iou_threshold=args.iou,
        device=args.device,
        batch_size=args.batch_size,
    )
    harness = EvaluationHarness(eval_config, yolo_config)

    logger.info(f"Evaluating model: {args.model}")
    logger.info(f"Dataset: {args.dataset}")

    result = harness.evaluate(
        model_path=args.model,
        dataset_path=args.dataset,
        model_name=args.name,
        model_version=args.version,
    )

    # Generate visualizations
    vis_dir = eval_config.visualizations_dir
    if result.confusion_matrix is not None:
        cm_path = vis_dir / "confusion_matrix.png"
        plot_confusion_matrix(result.confusion_matrix, result.class_names, cm_path)
        logger.info(f"Confusion matrix saved to {cm_path}")

    if result.pr_curve_data:
        pr_path = vis_dir / "pr_curves.png"
        plot_pr_curves(result.pr_curve_data, pr_path)
        logger.info(f"PR curves saved to {pr_path}")

    # Generate reports
    report_dir = eval_config.reports_dir
    html_gen = HTMLReportGenerator()
    html_path = report_dir / f"eval_{result.model_name}_v{result.model_version}.html"
    html_gen.generate(result, html_path, visualizations={
        "pr_curve": str(vis_dir / "pr_curves.png") if result.pr_curve_data else None,
        "confusion_matrix": str(vis_dir / "confusion_matrix.png") if result.confusion_matrix is not None else None,
    })
    logger.info(f"HTML report saved to {html_path}")

    csv_gen = CSVReportGenerator()
    csv_path = report_dir / f"eval_{result.model_name}_v{result.model_version}.csv"
    csv_gen.generate_detailed(result, csv_path)
    logger.info(f"CSV report saved to {csv_path}")

    json_gen = JSONReportGenerator()
    json_path = report_dir / f"eval_{result.model_name}_v{result.model_version}.json"
    json_gen.generate_result(result, json_path)
    logger.info(f"JSON report saved to {json_path}")

    # Register in experiment registry
    registry = ExperimentRegistry()
    registry.register_experiment(result)
    registry.close()

    # Register in regression tracker
    tracker = RegressionTracker(eval_config)
    tracker.register_result(result)

    # Print summary
    m = result.metrics
    logger.info("=" * 60)
    logger.info("EVALUATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Model:         {result.model_name} v{result.model_version}")
    logger.info(f"  Dataset:       {result.dataset}")
    logger.info(f"  mAP50:         {m.mAP50:.4f}")
    logger.info(f"  mAP50-95:      {m.mAP50_95:.4f}")
    logger.info(f"  Precision:     {m.precision:.4f}")
    logger.info(f"  Recall:        {m.recall:.4f}")
    logger.info(f"  F1:            {m.f1_score:.4f}")
    logger.info(f"  FPS:           {m.fps:.1f}")
    logger.info(f"  Latency (ms):  {m.latency_ms:.2f}")
    logger.info(f"  GPU Mem (MB):  {m.gpu_memory_mb:.1f}")
    logger.info(f"  Model Size:    {m.model_size_mb:.1f} MB")
    logger.info("=" * 60)


def cmd_benchmark(args):
    """Run lightweight speed benchmark only."""
    eval_config = EvaluationConfig.from_env()
    yolo_config = YOLOConfig(device=args.device)
    harness = EvaluationHarness(eval_config, yolo_config)

    logger.info(f"Benchmarking: {args.model}")
    results = harness.benchmark(args.model, args.dataset, args.name)

    logger.info("=" * 60)
    logger.info("BENCHMARK RESULTS")
    logger.info("=" * 60)
    for k, v in results.items():
        logger.info(f"  {k}: {v}")
    logger.info("=" * 60)


def cmd_compare(args):
    """Compare two model versions."""
    eval_config = EvaluationConfig.from_env()
    tracker = RegressionTracker(eval_config)

    comparison = tracker.compare(args.baseline, args.candidate, args.model_name)
    report = tracker.generate_comparison_report(
        [comparison],
        output_path=eval_config.reports_dir / f"comparison_{args.baseline}_vs_{args.candidate}.txt",
    )

    print(report)


def cmd_leaderboard(args):
    """Generate model leaderboard."""
    registry = ExperimentRegistry()
    leaderboard = ModelLeaderboard(registry)

    if args.composite:
        lb = leaderboard.generate_multi_metric(top_k=args.top_k)
    else:
        lb = leaderboard.generate(metric=args.metric, top_k=args.top_k)

    print(leaderboard.format_markdown(lb))


def cmd_all(args):
    """Run full pipeline: evaluate, visualize, report, register."""
    cmd_evaluate(args)
    cmd_compare(args) if hasattr(args, 'baseline') else None
    cmd_leaderboard(args)


def main():
    parser = argparse.ArgumentParser(
        description="YOLOv8 Retail Intelligence Benchmark Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m evaluation.benchmark evaluate --model yolov8n.pt --dataset data/val
  python -m evaluation.benchmark benchmark --model yolov8n.pt --dataset data/val --device cuda:0
  python -m evaluation.benchmark compare --baseline v1 --candidate v2 --model-name retail_model
  python -m evaluation.benchmark leaderboard --metric mAP50 --top-k 10
  python -m evaluation.benchmark all --model yolov8n.pt --dataset data/val
        """,
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Full model evaluation")
    eval_parser.add_argument("--model", required=True, help="Path to YOLO model (.pt)")
    eval_parser.add_argument("--dataset", required=True, help="Path to validation dataset")
    eval_parser.add_argument("--name", help="Model name (default: filename)")
    eval_parser.add_argument("--version", help="Model version (default: auto)")
    eval_parser.add_argument("--confidence", type=float, default=0.25, help="Confidence threshold")
    eval_parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold")
    eval_parser.add_argument("--device", default="cpu", help="Device (cpu, cuda:0, etc.)")
    eval_parser.add_argument("--batch-size", type=int, default=16, help="Batch size")

    # benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Speed benchmark only")
    bench_parser.add_argument("--model", required=True, help="Path to YOLO model (.pt)")
    bench_parser.add_argument("--dataset", required=True, help="Path to validation images")
    bench_parser.add_argument("--name", help="Model name")
    bench_parser.add_argument("--device", default="cpu", help="Device")

    # compare
    comp_parser = subparsers.add_parser("compare", help="Compare model versions")
    comp_parser.add_argument("--baseline", required=True, help="Baseline version tag")
    comp_parser.add_argument("--candidate", required=True, help="Candidate version tag")
    comp_parser.add_argument("--model-name", required=True, help="Model name")

    # leaderboard
    lb_parser = subparsers.add_parser("leaderboard", help="Generate leaderboard")
    lb_parser.add_argument("--metric", default="mAP50", help="Sort metric")
    lb_parser.add_argument("--top-k", type=int, default=20, help="Number of entries")
    lb_parser.add_argument("--composite", action="store_true", help="Use composite scoring")

    # all
    all_parser = subparsers.add_parser("all", help="Run full evaluation pipeline")
    all_parser.add_argument("--model", required=True, help="Path to YOLO model (.pt)")
    all_parser.add_argument("--dataset", required=True, help="Path to validation dataset")
    all_parser.add_argument("--name", help="Model name")
    all_parser.add_argument("--version", help="Model version")
    all_parser.add_argument("--confidence", type=float, default=0.25)
    all_parser.add_argument("--iou", type=float, default=0.45)
    all_parser.add_argument("--device", default="cpu")
    all_parser.add_argument("--batch-size", type=int, default=16)

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "evaluate": cmd_evaluate,
        "benchmark": cmd_benchmark,
        "compare": cmd_compare,
        "leaderboard": cmd_leaderboard,
        "all": cmd_all,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
