"""Reporting utilities for Narrative Nexus.

This module converts the rich analysis payload produced by
:func:`src.insights.generate_insights` into a comprehensive report structure
and optional Markdown export.  Reports combine sentiment breakdowns, topic
insights, keyword highlights, and actionable recommendations so they can be
shared with stakeholders or archived in the ``reports`` directory.
"""

from __future__ import annotations

import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_Number = Optional[float]


def _safe_percentage(value: _Number, fallback: float = 0.0) -> float:
    if value is None:
        return fallback
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return fallback


def _format_percentage(value: _Number, digits: int = 1) -> str:
    return f"{_safe_percentage(value) * 100:.{digits}f}%"


def _text_statistics(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    words = re.findall(r"\b\w+\b", stripped)
    sentences = re.split(r"[.!?]+\s*", stripped)
    sentences = [sentence for sentence in sentences if sentence]

    word_count = len(words)
    sentence_count = len(sentences) or 1
    avg_sentence_length = word_count / sentence_count if sentence_count else 0.0
    reading_time_minutes = word_count / 200 if word_count else 0.0

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "character_count": len(stripped),
        "average_sentence_length": round(avg_sentence_length, 2),
        "estimated_reading_time_minutes": round(max(reading_time_minutes, 0.1), 2),
    }


def _prepare_sentiment_section(sentiment: Dict[str, Any]) -> Dict[str, Any]:
    overall = sentiment.get("overall", {}) if isinstance(sentiment, dict) else {}
    distribution = sentiment.get("distribution", {}) if isinstance(sentiment, dict) else {}
    formatted_distribution = {
        key: {
            "value": _safe_percentage(distribution.get(key)),
            "percentage": _format_percentage(distribution.get(key)),
        }
        for key in ("positive", "neutral", "negative")
    }

    model_breakdown: List[Dict[str, Any]] = []
    for model in sentiment.get("models", []) if isinstance(sentiment, dict) else []:
        if not isinstance(model, dict):
            continue
        model_breakdown.append(
            {
                "name": model.get("name", "unknown"),
                "label": model.get("label"),
                "confidence": round(_safe_percentage(model.get("confidence")), 3),
                "weight": round(float(model.get("weight", 0.0)), 3),
            }
        )

    return {
        "dominant_label": overall.get("label"),
        "confidence": round(_safe_percentage(overall.get("confidence")), 3),
        "probability": round(_safe_percentage(overall.get("probability")), 3),
        "distribution": formatted_distribution,
        "model_breakdown": model_breakdown,
    }


def _prepare_topics_section(analysis: Dict[str, Any]) -> Dict[str, Any]:
    topics = analysis.get("topics") or []
    detailed = analysis.get("topic_details") or []
    narratives = analysis.get("topic_narratives") or []

    def _produce_topic_entry(topic: Dict[str, Any], rank: int) -> Dict[str, Any]:
        share_value = topic.get("share", topic.get("confidence", 0.0))
        return {
            "rank": rank,
            "label": topic.get("label", f"Topic {rank}"),
            "category_key": topic.get("category_key"),
            "share": round(_safe_percentage(share_value), 4),
            "share_pretty": _format_percentage(share_value),
            "confidence": round(_safe_percentage(topic.get("confidence")), 4),
            "keywords": topic.get("keywords", [])[:10],
            "mentions": topic.get("mentions"),
        }

    primary_topic = topics[0] if topics else None
    top_topics = [_produce_topic_entry(topic, idx + 1) for idx, topic in enumerate(topics[:6])]

    formatted_narratives: List[Dict[str, Any]] = []
    for item in narratives[:6]:
        if not isinstance(item, dict):
            continue
        formatted_narratives.append(
            {
                "title": item.get("title"),
                "sentiment_label": item.get("sentiment_label"),
                "snippet": item.get("snippet"),
                "keywords": item.get("keywords", [])[:8],
            }
        )

    return {
        "primary_topic": _produce_topic_entry(primary_topic, 1) if primary_topic else None,
        "top_topics": top_topics,
        "narratives": formatted_narratives,
        "detailed_topics": detailed,
    }


