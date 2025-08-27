import React from 'react';
import jsPDF from 'jspdf';

// Import autoTable plugin differently for React
import autoTable from 'jspdf-autotable';

export default function ExportReportButton({ 
  sentimentData = {}, 
  topics = [], 
  topTerms = [], 
  summary = "", 
  insights = "", 
  metadata = {} 
}) {

  const exportReport = () => {
    try {
      console.log('PDF Export Data:', { sentimentData, topics, topTerms, summary, insights, metadata });
      
      const doc = new jsPDF();
      let y = 20;

      // Header
      doc.setFontSize(20);
      doc.setTextColor(147, 51, 234);
      doc.text('AI Dataset Analysis Report', 20, y);
      y += 15;

      // Date
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 20, y);
      y += 20;

      // Sentiment Analysis
      doc.setFontSize(14);
      doc.setTextColor(0, 0, 0);
      doc.text('Sentiment Distribution', 20, y);
      y += 10;

      const sentimentRows = sentimentData && typeof sentimentData === 'object' 
        ? Object.entries(sentimentData)
            .filter(([key, val]) => val !== undefined && val !== null)
            .map(([key, val]) => [
              key.charAt(0).toUpperCase() + key.slice(1),
              `${Math.round((val || 0) * 100)}%`
            ])
        : [['No data', '-']];

      // Use autoTable function directly (imported above)
      autoTable(doc, {
        startY: y,
        head: [['Sentiment', 'Percentage']],
        body: sentimentRows,
        theme: 'striped',
        headStyles: { fillColor: [147, 51, 234] },
        margin: { left: 20, right: 20 }
      });
      y = doc.lastAutoTable.finalY + 15;

      // Topics Analysis
      doc.setFontSize(14);
      doc.text('Topics Analysis (LDA/NMF)', 20, y);
      y += 10;

      let topicsRows = [];
      if (Array.isArray(topics) && topics.length > 0) {
        topicsRows = topics.map((topic, index) => {
          let topicName = `Topic ${index + 1}`;
          let keyWords = 'Processing...';
          let percentage = '-';

          if (typeof topic === 'object' && topic !== null) {
            topicName = topic.topic || topicName;
            keyWords = topic.keyWords || topic.words || 'Processing...';
            percentage = topic.percent || topic.percentage || '-';
          } else if (Array.isArray(topic)) {
            keyWords = topic.join(', ');
            percentage = `${Math.round(100 / topics.length)}%`;
          }

          return [topicName, keyWords, percentage];
        });
      } else {
        topicsRows = [['No topics found', 'Analysis in progress', '-']];
      }

      autoTable(doc, {
        startY: y,
        head: [['Topic', 'Key Words', 'Weight']],
        body: topicsRows,
        theme: 'striped',
        headStyles: { fillColor: [59, 130, 246] },
        margin: { left: 20, right: 20 }
      });
      y = doc.lastAutoTable.finalY + 15;

      // Top Terms
      doc.setFontSize(14);
      doc.text('Top Terms', 20, y);
      y += 10;

      const termsText = Array.isArray(topTerms) && topTerms.length > 0 
        ? topTerms.slice(0, 10).join(', ')
        : 'Analysis in progress...';
        
      doc.setFontSize(10);
      const splitTerms = doc.splitTextToSize(termsText, 170);
      doc.text(splitTerms, 20, y);
      y += splitTerms.length * 5 + 15;

      // Summary & Insights sections...
      if (summary && summary.trim()) {
        doc.setFontSize(14);
        doc.text('Summary', 20, y);
        y += 10;
        doc.setFontSize(10);
        const summaryText = doc.splitTextToSize(summary, 170);
        doc.text(summaryText, 20, y);
        y += summaryText.length * 5 + 15;
      }

      if (insights && insights.trim()) {
        doc.setFontSize(14);
        doc.text('Key Insights & Recommendations', 20, y);
        y += 10;
        doc.setFontSize(10);
        const insightsText = doc.splitTextToSize(insights, 170);
        doc.text(insightsText, 20, y);
      }

      // Save the PDF
      const filename = `analysis-report-${new Date().toISOString().slice(0, 10)}.pdf`;
      doc.save(filename);
      
    } catch (error) {
      console.error('PDF Export Error:', error);
      alert(`PDF Export Failed: ${error.message}`);
    }
  };

  return (
    <button
      onClick={exportReport}
      className="px-8 py-3 bg-gradient-to-r from-purple-500 to-cyan-400 text-white rounded-full text-lg font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 flex items-center gap-2"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      Download PDF Report
    </button>
  );
}
