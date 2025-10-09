import React from "react";

export default function DocsPage() {
  return (
    <div style={{ padding:"36px", color:"#eaf0ff", maxWidth:700, margin:"0 auto" }}>
      <h1>SmartInsights Documentation</h1>
      <p className="small">
        SmartInsights is a dynamic text analysis platform. It processes text from multiple sources,
        cleans and normalizes it, and applies topic modeling, sentiment analysis, and summarization.
      </p>

      <h2>Features</h2>
      <ul>
        <li>Summarization (Extractive, Abstractive, Hybrid)</li>
        <li>Sentiment analysis (overall + sentence-level)</li>
        <li>Topic modeling with NMF/LDA</li>
        <li>Insights extraction (keywords, representative sentences)</li>
        <li>Interactive dashboards and visualizations</li>
        <li>Exportable reports (HTML/PDF)</li>
      </ul>

      <h2>Workflow</h2>
      <ol>
        <li>Input text via paste or upload.</li>
        <li>Preprocessing: cleaning, tokenization, lemmatization.</li>
        <li>Analysis: summarization, sentiment, topic modeling.</li>
        <li>Visualization: wordclouds, charts.</li>
        <li>Export results as PDF/HTML.</li>
      </ol>

      <h2>Privacy</h2>
      <p className="small">Text is processed locally. No data is stored on servers.</p>
    </div>
  );
}

