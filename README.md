<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn">
  <img src="https://img.shields.io/badge/XGBoost-189FDD?style=for-the-badge&logo=xgboost&logoColor=white" alt="XGBoost">
  <img src="https://img.shields.io/badge/SHAP-4B0082?style=for-the-badge" alt="SHAP">
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" alt="MLflow">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/ECharts-AA2116?style=for-the-badge&logo=apacheecharts&logoColor=white" alt="Apache ECharts">
</p>

<h1 align="center">🧠 Enterprise Customer Intelligence Platform</h1>

<p align="center">
  <strong>An end-to-end ML platform for predicting customer churn, forecasting lifetime value, and optimizing retention strategies using causal inference and explainable AI.</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-ml-pipeline">ML Pipeline</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-dashboard">Dashboard</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## ✨ Features

| Module | Description | Techniques |
|--------|-------------|------------|
| 🔮 **Churn Prediction** | Multi-model ensemble to predict customer attrition | XGBoost, LightGBM, CatBoost, Logistic Regression, Random Forest |
| 💰 **CLV Forecasting** | 12-month customer lifetime value projection | Regression ensemble with temporal feature engineering |
| 👥 **Customer Segmentation** | Behavioral clustering with persona mapping | K-Means, Hierarchical, DBSCAN with silhouette optimization |
| 🔬 **Causal Inference** | Measure true campaign impact on retention | Propensity Score Matching, Difference-in-Differences, Uplift Modeling |
| 🧪 **Explainable AI** | Transparent model decisions via SHAP | Global & local feature importance, waterfall plots, churn driver analysis |
| 🎯 **Recommendations** | Rule-based retention intervention engine | ROI-ranked actions with cost-benefit scoring |
| 📊 **Interactive Dashboard** | Real-time analytics with dark/light theme | Chart.js visualizations, 7-page SPA, responsive design |
| ⚡ **REST API** | Production-ready prediction endpoints | FastAPI with auto-docs, batch inference, health monitoring |
| 🔄 **MLOps** | Experiment tracking & model versioning | MLflow integration with model registry |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Overview  │ │  Churn   │ │   CLV    │ │ Segments │ │  Causal  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │   Recommendations    │  │   Explainability     │                │
│  └──────────────────────┘  └──────────────────────┘                │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ REST API
┌───────────────────────────────▼─────────────────────────────────────┐
│                       BACKEND (FastAPI + Python)                    │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   Churn      │  │    CLV      │  │ Segmentation│                │
│  │  Predictor   │  │  Predictor  │  │  Clustering │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   Causal     │  │   SHAP      │  │Recommendation│               │
│  │  Inference   │  │  Explainer  │  │   Engine    │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │    Data      │  │  Feature    │  │   MLOps     │                │
│  │ Engineering  │  │ Engineering │  │  Tracking   │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/Nithyaviswak/Enterprise-Customer-Intelligence-Platform.git
cd Enterprise-Customer-Intelligence-Platform
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database and API settings
```

### 5. Start the API Server

```bash
python run.py
```

The API will be available at **http://localhost:8000**.

### 6. Run the React Frontend

Navigate to the frontend folder, install the required node packages, and run the development server:

```bash
cd frontend
npm install
npm run dev
```

The React frontend dashboard will be available at **http://localhost:5173**.

---

## 📂 Project Structure

```
Enterprise-Customer-Intelligence-Platform/
│
├── backend/                        # Backend ML modules
│   ├── api/
│   │   └── main.py                 # FastAPI app with endpoints & CORS
│   ├── churn_prediction/
│   │   └── models.py               # Multi-model churn classification
│   ├── clv_prediction/
│   │   └── predictor.py            # Customer lifetime value regression
│   ├── causal_inference/
│   │   └── engine.py               # PSM, DiD, uplift modeling
│   ├── segmentation/
│   │   └── clustering.py           # K-Means, Hierarchical, DBSCAN
│   ├── recommendations/
│   │   └── engine.py               # Rule-based retention strategies
│   ├── explainable_ai/
│   │   └── shap_explainer.py       # SHAP global & local explanations
│   ├── data_engineering/
│   │   └── preprocessing.py        # Missing values, outliers, validation
│   ├── features/
│   │   └── engineering.py          # Behavioral, temporal, revenue features
│   ├── eda/
│   │   └── analyzer.py             # EDA, RFM, cohort analysis
│   ├── mlops/
│   │   └── tracking.py             # MLflow experiment tracking
│   └── dashboard/
│       └── app.py                  # Streamlit dashboard (alternative UI)
│
├── frontend/                       # React + Vite web dashboard
│   ├── index.html                  # Main entry point
│   ├── vite.config.js              # Vite configuration
│   ├── package.json                # Frontend dependencies & scripts
│   ├── public/                     # Static assets
│   └── src/                        # React source code
│       ├── App.jsx                 # Root component
│       ├── App.css                 # Global styling
│       └── main.jsx                # Application entry point
│       └── ...                     # Components and state layers
│
├── config/
│   └── __init__.py                 # Centralized configuration
│
├── src/                            # Legacy source modules (mirrored in backend/)
├── data/                           # Data files (gitignored)
├── models/                         # Trained model artifacts (gitignored)
├── tests/                          # Unit & integration tests
├── notebooks/                      # Jupyter notebooks for exploration
├── docs/                           # Documentation
│
├── .env                            # Environment variables (gitignored)
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── setup.py                        # Package configuration
└── run.py                          # Server entry point
```

---

## 🔬 ML Pipeline

### Phase 1 — Data Engineering
```python
from backend.data_engineering import DataPreprocessor

