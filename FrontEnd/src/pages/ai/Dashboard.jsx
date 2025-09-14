// src/pages/ai/Dashboard.jsx
import React from 'react';
import { useOutletContext } from 'react-router-dom';

const Dashboard = () => {
  const { analysisData, sentimentData, insights } = useOutletContext();

  const hasData = analysisData || sentimentData || (insights && insights.length > 0);

  if (!hasData) {
    return <p className='text-center py-28 text-3xl'>No records found yet.</p>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-4">Dashboard Summary</h2>

      {analysisData && (
        <div className="mb-6">
          <h3 className="font-semibold mb-2">Analysis Results</h3>
          <p>Summary: {analysisData.summary}</p>
          <p>Word Cloud:</p>
          <div className="flex flex-wrap gap-2 mb-2">
            {analysisData.wordCloud.map((word, i) => (
              <span key={i} className="bg-blue-500 px-3 py-1 rounded-full text-sm">{word}</span>
            ))}
          </div>
          <p>Topics:</p>
          <ul className="list-disc pl-5">
            {analysisData.topics.map((topic, i) => (
              <li key={i}>{topic.name}: {topic.keywords.join(', ')}</li>
            ))}
          </ul>
        </div>
      )}

      {sentimentData && (
        <div className="mb-6">
          <h3 className="font-semibold mb-2">Sentiment Analysis</h3>
          <p>{sentimentData.text}</p>
          <p>Topics:</p>
          <ul className="list-disc pl-5">
            {sentimentData.topics.map((topic, i) => (
              <li key={i}>{topic.name}: {topic.keywords.join(', ')}</li>
            ))}
          </ul>
        </div>
      )}

      {insights.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2">Insights</h3>
          {insights.map((insight, i) => (
            <div key={i} className="max-w-3xl mb-2 p-4 border rounded bg-slate-500">
              {insight}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
