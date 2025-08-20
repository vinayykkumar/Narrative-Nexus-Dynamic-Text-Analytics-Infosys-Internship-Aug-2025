from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import joblib

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from gensim.corpora import Dictionary
from gensim.models import LdaModel

import spacy
import spacy.cli

# -----------------------------------------------------------------------------
# Paths & Logging
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SENTIMENT_MODEL_PATH = BASE_DIR / "sentiment_analysis_model.pkl"
SENTIMENT_VECTORIZER_PATH = BASE_DIR / "sentiment_analysis_vectorizer.pkl"
SUMM_MODEL_DIR = BASE_DIR / "t5_summarization_model"
TOPIC_MODEL_PATH = BASE_DIR / "topic_modeling_model.model"
TOPIC_DICTIONARY_PATH = BASE_DIR / "topic_modeling_dictionary.dict"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml.app")

# -----------------------------------------------------------------------------
# FastAPI App
# -----------------------------------------------------------------------------
app = FastAPI(title="NLP Model Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Global model holders (lazy-loaded)
# -----------------------------------------------------------------------------
_sentiment_model = None
_sentiment_vectorizer = None
_summarizer_tokenizer = None
_summarizer_model = None
_lda_model = None
_lda_dictionary = None
_spacy_nlp = None

# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------
class SentimentRequest(BaseModel):
    text: str

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 150
    min_length: int = 40
    num_beams: int = 4
    length_penalty: float = 2.0

class TopicsRequest(BaseModel):
    text: str
    top_k: int = 3
    topn_terms: int = 10

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def ensure_spacy() -> spacy.language.Language:
    global _spacy_nlp
    if _spacy_nlp is not None:
        return _spacy_nlp
    try:
        _spacy_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    except OSError:
        logger.info("Downloading spaCy model en_core_web_sm...")
        spacy.cli.download("en_core_web_sm")
        _spacy_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    return _spacy_nlp


def preprocess_tm_text(text: str) -> List[str]:
    nlp = ensure_spacy()
    doc = nlp(text)
    return [t.lemma_ for t in doc if not t.is_stop and not t.is_punct]


def load_sentiment() -> None:
    global _sentiment_model, _sentiment_vectorizer
    if _sentiment_model is None or _sentiment_vectorizer is None:
        if not SENTIMENT_MODEL_PATH.exists() or not SENTIMENT_VECTORIZER_PATH.exists():
            raise FileNotFoundError("Sentiment model/vectorizer not found. Train and save them first.")
        _sentiment_model = joblib.load(SENTIMENT_MODEL_PATH)
        _sentiment_vectorizer = joblib.load(SENTIMENT_VECTORIZER_PATH)
        logger.info("Loaded sentiment model and vectorizer.")


def load_summarizer() -> None:
    global _summarizer_model, _summarizer_tokenizer
    if _summarizer_model is None or _summarizer_tokenizer is None:
        # Prefer local fine-tuned dir; fallback to base model
        model_id = str(SUMM_MODEL_DIR) if SUMM_MODEL_DIR.exists() else "t5-small"
        _summarizer_tokenizer = AutoTokenizer.from_pretrained(model_id)
        _summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        logger.info("Loaded summarization model: %s", model_id)


def load_topics() -> None:
    global _lda_model, _lda_dictionary
    if _lda_model is None or _lda_dictionary is None:
        if not TOPIC_MODEL_PATH.exists() or not TOPIC_DICTIONARY_PATH.exists():
            raise FileNotFoundError("Topic model/dictionary not found. Train and save them first.")
        _lda_dictionary = Dictionary.load(str(TOPIC_DICTIONARY_PATH))
        _lda_model = LdaModel.load(str(TOPIC_MODEL_PATH))
        logger.info("Loaded LDA model and dictionary.")


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "models": {
            "sentiment": SENTIMENT_MODEL_PATH.exists() and SENTIMENT_VECTORIZER_PATH.exists(),
            "summarizer": SUMM_MODEL_DIR.exists(),
            "topics": TOPIC_MODEL_PATH.exists() and TOPIC_DICTIONARY_PATH.exists(),
        },
    }


@app.post("/sentiment")
def sentiment(req: SentimentRequest) -> Dict[str, Any]:
    try:
        load_sentiment()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment model not available: {e}")

    vec = _sentiment_vectorizer.transform([req.text])
    label = _sentiment_model.predict(vec)[0]

    # Probabilities if available
    probs = None
    if hasattr(_sentiment_model, "predict_proba"):
        proba = _sentiment_model.predict_proba(vec)[0]
        classes = list(getattr(_sentiment_model, "classes_", []))
        probs = {str(c): float(p) for c, p in zip(classes, proba)}

    return {
        "label": str(label),
        "probabilities": probs,
    }


@app.post("/summarize")
def summarize(req: SummarizeRequest) -> Dict[str, Any]:
    try:
        load_summarizer()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarizer not available: {e}")

    prefix = "summarize: " if getattr(_summarizer_model.config, "model_type", "") == "t5" else ""
    inputs = _summarizer_tokenizer.encode(
        prefix + req.text,
        return_tensors="pt",
        max_length=512,
        truncation=True,
    )
    outputs = _summarizer_model.generate(
        inputs,
        max_length=req.max_length,
        min_length=req.min_length,
        num_beams=req.num_beams,
        length_penalty=req.length_penalty,
        early_stopping=True,
    )
    summary = _summarizer_tokenizer.decode(outputs[0], skip_special_tokens=True)

    return {"summary": summary}


@app.post("/topics")
def topics(req: TopicsRequest) -> Dict[str, Any]:
    try:
        load_topics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic model not available: {e}")

    tokens = preprocess_tm_text(req.text)
    bow = _lda_dictionary.doc2bow(tokens)
    doc_topics: List[Tuple[int, float]] = _lda_model.get_document_topics(bow)
    doc_topics = sorted(doc_topics, key=lambda x: x[1], reverse=True)

    # Prepare top-k topics with their top terms
    top = []
    for topic_id, prob in doc_topics[: max(req.top_k, 0) or 3]:
        terms = _lda_model.show_topic(topic_id, topn=max(req.topn_terms, 1))
        top.append(
            {
                "topic_id": int(topic_id),
                "probability": float(prob),
                "top_terms": [{"term": t, "weight": float(w)} for t, w in terms],
            }
        )

    return {"topics": top}


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
