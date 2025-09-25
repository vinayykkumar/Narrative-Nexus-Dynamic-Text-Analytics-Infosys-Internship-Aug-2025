from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import joblib
import os
from typing import Optional
import io
import csv
from docx import Document
from PyPDF2 import PdfReader
from pathlib import Path
import sys

# Ensure project root is importable so `src.*` can be resolved when running directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.preprocessing import clean_text
from src.sentiment import get_sentiment_pipeline, analyze_texts
from src.summarization import extractive_summary, abstractive_summary
from src.insights import get_topics_for_doc, generate_insights

# Extra sentiment tools for richer output expected by FE
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# Ensure required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

app = FastAPI(title="NarrativeNexus API", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve models directory from project root
BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models"
tfidf = None
nmf = None
sent_pipeline = None
vader = SentimentIntensityAnalyzer()

class TextIn(BaseModel):
    text: str

class DocsIn(BaseModel):
    docs: list[str]

# -----------------------------
# Startup: Load models
# -----------------------------
@app.on_event("startup")
def load_all():
    global tfidf, nmf, sent_pipeline
    try:
        tfidf = joblib.load(str(MODEL_DIR / "tfidf_vectorizer.pkl"))
        nmf = joblib.load(str(MODEL_DIR / "nmf_model.pkl"))
        print("✅ Topic models loaded")
    except Exception as e:
        print("⚠️ Model load warning:", e)
    sent_pipeline = get_sentiment_pipeline()
    print("✅ Sentiment pipeline loaded")

# -----------------------------
# Health
# -----------------------------
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# -----------------------------
# Text Endpoints (prefixed with /api)
# -----------------------------
@app.post("/api/summarize")
async def summarize(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    ext = extractive_summary(cleaned)
    absum = None
    try:
        absum = abstractive_summary(cleaned)
    except Exception:
        absum = None
    # FE Summarization.jsx expects `summary`
    return {"summary": ext, "extractive": ext, "abstractive": absum}

@app.post("/api/sentiment")
async def sentiment(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    # Transformer sentiment (lowercase labels for FE compatibility)
    tr = analyze_texts(sent_pipeline, [cleaned], max_length=256)[0]
    tr_label = (tr.get("label") or "").lower()
    if tr_label in ("positive", "negative"):
        pass
    else:
        # map 'POSITIVE' -> 'positive'
        tr_label = tr_label.replace("positive", "positive").replace("negative", "negative").upper().lower()
        if tr_label not in ("positive", "negative", "neutral"):
            tr_label = "positive" if tr.get("score", 0.0) >= 0.5 else "negative"
    transformer = {"label": tr_label, "score": float(tr.get("score", 0.0))}

    # VADER
    vs = vader.polarity_scores(cleaned)
    # TextBlob
    tb = TextBlob(cleaned)
    textblob = {"polarity": float(tb.sentiment.polarity), "subjectivity": float(tb.sentiment.subjectivity)}

    return {"vader": vs, "textblob": textblob, "transformer": transformer}

@app.post("/api/topics")
async def topics(payload: TextIn, n_topics: Optional[int] = 3):
    txt = payload.text
    cleaned = clean_text(txt)
    if tfidf is None or nmf is None:
        return {"error": "Topic models not loaded. Train and place models in models/."}
    t = get_topics_for_doc(cleaned, tfidf, nmf, n_top=n_topics)
    return {"topics": t}

@app.post("/api/topic")
async def batch_topics(payload: DocsIn, n_topics: Optional[int] = 3):
    if tfidf is None or nmf is None:
        return {"error": "Topic models not loaded. Train and place models in models/."}
    results = []
    for txt in payload.docs:
        cleaned = clean_text(txt)
        results.append(get_topics_for_doc(cleaned, tfidf, nmf, n_top=n_topics))
    return {"topics": results}

@app.post("/api/analyze")
async def analyze(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    sent = analyze_texts(sent_pipeline, [cleaned], max_length=256)[0]
    insights = generate_insights(cleaned, sent, tfidf, nmf)
    return insights

@app.post("/api/preprocess")
async def preprocess(payload: TextIn):
    return {"cleaned": clean_text(payload.text)}

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

@app.post("/api/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        text = extract_text_from_file(file)
        if not text.strip():
            return {"error": "No text extracted from file."}

        sent = analyze_texts(sent_pipeline, [text], max_length=256)[0]
        insights = generate_insights(text, sent, tfidf, nmf)
        return insights

    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
