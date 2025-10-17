// Interactive Animated Word Cloud with D3.js
// ===========================================

class InteractiveWordCloud {
    constructor(container, options = {}) {
        this.container = d3.select(container);
        this.options = {
            width: options.width || 800,
            height: options.height || 400,
            fontSizeRange: [12, 48],
            colorSchemes: {
                default: ['#4361ee', '#3f37c9', '#7209b7', '#f72585', '#4cc9f0'],
                vibrant: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'],
                warm: ['#ff7675', '#fd79a8', '#fdcb6e', '#6c5ce7', '#74b9ff'],
                cool: ['#00cec9', '#55a3ff', '#5f27cd', '#00d2d3', '#0984e3']
            },
            animationDuration: 1500,
            ...options
        };
        this.words = [];
        this.svg = null;
        this.layout = null;
        this.isAnimating = false;
    }

    async loadWordData(dataUrl) {
        try {
            const response = await fetch(dataUrl);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            // Handle different data formats
            if (Array.isArray(data)) {
                // Format: [{word: "text", weight: 0.8}]
                this.words = data.map(item => ({
                    text: item.word || item.text,
                    size: Math.max(this.options.fontSizeRange[0], 
                           Math.min(this.options.fontSizeRange[1], 
                           (item.weight || item.size || 0.5) * this.options.fontSizeRange[1]))
                }));
            } else if (typeof data === 'object') {
                // Format: {word1: frequency, word2: frequency}
                const maxFreq = Math.max(...Object.values(data));
                this.words = Object.entries(data).map(([word, freq]) => ({
                    text: word,
                    size: Math.max(this.options.fontSizeRange[0],
                           Math.min(this.options.fontSizeRange[1],
                           (freq / maxFreq) * this.options.fontSizeRange[1]))
                }));
            }
            
            // Filter out empty words and sort by size
            this.words = this.words
                .filter(d => d.text && d.text.length > 2)
                .sort((a, b) => b.size - a.size)
                .slice(0, 100); // Limit to top 100 words
            
            return this.words.length > 0;
        } catch (error) {
            console.error('Error loading word data:', error);
            return false;
        }
    }

