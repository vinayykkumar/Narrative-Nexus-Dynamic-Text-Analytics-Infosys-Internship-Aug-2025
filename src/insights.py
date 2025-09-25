# src/insights.py
from typing import Dict, Any
import joblib
import os
import numpy as np
from src.preprocessing import preprocess_series
from src.summarization import extractive_summary, abstractive_summary
from src.topic_modeling import fit_tfidf

MODEL_DIR = "../models"

def load_models():
    tfidf = joblib.load(os.path.join(MODEL_DIR,"tfidf_vectorizer.pkl"))
    nmf = joblib.load(os.path.join(MODEL_DIR,"nmf_model.pkl"))
    # load gensim LDA if needed separately
    return tfidf, nmf

def get_topics_for_doc(text: str, tfidf, nmf, n_top=3):
    vec = tfidf.transform([text])
    topic_dist = nmf.transform(vec)[0]
    top_idx = np.argsort(topic_dist)[::-1][:n_top]
    # Derive keywords for each topic if possible (using top features)
    feature_names = getattr(tfidf, 'get_feature_names_out', None)
    keywords = []
    if feature_names:
        feature_names = tfidf.get_feature_names_out()
        for i in top_idx:
            # top terms per topic
            comps = nmf.components_[i]
            top_terms = [feature_names[j] for j in comps.argsort()[-5:][::-1]]
            keywords.append(top_terms)
    result = []
    for rank, i in enumerate(top_idx):
        item = {"topic_id": int(i), "score": float(topic_dist[i])}
        if keywords:
            item["keywords"] = keywords[rank]
        result.append(item)
    return result

def generate_insights(text: str, sentiment_result: Dict[str, Any], tfidf=None, nmf=None):
    summ_ext = extractive_summary(text, max_sentences=3)
    try:
        summ_abs = abstractive_summary(text)
    except Exception:
        summ_abs = None
    topics = get_topics_for_doc(text, tfidf, nmf) if (tfidf and nmf) else []
    sentiment = sentiment_result
    # simple rule-based suggestions
    suggestions = []
    if sentiment.get("label") == "NEGATIVE" or sentiment.get("score",0) < 0.6:
        suggestions.append("Investigate causes of negative sentiment, prioritize frequently mentioned terms.")
    else:
        suggestions.append("Leverage positive trends; identify frequently mentioned strengths for promotion.")
    return {
        "extractive_summary": summ_ext,
        "abstractive_summary": summ_abs,
        "topics": topics,
        "sentiment": sentiment,
        "suggestions": suggestions
    }