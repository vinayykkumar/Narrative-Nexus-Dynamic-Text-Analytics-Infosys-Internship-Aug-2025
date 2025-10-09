import React, { useMemo } from "react";

export default function SentimentTrend({ scores = [], texts = [] }) {
  const W = 360, H = 140, pad = 16;

  const pts = useMemo(() => {
    if (!scores || scores.length === 0) return [];
    const n = scores.length;
    const xStep = (W - pad*2) / Math.max(1, n-1);
    return scores.map((s, i) => {
      const x = pad + i * xStep;
      // map [-1,1] to [H-pad, pad]
      const y = pad + (1 - ((s + 1) / 2)) * (H - pad*2);
      return { x, y, s };
    });
  }, [scores]);

  const path = useMemo(() => {
    if (pts.length === 0) return "";
    return pts.map((p,i)=>`${i===0?'M':'L'}${p.x},${p.y}`).join(" ");
  }, [pts]);

  return (
    <div>
      <div className="small" style={{ marginBottom: 6 }}>Sentiment trend by sentence</div>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`} aria-label="Sentiment trend">
        <line x1={pad} x2={W-pad} y1={H/2} y2={H/2} stroke="currentColor" opacity="0.25" />
        <path d={path} fill="none" stroke="currentColor" opacity="0.85" strokeWidth="2"/>
        {/* points */}
        {pts.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="2.5" fill="currentColor" opacity="0.9">
            {/* Optional: tooltip title */}
            <title>{`${(p.s>=0?'+':'')}${p.s.toFixed(3)}${texts?.[i] ? `\n${texts[i]}` : ''}`}</title>
          </circle>
        ))}
        {/* axes labels */}
        <text x={pad} y={H-2} fontSize="10" fill="currentColor" opacity="0.7">Start</text>
        <text x={W-pad-24} y={H-2} fontSize="10" fill="currentColor" opacity="0.7">End</text>
        <text x={pad} y={pad+8} fontSize="10" fill="currentColor" opacity="0.7">+1</text>
        <text x={pad} y={H-pad+10} fontSize="10" fill="currentColor" opacity="0.7">-1</text>
      </svg>
    </div>
  );
}
