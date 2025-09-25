"""Topic modelling helpers mirroring the notebook logic."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import joblib
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel, LdaModel
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


@dataclass
class TopicModelArtifacts:
    lda: LatentDirichletAllocation
    nmf: NMF
    count_vectorizer: CountVectorizer
    tfidf_vectorizer: TfidfVectorizer
    lda_perplexity: float
    lda_coherence: float
    nmf_coherence: float


def _prepare_dictionary(tokenized_texts: Iterable[List[str]]) -> Dictionary:
    dictionary = Dictionary(tokenized_texts)
    dictionary.filter_extremes(no_below=2, no_above=0.95)
    return dictionary


def _compute_nmf_coherence(nmf: NMF, tfidf_vectorizer: TfidfVectorizer, tokenized_texts: List[List[str]], dictionary: Dictionary) -> float:
    feature_names = tfidf_vectorizer.get_feature_names_out()
    topics = []
    for topic in nmf.components_:
        top_words = [feature_names[i] for i in topic.argsort()[-10:]]
        topics.append(top_words)

    coherence_model = CoherenceModel(topics=topics, texts=tokenized_texts, dictionary=dictionary, coherence="c_v")
    return float(coherence_model.get_coherence())


def train_topic_models(
    clean_texts: List[str],
    n_topics: int = 5,
    random_state: int = 42,
    model_dir: Path | str = Path("models"),
) -> TopicModelArtifacts:
    """Train LDA and NMF models and persist the fitted components."""

    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    tokenized_texts = [text.split() for text in clean_texts]
    dictionary = _prepare_dictionary(tokenized_texts)
    corpus = [dictionary.doc2bow(text) for text in tokenized_texts]

    count_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words="english")
    count_matrix = count_vectorizer.fit_transform(clean_texts)

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=random_state)
    lda.fit(count_matrix)
    lda_perplexity = float(lda.perplexity(count_matrix))

    gensim_lda = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=n_topics,
        random_state=random_state,
        passes=5,
        iterations=50,
    )
    lda_coherence_model = CoherenceModel(model=gensim_lda, texts=tokenized_texts, dictionary=dictionary, coherence="c_v")
    lda_coherence = float(lda_coherence_model.get_coherence())

    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words="english")
    tfidf_matrix = tfidf_vectorizer.fit_transform(clean_texts)

    nmf = NMF(n_components=n_topics, random_state=random_state)
    nmf.fit(tfidf_matrix)
    nmf_coherence = _compute_nmf_coherence(nmf, tfidf_vectorizer, tokenized_texts, dictionary)

    joblib.dump(lda, model_dir / "lda_model.pkl")
    joblib.dump(nmf, model_dir / "nmf_model.pkl")
    joblib.dump(count_vectorizer, model_dir / "count_vectorizer.pkl")
    joblib.dump(tfidf_vectorizer, model_dir / "tfidf_vectorizer.pkl")

    return TopicModelArtifacts(
        lda=lda,
        nmf=nmf,
        count_vectorizer=count_vectorizer,
        tfidf_vectorizer=tfidf_vectorizer,
        lda_perplexity=lda_perplexity,
        lda_coherence=lda_coherence,
        nmf_coherence=nmf_coherence,
    )


def describe_topics(model: NMF | LatentDirichletAllocation, vectorizer, top_n: int = 10) -> List[List[str]]:
    feature_names = vectorizer.get_feature_names_out()
    topics: List[List[str]] = []
    for topic in model.components_:
        topics.append([feature_names[i] for i in topic.argsort()[-top_n:]])
    return topics


if __name__ == "__main__":  # pragma: no cover - convenience execution
    import pandas as pd

    data = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "merged_preprocessed.csv")
    artifacts = train_topic_models(data["clean_text"].astype(str).tolist())
    print("LDA Perplexity:", artifacts.lda_perplexity)
    print("LDA Coherence:", artifacts.lda_coherence)
    print("NMF Coherence:", artifacts.nmf_coherence)
