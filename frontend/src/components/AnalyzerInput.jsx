import React, { useState } from "react";

export default function AnalyzerInput({ onResult, onAnalyzeResult }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!input.trim()) return;
    setLoading(true);
    setError("");

    try {
      // Change to http://localhost:5000/analyse if your backend uses 'analyse'
      const url = "http://localhost:5000/analyze";

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();

      // Support both prop names so existing pages work
      if (onResult) onResult(data);
      if (onAnalyzeResult) onAnalyzeResult(data);
    } catch (e) {
      console.error("Analyze failed:", e);
      setError("Analysis failed. Check backend logs.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <textarea
        className="input-text"
        rows={6}
        placeholder="Paste text here..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <div style={{ marginTop: 12, display: "flex", gap: 12 }}>
        <button className="btn-action" onClick={handleAnalyze} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
        {error && <span className="small" style={{ color: "red" }}>{error}</span>}
      </div>
    </div>
  );
}
