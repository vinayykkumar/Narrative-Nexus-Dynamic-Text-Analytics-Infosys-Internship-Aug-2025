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

from src.preprocessing import clean_text
from src.sentiment import get_sentiment_pipeline, analyze_texts
from src.summarization import extractive_summary, abstractive_summary
from src.insights import get_topics_for_doc, generate_insights

app = FastAPI(title="NarrativeNexus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = "../models"
tfidf = None
nmf = None
sent_pipeline = None

class TextIn(BaseModel):
    text: str

# -----------------------------
# Startup: Load models
# -----------------------------
@app.on_event("startup")
def load_all():
    global tfidf, nmf, sent_pipeline
    try:
        tfidf = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))
        nmf = joblib.load(os.path.join(MODEL_DIR, "nmf_model.pkl"))
        print("✅ Topic models loaded")
    except Exception as e:
        print("⚠️ Model load warning:", e)
    sent_pipeline = get_sentiment_pipeline()
    print("✅ Sentiment pipeline loaded")

# -----------------------------
# Text Endpoints
# -----------------------------
@app.post("/summarize")
async def summarize(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    ext = extractive_summary(cleaned)
    absum = abstractive_summary(cleaned)
    return {"extractive": ext, "abstractive": absum}

@app.post("/sentiment")
async def sentiment(payload: TextIn):
    txt = payload.text
    cleaned = clean_text(txt)
    out = analyze_texts(sent_pipeline, [cleaned])
    return {"sentiment": out[0]}

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
    sent = analyze_texts(sent_pipeline, [cleaned])[0]
    insights = generate_insights(cleaned, sent, tfidf, nmf)
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

        sent = analyze_texts(sent_pipeline, [text])[0]
        insights = generate_insights(text, sent, tfidf, nmf)
        return insights

    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
