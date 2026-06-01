import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { CustomerIQAPI } from '../api';

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return n.toLocaleString();
  return n;
}

export default function CausalPage({ theme, searchQuery, setSearchQuery }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const res = await CustomerIQAPI.fetchData('causal');
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
        <div className="grid-2col">
          <div className="card"><div className="skeleton" style={{ height: '150px' }}></div></div>
          <div className="card"><div className="skeleton" style={{ height: '150px' }}></div></div>
        </div>
      </div>
    );
  }

  const tc = data.treatment_control;
  const eff = data.effects;
  const did = data.did_plot;
  const isDark = theme === 'dark';
  const textColor = isDark ? '#CBD5E1' : '#334155';
  const gridColor = isDark ? '#334155' : '#E2E8F0';

  const didOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#4F46E5',
      borderWidth: 1,
      textStyle: { color: '#F8FAFC', fontFamily: 'Inter' }
    },
    legend: {
      data: ['Treatment Group (Campaign)', 'Control Group (Holdout)'],
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
      data: did.labels,
      axisLabel: { color: textColor, fontFamily: 'Inter' },
      axisLine: { lineStyle: { color: gridColor } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: textColor,
        fontFamily: 'Inter',
        formatter: '{value}%'
      },
      splitLine: { lineStyle: { color: gridColor } }
    },
    series: [
      {
        name: 'Treatment Group (Campaign)',
        type: 'line',
        data: did.treatment,
        smooth: true,
        itemStyle: { color: '#4F46E5' },
        lineStyle: { width: 2 }
      },
      {
        name: 'Control Group (Holdout)',
        type: 'line',
        data: did.control,
        smooth: true,
        itemStyle: { color: '#94A3B8' },
        lineStyle: { width: 2 }
      }
    ]
  };

  const upliftOption = {
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
        name: 'Uplift Segment',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['45%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false },
        data: data.uplift_segments.labels.map((label, idx) => ({
          value: data.uplift_segments.counts[idx],
          name: label,
          itemStyle: { color: data.uplift_segments.colors[idx] }
        }))
      }
    ]
  };

  return (
    <div className="page active">
      <div className="page-header">
        <div>
          <h1 className="page-title">Causal Impact Analysis</h1>
          <p className="page-subtitle">Propensity score matching & Difference-in-Differences statistical evaluation</p>
        </div>
      </div>

      <div className="grid-2col">
        <div className="card" style={{ borderTop: '4px solid var(--color-primary)' }}>
          <div className="card-header">
            <span className="card-title">Treatment Group (Campaign Recipients)</span>
            <span className="badge badge-primary">Sample Size: {formatNumber(tc.treatment.size)}</span>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Churn Rate</span>
                <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--color-danger)' }}>{tc.treatment.churn_rate}%</div>
              </div>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Avg CLV Contribution</span>
                <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--color-success)' }}>${tc.treatment.avg_clv}</div>
              </div>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Retention Score</span>
                <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--color-primary-hover)' }}>{tc.treatment.retention}%</div>
              </div>
            </div>
          </div>
        </div>

        <div className="card" style={{ borderTop: '4px solid var(--text-muted)' }}>
          <div className="card-header">
            <span className="card-title">Control Group (Campaign Holdout)</span>
            <span className="badge" style={{ backgroundColor: 'rgba(148,163,184,0.1)', color: 'var(--text-muted)' }}>
              Sample Size: {formatNumber(tc.control.size)}
            </span>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Churn Rate</span>
                <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--text-muted)' }}>{tc.control.churn_rate}%</div>
              </div>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Avg CLV Contribution</span>
                <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--text-muted)' }}>${tc.control.avg_clv}</div>
              </div>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Retention Score</span>
                <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--text-muted)' }}>{tc.control.retention}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Difference-in-Differences Campaign Plot</span>
          </div>
          <div className="card-body">
            <div className="chart-container">
              <ReactECharts option={didOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Uplift Target Segmentation</span>
          </div>
          <div className="card-body">
            <div className="chart-container">
              <ReactECharts option={upliftOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>
      </div>

      <div className="grid-3col">
        <div className="card">
          <div className="card-header"><span className="card-title">Average Treatment Effect (ATE)</span></div>
          <div className="card-body" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-danger)' }}>{eff.ate.value}%</div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Confidence Interval: [{eff.ate.ci_lower}%, {eff.ate.ci_upper}%]</span>
            <div style={{ marginTop: '8px', fontSize: '11px', fontWeight: 600, color: 'var(--color-success)' }}>
              Statistically Significant (p = {eff.ate.p_value})
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">Treatment on Treated (ATT)</span></div>
          <div className="card-body" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-danger)' }}>{eff.att.value}%</div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Confidence Interval: [{eff.att.ci_lower}%, {eff.att.ci_upper}%]</span>
            <div style={{ marginTop: '8px', fontSize: '11px', fontWeight: 600, color: 'var(--color-success)' }}>
              Statistically Significant (p = {eff.att.p_value})
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">Campaign Uplift Lift</span></div>
          <div className="card-body" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-success)' }}>+{eff.uplift.value}%</div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Confidence Interval: [{eff.uplift.ci_lower}%, {eff.uplift.ci_upper}%]</span>
            <div style={{ marginTop: '8px', fontSize: '11px', fontWeight: 600, color: 'var(--color-success)' }}>
              Statistically Significant (p = {eff.uplift.p_value})
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
