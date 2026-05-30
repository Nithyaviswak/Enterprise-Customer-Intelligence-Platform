"""Retention Recommendation Engine - Phase 9"""

import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generate retention intervention recommendations."""

    def __init__(self):
        self.rules = []
        self.recommendations = []

    def add_rule(
        self,
        name: str,
        condition: Dict,
        action: str,
        priority: int = 1,
    ):
        """Add a business rule for recommendations."""
        rule = {
            "name": name,
            "condition": condition,
            "action": action,
            "priority": priority,
        }
        self.rules.append(rule)
        logger.info(f"Added rule: {name}")

    def _evaluate_condition(self, customer: Dict, condition: Dict) -> bool:
        """Evaluate if a condition is met."""
        for key, op_value in condition.items():
            if isinstance(op_value, dict):
                operator = op_value.get("op")
                value = op_value.get("value")

                if key not in customer:
                    return False

                customer_value = customer[key]

                if operator == "gt" and not (customer_value > value):
                    return False
                elif operator == "gte" and not (customer_value >= value):
                    return False
                elif operator == "lt" and not (customer_value < value):
                    return False
                elif operator == "lte" and not (customer_value <= value):
                    return False
                elif operator == "eq" and not (customer_value == value):
                    return False
                elif operator == "in" and not (customer_value in value):
                    return False

        return True

    def generate_recommendations(
        self,
        customers: pd.DataFrame,
        churn_risk_col: str = "churn_risk",
        clv_col: str = "clv",
        segment_col: str = "segment",
    ) -> pd.DataFrame:
        """Generate recommendations for all customers."""
        recommendations = []

        for _, customer in customers.iterrows():
            customer_dict = customer.to_dict()
            customer_recs = []

            # Evaluate each rule
            for rule in self.rules:
                if self._evaluate_condition(customer_dict, rule["condition"]):
                    customer_recs.append({
                        "action": rule["action"],
                        "priority": rule["priority"],
                        "rule": rule["name"],
                    })

            if customer_recs:
                # Sort by priority (higher first)
                customer_recs.sort(key=lambda x: x["priority"], reverse=True)
                best_rec = customer_recs[0]

                recommendations.append({
                    "customer_id": customer.get("customer_id", "unknown"),
                    "churn_risk": customer.get(churn_risk_col, 0),
                    "clv": customer.get(clv_col, 0),
                    "segment": customer.get(segment_col, "unknown"),
                    "recommended_action": best_rec["action"],
                    "priority": best_rec["priority"],
                    "all_actions": [r["action"] for r in customer_recs],
                })

        return pd.DataFrame(recommendations)

    def set_default_rules(self):
        """Set default retention rules."""
        # High risk + high CLV = premium retention offer
        self.add_rule(
            name="premium_retention",
            condition={
                "churn_risk": {"op": "gte", "value": 0.8},
                "clv": {"op": "gte", "value": 1000},
            },
            action="premium_retention_offer",
            priority=10,
        )

        # High risk + low CLV = low-cost intervention
        self.add_rule(
            name="low_cost_intervention",
            condition={
                "churn_risk": {"op": "gte", "value": 0.8},
                "clv": {"op": "lt", "value": 200},
            },
            action="low_cost_email_campaign",
            priority=5,
        )

        # Medium risk + high value = personalized outreach
        self.add_rule(
            name="personalized_outreach",
            condition={
                "churn_risk": {"op": "gte", "value": 0.5},
                "churn_risk": {"op": "lt", "value": 0.8},
                "clv": {"op": "gte", "value": 500},
            },
            action="personalized_outreach",
            priority=7,
        )

        # At-risk segment = loyalty program
        self.add_rule(
            name="loyalty_program",
            condition={
                "segment": {"op": "eq", "value": "at_risk"},
            },
            action="enroll_loyalty_program",
            priority=6,
        )

        # Dormant customers = win-back campaign
        self.add_rule(
            name="win_back",
            condition={
                "segment": {"op": "eq", "value": "dormant"},
            },
            action="win_back_campaign",
            priority=4,
        )

        # New customers = onboarding
        self.add_rule(
            name="onboarding",
            condition={
                "segment": {"op": "eq", "value": "new"},
            },
            action="enhanced_onboarding",
            priority=8,
        )

        logger.info("Default retention rules set")

    def rank_interventions(self, recommendations: pd.DataFrame) -> pd.DataFrame:
        """Rank interventions by expected ROI."""
        # Define action costs and expected impact
        action_impact = {
            "premium_retention_offer": {"cost": 100, "impact": 0.8},
            "low_cost_email_campaign": {"cost": 10, "impact": 0.3},
            "personalized_outreach": {"cost": 50, "impact": 0.5},
            "enroll_loyalty_program": {"cost": 30, "impact": 0.4},
            "win_back_campaign": {"cost": 20, "impact": 0.3},
            "enhanced_onboarding": {"cost": 40, "impact": 0.6},
        }

        recommendations = recommendations.copy()
        recommendations["expected_cost"] = recommendations["recommended_action"].map(
            lambda x: action_impact.get(x, {}).get("cost", 50)
        )
        recommendations["expected_impact"] = recommendations["recommended_action"].map(
            lambda x: action_impact.get(x, {}).get("impact", 0.5)
        )
        recommendations["roi_score"] = (
            recommendations["expected_impact"] * recommendations["clv"] /
            recommendations["expected_cost"]
        )

        return recommendations.sort_values("roi_score", ascending=False)