def _prepare_keywords_section(analysis: Dict[str, Any]) -> Dict[str, Any]:
    weighted = analysis.get("keyword_cloud_weighted")
    keywords: Iterable[Dict[str, Any]]
    if isinstance(weighted, list) and weighted:
        keywords = weighted
    else:
        cloud = analysis.get("keyword_cloud") or []
        keywords = [{"term": term, "score": max(1.0 - idx * 0.05, 0.1)} for idx, term in enumerate(cloud)]

    formatted = []
    for item in keywords:
        if not isinstance(item, dict):
            continue
        term = item.get("term")
        if not term:
            continue
        formatted.append(
            {
                "term": term,
                "score": round(_safe_percentage(item.get("score"), 0.0), 4),
            }
        )

    return {"keywords": formatted[:40]}


def generate_report(
    source_text: str,
    analysis: Dict[str, Any],
    *,
    metadata: Optional[Dict[str, Any]] = None,
    evaluation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a structured report dictionary from an analysis payload."""

    text_stats = _text_statistics(source_text)
    sentiment_section = _prepare_sentiment_section(analysis.get("sentiment", {}))
    topics_section = _prepare_topics_section(analysis)
    keywords_section = _prepare_keywords_section(analysis)

    extractive_summary = analysis.get("extractive_summary")
    abstractive_summary = analysis.get("abstractive_summary")

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    dominant_sentiment = sentiment_section.get("dominant_label")
    primary_topic = topics_section.get("primary_topic", {}) if topics_section else {}

    source_preview = source_text.strip().replace("\n", " ")[:240]

    report: Dict[str, Any] = {
        "generated_at": generated_at,
        "metadata": {
            "source": metadata or {},
            "text_statistics": text_stats,
            "source_preview": source_preview,
            "evaluation_metrics": evaluation or {},
        },
        "executive_summary": {
            "highlights": [highlight for highlight in [extractive_summary, abstractive_summary] if highlight],
            "dominant_sentiment": dominant_sentiment,
            "primary_topic": primary_topic,
        },
        "sentiment_overview": sentiment_section,
        "topic_intelligence": topics_section,
        "keyword_spotlight": keywords_section,
        "recommendations": analysis.get("suggestions", []),
        "raw_analysis": analysis,
    }

    return report


def report_to_markdown(report: Dict[str, Any]) -> str:
    """Convert a report dictionary to a Markdown string."""

    lines: List[str] = []
    generated_at = report.get("generated_at")
    lines.append("# Narrative Nexus Insight Report")
    if generated_at:
        lines.append(f"_Generated at: {generated_at}_")
    lines.append("")

    metadata = report.get("metadata", {})
    text_stats = metadata.get("text_statistics", {})
    if text_stats:
        lines.append("## Text Overview")
        lines.append(f"- Word count: {text_stats.get('word_count', 0)}")
        lines.append(f"- Sentence count: {text_stats.get('sentence_count', 0)}")
        lines.append(f"- Estimated reading time: {text_stats.get('estimated_reading_time_minutes', 0)} minutes")
        lines.append("")

    exec_summary = report.get("executive_summary", {})
    highlights = exec_summary.get("highlights", [])
    if highlights:
        lines.append("## Executive Summary")
        for idx, highlight in enumerate(highlights, start=1):
            lines.append(f"{idx}. {highlight}")
        lines.append("")

    sentiment = report.get("sentiment_overview", {})
    distribution = sentiment.get("distribution", {})
    if distribution:
        lines.append("## Sentiment Overview")
        lines.append(f"Dominant sentiment: **{sentiment.get('dominant_label', 'unknown').capitalize()}**")
        lines.append("")
        lines.append("| Sentiment | Share | Confidence |")
        lines.append("|-----------|-------|------------|")
        for label in ("positive", "neutral", "negative"):
            row = distribution.get(label, {})
            lines.append(
                f"| {label.capitalize()} | {row.get('percentage', '0%')} | {sentiment.get('confidence', 0):.2f} |"
            )
        lines.append("")

    topics = report.get("topic_intelligence", {})
    top_topics = topics.get("top_topics", [])
    if top_topics:
        lines.append("## Topic Highlights")
        for topic in top_topics:
            label = topic.get("label", "Topic")
            share = topic.get("share_pretty", "0%")
            keywords = ", ".join(topic.get("keywords", []))
            lines.append(f"- **{label}** ({share}) – {keywords}")
        lines.append("")

    narratives = topics.get("narratives", [])
    if narratives:
        lines.append("### Topic Narratives")
        for narrative in narratives:
            title = narrative.get("title", "Narrative")
            sentiment_label = narrative.get("sentiment_label", "neutral")
            snippet = narrative.get("snippet", "")
            lines.append(f"- **{title}** ({sentiment_label}) – {snippet}")
        lines.append("")

    keywords_section = report.get("keyword_spotlight", {})
    keywords = keywords_section.get("keywords", [])
    if keywords:
        lines.append("## Keyword Spotlight")
        keywords_preview = ", ".join(keyword.get("term") for keyword in keywords[:20])
        lines.append(keywords_preview)
        lines.append("")

    recommendations = report.get("recommendations", [])
    if recommendations:
        lines.append("## Recommendations")
        for recommendation in recommendations:
            lines.append(f"- {recommendation}")
        lines.append("")

    evaluation = metadata.get("evaluation_metrics")
    if evaluation:
        lines.append("## Model Evaluation Snapshot")
        lines.append("```json")
        lines.append(json.dumps(evaluation, indent=2))
        lines.append("```")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def report_to_pdf(report: Dict[str, Any], *, title: Optional[str] = None) -> bytes:
    """Render a report dictionary to a formatted PDF document."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=54,
        title=title or "Narrative Nexus Insight Report",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#312e81"),
        alignment=TA_LEFT,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=20,
        textColor=colors.HexColor("#4338ca"),
        spaceBefore=12,
        spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        "BodyText",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
    )
    muted_style = ParagraphStyle(
        "Muted",
        parent=normal_style,
        textColor=colors.grey,
        fontSize=10,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=normal_style,
        leftIndent=18,
        bulletIndent=9,
        bulletFontName="Helvetica",
        bulletFontSize=10,
    )
    code_style = ParagraphStyle(
        "Code",
        parent=normal_style,
        fontName="Courier",
        fontSize=9,
        leading=13,
    )

    doc_title = title or "Narrative Nexus Insight Report"
    generated_at = report.get("generated_at")

    elements: List[Any] = []
    elements.append(Paragraph(doc_title, title_style))
    if generated_at:
        elements.append(Paragraph(f"Generated on {generated_at}", muted_style))
    elements.append(Spacer(1, 16))

    metadata = report.get("metadata", {})
    text_stats = metadata.get("text_statistics", {})
    if text_stats:
        elements.append(Paragraph("Text Overview", heading_style))
        table_data = [
            ["Metric", "Value"],
            ["Word count", str(text_stats.get("word_count", "--"))],
            ["Sentence count", str(text_stats.get("sentence_count", "--"))],
            [
                "Estimated reading time",
                f"{text_stats.get('estimated_reading_time_minutes', '--')} minutes",
            ],
            ["Average sentence length", str(text_stats.get("average_sentence_length", "--"))],
        ]
        overview_table = Table(table_data, colWidths=[200, 220])
        overview_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2ff")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#312e81")),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c7d2fe")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ]
            )
        )
        elements.append(overview_table)

    exec_summary = report.get("executive_summary", {})
    highlights = exec_summary.get("highlights", [])
    if highlights:
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("Executive Summary", heading_style))
        for item in highlights:
            elements.append(Paragraph(item, bullet_style, bulletText="•"))

    sentiment = report.get("sentiment_overview", {})
    distribution = sentiment.get("distribution", {})
    if distribution:
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("Sentiment Overview", heading_style))
        dominant = sentiment.get("dominant_label")
        if dominant:
            elements.append(
                Paragraph(
                    f"Dominant sentiment: <b>{str(dominant).title()}</b>", normal_style
                )
            )

        sentiment_table_data = [["Sentiment", "Share", "Model confidence"]]
        confidence = sentiment.get("confidence")
        confidence_pretty = f"{confidence:.2f}" if isinstance(confidence, (float, int)) else "--"
        for label in ("positive", "neutral", "negative"):
            row = distribution.get(label, {})
            sentiment_table_data.append(
                [
                    label.title(),
                    row.get("percentage", "0%"),
                    confidence_pretty,
                ]
            )

        sentiment_table = Table(
            sentiment_table_data,
            colWidths=[140, 120, 120],
        )
        sentiment_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c7d2fe")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f3ff")]),
                ]
            )
        )
        elements.append(sentiment_table)

    topics = report.get("topic_intelligence", {})
    top_topics = topics.get("top_topics", [])
    if top_topics:
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("Topic Highlights", heading_style))
        for topic in top_topics:
            label = topic.get("label", "Topic")
            share = topic.get("share_pretty", "0%")
            keywords = ", ".join(topic.get("keywords", []))
            body = f"<b>{label}</b> ({share})"
            if keywords:
                body += f" — {keywords}"
            elements.append(Paragraph(body, bullet_style, bulletText="•"))

    narratives = topics.get("narratives", [])
    if narratives:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Topic Narratives", heading_style))
        for narrative in narratives:
            title_text = narrative.get("title", "Narrative")
            sentiment_label = narrative.get("sentiment_label", "neutral")
            snippet = narrative.get("snippet", "")
            content = f"<b>{title_text}</b> ({sentiment_label}) — {snippet}"
            elements.append(Paragraph(content, bullet_style, bulletText="•"))

    keywords_section = report.get("keyword_spotlight", {})
    keywords = keywords_section.get("keywords", [])
    if keywords:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Keyword Spotlight", heading_style))
        preview = ", ".join(keyword.get("term") for keyword in keywords[:25])
        elements.append(Paragraph(preview, normal_style))

    recommendations = report.get("recommendations", [])
    if recommendations:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Recommendations", heading_style))
        for rec in recommendations:
            elements.append(Paragraph(rec, bullet_style, bulletText="•"))
    else:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Recommendations", heading_style))
        elements.append(
            Paragraph(
                "No specific recommendations were generated for this analysis. Continue monitoring new inputs for emerging actions.",
                normal_style,
            )
        )

    evaluation = metadata.get("evaluation_metrics")
    if evaluation:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Model Evaluation Snapshot", heading_style))
        formatted = json.dumps(evaluation, indent=2, ensure_ascii=False)
        elements.append(Preformatted(formatted, code_style))

    def _header_footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        width, height = doc_obj.pagesize
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.setFillColor(colors.HexColor("#4338ca"))
        canvas_obj.drawString(doc_obj.leftMargin, height - doc_obj.topMargin + 30, "NarrativeNexus")
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawRightString(
            width - doc_obj.rightMargin,
            doc_obj.bottomMargin - 20,
            f"Page {canvas_obj.getPageNumber()}",
        )
        canvas_obj.restoreState()

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)

    buffer.seek(0)
    return buffer.getvalue()


def save_report(report: Dict[str, Any], output_path: Path | str, format: Optional[str] = None) -> Path:
    """Persist a report to disk in JSON or Markdown format."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fmt = (format or "").lower().strip()
    if not fmt:
        suffix = path.suffix.lower()
        if suffix in {".md", ".markdown"}:
            fmt = "markdown"
        else:
            fmt = "json"

    if fmt == "markdown" or fmt == "md":
        content = report_to_markdown(report)
        path.write_text(content, encoding="utf-8")
    elif fmt == "json":
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported report format: {format}")

    return path


__all__ = ["generate_report", "report_to_markdown", "report_to_pdf", "save_report"]
