import React, { useMemo } from "react";

function bucket(c) {
  if (c >= 0.05) return "positive";
  if (c <= -0.05) return "negative";
  return "neutral";
}

export default function SentimentBars({ scores = [] }) {
  const counts = useMemo(() => {
    const init = { positive: 0, neutral: 0, negative: 0 };
    for (const s of scores || []) init[bucket(s)]++;
    return init;
  }, [scores]);

  const total = Math.max(1, counts.positive + counts.neutral + counts.negative);
  const data = [
    { key: "positive", label: "Positive", value: counts.positive, pct: Math.round((counts.positive/total)*100) },
    { key: "neutral",  label: "Neutral",  value: counts.neutral,  pct: Math.round((counts.neutral/total)*100)  },
    { key: "negative", label: "Negative", value: counts.negative, pct: Math.round((counts.negative/total)*100) },
  ];

  const W = 360, H = 140, pad = 16;
  const barW = (W - pad*2) / data.length - 12; // gap

  const maxVal = Math.max(1, ...data.map(d => d.value));

  const color = (k) => (
    k === "positive" ? "rgba(16,185,129,0.9)" :
    k === "negative" ? "rgba(239,68,68,0.9)"  :
                       "rgba(148,163,184,0.9)"
  );

  return (
    <div>
      <div className="small" style={{ marginBottom: 6 }}>Sentiment (bars)</div>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`} aria-label="Sentiment bars">
        <line x1={pad} x2={W-pad} y1={H-pad} y2={H-pad} stroke="currentColor" opacity="0.25" />
        {data.map((d, i) => {
          const x = pad + i * (barW + 12);
          const h = (d.value / maxVal) * (H - pad*2);
          const y = H - pad - h;
          return (
            <g key={d.key}>
              <rect x={x} y={y} width={barW} height={h} rx="4" fill={color(d.key)} />
              <text x={x + barW/2} y={y - 6} fontSize="11" textAnchor="middle" fill="currentColor" opacity="0.9">
                {d.value} ({d.pct}%)
              </text>
              <text x={x + barW/2} y={H - pad + 12} fontSize="12" textAnchor="middle" fill="currentColor" opacity="0.9">
                {d.label}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="small" style={{ opacity:.75, marginTop: 4 }}>
        Based on sentence-level VADER scores (±0.05 thresholds).
      </div>
    </div>
  );
}
