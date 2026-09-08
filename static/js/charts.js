/**
 * SmartCart - Dynamic Chart.js Analytics Controller
 * Renders all 12 real database charts with dark-mode responsiveness.
 */

window.adminChartInstances = {};

async function renderAllAdminCharts() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? '#334155' : '#e2e8f0';

    try {
        const response = await fetch('/admin/api/analytics/charts');
        const data = await response.json();

        // Helper to destroy prior instance before re-render
        function createChart(canvasId, config) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            if (window.adminChartInstances[canvasId]) {
                window.adminChartInstances[canvasId].destroy();
            }
            window.adminChartInstances[canvasId] = new Chart(canvas, config);
        }

        // 1. Daily Sales
        createChart('chartDailySales', {
            type: 'line',
            data: {
                labels: data.daily_sales.labels,
                datasets: [{
                    label: 'Daily Revenue (₹)',
                    data: data.daily_sales.data,
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    fill: true,
                    tension: 0.35
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });

        // 2. Monthly Revenue
        createChart('chartMonthlyRevenue', {
            type: 'bar',
            data: {
                labels: data.monthly_revenue.labels,
                datasets: [{
                    label: 'Monthly Revenue (₹)',
                    data: data.monthly_revenue.data,
                    backgroundColor: '#06b6d4',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });

        // 3. Orders Over Time
        createChart('chartOrdersOverTime', {
            type: 'line',
            data: {
                labels: data.orders_over_time.labels,
                datasets: [{
                    label: 'Orders',
                    data: data.orders_over_time.data,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });

        // 4. Sales by Category
        createChart('chartSalesByCategory', {
            type: 'doughnut',
            data: {
                labels: data.sales_by_category.labels,
                datasets: [{
                    data: data.sales_by_category.data,
                    backgroundColor: ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#14b8a6', '#64748b']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: textColor, boxWidth: 12 } } }
            }
        });

        // 5. Top Products
        createChart('chartTopProducts', {
            type: 'bar',
            data: {
                labels: data.top_products.labels,
                datasets: [{
                    label: 'Units Sold',
                    data: data.top_products.units,
                    backgroundColor: '#f59e0b',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { grid: { display: false }, ticks: { color: textColor } }
                }
            }
        });

        // 6. Customer Growth
        createChart('chartCustomerGrowth', {
            type: 'line',
            data: {
                labels: data.customer_growth.labels,
                datasets: [{
                    label: 'New Customers',
                    data: data.customer_growth.data,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.15)',
                    fill: true,
                    tension: 0.35
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });

        // 7. Product Views & Interaction Funnel
        createChart('chartProductViews', {
            type: 'bar',
            data: {
                labels: data.funnel.labels,
                datasets: [{
                    label: 'Events Count',
                    data: data.funnel.data,
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });

        // 8. Add-to-Cart Rate
        createChart('chartAddToCartRate', {
            type: 'doughnut',
            data: {
                labels: ['Added to Cart', 'Browsed Only'],
                datasets: [{
                    data: [data.cart_rate, Math.max(0, 100 - data.cart_rate)],
                    backgroundColor: ['#06b6d4', isDark ? '#334155' : '#e2e8f0']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: textColor } } }
            }
        });

        // 9. Purchase Conversion Rate
        createChart('chartConversionRate', {
            type: 'doughnut',
            data: {
                labels: ['Purchased', 'Abandoned'],
                datasets: [{
                    data: [data.conversion_rate, Math.max(0, 100 - data.conversion_rate)],
                    backgroundColor: ['#10b981', isDark ? '#334155' : '#e2e8f0']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: textColor } } }
            }
        });

        // 10. Recommendation Click Rate
        createChart('chartRecClickRate', {
            type: 'bar',
            data: {
                labels: ['Recommendation CTR (%)'],
                datasets: [{
                    data: [data.rec_ctr],
                    backgroundColor: '#4f46e5',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { min: 0, max: 100, ticks: { color: textColor, callback: v => v + '%' }, grid: { color: gridColor } },
                    x: { ticks: { color: textColor }, grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });

        // 11. Recommendation Purchase Rate
        createChart('chartRecPurchaseRate', {
            type: 'bar',
            data: {
                labels: ['Recommendation CVR (%)'],
                datasets: [{
                    data: [data.rec_cvr],
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { min: 0, max: 100, ticks: { color: textColor, callback: v => v + '%' }, grid: { color: gridColor } },
                    x: { ticks: { color: textColor }, grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });

        // 12. Average Order Value
        createChart('chartDailyAOV', {
            type: 'line',
            data: {
                labels: data.daily_aov.labels,
                datasets: [{
                    label: 'AOV (₹)',
                    data: data.daily_aov.data,
                    borderColor: '#ec4899',
                    backgroundColor: 'rgba(236, 72, 153, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: { grid: { color: gridColor }, ticks: { color: textColor } }
                }
            }
        });

    } catch (e) {
        console.error('Error fetching admin chart data:', e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('chartDailySales')) {
        renderAllAdminCharts();
    }
});
