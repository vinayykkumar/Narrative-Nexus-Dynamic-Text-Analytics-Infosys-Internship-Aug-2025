from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import sys
from pathlib import Path
from typing import Optional
import io
import csv
from docx import Document
from PyPDF2 import PdfReader

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.preprocessing import clean_text
from src.sentiment import analyze_sentiment_text, load_sentiment_models, SentimentInferenceModels
from src.summarization import extractive_summary, abstractive_summary
from src.insights import load_models, get_topics_for_doc, generate_insights

app = FastAPI(title="NarrativeNexus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = ROOT_DIR / "models"
tfidf = None
nmf = None
sentiment_models: Optional[SentimentInferenceModels] = None

class TextIn(BaseModel):
    text: str

# -----------------------------
# Startup: Load models
# -----------------------------
@app.on_event("startup")
def load_all():
    global tfidf, nmf, sentiment_models
    if os.getenv("NARRATIVENEXUS_TEST_MODE") == "1":
        tfidf = None
        nmf = None
        sentiment_models = None
        print("⚠️ Running in test mode – models not loaded.")
        return

    try:
        tfidf, nmf = load_models(MODEL_DIR)
        print("✅ Topic models loaded")
    except Exception as e:
        tfidf = None
        nmf = None
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
async def topics(payload: TextIn, n_topics: Optional[int] = 3):
    txt = payload.text
    cleaned = clean_text(txt)
    if tfidf is None or nmf is None:
        return {"error": "Topic models not loaded. Train and place models in ../models."}
    t = get_topics_for_doc(cleaned, tfidf, nmf, n_top=n_topics)
    return {"topics": t}

@app.post("/analyze")
async def analyze(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    sent = analyze_sentiment_text(cleaned, sentiment_models)
    insights = generate_insights(txt, sent, tfidf, nmf)
    return insights

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

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        text = extract_text_from_file(file)
        if not text.strip():
            return {"error": "No text extracted from file."}

        cleaned = clean_text(text)
        sent = analyze_sentiment_text(cleaned, sentiment_models)
        insights = generate_insights(text, sent, tfidf, nmf)
        return insights

    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)