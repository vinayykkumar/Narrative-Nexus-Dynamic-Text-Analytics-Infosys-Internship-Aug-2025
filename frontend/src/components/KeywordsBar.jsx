import React from "react";

export default function KeywordsBar({ counts = {} }) {
  const entries = Object.entries(counts || {}).slice(0, 10);
  const max = Math.max(1, ...entries.map(([,v]) => v));

  return (
    <div>
      <div className="small" style={{ marginBottom: 6 }}>Top Keywords</div>
      <div style={{ display: "grid", gap: 6 }}>
        {entries.map(([k, v]) => (
          <div key={k} style={{ display:"grid", gridTemplateColumns:"120px 1fr 40px", gap:8, alignItems:"center" }}>
            <div className="small" style={{ whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>{k}</div>
            <div style={{ background:"rgba(255,255,255,0.06)", borderRadius:999, overflow:"hidden" }}>
              <div style={{ height:8, width:`${(v / max) * 100}%`, background:"linear-gradient(90deg,#6366f1,#7c3aed)" }} />
            </div>
            <div className="small" style={{ textAlign:"right" }}>{v}</div>
          </div>
        ))}
        {entries.length === 0 && <div className="small">No keywords.</div>}
      </div>
    </div>
  );
}
