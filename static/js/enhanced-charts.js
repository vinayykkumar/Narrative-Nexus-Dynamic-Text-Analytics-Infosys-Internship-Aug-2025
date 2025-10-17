// Enhanced Interactive Charts with Advanced Animations
// =====================================================

// Animation configurations
const ANIMATION_CONFIG = {
    duration: 1500,
    easing: 'easeOutCubic',
    stagger: 100,
    bounce: 'easeOutBounce',
    elastic: 'easeOutElastic'
};

// Color palettes for different chart types
const COLOR_PALETTES = {
    sentiment: {
        positive: '#22c55e',
        neutral: '#64748b', 
        negative: '#ef4444'
    },
    gradient: [
        '#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', 
        '#ef4444', '#ec4899', '#8b5cf6', '#06b6d4'
    ],
    vibrant: [
        '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
        '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43'
    ]
};

// Enhanced Chart.js configurations
Chart.defaults.plugins.legend.position = 'bottom';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 15;

// Utility functions
function getRandomColor(alpha = 1) {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);  
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function generateGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

function createPulsingAnimation() {
    return {
        duration: 2000,
        easing: 'easeInOutQuad',
        loop: true,
        delay: (context) => context.dataIndex * 200
    };
}

// Enhanced drawing functions
async function drawEnhancedSentimentChart() {
    const container = document.getElementById('sentiment-chart');
    if (!container) return;

    showLoader('sentiment');
    
    try {
        const data = await safeFetchJson('/api/sentiment-data');
        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = "<div class='no-data'>No sentiment data available</div>";
            hideLoader('sentiment');
            return;
        }

        // Clear container and create canvas
        container.innerHTML = '<canvas id="sentiment-canvas"></canvas>';
        const ctx = document.getElementById('sentiment-canvas').getContext('2d');

        // Prepare data with emojis
        const labels = ['😊 Positive', '😐 Neutral', '😔 Negative'];
        const values = [data.positive || 0, data.neutral || 0, data.negative || 0];
        const colors = [COLOR_PALETTES.sentiment.positive, COLOR_PALETTES.sentiment.neutral, COLOR_PALETTES.sentiment.negative];
        
        // Create gradients for each segment
        const backgroundColors = colors.map(color => {
            const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, 150);
            gradient.addColorStop(0, color);
            gradient.addColorStop(1, color + '80');
            return gradient;
        });

        const sentimentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
                    borderColor: colors,
                    borderWidth: 3,
                    hoverBorderWidth: 5,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: { size: 12, weight: 'bold' },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#ffffff',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            title: function(context) {
                                return '📈 Sentiment Analysis';
                            },
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} items (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: ANIMATION_CONFIG.duration,
                    easing: ANIMATION_CONFIG.bounce
                },
                interaction: {
                    intersect: false,
                    mode: 'nearest'
                },
                onHover: (event, elements) => {
                    event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
                }
            }
        });

        // Add center text animation
        setTimeout(() => {
            addCenterText(ctx, values.reduce((a, b) => a + b, 0), 'Total Items');
        }, ANIMATION_CONFIG.duration);

        hideLoader('sentiment');

    } catch (error) {
        console.error('Error creating sentiment chart:', error);
        container.innerHTML = "<div class='error-message'>Error loading sentiment data</div>";
        hideLoader('sentiment');
    }
}

async function drawEnhancedDifficultyChart() {
    const container = document.getElementById('difficulty-chart');
    if (!container) return;

    showLoader('difficulty');
    
    try {
        const data = await safeFetchJson('/api/difficulty-data');
        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = "<div class='no-data'>No difficulty data available</div>";
            hideLoader('difficulty');
            return;
        }

        container.innerHTML = '<canvas id="difficulty-canvas"></canvas>';
        const ctx = document.getElementById('difficulty-canvas').getContext('2d');

        const labels = Object.keys(data);
        const values = Object.values(data);
        
        // Create animated gradient backgrounds
        const gradients = values.map((_, index) => {
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            const baseColor = COLOR_PALETTES.vibrant[index % COLOR_PALETTES.vibrant.length];
            gradient.addColorStop(0, baseColor);
            gradient.addColorStop(1, baseColor + '40');
            return gradient;
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Count',
                    data: values,
                    backgroundColor: gradients,
                    borderColor: COLOR_PALETTES.vibrant.slice(0, values.length),
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                    hoverBackgroundColor: COLOR_PALETTES.vibrant.slice(0, values.length),
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#ffffff',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            title: () => 'Difficulty Level',
                            label: (context) => `${context.label}: ${context.raw} items`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            font: { size: 11 },
                            color: '#666'
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            font: { size: 11, weight: 'bold' },
                            color: '#333'
                        }
                    }
                },
                animation: {
                    duration: ANIMATION_CONFIG.duration,
                    easing: ANIMATION_CONFIG.elastic,
                    delay: (context) => context.dataIndex * ANIMATION_CONFIG.stagger
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                onHover: (event, elements) => {
                    event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
                }
            }
        });

        hideLoader('difficulty');

    } catch (error) {
        console.error('Error creating difficulty chart:', error);
        container.innerHTML = "<div class='error-message'>Error loading difficulty data</div>";
        hideLoader('difficulty');
    }
}

