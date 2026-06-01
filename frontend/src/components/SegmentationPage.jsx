import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { CustomerIQAPI } from '../api';

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return n.toLocaleString();
  return n;
}

export default function SegmentationPage({ theme, searchQuery, setSearchQuery }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const res = await CustomerIQAPI.fetchData('segmentation');
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
        <div className="segment-cards-row">
          {[1, 2, 3, 4, 5].map(i => (
            <div className="segment-card" key={i}>
              <div className="skeleton skeleton-text" style={{ height: '100px' }}></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const isDark = theme === 'dark';
  const textColor = isDark ? '#CBD5E1' : '#334155';
  const gridColor = isDark ? '#334155' : '#E2E8F0';

  // Scatter plot
  const scatterSeries = Object.keys(data.clusters).map(name => {
    const segInfo = data.segments.find(s => s.name === name);
    const points = data.clusters[name].x.map((xVal, i) => [
      xVal,
      data.clusters[name].y[i]
    ]);
    return {
      name: name,
      type: 'scatter',
      data: points,
      itemStyle: { color: segInfo ? segInfo.color : '#FFFFFF' },
      symbolSize: 12
    };
  });

  const scatterOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        return `<strong>${params.seriesName}</strong><br/>Dim 1: ${params.value[0]}<br/>Dim 2: ${params.value[1]}`;
      },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#4F46E5',
      borderWidth: 1,
      textStyle: { color: '#F8FAFC', fontFamily: 'Inter' }
    },
    legend: {
      data: Object.keys(data.clusters),
      textStyle: { color: textColor, fontFamily: 'Inter' },
      top: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      top: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'Revenue Factor',
      nameLocation: 'middle',
      nameGap: 25,
      nameTextStyle: { color: textColor, fontFamily: 'Inter' },
      axisLabel: { color: textColor, fontFamily: 'Inter' },
      splitLine: { lineStyle: { color: gridColor } }
    },
    yAxis: {
      type: 'value',
      name: 'Engagement Factor',
      nameLocation: 'middle',
      nameGap: 30,
      nameTextStyle: { color: textColor, fontFamily: 'Inter' },
      axisLabel: { color: textColor, fontFamily: 'Inter' },
      splitLine: { lineStyle: { color: gridColor } }
    },
    series: scatterSeries
  };

  const pieOption = {
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
      right: '0%',
      top: 'center',
      textStyle: { color: textColor, fontFamily: 'Inter' }
    },
    series: [
      {
        name: 'Cluster Size',
        type: 'pie',
        radius: '70%',
        center: ['40%', '50%'],
        data: data.segments.map(s => ({
          value: s.count,
          name: s.name,
          itemStyle: { color: s.color }
        })),
        label: { show: false }
      }
    ]
  };

  const filteredSegments = data.segments.filter(s =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="page active">
      <div className="page-header">
        <div>
          <h1 className="page-title">Customer Segmentation</h1>
          <p className="page-subtitle">Interactive behavioral clustering & K-Means persona insights</p>
        </div>
        {searchQuery && (
          <span className="badge badge-info" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginTop: '8px' }}>
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

      <div className="segment-cards-row">
        {filteredSegments.length > 0 ? (
          filteredSegments.map((s, idx) => (
            <div className="segment-card" key={idx}>
              <div className="segment-card-border" style={{ backgroundColor: s.color }}></div>
              <div className="segment-name" style={{ color: s.color }}>{s.name}</div>
              <div className="segment-stat">
                <span className="segment-stat-label">Customers</span>
                <span className="segment-stat-value">{formatNumber(s.count)}</span>
              </div>
              <div className="segment-stat">
                <span className="segment-stat-label">Avg CLV</span>
                <span className="segment-stat-value">${s.avg_clv}</span>
              </div>
              <div className="segment-stat">
                <span className="segment-stat-label">Churn Rate</span>
                <span className="segment-stat-value" style={{ color: s.churn_pct > 15 ? 'var(--color-danger)' : 'var(--color-success)' }}>
                  {s.churn_pct}%
                </span>
              </div>
            </div>
          ))
        ) : (
          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', color: 'var(--text-muted)' }}>
            No segments matched your search query.
          </div>
        )}
      </div>

      <div className="dashboard-grid" style={{ gridTemplateColumns: '2fr 1fr' }}>
        <div className="card">
          <div className="card-header">
            <span className="card-title">2D UMAP Behavioral Projection (K-Means)</span>
          </div>
          <div className="card-body">
            <div className="chart-container" style={{ height: '350px' }}>
              <ReactECharts option={scatterOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Cluster Explanations & Size</span>
          </div>
          <div className="card-body">
            <div className="chart-container" style={{ height: '350px' }}>
              <ReactECharts option={pieOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
