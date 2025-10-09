import React, { useMemo } from "react";

export default function SentimentHistogram({ scores = [] }) {
  const bins = useMemo(() => {
    const edges = [-1,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1.01];
    const counts = new Array(edges.length - 1).fill(0);
    for (const s of scores || []) {
      for (let i = 0; i < edges.length - 1; i++) {
        if (s >= edges[i] && s < edges[i + 1]) { counts[i]++; break; }
      }
    }
    const max = Math.max(1, ...counts);
    return { edges, counts, max };
  }, [scores]);

  const W = 360, H = 120, pad = 16;
  const bw = (W - pad*2) / bins.counts.length;

  return (
    <div>
      <div className="small" style={{ marginBottom: 6 }}>Sentence Sentiment (VADER compound)</div>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`}>
        {bins.counts.map((c, i) => {
          const h = (c / bins.max) * (H - pad*2);
          const x = pad + i * bw;
          const y = H - pad - h;
          return <rect key={i} x={x} y={y} width={bw - 2} height={h} fill="currentColor" opacity="0.7" rx="2" />;
        })}
        <line x1={pad} x2={W-pad} y1={H-pad} y2={H-pad} stroke="currentColor" opacity="0.25" />
        <text x={pad} y={H-2} fontSize="10" fill="currentColor" opacity="0.7">-1</text>
        <text x={W-pad-10} y={H-2} fontSize="10" fill="currentColor" opacity="0.7">1</text>
      </svg>
    </div>
  );
}
