/**
 * Interactive Charts using Plotly.js
 * This module handles all interactive chart visualizations with API integration
 */

class InteractiveCharts {
    constructor() {
        this.plotlyConfig = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
            modeBarButtonsToAdd: ['downloadSVG'],
            displaylogo: false
        };
    }

    // Sentiment chart removed - using static image instead

    /**
     * Create difficulty rating bar chart
     */
    async createDifficultyChart() {
        try {
            const response = await fetch('/api/chart-data/difficulty_rating');
            const data = await response.json();
            
            const plotData = [{
                type: 'bar',
                x: data.labels,
                y: data.values,
                text: data.values,
                textposition: 'auto',
                hovertemplate: '<b>%{x}</b><br>Count: %{y}<extra></extra>',
                marker: {
                    color: data.values,
                    colorscale: 'RdYlGn_r',
                    line: {
                        color: 'rgba(50,171,96,1.0)',
                        width: 1
                    }
                }
            }];

            const layout = {
                title: {
                    text: 'Difficulty Rating Distribution',
                    font: { size: 18, family: 'Arial, sans-serif' }
                },
                xaxis: {
                    title: 'Difficulty Level',
                    tickangle: -45
                },
                yaxis: {
                    title: 'Count'
                },
                margin: { t: 60, b: 100, l: 60, r: 60 }
            };

            Plotly.newPlot('difficulty-chart', plotData, layout, this.plotlyConfig);
            
            // Add export functionality
            this.addExportButton('difficulty-chart', 'difficulty_rating');
            
        } catch (error) {
            console.error('Error creating difficulty chart:', error);
            this.showError('difficulty-chart', 'Failed to load difficulty data');
        }
    }

    /**
     * Create attendance over time line chart
     */
    async createAttendanceChart() {
        try {
            const response = await fetch('/api/chart-data/attendance_over_time');
            const data = await response.json();
            
            const plotData = [{
                type: 'scatter',
                mode: 'lines+markers',
                x: data.dates,
                y: data.values,
                name: 'Attendance Rate',
                hovertemplate: '<b>%{x}</b><br>Attendance: %{y}%<extra></extra>',
                line: {
                    color: '#1f77b4',
                    width: 3
                },
                marker: {
                    size: 8,
                    color: '#1f77b4',
                    line: {
                        color: 'white',
                        width: 2
                    }
                }
            }];

            const layout = {
                title: {
                    text: 'Attendance Over Time',
                    font: { size: 18, family: 'Arial, sans-serif' }
                },
                xaxis: {
                    title: 'Date',
                    type: 'date'
                },
                yaxis: {
                    title: 'Attendance Rate (%)',
                    range: [0, 100]
                },
                margin: { t: 60, b: 60, l: 60, r: 60 },
                showlegend: false
            };

            Plotly.newPlot('attendance-chart', plotData, layout, this.plotlyConfig);
            
            // Add export functionality
            this.addExportButton('attendance-chart', 'attendance_over_time');
            
        } catch (error) {
            console.error('Error creating attendance chart:', error);
            this.showError('attendance-chart', 'Failed to load attendance data');
        }
    }

    // Correlation heatmap removed - using static image instead

    /**
     * Add export button for a chart
     */
    addExportButton(chartId, chartName) {
        const chartContainer = document.getElementById(chartId);
        if (!chartContainer) return;

        // Remove existing export button if any
        const existingButton = chartContainer.parentElement.querySelector('.export-btn');
        if (existingButton) {
            existingButton.remove();
        }

        // Create export button
        const exportButton = document.createElement('button');
        exportButton.className = 'btn btn-sm btn-outline-secondary export-btn mt-2';
        exportButton.innerHTML = '<i class="fas fa-download"></i> Export Chart';
        exportButton.onclick = () => this.exportChart(chartId, chartName);

        // Add button after chart
        chartContainer.parentElement.appendChild(exportButton);
    }

    /**
     * Export chart as PNG
     */
    exportChart(chartId, chartName) {
        Plotly.downloadImage(chartId, {
            format: 'png',
            width: 1200,
            height: 800,
            filename: `${chartName}_${new Date().toISOString().split('T')[0]}`
        });
    }

    /**
     * Show error message in chart container
     */
    showError(chartId, message) {
        const container = document.getElementById(chartId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning d-flex align-items-center" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <div>${message}</div>
                </div>
            `;
        }
    }

    /**
     * Initialize all charts
     */
    async initializeAll() {
        const charts = [
            { method: 'createDifficultyChart', elementId: 'difficulty-chart' },
            { method: 'createAttendanceChart', elementId: 'attendance-chart' }
        ];

        for (const chart of charts) {
            if (document.getElementById(chart.elementId)) {
                try {
                    await this[chart.method]();
                } catch (error) {
                    console.error(`Error initializing ${chart.method}:`, error);
                }
            }
        }
        
        console.log('[CHARTS] Interactive charts initialization complete');
    }
}

// Simplified initialization - only initialize if elements exist and Plotly is available
function initializeChartsWhenReady() {
    console.log('[CHARTS] Checking for interactive chart elements...');
    
    // Only initialize if we have elements that need interactive charts
    const difficultyChart = document.getElementById('difficulty-chart');
    const attendanceChart = document.getElementById('attendance-chart');
    
    if (!difficultyChart && !attendanceChart) {
        console.log('[CHARTS] No interactive chart elements found, skipping initialization');
        return;
    }
    
    // Check if Plotly is available
    if (typeof Plotly === 'undefined') {
        console.warn('[CHARTS] Plotly not loaded yet, retrying in 500ms...');
        setTimeout(initializeChartsWhenReady, 500);
        return;
    }
    
    console.log('[CHARTS] Initializing available interactive charts...');
    const charts = new InteractiveCharts();
    charts.initializeAll();
}

// Start initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChartsWhenReady);
} else {
    // DOM is already loaded
    initializeChartsWhenReady();
}

// Export for external use
window.InteractiveCharts = InteractiveCharts;