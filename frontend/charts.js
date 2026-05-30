/**
 * Chart.js configuration and helpers for the dashboard.
 */

const ChartDefaults = {
    colors: {
        blue: '#3b82f6',
        purple: '#8b5cf6',
        emerald: '#10b981',
        amber: '#f59e0b',
        rose: '#f43f5e',
        cyan: '#06b6d4',
        grid: 'rgba(148, 163, 184, 0.08)',
        gridLight: 'rgba(148, 163, 184, 0.15)',
    },
    font: { family: "'Inter', sans-serif" },
};

function getChartOptions(overrides = {}) {
    const isDark = !document.documentElement.hasAttribute('data-theme') || document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? ChartDefaults.colors.grid : ChartDefaults.colors.gridLight;

    return Object.assign({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false, labels: { color: textColor, font: { family: ChartDefaults.font.family, size: 11 } } },
            tooltip: {
                backgroundColor: isDark ? '#1a2035' : '#ffffff',
                titleColor: isDark ? '#f1f5f9' : '#0f172a',
                bodyColor: isDark ? '#94a3b8' : '#475569',
                borderColor: isDark ? '#2d3a52' : '#e2e8f0',
                borderWidth: 1,
                cornerRadius: 8,
                padding: 10,
                titleFont: { family: ChartDefaults.font.family, weight: '600' },
                bodyFont: { family: ChartDefaults.font.family },
            },
        },
        scales: {
            x: {
                grid: { color: gridColor, drawBorder: false },
                ticks: { color: textColor, font: { family: ChartDefaults.font.family, size: 11 } },
            },
            y: {
                grid: { color: gridColor, drawBorder: false },
                ticks: { color: textColor, font: { family: ChartDefaults.font.family, size: 11 } },
            },
        },
    }, overrides);
}

function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, ctx.canvas.height);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// Stored chart instances for cleanup
const chartInstances = {};

function destroyChart(id) {
    if (chartInstances[id]) {
        chartInstances[id].destroy();
        delete chartInstances[id];
    }
}

function createLineChart(canvasId, labels, datasets, options = {}) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');

    const processedDatasets = datasets.map(ds => ({
        ...ds,
        borderWidth: ds.borderWidth || 2.5,
        pointRadius: ds.pointRadius ?? 0,
        pointHoverRadius: ds.pointHoverRadius || 5,
        tension: ds.tension ?? 0.4,
        fill: ds.fill ?? true,
        backgroundColor: ds.fill !== false ? createGradient(ctx, (ds.borderColor || '#3b82f6') + '30', (ds.borderColor || '#3b82f6') + '00') : undefined,
    }));

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: processedDatasets },
        options: getChartOptions(options),
    });
    return chartInstances[canvasId];
}

function createBarChart(canvasId, labels, datasets, options = {}) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    chartInstances[canvasId] = new Chart(canvas, {
        type: 'bar',
        data: { labels, datasets: datasets.map(ds => ({ borderRadius: 6, borderSkipped: false, maxBarThickness: 50, ...ds })) },
        options: getChartOptions(options),
    });
    return chartInstances[canvasId];
}

function createDoughnutChart(canvasId, labels, data, colors, options = {}) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    chartInstances[canvasId] = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{ data, backgroundColor: colors, borderWidth: 0, hoverOffset: 8 }],
        },
        options: Object.assign({
            responsive: true, maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: { position: 'bottom', labels: { color: getChartOptions().scales.x.ticks.color, font: { family: ChartDefaults.font.family, size: 11 }, padding: 16, usePointStyle: true, pointStyleWidth: 8 } },
                tooltip: getChartOptions().plugins.tooltip,
            },
        }, options),
    });
    return chartInstances[canvasId];
}

function createScatterChart(canvasId, datasets, options = {}) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    chartInstances[canvasId] = new Chart(canvas, {
        type: 'scatter',
        data: { datasets },
        options: getChartOptions(options),
    });
    return chartInstances[canvasId];
}

function createHorizontalBarChart(canvasId, labels, data, colors, options = {}) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    chartInstances[canvasId] = new Chart(canvas, {
        type: 'bar',
        data: { labels, datasets: [{ data, backgroundColor: colors, borderRadius: 6, borderSkipped: false, maxBarThickness: 28 }] },
        options: getChartOptions({ indexAxis: 'y', scales: { ...getChartOptions().scales, x: { ...getChartOptions().scales.x, beginAtZero: true } }, ...options }),
    });
    return chartInstances[canvasId];
}
