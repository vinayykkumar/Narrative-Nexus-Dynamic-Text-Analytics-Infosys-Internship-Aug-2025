from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import io
import csv
import re
from datetime import datetime
from docx import Document
from PyPDF2 import PdfReader

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.preprocessing import clean_text
from src.sentiment import analyze_sentiment_text, load_sentiment_models, SentimentInferenceModels
from src.summarization import extractive_summary, abstractive_summary
from src.insights import TopicModels, load_models, get_topics_for_doc, generate_insights
from src.reporting import generate_report, report_to_markdown, report_to_pdf

app = FastAPI(title="NarrativeNexus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = ROOT_DIR / "models"
topic_models: Optional[TopicModels] = None
sentiment_models: Optional[SentimentInferenceModels] = None

class TextIn(BaseModel):
    text: str


class ReportIn(BaseModel):
    text: str
    include_markdown: bool = False
    include_analysis: bool = False
    metadata: Optional[dict] = None
    evaluation: Optional[dict] = None


def _safe_slug(value: Optional[str], fallback: str = "narrative-report") -> str:
    if not value:
        return fallback
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return cleaned or fallback

# -----------------------------
# Startup: Load models
# -----------------------------
@app.on_event("startup")
def load_all():
    global topic_models, sentiment_models
    if os.getenv("NARRATIVENEXUS_TEST_MODE") == "1":
        topic_models = None
        sentiment_models = None
        print("⚠️ Running in test mode – models not loaded.")
        return

    try:
        topic_models = load_models(MODEL_DIR)
        print("✅ Topic models loaded")
    except Exception as e:
        topic_models = None
        print("⚠️ Model load warning:", e)
    sentiment_models = load_sentiment_models(MODEL_DIR)
    print("✅ Sentiment models ready")

# -----------------------------
# Text Endpoints
# -----------------------------
@app.post("/summarize")
async def summarize(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    ext = extractive_summary(txt)
    try:
        absum = abstractive_summary(txt)
    except Exception:
        absum = None
    return {"extractive": ext, "abstractive": absum}

@app.post("/sentiment")
async def sentiment(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    out = analyze_sentiment_text(cleaned, sentiment_models)
    return out

@app.post("/topics")
async def topics(payload: TextIn, n_topics: Optional[int] = 6):
    txt = payload.text
    cleaned = clean_text(txt)
    if topic_models is None:
        return {"error": "Topic models not loaded. Train and place models in ../models."}
    requested_topics = 6
    if n_topics is not None:
        try:
            requested_topics = max(1, int(n_topics))
        except (TypeError, ValueError):
            requested_topics = 6

    bundle = get_topics_for_doc(cleaned, topic_models, n_top=requested_topics)
    return {
        "topics": bundle.get("summary", []),
        "primary_topic": bundle.get("primary"),
        "topic_details": bundle.get("detailed", []),
        "total_topics": len(bundle.get("detailed", [])) if isinstance(bundle, dict) else 0,
        "model_topics": bundle.get("model_topics", {}),
    }

@app.post("/analyze")
async def analyze(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    sent = analyze_sentiment_text(cleaned, sentiment_models)
    insights = generate_insights(
        txt,
        sent,
        topic_models=topic_models,
        sentiment_models=sentiment_models,
    )
    return insights


@app.post("/report")
async def report(payload: ReportIn):
    txt = payload.text
    cleaned = clean_text(txt)
    sent = analyze_sentiment_text(cleaned, sentiment_models)
    insights = generate_insights(
        txt,
        sent,
        topic_models=topic_models,
        sentiment_models=sentiment_models,
    )
    report_payload = generate_report(
        txt,
        insights,
        metadata=payload.metadata,
        evaluation=payload.evaluation,
    )
    response: Dict[str, Any] = {"report": report_payload}
    if payload.include_markdown:
        response["markdown"] = report_to_markdown(report_payload)
    if payload.include_analysis:
        response["analysis"] = insights
    return response


@app.post("/report/pdf")
async def report_pdf(payload: ReportIn):
    txt = payload.text
    if not txt.strip():
        raise HTTPException(status_code=400, detail="Text is required to generate the report.")

    cleaned = clean_text(txt)
    sent = analyze_sentiment_text(cleaned, sentiment_models)
    insights = generate_insights(
        txt,
        sent,
        topic_models=topic_models,
        sentiment_models=sentiment_models,
    )
    report_payload = generate_report(
        txt,
        insights,
        metadata=payload.metadata,
        evaluation=payload.evaluation,
    )

    title = None
    if isinstance(payload.metadata, dict):
        source_title = payload.metadata.get("title") or payload.metadata.get("name")
        if isinstance(source_title, str):
            title = source_title.strip() or None

    pdf_bytes = report_to_pdf(report_payload, title=title)
    filename = f"{_safe_slug(title) if title else 'narrative-report'}-{datetime.utcnow():%Y%m%d%H%M%S}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)

# -----------------------------
# File Upload Endpoint
# -----------------------------
def extract_text_from_file(file: UploadFile) -> str:
    content = file.file.read()

    if file.filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    elif file.filename.endswith(".csv"):
        decoded = content.decode("utf-8", errors="ignore").splitlines()
        reader = csv.reader(decoded)
        rows = [" ".join(row) for row in reader]
        return " ".join(rows)

    elif file.filename.endswith(".docx"):
        with io.BytesIO(content) as buffer:
            doc = Document(buffer)
            return " ".join([p.text for p in doc.paragraphs])

    elif file.filename.endswith(".pdf"):
        text = ""
        with io.BytesIO(content) as buffer:
            reader = PdfReader(buffer)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    else:
        raise ValueError("Unsupported file type")


@app.post("/report/pdf/file")
async def report_pdf_from_file(file: UploadFile = File(...)):
    try:
        text = extract_text_from_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from the uploaded file.")

    cleaned = clean_text(text)
    sent = analyze_sentiment_text(cleaned, sentiment_models)
    insights = generate_insights(
        text,
        sent,
        topic_models=topic_models,
        sentiment_models=sentiment_models,
    )
    report_payload = generate_report(text, insights, metadata={"filename": file.filename})

    title = file.filename.rsplit(".", 1)[0] if file.filename else None
    pdf_bytes = report_to_pdf(report_payload, title=title)
    safe_title = _safe_slug(title)
    filename = f"{safe_title}-{datetime.utcnow():%Y%m%d%H%M%S}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        text = extract_text_from_file(file)
        if not text.strip():
            return {"error": "No text extracted from file."}

        cleaned = clean_text(text)
        sent = analyze_sentiment_text(cleaned, sentiment_models)
        insights = generate_insights(
            text,
            sent,
            topic_models=topic_models,
            sentiment_models=sentiment_models,
        )
        return insights

    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)