import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { CustomerIQAPI } from '../api';

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return n.toLocaleString();
  return n;
}

export default function ChurnPage({ theme, searchQuery, setSearchQuery }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const res = await CustomerIQAPI.fetchData('churn');
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
        <div className="hero-stats">
          {[1, 2, 3].map(i => (
            <div className="hero-stat-card" key={i}>
              <div className="skeleton skeleton-text" style={{ height: '80px' }}></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const h = data.hero;
  const isDark = theme === 'dark';
  const textColor = isDark ? '#CBD5E1' : '#334155';
  const gridColor = isDark ? '#334155' : '#E2E8F0';

  // Heatmap helper for CSS color
  const getCellColor = (val) => {
    if (val > 80) return '#EF4444';
    if (val > 50) return '#F59E0B';
    if (val > 25) return '#4F46E5';
    if (val > 10) return '#38BDF8';
    return '#1E293B';
  };

  const trendChartOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#4F46E5',
      borderWidth: 1,
      textStyle: { color: '#F8FAFC', fontFamily: 'Inter' }
    },
    legend: {
      data: ['Churn Rate (%)', 'Customers Lost'],
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
      data: data.monthly_trend.labels,
      axisLabel: { color: textColor, fontFamily: 'Inter' },
      axisLine: { lineStyle: { color: gridColor } }
    },
    yAxis: [
      {
        type: 'value',
        axisLabel: {
          color: textColor,
          fontFamily: 'Inter',
          formatter: '{value}%'
        },
        splitLine: { lineStyle: { color: gridColor } }
      },
      {
        type: 'value',
        position: 'right',
        axisLabel: {
          color: textColor,
          fontFamily: 'Inter',
          formatter: (v) => formatNumber(v)
        },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'Churn Rate (%)',
        type: 'line',
        data: data.monthly_trend.churn_rate,
        smooth: true,
        itemStyle: { color: '#EF4444' }
      },
      {
        name: 'Customers Lost',
        type: 'line',
        yAxisIndex: 1,
        data: data.monthly_trend.customers_lost,
        smooth: true,
        itemStyle: { color: '#F59E0B' }
      }
    ]
  };

  const filteredFeatures = data.shap_features.filter(f =>
    f.feature.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="page active">
      <div className="page-header">
        <div>
          <h1 className="page-title">Churn Analytics</h1>
          <p className="page-subtitle">Predictive churn modeling & retention risk mitigation</p>
        </div>
      </div>

      <div className="hero-stats">
        <div className="hero-stat-card">
          <span className="hero-stat-label">Current Churn Rate</span>
          <span className="hero-stat-value" style={{ color: 'var(--color-danger)' }}>{h.current_churn_rate}%</span>
          <span className="hero-stat-subtext">Down 3.1% from last month</span>
        </div>
        <div className="hero-stat-card">
          <span className="hero-stat-label">Predicted Monthly Loss</span>
          <span className="hero-stat-value">${formatNumber(h.predicted_monthly_loss)}</span>
          <span className="hero-stat-subtext">Optimized from $54K baseline</span>
        </div>
        <div className="hero-stat-card">
          <span className="hero-stat-label">At-Risk Customers</span>
          <span className="hero-stat-value">{formatNumber(h.at_risk_customers)}</span>
          <span className="hero-stat-subtext">Flagged by XGBoost classifier</span>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Churn Risk Heatmap</span>
          </div>
          <div className="card-body">
            <div className="heatmap-grid">
              <div></div>
              {data.heatmap.risk_buckets.map((b, idx) => (
                <div key={idx} className="heatmap-col-header">{b}</div>
              ))}

              {data.heatmap.segments.map((seg, sIdx) => (
                <React.Fragment key={sIdx}>
                  <div className="heatmap-label">{seg}</div>
                  {data.heatmap.data[sIdx].map((val, vIdx) => (
                    <div
                      key={vIdx}
                      className="heatmap-cell"
                      style={{ backgroundColor: getCellColor(val) }}
                      title={`${seg}: ${val}% customers`}
                    >
                      {val}%
                    </div>
                  ))}
                </React.Fragment>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '16px', fontSize: '11px', color: 'var(--text-muted)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#1E293B', borderRadius: '2px' }}></span> Low Risk
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#38BDF8', borderRadius: '2px' }}></span> Moderate
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#4F46E5', borderRadius: '2px' }}></span> Elevated
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#F59E0B', borderRadius: '2px' }}></span> High Risk
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '12px', height: '12px', backgroundColor: '#EF4444', borderRadius: '2px' }}></span> Critical
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Top Churn Drivers (SHAP Importance)</span>
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
          <div className="card-body">
            <div className="shap-list">
              {filteredFeatures.length > 0 ? (
                filteredFeatures.map((f, idx) => {
                  const isPositive = f.direction === 'churn';
                  const color = isPositive ? 'var(--color-danger)' : 'var(--color-success)';
                  const width = Math.abs(f.impact * 100);
                  return (
                    <div className="shap-row" key={idx}>
                      <div className="shap-label" title={f.feature}>{f.feature}</div>
                      <div className="shap-bar-container">
                        <div className="shap-bar" style={{ width: `${width}%`, backgroundColor: color }}></div>
                      </div>
                      <div className="shap-value">{isPositive ? '+' : ''}{Math.round(f.impact * 100)}%</div>
                    </div>
                  );
                })
              ) : (
                <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No churn drivers matched your search query.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title">Monthly Churn Trend Analysis</span>
        </div>
        <div className="card-body">
          <div className="chart-container">
            <ReactECharts option={trendChartOption} style={{ height: '100%', width: '100%' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
