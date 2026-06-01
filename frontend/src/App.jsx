import React, { useState, useEffect } from 'react';
import { CustomerIQAPI } from './api';
import DashboardPage from './components/DashboardPage';
import ChurnPage from './components/ChurnPage';
import SegmentationPage from './components/SegmentationPage';
import ClvPage from './components/ClvPage';
import CausalPage from './components/CausalPage';
import RecommendationsPage from './components/RecommendationsPage';

const SEARCH_INDEX = [
  // Pages/Tabs
  { name: 'Executive Dashboard', type: 'page', tabId: 'dashboard', icon: '📊' },
  { name: 'Churn Analytics & Drivers', type: 'page', tabId: 'churn', icon: '📈' },
  { name: 'Customer Segmentation Clusters', type: 'page', tabId: 'segmentation', icon: '👥' },
  { name: 'CLV Forecasting & Projections', type: 'page', tabId: 'clv', icon: '💰' },
  { name: 'Causal Impact & Lift Analysis', type: 'page', tabId: 'causal', icon: '🧪' },
  { name: 'AI Recommendations Feed', type: 'page', tabId: 'recommendations', icon: '💡' },

  // Segments
  { name: 'VIP Customer Segment', type: 'segment', query: 'VIP', tabId: 'segmentation', icon: '👑' },
  { name: 'Loyal Customer Segment', type: 'segment', query: 'Loyal', tabId: 'segmentation', icon: '🤝' },
  { name: 'Growth Customer Segment', type: 'segment', query: 'Growth', tabId: 'segmentation', icon: '⚡' },
  { name: 'At-Risk Customer Segment', type: 'segment', query: 'At-Risk', tabId: 'segmentation', icon: '⚠️' },
  { name: 'Dormant Customer Segment', type: 'segment', query: 'Dormant', tabId: 'segmentation', icon: '😴' },

  // Recommendations
  { name: 'Offer Premium Retention Package', type: 'recommendation', query: 'Premium Retention', tabId: 'recommendations', icon: '🎁' },
  { name: 'Personalized Upsell Campaign', type: 'recommendation', query: 'Upsell', tabId: 'recommendations', icon: '🚀' },
  { name: 'Loyalty Reward Acceleration', type: 'recommendation', query: 'Loyalty Reward', tabId: 'recommendations', icon: '✨' },
  { name: 'Enhanced Onboarding Sequence', type: 'recommendation', query: 'Onboarding', tabId: 'recommendations', icon: '🏁' },
  { name: 'Win-Back Email + Discount', type: 'recommendation', query: 'Win-Back', tabId: 'recommendations', icon: '✉️' },

  // Churn Drivers
  { name: 'Support Tickets Impact', type: 'driver', query: 'Support Tickets', tabId: 'churn', icon: '🎫' },
  { name: 'Days Since Last Login Impact', type: 'driver', query: 'Days Since Last Login', tabId: 'churn', icon: '📅' },
  { name: 'Monthly Spend Decline Impact', type: 'driver', query: 'Monthly Spend Decline', tabId: 'churn', icon: '📉' },
  { name: 'Low Engagement Score Impact', type: 'driver', query: 'Low Engagement Score', tabId: 'churn', icon: '📴' },
  { name: 'Contract Type (Monthly) Impact', type: 'driver', query: 'Contract Type', tabId: 'churn', icon: '📄' },
  { name: 'Payment Failures Impact', type: 'driver', query: 'Payment Failures', tabId: 'churn', icon: '❌' },
  { name: 'Loyalty Points Balance Impact', type: 'driver', query: 'Loyalty Points', tabId: 'churn', icon: '🏆' },
  { name: 'Feature Adoption Rate Impact', type: 'driver', query: 'Feature Adoption', tabId: 'churn', icon: '⚙️' },
  { name: 'NPS Score Impact', type: 'driver', query: 'NPS Score', tabId: 'churn', icon: '💬' },
  { name: 'Account Tenure Impact', type: 'driver', query: 'Account Tenure', tabId: 'churn', icon: '⏳' },
];

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [theme, setTheme] = useState(() => localStorage.getItem('customeriq-theme') || 'dark');
  const [isOnline, setIsOnline] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  useEffect(() => {
    // Set theme class on html document element
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('customeriq-theme', theme);
  }, [theme]);

  useEffect(() => {
    // Set current date
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    setCurrentDate(new Date().toLocaleDateString('en-US', options));

    // Initial connection check
    async function checkConn() {
      const status = await CustomerIQAPI.checkConnection();
      setIsOnline(status);
    }
    checkConn();

    // Check periodically
    const interval = setInterval(async () => {
      const status = await CustomerIQAPI.checkConnection();
      setIsOnline(status);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const handleItemSelect = (item) => {
    setCurrentPage(item.tabId);
    if (item.query) {
      setSearchQuery(item.query);
    } else {
      setSearchQuery('');
    }
    setIsSearchFocused(false);
  };

  const getFilteredSearchResults = () => {
    if (!searchQuery.trim()) {
      return [
        { name: 'Go to Churn Analytics', type: 'suggested', tabId: 'churn', icon: '📈' },
        { name: 'Filter by VIP Segment', type: 'suggested', query: 'VIP', tabId: 'segmentation', icon: '👑' },
        { name: 'Review Upsell Recommendation', type: 'suggested', query: 'Upsell', tabId: 'recommendations', icon: '🚀' },
        { name: 'Analyze Support Tickets Driver', type: 'suggested', query: 'Support Tickets', tabId: 'churn', icon: '🎫' },
      ];
    }

    const queryLower = searchQuery.toLowerCase();
    return SEARCH_INDEX.filter(item => 
      item.name.toLowerCase().includes(queryLower) ||
      (item.query && item.query.toLowerCase().includes(queryLower)) ||
      item.type.toLowerCase().includes(queryLower)
    );
  };

  const renderSearchResults = () => {
    const results = getFilteredSearchResults();
    
    if (results.length === 0) {
      return <div className="search-no-results">No matches found for "{searchQuery}"</div>;
    }

    if (!searchQuery.trim()) {
      return (
        <div className="search-section">
          <div className="search-section-title">Suggested Searches</div>
          {results.map((item, idx) => (
            <div
              key={idx}
              className="search-item"
              onMouseDown={() => handleItemSelect(item)}
            >
              <span className="search-item-icon">{item.icon}</span>
              <span className="search-item-text">{item.name}</span>
              <span className="search-item-badge">Quick Link</span>
            </div>
          ))}
        </div>
      );
    }

    // Group by category
    const categories = {
      page: { title: 'Navigate Pages', items: [] },
      segment: { title: 'Customer Segments', items: [] },
      recommendation: { title: 'AI Recommendations', items: [] },
      driver: { title: 'Churn Drivers', items: [] },
    };

    results.forEach(item => {
      if (categories[item.type]) {
        categories[item.type].items.push(item);
      }
    });

    return Object.keys(categories).map(catKey => {
      const cat = categories[catKey];
      if (cat.items.length === 0) return null;
      return (
        <div className="search-section" key={catKey}>
          <div className="search-section-title">{cat.title}</div>
          {cat.items.map((item, idx) => (
            <div
              key={idx}
              className="search-item"
              onMouseDown={() => handleItemSelect(item)}
            >
              <span className="search-item-icon">{item.icon}</span>
              <span className="search-item-text">{item.name}</span>
              <span className="search-item-badge">{item.type.toUpperCase()}</span>
            </div>
          ))}
        </div>
      );
    });
  };

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    const status = await CustomerIQAPI.checkConnection();
    setIsOnline(status);
    
    // Slight timeout to show rotation
    setTimeout(() => {
      setIsRefreshing(false);
    }, 500);
  };

  const renderActivePage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage theme={theme} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />;
      case 'churn':
        return <ChurnPage theme={theme} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />;
      case 'segmentation':
        return <SegmentationPage theme={theme} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />;
      case 'clv':
        return <ClvPage theme={theme} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />;
      case 'causal':
        return <CausalPage theme={theme} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />;
      case 'recommendations':
        return <RecommendationsPage searchQuery={searchQuery} setSearchQuery={setSearchQuery} />;
      default:
        return <DashboardPage theme={theme} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />;
    }
  };

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <rect x="3" y="3" width="7" height="7" rx="1.5" />
          <rect x="14" y="3" width="7" height="7" rx="1.5" />
          <rect x="3" y="14" width="7" height="7" rx="1.5" />
          <rect x="14" y="14" width="7" height="7" rx="1.5" />
        </svg>
      )
    },
    {
      id: 'churn',
      label: 'Churn Analytics',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
        </svg>
      )
    },
    {
      id: 'segmentation',
      label: 'Segmentation',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 2a10 10 0 0 1 0 20" />
          <line x1="2" y1="12" x2="22" y2="12" />
        </svg>
      )
    },
    {
      id: 'clv',
      label: 'CLV Analytics',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <line x1="12" y1="1" x2="12" y2="23" />
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
        </svg>
      )
    },
    {
      id: 'causal',
      label: 'Causal Analysis',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <circle cx="18" cy="5" r="3" />
          <circle cx="6" cy="12" r="3" />
          <circle cx="18" cy="19" r="3" />
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
        </svg>
      )
    },
    {
      id: 'recommendations',
      label: 'Recommendations',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 1 1 7.072 0l-.548.547A3.374 3.374 0 0 0 14 18.469V19a2 2 0 1 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      )
    }
  ];

  return (
    <>
      {/* Sidebar */}
      <aside className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <div className="brand-text">
            <span className="brand-name" style={{ color: '#ffffff' }}>CustomerIQ</span>
            <span className="brand-tag">Intelligence Platform</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          <div className="nav-section-label">Analytics</div>
          {menuItems.map(item => (
            <button
              key={item.id}
              className={`nav-link ${currentPage === item.id ? 'active' : ''}`}
              onClick={() => {
                setCurrentPage(item.id);
                setIsSidebarOpen(false);
              }}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="connection-status">
            <div className={`status-indicator ${isOnline ? 'online' : 'offline'}`}></div>
            <span>{isOnline ? 'API Connected' : 'Demo Mode (Offline)'}</span>
          </div>
        </div>
      </aside>

      {/* Main Container */}
      <main className="main">
        {/* Topbar */}
        <header className="topbar">
          <button className="topbar-menu-btn" onClick={() => setIsSidebarOpen(true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          <div className="topbar-search">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input 
              type="text" 
              placeholder="Search segments, recommendations..." 
              id="global-search" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setIsSearchFocused(true)}
              onBlur={() => setTimeout(() => setIsSearchFocused(false), 200)}
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')} 
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer', 
                  color: 'var(--text-muted)',
                  marginLeft: '4px',
                  display: 'flex',
                  alignItems: 'center'
                }}
                title="Clear Search"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            )}
            {isSearchFocused && (
              <div className="search-dropdown">
                {renderSearchResults()}
              </div>
            )}
          </div>
          <div className="topbar-right">
            <div className="topbar-date">{currentDate}</div>
            <button
              className="topbar-icon-btn"
              onClick={handleRefresh}
              title="Refresh Data"
              style={{
                transform: isRefreshing ? 'rotate(360deg)' : 'none',
                transition: isRefreshing ? 'transform 0.5s ease' : 'none'
              }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="23 4 23 10 17 10" />
                <polyline points="1 20 1 14 7 14" />
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
              </svg>
            </button>
            <button className="topbar-icon-btn" onClick={toggleTheme} title="Toggle Theme">
              {theme === 'dark' ? (
                // Sun Icon (for switching to light theme)
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="5" />
                  <line x1="12" y1="1" x2="12" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="23" />
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                  <line x1="1" y1="12" x2="3" y2="12" />
                  <line x1="21" y1="12" x2="23" y2="12" />
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                </svg>
              ) : (
                // Moon Icon (for switching to dark theme)
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              )}
            </button>
            <div className="topbar-avatar" title="Admin">A</div>
          </div>
        </header>

        {/* Content Area */}
        <div className="content">
          {renderActivePage()}
        </div>
      </main>

      {/* Mobile Drawer Overlay */}
      {isSidebarOpen && (
        <div className="mobile-overlay active" onClick={() => setIsSidebarOpen(false)}></div>
      )}
    </>
  );
}
