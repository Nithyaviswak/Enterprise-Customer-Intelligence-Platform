"""FastAPI Backend - Enterprise Customer Intelligence API"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import joblib
import os

app = FastAPI(
    title="Enterprise Customer Intelligence API",
    description="API for churn prediction, CLV forecasting, segmentation, and causal inference",
    version="1.0.0",
)

# CORS middleware for frontend communication
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
    model_type: str = "churn"  # churn or clv


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
    """Load trained models from disk."""
    global churn_model, clv_model
    models_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
    if os.path.exists(f"{models_dir}/churn_model.pkl"):
        churn_model = joblib.load(f"{models_dir}/churn_model.pkl")
    if os.path.exists(f"{models_dir}/clv_model.pkl"):
        clv_model = joblib.load(f"{models_dir}/clv_model.pkl")


@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    load_models()


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Enterprise Customer Intelligence API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": {
            "churn": churn_model is not None,
            "clv": clv_model is not None,
        },
    }


@app.post("/predict/churn", response_model=List[CustomerResponse])
async def predict_churn(customers: List[CustomerFeatures]):
    """Predict churn probability for customers."""
    if churn_model is None:
        raise HTTPException(status_code=503, detail="Churn model not loaded")

    results = []
    for customer in customers:
        feature_vector = [customer.features.get(f, 0) for f in churn_model.feature_names_]
        prob = churn_model.predict_proba([feature_vector])[0][1]
        results.append(CustomerResponse(
            customer_id=customer.customer_id,
            churn_probability=prob,
        ))
    return results


@app.post("/predict/clv", response_model=List[CustomerResponse])
async def predict_clv(customers: List[CustomerFeatures]):
    """Predict CLV for customers."""
    if clv_model is None:
        raise HTTPException(status_code=503, detail="CLV model not loaded")

    results = []
    for customer in customers:
        feature_vector = [customer.features.get(f, 0) for f in clv_model.feature_names_]
        clv = clv_model.predict([feature_vector])[0]
        results.append(CustomerResponse(
            customer_id=customer.customer_id,
            clv_prediction=clv,
        ))
    return results


@app.post("/predict/batch")
async def predict_batch(request: PredictionRequest):
    """Batch prediction for multiple models."""
    return {"message": "Batch prediction endpoint", "status": "ready", "count": len(request.customer_ids)}


@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer profile and predictions."""
    return {
        "customer_id": customer_id,
        "segment": "high_value",
        "churn_risk": 0.15,
        "clv": 2450.0,
    }


@app.get("/segments")
async def get_segments():
    """Get customer segments."""
    return {
        "segments": [
            {"name": "high_value", "count": 2500, "avg_revenue": 3500, "churn_risk": 0.08},
            {"name": "loyal", "count": 3500, "avg_revenue": 2200, "churn_risk": 0.12},
            {"name": "at_risk", "count": 2000, "avg_revenue": 800, "churn_risk": 0.65},
            {"name": "new", "count": 3000, "avg_revenue": 450, "churn_risk": 0.15},
            {"name": "dormant", "count": 1450, "avg_revenue": 200, "churn_risk": 0.45},
        ]
    }


@app.get("/metrics/overview")
async def get_overview_metrics():
    """Get dashboard overview metrics."""
    return {
        "total_customers": 12450,
        "churn_rate": 23.5,
        "avg_clv": 1245,
        "total_revenue": 2300000,
    }


# ─── Serve Frontend ─────────────────────────────────────────────────────────

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/dashboard")
    async def serve_dashboard():
        """Serve the frontend dashboard."""
        return FileResponse(os.path.join(frontend_dir, "index.html"))


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
