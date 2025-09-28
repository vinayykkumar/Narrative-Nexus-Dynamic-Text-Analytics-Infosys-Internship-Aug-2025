# src/summarization.py
from __future__ import annotations
from typing import List, Optional
import re
import numpy as np
from functools import lru_cache



# ---- Configuration defaults ----
HF_ABS_DEFAULT = "sshleifer/distilbart-cnn-12-6"  # small, reasonably fast
EMBEDDING_MODEL = "all-MiniLM-L6-v2"            # sentence-transformers small model

# ---- Robust sentence splitting & chunking ----
_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9])')

def split_sentences(text: str, min_words: int = 5, fallback_chunk: int = 60) -> List[str]:
    """
    Split text into reasonable sentence-like units.
    - Normalizes newlines -> periods
    - Splits on punctuation; if punctuation missing returns chunked segments
    - Filters extremely short fragments (< min_words)
    """
    text = (text or "").strip()
    if not text:
        return []

    # Normalize newlines, multiple spaces
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)

    # Primary split: punctuation-aware
    sents = _SENT_SPLIT.split(text)
    cleaned = []
    for s in sents:
        s = s.strip()
        if not s:
            continue
        # trim stray non-word start/end
        s = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', s).strip()
        if not s:
            continue
        # keep longer fragments only; short fragments will be dropped
        if len(s.split()) >= min_words:
            cleaned.append(s)

    # If nothing parsed as sentences (no punctuation or all too short), fallback chunking
    if not cleaned:
        words = text.split()
        cleaned = [" ".join(words[i:i + fallback_chunk]) for i in range(0, len(words), fallback_chunk)]
        cleaned = [c for c in cleaned if len(c.split()) >= min_words]

    return cleaned

# ---- Helper to further chunk overly long sentences ----
def _word_chunk_sentences(sents: List[str], chunk_words: int = 60) -> List[str]:
    out = []
    for s in sents:
        words = s.split()
        if len(words) <= chunk_words:
            out.append(s)
        else:
            for i in range(0, len(words), chunk_words):
                piece = " ".join(words[i:i + chunk_words])
                if len(piece.split()) >= 5:
                    out.append(piece)
    return out

# ---- TF-IDF + MMR utilities (fast default extractive) ----
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def mmr_select(sentences: List[str], doc_scores: np.ndarray, k: int = 5, lambda_param: float = 0.7) -> List[str]:
    """
    MMR sentence selection to get relevance + diversity.
    - sentences: list of candidate sentence strings
    - doc_scores: 1d relevance scores (higher=more relevant)
    - Returns up to k selected sentences in original order
    """
    if not sentences:
        return []

    n = len(sentences)
    k = min(k, n)
    vec = TfidfVectorizer(stop_words='english', max_features=2000)
    X = vec.fit_transform(sentences)  # sparse
    sim = cosine_similarity(X)        # dense

    doc_scores = np.asarray(doc_scores).ravel()

    selected_idx = []
    remaining = list(range(n))

    # pick first by highest relevance
    first = int(np.argmax(doc_scores))
    selected_idx.append(first)
    remaining.remove(first)

    while len(selected_idx) < k and remaining:
        mmr_scores = []
        for j in remaining:
            relevance = doc_scores[j]
            diversity = max(sim[j][selected_idx]) if selected_idx else 0.0
            mmr_score = lambda_param * relevance - (1.0 - lambda_param) * diversity
            mmr_scores.append((mmr_score, j))
        mmr_scores.sort(reverse=True)
        _, pick = mmr_scores[0]
        selected_idx.append(pick)
        remaining.remove(pick)

    selected_idx_sorted = sorted(selected_idx)
    return [sentences[i] for i in selected_idx_sorted]

# ---- Paste these into src/summarization.py ----
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def dedupe_sentences(sentences: List[str], threshold: float = 0.78) -> List[str]:
    """
    Remove near-duplicate sentences from 'sentences' preserving order.
    Uses a small TF-IDF and cosine similarity threshold.
    """
    if not sentences:
        return []
    try:
        vec = TfidfVectorizer(stop_words='english', max_features=2000)
        X = vec.fit_transform(sentences)
        keep = []
        for i in range(len(sentences)):
            if not keep:
                keep.append(i)
                continue
            sims = cosine_similarity(X[i], X[keep]).ravel()
            if sims.max() < threshold:
                keep.append(i)
        return [sentences[i] for i in keep]
    except Exception:
        # if anything goes wrong, return original list (best-effort)
        return sentences


