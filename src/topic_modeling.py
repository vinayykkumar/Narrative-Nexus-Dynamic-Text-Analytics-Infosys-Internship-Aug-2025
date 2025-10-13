# src/topic_modeling.py
from __future__ import annotations
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import numpy as np
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

import numpy as np
import scipy.sparse as sp

def safe_array(X):
    """Convert deprecated np.matrix / sparse matrix to safe ndarray."""
    if isinstance(X, np.matrix):
        return np.asarray(X)
    if sp.issparse(X):
        return X.toarray()
    return np.array(X)

# --------- Utilities ---------
# Robust make_docs_from_text: chunk by sentences -> group into docs of approx words_per_doc
def make_docs_from_text(text: str, words_per_doc: int = 200) -> list:
    """
    Produces a list of document strings from a long text.
    - Splits into sentence-like units (uses a simple regex split) and groups them
      until roughly words_per_doc words are collected per doc.
    - Safe: avoids splitting into characters or tiny tokens.
    """
    import re
    if not text:
        return []

    # normalize whitespace and newlines
    t = re.sub(r'\s+', ' ', text.strip())

    # sentence split pattern similar to summarizer
    sent_split = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9])')
    sents = sent_split.split(t)
    sents = [s.strip() for s in sents if s and len(s.split()) >= 3]  # drop very short fragments

    docs = []
    cur = []
    cur_words = 0
    for s in sents:
        w = len(s.split())
        # if adding this sentence exceeds words_per_doc and current doc not empty, start new doc
        if cur and cur_words + w > words_per_doc:
            docs.append(" ".join(cur))
            cur = [s]
            cur_words = w
        else:
            cur.append(s)
            cur_words += w

    if cur:
        docs.append(" ".join(cur))

    # fallback: if nothing produced (weird input), chunk by words
    if not docs:
        words = t.split()
        for i in range(0, len(words), words_per_doc):
            docs.append(" ".join(words[i:i+words_per_doc]))

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
        stop_words='english',
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        token_pattern=r'(?u)\b[a-zA-Z]{3,}\b'   # only tokens >=3 letters
    )

    X = vec.fit_transform(docs)
    return Vectorized(X=X, vectorizer=vec, feature_names=vec.get_feature_names_out().tolist())

