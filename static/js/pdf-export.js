// PDF Export functionality using html2pdf.js
document.addEventListener('DOMContentLoaded', function() {
    const exportButton = document.getElementById('export-pdf-btn');
    
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            // Show loading indicator
            const loadingElement = document.createElement('div');
            loadingElement.className = 'loading-overlay';
            loadingElement.innerHTML = `
                <div class="spinner"></div>
                <p>Generating PDF...</p>
            `;
            document.body.appendChild(loadingElement);
            
            // Get the content to export
            const contentToExport = document.getElementById('export-content');
            
            // Configure PDF options
            const options = {
                margin: 10,
                filename: 'data-analysis-report.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true, logging: false },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            
            // Generate PDF
            html2pdf().from(contentToExport).set(options).save().then(function() {
                // Remove loading indicator when done
                document.body.removeChild(loadingElement);
            });
        });
    }
    
    // Add export all button functionality if it exists
    const exportAllButton = document.getElementById('export-all-btn');
    if (exportAllButton) {
        exportAllButton.addEventListener('click', function() {
            // Fetch all content via AJAX and generate PDF
            fetch('/get-export-content')
                .then(response => response.json())
                .then(data => {
                    // Create a temporary container with all content
                    const tempContainer = document.createElement('div');
                    tempContainer.innerHTML = data.content;
                    tempContainer.style.display = 'none';
                    document.body.appendChild(tempContainer);
                    
                    // Show loading indicator
                    const loadingElement = document.createElement('div');
                    loadingElement.className = 'loading-overlay';
                    loadingElement.innerHTML = `
                        <div class="spinner"></div>
                        <p>Generating Complete Report...</p>
                    `;
                    document.body.appendChild(loadingElement);
                    
                    // Configure PDF options
                    const options = {
                        margin: 10,
                        filename: 'complete-analysis-report.pdf',
                        image: { type: 'jpeg', quality: 0.98 },
                        html2canvas: { scale: 2, useCORS: true, logging: false },
                        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                    };
                    
                    // Generate PDF
                    html2pdf().from(tempContainer).set(options).save().then(function() {
                        // Remove temporary container and loading indicator
                        document.body.removeChild(tempContainer);
                        document.body.removeChild(loadingElement);
                    });
                })
                .catch(error => {
                    console.error('Error generating PDF:', error);
                    alert('Failed to generate PDF. Please try again.');
                });
        });
    }
});