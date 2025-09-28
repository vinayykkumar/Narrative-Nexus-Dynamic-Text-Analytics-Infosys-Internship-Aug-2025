# src/labeling.py
from __future__ import annotations
from typing import List, Optional
import re
from functools import lru_cache

# Candidate high-level labels (used by zero-shot fallback)
DEFAULT_CANDIDATE_LABELS = [
    "Technology", "Business", "Sports", "Politics", "Health",
    "Science", "Entertainment", "Crime", "World", "Environment",
    "Lifestyle", "Travel", "Education", "Opinion", "Other"
]

# Small heuristic keyword maps to boost fast labeling (lowercase tokens)
_LABEL_KEYWORDS = {
    "Technology": {"tech", "technology", "software", "app", "ai", "model", "device", "chip", "cloud", "gadget"},
    "Business": {"company", "business", "firm", "market", "shares", "revenue", "profit", "ceo", "stock", "industry"},
    "Sports": {"match", "season", "goal", "score", "league", "player", "coach", "cup", "win", "team", "premier"},
    "Politics": {"election", "minister", "government", "president", "policy", "parliament", "vote", "mp", "senate"},
    "Health": {"health", "hospital", "clinic", "patient", "disease", "doctor", "covid", "cancer", "treatment"},
    "Science": {"study", "research", "scientist", "lab", "experiment", "university", "research", "analysis"},
    "Entertainment": {"film", "movie", "tv", "music", "song", "premiere", "actor", "actress", "show"},
    "Crime": {"police", "murder", "arrest", "court", "charge", "robbery", "sentenced"},
    "World": {"international", "global", "country", "world", "minister", "u.s.", "ukraine", "afghanistan"},
    "Environment": {"climate", "environment", "emissions", "pollution", "sustain", "carbon"},
    "Lifestyle": {"travel", "food", "fashion", "style", "lifestyle", "vacation", "hotel"},
    "Education": {"school", "student", "university", "education", "teacher", "curriculum"},
    "Opinion": {"opinion", "column", "editorial", "op-ed", "view"}
}

_RE_TOKEN = re.compile(r'[^A-Za-z0-9\-]+')

def _sanitize_token(tok: str) -> str:
    tok = (tok or "").lower().strip()
    tok = _RE_TOKEN.sub('', tok)
    # drop short and clearly garbage tokens
    if len(tok) <= 2:
        return ""
    # drop tokens that are mostly digits
    alpha_count = sum(1 for ch in tok if ch.isalpha())
    if alpha_count < max(1, len(tok)//2):
        return ""
    return tok

def keyword_labeler(keywords: List[str]) -> str:
    """
    Fast rule-based label suggestion from a list of keywords (topic top terms).
    Returns a single label (one of DEFAULT_CANDIDATE_LABELS) or "Other".
    """
    if not keywords:
        return "Other"
    toks = [_sanitize_token(t) for t in (keywords or [])]
    toks = [t for t in toks if t]
    if not toks:
        return "Other"

    # score each high-level label by number of token hits (simple)
    scores = {}
    for label, kws in _LABEL_KEYWORDS.items():
        s = 0
        for t in toks:
            if t in kws:
                s += 2  # exact strong hit
            else:
                # partial match: e.g., 'premiere' matches 'premier' etc
                for kw in kws:
                    if kw in t or t in kw:
                        s += 1
                        break
        scores[label] = s

    # choose best label if score convincingly higher than others
    best_label = max(scores, key=lambda k: scores[k])
    best_score = scores[best_label]
    # second-best to check gap
    second_best_score = max(v for k,v in scores.items() if k != best_label)

    # thresholds tuned for safety:
    # - if best_score >= 3 -> strong match
    # - or if best_score >= 2 and gap >=1 -> acceptable
    if best_score >= 3 or (best_score >= 2 and (best_score - second_best_score) >= 1):
        return best_label

    return "Other"


# ------------------------------
# Zero-shot fallback (optional)
# ------------------------------
@lru_cache(maxsize=1)
def _load_zero_shot_pipeline(model_name: str = "facebook/bart-large-mnli"):
    """
    Lazily load transformers zero-shot pipeline and cache it.
    May be slow on first call (CPU).
    """
    try:
        from transformers import pipeline
    except Exception as e:
        raise RuntimeError("transformers not available for zero-shot labeling") from e
    # device=-1 => CPU; pipeline cached here
    return pipeline("zero-shot-classification", model=model_name, device=-1)

def zero_shot_label(text: str, candidate_labels: Optional[List[str]] = None, model_name: str = "facebook/bart-large-mnli", threshold: float = 0.45) -> str:
    """
    Use a zero-shot classifier to pick a label from candidate_labels.
    Returns top label if confidence > threshold, else "Other".
    """
    if not text or not text.strip():
        return "Other"
    cl = list(candidate_labels or DEFAULT_CANDIDATE_LABELS)
    try:
        pipe = _load_zero_shot_pipeline(model_name)
        out = pipe(text, cl, multi_class=False)
        # out has 'labels' (ordered) and 'scores'
        top_label = out['labels'][0] if out and 'labels' in out else None
        top_score = out['scores'][0] if out and 'scores' in out else 0.0
        if top_label and top_score >= threshold:
            return top_label
        # try relaxed threshold
        if top_label and top_score >= 0.33:
            return top_label
    except Exception:
        # transformers may fail on CPU or model not found — fall back
        return "Other"
    return "Other"

# src/labeling.py

from sentence_transformers import SentenceTransformer

def keyword_labeler(keywords):
    """
    Simple keyword-based labeler.
    Takes a list of topic keywords and returns a rough category.
    """
    kws = [k.lower() for k in keywords if isinstance(k, str)]
    if any(k in kws for k in ["game", "team", "match", "league", "player", "score"]):
        return "Sports"
    if any(k in kws for k in ["government", "minister", "policy", "election", "law"]):
        return "Politics"
    if any(k in kws for k in ["stock", "market", "trade", "company", "business"]):
        return "Business"
    if any(k in kws for k in ["doctor", "health", "disease", "treatment", "cancer"]):
        return "Health"
    if any(k in kws for k in ["science", "technology", "computer", "ai", "research"]):
        return "Technology"
    return "Other"


def get_emb_model(name: str = "all-mpnet-base-v2"):
    """
    Returns a sentence-transformers embedding model.
    Cached so it's only loaded once per session.
    """
    return SentenceTransformer(name)


# Optional: zero-shot labeler (if transformers available)
def zero_shot_label(text: str):
    try:
        from transformers import pipeline
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        labels = ["Sports", "Politics", "Business", "Health", "Technology", "Entertainment", "Other"]
        result = classifier(text, labels)
        return result["labels"][0]
    except Exception:
        return "Other"
