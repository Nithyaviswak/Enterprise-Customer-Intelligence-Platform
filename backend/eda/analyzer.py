"""Exploratory Data Analysis Module - Phase 2"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EDAAnalyzer:
    """Perform exploratory data analysis on customer data."""

    def __init__(self, df: pd.DataFrame, target_col: str = "churn"):
        self.df = df
        self.target_col = target_col
        self.insights = {}

    def analyze_churn_distribution(self) -> Dict:
        """Analyze churn distribution."""
        if self.target_col not in self.df.columns:
            return {"error": f"Target column {self.target_col} not found"}

        churn_counts = self.df[self.target_col].value_counts()
        churn_rate = churn_counts.get(1, 0) / len(self.df) * 100 if 1 in churn_counts else 0

        return {
            "churn_counts": churn_counts.to_dict(),
            "churn_rate": churn_rate,
            "non_churn_rate": 100 - churn_rate,
        }

    def analyze_revenue_distribution(self, revenue_col: str = "revenue") -> Dict:
        """Analyze revenue distribution."""
        if revenue_col not in self.df.columns:
            return {"error": f"Revenue column {revenue_col} not found"}

        return {
            "mean": self.df[revenue_col].mean(),
            "median": self.df[revenue_col].median(),
            "std": self.df[revenue_col].std(),
            "min": self.df[revenue_col].min(),
            "max": self.df[revenue_col].max(),
            "q25": self.df[revenue_col].quantile(0.25),
            "q75": self.df[revenue_col].quantile(0.75),
        }

    def compute_correlation_matrix(
        self, columns: Optional[List[str]] = None, method: str = "pearson"
    ) -> pd.DataFrame:
        """Compute correlation matrix."""
        cols = columns or self.df.select_dtypes(include=[np.number]).columns
        return self.df[cols].corr(method=method)

    def rfm_analysis(
        self, customer_id_col: str, recency_col: str, frequency_col: str, monetary_col: str
    ) -> pd.DataFrame:
        """Perform RFM (Recency, Frequency, Monetary) analysis."""
        rfm_df = self.df.groupby(customer_id_col).agg({
            recency_col: "min",
            frequency_col: "sum",
            monetary_col: "sum",
        }).reset_index()

        rfm_df.columns = [customer_id_col, "recency", "frequency", "monetary"]

        # Create RFM scores
        rfm_df["R_score"] = pd.qcut(rfm_df["recency"], 5, labels=[5, 4, 3, 2, 1], duplicates="drop")
        rfm_df["F_score"] = pd.qcut(rfm_df["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        rfm_df["M_score"] = pd.qcut(rfm_df["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

        rfm_df["R_score"] = rfm_df["R_score"].astype(int)
        rfm_df["F_score"] = rfm_df["F_score"].astype(int)
        rfm_df["M_score"] = rfm_df["M_score"].astype(int)

        rfm_df["RFM_score"] = rfm_df["R_score"] + rfm_df["F_score"] + rfm_df["M_score"]

        return rfm_df

    def cohort_analysis(
        self, customer_id_col: str, date_col: str, metric_col: str = "customer_id"
    ) -> pd.DataFrame:
        """Perform cohort analysis."""
        df = self.df.copy()
        df["cohort_month"] = pd.to_datetime(df[date_col]).dt.to_period("M")

        cohort_data = df.groupby(customer_id_col)["cohort_month"].min().reset_index()
        cohort_data.columns = [customer_id_col, "cohort"]

        df = df.merge(cohort_data, on=customer_id_col)
        df["cohort_index"] = (df["cohort_month"] - df["cohort"]).apply(lambda x: x.n)

        cohort_summary = df.groupby(["cohort", "cohort_index"])[metric_col].nunique()
        cohort_table = cohort_summary.unstack(0)

        return cohort_table

    def generate_summary_report(self) -> Dict:
        """Generate comprehensive EDA summary report."""
        self.insights = {
            "churn_analysis": self.analyze_churn_distribution(),
            "revenue_analysis": self.analyze_revenue_distribution(),
            "data_shape": {"rows": len(self.df), "columns": len(self.df.columns)},
            "numeric_columns": self.df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": self.df.select_dtypes(include=["object", "category"]).columns.tolist(),
        }
        return self.insights
