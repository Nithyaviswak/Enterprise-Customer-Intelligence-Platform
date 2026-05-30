"""FastAPI Backend - Phase 10"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import joblib
import os

app = FastAPI(
    title="Enterprise Customer Intelligence API",
    description="API for churn prediction, CLV, and recommendations",
    version="1.0.0",
)


# Data models
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


# Global variables for models
churn_model = None
clv_model = None
recommendation_model = None


def load_models():
    """Load trained models."""
    global churn_model, clv_model, recommendation_model

    models_dir = "models"
    if os.path.exists(f"{models_dir}/churn_model.pkl"):
        churn_model = joblib.load(f"{models_dir}/churn_model.pkl")
    if os.path.exists(f"{models_dir}/clv_model.pkl"):
        clv_model = joblib.load(f"{models_dir}/clv_model.pkl")


@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    load_models()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Enterprise Customer Intelligence API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "models_loaded": churn_model is not None}


@app.post("/predict/churn", response_model=List[CustomerResponse])
async def predict_churn(customers: List[CustomerFeatures]):
    """Predict churn probability for customers."""
    if churn_model is None:
        raise HTTPException(status_code=503, detail="Churn model not loaded")

    results = []
    for customer in customers:
        # Extract features in correct order
        feature_vector = [customer.features.get(f, 0) for f in churn_model.feature_names_]

        # Predict
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
        # Extract features
        feature_vector = [customer.features.get(f, 0) for f in clv_model.feature_names_]

        # Predict
        clv = clv_model.predict([feature_vector])[0]

        results.append(CustomerResponse(
            customer_id=customer.customer_id,
            clv_prediction=clv,
        ))

    return results


@app.post("/predict/batch")
async def predict_batch(request: PredictionRequest):
    """Batch prediction for multiple models."""
    # Placeholder for batch prediction
    return {"message": "Batch prediction endpoint", "status": "implemented"}


@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer profile and predictions."""
    # Placeholder - would fetch from database
    return {
        "customer_id": customer_id,
        "message": "Customer profile endpoint",
    }


@app.get("/segments")
async def get_segments():
    """Get customer segments."""
    # Placeholder - would fetch from database
    return {
        "segments": ["high_value", "at_risk", "loyal", "new", "dormant"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
