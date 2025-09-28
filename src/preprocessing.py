import re
import spacy
from collections import Counter

# Lightweight spaCy pipeline (disable heavy parts)
_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = str(text)
    # remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # remove emails
    text = re.sub(r'\S+@\S+', '', text)
    # normalize newlines
    text = re.sub(r'\s+', ' ', text)
    # strip control chars
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    # trim
    text = text.strip()

    def _filter_short_and_nonalpha(text_in: str) -> str:
        # remove non-word characters, keep letters/digits/space, collapse spaces
        text_in = re.sub(r'[^A-Za-z0-9\s]', ' ', text_in)
        text_in = re.sub(r'\s+', ' ', text_in).strip()
        # drop tokens with length <= 2
        tokens = [t for t in text_in.split() if len(t) > 2]
        return " ".join(tokens)

    cleaned_text = _filter_short_and_nonalpha(text)
    return cleaned_text


    

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
