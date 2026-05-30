/**
 * Main application controller.
 * Handles navigation, theming, and page lifecycle.
 */

(function () {
    'use strict';

    const pageConfig = {
        overview:        { title: 'Platform Overview',       subtitle: 'Real-time customer intelligence metrics' },
        churn:           { title: 'Churn Analysis',          subtitle: 'Predictive churn modeling & risk assessment' },
        clv:             { title: 'CLV Forecast',            subtitle: 'Customer lifetime value predictions' },
        segmentation:    { title: 'Customer Segmentation',   subtitle: 'Behavioral clustering & persona mapping' },
        causal:          { title: 'Causal Impact Analysis',  subtitle: 'Campaign treatment effects & uplift modeling' },
        recommendations: { title: 'Retention Recommendations', subtitle: 'AI-powered intervention strategy' },
        explainability:  { title: 'Model Explainability',    subtitle: 'SHAP-based feature attribution' },
    };

    let currentPage = 'overview';

    // Navigation
    function navigateTo(page) {
        if (!pageConfig[page]) return;
        currentPage = page;

        // Update nav
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        const navItem = document.querySelector(`[data-page="${page}"]`);
        if (navItem) navItem.classList.add('active');

        // Update topbar
        document.getElementById('page-title').textContent = pageConfig[page].title;
        document.getElementById('page-subtitle').textContent = pageConfig[page].subtitle;

        // Update pages
        document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
        const pageEl = document.getElementById('page-' + page);
        if (pageEl) {
            // Render content
            const renderer = PageRenderers[page];
            if (renderer) pageEl.innerHTML = renderer();
            pageEl.classList.add('active');

            // Initialize charts after render
            requestAnimationFrame(() => {
                const chartInit = ChartInitializers[page];
                if (chartInit) chartInit();
            });
        }

        // Close mobile sidebar
        document.getElementById('sidebar').classList.remove('open');
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) overlay.classList.remove('active');
    }

    // Theme toggle
    function toggleTheme() {
        const html = document.documentElement;
        const current = html.getAttribute('data-theme');
        html.setAttribute('data-theme', current === 'light' ? 'dark' : 'light');
        localStorage.setItem('theme', html.getAttribute('data-theme'));
        // Re-render current page to update chart colors
        navigateTo(currentPage);
    }

    // Initialize
    function init() {
        // Restore theme
        const saved = localStorage.getItem('theme');
        if (saved) document.documentElement.setAttribute('data-theme', saved);

        // Nav clicks
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', e => {
                e.preventDefault();
                navigateTo(item.dataset.page);
            });
        });

        // Mobile menu
        const menuBtn = document.getElementById('menu-toggle');
        const sidebar = document.getElementById('sidebar');
        menuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            let overlay = document.querySelector('.sidebar-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = 'sidebar-overlay';
                document.body.appendChild(overlay);
                overlay.addEventListener('click', () => {
                    sidebar.classList.remove('open');
                    overlay.classList.remove('active');
                });
            }
            overlay.classList.toggle('active');
        });

        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', function () {
            this.classList.add('spinning');
            setTimeout(() => {
                this.classList.remove('spinning');
                navigateTo(currentPage);
            }, 800);
        });

        // API status check
        checkApiStatus();

        // Render initial page
        navigateTo('overview');
    }

    async function checkApiStatus() {
        const statusEl = document.getElementById('api-status');
        try {
            const res = await fetch('http://localhost:8000/health', { signal: AbortSignal.timeout(3000) });
            if (res.ok) {
                statusEl.innerHTML = '<div class="status-dot"></div><span>API Connected</span>';
            } else {
                throw new Error('not ok');
            }
        } catch {
            statusEl.innerHTML = '<div class="status-dot" style="background:#f59e0b;box-shadow:0 0 8px rgba(245,158,11,0.5)"></div><span>Demo Mode</span>';
        }
    }

    document.addEventListener('DOMContentLoaded', init);
})();
