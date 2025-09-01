import re
import spacy
from collections import Counter

# Lightweight spaCy pipeline (disable heavy parts)
_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

def clean_text(text: str, chunk_size: int = 50_000) -> str:
    """
    Lowercase, keep letters/spaces, lemmatize, drop stopwords.
    Processes large text in chunks to avoid memory issues.
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)

    tokens = []
    for i in range(0, len(text), chunk_size):
        doc = _nlp(text[i:i + chunk_size])
        tokens.extend([t.lemma_ for t in doc if t.is_alpha and not t.is_stop])

    return " ".join(tokens)

def summarize_text_stats(cleaned_text: str):
    words = cleaned_text.split()
    total = len(words)
    uniq = len(set(words))
    avg_len = round(sum(len(w) for w in words) / max(total, 1), 2)
    top_k = Counter(words).most_common(10)
    return {
        "total_chars": len(cleaned_text),
        "total_words": total,
        "unique_words": uniq,
        "avg_word_len": avg_len,
        "top_10_terms": ", ".join([f"{w}({c})" for w, c in top_k]),
    }
