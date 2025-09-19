# src/summarization.py
from transformers import pipeline
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Extractive (simple TF-IDF + sentence scoring)
def extractive_summary(text: str, max_sentences: int = 3):
    sents = sent_tokenize(text)
    if len(sents) <= max_sentences:
        return text
    tfidf = TfidfVectorizer(stop_words='english')
    X = tfidf.fit_transform(sents)
    scores = X.sum(axis=1).A1
    top_idx = np.argsort(scores)[-max_sentences:][::-1]
    top_idx = sorted(top_idx)  # keep original order
    summary = " ".join([sents[i] for i in top_idx])
    return summary

# Abstractive (Hugging Face)
_abstractive_summarizer = None
def get_abstractive_summarizer(model_name: str = "sshleifer/distilbart-cnn-12-6"):  # smaller/fast model
    global _abstractive_summarizer
    if _abstractive_summarizer is None:
        _abstractive_summarizer = pipeline("summarization", model=model_name, device=-1)
    return _abstractive_summarizer

def abstractive_summary(text: str, max_length:int = 130, min_length:int=30):
    s = get_abstractive_summarizer()
    # chunk if very long
    if len(text.split()) > 800:
        # naive chunking by sentences
        sents = sent_tokenize(text)
        chunks = []
        cur = []
        cur_len = 0
        for sent in sents:
            cur.append(sent)
            cur_len += len(sent.split())
            if cur_len > 400:
                chunks.append(" ".join(cur))
                cur = []
                cur_len = 0
        if cur:
            chunks.append(" ".join(cur))
        parts = []
        for c in chunks:
            out = s(c, max_length=max_length, min_length=min_length, truncation=True)[0]['summary_text']
            parts.append(out)
        return " ".join(parts)
    else:
        return s(text, max_length=max_length, min_length=min_length, truncation=True)[0]['summary_text']
