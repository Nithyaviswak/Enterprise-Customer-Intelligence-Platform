"""
Enterprise Customer Intelligence Platform - Backend Runner

Start the FastAPI server:
    python run.py

The API will be available at http://localhost:8000
The dashboard will be available at http://localhost:8000/dashboard
API docs at http://localhost:8000/docs
"""

import uvicorn
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend"],
    )
