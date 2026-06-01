import React, { useState, useEffect } from 'react';
import { CustomerIQAPI } from './api';
import DashboardPage from './components/DashboardPage';
import ChurnPage from './components/ChurnPage';
import SegmentationPage from './components/SegmentationPage';
import ClvPage from './components/ClvPage';
import CausalPage from './components/CausalPage';
import RecommendationsPage from './components/RecommendationsPage';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [theme, setTheme] = useState(() => localStorage.getItem('customeriq-theme') || 'dark');
  const [isOnline, setIsOnline] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

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
