# src/topic_modeling.py
import joblib
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import numpy as np
import pandas as pd
from gensim import corpora, models
import gensim
from typing import List
import os

MODEL_DIR = "../models"

def fit_tfidf(texts: List[str], max_features=10000):
    tfidf = TfidfVectorizer(max_df=0.95, min_df=5, max_features=max_features, ngram_range=(1,2))
    X = tfidf.fit_transform(texts)
    return tfidf, X

def train_nmf(X, n_topics=10, random_state=42):
    nmf = NMF(n_components=n_topics, random_state=random_state, init="nndsvda", max_iter=300)
    W = nmf.fit_transform(X)
    H = nmf.components_
    return nmf, W, H

def print_top_words_nmf(nmf, tfidf, n_top_words=10):
    feature_names = tfidf.get_feature_names_out()
    for topic_idx, topic in enumerate(nmf.components_):
        top = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        print("Topic %d:" % topic_idx, ", ".join(top))

def train_lda(texts: List[str], n_topics=10, passes=10):
    tokenized = [t.split() for t in texts]
    dictionary = corpora.Dictionary(tokenized)
    dictionary.filter_extremes(no_below=5, no_above=0.5)
    corpus = [dictionary.doc2bow(text) for text in tokenized]
    lda = gensim.models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=n_topics, passes=passes, random_state=42)
    return lda, dictionary, corpus

def save_models(tfidf, nmf, lda, dictionary):
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(tfidf, os.path.join(MODEL_DIR,"tfidf_vectorizer.pkl"))
    joblib.dump(nmf, os.path.join(MODEL_DIR,"nmf_model.pkl"))
    lda.save(os.path.join(MODEL_DIR,"lda_model.gensim"))
    dictionary.save(os.path.join(MODEL_DIR,"lda_dictionary.dict"))

if __name__ == "__main__":
    df = pd.read_csv("../data/preprocessed_all.csv")
    texts = df['clean_text'].astype(str).tolist()
    tfidf, X = fit_tfidf(texts)
    nmf, W, H = train_nmf(X, n_topics=12)
    print_top_words_nmf(nmf, tfidf)
    lda, dictionary, corpus = train_lda(texts, n_topics=12)
    save_models(tfidf, nmf, lda, dictionary)
    print("Saved models to ../models")
