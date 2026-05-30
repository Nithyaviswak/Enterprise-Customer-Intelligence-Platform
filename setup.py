from setuptools import setup, find_packages

setup(
    name="enterprise-customer-intelligence",
    version="1.0.0",
    description="Enterprise Customer Intelligence Platform for churn prediction, CLV, and causal inference",
    author="Nithyaviswak",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "xgboost>=2.0.0",
        "lightgbm>=4.0.0",
        "catboost>=1.2.0",
    ],
    python_requires=">=3.9",
)
