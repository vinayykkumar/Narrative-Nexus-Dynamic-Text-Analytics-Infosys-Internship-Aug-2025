# src/sentiment.py
from __future__ import annotations
from typing import List, Dict, Any
import numpy as np

# ---------- Option A: VADER (lightweight, fast) ----------
def _ensure_vader():
    import nltk
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon")

def analyze_vader(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Returns [{label:'NEGATIVE|NEUTRAL|POSITIVE', score:float, raw:dict}, ...]
    """
    _ensure_vader()
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()

    out = []
    for t in texts:
        s = sia.polarity_scores(t or "")
        comp = s["compound"]
        if comp >= 0.05:
            label = "POSITIVE"
        elif comp <= -0.05:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"
        out.append({"label": label, "score": float(abs(comp)), "raw": s})
    return out

# ---------- Option B: Hugging Face (transformer, accurate) ----------
HF_DEFAULT = "cardiffnlp/twitter-roberta-base-sentiment-latest"

def analyze_hf(texts: List[str], model_name: str = HF_DEFAULT, batch_size: int = 16) -> List[Dict[str, Any]]:
    """
    Returns [{label:'NEGATIVE|NEUTRAL|POSITIVE', score:float}, ...]
    """
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    tok = AutoTokenizer.from_pretrained(model_name)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_name)
    mdl.eval()

    labels_map = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
    outs: List[Dict[str, Any]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        enc = tok(batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
        with torch.no_grad():
            logits = mdl(**enc).logits
            probs = torch.nn.functional.softmax(logits, dim=1).cpu().numpy()

        for p in probs:
            idx = int(np.argmax(p))
            outs.append({"label": labels_map[idx], "score": float(p[idx])})
    return outs

# ---------- Aggregations ----------
def distribution(labels: List[str]) -> Dict[str, int]:
    from collections import Counter
    c = Counter(labels)
    return {"NEGATIVE": c.get("NEGATIVE", 0),
            "NEUTRAL": c.get("NEUTRAL", 0),
            "POSITIVE": c.get("POSITIVE", 0)}

def dominant_topic_per_doc(theta: np.ndarray) -> np.ndarray:
    """ theta: (n_docs, n_topics) doc-topic weights → argmax topic per doc """
    return np.argmax(theta, axis=1)

def sentiment_by_topic(labels: List[str], theta: np.ndarray) -> Dict[int, Dict[str, int]]:
    """
    Aggregate 3-class sentiment counts per dominant topic.
    """
    dom = dominant_topic_per_doc(theta)
    result: Dict[int, Dict[str, int]] = {}
    for i, lab in enumerate(labels):
        t = int(dom[i])
        if t not in result:
            result[t] = {"NEGATIVE": 0, "NEUTRAL": 0, "POSITIVE": 0}
        result[t][lab] += 1
    return result

# append / replace at bottom of src/sentiment.py

from typing import Iterable, Tuple
import pandas as pd

def counts_to_pct(counts: Dict[str, int]) -> Dict[str, float]:
    total = sum(counts.values()) or 1
    return {k: (v / total) * 100.0 for k, v in counts.items()}

def overall_distribution_pct(labels: Iterable[str]) -> Dict[str, float]:
    """
    Returns percentages for NEGATIVE/NEUTRAL/POSITIVE across the entire labels list.
    """
    counts = distribution(list(labels))
    return counts_to_pct(counts)

def sentiment_by_topic_argmax(labels: Iterable[str], theta: np.ndarray) -> pd.DataFrame:
    """
    Aggregate sentiment by dominant (argmax) topic per document.
    Returns a DataFrame with columns:
    ['topic', 'NEGATIVE','NEUTRAL','POSITIVE','total_docs','neg_pct','neu_pct','pos_pct']
    topic is int (0-indexed)
    """
    dom = dominant_topic_per_doc(theta)
    rows = {}
    for i, lab in enumerate(labels):
        t = int(dom[i])
        if t not in rows:
            rows[t] = {"NEGATIVE": 0, "NEUTRAL": 0, "POSITIVE": 0}
        rows[t][lab] += 1

    out = []
    for t, bucket in sorted(rows.items()):
        total = sum(bucket.values()) or 1
        out.append({
            "topic": int(t),
            "NEGATIVE": bucket["NEGATIVE"],
            "NEUTRAL": bucket["NEUTRAL"],
            "POSITIVE": bucket["POSITIVE"],
            "total_docs": total,
            "neg_pct": (bucket["NEGATIVE"] / total) * 100.0,
            "neu_pct": (bucket["NEUTRAL"] / total) * 100.0,
            "pos_pct": (bucket["POSITIVE"] / total) * 100.0,
        })
    df = pd.DataFrame(out)
    return df

def sentiment_by_topic_weighted(labels: Iterable[str], theta: np.ndarray) -> pd.DataFrame:
    """
    Weighted aggregation: each doc contributes its sentiment to every topic
    proportional to the doc->topic weight in `theta`.
    theta shape: (n_docs, n_topics)
    labels: list of strings per doc ("NEGATIVE"/"NEUTRAL"/"POSITIVE")
    Returns DataFrame similar to sentiment_by_topic_argmax but using weighted sums.
    """
    n_docs, n_topics = theta.shape
    # initialize numeric accumulators
    neg = np.zeros(n_topics, dtype=float)
    neu = np.zeros(n_topics, dtype=float)
    pos = np.zeros(n_topics, dtype=float)
    total_weight = np.zeros(n_topics, dtype=float)

    label_map = {"NEGATIVE": "neg", "NEUTRAL": "neu", "POSITIVE": "pos"}

    for i, lab in enumerate(labels):
        w = theta[i]  # vector length n_topics
        total_weight += w
        if lab == "NEGATIVE":
            neg += w
        elif lab == "NEUTRAL":
            neu += w
        else:
            pos += w

    out = []
    for t in range(n_topics):
        tot_w = float(total_weight[t]) or 1.0
        out.append({
            "topic": int(t),
            "NEGATIVE": float(neg[t]),
            "NEUTRAL": float(neu[t]),
            "POSITIVE": float(pos[t]),
            "total_weight": float(tot_w),
            "neg_pct": (float(neg[t]) / tot_w) * 100.0,
            "neu_pct": (float(neu[t]) / tot_w) * 100.0,
            "pos_pct": (float(pos[t]) / tot_w) * 100.0,
        })
    df = pd.DataFrame(out)
    return df
