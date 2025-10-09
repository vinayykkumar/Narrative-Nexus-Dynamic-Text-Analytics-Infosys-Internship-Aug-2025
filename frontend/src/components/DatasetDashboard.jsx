import React, { useEffect, useState } from "react";

export default function DatasetDashboard() {
  const [counts, setCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [topicImg, setTopicImg] = useState(null);

  useEffect(() => {
    fetch("/dataset/topics")
      .then(r => r.json())
      .then(j => {
        if (j.ok) setCounts(j.counts || {});
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function loadWordcloud(id) {
    try {
      const res = await fetch(`/dataset/topic_wordcloud/${id}`);
      const j = await res.json();
      if (j.ok) setTopicImg(j.url);
    } catch {}
  }

  return (
    <div className="card" style={{ marginTop: 16 }}>
      <h3 style={{ marginTop: 0 }}>Dataset Dashboard</h3>
      {loading ? (
        <div className="small">Loading…</div>
      ) : (
        <div>
          <div className="small" style={{ marginBottom: 6 }}>Topic distribution (docs per topic)</div>
          <div style={{ display: "grid", gap: 6 }}>
            {Object.entries(counts).map(([k, v]) => (
              <div key={k} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <button className="btn-tool" onClick={() => loadWordcloud(k)}>
                  Topic {k}
                </button>
                <div className="small">{v} docs</div>
              </div>
            ))}
            {Object.keys(counts).length === 0 && (
              <div className="small">No topic data.</div>
            )}
          </div>
          {topicImg && (
            <div style={{ marginTop: 12 }}>
              <div className="small">Topic wordcloud:</div>
              <img src={topicImg} alt="topic cloud"
                style={{ width:"100%", border:"1px solid rgba(255,255,255,0.06)", borderRadius:12 }}/>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
