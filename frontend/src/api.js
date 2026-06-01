import axios from 'axios';

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : `http://${window.location.hostname}:8000`;

export const MockData = {
    dashboard: {
        kpis: {
            total_customers: { value: 125842, change: 8.2, trend: "up" },
            avg_clv: { value: 842, change: 12.0, trend: "up" },
            churn_rate: { value: 7.4, change: -3.1, trend: "down" },
            campaign_roi: { value: 4.2, change: 1.8, trend: "up" }
        },
        revenue_trend: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            data: [2100000, 2250000, 2180000, 2420000, 2560000, 2480000, 2680000, 2750000, 2620000, 2840000, 2950000, 3100000]
        },
        retention_trend: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            data: [91.2, 91.5, 91.8, 92.0, 92.1, 92.4, 92.6, 92.5, 92.8, 93.0, 93.1, 93.4]
        },
        risk_distribution: {
            labels: ["Healthy", "At-Risk", "Critical"],
            data: [78450, 35200, 12192],
            colors: ["#10B981", "#F59E0B", "#EF4444"]
        },
        top_segments: [
            { name: "VIP", count: 8400, revenue: 4200000, churn_risk: 2.1 },
            { name: "Loyal", count: 42500, revenue: 12800000, churn_risk: 4.8 },
            { name: "Growth", count: 38200, revenue: 8900000, churn_risk: 6.2 },
            { name: "At-Risk", count: 24500, revenue: 4100000, churn_risk: 18.5 },
            { name: "Dormant", count: 12242, revenue: 980000, churn_risk: 34.2 }
        ]
    },
    churn: {
        hero: {
            current_churn_rate: 7.4,
            predicted_monthly_loss: 42000,
            at_risk_customers: 12192,
            avg_days_to_churn: 45
        },
        monthly_trend: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            churn_rate: [9.8, 9.5, 9.2, 8.8, 8.5, 8.2, 7.9, 7.8, 7.6, 7.5, 7.4, 7.4],
            customers_lost: [420, 390, 380, 360, 340, 320, 310, 305, 298, 290, 285, 280]
        },
        heatmap: {
            segments: ["VIP", "Loyal", "Growth", "At-Risk", "Dormant"],
            risk_buckets: ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"],
            data: [
                [92, 5, 2, 1, 0],
                [78, 14, 5, 2, 1],
                [60, 22, 10, 5, 3],
                [15, 20, 25, 25, 15],
                [5, 10, 20, 30, 35]
            ]
        },
        shap_features: [
            { feature: "Support Tickets", impact: 0.34, direction: "churn" },
            { feature: "Days Since Last Login", impact: 0.28, direction: "churn" },
            { feature: "Monthly Spend Decline", impact: 0.22, direction: "churn" },
            { feature: "Low Engagement Score", impact: 0.18, direction: "churn" },
            { feature: "Contract Type (Monthly)", impact: 0.15, direction: "churn" },
            { feature: "Payment Failures", impact: 0.12, direction: "churn" },
            { feature: "Loyalty Points Balance", impact: -0.08, direction: "retain" },
            { feature: "Feature Adoption Rate", impact: -0.12, direction: "retain" },
            { feature: "NPS Score", impact: -0.15, direction: "retain" },
            { feature: "Account Tenure (Years)", impact: -0.22, direction: "retain" }
        ],
        segment_churn: {
            labels: ["VIP", "Loyal", "Growth", "At-Risk", "Dormant"],
            rates: [2.1, 4.8, 6.2, 18.5, 34.2]
        }
    },
    segmentation: {
        segments: [
            { name: "VIP", count: 8400, revenue: 4200000, avg_clv: 2850, churn_pct: 2.1, color: "#10B981" },
            { name: "Loyal", count: 42500, revenue: 12800000, avg_clv: 1420, churn_pct: 4.8, color: "#4F46E5" },
            { name: "Growth", count: 38200, revenue: 8900000, avg_clv: 680, churn_pct: 6.2, color: "#6366F1" },
            { name: "At-Risk", count: 24500, revenue: 4100000, avg_clv: 320, churn_pct: 18.5, color: "#F59E0B" },
            { name: "Dormant", count: 12242, revenue: 980000, avg_clv: 85, churn_pct: 34.2, color: "#EF4444" }
        ],
        clusters: {
            "VIP": {
                x: [8.2, 8.5, 7.9, 9.1, 8.8, 7.5, 8.3, 8.0, 9.2, 8.6, 7.8, 8.4, 8.9, 8.1, 8.7],
                y: [8.4, 8.8, 8.1, 9.0, 8.5, 7.9, 8.2, 8.6, 9.3, 8.7, 8.0, 8.5, 9.1, 8.3, 8.9]
            },
            "Loyal": {
                x: [6.2, 6.5, 5.9, 7.1, 6.8, 5.5, 6.3, 6.0, 7.2, 6.6, 5.8, 6.4, 6.9, 6.1, 6.7],
                y: [6.8, 7.2, 6.5, 7.5, 7.0, 6.2, 6.9, 6.7, 7.6, 7.1, 6.4, 6.8, 7.3, 6.6, 7.0]
            },
            "Growth": {
                x: [4.5, 5.2, 3.8, 5.9, 4.8, 3.5, 4.9, 4.2, 5.6, 5.0, 4.1, 4.6, 5.3, 4.0, 4.7],
                y: [4.8, 5.5, 4.2, 6.1, 5.0, 3.8, 5.2, 4.5, 5.8, 5.3, 4.4, 4.9, 5.6, 4.3, 5.1]
            },
            "At-Risk": {
                x: [2.5, 3.1, 2.0, 3.8, 2.9, 1.8, 3.2, 2.4, 3.6, 3.0, 2.2, 2.7, 3.4, 2.1, 2.8],
                y: [3.1, 3.5, 2.6, 4.0, 3.3, 2.4, 3.6, 2.9, 3.9, 3.4, 2.7, 3.1, 3.7, 2.5, 3.2]
            },
            "Dormant": {
                x: [1.2, 1.5, 0.9, 1.8, 1.4, 0.8, 1.6, 1.1, 1.9, 1.3, 1.0, 1.4, 1.7, 0.7, 1.5],
                y: [1.4, 1.8, 1.1, 2.0, 1.5, 1.0, 1.7, 1.3, 2.1, 1.6, 1.2, 1.5, 1.9, 0.9, 1.6]
            }
        }
    },
    clv: {
        kpis: {
            avg_clv: { value: 842, change: 12.0 },
            total_ltv: { value: 106000000, change: 15.4 },
            high_value_pct: { value: 6.7, change: 1.2 },
            payback_months: { value: 4.8, change: -0.6 }
        },
        projection: {
            labels: ["Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25", "Q2'25", "Q3'25", "Q4'25"],
            actual: [24500000, 26200000, 27800000, 29500000, 31000000, null, null, null],
            forecast: [null, null, null, null, 31000000, 33200000, 35100000, 37400000],
            upper: [null, null, null, null, 31000000, 34800000, 37500000, 40200000],
            lower: [null, null, null, null, 31000000, 31600000, 32700000, 34600000]
        },
        distribution: {
            labels: ["$0-100", "$100-300", "$300-500", "$500-800", "$800-1200", "$1200-2000", "$2000-3000", "$3000+"],
            counts: [12200, 28500, 32100, 24800, 15400, 8200, 3400, 1242]
        }
    },
    causal: {
        treatment_control: {
            treatment: { label: "Treatment Group", size: 4500, churn_rate: 12.0, avg_clv: 920, retention: 88.0 },
            control: { label: "Control Group", size: 5450, churn_rate: 18.0, avg_clv: 780, retention: 82.0 }
        },
        effects: {
            ate: { value: -6.0, ci_lower: -8.2, ci_upper: -3.8, p_value: 0.001 },
            att: { value: -7.2, ci_lower: -9.5, ci_upper: -4.9, p_value: 0.0005 },
            uplift: { value: 5.8, ci_lower: 3.5, ci_upper: 8.1, p_value: 0.002 }
        },
        did_plot: {
            labels: ["6 Mo Before", "3 Mo Before", "Campaign", "3 Mo After", "6 Mo After"],
            treatment: [18.5, 18.2, 17.0, 13.5, 12.0],
            control: [18.0, 17.8, 17.5, 17.2, 18.0],
            treatment_ci: [1.2, 1.1, 1.0, 0.9, 0.8],
            control_ci: [1.1, 1.0, 0.9, 0.8, 0.9]
        },
        uplift_segments: {
            labels: ["Persuadable", "Sure Thing", "Do Not Disturb", "Lost Cause"],
            counts: [18500, 42200, 38900, 26242],
            colors: ["#10B981", "#4F46E5", "#F59E0B", "#EF4444"]
        }
    },
    recommendations: {
        cards: [
            {
                segment: "High-Value At-Risk",
                customer_count: 842,
                predicted_churn: 91,
                recommendation: "Offer Premium Retention Package",
                expected_lift: 18,
                priority: "critical",
                estimated_revenue_saved: 2400000
            },
            {
                segment: "Growth Segment",
                customer_count: 2150,
                predicted_churn: 34,
                recommendation: "Personalized Upsell Campaign",
                expected_lift: 12,
                priority: "high",
                estimated_revenue_saved: 1800000
            },
            {
                segment: "Loyal Declining",
                customer_count: 1680,
                predicted_churn: 22,
                recommendation: "Loyalty Reward Acceleration",
                expected_lift: 8,
                priority: "medium",
                estimated_revenue_saved: 950000
            },
            {
                segment: "New Customers",
                customer_count: 3200,
                predicted_churn: 15,
                recommendation: "Enhanced Onboarding Sequence",
                expected_lift: 6,
                priority: "medium",
                estimated_revenue_saved: 680000
            },
            {
                segment: "Dormant Reactivation",
                customer_count: 4500,
                predicted_churn: 62,
                recommendation: "Win-Back Email + Discount",
                expected_lift: 4,
                priority: "low",
                estimated_revenue_saved: 420000
            }
        ],
        priority_matrix: {
            quadrants: [
                { label: "Protect", description: "High CLV + High Risk", count: 842, color: "#EF4444" },
                { label: "Nurture", description: "High CLV + Low Risk", count: 7558, color: "#10B981" },
                { label: "Monitor", description: "Low CLV + High Risk", count: 11350, color: "#F59E0B" },
                { label: "Maintain", description: "Low CLV + Low Risk", count: 106092, color: "#4F46E5" }
            ]
        },
        summary: "AI analysis identifies $6.25M in recoverable revenue across 12,372 at-risk customers. Top priority: 842 high-value customers showing critical churn signals. Recommended total investment: $340K for projected 4.2x ROI."
    }
};

export const CustomerIQAPI = {
    async checkConnection() {
        try {
            const res = await axios.get(`${API_BASE_URL}/health`, { timeout: 2000 });
            return res.status === 200;
        } catch (e) {
            return false;
        }
    },

    async fetchData(endpoint) {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/${endpoint}`);
            if (res.status === 200) {
                return res.data;
            }
        } catch (e) {
            console.warn(`Fetch error for endpoint '${endpoint}', falling back to mock data:`, e);
        }
        return MockData[endpoint];
    }
};