async function drawEnhancedAttendanceChart() {
    const container = document.getElementById('attendance-chart');
    if (!container) return;

    showLoader('attendance');
    
    try {
        const data = await safeFetchJson('/api/attendance-data');
        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = "<div class='no-data'>No attendance data available</div>";
            hideLoader('attendance');
            return;
        }

        container.innerHTML = '<canvas id="attendance-canvas"></canvas>';
        const ctx = document.getElementById('attendance-canvas').getContext('2d');

        const labels = Object.keys(data);
        const values = Object.values(data);

        // Create rainbow gradient effect
        const rainbowGradients = labels.map((_, index) => {
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            const hue = (index / labels.length) * 360;
            gradient.addColorStop(0, `hsl(${hue}, 70%, 60%)`);
            gradient.addColorStop(1, `hsl(${hue}, 70%, 40%)`);
            return gradient;
        });

        new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: rainbowGradients,
                    borderColor: labels.map((_, index) => {
                        const hue = (index / labels.length) * 360;
                        return `hsl(${hue}, 70%, 50%)`;
                    }),
                    borderWidth: 2,
                    hoverBorderWidth: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: { size: 11, weight: 'bold' },
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#ffffff',
                        borderWidth: 1,
                        cornerRadius: 8
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            display: false
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: ANIMATION_CONFIG.duration,
                    easing: ANIMATION_CONFIG.bounce,
                    delay: (context) => context.dataIndex * 150
                }
            }
        });

        hideLoader('attendance');

    } catch (error) {
        console.error('Error creating attendance chart:', error);
        container.innerHTML = "<div class='error-message'>Error loading attendance data</div>";
        hideLoader('attendance');
    }
}

// Helper function to add center text to doughnut charts
function addCenterText(ctx, text, label) {
    const canvas = ctx.canvas;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    ctx.save();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#333';
    ctx.font = 'bold 24px Poppins';
    ctx.fillText(text, centerX, centerY - 5);
    ctx.font = '12px Poppins';
    ctx.fillStyle = '#666';
    ctx.fillText(label, centerX, centerY + 20);
    ctx.restore();
}

// Enhanced loader and error styling
function showLoader(key) {
    const loader = document.querySelector(`[data-loader-for="${key}"]`);
    if (loader) {
        loader.style.display = 'flex';
        loader.innerHTML = '<div class="enhanced-spinner"></div>';
    }
}

function hideLoader(key) {
    const loader = document.querySelector(`[data-loader-for="${key}"]`);
    if (loader) {
        loader.style.display = 'none';
    }
}

// CSS injection for enhanced styling
function injectEnhancedStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .enhanced-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(67, 97, 238, 0.1);
            border-top: 4px solid #4361ee;
            border-radius: 50%;
            animation: spin 1s linear infinite, pulse 2s ease-in-out infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .no-data, .error-message {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #666;
            font-size: 14px;
            text-align: center;
            padding: 20px;
        }
        
        .error-message {
            color: #ef4444;
        }
        
        .plot-card {
            transition: all 0.3s ease;
        }
        
        .plot-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .interactive-chart canvas {
            border-radius: 8px;
        }
    `;
    document.head.appendChild(style);
}

// Safe fetch function with enhanced error handling
async function safeFetchJson(url, loaderKey = null) {
    if (loaderKey) showLoader(loaderKey);
    try {
        const response = await fetch(url, { 
            cache: 'no-cache',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Validate data structure
        if (data === null || data === undefined) return null;
        if (Array.isArray(data) && data.length === 0) return null;
        if (typeof data === 'object' && Object.keys(data).length === 0) return null;
        
        return data;
    } catch (err) {
        console.warn(`Fetch failed for ${url}:`, err);
        return null;
    } finally {
        if (loaderKey) hideLoader(loaderKey);
    }
}

// Export functions for global access
window.EnhancedCharts = {
    drawEnhancedSentimentChart,
    drawEnhancedDifficultyChart,
    drawEnhancedAttendanceChart,
    injectEnhancedStyles
};