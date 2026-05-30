/**
 * Page renderers for each dashboard section.
 */

function fmt(n, prefix = '', suffix = '') {
    if (n >= 1000000) return prefix + (n / 1000000).toFixed(1) + 'M' + suffix;
    if (n >= 1000) return prefix + n.toLocaleString() + suffix;
    return prefix + n + suffix;
}

function metricCard(label, value, change, trend, iconClass, colorClass, delay) {
    const arrow = trend === 'up' ? '↑' : '↓';
    const trendBadge = trend === 'down' && change < 0 ? 'up' : trend; // negative churn = good
    return `
    <div class="metric-card ${colorClass} animate-in animate-delay-${delay}">
        <div class="metric-header">
            <span class="metric-label">${label}</span>
            <div class="metric-icon ${colorClass}">${iconClass}</div>
        </div>
        <div class="metric-value">${value}</div>
        <span class="metric-change ${trendBadge}">${arrow} ${Math.abs(change)}%</span>
    </div>`;
}

const PageRenderers = {
    overview() {
        const d = DashboardData.overview;
        const m = d.metrics;
        return `
            <div class="metrics-grid">
                ${metricCard('Total Customers', fmt(m.totalCustomers.value), m.totalCustomers.change, m.totalCustomers.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>', 'blue', 1)}
                ${metricCard('Churn Rate', m.churnRate.value + '%', m.churnRate.change, 'down',
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>', 'rose', 2)}
                ${metricCard('Average CLV', '$' + fmt(m.avgCLV.value), m.avgCLV.change, m.avgCLV.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>', 'emerald', 3)}
                ${metricCard('Total Revenue', '$' + fmt(m.revenue.value), m.revenue.change, m.revenue.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>', 'purple', 4)}
            </div>
            <div class="charts-grid">
                <div class="chart-card animate-in animate-delay-2">
                    <div class="chart-header">
                        <div><div class="chart-title">Monthly Revenue Trend</div><div class="chart-subtitle">Jan – Dec 2024</div></div>
                        <span class="chart-badge emerald">+12.1%</span>
                    </div>
                    <div class="chart-container" style="height:280px"><canvas id="chart-revenue"></canvas></div>
                </div>
                <div class="chart-card animate-in animate-delay-3">
                    <div class="chart-header">
                        <div><div class="chart-title">Customer Segments</div><div class="chart-subtitle">Distribution by value tier</div></div>
                        <span class="chart-badge blue">5 segments</span>
                    </div>
                    <div class="chart-container" style="height:280px"><canvas id="chart-segments"></canvas></div>
                </div>
            </div>
            <div class="insights-grid">
                <div class="insight-card animate-in animate-delay-3">
                    <div class="insight-icon" style="background:rgba(16,185,129,0.12)">📈</div>
                    <div class="insight-content"><h4>Revenue Growing</h4><p>Monthly revenue increased 12.1% year-over-year, driven by high-value segment expansion.</p></div>
                </div>
                <div class="insight-card animate-in animate-delay-4">
                    <div class="insight-icon" style="background:rgba(244,63,94,0.12)">🎯</div>
                    <div class="insight-content"><h4>Churn Declining</h4><p>Churn rate decreased 2.1% after implementing targeted retention campaigns for at-risk customers.</p></div>
                </div>
                <div class="insight-card animate-in animate-delay-4">
                    <div class="insight-icon" style="background:rgba(59,130,246,0.12)">💡</div>
                    <div class="insight-content"><h4>CLV Opportunity</h4><p>2,000 at-risk customers with above-average CLV identified. Prioritize personalized outreach.</p></div>
                </div>
            </div>`;
    },

    churn() {
        const d = DashboardData.churn;
        const m = d.metrics;
        return `
            <div class="metrics-grid">
                ${metricCard('Total Churned', fmt(m.totalChurned.value), m.totalChurned.change, 'down',
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="18" y1="8" x2="23" y2="13"/><line x1="23" y1="8" x2="18" y2="13"/></svg>', 'rose', 1)}
                ${metricCard('Churn Rate', m.avgChurnRate.value + '%', m.avgChurnRate.change, 'down',
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>', 'amber', 2)}
                ${metricCard('Predicted to Churn', fmt(m.predictedChurn.value), m.predictedChurn.change, m.predictedChurn.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>', 'purple', 3)}
                ${metricCard('Retention Rate', m.retentionRate.value + '%', m.retentionRate.change, m.retentionRate.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>', 'emerald', 4)}
            </div>
            <div class="charts-grid">
                <div class="chart-card animate-in animate-delay-2">
                    <div class="chart-header"><div><div class="chart-title">Monthly Churn Trend</div><div class="chart-subtitle">Churned vs Retained customers</div></div></div>
                    <div class="chart-container" style="height:280px"><canvas id="chart-churn-trend"></canvas></div>
                </div>
                <div class="chart-card animate-in animate-delay-3">
                    <div class="chart-header"><div><div class="chart-title">Churn Distribution</div><div class="chart-subtitle">Overall customer status</div></div></div>
                    <div class="chart-container" style="height:280px"><canvas id="chart-churn-dist"></canvas></div>
                </div>
            </div>
            <div class="charts-grid">
                <div class="chart-card animate-in animate-delay-3">
                    <div class="chart-header"><div><div class="chart-title">Churn Rate by Segment</div><div class="chart-subtitle">Segment-level analysis</div></div></div>
                    <div class="chart-container" style="height:260px"><canvas id="chart-churn-segment"></canvas></div>
                </div>
                <div class="chart-card animate-in animate-delay-4">
                    <div class="chart-header"><div><div class="chart-title">Top Churn Drivers</div><div class="chart-subtitle">Feature importance from XGBoost model</div></div></div>
                    <div class="chart-container" style="height:260px"><canvas id="chart-churn-drivers"></canvas></div>
                </div>
            </div>`;
    },

    clv() {
        const d = DashboardData.clv;
        const m = d.metrics;
        return `
            <div class="metrics-grid">
                ${metricCard('Avg 12-Month CLV', '$' + fmt(m.avgCLV12.value), m.avgCLV12.change, m.avgCLV12.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>', 'emerald', 1)}
                ${metricCard('Total Predicted Revenue', '$' + fmt(m.totalPredicted.value), m.totalPredicted.change, m.totalPredicted.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>', 'blue', 2)}
                ${metricCard('High-Value Customers', fmt(m.highValueCount.value), m.highValueCount.change, m.highValueCount.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>', 'purple', 3)}
                ${metricCard('Avg Order Value', '$' + m.avgOrderValue.value, m.avgOrderValue.change, m.avgOrderValue.trend,
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>', 'cyan', 4)}
            </div>
            <div class="charts-grid">
                <div class="chart-card animate-in animate-delay-2">
                    <div class="chart-header"><div><div class="chart-title">CLV Distribution</div><div class="chart-subtitle">Customer lifetime value histogram</div></div></div>
                    <div class="chart-container" style="height:280px"><canvas id="chart-clv-dist"></canvas></div>
                </div>
                <div class="chart-card animate-in animate-delay-3">
                    <div class="chart-header"><div><div class="chart-title">CLV by Segment</div><div class="chart-subtitle">Average CLV per customer segment</div></div></div>
                    <div class="chart-container" style="height:280px"><canvas id="chart-clv-segment"></canvas></div>
                </div>
            </div>`;
    },

    segmentation() {
        const d = DashboardData.segmentation;
        let segCards = d.segments.map((s, i) => `
            <div class="metric-card animate-in animate-delay-${i % 4 + 1}" style="border-left: 3px solid ${s.color}">
                <div class="metric-header"><span class="metric-label">${s.icon} ${s.name}</span></div>
                <div class="metric-value">${fmt(s.count)}</div>
                <div style="display:flex;gap:16px;margin-top:8px">
                    <div><span style="font-size:0.75rem;color:var(--text-muted)">Avg Revenue</span><br><strong>$${fmt(s.avgRevenue)}</strong></div>
                    <div><span style="font-size:0.75rem;color:var(--text-muted)">Churn Risk</span><br><strong style="color:${s.churnRisk > 0.3 ? 'var(--accent-rose)' : 'var(--accent-emerald)'}">${(s.churnRisk * 100).toFixed(0)}%</strong></div>
                </div>
            </div>`).join('');

        return `
            <div class="metrics-grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">${segCards}</div>
            <div class="charts-grid">
                <div class="chart-card animate-in animate-delay-2">
                    <div class="chart-header"><div><div class="chart-title">Customer Clusters (K-Means)</div><div class="chart-subtitle">Revenue vs Engagement Score</div></div><span class="chart-badge purple">k=5</span></div>
                    <div class="chart-container" style="height:320px"><canvas id="chart-clusters"></canvas></div>
                </div>
                <div class="chart-card animate-in animate-delay-3">
                    <div class="chart-header"><div><div class="chart-title">Segment Distribution</div><div class="chart-subtitle">Customers per segment</div></div></div>
                    <div class="chart-container" style="height:320px"><canvas id="chart-seg-dist"></canvas></div>
                </div>
            </div>`;
    },

    causal() {
        const d = DashboardData.causal;
        return `
            <div class="metrics-grid">
                <div class="metric-card rose animate-in animate-delay-1">
                    <div class="metric-header"><span class="metric-label">Campaign ATE</span></div>
                    <div class="metric-value">${d.metrics.campaignATE.value}%</div>
                    <span class="metric-change up">Churn reduction</span>
                </div>
                <div class="metric-card emerald animate-in animate-delay-2">
                    <div class="metric-header"><span class="metric-label">Confidence Level</span></div>
                    <div class="metric-value">${d.metrics.confidence.value}%</div>
                    <span class="metric-change up">Statistical significance</span>
                </div>
                <div class="metric-card blue animate-in animate-delay-3">
                    <div class="metric-header"><span class="metric-label">Treated Group</span></div>
                    <div class="metric-value">${fmt(d.metrics.treatedGroup.value)}</div>
                    <span class="badge info">Campaign Recipients</span>
                </div>
                <div class="metric-card purple animate-in animate-delay-4">
                    <div class="metric-header"><span class="metric-label">Control Group</span></div>
                    <div class="metric-value">${fmt(d.metrics.controlGroup.value)}</div>
                    <span class="badge info">Holdout</span>
                </div>
            </div>
            <div class="charts-grid">
                <div class="chart-card animate-in animate-delay-2">
                    <div class="chart-header"><div><div class="chart-title">Difference-in-Differences</div><div class="chart-subtitle">Treated vs Control group churn rates</div></div></div>
                    <div class="chart-container" style="height:280px"><canvas id="chart-did"></canvas></div>
                </div>
                <div class="chart-card animate-in animate-delay-3">
                    <div class="chart-header"><div><div class="chart-title">Uplift Segmentation</div><div class="chart-subtitle">Customer response classification</div></div></div>
                    <div class="chart-container" style="height:280px"><canvas id="chart-uplift"></canvas></div>
                </div>
            </div>`;
    },

    recommendations() {
        const d = DashboardData.recommendations;
        let rows = d.actions.map(a => `
            <tr>
                <td><strong>#${a.priority}</strong></td>
                <td><strong>${a.action}</strong></td>
                <td>${fmt(a.customers)}</td>
                <td><span class="badge ${a.impact === 'High' ? 'high' : a.impact === 'Medium' ? 'medium' : 'low'}">${a.impact}</span></td>
                <td><strong>${a.roi}x</strong></td>
                <td><span class="badge info">${a.segment}</span></td>
                <td>${a.cost}</td>
            </tr>`).join('');

        return `
            <div class="insights-grid" style="margin-bottom:24px">
                <div class="insight-card animate-in animate-delay-1">
                    <div class="insight-icon" style="background:rgba(59,130,246,0.12)">🎯</div>
                    <div class="insight-content"><h4>Top Priority</h4><p>Premium retention offers for 450 high-value customers at risk. Expected ROI: 4.2x with $45K investment.</p></div>
                </div>
                <div class="insight-card animate-in animate-delay-2">
                    <div class="insight-icon" style="background:rgba(16,185,129,0.12)">💰</div>
                    <div class="insight-content"><h4>Total Budget</h4><p>$204,400 recommended across 6 interventions targeting 6,750 customers with combined expected ROI of 2.8x.</p></div>
                </div>
            </div>
            <div class="data-table-wrapper animate-in animate-delay-3">
                <div class="data-table-header">
                    <div class="data-table-title">Ranked Retention Interventions</div>
                    <span class="chart-badge blue">${d.actions.length} actions</span>
                </div>
                <table class="data-table">
                    <thead><tr><th>Priority</th><th>Action</th><th>Customers</th><th>Impact</th><th>ROI</th><th>Segment</th><th>Cost</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>`;
    },

    explainability() {
        const d = DashboardData.explainability;
        const local = d.localExplanation;
        let shapBars = local.features.map(f => {
            const width = Math.abs(f.shap) * 300;
            const color = f.direction === 'churn' ? 'var(--accent-rose)' : 'var(--accent-emerald)';
            const label = f.direction === 'churn' ? '→ Churn' : '→ Retain';
            return `
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
                <span style="width:180px;font-size:0.82rem;text-align:right;color:var(--text-secondary)">${f.name}</span>
                <div style="flex:1;display:flex;align-items:center;gap:6px">
                    <div style="height:20px;width:${width}px;background:${color};border-radius:4px;opacity:0.8;transition:width 1s ease"></div>
                    <span style="font-size:0.75rem;color:var(--text-muted)">${f.shap > 0 ? '+' : ''}${f.shap.toFixed(2)} ${label}</span>
                </div>
            </div>`;
        }).join('');

        return `
            <div class="charts-grid">
                <div class="chart-card animate-in animate-delay-1">
                    <div class="chart-header"><div><div class="chart-title">Global Feature Importance (SHAP)</div><div class="chart-subtitle">Mean absolute SHAP values across all predictions</div></div></div>
                    <div class="chart-container" style="height:320px"><canvas id="chart-shap-global"></canvas></div>
                </div>
                <div class="chart-card animate-in animate-delay-2">
                    <div class="chart-header">
                        <div><div class="chart-title">Local Explanation — ${local.customer}</div><div class="chart-subtitle">Individual prediction breakdown</div></div>
                        <span class="badge high">Churn Risk: ${(local.prediction * 100).toFixed(0)}%</span>
                    </div>
                    <div style="padding:12px 0">${shapBars}</div>
                </div>
            </div>`;
    },
};

