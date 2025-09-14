// src/pages/ai/Reports.jsx
import { Download } from 'lucide-react';
import React from 'react';
import { useOutletContext } from 'react-router-dom';

const Reports = () => {
  const { insights } = useOutletContext();

  const downloadReport = () => {
    const content = insights.join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'insights-report.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <h2 className="text-3xl font-bold mb-4">Reports & Insights</h2>
      {insights.length === 0 ? (
        <p className='text-center py-28 text-3xl'>No insights available.</p>
      ) : (
        <>
          {insights.map((insight, i) => (
            <div key={i} className="max-w-3xl mb-3 p-3 border rounded bg-slate-500">
              {insight}
            </div>
          ))}
          <button
            onClick={downloadReport}
            className="px-6 py-3 mt-6 flex gap-2 bg-green-600 rounded-full hover:bg-green-700"
          >
           <Download className='h-5 w-5'/> Download Report
          </button>
        </>
      )}
    </div>
  );
};

export default Reports;
