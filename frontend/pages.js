/**
 * CustomerIQ - Page Renderers & Content Handlers
 */

function formatNumber(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return n.toLocaleString();
    return n;
}

const PageRenderers = {
    async dashboard() {
        const data = await window.CustomerIQAPI.fetchData('dashboard');
        const k = data.kpis;
        
        return `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Executive Dashboard</h1>
                    <p class="page-subtitle">Real-time enterprise metrics & intelligence portfolio</p>
                </div>
                <div class="page-actions">
                    <button class="btn btn-secondary" onclick="window.exportDashboard()"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Export PDF</button>
                </div>
            </div>

            <!-- Executive Summary Panel -->
            <div class="executive-summary-panel">
                <div class="summary-icon">✨</div>
                <div class="summary-text">
                    <h4>Executive Intelligence Insight</h4>
                    <p>Overall customer health score remains strong at 92.6%. Monthly recurring revenue projection shows positive momentum (+8.2% MoM), while causal treatment models indicate churn interventions saved approximately $2.4M in potential recurring revenue this quarter.</p>
                </div>
            </div>

            <!-- KPI Row -->
            <div class="kpis-row">
                <div class="kpi-card">
                    <div class="kpi-header">
                        <span class="kpi-label">Total Users</span>
                        <div class="kpi-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></div>
                    </div>
                    <div class="kpi-value">${formatNumber(k.total_customers.value)}</div>
                    <div class="kpi-trend up">↑ ${k.total_customers.change}% <span style="color:var(--text-muted);font-weight:normal">vs last month</span></div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-header">
                        <span class="kpi-label">Avg CLV</span>
                        <div class="kpi-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
                    </div>
                    <div class="kpi-value">$${k.avg_clv.value}</div>
                    <div class="kpi-trend up">↑ ${k.avg_clv.change}% <span style="color:var(--text-muted);font-weight:normal">vs last quarter</span></div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-header">
                        <span class="kpi-label">Churn Risk</span>
                        <div class="kpi-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
                    </div>
                    <div class="kpi-value">${k.churn_rate.value}%</div>
                    <div class="kpi-trend down">↓ ${Math.abs(k.churn_rate.change)}% <span style="color:var(--text-muted);font-weight:normal">improvement</span></div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-header">
                        <span class="kpi-label">Campaign ROI</span>
                        <div class="kpi-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
                    </div>
                    <div class="kpi-value">${k.campaign_roi.value}x</div>
                    <div class="kpi-trend up">↑ ${k.campaign_roi.change}% <span style="color:var(--text-muted);font-weight:normal">net gain</span></div>
                </div>
            </div>

            <!-- Health Overview -->
            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Customer Health Overview</span>
                    </div>
                    <div class="card-body">
                        <div class="chart-container"><canvas id="health-overview-chart"></canvas></div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Risk Distribution</span>
                    </div>
                    <div class="card-body">
                        <div class="chart-container"><canvas id="risk-donut-chart"></canvas></div>
                    </div>
                </div>
            </div>

            <!-- Segments List -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Top Customer Segments</span>
                </div>
                <div class="table-responsive">
                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th>Segment Name</th>
                                <th>Customer Count</th>
                                <th>Revenue Contribution</th>
                                <th>Avg Churn Risk</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.top_segments.map(s => `
                                <tr>
                                    <td><strong>${s.name}</strong></td>
                                    <td>${formatNumber(s.count)}</td>
                                    <td>$${formatNumber(s.revenue)}</td>
                                    <td>${s.churn_risk}%</td>
                                    <td><span class="badge ${s.churn_risk < 5 ? 'badge-success' : s.churn_risk < 15 ? 'badge-warning' : 'badge-danger'}">${s.churn_risk < 5 ? 'Healthy' : s.churn_risk < 15 ? 'At Risk' : 'Critical'}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    async churn() {
        const data = await window.CustomerIQAPI.fetchData('churn');
        const h = data.hero;

        // Generate heatmap HTML
        let heatmapHTML = `<div class="heatmap-grid">
            <div></div> <!-- Spacer -->
            ${data.heatmap.risk_buckets.map(b => `<div class="heatmap-col-header">${b}</div>`).join('')}
        `;

        data.heatmap.segments.forEach((seg, sIdx) => {
            heatmapHTML += `<div class="heatmap-label">${seg}</div>`;
            data.heatmap.data[sIdx].forEach(val => {
                // Color scale based on percentage values
                let bg;
                if (val > 80) bg = '#EF4444';
                else if (val > 50) bg = '#F59E0B';
                else if (val > 25) bg = '#4F46E5';
                else if (val > 10) bg = '#38BDF8';
                else bg = '#1E293B';

                heatmapHTML += `<div class="heatmap-cell" style="background:${bg}" title="${seg}: ${val}% customers">${val}%</div>`;
            });
        });
        heatmapHTML += '</div>';

        return `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Churn Analytics</h1>
                    <p class="page-subtitle">Predictive churn modeling & retention risk mitigation</p>
                </div>
            </div>

            <!-- Hero Section -->
            <div class="hero-stats">
                <div class="hero-stat-card">
                    <span class="hero-stat-label">Current Churn Rate</span>
                    <span class="hero-stat-value" style="color:var(--color-danger)">${h.current_churn_rate}%</span>
                    <span class="hero-stat-subtext">Down 3.1% from last month</span>
                </div>
                <div class="hero-stat-card">
                    <span class="hero-stat-label">Predicted Monthly Loss</span>
                    <span class="hero-stat-value">$${formatNumber(h.predicted_monthly_loss)}</span>
                    <span class="hero-stat-subtext">Optimized from $54K baseline</span>
                </div>
                <div class="hero-stat-card">
                    <span class="hero-stat-label">At-Risk Customers</span>
                    <span class="hero-stat-value">${formatNumber(h.at_risk_customers)}</span>
                    <span class="hero-stat-subtext">Flagged by XGBoost classifier</span>
                </div>
            </div>

            <!-- Heatmap and Chart Grid -->
            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Churn Risk Heatmap</span>
                    </div>
                    <div class="card-body">
                        ${heatmapHTML}
                        <div style="display:flex;justify-content:center;gap:16px;margin-top:16px;font-size:11px;color:var(--text-muted)">
                            <div style="display:flex;align-items:center;gap:4px"><span style="width:12px;height:12px;background:#1E293B;border-radius:2px"></span> Low Risk</div>
                            <div style="display:flex;align-items:center;gap:4px"><span style="width:12px;height:12px;background:#38BDF8;border-radius:2px"></span> Moderate</div>
                            <div style="display:flex;align-items:center;gap:4px"><span style="width:12px;height:12px;background:#4F46E5;border-radius:2px"></span> elevated</div>
                            <div style="display:flex;align-items:center;gap:4px"><span style="width:12px;height:12px;background:#F59E0B;border-radius:2px"></span> High Risk</div>
                            <div style="display:flex;align-items:center;gap:4px"><span style="width:12px;height:12px;background:#EF4444;border-radius:2px"></span> Critical</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Top Churn Drivers (SHAP Importance)</span>
                    </div>
                    <div class="card-body">
                        <div class="shap-list">
                            ${data.shap_features.map(f => {
                                const isPositive = f.direction === 'churn';
                                const color = isPositive ? 'var(--color-danger)' : 'var(--color-success)';
                                const width = Math.abs(f.impact * 100);
                                return `
                                    <div class="shap-row">
                                        <div class="shap-label" title="${f.feature}">${f.feature}</div>
                                        <div class="shap-bar-container">
                                            <div class="shap-bar" style="width:${width}%;background:${color}"></div>
                                        </div>
                                        <div class="shap-value">${isPositive ? '+' : ''}${Math.round(f.impact * 100)}%</div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Churn Trend Chart -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Monthly Churn Trend Analysis</span>
                </div>
                <div class="card-body">
                    <div class="chart-container"><canvas id="churn-trend-chart"></canvas></div>
                </div>
            </div>
        `;
    },

    async segmentation() {
        const data = await window.CustomerIQAPI.fetchData('segmentation');
        
        return `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Customer Segmentation</h1>
                    <p class="page-subtitle">Interactive behavioral clustering & K-Means persona insights</p>
                </div>
            </div>

            <!-- Segment Cards Row -->
            <div class="segment-cards-row">
                ${data.segments.map(s => `
                    <div class="segment-card">
                        <div class="segment-card-border" style="background:${s.color}"></div>
                        <div class="segment-name" style="color:${s.color}">${s.name}</div>
                        <div class="segment-stat">
                            <span class="segment-stat-label">Customers</span>
                            <span class="segment-stat-value">${formatNumber(s.count)}</span>
                        </div>
                        <div class="segment-stat">
                            <span class="segment-stat-label">Avg CLV</span>
                            <span class="segment-stat-value">$${s.avg_clv}</span>
                        </div>
                        <div class="segment-stat">
                            <span class="segment-stat-label">Churn Rate</span>
                            <span class="segment-stat-value" style="color:${s.churn_pct > 15 ? 'var(--color-danger)' : 'var(--color-success)'}">${s.churn_pct}%</span>
                        </div>
                    </div>
                `).join('')}
            </div>

            <!-- 2D UMAP Visualisation -->
            <div class="dashboard-grid" style="grid-template-columns: 2fr 1fr">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">2D UMAP Behavioral Projection (K-Means)</span>
                    </div>
                    <div class="card-body">
                        <div class="chart-container" style="height:350px"><canvas id="umap-scatter-chart"></canvas></div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Cluster Explanations & Size</span>
                    </div>
                    <div class="card-body">
                        <div class="chart-container" style="height:350px"><canvas id="segment-pie-chart"></canvas></div>
                    </div>
                </div>
            </div>
        `;
    },

    async clv() {
        const data = await window.CustomerIQAPI.fetchData('clv');
        const k = data.kpis;

        return `
            <div class="page-header">
                <div>
                    <h1 class="page-title">CLV Forecasting</h1>
                    <p class="page-subtitle">Predictive CLV forecasting and customer value distribution histogram</p>
                </div>
            </div>

            <!-- Stats -->
            <div class="kpis-row">
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-label">Average CLV</span></div>
                    <div class="kpi-value">$${k.avg_clv.value}</div>
                    <div class="kpi-trend up">↑ ${k.avg_clv.change}% <span style="color:var(--text-muted);font-weight:normal">MoM</span></div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-label">Total Projected Value</span></div>
                    <div class="kpi-value">$${formatNumber(k.total_ltv.value)}</div>
                    <div class="kpi-trend up">↑ ${k.total_ltv.change}% <span style="color:var(--text-muted);font-weight:normal">YoY</span></div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-label">High-Value Ratio</span></div>
                    <div class="kpi-value">${k.high_value_pct.value}%</div>
                    <div class="kpi-trend up">↑ ${k.high_value_pct.change}% <span style="color:var(--text-muted);font-weight:normal">vs benchmark</span></div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-label">CAC Payback Time</span></div>
                    <div class="kpi-value">${k.payback_months.value} mo</div>
                    <div class="kpi-trend down">↓ ${Math.abs(k.payback_months.change)} mo <span style="color:var(--text-muted);font-weight:normal">improved</span></div>
                </div>
            </div>

            <!-- Projection Graph & Distribution Hist -->
            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">12-Month Revenue Projection & Forecast Confidence Bands</span>
                    </div>
                    <div class="card-body">
                        <div class="chart-container"><canvas id="clv-projection-chart"></canvas></div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Customer Value Distribution (CLV Histogram)</span>
                    </div>
                    <div class="card-body">
                        <div class="chart-container"><canvas id="clv-dist-chart"></canvas></div>
                    </div>
                </div>
            </div>
        `;
    },

    async causal() {
        const data = await window.CustomerIQAPI.fetchData('causal');
        const tc = data.treatment_control;
        const eff = data.effects;

        return `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Causal Impact Analysis</h1>
                    <p class="page-subtitle">Propensity score matching & Difference-in-Differences statistical evaluation</p>
                </div>
            </div>

            <!-- Treatment and Control Card side-by-side -->
            <div class="grid-2col">
                <div class="card" style="border-top: 4px solid var(--color-primary)">
                    <div class="card-header">
                        <span class="card-title">Treatment Group (Campaign Recipients)</span>
                        <span class="badge badge-primary">Sample Size: ${formatNumber(tc.treatment.size)}</span>
                    </div>
                    <div class="card-body">
                        <div style="display:flex;justify-content:space-around;text-align:center">
                            <div>
                                <span style="font-size:12px;color:var(--text-muted)">Churn Rate</span>
                                <div style="font-size:32px;font-weight:700;color:var(--color-danger)">${tc.treatment.churn_rate}%</div>
                            </div>
                            <div>
                                <span style="font-size:12px;color:var(--text-muted)">Avg CLV Contribution</span>
                                <div style="font-size:32px;font-weight:700;color:var(--color-success)">$${tc.treatment.avg_clv}</div>
                            </div>
                            <div>
                                <span style="font-size:12px;color:var(--text-muted)">Retention Score</span>
                                <div style="font-size:32px;font-weight:700;color:var(--color-primary-hover)">${tc.treatment.retention}%</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card" style="border-top: 4px solid var(--text-muted)">
                    <div class="card-header">
                        <span class="card-title">Control Group (Campaign Holdout)</span>
                        <span class="badge" style="background-color:rgba(148,163,184,0.1);color:var(--text-muted)">Sample Size: ${formatNumber(tc.control.size)}</span>
                    </div>
                    <div class="card-body">
                        <div style="display:flex;justify-content:space-around;text-align:center">
                            <div>
                                <span style="font-size:12px;color:var(--text-muted)">Churn Rate</span>
                                <div style="font-size:32px;font-weight:700;color:var(--text-muted)">${tc.control.churn_rate}%</div>
                            </div>
                            <div>
                                <span style="font-size:12px;color:var(--text-muted)">Avg CLV Contribution</span>
                                <div style="font-size:32px;font-weight:700;color:var(--text-muted)">$${tc.control.avg_clv}</div>
                            </div>
                            <div>
                                <span style="font-size:12px;color:var(--text-muted)">Retention Score</span>
                                <div style="font-size:32px;font-weight:700;color:var(--text-muted)">${tc.control.retention}%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- DiD and Uplift Plots -->
            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Difference-in-Differences Campaign Plot</span>
                    </div>
                    <div class="card-body">
                        <div class="chart-container"><canvas id="did-line-chart"></canvas></div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Uplift Target Segmentation</span>
                    </div>
                    <div class="card-body">
                        <div class="chart-container"><canvas id="uplift-donut-chart"></canvas></div>
                    </div>
                </div>
            </div>

            <!-- Statistical details row -->
            <div class="grid-3col">
                <div class="card">
                    <div class="card-header"><span class="card-title">Average Treatment Effect (ATE)</span></div>
                    <div class="card-body" style="text-align:center">
                        <div style="font-size:36px;font-weight:700;color:var(--color-danger)">${eff.ate.value}%</div>
                        <span style="font-size:12px;color:var(--text-muted)">Confidence Interval: [${eff.ate.ci_lower}%, ${eff.ate.ci_upper}%]</span>
                        <div style="margin-top:8px;font-size:11px;font-weight:600;color:var(--color-success)">Statistically Significant (p = ${eff.ate.p_value})</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><span class="card-title">Treatment on Treated (ATT)</span></div>
                    <div class="card-body" style="text-align:center">
                        <div style="font-size:36px;font-weight:700;color:var(--color-danger)">${eff.att.value}%</div>
                        <span style="font-size:12px;color:var(--text-muted)">Confidence Interval: [${eff.att.ci_lower}%, ${eff.att.ci_upper}%]</span>
                        <div style="margin-top:8px;font-size:11px;font-weight:600;color:var(--color-success)">Statistically Significant (p = ${eff.att.p_value})</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><span class="card-title">Campaign Uplift Lift</span></div>
                    <div class="card-body" style="text-align:center">
                        <div style="font-size:36px;font-weight:700;color:var(--color-success)">+${eff.uplift.value}%</div>
                        <span style="font-size:12px;color:var(--text-muted)">Confidence Interval: [${eff.uplift.ci_lower}%, ${eff.uplift.ci_upper}%]</span>
                        <div style="margin-top:8px;font-size:11px;font-weight:600;color:var(--color-success)">Statistically Significant (p = ${eff.uplift.p_value})</div>
                    </div>
                </div>
            </div>
        `;
    },

    async recommendations() {
        const data = await window.CustomerIQAPI.fetchData('recommendations');
        
        return `
            <div class="page-header">
                <div>
                    <h1 class="page-title">AI recommendations & Interventions</h1>
                    <p class="page-subtitle">Priority target groups for customer churn mitigation campaigns</p>
                </div>
            </div>

            <!-- Priority Matrix and Overview Summary -->
            <div class="dashboard-grid" style="grid-template-columns: 1fr 1fr">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Recommendation Matrix (Priority quadrants)</span>
                    </div>
                    <div class="card-body">
                        <div class="matrix-grid">
                            ${data.priority_matrix.quadrants.map(q => `
                                <div class="matrix-quadrant" style="border-color:${q.color}">
                                    <div>
                                        <div class="quadrant-label" style="color:${q.color}">${q.label}</div>
                                        <div class="quadrant-desc">${q.description}</div>
                                    </div>
                                    <div class="quadrant-count">${formatNumber(q.count)}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Active AI Decision Engine Summary</span>
                    </div>
                    <div class="card-body" style="display:flex;flex-direction:column;justify-content:space-between;height:100%">
                        <div style="font-size:14px;line-height:1.6;color:var(--text-secondary)">
                            ${data.summary}
                        </div>
                        <div style="margin-top:20px;padding:16px;background-color:rgba(79, 70, 229, 0.05);border:1px solid rgba(79, 70, 229, 0.2);border-radius:var(--radius-md)">
                            <div style="display:flex;justify-content:space-between;align-items:center">
                                <div>
                                    <div style="font-size:12px;color:var(--text-muted)">Expected ROI</div>
                                    <div style="font-size:24px;font-weight:700;color:var(--color-success)">4.2x</div>
                                </div>
                                <div>
                                    <div style="font-size:12px;color:var(--text-muted)">Investments</div>
                                    <div style="font-size:24px;font-weight:700;color:var(--text-primary)">$340,000</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recommendation Feed Cards -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Active Action Recommendation Feed</span>
                </div>
                <div class="card-body" style="display:flex;flex-direction:column;gap:16px">
                    <div class="rec-cards-list">
                        ${data.cards.map(c => `
                            <div class="rec-card priority-${c.priority}">
                                <div class="rec-header">
                                    <span class="rec-segment">${c.segment}</span>
                                    <span class="badge ${c.priority === 'critical' ? 'badge-danger' : c.priority === 'high' ? 'badge-warning' : 'badge-primary'}">${c.priority.toUpperCase()} PRIORITY</span>
                                </div>
                                <div class="rec-body">
                                    <div>
                                        <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;margin-bottom:4px">Target Action Recommendation</div>
                                        <div style="font-size:15px;font-weight:600;color:var(--text-primary)">${c.recommendation}</div>
                                    </div>
                                    <div class="rec-stats">
                                        <div class="rec-stat">
                                            <span class="rec-stat-label">Segment Size</span>
                                            <span class="rec-stat-value">${formatNumber(c.customer_count)} users</span>
                                        </div>
                                        <div class="rec-stat">
                                            <span class="rec-stat-label">Churn Risk</span>
                                            <span class="rec-stat-value" style="color:var(--color-danger)">${c.predicted_churn}%</span>
                                        </div>
                                        <div class="rec-stat">
                                            <span class="rec-stat-label">Expected Lift</span>
                                            <span class="rec-stat-value" style="color:var(--color-success)">+${c.expected_lift}%</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="rec-footer">
                                    <span style="font-size:12px;color:var(--text-muted)">Estimated Potential Recoverable Revenue: <strong style="color:var(--text-primary)">$${formatNumber(c.estimated_revenue_saved)}</strong></span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
};

// Initializers for charts
const ChartInitializers = {
    async dashboard() {
        const data = await window.CustomerIQAPI.fetchData('dashboard');
        
        // Health Overview Line chart
        const ctxOverview = document.getElementById('health-overview-chart');
        if (ctxOverview) {
            createChart('health-overview-chart', {
                type: 'line',
                data: {
                    labels: data.revenue_trend.labels,
                    datasets: [
                        {
                            label: 'Revenue Projection ($)',
                            data: data.revenue_trend.data,
                            borderColor: ChartColors.primary,
                            backgroundColor: 'rgba(79, 70, 229, 0.05)',
                            fill: true,
                            tension: 0.4,
                            borderWidth: 2,
                        },
                        {
                            label: 'Customer Retention Rate (%)',
                            data: data.retention_trend.data,
                            borderColor: ChartColors.accent,
                            backgroundColor: 'transparent',
                            yAxisID: 'y1',
                            tension: 0.4,
                            borderWidth: 2,
                        }
                    ]
                },
                options: getChartOptions({
                    scales: {
                        y: {
                            grid: { color: getThemeGridColor() },
                            ticks: {
                                color: getThemeTextColor(),
                                callback: v => '$' + formatNumber(v)
                            }
                        },
                        y1: {
                            position: 'right',
                            grid: { drawOnChartArea: false },
                            ticks: {
                                color: getThemeTextColor(),
                                callback: v => v + '%'
                            }
                        }
                    }
                })
            });
        }

        // Donut Chart for risk
        const ctxDonut = document.getElementById('risk-donut-chart');
        if (ctxDonut) {
            createChart('risk-donut-chart', {
                type: 'doughnut',
                data: {
                    labels: data.risk_distribution.labels,
                    datasets: [{
                        data: data.risk_distribution.data,
                        backgroundColor: data.risk_distribution.colors,
                        borderWidth: 2,
                        borderColor: getThemeGridColor()
                    }]
                },
                options: getChartOptions({
                    plugins: {
                        legend: { display: true, position: 'right' }
                    }
                })
            });
        }
    },

    async churn() {
        const data = await window.CustomerIQAPI.fetchData('churn');
        const ctxChurn = document.getElementById('churn-trend-chart');
        if (ctxChurn) {
            createChart('churn-trend-chart', {
                type: 'line',
                data: {
                    labels: data.monthly_trend.labels,
                    datasets: [
                        {
                            label: 'Churn Rate (%)',
                            data: data.monthly_trend.churn_rate,
                            borderColor: ChartColors.danger,
                            backgroundColor: 'transparent',
                            tension: 0.4,
                            borderWidth: 2
                        },
                        {
                            label: 'Customers Lost',
                            data: data.monthly_trend.customers_lost,
                            borderColor: ChartColors.warning,
                            backgroundColor: 'transparent',
                            yAxisID: 'y1',
                            tension: 0.4,
                            borderWidth: 2
                        }
                    ]
                },
                options: getChartOptions({
                    scales: {
                        y: {
                            ticks: { callback: v => v + '%' }
                        },
                        y1: {
                            position: 'right',
                            grid: { drawOnChartArea: false },
                            ticks: { callback: v => formatNumber(v) }
                        }
                    }
                })
            });
        }
    },

    async segmentation() {
        const data = await window.CustomerIQAPI.fetchData('segmentation');
        
        // Scatter plot representation
        const ctxScatter = document.getElementById('umap-scatter-chart');
        if (ctxScatter) {
            const datasets = Object.keys(data.clusters).map(name => {
                const segInfo = data.segments.find(s => s.name === name);
                const points = data.clusters[name].x.map((xVal, i) => ({
                    x: xVal,
                    y: data.clusters[name].y[i]
                }));
                return {
                    label: name,
                    data: points,
                    backgroundColor: segInfo ? segInfo.color : '#FFFFFF',
                    pointRadius: 6,
                    pointHoverRadius: 8
                };
            });

            createChart('umap-scatter-chart', {
                type: 'scatter',
                data: { datasets },
                options: getChartOptions({
                    plugins: {
                        legend: { display: true, position: 'top' }
                    },
                    scales: {
                        x: { title: { display: true, text: 'Feature Dim 1 (Revenue Factor)', color: getThemeTextColor() } },
                        y: { title: { display: true, text: 'Feature Dim 2 (Engagement Factor)', color: getThemeTextColor() } }
                    }
                })
            });
        }

        // Pie chart for sizes
        const ctxPie = document.getElementById('segment-pie-chart');
        if (ctxPie) {
            createChart('segment-pie-chart', {
                type: 'pie',
                data: {
                    labels: data.segments.map(s => s.name),
                    datasets: [{
                        data: data.segments.map(s => s.count),
                        backgroundColor: data.segments.map(s => s.color),
                        borderColor: getThemeGridColor(),
                        borderWidth: 1
                    }]
                },
                options: getChartOptions({
                    plugins: {
                        legend: { display: true, position: 'right' }
                    }
                })
            });
        }
    },

    async clv() {
        const data = await window.CustomerIQAPI.fetchData('clv');
        const proj = data.projection;

        // Line projection chart
        const ctxProj = document.getElementById('clv-projection-chart');
        if (ctxProj) {
            createChart('clv-projection-chart', {
                type: 'line',
                data: {
                    labels: proj.labels,
                    datasets: [
                        {
                            label: 'Historical Revenue ($)',
                            data: proj.actual,
                            borderColor: ChartColors.primary,
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            tension: 0.3
                        },
                        {
                            label: 'Forecast ($)',
                            data: proj.forecast,
                            borderColor: ChartColors.accent,
                            borderDash: [5, 5],
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            tension: 0.3
                        },
                        {
                            label: 'Confidence Interval (Upper)',
                            data: proj.upper,
                            borderColor: 'transparent',
                            backgroundColor: 'rgba(56, 189, 248, 0.1)',
                            fill: '+1', // Fill to next dataset (lower)
                            tension: 0.3,
                            pointRadius: 0
                        },
                        {
                            label: 'Confidence Interval (Lower)',
                            data: proj.lower,
                            borderColor: 'transparent',
                            backgroundColor: 'rgba(56, 189, 248, 0.1)',
                            fill: '-1',
                            tension: 0.3,
                            pointRadius: 0
                        }
                    ]
                },
                options: getChartOptions({
                    plugins: {
                        legend: { display: true }
                    },
                    scales: {
                        y: { ticks: { callback: v => '$' + formatNumber(v) } }
                    }
                })
            });
        }

        // CLV histogram distribution
        const ctxDist = document.getElementById('clv-dist-chart');
        if (ctxDist) {
            createChart('clv-dist-chart', {
                type: 'bar',
                data: {
                    labels: data.distribution.labels,
                    datasets: [{
                        label: 'Customers Count',
                        data: data.distribution.counts,
                        backgroundColor: ChartColors.primary,
                        borderRadius: 4
                    }]
                },
                options: getChartOptions({
                    scales: {
                        y: { ticks: { callback: v => formatNumber(v) } }
                    }
                })
            });
        }
    },

    async causal() {
        const data = await window.CustomerIQAPI.fetchData('causal');
        const did = data.did_plot;

        // DiD Plot using lines
        const ctxDid = document.getElementById('did-line-chart');
        if (ctxDid) {
            createChart('did-line-chart', {
                type: 'line',
                data: {
                    labels: did.labels,
                    datasets: [
                        {
                            label: 'Treatment Group (Campaign)',
                            data: did.treatment,
                            borderColor: ChartColors.primary,
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            tension: 0.3
                        },
                        {
                            label: 'Control Group (Holdout)',
                            data: did.control,
                            borderColor: ChartColors.textMuted,
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            tension: 0.3
                        }
                    ]
                },
                options: getChartOptions({
                    plugins: {
                        legend: { display: true }
                    },
                    scales: {
                        y: { ticks: { callback: v => v + '%' } }
                    }
                })
            });
        }

        // Uplift target donut
        const ctxUplift = document.getElementById('uplift-donut-chart');
        if (ctxUplift) {
            createChart('uplift-donut-chart', {
                type: 'doughnut',
                data: {
                    labels: data.uplift_segments.labels,
                    datasets: [{
                        data: data.uplift_segments.counts,
                        backgroundColor: data.uplift_segments.colors,
                        borderWidth: 2,
                        borderColor: getThemeGridColor()
                    }]
                },
                options: getChartOptions({
                    plugins: {
                        legend: { display: true, position: 'right' }
                    }
                })
            });
        }
    }
};