// Chart initializers per page
const ChartInitializers = {
    overview() {
        const d = DashboardData.overview;
        createLineChart('chart-revenue', d.revenueByMonth.labels, [{
            label: 'Revenue', data: d.revenueByMonth.data, borderColor: '#10b981',
        }], { scales: { y: { ...getChartOptions().scales.y, ticks: { ...getChartOptions().scales.y.ticks, callback: v => '$' + (v / 1000) + 'K' } } } });
        createDoughnutChart('chart-segments', d.segmentDistribution.labels, d.segmentDistribution.data, d.segmentDistribution.colors);
    },
    churn() {
        const d = DashboardData.churn;
        createLineChart('chart-churn-trend', d.monthlyTrend.labels, [
            { label: 'Churned', data: d.monthlyTrend.churned, borderColor: '#f43f5e' },
            { label: 'Retained', data: d.monthlyTrend.retained, borderColor: '#10b981' },
        ], { plugins: { legend: { display: true } } });
        createDoughnutChart('chart-churn-dist', d.distribution.labels, d.distribution.data, d.distribution.colors);
        const segColors = d.bySegment.data.map(v => v > 0.4 ? '#f43f5e' : v > 0.2 ? '#f59e0b' : '#10b981');
        createBarChart('chart-churn-segment', d.bySegment.labels, [{ label: 'Churn Rate', data: d.bySegment.data, backgroundColor: segColors }],
            { scales: { y: { ...getChartOptions().scales.y, ticks: { ...getChartOptions().scales.y.ticks, callback: v => (v * 100) + '%' } } } });
        const driverColors = d.drivers.data.map((_, i) => `hsl(${220 + i * 20}, 70%, ${55 + i * 3}%)`);
        createHorizontalBarChart('chart-churn-drivers', d.drivers.labels, d.drivers.data, driverColors);
    },
    clv() {
        const d = DashboardData.clv;
        const distLabels = d.distribution.map((_, i) => '$' + (i * 500));
        createBarChart('chart-clv-dist', distLabels, [{ label: 'Customers', data: d.distribution, backgroundColor: '#3b82f6' }]);
        const segColors = ['#3b82f6', '#8b5cf6', '#f43f5e', '#10b981', '#64748b'];
        createBarChart('chart-clv-segment', d.bySegment.labels, [{ label: 'Avg CLV', data: d.bySegment.data, backgroundColor: segColors }],
            { scales: { y: { ...getChartOptions().scales.y, ticks: { ...getChartOptions().scales.y.ticks, callback: v => '$' + v } } } });
    },
    segmentation() {
        const d = DashboardData.segmentation;
        const colors = d.segments.map(s => s.color);
        const datasets = d.clusterData.clusters.map((c, i) => ({
            label: d.segments[i].name,
            data: c.x.map((x, j) => ({ x, y: c.y[j] })),
            backgroundColor: colors[i] + '90', pointRadius: 4, pointHoverRadius: 6,
        }));
        createScatterChart('chart-clusters', datasets, {
            plugins: { legend: { display: true } },
            scales: { x: { ...getChartOptions().scales.x, title: { display: true, text: 'Revenue Score', color: '#94a3b8' } },
                      y: { ...getChartOptions().scales.y, title: { display: true, text: 'Engagement Score', color: '#94a3b8' } } },
        });
        createDoughnutChart('chart-seg-dist', d.segments.map(s => s.name), d.segments.map(s => s.count), colors);
    },
    causal() {
        const d = DashboardData.causal;
        createBarChart('chart-did', d.didResults.labels, [
            { label: 'Treated', data: d.didResults.treated, backgroundColor: '#3b82f6' },
            { label: 'Control', data: d.didResults.control, backgroundColor: '#64748b' },
        ], { plugins: { legend: { display: true } }, scales: { y: { ...getChartOptions().scales.y, ticks: { ...getChartOptions().scales.y.ticks, callback: v => (v * 100) + '%' } } } });
        createDoughnutChart('chart-uplift', d.upliftSegments.labels, d.upliftSegments.data, d.upliftSegments.colors);
    },
    explainability() {
        const d = DashboardData.explainability;
        const colors = d.globalImportance.data.map((v, i) => `hsl(${220 + i * 15}, 70%, ${55 + i * 2}%)`);
        createHorizontalBarChart('chart-shap-global', d.globalImportance.labels, d.globalImportance.data, colors);
    },
};
