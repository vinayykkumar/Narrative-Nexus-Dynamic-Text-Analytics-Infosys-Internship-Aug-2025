import React, { useEffect, useState, useRef } from "react";
import "./landing.css";
import { useNavigate } from "react-router-dom";

const CARDS = [
  {
    title: "Summarization",
    subtitle: "Concise, human-like summaries of long documents",
    body:
      "We compress documents into clear summaries while preserving the main points. Choose extractive, abstractive, or hybrid.",
  },
  {
    title: "Sentiment Analysis",
    subtitle: "Polarity & distribution",
    body:
      "Get overall sentiment plus a distribution of sentences (positive • neutral • negative) for deeper understanding.",
  },
  {
    title: "Insights",
    subtitle: "Actionable bullets",
    body:
      "Auto-generated insights and keyword frequency charts highlight what matters most in your document.",
  },
];

export default function Landing({ onStart }) {
  const [index, setIndex] = useState(0);
  const intervalRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    startAuto();
    return stopAuto;
  }, []);

  function startAuto() {
    stopAuto();
    intervalRef.current = setInterval(() => {
      setIndex((i) => (i + 1) % CARDS.length);
    }, 2800);
  }
  function stopAuto() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }

  function goTo(i) {
    setIndex(i);
    startAuto();
  }

  return (
    <div className="landing-root landing-gemini">
      <header className="hero-top">
        <h1 className="brand-title">SmartInsights</h1>
        <p className="brand-sub">Summarize · Sentiment · Insights</p>

        <div className="hero-actions">
          <button
            className="btn-analyze"
            onMouseDown={(e) => e.currentTarget.classList.add("pressed")}
            onMouseUp={(e) => e.currentTarget.classList.remove("pressed")}
            onMouseLeave={(e) => e.currentTarget.classList.remove("pressed")}
            onClick={() => {
              if (onStart) onStart();
              else navigate("/analyzer");
            }}
            type="button"
          >
            Analyze
          </button>
        </div>
      </header>

      {/* remove the big spacer so bottom content is visible */}
      {/* <div style={{ flex: 1 }} /> */}

      <section className="carousel-wrap" aria-roledescription="carousel" style={{ marginTop: 32, marginBottom: 24 }}>
        <div className="carousel-inner">
          {CARDS.map((c, i) => {
            const active = i === index;
            return (
              <article
                key={c.title}
                className={`card ${active ? "card-active" : "card-inactive"}`}
                aria-hidden={!active}
              >
                <div className="card-meta">
                  <div className="card-label">{c.subtitle}</div>
                  <h3 className="card-head">{c.title}</h3>
                </div>
                <div className="card-body">{c.body}</div>
              </article>
            );
          })}
        </div>

        <div className="carousel-controls">
          <div className="dots">
            {CARDS.map((_, i) => (
              <button
                key={i}
                className={`dot ${i === index ? "dot-active" : ""}`}
                onClick={() => goTo(i)}
                aria-label={`Show ${i + 1}`}
                type="button"
              />
            ))}
          </div>

          <div className="pill">
            <div className="pill-bar" style={{ width: `${((index + 1) / CARDS.length) * 100}%` }} />
          </div>
        </div>
      </section>

      <footer className="landing-foot">Built with ❤️ — SmartInsights</footer>
    </div>
  );
}