    initializeLayout() {
        // Clear existing content
        this.container.selectAll('*').remove();
        
        // Create SVG
        this.svg = this.container
            .append('svg')
            .attr('width', this.options.width)
            .attr('height', this.options.height)
            .style('background', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
            .style('border-radius', '12px')
            .style('overflow', 'hidden');

        // Add defs for gradients and filters
        const defs = this.svg.append('defs');
        
        // Create gradient definitions
        Object.keys(this.options.colorSchemes).forEach((scheme, i) => {
            const gradient = defs.append('linearGradient')
                .attr('id', `gradient-${scheme}`)
                .attr('x1', '0%').attr('y1', '0%')
                .attr('x2', '100%').attr('y2', '100%');
            
            this.options.colorSchemes[scheme].forEach((color, j) => {
                gradient.append('stop')
                    .attr('offset', `${(j / (this.options.colorSchemes[scheme].length - 1)) * 100}%`)
                    .attr('stop-color', color);
            });
        });

        // Add glow filter
        const filter = defs.append('filter')
            .attr('id', 'glow')
            .attr('x', '-20%')
            .attr('y', '-20%')
            .attr('width', '140%')
            .attr('height', '140%');

        filter.append('feGaussianBlur')
            .attr('stdDeviation', '3')
            .attr('result', 'coloredBlur');

        const feMerge = filter.append('feMerge');
        feMerge.append('feMergeNode').attr('in', 'coloredBlur');
        feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

        // Create main group for words
        this.wordsGroup = this.svg.append('g')
            .attr('transform', `translate(${this.options.width / 2}, ${this.options.height / 2})`);

        // Add background particles
        this.createParticleSystem();
    }

    createParticleSystem() {
        const particleData = d3.range(30).map(() => ({
            x: Math.random() * this.options.width,
            y: Math.random() * this.options.height,
            r: Math.random() * 3 + 1,
            dx: (Math.random() - 0.5) * 2,
            dy: (Math.random() - 0.5) * 2,
            opacity: Math.random() * 0.5 + 0.1
        }));

        const particles = this.svg.append('g')
            .attr('class', 'particles')
            .selectAll('circle')
            .data(particleData)
            .enter().append('circle')
            .attr('cx', d => d.x)
            .attr('cy', d => d.y)
            .attr('r', d => d.r)
            .attr('fill', '#ffffff')
            .attr('opacity', d => d.opacity);

        // Animate particles
        const animateParticles = () => {
            particles
                .transition()
                .duration(4000)
                .ease(d3.easeLinear)
                .attr('cx', d => {
                    d.x += d.dx;
                    if (d.x < 0 || d.x > this.options.width) {
                        d.dx = -d.dx;
                        d.x = Math.max(0, Math.min(this.options.width, d.x));
                    }
                    return d.x;
                })
                .attr('cy', d => {
                    d.y += d.dy;
                    if (d.y < 0 || d.y > this.options.height) {
                        d.dy = -d.dy;
                        d.y = Math.max(0, Math.min(this.options.height, d.y));
                    }
                    return d.y;
                })
                .on('end', animateParticles);
        };
        
        animateParticles();
    }

    calculateLayout() {
        // Use a simple spiral layout for positioning
        const spiral = (size, i) => {
            const angle = i * 0.5;
            const radius = Math.sqrt(i) * 5;
            return {
                x: radius * Math.cos(angle),
                y: radius * Math.sin(angle)
            };
        };

        this.words.forEach((word, i) => {
            const pos = spiral(word.size, i);
            word.x = pos.x;
            word.y = pos.y;
            word.rotate = Math.random() * 60 - 30; // Random rotation between -30 and 30 degrees
        });
    }

    render() {
        this.calculateLayout();
        
        const colorScheme = this.options.colorSchemes.default;
        
        // Bind data to text elements
        const words = this.wordsGroup
            .selectAll('.word')
            .data(this.words, d => d.text);

        // Remove old words
        words.exit()
            .transition()
            .duration(500)
            .style('opacity', 0)
            .attr('transform', d => `translate(${d.x}, ${d.y}) scale(0) rotate(${d.rotate})`)
            .remove();

        // Add new words
        const wordsEnter = words.enter()
            .append('text')
            .attr('class', 'word')
            .attr('text-anchor', 'middle')
            .attr('font-family', 'Poppins, sans-serif')
            .attr('font-weight', 'bold')
            .style('cursor', 'pointer')
            .style('opacity', 0)
            .attr('transform', d => `translate(0, 0) scale(0) rotate(0)`)
            .text(d => d.text);

        // Merge enter and update selections
        const wordsUpdate = wordsEnter.merge(words);

        // Apply styling and animations
        wordsUpdate
            .attr('font-size', d => d.size)
            .attr('fill', (d, i) => colorScheme[i % colorScheme.length])
            .attr('filter', 'url(#glow)')
            .transition()
            .duration(this.options.animationDuration)
            .delay((d, i) => i * 50)
            .ease(d3.easeBounceOut)
            .style('opacity', 1)
            .attr('transform', d => `translate(${d.x}, ${d.y}) scale(1) rotate(${d.rotate}deg)`);

        // Add interactive behaviors
        this.addInteractions(wordsUpdate);
    }

    addInteractions(words) {
        const self = this;
        
        words
            .on('mouseenter', function(event, d) {
                const element = d3.select(this);
                
                // Grow and glow effect
                element
                    .transition()
                    .duration(200)
                    .attr('font-size', d.size * 1.3)
                    .style('opacity', 1)
                    .attr('filter', 'url(#glow)');
                
                // Create tooltip
                const tooltip = self.svg.append('g')
                    .attr('class', 'tooltip')
                    .style('opacity', 0);
                
                const bbox = element.node().getBBox();
                const tooltipText = `"${d.text}" - Weight: ${Math.round((d.size / self.options.fontSizeRange[1]) * 100)}%`;
                
                const rect = tooltip.append('rect')
                    .attr('x', d.x - tooltipText.length * 3)
                    .attr('y', d.y - d.size / 2 - 25)
                    .attr('width', tooltipText.length * 6)
                    .attr('height', 20)
                    .attr('rx', 10)
                    .attr('fill', 'rgba(0, 0, 0, 0.8)');
                
                tooltip.append('text')
                    .attr('x', d.x)
                    .attr('y', d.y - d.size / 2 - 10)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#ffffff')
                    .attr('font-size', '12px')
                    .attr('font-family', 'Poppins, sans-serif')
                    .text(tooltipText);
                
                tooltip
                    .transition()
                    .duration(200)
                    .style('opacity', 1);
            })
            .on('mouseleave', function(event, d) {
                const element = d3.select(this);
                
                // Return to normal size
                element
                    .transition()
                    .duration(200)
                    .attr('font-size', d.size)
                    .style('opacity', 0.9);
                
                // Remove tooltip
                self.svg.selectAll('.tooltip')
                    .transition()
                    .duration(200)
                    .style('opacity', 0)
                    .remove();
            })
            .on('click', function(event, d) {
                // Click animation - create expanding circle
                const clickEffect = self.svg.append('circle')
                    .attr('cx', d.x + self.options.width / 2)
                    .attr('cy', d.y + self.options.height / 2)
                    .attr('r', 0)
                    .attr('fill', 'none')
                    .attr('stroke', '#ffffff')
                    .attr('stroke-width', 3)
                    .style('opacity', 1);
                
                clickEffect
                    .transition()
                    .duration(600)
                    .attr('r', 50)
                    .style('opacity', 0)
                    .on('end', () => clickEffect.remove());
                
                // Trigger custom event
                self.container.node().dispatchEvent(new CustomEvent('wordClick', {
                    detail: { word: d.text, size: d.size }
                }));
            });
    }

    async createFromData(dataUrl, containerSelector = null) {
        if (containerSelector) {
            this.container = d3.select(containerSelector);
        }
        
        const hasData = await this.loadWordData(dataUrl);
        if (!hasData) {
            this.showNoDataMessage();
            return;
        }
        
        this.initializeLayout();
        this.render();
    }

    showNoDataMessage() {
        this.container.selectAll('*').remove();
        this.container
            .append('div')
            .attr('class', 'no-wordcloud-data')
            .style('display', 'flex')
            .style('align-items', 'center')
            .style('justify-content', 'center')
            .style('height', this.options.height + 'px')
            .style('background', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
            .style('border-radius', '12px')
            .style('color', '#ffffff')
            .style('font-family', 'Poppins, sans-serif')
            .style('font-size', '16px')
            .text('No word cloud data available');
    }

    // Method to update with new data
    async update(dataUrl) {
        const hasData = await this.loadWordData(dataUrl);
        if (hasData) {
            this.render();
        }
    }

    // Method to change color scheme
    setColorScheme(schemeName) {
        if (this.options.colorSchemes[schemeName]) {
            const colorScheme = this.options.colorSchemes[schemeName];
            this.wordsGroup.selectAll('.word')
                .transition()
                .duration(1000)
                .attr('fill', (d, i) => colorScheme[i % colorScheme.length]);
        }
    }

    // Method to resize the wordcloud
    resize(width, height) {
        this.options.width = width;
        this.options.height = height;
        
        if (this.svg) {
            this.svg
                .attr('width', width)
                .attr('height', height);
            
            this.wordsGroup
                .attr('transform', `translate(${width / 2}, ${height / 2})`);
            
            this.calculateLayout();
            this.render();
        }
    }
}

// Utility function to create wordclouds for different categories
async function createWordClouds() {
    const wordcloudConfigs = [
        {
            container: '#wordcloud-overall',
            dataUrl: '/api/wordcloud-data/wordcloud_overall',
            title: 'Overall Word Cloud'
        },
        {
            container: '#wordcloud-positive',
            dataUrl: '/api/wordcloud-data/wordcloud_positive',
            title: 'Positive Sentiment Words'
        },
        {
            container: '#wordcloud-negative',
            dataUrl: '/api/wordcloud-data/wordcloud_negative',
            title: 'Negative Sentiment Words'
        }
    ];

    for (const config of wordcloudConfigs) {
        const container = document.querySelector(config.container);
        if (container) {
            const wordcloud = new InteractiveWordCloud(config.container, {
                width: container.offsetWidth || 800,
                height: 320
            });
            
            // Add event listener for word clicks
            container.addEventListener('wordClick', (event) => {
                console.log(`Clicked word: ${event.detail.word} in ${config.title}`);
                // You can add custom behavior here, like searching for the word
            });
            
            await wordcloud.createFromData(config.dataUrl);
        }
    }
}

// Enhanced wordcloud creation function that replaces static images
async function replaceStaticWordClouds() {
    // Find all wordcloud images and replace them with interactive versions
    const wordcloudImages = document.querySelectorAll('img[alt*="wordcloud"], img[src*="wordcloud"]');
    
    for (const img of wordcloudImages) {
        const altText = img.alt || img.src;
        let dataUrl = '';
        
        // Determine the data URL based on the image name
        if (altText.includes('positive')) {
            dataUrl = '/api/wordcloud-data/wordcloud_positive';
        } else if (altText.includes('negative')) {
            dataUrl = '/api/wordcloud-data/wordcloud_negative';
        } else {
            dataUrl = '/api/wordcloud-data/wordcloud_overall';
        }
        
        // Create a container to replace the image
        const container = document.createElement('div');
        container.id = `interactive-wordcloud-${Date.now()}`;
        container.style.width = '100%';
        container.style.height = '320px';
        
        // Replace the image with the container
        img.parentNode.replaceChild(container, img);
        
        // Create the interactive wordcloud
        const wordcloud = new InteractiveWordCloud(`#${container.id}`, {
            width: container.offsetWidth || 800,
            height: 320
        });
        
        await wordcloud.createFromData(dataUrl);
    }
}

// Function to create an interactive word cloud - defined globally for backward compatibility
function createWordcloud(containerId, dataUrl, colorInterpolator = d3.interpolateBlues) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Use the new InteractiveWordCloud class
    const wordcloud = new InteractiveWordCloud(`#${containerId}`, {
        width: container.offsetWidth || 800,
        height: 400
    });
    
    wordcloud.createFromData(dataUrl);
}

// Export for global access
window.InteractiveWordCloud = InteractiveWordCloud;
window.createWordClouds = createWordClouds;
window.replaceStaticWordClouds = replaceStaticWordClouds;
window.createWordcloud = createWordcloud; // Backward compatibility
                            .style("stroke-width", 1)
                            .style("filter", "url(#glow)");
                            