def summarize_with_mmr(
    text: str,
    k: int = 5,
    min_words: int = 6,
    chunk_words: int = 60,
    lambda_param: float = 0.7,
    use_embeddings: bool = False,
    embedding_model: str = EMBEDDING_MODEL
) -> str:
    """
    Improved extractive summarization using TF-IDF + MMR with:
      - stronger sentence filtering (min_words default 6),
      - greedy merge of short fragments,
      - deduplication of chosen sentences,
      - optional embeddings-based fallback if sentence-transformers is available.

    Parameters:
      text: source text
      k: target number of sentences to select
      min_words: minimum words for a candidate sentence (raise to avoid tiny fragments)
      chunk_words: chunk length for fallback chunking
      lambda_param: MMR tradeoff (0..1)
      use_embeddings: if True and sentence-transformers installed, prefer embedding-MMR
      embedding_model: embedding model name for sentence-transformers
    """
    if not text or not text.strip():
        return ""

    # --- 1) Sentence splitting (stricter) ---
    sents = split_sentences(text, min_words=max(3, min_words), fallback_chunk=chunk_words)
    if not sents:
        return ""

    # Merge neighboring short fragments to reduce noise (greedy)
    if len(sents) > 1:
        merged = []
        buf = ""
        for s in sents:
            if len(s.split()) < min_words:
                buf = (buf + " " + s).strip()
            else:
                if buf:
                    merged.append((buf + " " + s).strip())
                    buf = ""
                else:
                    merged.append(s)
        if buf:
            merged.append(buf)
        sents = merged

    # If after merging we have too few candidates for target k, chunk long sentences for more granularity
    avg_words = sum(len(s.split()) for s in sents) / max(1, len(sents))
    if len(sents) <= k and avg_words > (chunk_words * 1.5):
        sents = _word_chunk_sentences(sents, chunk_words=chunk_words)

    # final guard: filter extremely short candidates
    sents = [s for s in sents if len(s.split()) >= max(2, int(min_words/2))]
    if not sents:
        return ""

    # --- 2) Option A: Embedding-MMR (if requested and available) ---
    if use_embeddings:
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as _np
            model = SentenceTransformer(embedding_model)
            embeddings = model.encode(sents, convert_to_numpy=True, show_progress_bar=False)
            doc_emb = embeddings.mean(axis=0, keepdims=True)
            relevance = cosine_similarity(embeddings, doc_emb).ravel()
            # MMR with embeddings
            n = len(sents)
            k_local = min(k, n)
            sim = cosine_similarity(embeddings)
            selected_idx = []
            remaining = list(range(n))
            first = int(_np.argmax(relevance))
            selected_idx.append(first)
            remaining.remove(first)
            while len(selected_idx) < k_local and remaining:
                mmr_scores = []
                for j in remaining:
                    diversity = max(sim[j][selected_idx]) if selected_idx else 0.0
                    mmr_score = lambda_param * relevance[j] - (1.0 - lambda_param) * diversity
                    mmr_scores.append((mmr_score, j))
                mmr_scores.sort(reverse=True)
                _, pick = mmr_scores[0]
                selected_idx.append(pick)
                remaining.remove(pick)
            selected_idx_sorted = sorted(selected_idx)
            chosen = [sents[i] for i in selected_idx_sorted]
            # dedupe chosen
            chosen = dedupe_sentences(chosen, threshold=0.78)
            return " ".join(chosen)
        except Exception:
            # graceful fallback to TF-IDF method below
            pass

    # --- 3) TF-IDF MMR (default and robust fallback) ---
    try:
        vec = TfidfVectorizer(stop_words='english', max_features=3000)
        X = vec.fit_transform(sents)  # shape (n_sents, vocab)
        # doc_vec: average dense vector
        doc_vec = np.asarray(X.mean(axis=0)).ravel()
        scores = cosine_similarity(X, doc_vec.reshape(1, -1)).ravel()
    except Exception:
        # If TF-IDF fails for any reason, return first k cleaned sentences
        return " ".join(sents[:k])

    # apply MMR selection using existing mmr_select (keeps diversity)
    chosen = mmr_select(sents, scores, k=min(k, len(sents)), lambda_param=lambda_param)

    # --- 4) Deduplicate near-duplicates (final clean) ---
    chosen = dedupe_sentences(chosen, threshold=0.78)

    # Keep original order of chosen sentences and return
    return " ".join(chosen)
# ---- End paste ----


