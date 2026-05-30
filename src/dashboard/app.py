"""Streamlit Dashboard - Phase 10"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Enterprise Customer Intelligence",
    page_icon="📊",
    layout="wide",
)


def main():
    st.title("📊 Enterprise Customer Intelligence Platform")
    st.markdown("### Churn Prediction, CLV, and Causal Impact Analysis")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Overview", "Churn Analysis", "CLV Forecast", "Segmentation",
         "Causal Impact", "Recommendations", "Model Explainability"]
    )

    if page == "Overview":
        overview_page()
    elif page == "Churn Analysis":
        churn_page()
    elif page == "CLV Forecast":
        clv_page()
    elif page == "Segmentation":
        segmentation_page()
    elif page == "Causal Impact":
        causal_page()
    elif page == "Recommendations":
        recommendations_page()
    elif page == "Model Explainability":
        explainability_page()


def overview_page():
    """Overview dashboard."""
    st.header("Platform Overview")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Customers", "12,450", "+5.2%")
    with col2:
        st.metric("Churn Rate", "23.5%", "-2.1%")
    with col3:
        st.metric("Avg CLV", "$1,245", "+8.3%")
    with col4:
        st.metric("Revenue", "$2.3M", "+12.1%")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Revenue Trend")
        months = pd.date_range(start="2024-01-01", periods=12, freq="M")
        revenue = np.random.uniform(150000, 250000, 12)
        fig = px.line(x=months, y=revenue, labels={"x": "Month", "y": "Revenue"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Customer Segments")
        segments = ["High-Value", "Loyal", "At-Risk", "New", "Dormant"]
        counts = [2500, 3500, 2000, 3000, 1450]
        fig = px.pie(values=counts, names=segments, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)


def churn_page():
    """Churn analysis page."""
    st.header("Churn Analysis")

    # Churn distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Churn Distribution")
        churn_data = pd.DataFrame({
            "Status": ["Churned", "Retained"],
            "Count": [2850, 9600],
        })
        fig = px.bar(churn_data, x="Status", y="Count", color="Status")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Churn by Segment")
        segment_churn = pd.DataFrame({
            "Segment": ["High-Value", "Loyal", "At-Risk", "New", "Dormant"],
            "Churn Rate": [0.08, 0.12, 0.65, 0.15, 0.45],
        })
        fig = px.bar(segment_churn, x="Segment", y="Churn Rate", color="Churn Rate")
        st.plotly_chart(fig, use_container_width=True)

    # Top churn factors
    st.subheader("Top Churn Drivers")
    factors = pd.DataFrame({
        "Feature": ["Support Tickets", "Inactivity Days", "Payment Delays", "Low Engagement", "Competitor Activity"],
        "Importance": [0.32, 0.25, 0.18, 0.15, 0.10],
    })
    fig = px.bar(factors, x="Importance", y="Feature", orientation="h", color="Importance")
    st.plotly_chart(fig, use_container_width=True)


def clv_page():
    """CLV analysis page."""
    st.header("Customer Lifetime Value")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg 12-Month CLV", "$1,245")
    with col2:
        st.metric("Total Predicted Revenue", "$15.5M")
    with col3:
        st.metric("High-Value Customers", "2,500")

    # CLV distribution
    st.subheader("CLV Distribution")
    clv_data = pd.DataFrame({
        "CLV": np.random.exponential(1000, 1000),
    })
    fig = px.histogram(clv_data, x="CLV", nbins=30, title="CLV Distribution")
    st.plotly_chart(fig, use_container_width=True)

    # CLV by segment
    st.subheader("CLV by Segment")
    clv_segment = pd.DataFrame({
        "Segment": ["High-Value", "Loyal", "At-Risk", "New", "Dormant"],
        "Avg CLV": [3500, 2200, 800, 450, 200],
    })
    fig = px.bar(clv_segment, x="Segment", y="Avg CLV", color="Segment")
    st.plotly_chart(fig, use_container_width=True)


def segmentation_page():
    """Customer segmentation page."""
    st.header("Customer Segmentation")

    # Segment summary
    st.subheader("Segment Summary")
    segments = pd.DataFrame({
        "Segment": ["High-Value", "Loyal", "At-Risk", "New", "Dormant"],
        "Count": [2500, 3500, 2000, 3000, 1450],
        "Avg Revenue": [3500, 2200, 800, 450, 200],
        "Churn Risk": [0.08, 0.12, 0.65, 0.15, 0.45],
    })
    st.dataframe(segments)

    # Cluster visualization placeholder
    st.subheader("Customer Clusters")
    st.info("Cluster visualization would show K-Means/Hierarchical clustering results")


def causal_page():
    """Causal impact analysis page."""
    st.header("Causal Impact Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Campaign Impact (DiD)")
        st.metric("Estimated ATE", "-5.2%", "Churn reduction")
        st.caption("Average Treatment Effect of retention campaign")

    with col2:
        st.subheader("Uplift Modeling")
        segments = ["Persuadable", "Sure Thing", "Do Not Disturb"]
        counts = [2500, 4500, 5450]
        fig = px.pie(values=counts, names=segments, title="Uplift Segments")
        st.plotly_chart(fig, use_container_width=True)


def recommendations_page():
    """Retention recommendations page."""
    st.header("Retention Recommendations")

    st.subheader("Priority Actions")

    recommendations = pd.DataFrame({
        "Priority": [1, 2, 3, 4, 5],
        "Action": ["Premium Retention Offer", "Personalized Outreach",
                   "Enhanced Onboarding", "Loyalty Program", "Win-back Campaign"],
        "Customers": [450, 1200, 800, 1500, 700],
        "Expected Impact": ["High", "High", "Medium", "Medium", "Low"],
    })
    st.dataframe(recommendations)


def explainability_page():
    """Model explainability page."""
    st.header("Model Explainability (SHAP)")

    st.subheader("Global Feature Importance")
    features = pd.DataFrame({
        "Feature": ["tenure", "monthly_charges", "total_charges", "support_tickets",
                   "payment_delay", "contract_type", "internet_service"],
        "Importance": [0.25, 0.18, 0.15, 0.12, 0.10, 0.08, 0.07],
    })
    fig = px.bar(features, x="Importance", y="Feature", orientation="h", color="Importance")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Local Explanation (Sample Customer)")
    st.info("Select a customer to see individual SHAP explanation")


if __name__ == "__main__":
    main()
