document.addEventListener('DOMContentLoaded', () => {
    // --- Get all the necessary HTML elements ---
    const analyzeTextButton = document.getElementById('analyze-text-button');
    const textInput = document.getElementById('text-input');
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const resultsContainer = document.getElementById('results-container');
    const loader = document.getElementById('loader');
    const startAnalysisButton = document.getElementById('startAnalysisButton');
    const clearAllButton = document.getElementById('clearAllButton');
    const filesList = document.getElementById('filesList');
    
    let uploadedFile = null;
    let sentimentChart = null;
    let currentResults = null; // NEW: Variable to store the latest analysis results

    // --- Analyze Pasted Text ---
    analyzeTextButton.addEventListener('click', () => {
        const text = textInput.value;
        if (!text.trim()) {
            alert('Please paste some text to analyze.');
            return;
        }
        performTextAnalysis(text);
    });

    // --- File Upload Logic ---
    uploadZone.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
    uploadZone.addEventListener('dragleave', () => { uploadZone.classList.remove('dragover'); });
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    });
    
    function handleFile(file) {
        filesList.innerHTML = `<div class="file-item">${file.name}</div>`;
        startAnalysisButton.disabled = false;
        clearAllButton.disabled = false;
        uploadedFile = file;
    }
    
    startAnalysisButton.addEventListener('click', () => {
        if (!uploadedFile) {
            alert("Please select a file first.");
            return;
        }
        if (uploadedFile.type === "text/plain") {
            const reader = new FileReader();
            reader.onload = (e) => {
                performTextAnalysis(e.target.result);
            };
            reader.readAsText(uploadedFile);
        } else {
            performFileAnalysis(uploadedFile);
        }
    });

    clearAllButton.addEventListener('click', () => {
        textInput.value = '';
        filesList.innerHTML = '';
        resultsContainer.innerHTML = '';
        uploadedFile = null;
        currentResults = null; // NEW: Clear results
        startAnalysisButton.disabled = true;
        clearAllButton.disabled = true;
        if (sentimentChart) {
            sentimentChart.destroy();
        }
    });

    // --- API Calls ---
    async function performTextAnalysis(text) {
        showLoader();
        try {
            const response = await fetch('http://127.0.0.1:5000/analyze_text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text }),
            });
            const results = await response.json();
            if (!response.ok) throw new Error(results.error || 'HTTP Error');
            displayResults(results);
        } catch (error) {
            displayError(error);
        }
    }

    async function performFileAnalysis(file) {
        showLoader();
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch('http://127.0.0.1:5000/analyze_file', {
                method: 'POST',
                body: formData,
            });
            const results = await response.json();
            if (!response.ok) throw new Error(results.error || 'HTTP Error');
            displayResults(results);
        } catch (error) {
            displayError(error);
        }
    }

    // --- UI Helper Functions ---
    function showLoader() {
        if (sentimentChart) {
            sentimentChart.destroy();
        }
        loader.style.display = 'block';
        resultsContainer.innerHTML = '';
        resultsContainer.appendChild(loader);
    }

    function displayError(error) {
        loader.style.display = 'none';
        resultsContainer.innerHTML = `<div class="error">An error occurred: ${error.message}.</div>`;
    }
    
    function displayResults(results) {
        currentResults = results; // NEW: Store the latest results
        loader.style.display = 'none';
        resultsContainer.innerHTML = `
            <h3>Analysis Results</h3>
            <div class="result-item"><h4>Key Words</h4><img src="${results.wordcloud}" alt="Word Cloud" class="wordcloud-image"></div>
            <div class="chart-container"><h4>Sentiment Distribution</h4><canvas id="sentimentChart"></canvas></div>
            <div class="result-item"><h4>Predicted Topic</h4><p class="topic-badge">${results.topic}</p></div>
            <div class="result-item"><h4>Generated Summary</h4><p class="summary-text">${results.summary}</p></div>
            <div id="report-section"></div>
        `;
        
        const ctx = document.getElementById('sentimentChart').getContext('2d');
        sentimentChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Positive', 'Negative'],
                datasets: [{
                    data: (results.sentiment === 'positive') ? [1, 0] : [0, 1],
                    backgroundColor: ['rgba(46, 204, 113, 0.6)', 'rgba(231, 76, 60, 0.6)'],
                    borderColor: ['rgba(46, 204, 113, 1)', 'rgba(231, 76, 60, 1)'],
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                scales: { x: { display: false, max: 1 }, y: { grid: { display: false } } },
                plugins: { legend: { display: false } }
            }
        });

        // NEW: Create and add the download button
        const reportSection = document.getElementById('report-section');
        reportSection.innerHTML = `<button id="download-report-button" class="btn">Download Report</button>`;
        document.getElementById('download-report-button').addEventListener('click', downloadReport);
    }

    // --- NEW: FUNCTION TO GENERATE AND DOWNLOAD THE REPORT ---
    function downloadReport() {
        if (!currentResults) {
            alert("No results to download.");
            return;
        }

        const reportContent = `
NarrativeNexus Analysis Report
=================================

Predicted Topic: ${currentResults.topic}
Predicted Sentiment: ${currentResults.sentiment}

---------------------------------
Summary
---------------------------------
${currentResults.summary}
        `;

        const blob = new Blob([reportContent.trim()], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'analysis_report.txt';
        document.body.appendChild(a);
a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
});