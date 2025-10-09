import React from "react";

function SentimentBadge({ label, score }) {
  const map = {
    positive: { emoji: "😊", bg: "rgba(16,185,129,0.22)" },
    neutral:  { emoji: "😐", bg: "rgba(148,163,184,0.22)" },
    negative: { emoji: "😞", bg: "rgba(239,68,68,0.22)" },
    unknown:  { emoji: "❔", bg: "rgba(148,163,184,0.18)" },
  };
  const k = (label || "unknown").toLowerCase();
  const { emoji, bg } = map[k] || map.unknown;

  return (
    <div
      style={{
        display: "flex",
        gap: 10,
        alignItems: "center",
        padding: "10px 12px",
        borderRadius: 12,
        background: "rgba(255,255,255,0.02)",
        border: "1px solid rgba(255,255,255,0.06)",
      }}
    >
      <div
        style={{
          width: 38,
          height: 38,
          borderRadius: 10,
          display: "grid",
          placeItems: "center",
          background: bg,
        }}
      >
        {emoji}
      </div>
      <div>
        <div style={{ fontWeight: 700 }}>{label || "Unknown"}</div>
        <div className="small">
          Score: {typeof score === "number" ? score.toFixed(3) : "n/a"}
        </div>
      </div>
    </div>
  );
}

function TopicBadge({ index, label }) {
  const text = Array.isArray(label) ? label.join(", ") : (label || "No label");
  return (
    <div
      style={{
        padding: "10px 12px",
        borderRadius: 12,
        background: "rgba(255,255,255,0.02)",
        border: "1px solid rgba(255,255,255,0.06)",
      }}
    >
      <div style={{ fontWeight: 700 }}>Topic {index ?? "—"}</div>
      <div className="small" style={{ opacity: 0.85 }}>{text}</div>
    </div>
  );
}

export default function StatBadges({
  sentimentLabel,
  sentimentScore,
  predictedTopic,
  predictedLabel,
}) {
  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Overview</h3>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <SentimentBadge label={sentimentLabel} score={sentimentScore} />
        <TopicBadge index={predictedTopic} label={predictedLabel} />
      </div>
    </div>
  );
}
