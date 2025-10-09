import React from "react";

export default function InsightsPanel({ insights = [] }) {
  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Insights</h3>
      {Array.isArray(insights) && insights.length > 0 ? (
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          {insights.map((t, i) => (
            <li key={i} dangerouslySetInnerHTML={{ __html: t }} />
          ))}
        </ul>
      ) : (
        <div className="small">No insights available.</div>
      )}
    </div>
  );
}
