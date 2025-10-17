/**
 * Interactive Word Clouds using D3.js
 * This module handles all wordcloud visualizations with animations and hover effects
 */

class InteractiveWordClouds {
    constructor() {
        this.defaultColors = d3.scaleOrdinal(d3.schemeCategory10);
    }

    /**
     * Create an interactive wordcloud
     */
    async createWordCloud(containerId, wordcloudType) {
        console.log(`[WORDCLOUD] Creating wordcloud: ${containerId} (${wordcloudType})`);
        try {
            const response = await fetch(`/api/wordcloud-frequencies/${wordcloudType}`);
            const data = await response.json();
            console.log(`[WORDCLOUD] Received data for ${wordcloudType}:`, data);

            // Clear existing content
            const container = d3.select(`#${containerId}`);
            container.selectAll("*").remove();

            if (!data || data.length === 0) {
                this.showError(containerId, 'No wordcloud data available');
                return;
            }

            // Set dimensions
            const containerElement = document.getElementById(containerId);
            const width = containerElement.offsetWidth || 600;
            const height = 400;

            // Create SVG
            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height);

            // Create tooltip
            const tooltip = d3.select("body").append("div")
                .attr("class", "wordcloud-tooltip")
                .style("opacity", 0)
                .style("position", "absolute")
                .style("background", "rgba(0, 0, 0, 0.8)")
                .style("color", "white")
                .style("padding", "8px 12px")
                .style("border-radius", "4px")
                .style("font-size", "14px")
                .style("pointer-events", "none")
                .style("z-index", "1000");

            // Create wordcloud layout - use fallback if d3.layout.cloud is not available
            if (d3.layout && d3.layout.cloud) {
                const layout = d3.layout.cloud()
                    .size([width, height])
                    .words(data.map(d => ({
                        text: d.text,
                        size: Math.max(12, Math.min(60, d.size)),
                        originalSize: d.size
                    })))
                    .padding(5)
                    .rotate(() => (Math.random() - 0.5) * 60)
                    .font("Impact, Arial, sans-serif")
                    .fontSize(d => d.size)
                    .on("end", (words) => this.drawWordCloud(svg, words, tooltip, wordcloudType));

                layout.start();
            } else {
                // Fallback: create simple positioned wordcloud
                const words = data.map((d, i) => ({
                    text: d.text,
                    size: Math.max(12, Math.min(60, d.size)),
                    originalSize: d.size,
                    x: (Math.random() - 0.5) * width * 0.8,
                    y: (Math.random() - 0.5) * height * 0.8,
                    rotate: (Math.random() - 0.5) * 60
                }));
                
                this.drawWordCloud(svg, words, tooltip, wordcloudType);
            }

        } catch (error) {
            console.error(`Error creating wordcloud ${wordcloudType}:`, error);
            this.showError(containerId, 'Failed to load wordcloud data');
        }
    }

    /**
     * Draw the wordcloud with animations
     */
    drawWordCloud(svg, words, tooltip, wordcloudType) {
        const width = svg.attr("width");
        const height = svg.attr("height");

        // Create group for centering
        const g = svg.append("g")
            .attr("transform", `translate(${width/2},${height/2})`);

        // Color scale based on wordcloud type
        const colorScale = this.getColorScale(wordcloudType);

        // Create text elements
        const text = g.selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", d => `${d.size}px`)
            .style("font-family", "Impact, Arial, sans-serif")
            .style("fill", (d, i) => colorScale(i))
            .style("cursor", "pointer")
            .attr("text-anchor", "middle")
            .attr("transform", d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
            .text(d => d.text)
            .style("opacity", 0);

        // Add animations
        text.transition()
            .delay((d, i) => i * 50)
            .duration(800)
            .ease(d3.easeElastic)
            .style("opacity", 1)
            .style("font-size", d => `${d.size}px`);

        // Add hover effects
        text
            .on("mouseover", function(event, d) {
                // Highlight effect
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style("font-size", `${Math.min(80, d.size * 1.2)}px`)
                    .style("font-weight", "bold")
                    .style("fill", "#ff6b6b");

                // Show tooltip
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                
                tooltip.html(`
                    <strong>${d.text}</strong><br>
                    Frequency: ${d.originalSize}<br>
                    Click for details
                `)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function(event, d) {
                // Remove highlight
                d3.select(this)
                    .transition()
                    .duration(200)
                    .style("font-size", `${d.size}px`)
                    .style("font-weight", "normal")
                    .style("fill", colorScale(words.indexOf(d)));

                // Hide tooltip
                tooltip.transition()
                    .duration(200)
                    .style("opacity", 0);
            })
            .on("click", function(event, d) {
                // Add click animation
                d3.select(this)
                    .transition()
                    .duration(100)
                    .style("font-size", `${Math.min(100, d.size * 1.5)}px`)
                    .transition()
                    .duration(200)
                    .style("font-size", `${d.size}px`);

                // Show detailed info (could be extended)
                alert(`Word: ${d.text}\\nFrequency: ${d.originalSize}\\nRelative size: ${d.size}`);
            });

        // Add export button
        this.addExportButton(svg.node().parentElement, wordcloudType);
    }

    /**
     * Get color scale based on wordcloud type
     */
    getColorScale(wordcloudType) {
        if (wordcloudType.includes('positive')) {
            return d3.scaleOrdinal()
                .range(['#2ecc71', '#27ae60', '#58d68d', '#82e0aa', '#a9dfbf']);
        } else if (wordcloudType.includes('negative')) {
            return d3.scaleOrdinal()
                .range(['#e74c3c', '#c0392b', '#ec7063', '#f1948a', '#f5b7b1']);
        } else {
            return d3.scaleOrdinal()
                .range(['#3498db', '#2980b9', '#5dade2', '#85c1e9', '#aed6f1']);
        }
    }

    /**
     * Add export functionality to wordcloud
     */
    addExportButton(container, wordcloudType) {
        // Remove existing export button
        const existingButton = container.parentElement.querySelector('.export-btn');
        if (existingButton) {
            existingButton.remove();
        }

        // Create export button
        const exportButton = document.createElement('button');
        exportButton.className = 'btn btn-sm btn-outline-secondary export-btn mt-2';
        exportButton.innerHTML = '<i class="fas fa-download"></i> Export Wordcloud';
        exportButton.onclick = () => this.exportWordcloud(container, wordcloudType);

        container.parentElement.appendChild(exportButton);
    }

    /**
     * Export wordcloud as SVG
     */
    exportWordcloud(container, wordcloudType) {
        const svg = container.querySelector('svg');
        if (!svg) return;

        // Create a copy for export
        const svgData = new XMLSerializer().serializeToString(svg);
        const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
        const svgUrl = URL.createObjectURL(svgBlob);
        
        // Download
        const downloadLink = document.createElement('a');
        downloadLink.href = svgUrl;
        downloadLink.download = `${wordcloudType}_${new Date().toISOString().split('T')[0]}.svg`;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        URL.revokeObjectURL(svgUrl);
    }

    /**
     * Show error message
     */
    showError(containerId, message) {
        const container = document.getElementById(containerId);
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
     * Initialize all wordclouds
     */
    async initializeAll() {
        const wordclouds = [
            { containerId: 'wordcloud-positive', type: 'wordcloud_positive' },
            { containerId: 'wordcloud-negative', type: 'wordcloud_negative' },
            { containerId: 'wordcloud-neutral', type: 'wordcloud_neutral' },
            { containerId: 'wordcloud-overall', type: 'wordcloud_overall' }
        ];

        for (const wordcloud of wordclouds) {
            if (document.getElementById(wordcloud.containerId)) {
                try {
                    await this.createWordCloud(wordcloud.containerId, wordcloud.type);
                } catch (error) {
                    console.error(`Error initializing wordcloud ${wordcloud.type}:`, error);
                }
            }
        }
    }
}

// Simple D3 cloud layout implementation if d3-cloud is not available
if (!d3.layout || !d3.layout.cloud) {
    d3.layout = d3.layout || {};
    d3.layout.cloud = function() {
        let size = [256, 256],
            text = cloudText,
            font = cloudFont,
            fontSize = cloudFontSize,
            fontStyle = cloudFontNormal,
            fontWeight = cloudFontNormal,
            rotate = cloudRotate,
            padding = cloudPadding,
            spiral = archimedeanSpiral,
            words = [],
            timeInterval = Infinity,
            event = d3.dispatch("word", "end"),
            timer = null,
            random = Math.random,
            cloud = {},
            canvas = cloudCanvas;

        function cloudText(d) { return d.text; }
        function cloudFont() { return "serif"; }
        function cloudFontNormal() { return "normal"; }
        function cloudFontSize(d) { return Math.sqrt(d.value); }
        function cloudRotate() { return (Math.random() - 0.5) * 60; }
        function cloudPadding() { return 1; }

        function archimedeanSpiral(size) {
            var e = size[0] / size[1];
            return function(t) {
                return [e * (t *= 0.1) * Math.cos(t), t * Math.sin(t)];
            };
        }

        function cloudCanvas() {
            return document.createElement("canvas");
        }

        cloud.words = function(_) {
            return arguments.length ? (words = _, cloud) : words;
        };

        cloud.size = function(_) {
            return arguments.length ? (size = [+_[0], +_[1]], cloud) : size;
        };

        cloud.font = function(_) {
            return arguments.length ? (font = typeof _ === "function" ? _ : cloudConstant(_), cloud) : font;
        };

        cloud.fontStyle = function(_) {
            return arguments.length ? (fontStyle = typeof _ === "function" ? _ : cloudConstant(_), cloud) : fontStyle;
        };

        cloud.fontWeight = function(_) {
            return arguments.length ? (fontWeight = typeof _ === "function" ? _ : cloudConstant(_), cloud) : fontWeight;
        };

        cloud.rotate = function(_) {
            return arguments.length ? (rotate = typeof _ === "function" ? _ : cloudConstant(_), cloud) : rotate;
        };

        cloud.text = function(_) {
            return arguments.length ? (text = typeof _ === "function" ? _ : cloudConstant(_), cloud) : text;
        };

        cloud.spiral = function(_) {
            return arguments.length ? (spiral = spirals[_] || _, cloud) : spiral;
        };

        cloud.fontSize = function(_) {
            return arguments.length ? (fontSize = typeof _ === "function" ? _ : cloudConstant(_), cloud) : fontSize;
        };

        cloud.padding = function(_) {
            return arguments.length ? (padding = typeof _ === "function" ? _ : cloudConstant(_), cloud) : padding;
        };

        cloud.random = function(_) {
            return arguments.length ? (random = _, cloud) : random;
        };

        cloud.on = function() {
            return event.on.apply(event, arguments);
        };

        cloud.start = function() {
            words.forEach(function(d, i) {
                d.x = (size[0] * (random() - 0.5)) / 2;
                d.y = (size[1] * (random() - 0.5)) / 2;
            });
            event.call("end", null, words);
            return cloud;
        };

        return cloud;

        function cloudConstant(_) {
            return function() { return _; };
        }
    };
}

// Initialize wordclouds when DOM is loaded AND all dependencies are available
function initializeWordcloudsWhenReady() {
    // Check if all required libraries are loaded
    if (typeof d3 === 'undefined') {
        console.warn('[WORDCLOUDS] D3 not loaded yet, retrying in 500ms...');
        setTimeout(initializeWordcloudsWhenReady, 500);
        return;
    }
    
    console.log('[WORDCLOUDS] D3 loaded, initializing wordclouds...');
    const wordclouds = new InteractiveWordClouds();
    wordclouds.initializeAll();
}

// Start initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeWordcloudsWhenReady);
} else {
    // DOM is already loaded
    initializeWordcloudsWhenReady();
}

// Export for external use
window.InteractiveWordClouds = InteractiveWordClouds;