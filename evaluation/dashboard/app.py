"""
Streamlit Dashboard for YOLOv8 Retail Intelligence Evaluation Platform.

Usage:
    streamlit run evaluation/dashboard/app.py
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from ..registry import ExperimentRegistry, ModelLeaderboard
from ..config import EvaluationConfig

st.set_page_config(
    page_title="YOLOv8 Evaluation Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_default_config():
    return EvaluationConfig.from_env()


def load_registry():
    return ExperimentRegistry()


def main():
    st.sidebar.title("🎯 YOLOv8 Evaluation")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "Model Leaderboard",
            "Model Comparison",
            "Per-Class Analysis",
            "History & Trends",
            "Benchmark Runs",
            "Experiment Registry",
        ],
    )

    registry = load_registry()
    config = load_default_config()

    if page == "Overview":
        show_overview(registry, config)
    elif page == "Model Leaderboard":
        show_leaderboard(registry)
    elif page == "Model Comparison":
        show_comparison(registry)
    elif page == "Per-Class Analysis":
        show_per_class(registry)
    elif page == "History & Trends":
        show_trends(registry)
    elif page == "Benchmark Runs":
        show_benchmark_runs(registry)
    elif page == "Experiment Registry":
        show_registry(registry, config)


def show_overview(registry: ExperimentRegistry, config: EvaluationConfig):
    st.title("🎯 YOLOv8 Evaluation Dashboard")
    st.markdown("Enterprise-grade evaluation platform for retail object detection models.")

    experiments = registry.query_experiments(limit=200)
    if not experiments:
        st.info("No evaluation results found. Run `python -m evaluation.benchmark evaluate` to get started.")
        return

    df = pd.DataFrame(experiments)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Experiments", len(df))
    with col2:
        st.metric("Unique Models", df["model_name"].nunique() if "model_name" in df else 0)
    with col3:
        best_mAP = df["mAP50"].max() if "mAP50" in df else 0
        st.metric("Best mAP50", f"{best_mAP:.4f}")
    with col4:
        best_fps = df["fps"].max() if "fps" in df else 0
        st.metric("Best FPS", f"{best_fps:.1f}")
    with col5:
        avg_latency = df["latency_ms"].mean() if "latency_ms" in df else 0
        st.metric("Avg Latency", f"{avg_latency:.2f}ms")

    st.subheader("Model Performance Overview")
    if "model_name" in df and "mAP50" in df:
        fig = px.scatter(
            df,
            x="fps",
            y="mAP50",
            size="model_size_mb",
            color="model_name",
            hover_data=["model_version", "precision", "recall"],
            labels={"fps": "FPS (↑)", "mAP50": "mAP50 (↑)", "model_size_mb": "Size (MB)"},
            title="mAP50 vs FPS (bubble = model size)",
        )
        fig.update_traces(marker=dict(line=dict(width=1, color="DarkSlateGrey")))
        st.plotly_chart(fig, use_container_width=True)


def show_leaderboard(registry: ExperimentRegistry):
    st.title("🏆 Model Leaderboard")
    st.markdown("Ranked by composite performance score.")

    metric = st.selectbox(
        "Sort Metric",
        ["composite", "mAP50", "mAP50_95", "precision", "recall", "f1_score", "fps"],
        index=0,
    )
    top_k = st.slider("Top K", 5, 50, 20)

    leaderboard = ModelLeaderboard(registry)

    if metric == "composite":
        lb = leaderboard.generate_multi_metric(top_k=top_k)
    else:
        lb = leaderboard.generate(metric=metric, top_k=top_k)

    entries = lb.get("entries", [])
    if not entries:
        st.warning("No results available.")
        return

    df = pd.DataFrame(entries)
    st.dataframe(
        df.style.highlight_max(
            subset=["mAP50", "mAP50_95", "precision", "recall", "f1_score", "fps"],
            color="#90EE90",
        ),
        use_container_width=True,
        hide_index=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            df.head(10),
            x="model_name",
            y="mAP50",
            color="model_version",
            title="Top 10 Models by mAP50",
            labels={"mAP50": "mAP50", "model_name": "Model"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df.head(10),
            x="model_name",
            y="fps",
            color="model_version",
            title="Top 10 Models by FPS",
            labels={"fps": "FPS", "model_name": "Model"},
        )
        st.plotly_chart(fig, use_container_width=True)


def show_comparison(registry: ExperimentRegistry):
    st.title("🔬 Model Comparison")
    st.markdown("Compare evaluation results across model versions.")

    models = set()
    for r in registry.query_experiments(limit=500):
        models.add(r.get("model_name", ""))

    if not models:
        st.info("No models registered yet.")
        return

    model_name = st.selectbox("Select Model", sorted(models))

    experiments = registry.query_experiments(model_name=model_name, limit=50)
    if len(experiments) < 2:
        st.warning(f"Need at least 2 versions for comparison.")
        return

    versions = [e["model_version"] for e in experiments]
    col1, col2 = st.columns(2)
    with col1:
        v1 = st.selectbox("Baseline", versions, index=0)
    with col2:
        v2 = st.selectbox("Candidate", versions, index=min(1, len(versions) - 1))

    e1 = next(e for e in experiments if e["model_version"] == v1)
    e2 = next(e for e in experiments if e["model_version"] == v2)

    metrics_compare = [
        "mAP50", "mAP50_95", "precision", "recall", "f1_score",
        "fps", "latency_ms", "model_size_mb",
    ]
    compare_data = []
    for m in metrics_compare:
        val1 = e1.get(m, 0)
        val2 = e2.get(m, 0)
        delta = val2 - val1
        direction = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        compare_data.append({
            "Metric": m,
            v1: f"{val1:.4f}",
            v2: f"{val2:.4f}",
            "Delta": f"{direction} {abs(delta):.4f}",
        })

    df = pd.DataFrame(compare_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    radar_categories = ["mAP50", "precision", "recall", "f1_score", "fps"]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[e1.get(m, 0) for m in radar_categories],
        theta=radar_categories,
        fill="toself",
        name=f"{v1}",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[e2.get(m, 0) for m in radar_categories],
        theta=radar_categories,
        fill="toself",
        name=f"{v2}",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Radar Comparison",
    )
    st.plotly_chart(fig, use_container_width=True)


def show_per_class(registry: ExperimentRegistry):
    st.title("📊 Per-Class Metrics")
    st.markdown("Detailed per-class performance breakdown.")

    experiments = registry.query_experiments(limit=100)
    models = set(e["model_name"] for e in experiments)

    if not models:
        st.info("No data available.")
        return

    model_name = st.selectbox("Select Model", sorted(models))
    model_exps = registry.query_experiments(model_name=model_name, limit=20)

    if not model_exps:
        return

    versions = [e["model_version"] for e in model_exps]
    selected_version = st.selectbox("Select Version", versions)

    exp_id = None
    for e in model_exps:
        if e["model_version"] == selected_version:
            exp_id = e["id"]
            break

    if not exp_id:
        return

    import sqlite3
    conn = sqlite3.connect(str(Path("evaluation_output/registry.db")))
    df = pd.read_sql_query(
        "SELECT * FROM class_metrics WHERE experiment_id = ? ORDER BY class_name",
        conn,
        params=(exp_id,),
    )
    conn.close()

    if df.empty:
        st.info("No per-class metrics available.")
        return

    metric = st.selectbox("Metric", ["ap50", "precision", "recall", "f1_score"])
    df_sorted = df.sort_values(metric, ascending=True)

    fig = px.bar(
        df_sorted,
        x=metric,
        y="class_name",
        orientation="h",
        color=metric,
        color_continuous_scale="Viridis",
        title=f"{metric.upper()} by Class",
        labels={metric: metric.upper(), "class_name": "Class"},
    )
    fig.update_layout(height=max(400, len(df) * 20))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        df[["class_name", "precision", "recall", "f1_score", "ap50", "support", "tp", "fp", "fn"]],
        use_container_width=True,
        hide_index=True,
    )


def show_trends(registry: ExperimentRegistry):
    st.title("📈 Performance Trends")
    st.markdown("Track metric evolution across model versions.")

    experiments = registry.query_experiments(limit=500)
    models = set(e["model_name"] for e in experiments)

    if not models:
        st.info("No data available.")
        return

    model_name = st.selectbox("Select Model", sorted(models))
    model_exps = registry.query_experiments(model_name=model_name, limit=100)
    model_exps.sort(key=lambda x: x.get("timestamp", ""))

    if len(model_exps) < 2:
        st.warning("Need at least 2 data points for trend analysis.")
        return

    df = pd.DataFrame(model_exps)

    metrics_to_plot = st.multiselect(
        "Metrics",
        ["mAP50", "mAP50_95", "precision", "recall", "f1_score", "fps", "latency_ms"],
        default=["mAP50", "mAP50_95", "precision", "recall"],
    )

    if metrics_to_plot:
        fig = go.Figure()
        for m in metrics_to_plot:
            if m in df.columns:
                fig.add_trace(go.Scatter(
                    x=list(range(len(df))),
                    y=df[m],
                    mode="lines+markers",
                    name=m,
                    text=df["model_version"],
                    hovertemplate="%{text}<br>%{y:.4f}<extra></extra>",
                ))
        fig.update_layout(
            title=f"Metric Trends for {model_name}",
            xaxis_title="Version (chronological)",
            yaxis_title="Value",
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    corr = df[["mAP50", "mAP50_95", "precision", "recall", "f1_score", "fps", "latency_ms"]].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", title="Metric Correlations")
    st.plotly_chart(fig, use_container_width=True)


def show_benchmark_runs(registry: ExperimentRegistry):
    st.title("⚡ Benchmark Runs")
    st.markdown("Speed and efficiency benchmarks.")

    experiments = registry.query_experiments(limit=200)
    if not experiments:
        st.info("No benchmark data available.")
        return

    df = pd.DataFrame(experiments)

    selected = st.multiselect(
        "Columns",
        ["model_name", "model_version", "mAP50", "fps", "latency_ms",
         "latency_p99_ms", "model_size_mb", "gpu_memory_mb"],
        default=["model_name", "model_version", "mAP50", "fps", "latency_ms", "model_size_mb"],
    )
    if selected:
        st.dataframe(df[selected], use_container_width=True, hide_index=True)


def show_registry(registry: ExperimentRegistry, config: EvaluationConfig):
    st.title("📋 Experiment Registry")
    st.markdown("All registered experiments and evaluation runs.")

    experiments = registry.query_experiments(limit=100)

    if not experiments:
        st.info("Registry is empty.")
        return

    df = pd.DataFrame(experiments)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("Export Registry as JSON"):
        export_path = config.output_path / "registry_export.json"
        df.to_json(export_path, orient="records", indent=2)
        st.success(f"Exported to {export_path}")

    st.subheader("Database Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Runs", len(df))
    with col2:
        st.metric("Unique Models", df["model_name"].nunique())
    with col3:
        st.metric("Avg mAP50", f"{df['mAP50'].mean():.4f}")


if __name__ == "__main__":
    main()
