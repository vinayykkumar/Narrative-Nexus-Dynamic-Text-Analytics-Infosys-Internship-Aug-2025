from __future__ import annotations

from typing import Dict, List, Tuple

import re

def _split_sentences(text: str) -> List[str]:
    # Lightweight sentence splitter
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if s.strip()]

def _score_sentences_tfidf(sentences: List[str]) -> Dict[str, float]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
    except Exception:
        return {s: 1.0 for s in sentences}
    if not sentences:
        return {}
    vect = TfidfVectorizer(stop_words="english")
    X = vect.fit_transform(sentences)
    scores = X.sum(axis=1).A.ravel()
    return {sentences[i]: float(scores[i]) for i in range(len(sentences))}

def _score_sentences_frequency(sentences: List[str]) -> Dict[str, float]:
    """Score sentences by raw term frequency (stopword-filtered), length-normalized.

    No external dependencies; uses a lightweight stopword set and regex tokenization.
    """
    if not sentences:
        return {}

    # Minimal English stopword list to avoid heavy NLTK dependency
    STOPWORDS = {
        "a","an","the","and","or","but","if","while","with","of","at","by","for","to","in","on","from","as","is","are","was","were","be","been","being","it","this","that","these","those","i","you","he","she","they","we","me","him","her","them","us","my","your","his","their","our","yours","hers","theirs","ours","not","so","than","too","very","can","could","should","would","may","might","will","just","about","into","over","after","before","between","through","also","more","most","some","such","no","nor","only","own","same","both","each","few","other","which","who","whom","what","when","where","why","how"
    }

    def tokenize(s: str) -> List[str]:
        return re.findall(r"[a-zA-Z]+", s.lower())

    # Build frequency table
    freq: Dict[str, int] = {}
    tokenized_sentences: List[List[str]] = []
    for s in sentences:
        toks = [t for t in tokenize(s) if t not in STOPWORDS]
        tokenized_sentences.append(toks)
        for t in toks:
            freq[t] = freq.get(t, 0) + 1

    if not freq:
        return {s: 0.0 for s in sentences}

    # Score sentences: sum of term frequencies, normalized by sentence length to reduce bias
    scores: Dict[str, float] = {}
    for i, s in enumerate(sentences):
        toks = tokenized_sentences[i]
        raw = sum(freq.get(t, 0) for t in toks)
        length = max(1, len(toks))
        scores[s] = raw / float(length)
    return scores

def _abstractive_summary(text: str, max_tokens: int = 128, model_name: str = "sshleifer/distilbart-cnn-12-6") -> str:
    """Run abstractive summarization with basic chunking.

    If transformers isn't available at runtime, raises a RuntimeError to allow
    caller to fallback gracefully.
    """
    try:
        from transformers import pipeline
    except Exception as exc:  # pragma: no cover - env dependent
        raise RuntimeError("transformers is not installed; cannot run abstractive summary") from exc

    summarizer = pipeline("summarization", model=model_name)

    # Determine a safe input token length from the model/tokenizer (fallback to 1024)
    try:
        tokenizer = summarizer.tokenizer
        model_max_len = getattr(tokenizer, "model_max_length", 1024) or 1024
        # Some models report very large sentinel values (e.g., 10000000000000); clamp it
        if model_max_len and model_max_len > 4096:
            model_max_len = 1024
    except Exception:
        model_max_len = 1024

    # Tokenizer-aware chunking: split by sentences and pack into chunks under model_max_len
    sentences = _split_sentences(text)
    if not sentences:
        return ""

    chunks: List[str] = []
    current: List[str] = []

    def tokens_count(s: str) -> int:
        try:
            # Avoid special tokens to get raw input length
            return len(summarizer.tokenizer.encode(s, add_special_tokens=False))
        except Exception:
            # Fallback approximation: 1 token ~= 4 chars (very rough)
            return max(1, len(s) // 4)

    for sent in sentences:
        candidate = (" ".join(current + [sent])).strip()
        if tokens_count(candidate) <= max(512, int(0.9 * model_max_len)):
            current.append(sent)
        else:
            if current:
                chunks.append(" ".join(current).strip())
            current = [sent]
    if current:
        chunks.append(" ".join(current).strip())

    summaries: List[str] = []
    for ch in chunks:
        result = summarizer(
            ch,
            max_length=max_tokens,
            min_length=max(16, max_tokens // 4),
            do_sample=False,
            truncation=True,
        )
        summaries.append(result[0]["summary_text"].strip())

    combined = " ".join(summaries).strip()

    # If we had multiple chunks, do a second pass to compress the combined text a bit
    if len(chunks) > 1 and len(combined) > 0:
        result2 = summarizer(
            combined,
            max_length=max_tokens,
            min_length=max(16, max_tokens // 4),
            do_sample=False,
            truncation=True,
        )
        combined = result2[0]["summary_text"].strip()

    return combined

def summarize_text(
    text: str,
    method: str = "abstractive",
    max_sentences: int = 3,
    max_tokens: int = 128,
    model_name: str = "facebook/bart-large-cnn",
) -> Tuple[str, List[str], Dict[str, float], str]:
    """
    Returns: (summary, key_sentences, sentence_scores, method_used)
    """
    sentences = _split_sentences(text)
    # Choose scoring based on method to ensure UI reflects the correct scores
    if method == "frequency":
        sentence_scores = _score_sentences_frequency(sentences)
    else:
        sentence_scores = _score_sentences_tfidf(sentences)
    key_sentences = [s for s, _ in sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:max_sentences]]

    if method == "abstractive":
        try:
            summary = _abstractive_summary(text, max_tokens=max_tokens, model_name=model_name)
            used = f"abstractive:{model_name}"
        except RuntimeError:
            # Graceful fallback if transformers isn't installed
            summary = " ".join(key_sentences)
            used = "extractive:tfidf(fallback)"
    elif method == "tfidf":
        summary = " ".join(key_sentences)
        used = "extractive:tfidf"
    elif method == "frequency":
        summary = " ".join(key_sentences)
        used = "extractive:frequency"
    else:
        summary = " ".join(key_sentences)
        used = f"extractive:{method}"

    return summary, key_sentences, sentence_scores, used
