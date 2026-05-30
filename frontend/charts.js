/**
 * CustomerIQ - Reusable Chart Helpers
 */

const ChartColors = {
    primary: '#4F46E5',    // Indigo
    primaryHover: '#6366F1',
    accent: '#38BDF8',     // Sky Blue
    success: '#10B981',    // Emerald
    warning: '#F59E0B',    // Amber
    danger: '#EF4444',     // Rose Red
    info: '#06B6D4',       // Cyan
    textMuted: '#94A3B8',
    gridLines: '#334155'
};

function getThemeGridColor() {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    return isLight ? '#E2E8F0' : '#334155';
}

function getThemeTextColor() {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    return isLight ? '#334155' : '#CBD5E1';
}

function getChartOptions(override = {}) {
    const textColor = getThemeTextColor();
    const gridColor = getThemeGridColor();

    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
                labels: {
                    color: textColor,
                    font: { family: 'Inter', size: 11 }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                titleColor: '#FFFFFF',
                bodyColor: '#F8FAFC',
                borderColor: '#4F46E5',
                borderWidth: 1,
                padding: 10,
                cornerRadius: 8,
                titleFont: { family: 'Inter', size: 12, weight: 'bold' },
                bodyFont: { family: 'Inter', size: 12 }
            }
        },
        scales: {
            x: {
                grid: { color: gridColor, drawBorder: false },
                ticks: { color: textColor, font: { family: 'Inter', size: 10 } }
            },
            y: {
                grid: { color: gridColor, drawBorder: false },
                ticks: { color: textColor, font: { family: 'Inter', size: 10 } }
            }
        },
        ...override
    };
}

// Chart instance cache to prevent memory leaks / double initialization errors
const ChartCache = {};

function createChart(canvasId, config) {
    if (ChartCache[canvasId]) {
        ChartCache[canvasId].destroy();
    }
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    ChartCache[canvasId] = new Chart(ctx, config);
    return ChartCache[canvasId];
}
