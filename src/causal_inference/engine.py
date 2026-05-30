"""Causal Inference Module - Phase 8"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neighbors import NearestNeighbors
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CausalInferenceEngine:
    """Estimate causal effects of retention campaigns."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.treatment_effects = {}

    def propensity_score_matching(
        self,
        treatment_col: str,
        outcome_col: str,
        features: list,
        n_neighbors: int = 5,
    ) -> Dict:
        """Perform Propensity Score Matching."""
        df = self.df.copy()
        df = df.dropna(subset=features + [treatment_col, outcome_col])

        # Calculate propensity scores
        X = df[features]
        treatment = df[treatment_col]

        propensity_model = LogisticRegression(max_iter=1000)
        propensity_model.fit(X, treatment)
        propensity_scores = propensity_model.predict_proba(X)[:, 1]

        df["propensity_score"] = propensity_scores

        # Match treated and control groups
        treated = df[df[treatment_col] == 1].copy()
        control = df[df[treatment_col] == 0].copy()

        # Nearest neighbor matching
        nn = NearestNeighbors(n_neighbors=n_neighbors)
        nn.fit(control[["propensity_score"]])

        matched_indices = []
        for idx in treated.index:
            treated_score = treated.loc[idx, "propensity_score"]
            distances, indices = nn.kneighbors([[treated_score]])
            matched_idx = control.iloc[indices[0]].index[0]
            matched_indices.append((idx, matched_idx))

        # Calculate treatment effects
        treated_outcomes = [treated.loc[idx, outcome_col] for idx, _ in matched_indices]
        control_outcomes = [control.loc[idx, outcome_col] for _, idx in matched_indices]

        ate = np.mean(treated_outcomes) - np.mean(control_outcomes)

        self.treatment_effects["psm"] = {
            "ATE": ate,
            "treated_mean": np.mean(treated_outcomes),
            "control_mean": np.mean(control_outcomes),
            "n_treated": len(treated_outcomes),
            "n_matched": len(matched_indices),
        }

        logger.info(f"PSM: ATE = {ate:.4f}")
        return self.treatment_effects["psm"]

    def difference_in_differences(
        self,
        treatment_col: str,
        time_col: str,
        outcome_col: str,
        pre_period: Tuple,
        post_period: Tuple,
    ) -> Dict:
        """Perform Difference-in-Differences analysis."""
        df = self.df.copy()
        df[time_col] = pd.to_datetime(df[time_col])

        # Define periods
        df["period"] = "middle"
        df.loc[df[time_col].between(*pre_period), "period"] = "pre"
        df.loc[df[time_col].between(*post_period), "period"] = "post"

        treated = df[df[treatment_col] == 1]
        control = df[df[treatment_col] == 0]

        # Pre-treatment means
        treated_pre = treated[treated["period"] == "pre"][outcome_col].mean()
        treated_post = treated[treated["period"] == "post"][outcome_col].mean()
        control_pre = control[control["period"] == "pre"][outcome_col].mean()
        control_post = control[control["period"] == "post"][outcome_col].mean()

        # DID estimate
        did = (treated_post - treated_pre) - (control_post - control_pre)

        self.treatment_effects["did"] = {
            "ATE": did,
            "treated_pre": treated_pre,
            "treated_post": treated_post,
            "control_pre": control_pre,
            "control_post": control_post,
            "treated_diff": treated_post - treated_pre,
            "control_diff": control_post - control_pre,
        }

        logger.info(f"DiD: ATE = {did:.4f}")
        return self.treatment_effects["did"]

    def uplift_modeling(
        self,
        treatment_col: str,
        outcome_col: str,
        features: list,
    ) -> pd.DataFrame:
        """Perform uplift modeling for treatment effect prediction."""
        df = self.df.copy()
        df = df.dropna(subset=features + [treatment_col, outcome_col])

        X = df[features]
        treatment = df[treatment_col]
        outcome = df[outcome_col]

        # Simple uplift model: predict outcome for treated and control separately
        treated_idx = treatment == 1
        control_idx = treatment == 0

        # Train models
        model_treated = LinearRegression()
        model_control = LinearRegression()

        model_treated.fit(X[treated_idx], outcome[treated_idx])
        model_control.fit(X[control_idx], outcome[control_idx])

        # Predict uplift
        uplift_pred = model_treated.predict(X) - model_control.predict(X)

        df["uplift_score"] = uplift_pred

        # Segment customers
        df["uplift_segment"] = pd.cut(
            uplift_pred,
            bins=[-np.inf, -0.1, 0.1, np.inf],
            labels=["do_not_disturb", "persuadable", "sure_thing"],
        )

        self.treatment_effects["uplift"] = df[["uplift_score", "uplift_segment"]].to_dict()

        return df

    def calculate_ate_att(
        self, treatment_col: str, outcome_col: str
    ) -> Dict:
        """Calculate Average Treatment Effect and ATT."""
        df = self.df.copy()

        treated = df[df[treatment_col] == 1][outcome_col]
        control = df[df[treatment_col] == 0][outcome_col]

        ate = treated.mean() - control.mean()

        # For ATT, we need matched pairs - simplified version
        att = ate  # Using ATE as approximation

        return {
            "ATE": ate,
            "ATT": att,
            "treated_mean": treated.mean(),
            "control_mean": control.mean(),
            "treated_n": len(treated),
            "control_n": len(control),
        }

    def get_all_effects(self) -> Dict:
        """Get all calculated treatment effects."""
        return self.treatment_effects
