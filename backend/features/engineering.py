"""Feature Engineering Module - Phase 3"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Create advanced customer features."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.feature_names = []

    def create_behavior_features(
        self,
        customer_id_col: str,
        transaction_col: str,
        amount_col: str,
        date_col: str,
    ) -> pd.DataFrame:
        """Create behavior-based features."""
        df = self.df.copy()
        df[date_col] = pd.to_datetime(df[date_col])

        # Group by customer
        customer_data = df.groupby(customer_id_col).agg({
            transaction_col: "count",
            amount_col: ["mean", "sum", "std", "min", "max"],
            date_col: ["min", "max", "nunique"],
        })

        # Flatten column names
        customer_data.columns = [
            f"behave_{col[0]}_{col[1]}" for col in customer_data.columns
        ]
        customer_data = customer_data.reset_index()

        # Calculate additional features
        customer_data["behave_purchase_frequency"] = customer_data[f"behave_{transaction_col}_count"]
        customer_data["behave_avg_order_value"] = customer_data[f"behave_{amount_col}_mean"]
        customer_data["behave_total_revenue"] = customer_data[f"behave_{amount_col}_sum"]
        customer_data["behave_revenue_std"] = customer_data[f"behave_{amount_col}_std"]

        # Recency (days since last purchase)
        reference_date = df[date_col].max()
        customer_data["behave_recency"] = (
            reference_date - df.groupby(customer_id_col)[date_col].max()
        ).dt.days.values

        self.df = customer_data
        self.feature_names.extend([
            "behave_purchase_frequency", "behave_avg_order_value",
            "behave_total_revenue", "behave_revenue_std", "behave_recency"
        ])
        return self.df

    def create_temporal_features(
        self, date_col: str, customer_id_col: str
    ) -> pd.DataFrame:
        """Create temporal features."""
        df = self.df.copy()
        df[date_col] = pd.to_datetime(df[date_col])

        # Day of week, month, hour
        df[f"temporal_day_of_week"] = df[date_col].dt.dayofweek
        df[f"temporal_month"] = df[date_col].dt.month
        df[f"temporal_day_of_month"] = df[date_col].dt.day
        df[f"temporal_quarter"] = df[date_col].dt.quarter
        df[f"temporal_is_weekend"] = (df[date_col].dt.dayofweek >= 5).astype(int)

        # Days since first purchase
        first_purchase = df.groupby(customer_id_col)[date_col].min()
        df["temporal_days_since_first"] = (
            df[date_col] - df[customer_id_col].map(first_purchase)
        ).dt.days

        self.df = df
        self.feature_names.extend([
            "temporal_day_of_week", "temporal_month", "temporal_day_of_month",
            "temporal_quarter", "temporal_is_weekend", "temporal_days_since_first"
        ])
        return df

    def create_revenue_features(
        self, customer_id_col: str, amount_col: str, date_col: str
    ) -> pd.DataFrame:
        """Create revenue-related features."""
        df = self.df.copy()
        df[date_col] = pd.to_datetime(df[date_col])

        # Monthly revenue
        df["revenue_month"] = df[date_col].dt.to_period("M")
        monthly_revenue = df.groupby([customer_id_col, "revenue_month"])[amount_col].sum().reset_index()
        monthly_revenue_pivot = monthly_revenue.pivot(
            index=customer_id_col, columns="revenue_month", values=amount_col
        ).fillna(0)

        # Revenue growth rate
        monthly_revenue_pivot["revenue_growth_rate"] = monthly_revenue_pivot.pct_change(axis=1).mean(axis=1)

        # Average monthly revenue
        monthly_revenue_pivot["revenue_avg_monthly"] = monthly_revenue_pivot.mean(axis=1)

        # Merge back
        revenue_features = monthly_revenue_pivot[["revenue_growth_rate", "revenue_avg_monthly"]].reset_index()
        df = df.merge(revenue_features, on=customer_id_col, how="left")

        self.df = df
        self.feature_names.extend(["revenue_growth_rate", "revenue_avg_monthly"])
        return df

    def create_engagement_features(
        self,
        customer_id_col: str,
        login_col: Optional[str] = None,
        support_col: Optional[str] = None,
        email_col: Optional[str] = None,
    ) -> pd.DataFrame:
        """Create engagement features."""
        df = self.df.copy()

        if login_col and login_col in df.columns:
            df["engagement_login_count"] = df.groupby(customer_id_col)[login_col].transform("count")
            self.feature_names.append("engagement_login_count")

        if support_col and support_col in df.columns:
            df["engagement_support_tickets"] = df.groupby(customer_id_col)[support_col].transform("sum")
            self.feature_names.append("engagement_support_tickets")

        if email_col and email_col in df.columns:
            df["engagement_email_open_rate"] = df.groupby(customer_id_col)[email_col].transform("mean")
            self.feature_names.append("engagement_email_open_rate")

        self.df = df
        return df

    def get_feature_names(self) -> List[str]:
        """Get list of created feature names."""
        return self.feature_names
