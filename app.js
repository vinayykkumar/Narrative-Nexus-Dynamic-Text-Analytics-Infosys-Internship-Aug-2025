class DocumentAnalyzer {
    constructor() {
        this.files = [];
        this.analysisResults = null;
        this.maxFileSize = 5 * 1024 * 1024; // 5MB
        this.maxTotalSize = 20 * 1024 * 1024; // 20MB
        this.supportedTypes = ['txt', 'docx', 'pdf', 'csv', 'doc'];
        this.sentimentChart = null;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeAnimations();
    }

    initializeElements() {
        // Upload elements
        this.uploadZone = document.getElementById('uploadZone');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.fileInput = document.getElementById('fileInput');
        this.uploadOverlay = document.getElementById('uploadOverlay');
        
        // Text input elements
        this.textInput = document.getElementById('textInput');
        this.analyzeTextBtn = document.getElementById('analyzeTextBtn');
        this.clearTextBtn = document.getElementById('clearTextBtn');
        this.charCount = document.getElementById('charCount');
        
        // File list elements
        this.fileListSection = document.getElementById('fileListSection');
        this.fileList = document.getElementById('fileList');
        this.clearAllBtn = document.getElementById('clearAllBtn');
        this.startAnalysisBtn = document.getElementById('startAnalysisBtn');
        
        // Progress elements
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.currentFile = document.getElementById('currentFile');
        this.progressPercentage = document.getElementById('progressPercentage');
        
        // Results elements
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsGrid = document.getElementById('resultsGrid');
        this.exportBtn = document.getElementById('exportBtn');
        this.copyResultsBtn = document.getElementById('copyResultsBtn');
        
        // Loading overlay
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // Toasts
        this.successToast = document.getElementById('successToast');
        this.errorToast = document.getElementById('errorToast');
        this.toastMessage = document.getElementById('toastMessage');
        this.errorMessage = document.getElementById('errorMessage');
    }

    bindEvents() {
        // File upload events
        if (this.uploadZone && this.fileInput) {
            this.uploadZone.addEventListener('click', () => this.fileInput.click());
            this.uploadZone.addEventListener('dragover', (e) => this.handleDragOver(e));
            this.uploadZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            this.uploadZone.addEventListener('drop', (e) => this.handleDrop(e));
        }
        
        if (this.uploadBtn) {
            this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        }
        
        if (this.fileInput) {
            this.fileInput.addEventListener('change', () => this.handleFileSelect());
        }
        
        // Text input events
        if (this.analyzeTextBtn) {
            this.analyzeTextBtn.addEventListener('click', () => this.analyzePastedText());
        }
        
        if (this.clearTextBtn) {
            this.clearTextBtn.addEventListener('click', () => this.clearTextInput());
        }
        
        if (this.textInput && this.charCount) {
            this.textInput.addEventListener('input', () => this.updateCharCount());
        }
        
        // Control buttons
        if (this.clearAllBtn) {
            this.clearAllBtn.addEventListener('click', () => this.clearAll());
        }
        
        if (this.startAnalysisBtn) {
            this.startAnalysisBtn.addEventListener('click', () => this.analyzeFiles());
        }
        
        if (this.exportBtn) {
            this.exportBtn.addEventListener('click', () => this.exportResults());
        }
        
        if (this.copyResultsBtn) {
            this.copyResultsBtn.addEventListener('click', () => this.copyResults());
        }
        
        // Toast close buttons
        const toastCloseButtons = document.querySelectorAll('.toast-close');
        toastCloseButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.closeToast(e.target.closest('.toast')));
        });
    }

    initializeAnimations() {
        // Add any initialization animations here
        if (this.uploadZone) {
            this.uploadZone.style.transition = 'all 0.3s ease';
        }
    }

    // ======================
    // FILE HANDLING METHODS
    // ======================

    handleDragOver(e) {
        e.preventDefault();
        this.uploadZone.classList.add('drag-active');
        if (this.uploadOverlay) {
            this.uploadOverlay.classList.remove('hidden');
        }
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadZone.classList.remove('drag-active');
        if (this.uploadOverlay) {
            this.uploadOverlay.classList.add('hidden');
        }
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadZone.classList.remove('drag-active');
        if (this.uploadOverlay) {
            this.uploadOverlay.classList.add('hidden');
        }
        
        const files = Array.from(e.dataTransfer.files);
        files.forEach(file => this.addFile(file));
    }

    handleFileSelect() {
        if (this.fileInput.files.length > 0) {
            Array.from(this.fileInput.files).forEach(file => this.addFile(file));
            this.fileInput.value = ''; // Reset input
        }
    }

    addFile(file) {
        if (!this.validateFile(file)) {
            return;
        }

        // Check for duplicates
        if (this.files.some(f => f.name === file.name && f.size === file.size)) {
            this.showToast('File already added', 'error');
            return;
        }

        this.files.push(file);
        this.renderFileList();
        this.updateUI();
        this.showToast(`Added ${file.name}`, 'success');
    }

    validateFile(file) {
        const extension = file.name.split('.').pop().toLowerCase();
        
        if (!this.supportedTypes.includes(extension)) {
            this.showToast(`Unsupported file type: .${extension}`, 'error');
            return false;
        }
        
        if (file.size > this.maxFileSize) {
            this.showToast('File size exceeds 5MB limit', 'error');
            return false;
        }
        
        const totalSize = this.files.reduce((sum, f) => sum + f.size, 0) + file.size;
        if (totalSize > this.maxTotalSize) {
            this.showToast('Total size would exceed 20MB limit', 'error');
            return false;
        }
        
        return true;
    }

    removeFile(index) {
        const fileName = this.files[index].name;
        this.files.splice(index, 1);
        this.renderFileList();
        this.updateUI();
        this.showToast(`Removed ${fileName}`, 'success');
    }

    renderFileList() {
        if (!this.fileList) return;
        
        this.fileList.innerHTML = this.files.map((file, index) => `
            <div class="file-item" data-index="${index}">
                <div class="file-info">
                    <div class="file-icon">${this.getFileIcon(file.name)}</div>
                    <div class="file-details">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button class="file-remove" onclick="analyzer.removeFile(${index})">
                    <span>×</span>
                </button>
            </div>
        `).join('');
    }

    // ======================
    // ANALYSIS METHODS
    // ======================

    async analyzePastedText() {
        const text = this.textInput.value.trim();
        if (!text) {
            this.showToast('Please enter some text to analyze', 'error');
            return;
        }

        try {
            this.showLoading('Analyzing text...');
            const results = await this.performTextAnalysis(text);
            this.analysisResults = results;
            this.displayResults(results);
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showToast(`Analysis failed: ${error.message}`, 'error');
        }
    }

    async analyzeFiles() {
        if (this.files.length === 0) {
            this.showToast('Please select files to analyze', 'error');
            return;
        }

        try {
            this.showLoading('Analyzing files...');
            
            // For now, analyze the first file (you can modify to handle multiple files)
            const file = this.files[0];
            const results = await this.performFileAnalysis(file);
            this.analysisResults = results;
            this.displayResults(results);
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showToast(`Analysis failed: ${error.message}`, 'error');
        }
    }

    // ======================
    // API COMMUNICATION
    // ======================

    async performTextAnalysis(text) {
        try {
            const response = await fetch('http://127.0.0.1:5000/analyze_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Text analysis error:', error);
            throw error;
        }
    }

    async performFileAnalysis(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('http://127.0.0.1:5000/analyze_file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('File analysis error:', error);
            throw error;
        }
    }

    // ======================
    // RESULTS DISPLAY
    // ======================

    displayResults(results) {
        if (!this.resultsGrid) return;

        // Show results section
        if (this.resultsSection) {
            this.resultsSection.classList.remove('hidden');
        }

        // Create result cards
        this.resultsGrid.innerHTML = `
            <div class="result-card topic-card">
                <div class="result-header">
                    <div class="result-icon"><h3>🎯 Topic Analysis</h3></div>
                </div>
                <div class="result-content">
                    <div class="topic-badge">${results.topic}</div>
                </div>
            </div>

            <div class="result-card sentiment-card">
                <div class="result-header">
                    <div class="result-icon"><h3>${results.sentiment.toLowerCase() === 'positive' ? '😊' : '😔'} Sentiment Analysis</h3></div>
                </div>
                <div class="result-content">
                    <div class="sentiment-badge sentiment-${results.sentiment.toLowerCase()}">
                        ${results.sentiment}
                    </div>
                    <div class="sentiment-chart">
                        ${this.createSentimentChart(results.sentiment)}
                    </div>
                </div>
            </div>

            <div class="result-card summary-card">
                <div class="result-header">
                    <div class="result-icon"><h3>📄 Summary</h3></div>
                </div>
                <div class="result-content">
                    <p class="summary-text">${results.summary}</p>
                </div>
            </div>

            <div class="result-card wordcloud-card">
                <div class="result-header">
                    <div class="result-icon"><h3>☁️ Word Cloud</h3></div>
                </div>
                <div class="result-content">
                    <div class="wordcloud-container">
                        <img src="${results.wordcloud}" alt="Word Cloud" class="wordcloud-image" />
                    </div>
                </div>
            </div>
        `;

        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
        this.showToast('Analysis completed successfully!', 'success');
    }

    createSentimentChart(sentiment) {
        const isPositive = sentiment.toLowerCase() === 'positive';
        const positiveWidth = isPositive ? 100 : 0;
        const negativeWidth = isPositive ? 0 : 100;
        
        return `
            <div class="sentiment-bars">
                <div class="sentiment-bar">
                    <span class="sentiment-label">Positive</span>
                    <div class="sentiment-bar-bg">
                        <div class="sentiment-bar-fill positive" style="width: ${positiveWidth}%"></div>
                    </div>
                    <span class="sentiment-value">${positiveWidth}%</span>
                </div>
                <div class="sentiment-bar">
                    <span class="sentiment-label">Negative</span>
                    <div class="sentiment-bar-bg">
                        <div class="sentiment-bar-fill negative" style="width: ${negativeWidth}%"></div>
                    </div>
                    <span class="sentiment-value">${negativeWidth}%</span>
                </div>
            </div>
        `;
    }

    // ======================
    // UTILITY METHODS
    // ======================

    showLoading(message = 'Processing...') {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('hidden');
            const loadingText = this.loadingOverlay.querySelector('.loading-text');
            if (loadingText) {
                loadingText.textContent = message;
            }
        }
    }

    hideLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.add('hidden');
        }
    }

    showToast(message, type = 'success') {
        const toast = type === 'success' ? this.successToast : this.errorToast;
        const messageElement = type === 'success' ? this.toastMessage : this.errorMessage;
        
        if (toast && messageElement) {
            messageElement.textContent = message;
            toast.classList.remove('hidden');
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                this.closeToast(toast);
            }, 3000);
        }
    }

    closeToast(toast) {
        if (toast) {
            toast.classList.add('hidden');
        }
    }

    updateCharCount() {
        if (this.textInput && this.charCount) {
            const count = this.textInput.value.length;
            this.charCount.textContent = count;
        }
    }

    clearTextInput() {
        if (this.textInput) {
            this.textInput.value = '';
            this.updateCharCount();
        }
    }

    updateUI() {
        // Update file count and enable/disable buttons
        const hasFiles = this.files.length > 0;
        const hasText = this.textInput && this.textInput.value.trim().length > 0;
        
        if (this.clearAllBtn) {
            this.clearAllBtn.disabled = !hasFiles;
        }

        if (this.startAnalysisBtn) {
            this.startAnalysisBtn.disabled = !hasFiles;
        }
        
        if (this.fileListSection) {
            if (hasFiles) {
                this.fileListSection.classList.remove('hidden');
            } else {
                this.fileListSection.classList.add('hidden');
            }
        }
    }

    clearAll() {
        this.files = [];
        this.analysisResults = null;
        
        if (this.textInput) {
            this.textInput.value = '';
        }
        
        this.renderFileList();
        this.updateUI();
        this.updateCharCount();
        
        // Hide results
        if (this.resultsSection) {
            this.resultsSection.classList.add('hidden');
        }
        
        this.showToast('Cleared all data', 'success');
    }

    exportResults() {
        if (!this.analysisResults) {
            this.showToast('No results to export', 'error');
            return;
        }

        // Export as TXT format instead of JSON
        const exportText = `Analysis Results Report
=======================

Generated on: ${new Date().toLocaleString()}

Topic Analysis
--------------
${this.analysisResults.topic}

Sentiment Analysis
------------------
${this.analysisResults.sentiment}

Summary
-------
${this.analysisResults.summary}

=======================
Document Analyzer Pro
=======================`;

        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis-results-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('Results exported as TXT file', 'success');
    }

    copyResults() {
        if (!this.analysisResults) {
            this.showToast('No results to copy', 'error');
            return;
        }

        const text = `Analysis Results:
Topic: ${this.analysisResults.topic}
Sentiment: ${this.analysisResults.sentiment}
Summary: ${this.analysisResults.summary}`;

        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Results copied to clipboard', 'success');
        }).catch(() => {
            this.showToast('Failed to copy results', 'error');
        });
    }

    // Helper methods
    getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const icons = {
            'txt': '📄',
            'docx': '📝',
            'doc': '📝',
            'pdf': '📕',
            'csv': '📊'
        };
        return icons[extension] || '📄';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.analyzer = new DocumentAnalyzer();
    
    // Add click handler for file analysis button that might be created dynamically
    document.addEventListener('click', (e) => {
        if (e.target.matches('#startAnalysisBtn, .analyze-files-btn')) {
            e.preventDefault();
            window.analyzer.analyzeFiles();
        }
    });
});