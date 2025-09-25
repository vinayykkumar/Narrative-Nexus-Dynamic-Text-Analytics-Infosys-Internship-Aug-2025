"""Summarization helpers with TF-IDF scoring and optional transformers."""

import os
import warnings

import nltk
import numpy as np
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Prefer PyTorch backend for transformers to avoid tensorflow imports
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
try:
    from transformers import pipeline
except Exception:
    pipeline = None  # Graceful fallback below


# Ensure punkt tokenizer is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)


def extractive_summary(text: str, max_sentences: int = 3) -> str:
    sentences = sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return text

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(sentences)
    scores = matrix.sum(axis=1).A1
    top_idx = np.argsort(scores)[-max_sentences:][::-1]
    top_idx = sorted(top_idx)
    return " ".join(sentences[i] for i in top_idx)


_abstractive_summarizer = None


def get_abstractive_summarizer(model_name: str = "sshleifer/distilbart-cnn-12-6"):
    """Return a CPU summarization pipeline, preferring PyTorch."""

    global _abstractive_summarizer
    if _abstractive_summarizer is not None:
        return _abstractive_summarizer

    if pipeline is None:
        warnings.warn("transformers unavailable; abstractive summarization disabled")
        return None

    try:
        _abstractive_summarizer = pipeline("summarization", model=model_name, device=-1, framework="pt")
        return _abstractive_summarizer
    except Exception as exc:
        warnings.warn(f"Failed to initialise abstractive summarizer: {exc}")
        _abstractive_summarizer = None
        return None


def _summarize_chunks(summarizer, sentences, max_length: int, min_length: int) -> str:
    parts = []
    chunk = []
    chunk_len = 0
    for sentence in sentences:
        chunk.append(sentence)
        chunk_len += len(sentence.split())
        if chunk_len > 400:
            text = " ".join(chunk)
            parts.append(summarizer(text, max_length=max_length, min_length=min_length, truncation=True)[0]["summary_text"])
            chunk = []
            chunk_len = 0
    if chunk:
        text = " ".join(chunk)
        parts.append(summarizer(text, max_length=max_length, min_length=min_length, truncation=True)[0]["summary_text"])
    return " ".join(parts)


def abstractive_summary(text: str, max_length: int = 130, min_length: int = 30) -> str:
    summarizer = get_abstractive_summarizer()
    if summarizer is None:
        raise RuntimeError("Abstractive summarizer not available")

    sentences = sent_tokenize(text)
    if len(text.split()) > 800:
        return _summarize_chunks(summarizer, sentences, max_length, min_length)

    return summarizer(text, max_length=max_length, min_length=min_length, truncation=True)[0]["summary_text"]
