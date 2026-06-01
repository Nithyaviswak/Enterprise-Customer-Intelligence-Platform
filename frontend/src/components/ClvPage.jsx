import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { CustomerIQAPI } from '../api';

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return n.toLocaleString();
  return n;
}

export default function ClvPage({ theme, searchQuery, setSearchQuery }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const res = await CustomerIQAPI.fetchData('clv');
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
      </div>
    );
  }

  const k = data.kpis;
  const proj = data.projection;
  const isDark = theme === 'dark';
  const textColor = isDark ? '#CBD5E1' : '#334155';
  const gridColor = isDark ? '#334155' : '#E2E8F0';

  // Calculate stack details for confidence bands
  const lowerData = proj.lower;
  const diffData = proj.upper.map((uVal, idx) => {
    const lVal = lowerData[idx];
    if (uVal === null || lVal === null) return null;
    return uVal - lVal;
  });

  const projectionOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#4F46E5',
      borderWidth: 1,
      textStyle: { color: '#F8FAFC', fontFamily: 'Inter' },
      formatter: (params) => {
        let res = `<strong>${params[0].name}</strong><br/>`;
        params.forEach(p => {
          if (p.seriesName !== 'Confidence Band Lower' && p.seriesName !== 'Confidence Band Height' && p.value !== undefined && p.value !== null) {
            res += `${p.marker} ${p.seriesName}: $${formatNumber(p.value)}<br/>`;
          }
        });
        return res;
      }
    },
    legend: {
      data: ['Historical Revenue ($)', 'Forecast ($)', 'Confidence Range'],
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
      data: proj.labels,
      axisLabel: { color: textColor, fontFamily: 'Inter' },
      axisLine: { lineStyle: { color: gridColor } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: textColor,
        fontFamily: 'Inter',
        formatter: (v) => '$' + formatNumber(v)
      },
      splitLine: { lineStyle: { color: gridColor } }
    },
    series: [
      {
        name: 'Historical Revenue ($)',
        type: 'line',
        data: proj.actual,
        smooth: true,
        itemStyle: { color: '#4F46E5' },
        lineStyle: { width: 2 }
      },
      {
        name: 'Forecast ($)',
        type: 'line',
        data: proj.forecast,
        smooth: true,
        itemStyle: { color: '#38BDF8' },
        lineStyle: { width: 2, type: 'dashed' }
      },
      {
        name: 'Confidence Band Lower',
        type: 'line',
        data: lowerData,
        stack: 'confidence',
        lineStyle: { opacity: 0 },
        symbol: 'none'
      },
      {
        name: 'Confidence Band Height',
        type: 'line',
        data: diffData,
        stack: 'confidence',
        lineStyle: { opacity: 0 },
        symbol: 'none',
        areaStyle: { color: 'rgba(56, 189, 248, 0.15)' }
      }
    ]
  };

  const distOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#4F46E5',
      borderWidth: 1,
      textStyle: { color: '#F8FAFC', fontFamily: 'Inter' }
    },
    grid: {
      left: '3%',
      right: '4%',
      top: '10%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.distribution.labels,
      axisLabel: { color: textColor, fontFamily: 'Inter' },
      axisLine: { lineStyle: { color: gridColor } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: textColor,
        fontFamily: 'Inter',
        formatter: (v) => formatNumber(v)
      },
      splitLine: { lineStyle: { color: gridColor } }
    },
    series: [
      {
        name: 'Customers Count',
        type: 'bar',
        data: data.distribution.counts,
        itemStyle: { color: '#4F46E5', borderRadius: [4, 4, 0, 0] }
      }
    ]
  };

  return (
    <div className="page active">
      <div className="page-header">
        <div>
          <h1 className="page-title">CLV Forecasting</h1>
          <p className="page-subtitle">Predictive CLV forecasting and customer value distribution histogram</p>
        </div>
      </div>

      <div className="kpis-row">
        <div className="kpi-card">
          <div className="kpi-header"><span className="kpi-label">Average CLV</span></div>
          <div className="kpi-value">${k.avg_clv.value}</div>
          <div className="kpi-trend up">
            ↑ {k.avg_clv.change}% <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', marginLeft: '4px' }}>MoM</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header"><span className="kpi-label">Total Projected Value</span></div>
          <div className="kpi-value">${formatNumber(k.total_ltv.value)}</div>
          <div className="kpi-trend up">
            ↑ {k.total_ltv.change}% <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', marginLeft: '4px' }}>YoY</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header"><span className="kpi-label">High-Value Ratio</span></div>
          <div className="kpi-value">{k.high_value_pct.value}%</div>
          <div className="kpi-trend up">
            ↑ {k.high_value_pct.change}% <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', marginLeft: '4px' }}>vs benchmark</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header"><span className="kpi-label">CAC Payback Time</span></div>
          <div className="kpi-value">{k.payback_months.value} mo</div>
          <div className="kpi-trend down">
            ↓ {Math.abs(k.payback_months.change)} mo <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', marginLeft: '4px' }}>improved</span>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">12-Month Revenue Projection & Forecast Confidence Bands</span>
          </div>
          <div className="card-body">
            <div className="chart-container">
              <ReactECharts option={projectionOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Customer Value Distribution (CLV Histogram)</span>
          </div>
          <div className="card-body">
            <div className="chart-container">
              <ReactECharts option={distOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
