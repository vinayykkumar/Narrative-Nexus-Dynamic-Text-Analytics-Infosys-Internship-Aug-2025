import React, { useMemo } from "react";

/**
 * Props:
 *  - insights: string[]           (HTML-safe lines)
 *  - keyTerms: string[] | {term:string,count:number}[] | [term,count][]
 *  - repSentences: string[]
 *  - keyUniCounts: { [term:string]: number }  // optional fallback
 */
export default function InsightsPro({ insights = [], keyTerms = [], repSentences = [], keyUniCounts = null }) {
  // Normalize key terms (fallback to keyUniCounts if needed)
  const chips = useMemo(() => {
    if (Array.isArray(keyTerms) && keyTerms.length > 0) {
      if (typeof keyTerms[0] === "string") {
        return keyTerms.slice(0, 10).map(t => ({ term: t, count: null }));
      } else {
        // support [{term,count}] or [term,count]
        return keyTerms.slice(0, 10).map((x) => ({
          term: (x.term ?? x[0] ?? "").toString(),
          count: typeof x.count === "number" ? x.count : (Array.isArray(x) ? x[1] : null)
        }));
      }
    }
    if (keyUniCounts && typeof keyUniCounts === "object") {
      const arr = Object.entries(keyUniCounts).sort((a,b)=>b[1]-a[1]).slice(0,10);
      return arr.map(([term,count]) => ({ term, count }));
    }
    return [];
  }, [keyTerms, keyUniCounts]);

  const quotes = Array.isArray(repSentences) ? repSentences.slice(0, 4) : [];

  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Insights</h3>

      {/* Highlight insights */}
      <div style={{ display: "grid", gap: 8 }}>
        {Array.isArray(insights) && insights.length > 0 ? (
          insights.slice(0, 6).map((text, i) => (
            <div
              key={i}
              className="card"
              style={{
                display: "grid",
                gridTemplateColumns: "32px 1fr",
                gap: 10,
                alignItems: "start",
                padding: 12,
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.06)",
              }}
            >
              <div style={{
                width: 32, height: 32, borderRadius: 8,
                display: "grid", placeItems: "center",
                background: "rgba(99,102,241,0.18)"
              }}>💡</div>
              <div dangerouslySetInnerHTML={{ __html: text }} />
            </div>
          ))
        ) : (
          <div className="small">No insights.</div>
        )}
      </div>

      {/* Keyword chips */}
      <div style={{ marginTop: 12 }}>
        <div className="small" style={{ marginBottom: 6 }}>Key terms</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {chips.length > 0 ? chips.map((c, i) => (
            <span key={i} style={{
              padding: "6px 10px",
              borderRadius: 999,
              border: "1px solid rgba(255,255,255,0.08)",
              background: "rgba(255,255,255,0.03)",
              fontSize: 12,
              whiteSpace: "nowrap",
              color: "#cbd5ff",
            }}>
              #{c.term}{typeof c.count === "number" ? ` · ${c.count}` : ""}
            </span>
          )) : <span className="small">No keywords.</span>}
        </div>
      </div>

      {/* Representative quotes */}
      <div style={{ marginTop: 12 }}>
        <div className="small" style={{ marginBottom: 6 }}>Representative lines</div>
        <div style={{ display: "grid", gap: 8 }}>
          {quotes.length > 0 ? quotes.map((q, i) => (
            <blockquote key={i} className="card" style={{
              margin: 0, padding: 12,
              borderLeft: "3px solid rgba(99,102,241,0.6)",
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              fontStyle: "italic",
              color: "#e6eefc"
            }}>
              “{q}”
            </blockquote>
          )) : <div className="small">No representative lines.</div>}
        </div>
      </div>
    </div>
  );
}
