import React, { useEffect, useState } from 'react';
import { CustomerIQAPI } from '../api';

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return n.toLocaleString();
  return n;
}

export default function RecommendationsPage({ searchQuery, setSearchQuery }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const res = await CustomerIQAPI.fetchData('recommendations');
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
        <div className="dashboard-grid">
          <div className="card"><div className="skeleton" style={{ height: '280px' }}></div></div>
          <div className="card"><div className="skeleton" style={{ height: '280px' }}></div></div>
        </div>
      </div>
    );
  }

  const filteredCards = data.cards.filter(c =>
    c.segment.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.recommendation.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.priority.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="page active">
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Recommendations & Interventions</h1>
          <p className="page-subtitle">Priority target groups for customer churn mitigation campaigns</p>
        </div>
      </div>

      <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <div className="card">
          <div className="card-header">
            <span className="card-title">Recommendation Matrix (Priority quadrants)</span>
          </div>
          <div className="card-body">
            <div className="matrix-grid">
              {data.priority_matrix.quadrants.map((q, idx) => (
                <div className="matrix-quadrant" style={{ borderColor: q.color }} key={idx}>
                  <div>
                    <div className="quadrant-label" style={{ color: q.color }}>{q.label}</div>
                    <div className="quadrant-desc">{q.description}</div>
                  </div>
                  <div className="quadrant-count">{formatNumber(q.count)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Active AI Decision Engine Summary</span>
          </div>
          <div className="card-body" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '100%' }}>
            <div style={{ fontSize: '14px', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              {data.summary}
            </div>
            <div style={{ marginTop: '20px', padding: '16px', backgroundColor: 'rgba(79, 70, 229, 0.05)', border: '1px solid rgba(79, 70, 229, 0.2)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Expected ROI</div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-success)' }}>4.2x</div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Investments</div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)' }}>$340,000</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title">Active Action Recommendation Feed</span>
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
        <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="rec-cards-list">
            {filteredCards.length > 0 ? (
              filteredCards.map((c, idx) => (
                <div className={`rec-card priority-${c.priority}`} key={idx}>
                  <div className="rec-header">
                    <span className="rec-segment">{c.segment}</span>
                    <span className={`badge ${c.priority === 'critical' ? 'badge-danger' : c.priority === 'high' ? 'badge-warning' : 'badge-primary'}`}>
                      {c.priority.toUpperCase()} PRIORITY
                    </span>
                  </div>
                  <div className="rec-body">
                    <div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                        Target Action Recommendation
                      </div>
                      <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)' }}>{c.recommendation}</div>
                    </div>
                    <div className="rec-stats">
                      <div className="rec-stat">
                        <span className="rec-stat-label">Segment Size</span>
                        <span className="rec-stat-value">{formatNumber(c.customer_count)} users</span>
                      </div>
                      <div className="rec-stat">
                        <span className="rec-stat-label">Churn Risk</span>
                        <span className="rec-stat-value" style={{ color: 'var(--color-danger)' }}>{c.predicted_churn}%</span>
                      </div>
                      <div className="rec-stat">
                        <span className="rec-stat-label">Expected Lift</span>
                        <span className="rec-stat-value" style={{ color: 'var(--color-success)' }}>+{c.expected_lift}%</span>
                      </div>
                    </div>
                  </div>
                  <div className="rec-footer">
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      Estimated Potential Recoverable Revenue:{' '}
                      <strong style={{ color: 'var(--text-primary)' }}>${formatNumber(c.estimated_revenue_saved)}</strong>
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)', fontSize: '13px' }}>
                No recommendations matched your search query.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
