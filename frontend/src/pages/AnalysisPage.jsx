import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ParticleBG from '../components/ParticleBG';

export default function AnalysisPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadError, setDownloadError] = useState(null);

  useEffect(() => {
    if (location.state) {
      setAnalysisData(location.state);
      setLoading(false);
    } else {
      navigate('/upload');
    }
  }, [location.state, navigate]);

  // Download PDF report handler - sends full analysisData JSON to backend
  const handleDownload = async () => {
    setDownloadError(null);
    try {
      const res = await fetch('http://localhost:8001/download-report', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(analysisData)  // Send entire analysis JSON
      });
      if (!res.ok) {
        const err = await res.json();
        setDownloadError(err.message || "Failed to download report. Try again.");
        return;
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "analysis-report.pdf";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setDownloadError("Server unreachable or network error.");
    }
  };

  if (loading || !analysisData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  // Prepare sentiment data for BarChart
  const sentimentChartData = Object.entries(analysisData.sentiment || {}).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: Math.round(value * 100),
    fill: key === 'positive' ? '#10B981' : key === 'negative' ? '#EF4444' : '#8B5CF6'
  }));

  // Format topics data for display
  const topicsFormatted = analysisData.topics?.map((topic, index) => ({
    topic: topic.topic || `Topic ${index + 1}`,
    keyWords: topic.keyWords || (Array.isArray(topic) ? topic.join(', ') : topic),
    percent: topic.percent || `${Math.round(100 / analysisData.topics.length)}%`
  })) || [];

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8 overflow-x-hidden">
      <ParticleBG />

      {/* Header */}
      <div className="relative z-10 container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <button
            onClick={() => navigate('/upload')}
            className="flex items-center gap-2 px-6 py-3 bg-white/80 backdrop-blur-sm rounded-full shadow-lg hover:bg-white/90 transition-all duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Upload
          </button>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            AI Dataset Analysis Results
          </h1>
          <div className="w-32"></div> {/* Spacer for centering */}
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Sentiment Distribution */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.1, type: "spring", stiffness: 80 }}
            className="lg:col-span-1 bg-white/80 backdrop-blur-lg rounded-2xl p-6 shadow-xl"
            whileHover={{ scale: 1.03, boxShadow: "0 0 42px #a855f7cc" }}
          >
            <h2 className="text-2xl font-bold text-purple-700 mb-4">Sentiment Distribution</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sentimentChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value}%`, 'Percentage']} />
                  <Bar dataKey="value" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Key Insights */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.15, type: "spring", stiffness: 80 }}
            className="lg:col-span-2 bg-white/80 backdrop-blur-lg rounded-2xl p-6 shadow-xl"
            whileHover={{ scale: 1.02, boxShadow: "0 0 34px #0ea5e9aa" }}
          >
            <h2 className="text-2xl font-bold text-blue-700 mb-4">Key Insights & Recommendations</h2>
            <div className="prose max-w-none">
              <p className="text-gray-700 leading-relaxed">{analysisData.insights}</p>
              {analysisData.metadata && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-800">Processing Details:</h3>
                  <ul className="list-disc list-inside text-sm text-blue-700 mt-2">
                    <li>Total entries processed: {analysisData.metadata.totalEntries}</li>
                    <li>Method: {analysisData.metadata.processingMethod}</li>
                    <li>Advanced NLP: {analysisData.metadata.nlpEnabled ? '✅ Enabled' : '⚠️ Basic mode'}</li>
                  </ul>
                </div>
              )}
            </div>
          </motion.div>

          {/* Topics Analysis */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 80 }}
            className="bg-white/80 backdrop-blur-lg rounded-2xl p-6 shadow-xl"
            whileHover={{ scale: 1.03, boxShadow: "0 0 32px #c026d3cc" }}
          >
            <h2 className="text-2xl font-bold text-purple-700 mb-4">Topics (LDA/NMF)</h2>
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-4 text-sm font-semibold text-gray-600 border-b pb-2">
                <span>#</span>
                <span>Key Words</span>
                <span>%</span>
              </div>
              {topicsFormatted.map((topic, index) => (
                <div key={index} className="grid grid-cols-3 gap-4 text-sm py-2 border-b border-gray-100 last:border-b-0">
                  <span className="font-medium text-purple-600">{index + 1}</span>
                  <span className="text-gray-700 truncate" title={topic.keyWords}>{topic.keyWords}</span>
                  <span className="font-semibold text-blue-600">{topic.percent}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Top Terms */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.3, type: "spring", stiffness: 80 }}
            className="bg-white/80 backdrop-blur-lg rounded-2xl p-6 shadow-xl"
            whileHover={{ scale: 1.03, boxShadow: "0 0 28px #818cf8cc" }}
          >
            <h2 className="text-2xl font-bold text-purple-700 mb-4">Top Terms</h2>
            <div className="flex flex-wrap gap-2">
              {analysisData.topTerms?.slice(0, 15).map((term, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 rounded-full text-sm font-medium"
                  style={{ fontSize: `${Math.max(12, 16 - index * 0.5)}px` }}
                >
                  {term}
                </span>
              ))}
            </div>
          </motion.div>

          {/* Summary */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.4, type: "spring", stiffness: 80 }}
            className="bg-white/80 backdrop-blur-lg rounded-2xl p-6 shadow-xl"
            whileHover={{ scale: 1.02, boxShadow: "0 0 19px #06b6d4aa" }}
          >
            <h2 className="text-2xl font-bold text-blue-700 mb-4">Summary</h2>
            <div className="prose max-w-none">
              <p className="text-gray-700 leading-relaxed">{analysisData.summary}</p>
              <div className="mt-4 flex items-center gap-2">
                <div className="flex-1 h-1 bg-gradient-to-r from-purple-400 to-blue-400 rounded-full"></div>
                <span className="text-xs text-gray-500 font-medium">Analysis Complete</span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Export/Download Button and error feedback */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex flex-col items-center mt-8"
        >
          {downloadError && (
            <div className="mb-3 px-4 py-2 bg-red-100 text-red-700 rounded shadow">{downloadError}</div>
          )}
          <motion.button
            onClick={handleDownload}
            whileHover={{ scale: 1.10, boxShadow: "0 4px 18px #a855f7cc" }}
            whileTap={{ scale: 0.95 }}
            className="px-9 py-3 text-lg font-bold rounded-full bg-gradient-to-r from-fuchsia-400 via-purple-400 to-cyan-400 text-white shadow-lg transition-all duration-200"
          >
            ⬇️ Download Analysis Report
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
}
