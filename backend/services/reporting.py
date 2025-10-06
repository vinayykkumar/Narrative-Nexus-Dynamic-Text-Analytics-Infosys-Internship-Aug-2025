from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

try:
    from jinja2 import Environment, BaseLoader, select_autoescape
except Exception:
    Environment = None  # type: ignore


REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Narrative Nexus Report</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 2rem; color: #0f172a; }
    h1, h2, h3 { color: #111827; }
    h1 { margin-bottom: 0.25rem; }
    .muted { color: #6b7280; }
    .grid { display: grid; gap: 1rem; }
    .grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .card { border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 1rem; background: #fff; }
    .kpi { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; }
    .kpi .item { background: #f9fafb; padding: 0.75rem; border-radius: 0.5rem; text-align: center; }
    .small { font-size: 0.875rem; }
    img { max-width: 100%; height: auto; border-radius: 0.5rem; border: 1px solid #e5e7eb; }
    ul { margin-top: 0.25rem; }
    .pill { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 0.75rem; margin-right: 0.25rem; }
    .footer { margin-top: 2rem; font-size: 0.875rem; color: #6b7280; }
  </style>
</head>
<body>
  <header>
    <h1>AI Narrative Nexus — Analysis Report</h1>
    <div class="muted small">Generated: {{ generated_at }} | Job: {{ job_name }}</div>
  </header>

  {% if dataset_summary %}
  <section class="card">
    <h2>Executive Summary</h2>
    <p>{{ dataset_summary.summary }}</p>
    {% if dataset_summary.key_sentences %}
      <div class="small muted">Method: {{ dataset_summary.method_used }}</div>
      <ul>
        {% for s in dataset_summary.key_sentences %}
        <li>{{ s }}</li>
        {% endfor %}
      </ul>
    {% endif %}
  </section>
  {% endif %}

  <section class="grid grid-2">
    <div class="card">
      <h2>Topic Modeling (NMF)</h2>
      {% if topic_modeling_results %}
        <div class="small muted">Topics: {{ topic_modeling_results.num_topics }}</div>
        <ul>
          {% for t in topic_modeling_results.topics %}
            <li>
              <strong>{{ t.topic_label }}</strong>
              <div class="small">
                {% for w, wt in t.top_words %}
                  <span class="pill">{{ w }}</span>
                {% endfor %}
              </div>
            </li>
          {% endfor %}
        </ul>
      {% else %}
        <div class="muted small">No topic results available.</div>
      {% endif %}
    </div>

    <div class="card">
      <h2>Sentiment & Emotions</h2>
      {% if sentiment_results %}
        <div class="kpi">
          <div class="item"><div class="small muted">Overall</div><div><strong>{{ sentiment_results.overall_sentiment }}</strong></div></div>
          <div class="item"><div class="small muted">Confidence</div><div><strong>{{ (sentiment_results.overall_confidence*100)|round(1) }}%</strong></div></div>
          <div class="item"><div class="small muted">Positive</div><div><strong>{{ (sentiment_results.sentiment_distribution.positive*100)|round(1) }}%</strong></div></div>
          <div class="item"><div class="small muted">Negative</div><div><strong>{{ (sentiment_results.sentiment_distribution.negative*100)|round(1) }}%</strong></div></div>
          <div class="item"><div class="small muted">Neutral</div><div><strong>{{ (sentiment_results.sentiment_distribution.neutral*100)|round(1) }}%</strong></div></div>
        </div>
        {% if sentiment_results.emotional_indicators %}
          <div class="small muted" style="margin-top: .5rem">Emotions (NRC)</div>
          <ul>
            {% for k, v in sentiment_results.emotional_indicators.items() %}
              <li class="small">{{ k|capitalize }}: {{ (v*100)|round(1) }}%</li>
            {% endfor %}
          </ul>
        {% endif %}
      {% else %}
        <div class="muted small">No sentiment results available.</div>
      {% endif %}
    </div>
  </section>

  {% if artifacts %}
  <section class="grid grid-2" style="margin-top: 1rem;">
    {% if artifacts.topic_distribution_pie %}
    <div class="card">
      <h3>Topic Distribution</h3>
      <img src="{{ artifacts.topic_distribution_pie }}" alt="Topic Distribution" />
    </div>
    {% endif %}
    {% if artifacts.sentiment_distribution_bar %}
    <div class="card">
      <h3>Sentiment Distribution</h3>
      <img src="{{ artifacts.sentiment_distribution_bar }}" alt="Sentiment Distribution" />
    </div>
    {% endif %}
    {% if artifacts.topic_sentiment_pie %}
    <div class="card">
      <h3>Topic vs Sentiment (Pie)</h3>
      <img src="{{ artifacts.topic_sentiment_pie }}" alt="Topic Sentiment Pie" />
    </div>
    {% endif %}
  </section>
  {% endif %}

  <section class="card">
    <h2>Actionable Insights & Recommendations</h2>
    <ul>
      {% if sentiment_results and sentiment_results.sentiment_distribution.negative > 0.4 %}
        <li>High negative sentiment detected. Investigate top drivers within dominant topics and prioritize service recovery.</li>
      {% endif %}
      {% if topic_modeling_results %}
        <li>Focus on top keywords per topic to design targeted improvements and FAQs.</li>
      {% endif %}
      {% if sentiment_results and (sentiment_results.emotional_indicators.fear or 0) > 0.2 %}
        <li>Elevated fear detected. Improve clarity of communication and reduce uncertainty in user journeys.</li>
      {% endif %}
      <li>Leverage recurring positive themes to amplify what works (highlight in onboarding and documentation).</li>
      <li>Track these KPIs over time: Positive%, Negative%, top topic prevalence, and key complaint categories.</li>
    </ul>
  </section>

  <footer class="footer">Report generated by AI Narrative Nexus.</footer>
</body>
</html>
"""


def build_report(
    output_dir: Path,
    topic_modeling_results: Optional[Dict[str, Any]],
    sentiment_results: Optional[Dict[str, Any]],
    dataset_summary: Optional[Dict[str, Any]],
    artifacts: Dict[str, str],
    job_name: str,
) -> Optional[Path]:
    """Render an HTML report into output_dir/report.html and return its path.

    If Jinja2 isn't available, return None gracefully.
    """
    if Environment is None:
        return None

    env = Environment(loader=BaseLoader(), autoescape=select_autoescape(["html"]))
    template = env.from_string(REPORT_TEMPLATE)

    html = template.render(
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        topic_modeling_results=topic_modeling_results,
        sentiment_results=sentiment_results,
        dataset_summary=dataset_summary,
        artifacts=artifacts,
        job_name=job_name,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "report.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path
