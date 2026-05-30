"""Data Engineering Module - Phase 1"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handles missing values, outliers, and data validation."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.validation_report = {}

    def handle_missing_values(
        self, strategy: str = "auto", columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Handle missing values using specified strategy."""
        df = self.df.copy()
        columns = columns or df.columns.tolist()

        for col in columns:
            if df[col].isnull().sum() == 0:
                continue

            missing_pct = df[col].isnull().sum() / len(df) * 100

            if strategy == "auto":
                if df[col].dtype in ["object", "category"]:
                    df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown", inplace=True)
                else:
                    df[col].fillna(df[col].median(), inplace=True)
            elif strategy == "drop":
                df.dropna(subset=[col], inplace=True)
            elif strategy == "mean" and df[col].dtype != "object":
                df[col].fillna(df[col].mean(), inplace=True)
            elif strategy == "median" and df[col].dtype != "object":
                df[col].fillna(df[col].median(), inplace=True)
            elif strategy == "mode":
                df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown", inplace=True)

            logger.info(f"Handled missing values in {col}: {missing_pct:.2f}% missing, strategy: {strategy}")

        return df

    def detect_outliers(
        self, columns: Optional[List[str]] = None, method: str = "iqr"
    ) -> Dict[str, pd.Series]:
        """Detect outliers using IQR or Z-score method."""
        df = self.df
        columns = columns or df.select_dtypes(include=[np.number]).columns.tolist()
        outliers = {}

        for col in columns:
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers[col] = (df[col] < lower_bound) | (df[col] > upper_bound)
            elif method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers[col] = z_scores > 3

        return outliers

    def validate_data(self) -> Dict:
        """Validate data quality and return report."""
        report = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "missing_values": self.df.isnull().sum().to_dict(),
            "duplicates": self.df.duplicated().sum(),
            "dtypes": self.df.dtypes.astype(str).to_dict(),
        }
        self.validation_report = report
        return report

    def remove_duplicates(self) -> pd.DataFrame:
        """Remove duplicate rows."""
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = initial_rows - len(self.df)
        logger.info(f"Removed {removed} duplicate rows")
        return self.df


def load_data(path: str, **kwargs) -> pd.DataFrame:
    """Load data from various file formats."""
    if path.endswith(".csv"):
        return pd.read_csv(path, **kwargs)
    elif path.endswith(".parquet"):
        return pd.read_parquet(path, **kwargs)
    elif path.endswith(".json"):
        return pd.read_json(path, **kwargs)
    else:
        raise ValueError(f"Unsupported file format: {path}")
