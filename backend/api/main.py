"""FastAPI Backend - Enterprise Customer Intelligence API"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import joblib
import os
import random
import math

app = FastAPI(
    title="Enterprise Customer Intelligence API",
    description="API for churn prediction, CLV forecasting, segmentation, and causal inference",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Data Models ─────────────────────────────────────────────────────────────

class CustomerFeatures(BaseModel):
    customer_id: str
    features: dict


class PredictionRequest(BaseModel):
    customer_ids: List[str]
    model_type: str = "churn"


class CustomerResponse(BaseModel):
    customer_id: str
    churn_probability: Optional[float] = None
    clv_prediction: Optional[float] = None
    segment: Optional[str] = None
    recommendation: Optional[str] = None


# ─── Global Models ───────────────────────────────────────────────────────────

churn_model = None
clv_model = None


def load_models():
    global churn_model, clv_model
    models_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
    if os.path.exists(f"{models_dir}/churn_model.pkl"):
        churn_model = joblib.load(f"{models_dir}/churn_model.pkl")
    if os.path.exists(f"{models_dir}/clv_model.pkl"):
        clv_model = joblib.load(f"{models_dir}/clv_model.pkl")


@app.on_event("startup")
async def startup_event():
    load_models()


# ─── Core Endpoints ─────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Enterprise Customer Intelligence API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": {"churn": churn_model is not None, "clv": clv_model is not None}}


@app.post("/predict/churn", response_model=List[CustomerResponse])
async def predict_churn(customers: List[CustomerFeatures]):
    if churn_model is None:
        raise HTTPException(status_code=503, detail="Churn model not loaded")
    results = []
    for c in customers:
        fv = [c.features.get(f, 0) for f in churn_model.feature_names_]
        prob = churn_model.predict_proba([fv])[0][1]
        results.append(CustomerResponse(customer_id=c.customer_id, churn_probability=prob))
    return results


@app.post("/predict/clv", response_model=List[CustomerResponse])
async def predict_clv(customers: List[CustomerFeatures]):
    if clv_model is None:
        raise HTTPException(status_code=503, detail="CLV model not loaded")
    results = []
    for c in customers:
        fv = [c.features.get(f, 0) for f in clv_model.feature_names_]
        clv = clv_model.predict([fv])[0]
        results.append(CustomerResponse(customer_id=c.customer_id, clv_prediction=clv))
    return results


# ─── Dashboard Data Endpoints ───────────────────────────────────────────────

@app.get("/api/dashboard")
async def get_dashboard():
    """Executive dashboard data."""
    return {
        "kpis": {
            "total_customers": {"value": 125842, "change": 8.2, "trend": "up"},
            "avg_clv": {"value": 842, "change": 12.0, "trend": "up"},
            "churn_rate": {"value": 7.4, "change": -3.1, "trend": "down"},
            "campaign_roi": {"value": 4.2, "change": 1.8, "trend": "up"},
        },
        "revenue_trend": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "data": [2100000, 2250000, 2180000, 2420000, 2560000, 2480000, 2680000, 2750000, 2620000, 2840000, 2950000, 3100000],
        },
        "retention_trend": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "data": [91.2, 91.5, 91.8, 92.0, 92.1, 92.4, 92.6, 92.5, 92.8, 93.0, 93.1, 93.4],
        },
        "risk_distribution": {
            "labels": ["Healthy", "At-Risk", "Critical"],
            "data": [78450, 35200, 12192],
            "colors": ["#10B981", "#F59E0B", "#EF4444"],
        },
        "top_segments": [
            {"name": "VIP", "count": 8400, "revenue": 4200000, "churn_risk": 2.1},
            {"name": "Loyal", "count": 42500, "revenue": 12800000, "churn_risk": 4.8},
            {"name": "Growth", "count": 38200, "revenue": 8900000, "churn_risk": 6.2},
            {"name": "At-Risk", "count": 24500, "revenue": 4100000, "churn_risk": 18.5},
            {"name": "Dormant", "count": 12242, "revenue": 980000, "churn_risk": 34.2},
        ],
    }


@app.get("/api/churn")
async def get_churn_analytics():
    """Churn analytics data."""
    return {
        "hero": {
            "current_churn_rate": 7.4,
            "predicted_monthly_loss": 42000,
            "at_risk_customers": 12192,
            "avg_days_to_churn": 45,
        },
        "monthly_trend": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "churn_rate": [9.8, 9.5, 9.2, 8.8, 8.5, 8.2, 7.9, 7.8, 7.6, 7.5, 7.4, 7.4],
            "customers_lost": [420, 390, 380, 360, 340, 320, 310, 305, 298, 290, 285, 280],
        },
        "heatmap": {
            "segments": ["VIP", "Loyal", "Growth", "At-Risk", "Dormant"],
            "risk_buckets": ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"],
            "data": [
                [92, 5, 2, 1, 0],
                [78, 14, 5, 2, 1],
                [60, 22, 10, 5, 3],
                [15, 20, 25, 25, 15],
                [5, 10, 20, 30, 35],
            ],
        },
        "shap_features": [
            {"feature": "Support Tickets", "impact": 0.34, "direction": "churn"},
            {"feature": "Days Since Last Login", "impact": 0.28, "direction": "churn"},
            {"feature": "Monthly Spend Decline", "impact": 0.22, "direction": "churn"},
            {"feature": "Low Engagement Score", "impact": 0.18, "direction": "churn"},
            {"feature": "Contract Type (Monthly)", "impact": 0.15, "direction": "churn"},
            {"feature": "Payment Failures", "impact": 0.12, "direction": "churn"},
            {"feature": "Loyalty Points Balance", "impact": -0.08, "direction": "retain"},
            {"feature": "Feature Adoption Rate", "impact": -0.12, "direction": "retain"},
            {"feature": "NPS Score", "impact": -0.15, "direction": "retain"},
            {"feature": "Account Tenure (Years)", "impact": -0.22, "direction": "retain"},
        ],
        "segment_churn": {
            "labels": ["VIP", "Loyal", "Growth", "At-Risk", "Dormant"],
            "rates": [2.1, 4.8, 6.2, 18.5, 34.2],
        },
    }


@app.get("/api/segmentation")
async def get_segmentation():
    """Customer segmentation data."""
    random.seed(42)
    clusters = {}
    configs = [
        ("VIP", 40, 8.0, 1.0, 8.5, 0.8),
        ("Loyal", 60, 6.0, 1.5, 7.0, 1.0),
        ("Growth", 55, 5.0, 1.5, 5.0, 1.5),
        ("At-Risk", 45, 2.5, 1.5, 3.0, 1.5),
        ("Dormant", 30, 1.5, 1.0, 1.5, 1.0),
    ]
    for name, n, cx, sx, cy, sy in configs:
        clusters[name] = {
            "x": [round(random.gauss(cx, sx), 2) for _ in range(n)],
            "y": [round(random.gauss(cy, sy), 2) for _ in range(n)],
        }
    return {
        "segments": [
            {"name": "VIP", "count": 8400, "revenue": 4200000, "avg_clv": 2850, "churn_pct": 2.1, "color": "#10B981"},
            {"name": "Loyal", "count": 42500, "revenue": 12800000, "avg_clv": 1420, "churn_pct": 4.8, "color": "#4F46E5"},
            {"name": "Growth", "count": 38200, "revenue": 8900000, "avg_clv": 680, "churn_pct": 6.2, "color": "#6366F1"},
            {"name": "At-Risk", "count": 24500, "revenue": 4100000, "avg_clv": 320, "churn_pct": 18.5, "color": "#F59E0B"},
            {"name": "Dormant", "count": 12242, "revenue": 980000, "avg_clv": 85, "churn_pct": 34.2, "color": "#EF4444"},
        ],
        "clusters": clusters,
    }


@app.get("/api/clv")
async def get_clv_analytics():
    """CLV forecasting data."""
    return {
        "kpis": {
            "avg_clv": {"value": 842, "change": 12.0},
            "total_ltv": {"value": 106000000, "change": 15.4},
            "high_value_pct": {"value": 6.7, "change": 1.2},
            "payback_months": {"value": 4.8, "change": -0.6},
        },
        "projection": {
            "labels": ["Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25", "Q2'25", "Q3'25", "Q4'25"],
            "actual": [24500000, 26200000, 27800000, 29500000, 31000000, None, None, None],
            "forecast": [None, None, None, None, 31000000, 33200000, 35100000, 37400000],
            "upper": [None, None, None, None, 31000000, 34800000, 37500000, 40200000],
            "lower": [None, None, None, None, 31000000, 31600000, 32700000, 34600000],
        },
        "distribution": {
            "labels": ["$0-100", "$100-300", "$300-500", "$500-800", "$800-1200", "$1200-2000", "$2000-3000", "$3000+"],
            "counts": [12200, 28500, 32100, 24800, 15400, 8200, 3400, 1242],
        },
        "cohort_retention": {
            "cohorts": ["Jan'24", "Feb'24", "Mar'24", "Apr'24", "May'24", "Jun'24"],
            "months": ["M1", "M2", "M3", "M4", "M5", "M6"],
            "data": [
                [100, 82, 74, 68, 64, 61],
                [100, 84, 76, 70, 66, None],
                [100, 85, 78, 72, None, None],
                [100, 83, 75, None, None, None],
                [100, 86, None, None, None, None],
                [100, None, None, None, None, None],
            ],
        },
    }


@app.get("/api/causal")
async def get_causal_analysis():
    """Causal inference data."""
    return {
        "treatment_control": {
            "treatment": {"label": "Treatment Group", "size": 4500, "churn_rate": 12.0, "avg_clv": 920, "retention": 88.0},
            "control": {"label": "Control Group", "size": 5450, "churn_rate": 18.0, "avg_clv": 780, "retention": 82.0},
        },
        "effects": {
            "ate": {"value": -6.0, "ci_lower": -8.2, "ci_upper": -3.8, "p_value": 0.001},
            "att": {"value": -7.2, "ci_lower": -9.5, "ci_upper": -4.9, "p_value": 0.0005},
            "uplift": {"value": 5.8, "ci_lower": 3.5, "ci_upper": 8.1, "p_value": 0.002},
        },
        "did_plot": {
            "labels": ["6 Mo Before", "3 Mo Before", "Campaign", "3 Mo After", "6 Mo After"],
            "treatment": [18.5, 18.2, 17.0, 13.5, 12.0],
            "control": [18.0, 17.8, 17.5, 17.2, 18.0],
            "treatment_ci": [1.2, 1.1, 1.0, 0.9, 0.8],
            "control_ci": [1.1, 1.0, 0.9, 0.8, 0.9],
        },
        "uplift_segments": {
            "labels": ["Persuadable", "Sure Thing", "Do Not Disturb", "Lost Cause"],
            "counts": [18500, 42200, 38900, 26242],
            "colors": ["#10B981", "#4F46E5", "#F59E0B", "#EF4444"],
        },
    }


@app.get("/api/recommendations")
async def get_recommendations():
    """AI-powered recommendations."""
    return {
        "cards": [
            {
                "segment": "High-Value At-Risk",
                "customer_count": 842,
                "predicted_churn": 91,
                "recommendation": "Offer Premium Retention Package",
                "expected_lift": 18,
                "priority": "critical",
                "estimated_revenue_saved": 2400000,
            },
            {
                "segment": "Growth Segment",
                "customer_count": 2150,
                "predicted_churn": 34,
                "recommendation": "Personalized Upsell Campaign",
                "expected_lift": 12,
                "priority": "high",
                "estimated_revenue_saved": 1800000,
            },
            {
                "segment": "Loyal Declining",
                "customer_count": 1680,
                "predicted_churn": 22,
                "recommendation": "Loyalty Reward Acceleration",
                "expected_lift": 8,
                "priority": "medium",
                "estimated_revenue_saved": 950000,
            },
            {
                "segment": "New Customers",
                "customer_count": 3200,
                "predicted_churn": 15,
                "recommendation": "Enhanced Onboarding Sequence",
                "expected_lift": 6,
                "priority": "medium",
                "estimated_revenue_saved": 680000,
            },
            {
                "segment": "Dormant Reactivation",
                "customer_count": 4500,
                "predicted_churn": 62,
                "recommendation": "Win-Back Email + Discount",
                "expected_lift": 4,
                "priority": "low",
                "estimated_revenue_saved": 420000,
            },
        ],
        "priority_matrix": {
            "quadrants": [
                {"label": "Protect", "description": "High CLV + High Risk", "count": 842, "color": "#EF4444"},
                {"label": "Nurture", "description": "High CLV + Low Risk", "count": 7558, "color": "#10B981"},
                {"label": "Monitor", "description": "Low CLV + High Risk", "count": 11350, "color": "#F59E0B"},
                {"label": "Maintain", "description": "Low CLV + Low Risk", "count": 106092, "color": "#4F46E5"},
            ],
        },
        "summary": "AI analysis identifies $6.25M in recoverable revenue across 12,372 at-risk customers. Top priority: 842 high-value customers showing critical churn signals. Recommended total investment: $340K for projected 4.2x ROI.",
    }


# ─── Serve Frontend ─────────────────────────────────────────────────────────

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/dashboard")
    async def serve_dashboard():
        return FileResponse(os.path.join(frontend_dir, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