                        // Show tooltip with word weight
                        const tooltip = d3.select(container)
                            .append("div")
                            .attr("class", "wordcloud-tooltip")
                            .style("position", "absolute")
                            .style("background", "rgba(0,0,0,0.8)")
                            .style("color", "white")
                            .style("padding", "5px 10px")
                            .style("border-radius", "4px")
                            .style("font-size", "12px")
                            .style("pointer-events", "none")
                            .style("opacity", 0)
                            .style("z-index", 1000)
                            .html(`<strong>${d.text}</strong>: ${d.weight.toFixed(2)}`);
                            
                        const rect = container.getBoundingClientRect();
                        const x = event.pageX - rect.left;
                        const y = event.pageY - rect.top;
                        
                        tooltip.style("left", `${x + 10}px`)
                            .style("top", `${y - 25}px`)
                            .transition()
                            .duration(200)
                            .style("opacity", 1);
                    })
                    .on("mouseout", function(event, d) {
                        d3.select(this).select("text")
                            .transition()
                            .duration(200)
                            .style("font-size", `${d.size}px`)
                            .style("font-weight", "normal")
                            .style("fill", d.color)
                            .style("stroke-width", 0)
                            .style("filter", "none");
                            
                        // Remove tooltip
                        d3.select(container).selectAll(".wordcloud-tooltip")
                            .transition()
                            .duration(200)
                            .style("opacity", 0)
                            .remove();
                    })
                    .on("click", function(event, d) {
                        // Add click animation
                        d3.select(this)
                            .transition()
                            .duration(100)
                            .attr("transform", `translate(${d.x-2},${d.y-2}) rotate(${d.rotate})`)
                            .transition()
                            .duration(100)
                            .attr("transform", `translate(${d.x},${d.y}) rotate(${d.rotate})`);
                    });
                }
            })
            .catch(error => {
                console.error(`Error loading wordcloud data for ${containerId}:`, error);
                container.innerHTML = `<div class="error-message">Failed to load wordcloud data</div>`;
            });
    }
    
    // Create different wordclouds with different color schemes
    createWordcloud('wordcloud-overall', '/api/wordcloud-data/overall', d3.interpolateViridis);
    createWordcloud('wordcloud-positive', '/api/wordcloud-data/positive', d3.interpolateBlues);
    createWordcloud('wordcloud-neutral', '/api/wordcloud-data/neutral', d3.interpolateGreens);
    createWordcloud('wordcloud-negative', '/api/wordcloud-data/negative', d3.interpolateReds);
    
    // Create topic-specific wordclouds if they exist
document.addEventListener('DOMContentLoaded', function() {
    for (let i = 1; i <= 6; i++) {
        const topicElement = document.getElementById(`wordcloud-topic-${i}`);
        if (topicElement) {
            createWordcloud(`wordcloud-topic-${i}`, `/api/wordcloud-data/topic/${i}`, d3.interpolatePlasma);
        }
    }
});