preprocessor = DataPreprocessor(df)
preprocessor.validate_data()
clean_df = preprocessor.handle_missing_values(strategy="auto")
outliers = preprocessor.detect_outliers(method="iqr")
```

### Phase 2 — Exploratory Data Analysis
```python
from backend.eda import EDAAnalyzer

analyzer = EDAAnalyzer(df, target_col="churn")
churn_dist = analyzer.analyze_churn_distribution()
rfm = analyzer.rfm_analysis("customer_id", "recency", "frequency", "monetary")
report = analyzer.generate_summary_report()
```

### Phase 3 — Feature Engineering
```python
from backend.features import FeatureEngineer

engineer = FeatureEngineer(df)
df = engineer.create_behavior_features("customer_id", "txn_id", "amount", "date")
df = engineer.create_temporal_features("date", "customer_id")
df = engineer.create_engagement_features("customer_id", login_col="logins")
```

### Phase 4 — Customer Segmentation
```python
from backend.segmentation import CustomerSegmenter

segmenter = CustomerSegmenter(df, features=["revenue", "frequency", "recency"])
segmenter.prepare_data()
optimal = segmenter.find_optimal_k(range(2, 11))
labels = segmenter.kmeans_clustering(n_clusters=optimal["optimal_k"])
df = segmenter.assign_personas()
```

### Phase 5 — Churn Prediction
```python
from backend.churn_prediction import ChurnPredictor

predictor = ChurnPredictor(df, target_col="churn")
predictor.prepare_data(features=feature_list)
predictor.train_xgboost(n_estimators=200, max_depth=6)
predictor.train_lightgbm()
best = predictor.optimize_hyperparameters("xgboost", n_trials=50)
comparison = predictor.compare_models()
```

### Phase 6 — CLV Prediction
```python
from backend.clv_prediction import CLVPredictor

clv = CLVPredictor(df)
clv_data = clv.prepare_clv_data("customer_id", "amount", "date", prediction_months=12)
results = clv.train_regression_clv(features=["total_revenue", "order_count", "tenure_days"])
```

### Phase 7 — Explainable AI
```python
from backend.explainable_ai import ModelExplainer

explainer = ModelExplainer(model, X_train, X_test)
explainer.create_explainer(method="tree")
global_imp = explainer.get_global_importance(top_n=15)
local_exp = explainer.get_local_explanation(customer_idx=42)
drivers = explainer.get_churn_drivers(X_test)
```

### Phase 8 — Causal Inference
```python
from backend.causal_inference import CausalInferenceEngine

causal = CausalInferenceEngine(df)
psm = causal.propensity_score_matching("treated", "churned", features, n_neighbors=5)
did = causal.difference_in_differences("treated", "date", "churned", pre_period, post_period)
uplift_df = causal.uplift_modeling("treated", "churned", features)
```

---

## 📡 API Reference

Start the server with `python run.py`, then visit **http://localhost:8000/docs** for interactive Swagger documentation.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API root & version info |
| `GET` | `/health` | Health check with model status |
| `POST` | `/predict/churn` | Predict churn probability |
| `POST` | `/predict/clv` | Predict customer lifetime value |
| `POST` | `/predict/batch` | Batch predictions |
| `GET` | `/customers/{id}` | Customer profile & predictions |
| `GET` | `/segments` | Customer segment summary |
| `GET` | `/metrics/overview` | Dashboard overview metrics |
| `GET` | `/dashboard` | Serve frontend dashboard |

### Example Request

```bash
curl -X POST http://localhost:8000/predict/churn \
  -H "Content-Type: application/json" \
  -d '[{
    "customer_id": "CUST-001",
    "features": {
      "tenure": 12,
      "monthly_charges": 85.5,
      "support_tickets": 3,
      "payment_delay": 1
    }
  }]'
```

---

## 📊 Dashboard

The platform includes a **7-page interactive dashboard** built with **React** and **Apache ECharts**:

| Page | Visualizations |
|------|---------------|
| **Overview** | KPI metrics, revenue trend line chart, segment doughnut |
| **Churn Analysis** | Monthly churn trend, distribution, segment breakdown, driver importance |
| **CLV Forecast** | CLV histogram, segment comparison, prediction metrics |
| **Segmentation** | K-Means scatter plot, persona cards, segment distribution |
| **Causal Impact** | Difference-in-Differences bar chart, uplift segmentation |
| **Recommendations** | ROI-ranked intervention table, budget insights |
| **Explainability** | Global SHAP importance, local waterfall explanation |

**Features:**
- 🌙 Dark / Light theme toggle
- 📱 Fully responsive (mobile, tablet, desktop)
- ⚡ Real-time API status indicator
- 🔄 Refresh with animation
- 🎨 Premium glassmorphism design with smooth transitions

---

## 🛠 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **ML Models** | Scikit-learn, XGBoost, LightGBM, CatBoost, Optuna |
| **Causal** | DoWhy, EconML, CausalML |
| **Explainability** | SHAP |
| **API** | FastAPI, Uvicorn, Pydantic |
| **Frontend** | React, Vite, Apache ECharts, CSS3, ES6+ |
| **MLOps** | MLflow, Joblib |
| **Data** | Pandas, NumPy, SciPy |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Database** | PostgreSQL, SQLAlchemy |
| **Testing** | Pytest |

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <strong>Built with ❤️ by <a href="https://github.com/Nithyaviswak">Nithyaviswak</a></strong>
</p>
