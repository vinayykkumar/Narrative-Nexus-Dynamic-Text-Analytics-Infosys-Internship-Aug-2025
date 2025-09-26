"""Insight generation module combining summarisation, topics, and sentiment."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from src.summarization import extractive_summary, abstractive_summary
from src.preprocessing import clean_text


MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


def load_models(model_dir: Path | str = MODEL_DIR):
    """Load the TF-IDF vectorizer and NMF topic model."""

    model_path = Path(model_dir)
    tfidf = joblib.load(model_path / "tfidf_vectorizer.pkl")
    nmf = joblib.load(model_path / "nmf_model.pkl")
    return tfidf, nmf


def _feature_names(tfidf) -> Optional[np.ndarray]:
    if hasattr(tfidf, "get_feature_names_out"):
        return tfidf.get_feature_names_out()
    if hasattr(tfidf, "get_feature_names"):
        return np.array(tfidf.get_feature_names())
    return None


def get_topics_for_doc(text: str, tfidf, nmf, n_top: int = 3) -> List[Dict[str, Any]]:
    vec = tfidf.transform([text])
    topic_dist = nmf.transform(vec)[0]
    top_idx = np.argsort(topic_dist)[::-1][:n_top]

    feature_names = _feature_names(tfidf)
    keywords: List[List[str]] = []
    if feature_names is not None:
        for topic_id in top_idx:
            comps = nmf.components_[topic_id]
            terms = [feature_names[j] for j in comps.argsort()[-5:][::-1]]
            keywords.append(terms)

    topics: List[Dict[str, Any]] = []
    for rank, topic_id in enumerate(top_idx):
        item: Dict[str, Any] = {"topic_id": int(topic_id), "score": float(topic_dist[topic_id])}
        if keywords:
            item["keywords"] = keywords[rank]
        topics.append(item)
    return topics


def _extract_keywords(text: str, top_k: int = 15) -> List[str]:
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform([text])
    except ValueError:
        return []
    scores = matrix.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()
    top_indices = scores.argsort()[::-1][:top_k]
    return [feature_names[i] for i in top_indices]


def _normalise_sentiment(sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
    sentiment = sentiment_result.copy() if sentiment_result else {}
    label = sentiment.get("label")
    score = sentiment.get("score")

    overall = sentiment.get("overall", {}) if isinstance(sentiment.get("overall"), dict) else {}
    if label is None:
        label = overall.get("label")
    if score is None:
        score = overall.get("confidence")

    if label is not None:
        sentiment.setdefault("label", label)
    if score is not None:
        sentiment.setdefault("score", score)
    return sentiment


def generate_insights(text: str, sentiment_result: Dict[str, Any], tfidf=None, nmf=None) -> Dict[str, Any]:
    extractive = extractive_summary(text, max_sentences=3)
    try:
        abstractive = abstractive_summary(text)
    except Exception:
        abstractive = None

    topics = []
    if tfidf is not None and nmf is not None:
        topic_text = clean_text(text)
        topics = get_topics_for_doc(topic_text, tfidf, nmf)
    keywords = _extract_keywords(text)
    sentiment = _normalise_sentiment(sentiment_result)

    label = str(sentiment.get("label", "")).upper()
    score = sentiment.get("score")

    suggestions: List[str] = []
    if label == "NEGATIVE" or (isinstance(score, (int, float)) and score < 0.6):
        suggestions.append("Investigate causes of negative sentiment, prioritize frequently mentioned terms.")
    else:
        suggestions.append("Leverage positive trends; identify frequently mentioned strengths for promotion.")

    return {
        "extractive_summary": extractive,
        "abstractive_summary": abstractive,
        "topics": topics,
        "sentiment": sentiment,
        "suggestions": suggestions,
        "keyword_cloud": keywords,
    }