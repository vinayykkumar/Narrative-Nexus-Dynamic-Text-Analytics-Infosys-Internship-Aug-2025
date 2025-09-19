# src/preprocessing.py
import re
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import spacy
from typing import List
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

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

def lemmatize_text(text: str) -> str:
    doc = nlp(text)
    lemmas = []
    for token in doc:
        if token.is_stop or token.is_punct or token.like_num:
            continue
        lem = token.lemma_.strip()
        if lem and lem not in STOPWORDS and len(lem) > 1:
            lemmas.append(lem)
    return " ".join(lemmas)

def preprocess_series(series: pd.Series, do_lemmatize=True) -> pd.Series:
    cleaned = series.fillna("").map(clean_text)
    if do_lemmatize:
        cleaned = cleaned.map(lemmatize_text)
    return cleaned

if __name__ == "__main__":
    import sys, os
    # Example run:
    paths = ["../data/bbc-text.csv","../data/imdb-dataset.csv","../data/cnn_dailymail.csv"]
    df = load_csvs(paths)
    df['clean_text'] = preprocess_series(df['text'])
    print(df.head())
    df.to_csv("../data/preprocessed_all.csv", index=False)
