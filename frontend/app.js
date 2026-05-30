/**
 * CustomerIQ - Navigation & Lifecycle Controller
 */

(function () {
    'use strict';

    let currentPage = 'dashboard';

    // Global navigation switcher
    async function navigateTo(pageId) {
        currentPage = pageId;

        // Update nav UI active states
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('data-page') === pageId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Hide all pages first
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Render target page content
        const targetPage = document.getElementById(`page-${pageId}`);
        if (targetPage) {
            // Apply a loading skeleton state first
            targetPage.innerHTML = `
                <div class="page-header">
                    <div>
                        <div class="skeleton skeleton-title"></div>
                        <div class="skeleton skeleton-text" style="width: 40%"></div>
                    </div>
                </div>
                <div class="kpis-row">
                    <div class="kpi-card"><div class="skeleton skeleton-text" style="height: 60px"></div></div>
                    <div class="kpi-card"><div class="skeleton skeleton-text" style="height: 60px"></div></div>
                    <div class="kpi-card"><div class="skeleton skeleton-text" style="height: 60px"></div></div>
                    <div class="kpi-card"><div class="skeleton skeleton-text" style="height: 60px"></div></div>
                </div>
                <div class="dashboard-grid">
                    <div class="card" style="height: 300px"><div class="skeleton" style="height: 100%"></div></div>
                    <div class="card" style="height: 300px"><div class="skeleton" style="height: 100%"></div></div>
                </div>
            `;
            targetPage.classList.add('active');

            try {
                // Fetch dynamic layout template
                const renderer = PageRenderers[pageId];
                if (renderer) {
                    const html = await renderer();
                    targetPage.innerHTML = html;
                    
                    // Allow UI to paint before rendering the canvas charts
                    requestAnimationFrame(() => {
                        const initChart = ChartInitializers[pageId];
                        if (initChart) {
                            initChart();
                        }
                    });
                }
            } catch (err) {
                console.error(`Error rendering page ${pageId}:`, err);
                targetPage.innerHTML = `
                    <div class="page-header">
                        <h1 class="page-title">Error Loading Page</h1>
                    </div>
                    <div class="card">
                        <div class="card-body">
                            <p style="color:var(--color-danger)">Failed to load data. Please make sure the backend is active or try reloading.</p>
                        </div>
                    </div>
                `;
            }
        }

        // Close mobile drawer if active
        document.getElementById('sidebar').classList.remove('open');
        document.getElementById('mobile-overlay').classList.remove('active');
    }

    // Theme toggler
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('customeriq-theme', nextTheme);

        // Update charts to match new colors
        navigateTo(currentPage);
    }

    // Set up everything on load
    async function init() {
        // Restore theme selection
        const savedTheme = localStorage.getItem('customeriq-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);

        // Set current date
        const dateEl = document.getElementById('current-date');
        if (dateEl) {
            const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
            dateEl.textContent = new Date().toLocaleDateString('en-US', options);
        }

        // Sidebar Navigation click events
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const pageId = link.getAttribute('data-page');
                if (pageId) {
                    navigateTo(pageId);
                }
            });
        });

        // Mobile sidebar toggle controls
        const menuBtn = document.getElementById('menu-btn');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');

        if (menuBtn && sidebar && overlay) {
            menuBtn.addEventListener('click', () => {
                sidebar.classList.add('open');
                overlay.classList.add('active');
            });

            overlay.addEventListener('click', () => {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            });
        }

        // Theme button click event
        const themeBtn = document.getElementById('theme-btn');
        if (themeBtn) {
            themeBtn.addEventListener('click', toggleTheme);
        }

        // Refresh button click event
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                refreshBtn.style.transform = 'rotate(360deg)';
                refreshBtn.style.transition = 'transform 0.5s ease';
                await window.CustomerIQAPI.checkConnection();
                await navigateTo(currentPage);
                setTimeout(() => {
                    refreshBtn.style.transform = 'none';
                    refreshBtn.style.transition = 'none';
                }, 500);
            });
        }

        // Connect status checks
        await window.CustomerIQAPI.checkConnection();
        // Check connection periodically
        setInterval(() => {
            window.CustomerIQAPI.checkConnection();
        }, 10000);

        // Load dashboard page by default
        navigateTo('dashboard');
    }

    // Export PDF stub
    window.exportDashboard = function () {
        alert("Preparing executive PDF report download...\n\nMetrics summary:\nTotal Users: 125,842\nAvg CLV: $842\nChurn Risk: 7.4%\nCampaign ROI: 4.2x\n\nDownload will start shortly.");
    };

    document.addEventListener('DOMContentLoaded', init);
})();
