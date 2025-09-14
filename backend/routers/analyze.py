from fastapi import APIRouter, UploadFile, Form
from src.ml.topic_modeling import train_lda
from src.ml.sentiment_analysis import vader_sentiment
from src.ml.summarization import extractive_summary

import pandas as pd
import docx2txt
import PyPDF2
import io

router = APIRouter()

def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from txt, csv, pdf, docx"""
    file_bytes = file.file.read()

    if file.content_type == "text/plain":  # .txt
        return file_bytes.decode("utf-8", errors="ignore")

    elif file.content_type == "text/csv":  # .csv
        df = pd.read_csv(io.BytesIO(file_bytes))
        text_col = df.select_dtypes(include=["object"]).columns[0]
        return " ".join(df[text_col].dropna().astype(str).tolist())

    elif file.content_type == "application/pdf":  # .pdf
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":  # .docx
        buffer = io.BytesIO(file_bytes)
        return docx2txt.process(buffer)

    else:
        return ""

@router.post("/")
async def analyze(file: UploadFile = None, text: str = Form(None)):
    content = ""

    if file:
        content = extract_text_from_file(file)

    if text:
        content += f"\n{text}"

    if not content.strip():
        return {"error": "No text provided"}

    # --- Topic Modeling ---
    docs = [content]
    vec, lda = train_lda(docs, n_topics=3)
    feature_names = vec.get_feature_names_out()
    topics = []
    for idx, topic in enumerate(lda.components_):
        top_features = [feature_names[i] for i in topic.argsort()[:-6:-1]]
        topics.extend(top_features)

    # --- Sentiment ---
    sentiment_result = vader_sentiment(content)

    # --- Summarization (Sumy) ---
    summary = extractive_summary(content, sentence_count=3)

    return {
        "topics": topics,
        "sentiment": sentiment_result["label"],
        "summary": summary,
    }
