console.log("🚀 File Upload App Starting...");
class FileUploadApp {
    constructor() {
        this.uploadedFiles = [];
        this.validationRules = {
            allowedTypes: ['.txt', '.csv', '.docx', '.pdf', '.doc', '.ppt'],
            allowedMimeTypes: [
                'text/plain',
                'text/csv',
                'application/csv',
                'text/comma-separated-values',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/pdf',
                'application/msword',
                'application/vnd.ms-powerpoint'
            ],
            maxFileSize: 5 * 1024 * 1024, // 5MB in bytes
            maxTotalSize: 20 * 1024 * 1024, // 20MB in bytes
            maxFiles: 10
        };

        this.fileTypeIcons = {
            'text/plain': '📄',
            'text/csv': '📊',
            'application/csv': '📊',
            'text/comma-separated-values': '📊',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '📝',
            'application/pdf': '📕',
            'application/msword': '📝',
            'application/vnd.ms-powerpoint': '🖥️'
        };

        this.confirmCallback = null;
        this.init();
    }

    init() {
        console.log("🔧 Initializing File Upload App...");

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }

        this.updateUI();
    }

    setupEventListeners() {
        console.log("🎯 Setting up event listeners...");

        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const browseButton = document.getElementById('browseButton');
        const clearAllButton = document.getElementById('clearAllButton');
        const startAnalysisButton = document.getElementById('startAnalysisButton');

        if (!uploadZone || !fileInput || !browseButton) {
            console.error("❌ Required DOM elements not found!");
            return;
        }

        console.log("✅ DOM elements found, binding events...");

        fileInput.addEventListener('change', (e) => {
            console.log("📁 Files selected via input:", e.target.files.length);
            if (e.target.files.length > 0) {
                this.handleFiles(e.target.files);
                e.target.value = '';
            }
        });

        uploadZone.addEventListener('click', () => {
            console.log("🖱️ Upload zone clicked");
            fileInput.click();
        });

        browseButton.addEventListener('click', (e) => {
            console.log("🖱️ Browse button clicked");
            e.stopPropagation();
            fileInput.click();
        });

        uploadZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadZone.addEventListener('drop', (e) => this.handleDrop(e));

        if (clearAllButton) {
            clearAllButton.addEventListener('click', () => {
                this.showConfirmModal(
                    'Clear All Files', 
                    'Are you sure you want to remove all uploaded files?',
                    () => this.clearAllFiles()
                );
            });
        }

        if (startAnalysisButton) {
            startAnalysisButton.addEventListener('click', () => {
                this.startAnalysis();
            });
        }

        this.setupModalEvents();

        console.log("✅ Event listeners setup complete!");
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        const uploadZone = document.getElementById('uploadZone');
        uploadZone.classList.add('dragover');
        console.log("📥 Drag over detected");
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        const uploadZone = document.getElementById('uploadZone');
        if (e.relatedTarget && !uploadZone.contains(e.relatedTarget)) {
            uploadZone.classList.remove('dragover');
            console.log("📤 Drag leave detected");
        } else if (!e.relatedTarget) {
            uploadZone.classList.remove('dragover');
            console.log("📤 Drag leave detected (no related target)");
        }
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();

        const uploadZone = document.getElementById('uploadZone');
        uploadZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        console.log("🎯 Files dropped:", files.length);

        if (files.length > 0) {
            this.handleFiles(files);
        }
    }

    handleFiles(fileList) {
        console.log("📁 Processing files:", fileList.length);
        const files = Array.from(fileList);

        if (this.uploadedFiles.length + files.length > this.validationRules.maxFiles) {
            this.showStatus(`Too many files! Maximum ${this.validationRules.maxFiles} files allowed.`, 'error');
            return;
        }

        files.forEach(file => this.processFile(file));
        this.updateUI();
    }

    processFile(file) {
        console.log("🔍 Processing file:", file.name, file.type, file.size);

        const fileData = {
            id: Date.now() + Math.random(),
            file: file,
            name: file.name,
            size: file.size,
            type: file.type,
            status: 'processing',
            progress: 0,
            error: null
        };

        const validation = this.validateFile(file);
        if (!validation.valid) {
            fileData.status = 'error';
            fileData.error = validation.error;
            console.log("❌ File validation failed:", validation.error);
        } else {
            fileData.status = 'uploading';
            console.log("✅ File validation passed");
        }

        this.uploadedFiles.push(fileData);
        this.updateUI(); // Update UI immediately to show processing state

        if (fileData.status === 'uploading') {
            this.simulateUpload(fileData);
        }
    }

    validateFile(file) {
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.validationRules.allowedTypes.includes(extension)) {
            return {
                valid: false,
                error: `File type ${extension} not supported. Allowed: ${this.validationRules.allowedTypes.join(', ')}`
            };
        }
        
        const fileMime = file.type;
        if (fileMime && !this.validationRules.allowedMimeTypes.includes(fileMime)) {
             console.warn(`Warning: File "${file.name}" has an unexpected MIME type: ${fileMime}`);
        }

        if (file.size > this.validationRules.maxFileSize) {
            return {
                valid: false,
                error: `File too large. Maximum size: ${this.formatFileSize(this.validationRules.maxFileSize)}`
            };
        }

        const totalSize = this.uploadedFiles.reduce((sum, f) => sum + f.size, 0) + file.size;
        if (totalSize > this.validationRules.maxTotalSize) {
            return {
                valid: false,
                error: `Total size limit exceeded. Maximum: ${this.formatFileSize(this.validationRules.maxTotalSize)}`
            };
        }

        return { valid: true };
    }

    simulateUpload(fileData) {
        const duration = 2000 + Math.random() * 3000;
        const steps = 20;
        const stepDuration = duration / steps;

        let currentStep = 0;

        const interval = setInterval(() => {
            currentStep++;
            fileData.progress = Math.min((currentStep / steps) * 100, 100);

            if (currentStep >= steps) {
                fileData.status = 'completed';
                fileData.progress = 100;
                clearInterval(interval);
                console.log("✅ Upload completed:", fileData.name);
                this.showStatus(`File "${fileData.name}" uploaded successfully!`, 'success');
                this.updateUI(); // Final UI update after completion
            }

            this.updateFileDisplay();
        }, stepDuration);
    }
    
    removeFile(fileId) {
        const fileToRemove = this.uploadedFiles.find(file => file.id === fileId);
        if (fileToRemove) {
            this.showConfirmModal(
                'Remove File',
                `Are you sure you want to remove the file "${fileToRemove.name}"?`,
                () => {
                    console.log("🗑️ Removing file:", fileId);
                    this.uploadedFiles = this.uploadedFiles.filter(file => file.id !== fileId);
                    this.updateUI();
                    this.showStatus('File removed successfully', 'info');
                }
            );
        }
    }

    clearAllFiles() {
        console.log("🗑️ Clearing all files");
        this.uploadedFiles = [];
        this.updateUI();
        this.showStatus('All files removed', 'info');
    }

    startAnalysis() {
        this.showConfirmModal(
            'Coming Soon!',
            'Analysis functionality will be implemented in the upcoming weeks!',
            () => {},
            { 
                confirmText: 'OK', 
                showCancel: false 
            }
        );
    }

    updateUI() {
        this.updateFileDisplay();
        this.updateSummary();
        this.updateButtons();
    }
    
    updateFileDisplay() {
        const filesList = document.getElementById('filesList');
        if (!filesList) return;

        if (this.uploadedFiles.length === 0) {
            filesList.innerHTML = '';
            return;
        }

        filesList.innerHTML = this.uploadedFiles.map(file => `
            <div class="file-item" data-file-id="${file.id}">
                <!-- BUG FIX: Changed class. to class= -->
                <div class="file-info">
                    <div class="file-icon">${this.getFileIcon(file)}</div>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <div class="file-meta">${this.formatFileSize(file.size)} • ${file.type || 'Unknown'}</div>
                        ${file.status === 'uploading' ? `
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${file.progress}%"></div>
                            </div>
                        ` : ''}
                        ${file.error ? `<div class="error-message">${file.error}</div>` : ''}
                    </div>
                </div>
                <div class="file-status">
                    <span class="status-badge status-${file.status}">
                        ${this.getStatusText(file.status)}
                    </span>
                    <div class="file-actions">
                        <button class="btn btn--danger btn-small" onclick="app.removeFile(${file.id})">
                            🗑️ Remove
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateSummary() {
        const totalFilesEl = document.getElementById('totalFiles');
        const totalSizeEl = document.getElementById('totalSize');

        if (totalFilesEl) {
            totalFilesEl.textContent = `${this.uploadedFiles.length} files`;
        }

        if (totalSizeEl) {
            const totalSize = this.uploadedFiles.reduce((sum, file) => sum + file.size, 0);
            totalSizeEl.textContent = this.formatFileSize(totalSize);
        }
    }

    updateButtons() {
        const clearAllButton = document.getElementById('clearAllButton');
        const startAnalysisButton = document.getElementById('startAnalysisButton');

        const hasFiles = this.uploadedFiles.length > 0;
        const hasValidFiles = this.uploadedFiles.some(f => f.status === 'completed');

        if (clearAllButton) {
            clearAllButton.disabled = !hasFiles;
        }

        if (startAnalysisButton) {
            startAnalysisButton.disabled = !hasValidFiles;
        }
    }

    getFileIcon(file) {
        return this.fileTypeIcons[file.type] || '📄';
    }

    getStatusText(status) {
        const statusTexts = {
            'processing': '⏳ Processing',
            'uploading': '📤 Uploading',
            'completed': '✅ Completed',
            'error': '❌ Error'
        };
        return statusTexts[status] || status;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 bytes';
        const k = 1024;
        const sizes = ['bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    showStatus(message, type = 'info') {
        const statusMessage = document.getElementById('statusMessage');
        if (!statusMessage) return;

        statusMessage.innerHTML = `<p class="status-${type}">${message}</p>`;

        if (type !== 'error') {
            setTimeout(() => {
                const currentMessage = statusMessage.querySelector('p');
                if (currentMessage && currentMessage.textContent === message) {
                   statusMessage.innerHTML = '<p>No files uploaded yet. Select files to get started!</p>';
                }
            }, 5000);
        }
    }

    showConfirmModal(title, message, callback, options = {}) {
        const modal = document.getElementById('confirmModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalMessage = document.getElementById('modalMessage');
        const modalCancel = document.getElementById('modalCancel');
        const modalConfirm = document.getElementById('modalConfirm');

        if (!modal || !modalTitle || !modalMessage) return;

        modalTitle.textContent = title;
        modalMessage.textContent = message;

        modalConfirm.textContent = options.confirmText || 'Confirm';
        
        if (options.showCancel === false) {
            modalCancel.style.display = 'none';
        } else {
            modalCancel.style.display = 'inline-block';
            modalCancel.textContent = options.cancelText || 'Cancel';
        }

        modal.style.display = 'flex';

        this.confirmCallback = callback;
    }

    hideModal() {
        const modal = document.getElementById('confirmModal');
        if (modal) {
            modal.style.display = 'none';
        }
        this.confirmCallback = null;
    }

    setupModalEvents() {
        const modalCancel = document.getElementById('modalCancel');
        const modalConfirm = document.getElementById('modalConfirm');
        const modal = document.getElementById('confirmModal');

        if (modalCancel) {
            modalCancel.addEventListener('click', () => this.hideModal());
        }

        if (modalConfirm) {
            modalConfirm.addEventListener('click', () => {
                if (this.confirmCallback) {
                    this.confirmCallback();
                }
                this.hideModal();
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal();
                }
            });
        }
    }
}

console.log("📦 Creating File Upload App instance...");
const app = new FileUploadApp();

window.app = app;

console.log("🎉 File Upload App initialized successfully!");
