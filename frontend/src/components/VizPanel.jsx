import React from "react";
import SentimentHistogram from "./SentimentHistogram";
import KeywordsBar from "./KeywordsBar";

export default function VizPanel({ wordcloudUrl, sentenceScores = [], keywordCounts = {} }) {
  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Visualizations</h3>
      <div style={{ display: "grid", gap: 12 }}>
        {wordcloudUrl ? (
          <div>
            <div className="small" style={{ marginBottom: 6 }}>Wordcloud</div>
            <img
              src={wordcloudUrl}
              alt="wordcloud"
              crossOrigin="anonymous"
              style={{ width: "100%", borderRadius: 12, border: "1px solid rgba(255,255,255,0.06)" }}
            />
          </div>
        ) : (
          <div className="small">No wordcloud.</div>
        )}
        <SentimentHistogram scores={sentenceScores} />
        <KeywordsBar counts={keywordCounts} />
      </div>
    </div>
  );
}
