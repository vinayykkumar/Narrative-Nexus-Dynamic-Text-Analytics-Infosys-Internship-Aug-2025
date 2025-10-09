import React, { useState } from "react";

export default function SummaryTabs({ abstractive, extractive, hybrid }) {
  const [active, setActive] = useState("abstractive");

  const summaries = {
    abstractive,
    extractive,
    hybrid,
  };

  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        {Object.keys(summaries).map((key) => (
          <button
            key={key}
            className="btn-tool"
            onClick={() => setActive(key)}
            style={{
              padding: "6px 12px",
              borderRadius: 8,
              border: "1px solid rgba(255,255,255,0.1)",
              background:
                active === key ? "rgba(99,102,241,0.25)" : "transparent",
              cursor: "pointer",
            }}
          >
            {key.charAt(0).toUpperCase() + key.slice(1)}
          </button>
        ))}
      </div>

      <div
        style={{
          padding: 12,
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 8,
          background: "rgba(255,255,255,0.03)",
          minHeight: 80,
        }}
      >
        {summaries[active] ? (
          <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>
            {summaries[active]}
          </pre>
        ) : (
          <div className="small">No {active} summary available.</div>
        )}
      </div>
    </div>
  );
}