def vectorize_count(docs: List[str],
                    max_features: int = 5000,
                    ngram_range: Tuple[int, int] = (1, 2),
                    min_df: int | float = 2,
                    max_df: int | float = 0.95) -> Vectorized:
    vec = CountVectorizer(
        stop_words='english',
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        token_pattern=r'(?u)\b[a-zA-Z]{3,}\b'
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
    """Return list of topics, each is list of top words."""
    topics = []
    if hasattr(model, "components_"):
        comp = model.components_
        for k in range(comp.shape[0]):
            idx = np.argsort(comp[k])[::-1][:topn]
            terms = [feature_names[i] for i in idx]
            topics.append(terms)
    else:
        topics = [[]]
    return topics

def doc_topic_distribution(model, X) -> np.ndarray:
    """(n_docs, n_topics) responsibility matrix."""
    X = safe_array(X)
    return model.transform(X)

# --------- Save / Load ---------
def save_artifacts(path_prefix: str, model, vectorizer) -> None:
    joblib.dump(model, f"{path_prefix}_model.joblib")
    joblib.dump(vectorizer, f"{path_prefix}_vectorizer.joblib")

def load_artifacts(path_prefix: str):
    model = joblib.load(f"{path_prefix}_model.joblib")
    vectorizer = joblib.load(f"{path_prefix}_vectorizer.joblib")
    return model, vectorizer

# --------- Evaluation: Coherence, Perplexity, Diversity, Silhouette ---------

def _tokenize_for_gensim(docs: List[str]) -> List[List[str]]:
    """Simple whitespace tokenizer for gensim coherence."""
    return [[w for w in d.lower().split() if w.strip()] for d in docs]

def compute_coherence_score(model, docs: List[str], feature_names: List[str], topn: int = 10, coherence: str = "c_v") -> float:
    """
    Compute topic coherence.
    Tries gensim CoherenceModel (recommended). If gensim not available, falls back to UMass-style coherence.
    - coherence: 'c_v', 'c_npmi', 'u_mass', etc. (gensim)
    """
    # Try gensim first
    try:
        from gensim.models.coherencemodel import CoherenceModel
        from gensim.corpora.dictionary import Dictionary

        texts = _tokenize_for_gensim(docs)
        if not texts:
            return 0.0

        topics = top_terms_per_topic(model, feature_names, topn=topn)
        dictionary = Dictionary(texts)
        cm = CoherenceModel(topics=topics, texts=texts, dictionary=dictionary, coherence=coherence)
        return float(cm.get_coherence())
    except Exception:
        # Fallback to simple UMass-style coherence (uses only numpy/sklearn)
        return compute_coherence_umass(model, docs, feature_names, topn=topn)

def compute_coherence_umass(model, docs: List[str], feature_names: List[str], topn: int = 10) -> float:
    """
    Fallback UMass-style coherence computed from document-term counts.
    Returns average pairwise log co-occurrence score (higher is better; UMass usually negative).
    """
    # Build document-term binary matrix over the provided vocabulary
    vec = CountVectorizer(vocabulary=feature_names, binary=True)
    X = vec.fit_transform(docs)  # (n_docs, vocab)
    if X.shape[0] == 0:
        return float("nan")

    Xc = (X > 0).astype(int)  # ensure binary ints
    df = np.asarray(Xc.sum(axis=0)).ravel()  # document frequency per term
    topics = top_terms_per_topic(model, feature_names, topn=topn)

    total_score = 0.0
    n_topics = 0
    for terms in topics:
        # map terms to indices
        idxs = [vec.vocabulary_.get(t) for t in terms]
        idxs = [i for i in idxs if i is not None]
        if len(idxs) < 2:
            continue
        score = 0.0
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                ti, tj = idxs[i], idxs[j]
                # documents containing both terms
                both = Xc[:, ti].multiply(Xc[:, tj]).sum()
                numerator = both + 1.0  # add-one smoothing
                denom = df[tj] + 1.0
                score += np.log(numerator / denom)
        total_score += score
        n_topics += 1

    if n_topics == 0:
        return float("nan")
    return float(total_score / n_topics)

def compute_model_perplexity(model, X) -> float | None:
    """
    Compute perplexity for probabilistic models (sklearn LDA supports .perplexity).
    Returns float or None.
    """
    if hasattr(model, "perplexity"):
        try:
            return float(model.perplexity(X))
        except Exception:
            return None
    return None

def topic_diversity(model, feature_names: List[str], topn: int = 10) -> float:
    """
    Topic diversity: fraction of unique terms in the top-n words across all topics.
    Range: (0,1], higher indicates more distinct topics.
    """
    topics = top_terms_per_topic(model, feature_names, topn=topn)
    flat = [t for topic in topics for t in topic]
    total = len(flat)
    if total == 0:
        return 0.0
    unique = len(set(flat))
    return float(unique / total)

def topic_silhouette_score(docs: List[str], model, X_vectorized, feature_names: List[str], topn_docs: int = None, embedding_model: str = "all-MiniLM-L6-v2") -> float:
    """
    Optional: compute silhouette score using sentence embeddings.
    Requires: sentence-transformers.
    Steps:
      - Get doc-topic assignment (dominant topic)
      - Embed docs using SentenceTransformer
      - Compute sklearn silhouette_score on embeddings
    Returns float or raises RuntimeError if sentence-transformers is missing.
    """
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics import silhouette_score
    except Exception as e:
        raise RuntimeError("sentence-transformers and scikit-learn required for silhouette. pip install sentence-transformers scikit-learn") from e

    docs_texts = docs if topn_docs is None else docs[:topn_docs]
    if not docs_texts:
        return float("nan")

    # doc-topic responsibilities
    theta = model.transform(X_vectorized)  # (n_docs, n_topics)
    labels = np.argmax(theta, axis=1)

    # embeddings (may be slow)
    embedder = SentenceTransformer(embedding_model)
    embeddings = embedder.encode(docs_texts, convert_to_numpy=True, show_progress_bar=False)

    # compute silhouette (requires at least 2 clusters and appropriate distribution)
    try:
        score = silhouette_score(embeddings, labels[: len(docs_texts) ])
        return float(score)
    except Exception:
        return float("nan")
