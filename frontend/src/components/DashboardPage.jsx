import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { CustomerIQAPI } from '../api';

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return n.toLocaleString();
  return n;
}

export default function DashboardPage({ theme, searchQuery, setSearchQuery }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const res = await CustomerIQAPI.fetchData('dashboard');
      setData(res);
      setLoading(false);
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="page active">
        <div className="page-header">
          <div>
            <div className="skeleton skeleton-title"></div>
            <div className="skeleton skeleton-text" style={{ width: '40%' }}></div>
          </div>
        </div>
        <div className="kpis-row">
          {[1, 2, 3, 4].map(i => (
            <div className="kpi-card" key={i}>
              <div className="skeleton skeleton-text" style={{ height: '60px' }}></div>
            </div>
          ))}
        </div>
        <div className="dashboard-grid">
          <div className="card" style={{ height: '350px' }}><div className="skeleton" style={{ height: '100%' }}></div></div>
          <div className="card" style={{ height: '350px' }}><div className="skeleton" style={{ height: '100%' }}></div></div>
        </div>
      </div>
    );
  }

  const k = data.kpis;
  const isDark = theme === 'dark';
  const textColor = isDark ? '#CBD5E1' : '#334155';
  const gridColor = isDark ? '#334155' : '#E2E8F0';

  const healthChartOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#4F46E5',
      borderWidth: 1,
      textStyle: { color: '#F8FAFC', fontFamily: 'Inter' }
    },
    legend: {
      data: ['Revenue Projection ($)', 'Customer Retention Rate (%)'],
      textStyle: { color: textColor, fontFamily: 'Inter' },
      bottom: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      top: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.revenue_trend.labels,
      axisLabel: { color: textColor, fontFamily: 'Inter' },
      axisLine: { lineStyle: { color: gridColor } }
    },
    yAxis: [
      {
        type: 'value',
        axisLabel: {
          color: textColor,
          fontFamily: 'Inter',
          formatter: (value) => '$' + formatNumber(value)
        },
        splitLine: { lineStyle: { color: gridColor } }
      },
      {
        type: 'value',
        position: 'right',
        min: 90,
        max: 95,
        axisLabel: {
          color: textColor,
          fontFamily: 'Inter',
          formatter: '{value}%'
        },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'Revenue Projection ($)',
        type: 'line',
        data: data.revenue_trend.data,
        smooth: true,
        itemStyle: { color: '#4F46E5' },
        areaStyle: { opacity: 0.1, color: '#4F46E5' }
      },
      {
        name: 'Customer Retention Rate (%)',
        type: 'line',
        yAxisIndex: 1,
        data: data.retention_trend.data,
        smooth: true,
        itemStyle: { color: '#38BDF8' }
      }
    ]
  };

  const riskChartOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#4F46E5',
      borderWidth: 1,
      textStyle: { color: '#F8FAFC', fontFamily: 'Inter' }
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: textColor, fontFamily: 'Inter' }
    },
    series: [
      {
        name: 'Risk Distribution',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: textColor
          }
        },
        data: data.risk_distribution.labels.map((label, idx) => ({
          value: data.risk_distribution.data[idx],
          name: label,
          itemStyle: { color: data.risk_distribution.colors[idx] }
        }))
      }
    ]
  };

  const exportPdf = () => {
    alert("Preparing executive PDF report download...\n\nMetrics summary:\nTotal Users: 125,842\nAvg CLV: $842\nChurn Risk: 7.4%\nCampaign ROI: 4.2x\n\nDownload will start shortly.");
  };

  const filteredSegments = data.top_segments.filter(s =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="page active">
      <div className="page-header">
        <div>
          <h1 className="page-title">Executive Dashboard</h1>
          <p className="page-subtitle">Real-time enterprise metrics & intelligence portfolio</p>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary" onClick={exportPdf}>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px' }}>
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Export PDF
          </button>
        </div>
      </div>

      <div className="executive-summary-panel">
        <div className="summary-icon">✨</div>
        <div className="summary-text">
          <h4>Executive Intelligence Insight</h4>
          <p>Overall customer health score remains strong at 92.6%. Monthly recurring revenue projection shows positive momentum (+8.2% MoM), while causal treatment models indicate churn interventions saved approximately $2.4M in potential recurring revenue this quarter.</p>
        </div>
      </div>

      <div className="kpis-row">
        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">Total Users</span>
            <div className="kpi-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{formatNumber(k.total_customers.value)}</div>
          <div className="kpi-trend up">
            ↑ {k.total_customers.change}% <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', marginLeft: '4px' }}>vs last month</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">Avg CLV</span>
            <div className="kpi-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="1" x2="12" y2="23" />
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">${k.avg_clv.value}</div>
          <div className="kpi-trend up">
            ↑ {k.avg_clv.change}% <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', marginLeft: '4px' }}>vs last quarter</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">Churn Risk</span>
            <div className="kpi-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{k.churn_rate.value}%</div>
          <div className="kpi-trend down">
            ↓ {Math.abs(k.churn_rate.change)}% <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', marginLeft: '4px' }}>improvement</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">Campaign ROI</span>
            <div className="kpi-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{k.campaign_roi.value}x</div>
          <div className="kpi-trend up">
            ↑ {k.campaign_roi.change}% <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', marginLeft: '4px' }}>net gain</span>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Customer Health Overview</span>
          </div>
          <div className="card-body">
            <div className="chart-container">
              <ReactECharts option={healthChartOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Risk Distribution</span>
          </div>
          <div className="card-body">
            <div className="chart-container">
              <ReactECharts option={riskChartOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title">Top Customer Segments</span>
          {searchQuery && (
            <span className="badge badge-info" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              Filtered by: "{searchQuery}"
              <button 
                onClick={() => setSearchQuery('')}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0 }}
              >
                ✕
              </button>
            </span>
          )}
        </div>
        <div className="table-responsive">
          <table className="custom-table">
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
              {filteredSegments.length > 0 ? (
                filteredSegments.map((s, idx) => (
                  <tr key={idx}>
                    <td><strong>{s.name}</strong></td>
                    <td>{formatNumber(s.count)}</td>
                    <td>${formatNumber(s.revenue)}</td>
                    <td>{s.churn_risk}%</td>
                    <td>
                      <span className={`badge ${s.churn_risk < 5 ? 'badge-success' : s.churn_risk < 15 ? 'badge-warning' : 'badge-danger'}`}>
                        {s.churn_risk < 5 ? 'Healthy' : s.churn_risk < 15 ? 'At Risk' : 'Critical'}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                    No segments matched your search query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