# ---- Optional: embeddings + MMR (higher quality; requires sentence-transformers) ----
def summarize_with_embeddings_mmr(text: str, k: int = 5, model_name: str = EMBEDDING_MODEL) -> str:
    """
    Higher-quality extractive summarizer using sentence embeddings + MMR.
    Install: pip install sentence-transformers
    """
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise RuntimeError("sentence-transformers required for embedding MMR. pip install sentence-transformers") from e

    sents = split_sentences(text)
    if not sents:
        return ""

    # chunk extremely long sentences
    sents = _word_chunk_sentences(sents, chunk_words=60)

    model = SentenceTransformer(model_name)
    embeddings = model.encode(sents, convert_to_numpy=True, show_progress_bar=False)
    doc_emb = embeddings.mean(axis=0, keepdims=True)
    relevance = cosine_similarity(embeddings, doc_emb).ravel()
    # MMR using embedding similarity for diversity
    n = len(sents)
    k = min(k, n)
    sim = cosine_similarity(embeddings)
    selected_idx = []
    remaining = list(range(n))
    first = int(np.argmax(relevance))
    selected_idx.append(first)
    remaining.remove(first)
    while len(selected_idx) < k and remaining:
        mmr_scores = []
        for j in remaining:
            diversity = max(sim[j][selected_idx]) if selected_idx else 0.0
            mmr_score = 0.7 * relevance[j] - 0.3 * diversity
            mmr_scores.append((mmr_score, j))
        mmr_scores.sort(reverse=True)
        _, pick = mmr_scores[0]
        selected_idx.append(pick)
        remaining.remove(pick)
    selected_idx_sorted = sorted(selected_idx)
    return " ".join([sents[i] for i in selected_idx_sorted])

# ---- Abstractive: cached model loader + two-stage polish ----
@lru_cache(maxsize=2)
def _load_summarizer(model_name: str = HF_ABS_DEFAULT):
    """
    Cached loader for HF seq2seq summarization models.
    Moves model to CUDA if available.
    """
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    tok = AutoTokenizer.from_pretrained(model_name)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    mdl.eval()
    if torch.cuda.is_available():
        mdl.to("cuda")
    return tok, mdl

