import React, { useMemo } from "react";

function bucket(c) {
  if (c >= 0.05) return "positive";
  if (c <= -0.05) return "negative";
  return "neutral";
}

export default function SentimentDonut({ scores = [] }) {
  const counts = useMemo(() => {
    const init = { positive: 0, neutral: 0, negative: 0 };
    for (const s of scores || []) init[bucket(s)]++;
    return init;
  }, [scores]);

  const total = Math.max(1, counts.positive + counts.neutral + counts.negative);
  const data = [
    { key: "positive", label: "Positive", value: counts.positive, color: "rgba(16,185,129,0.9)" },
    { key: "neutral",  label: "Neutral",  value: counts.neutral,  color: "rgba(148,163,184,0.9)" },
    { key: "negative", label: "Negative", value: counts.negative, color: "rgba(239,68,68,0.9)" },
  ];

  const radius = 60, cx = 80, cy = 80, circ = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div style={{ marginTop: "12px" }}>
      <div className="small" style={{ marginBottom: 6 }}>Sentiment (donut)</div>
      <svg width="160" height="160" viewBox="0 0 160 160">
        {data.map((d) => {
          const frac = d.value / total;
          const len = circ * frac;
          const dash = `${len} ${circ - len}`;
          const el = (
            <circle
              key={d.key}
              r={radius}
              cx={cx}
              cy={cy}
              fill="transparent"
              stroke={d.color}
              strokeWidth="22"
              strokeDasharray={dash}
              strokeDashoffset={-offset}
            />
          );
          offset += len;
          return el;
        })}
        {/* inner hole */}
        <circle r={38} cx={cx} cy={cy} fill="rgba(2,6,23,0.95)" />
      </svg>
      <div className="small">
        {data.map((d) => `${d.label}: ${d.value}`).join(" · ")}
      </div>
    </div>
  );
}
