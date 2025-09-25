# src/preprocessing.py
import os
import re
from typing import List, Optional

import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Try to ensure stopwords are available without re-downloading every run
try:
    _ = stopwords.words('english')
except LookupError:
    nltk.download('stopwords', quiet=True)

STOPWORDS = set(stopwords.words('english'))
PORTER = PorterStemmer()

# Lazy spaCy loader to avoid heavy startup when not needed
_SPACY_NLP = None
def _get_spacy_nlp():
    global _SPACY_NLP
    if _SPACY_NLP is None:
        try:
            import spacy
            _SPACY_NLP = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        except Exception as e:
            _SPACY_NLP = None
    return _SPACY_NLP

def load_csvs(paths: List[str], text_column: str = 'text') -> pd.DataFrame:
    dfs = []
    for p in paths:
        df = pd.read_csv(p)
        if text_column not in df.columns:
            # try some common variants
            for cand in ['text', 'content', 'article', 'review']:
                if cand in df.columns:
                    df = df.rename(columns={cand: 'text'})
                    break
        df = df[[c for c in df.columns if c == 'text' or c == 'label' or c == 'title']]
        df['source_file'] = p
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True).dropna(subset=['text']).reset_index(drop=True)
    return data

def clean_text(text: str) -> str:
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'[^A-Za-z0-9\s\.,!?\'"]+', ' ', text)
    text = text.strip().lower()
    return text

def _porter_stem_text(text: str) -> str:
    # keep alphabetic tokens only for stemming
    tokens = re.findall(r"[a-zA-Z]+", text)
    out = []
    for tok in tokens:
        t = tok.lower()
        if t in STOPWORDS or len(t) <= 1:
            continue
        out.append(PORTER.stem(t))
    return " ".join(out)

def _spacy_lemmatize_texts(texts: List[str], n_process: Optional[int] = None, batch_size: int = 1000) -> List[str]:
    nlp = _get_spacy_nlp()
    if nlp is None:
        # Fallback if spacy not available
        return [_porter_stem_text(t) for t in texts]
    # Configure multiprocessing workers conservatively for Windows
    if n_process is None:
        try:
            cpus = os.cpu_count() or 1
            n_process = max(1, min(4, cpus // 2))
        except Exception:
            n_process = 1
    results: List[str] = []
    for doc in nlp.pipe(texts, n_process=n_process, batch_size=batch_size):
        lemmas = []
        for token in doc:
            if token.is_stop or token.is_punct or token.like_num:
                continue
            lem = token.lemma_.strip().lower()
            if lem and lem not in STOPWORDS and len(lem) > 1:
                lemmas.append(lem)
        results.append(" ".join(lemmas))
    return results

def preprocess_series(series: pd.Series, do_lemmatize: bool = True, method: Optional[str] = None) -> pd.Series:
    """
    Preprocess a text series quickly.

    Parameters:
    - do_lemmatize: whether to reduce tokens (via stemming/lemmatization). If False, returns cleaned lowercase text.
    - method: 'porter' (fast, default), 'spacy' (accurate, slower), or 'none'. If None, will read from env PREPROCESS_METHOD.
    """
    cleaned = series.fillna("").map(clean_text)
    if not do_lemmatize:
        return cleaned

    method = (method or os.getenv('PREPROCESS_METHOD', 'porter')).lower()
    if method == 'none':
        return cleaned
    if method == 'spacy':
        return pd.Series(_spacy_lemmatize_texts(cleaned.tolist()), index=cleaned.index)
    # default fast path: porter stemming
    return cleaned.map(_porter_stem_text)

if __name__ == "__main__":
    import sys, os
    # Example run:
    paths = ["../data/bbc-text.csv","../data/imdb-dataset.csv","../data/cnn_dailymail.csv"]
    df = load_csvs(paths)
    df['clean_text'] = preprocess_series(df['text'], method=os.getenv('PREPROCESS_METHOD', 'porter'))
    print(df.head())
    df.to_csv("../data/preprocessed_all.csv", index=False)