def summarize_abstractive_polish(
    text: str,
    model_name: str = HF_ABS_DEFAULT,
    max_words: int = 120,
    min_words: int = 30
) -> str:
    """
    Two-stage abstractive summarization:
      1) Short extractive summary (MMR TF-IDF)
      2) Abstractive polish of that short text (cached HF model)
    This reduces hallucination and runtime.
    """
    if not text or not text.strip():
        return ""

    # 1) Short extractive (k tuned to target size)
    k = max(3, int(max(1, max_words // 30)))  # rough sentences count
    short = summarize_with_mmr(text, k=k)
    if len(short.split()) < 10:
        # fallback: take first k cleaned sentences
        sents = split_sentences(text)
        short = " ".join(sents[:k])

    # 2) Load cached summarizer and polish
    from transformers import pipeline
    tok, mdl = _load_summarizer(model_name)
    import torch
    device = 0 if torch.cuda.is_available() else -1
    summarizer = pipeline("summarization", model=mdl, tokenizer=tok, device=device)

    max_len = max(60, min(400, int(max_words * 1.2)))
    min_len = max(20, int(min_words * 0.6))
    out = summarizer(short, max_length=max_len, min_length=min_len, do_sample=False, truncation=True)
    return out[0]["summary_text"]

# ---- Orchestrator ----
def summarize(
    text: str,
    mode: str = "Extractive",
    max_sentences: int = 5,
    model_name: str = HF_ABS_DEFAULT,
    max_words: int = 120,
    min_words: int = 30,
    use_embeddings: bool = False
) -> str:
    """
    Top-level entry:
      - mode: "Extractive" or "Abstractive"
      - max_sentences: for extractive k
      - use_embeddings: if True and sentence-transformers is installed, uses embedding MMR
    """
    mode = (mode or "Extractive").lower()
    if mode.startswith("abs"):
        return summarize_abstractive_polish(text, model_name=model_name, max_words=max_words, min_words=min_words)
    if use_embeddings:
        try:
            return summarize_with_embeddings_mmr(text, k=max_sentences)
        except Exception:
            # fallback gracefully to TF-IDF MMR
            return summarize_with_mmr(text, k=max_sentences)
    return summarize_with_mmr(text, k=max_sentences)

# ---- Convenience: summarize list of docs (per-topic) ----
def summarize_docs_list(docs: List[str], mode: str = "Extractive", **kwargs) -> str:
    """
    Summarize a list of documents (e.g., docs for a topic) by joining them into a single text
    and calling summarize(...).
    """
    combined = " ".join(docs)
    # If combined is too short, just return extractive on combined
    return summarize(combined, mode=mode, **kwargs)


# ------------------------
# Topic-level summarization helpers 
# ------------------------
from typing import Dict, List, Tuple
import math

def _top_docs_for_topic_argmax(docs: List[str], theta: np.ndarray, topic: int, top_k: int = 50) -> List[str]:
    """Return docs whose argmax == topic, up to top_k (no particular sort)."""
    dom = np.argmax(theta, axis=1)
    idxs = np.where(dom == topic)[0].tolist()
    # limit to top_k (keep original order)
    idxs = idxs[:top_k]
    return [docs[i] for i in idxs]

def _top_docs_for_topic_weighted(docs: List[str], theta: np.ndarray, topic: int, top_k: int = 50) -> List[str]:
    """
    Return top_k docs for a topic by descending theta weight.
    This gives the most representative docs for that topic.
    """
    weights = theta[:, int(topic)]
    # get indices sorted by weight desc
    idxs = np.argsort(weights)[::-1]
    # filter out near-zero weights to avoid including unrelated docs
    idxs = [int(i) for i in idxs if weights[int(i)] > 0][:top_k]
    return [docs[i] for i in idxs]

def summarize_topic_docs_list(docs: List[str], mode: str = "Extractive", max_sentences: int = 5,
                              use_embeddings: bool = False, max_words: int = 120, min_words: int = 30) -> str:
    """
    Summarize a list of documents (docs: list[str]) into a single summary string.
    mode: "Extractive" or "Abstractive"
    """
    combined = " ".join(docs)
    if not combined.strip():
        return ""
    if (mode or "Extractive").lower().startswith("abs"):
        # abstractive polish: first do short extractive then polish
        return summarize_abstractive_polish(combined, max_words=max_words, min_words=min_words)
    else:
        return summarize(combined, mode="Extractive", max_sentences=max_sentences, use_embeddings=use_embeddings)

def summarize_all_topics_argmax(
    docs: List[str],
    theta: np.ndarray,
    n_topics: int,
    mode: str = "Extractive",
    top_k_docs_per_topic: int = 50,
    max_sentences: int = 5,
    use_embeddings: bool = False,
    max_words: int = 120,
    min_words: int = 30
) -> Dict[int, Dict[str, object]]:
    """
    For each topic (0..n_topics-1) gather docs assigned by argmax and produce a summary.
    Returns dict: {topic_idx: {"summary": str, "n_docs": int, "sample_docs": [..]}}
    """
    out = {}
    for t in range(n_topics):
        topic_docs = _top_docs_for_topic_argmax(docs, theta, t, top_k=top_k_docs_per_topic)
        n_docs = len(topic_docs)
        if n_docs == 0:
            out[t] = {"summary": "", "n_docs": 0, "sample_docs": []}
            continue
        summ = summarize_topic_docs_list(topic_docs, mode=mode, max_sentences=max_sentences,
                                         use_embeddings=use_embeddings, max_words=max_words, min_words=min_words)
        out[t] = {"summary": summ, "n_docs": n_docs, "sample_docs": topic_docs[:3]}
    return out

def summarize_all_topics_weighted(
    docs: List[str],
    theta: np.ndarray,
    n_topics: int,
    mode: str = "Extractive",
    top_k_docs_per_topic: int = 50,
    max_sentences: int = 5,
    use_embeddings: bool = False,
    max_words: int = 120,
    min_words: int = 30
) -> Dict[int, Dict[str, object]]:
    """
    For each topic gather the top-K docs by theta weight and summarize them.
    Returns dict: {topic_idx: {"summary": str, "n_docs_considered": int, "sample_docs": [..]}}
    """
    out = {}
    for t in range(n_topics):
        topic_docs = _top_docs_for_topic_weighted(docs, theta, t, top_k=top_k_docs_per_topic)
        n_docs = len(topic_docs)
        if n_docs == 0:
            out[t] = {"summary": "", "n_docs_considered": 0, "sample_docs": []}
            continue
        summ = summarize_topic_docs_list(topic_docs, mode=mode, max_sentences=max_sentences,
                                         use_embeddings=use_embeddings, max_words=max_words, min_words=min_words)
        out[t] = {"summary": summ, "n_docs_considered": n_docs, "sample_docs": topic_docs[:3]}
    return out


# ---- CPU-friendly extractive + small-polish helpers ----

# We keep these functions independent so they can be used from app.py

def extractive_with_embedding_mmr(text: str, k: int = 4, emb_model=None, lambda_param: float = 0.7) -> str:
    """
    Embedding-based MMR extractive summarizer.
    - text: source text
    - k: number of sentences to select
    - emb_model: sentence-transformers model (optional; pass None to let caller provide cached model)
    """
    # Lazy import to avoid heavy loads if unused
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
    except Exception as e:
        raise RuntimeError("sentence-transformers required. pip install sentence-transformers") from e

    sents = split_sentences(text, min_words=6, fallback_chunk=60)
    if not sents:
        return ""

    # allow caller to pass a model instance (recommended)
    if emb_model is None:
        emb_model = SentenceTransformer("all-mpnet-base-v2")

    embeddings = emb_model.encode(sents, convert_to_numpy=True, show_progress_bar=False)
    doc_emb = embeddings.mean(axis=0, keepdims=True)
    relevance = cosine_similarity(embeddings, doc_emb).ravel()

    # MMR selection (embedding similarity for diversity)
    n = len(sents)
    k_local = min(k, n)
    sim = cosine_similarity(embeddings)
    selected_idx = []
    remaining = list(range(n))
    first = int(np.argmax(relevance))
    selected_idx.append(first)
    remaining.remove(first)
    while len(selected_idx) < k_local and remaining:
        mmr_scores = []
        for j in remaining:
            diversity = max(sim[j][selected_idx]) if selected_idx else 0.0
            mmr_score = lambda_param * relevance[j] - (1.0 - lambda_param) * diversity
            mmr_scores.append((mmr_score, j))
        mmr_scores.sort(reverse=True)
        _, pick = mmr_scores[0]
        selected_idx.append(pick)
        remaining.remove(pick)
    selected_idx_sorted = sorted(selected_idx)
    chosen = [sents[i] for i in selected_idx_sorted]

    # Small dedupe pass (TF-IDF) to avoid near-duplicate sentences
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as _cos
        vec = TfidfVectorizer(stop_words='english', max_features=1000)
        X = vec.fit_transform(chosen)
        keep = []
        for i in range(len(chosen)):
            if not keep:
                keep.append(i)
                continue
            sims = _cos(X[i], X[keep]).ravel()
            if sims.max() < 0.78:
                keep.append(i)
        chosen = [chosen[i] for i in keep]
    except Exception:
        # if sklearn missing or fails, keep original chosen
        pass

    return " ".join(chosen)


def pipeline_topic_summary_cpu(
    docs: List[str],
    theta: np.ndarray,
    topic_idx: int,
    top_k: int = 25,
    emb_k: int = 4,
    emb_model=None,
    polish: bool = True,
    polish_pipeline=None
) -> dict:
    """
    For a given topic index:
      - pick top_k docs by theta weight,
      - generate an extractive summary (embeddings MMR),
      - optionally polish with a small HF model (polish_pipeline).
    Returns dict with keys: 'extractive', 'abstractive', 'sample_docs', 'n_docs_considered'
    """
    # defensive checks
    if docs is None or theta is None:
        return {"extractive": "", "abstractive": "", "sample_docs": [], "n_docs_considered": 0}

    idxs = np.argsort(theta[:, topic_idx])[::-1][:top_k]
    rep_docs = [docs[i] for i in idxs if isinstance(docs[i], str) and docs[i].strip()][:top_k]

    combined = " ".join(rep_docs)
    if not combined.strip():
        return {"extractive": "", "abstractive": "", "sample_docs": [], "n_docs_considered": len(rep_docs)}

    # extractive (embedding MMR) — prefer passed emb_model to avoid reloading
    try:
        extractive = extractive_with_embedding_mmr(combined, k=emb_k, emb_model=emb_model)
    except Exception as e:
        # fallback to TF-IDF MMR in your module if embeddings fail
        try:
            extractive = summarize_with_mmr(combined, k=emb_k)
        except Exception:
            extractive = " ".join(split_sentences(combined)[:emb_k])

    # polish if requested (polish_pipeline is an hf pipeline, cached by app.py)
    abstractive = extractive
    if polish and polish_pipeline is not None:
        try:
            out = polish_pipeline(extractive, max_length=180, min_length=40, truncation=True)
            abstractive = out[0]["summary_text"]
        except Exception:
            abstractive = extractive

    return {
        "extractive": extractive,
        "abstractive": abstractive,
        "sample_docs": rep_docs[:3],
        "n_docs_considered": len(rep_docs)
    }
