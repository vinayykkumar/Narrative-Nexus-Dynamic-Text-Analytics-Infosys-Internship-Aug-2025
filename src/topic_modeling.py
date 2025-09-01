# src/topic_modeling.py
from __future__ import annotations
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import numpy as np
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

# --------- Utilities ---------
def make_docs_from_text(cleaned_text: str, words_per_doc: int = 200) -> List[str]:
    """
    Turn one long cleaned string into many short 'documents'
    so topic models have signal. (Simple & effective for this project.)
    """
    tokens = cleaned_text.split()
    if not tokens:
        return []
    docs = []
    for i in range(0, len(tokens), words_per_doc):
        chunk = tokens[i:i + words_per_doc]
        if len(chunk) >= max(30, words_per_doc // 4):  # skip tiny leftovers
            docs.append(" ".join(chunk))
    return docs

@dataclass
class Vectorized:
    X: Any
    vectorizer: Any
    feature_names: List[str]

# --------- Vectorization ---------
def vectorize_tfidf(docs: List[str],
                    max_features: int = 5000,
                    ngram_range: Tuple[int, int] = (1, 2),
                    min_df: int | float = 2,
                    max_df: int | float = 0.95) -> Vectorized:
    vec = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        dtype=np.float32,
        stop_words=None,
    )
    X = vec.fit_transform(docs)
    return Vectorized(X=X, vectorizer=vec, feature_names=vec.get_feature_names_out().tolist())

def vectorize_count(docs: List[str],
                    max_features: int = 5000,
                    ngram_range: Tuple[int, int] = (1, 2),
                    min_df: int | float = 2,
                    max_df: int | float = 0.95) -> Vectorized:
    vec = CountVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        dtype=np.int32,
        stop_words=None,
    )
    X = vec.fit_transform(docs)
    return Vectorized(X=X, vectorizer=vec, feature_names=vec.get_feature_names_out().tolist())

# --------- Models ---------
def fit_nmf(X, n_topics: int = 8, max_iter: int = 200, random_state: int = 42) -> NMF:
    nmf = NMF(
        n_components=n_topics,
        init="nndsvd",
        random_state=random_state,
        max_iter=max_iter,
        alpha_W=0.0,
        alpha_H=0.0,
        l1_ratio=0.0,
    )
    nmf.fit(X)
    return nmf

def fit_lda(X, n_topics: int = 8, max_iter: int = 20, random_state: int = 42) -> LatentDirichletAllocation:
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        learning_method="batch",
        max_iter=max_iter,
        random_state=random_state,
        doc_topic_prior=None,
        topic_word_prior=None,
        evaluate_every=-1,
        n_jobs=-1,
    )
    lda.fit(X)
    return lda

# --------- Topic inspection ---------
def top_terms_per_topic(model, feature_names: List[str], topn: int = 10) -> List[List[str]]:
    """Return list of topics, each is list of 'word(weight)' or just 'word'."""
    topics = []
    if hasattr(model, "components_"):
        comp = model.components_
        for k in range(comp.shape[0]):
            idx = np.argsort(comp[k])[::-1][:topn]
            terms = [feature_names[i] for i in idx]
            topics.append(terms)
    else:
        # Fallback: no components_ (shouldn't happen with NMF/LDA)
        topics = [[]]
    return topics

def doc_topic_distribution(model, X) -> np.ndarray:
    """(n_docs, n_topics) responsibility matrix."""
    return model.transform(X)

# --------- Save / Load ---------
def save_artifacts(path_prefix: str, model, vectorizer) -> None:
    joblib.dump(model, f"{path_prefix}_model.joblib")
    joblib.dump(vectorizer, f"{path_prefix}_vectorizer.joblib")

def load_artifacts(path_prefix: str):
    model = joblib.load(f"{path_prefix}_model.joblib")
    vectorizer = joblib.load(f"{path_prefix}_vectorizer.joblib")
    return model, vectorizer
