/**
 * Simulated data layer for the Enterprise Customer Intelligence Platform.
 * In production, these would be fetched from the FastAPI backend at /api/*.
 */

const DashboardData = {
    overview: {
        metrics: {
            totalCustomers: { value: 12450, change: 5.2, trend: 'up' },
            churnRate: { value: 23.5, change: -2.1, trend: 'down' },
            avgCLV: { value: 1245, change: 8.3, trend: 'up' },
            revenue: { value: 2300000, change: 12.1, trend: 'up' },
        },
        revenueByMonth: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            data: [185000, 192000, 178000, 205000, 215000, 198000, 225000, 232000, 218000, 240000, 248000, 255000],
        },
        segmentDistribution: {
            labels: ['High-Value', 'Loyal', 'At-Risk', 'New', 'Dormant'],
            data: [2500, 3500, 2000, 3000, 1450],
            colors: ['#3b82f6', '#8b5cf6', '#f43f5e', '#10b981', '#64748b'],
        },
    },
    churn: {
        metrics: {
            totalChurned: { value: 2850, change: -8.5, trend: 'down' },
            avgChurnRate: { value: 23.5, change: -2.1, trend: 'down' },
            predictedChurn: { value: 1240, change: 3.2, trend: 'up' },
            retentionRate: { value: 76.5, change: 2.1, trend: 'up' },
        },
        distribution: { labels: ['Churned', 'Retained'], data: [2850, 9600], colors: ['#f43f5e', '#10b981'] },
        bySegment: {
            labels: ['High-Value', 'Loyal', 'At-Risk', 'New', 'Dormant'],
            data: [0.08, 0.12, 0.65, 0.15, 0.45],
        },
        drivers: {
            labels: ['Support Tickets', 'Inactivity Days', 'Payment Delays', 'Low Engagement', 'Competitor Activity', 'Price Sensitivity', 'Product Issues'],
            data: [0.32, 0.25, 0.18, 0.15, 0.10, 0.08, 0.05],
        },
        monthlyTrend: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            churned: [320, 280, 310, 260, 240, 220, 200, 190, 180, 170, 165, 155],
            retained: [780, 820, 790, 840, 860, 880, 900, 910, 920, 930, 935, 945],
        },
    },
    clv: {
        metrics: {
            avgCLV12: { value: 1245, change: 8.3, trend: 'up' },
            totalPredicted: { value: 15500000, change: 15.2, trend: 'up' },
            highValueCount: { value: 2500, change: 4.1, trend: 'up' },
            avgOrderValue: { value: 85, change: 3.7, trend: 'up' },
        },
        distribution: [120, 450, 890, 1200, 980, 750, 520, 380, 250, 180, 120, 95, 65, 40, 25],
        bySegment: {
            labels: ['High-Value', 'Loyal', 'At-Risk', 'New', 'Dormant'],
            data: [3500, 2200, 800, 450, 200],
        },
        trend: {
            labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025'],
            actual: [1050, 1100, 1150, 1180, 1220, 1245],
            predicted: [null, null, null, null, 1210, 1240, 1280, 1320],
        },
    },
    segmentation: {
        segments: [
            { name: 'High-Value', count: 2500, avgRevenue: 3500, churnRisk: 0.08, color: '#3b82f6', icon: '💎' },
            { name: 'Loyal', count: 3500, avgRevenue: 2200, churnRisk: 0.12, color: '#8b5cf6', icon: '🏆' },
            { name: 'At-Risk', count: 2000, avgRevenue: 800, churnRisk: 0.65, color: '#f43f5e', icon: '⚠️' },
            { name: 'New', count: 3000, avgRevenue: 450, churnRisk: 0.15, color: '#10b981', icon: '🌱' },
            { name: 'Dormant', count: 1450, avgRevenue: 200, churnRisk: 0.45, color: '#64748b', icon: '💤' },
        ],
        clusterData: {
            clusters: [
                { x: Array.from({length: 40}, () => Math.random() * 3 + 7), y: Array.from({length: 40}, () => Math.random() * 2 + 8) },
                { x: Array.from({length: 55}, () => Math.random() * 3 + 4), y: Array.from({length: 55}, () => Math.random() * 3 + 5) },
                { x: Array.from({length: 35}, () => Math.random() * 4 + 1), y: Array.from({length: 35}, () => Math.random() * 3 + 1) },
                { x: Array.from({length: 50}, () => Math.random() * 3 + 6), y: Array.from({length: 50}, () => Math.random() * 2 + 2) },
                { x: Array.from({length: 25}, () => Math.random() * 2 + 1), y: Array.from({length: 25}, () => Math.random() * 2 + 6) },
            ],
        },
    },
    causal: {
        metrics: {
            campaignATE: { value: -5.2, unit: '%' },
            confidence: { value: 95, unit: '%' },
            treatedGroup: { value: 4500, unit: '' },
            controlGroup: { value: 5450, unit: '' },
        },
        upliftSegments: {
            labels: ['Persuadable', 'Sure Thing', 'Do Not Disturb', 'Lost Cause'],
            data: [2500, 4500, 3200, 2250],
            colors: ['#10b981', '#3b82f6', '#f59e0b', '#f43f5e'],
        },
        didResults: {
            labels: ['Pre-Campaign', 'Post-Campaign'],
            treated: [0.35, 0.22],
            control: [0.33, 0.31],
        },
    },
    recommendations: {
        actions: [
            { priority: 1, action: 'Premium Retention Offer', customers: 450, impact: 'High', roi: 4.2, segment: 'High-Value', cost: '$45,000' },
            { priority: 2, action: 'Personalized Outreach', customers: 1200, impact: 'High', roi: 3.8, segment: 'At-Risk', cost: '$60,000' },
            { priority: 3, action: 'Enhanced Onboarding', customers: 800, impact: 'Medium', roi: 3.1, segment: 'New', cost: '$32,000' },
            { priority: 4, action: 'Loyalty Program Enrollment', customers: 1500, impact: 'Medium', roi: 2.5, segment: 'Loyal', cost: '$45,000' },
            { priority: 5, action: 'Win-back Campaign', customers: 700, impact: 'Low', roi: 1.8, segment: 'Dormant', cost: '$14,000' },
            { priority: 6, action: 'Low-cost Email Campaign', customers: 2100, impact: 'Low', roi: 1.5, segment: 'All', cost: '$8,400' },
        ],
    },
    explainability: {
        globalImportance: {
            labels: ['Tenure', 'Monthly Charges', 'Total Charges', 'Support Tickets', 'Payment Delay', 'Contract Type', 'Internet Service', 'Engagement Score', 'Login Frequency', 'Email Opens'],
            data: [0.25, 0.18, 0.15, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04],
        },
        localExplanation: {
            customer: 'CUST-00421',
            prediction: 0.82,
            features: [
                { name: 'Support Tickets (12)', shap: 0.25, direction: 'churn' },
                { name: 'Inactivity (45 days)', shap: 0.18, direction: 'churn' },
                { name: 'Payment Delay (3x)', shap: 0.12, direction: 'churn' },
                { name: 'Tenure (8 months)', shap: 0.08, direction: 'churn' },
                { name: 'Contract (Monthly)', shap: 0.05, direction: 'churn' },
                { name: 'Loyalty Points (850)', shap: -0.04, direction: 'retain' },
                { name: 'Email Engagement (72%)', shap: -0.06, direction: 'retain' },
                { name: 'Product Usage (High)', shap: -0.10, direction: 'retain' },
            ],
        },
    },
};
