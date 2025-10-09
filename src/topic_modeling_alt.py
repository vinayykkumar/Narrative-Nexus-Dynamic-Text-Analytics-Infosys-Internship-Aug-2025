# src/topic_modeling_alt.py
from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Tuple
import json, joblib, numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models" / "topics_alt"
VIZ_DIR = ROOT / "viz" / "topics_alt"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
VIZ_DIR.mkdir(parents=True, exist_ok=True)

STOPWORDS_MINI = set("""
a an the and or but if while of to in on for with as is are was were be been being
this that these those i you he she it we they them our your his her its their
at by from up out into over after before about between through during than then
very just so not no nor too can could should would will do did doing done
""".split())

def _vect(kind: str, max_features=5000, ngram_range=(1,2)):
    if kind == "lda":
        return CountVectorizer(lowercase=True, stop_words=list(STOPWORDS_MINI),
                               max_features=max_features, ngram_range=ngram_range)
    return TfidfVectorizer(lowercase=True, stop_words=list(STOPWORDS_MINI),
                           max_features=max_features, ngram_range=ngram_range)

def plot_topic_distribution_alt(counts: List[int], tag: str) -> str:
    if not counts: raise ValueError("counts empty")
    x = list(range(len(counts)))
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=140)
    ax.bar([f"T{xi}" for xi in x], counts)
    ax.set_title("Topic Distribution (Prevalence)")
    ax.set_xlabel("Topic"); ax.set_ylabel("Documents")
    fig.tight_layout()
    out = VIZ_DIR / f"topic_dist_{tag}.png"
    fig.savefig(out, transparent=False)
    plt.close(fig)
    return str(out)

# ---------- sklearn NMF ----------
def train_sklearn_nmf(docs: List[str], k=8, max_features=5000, ngram_range=(1,2), tag: Optional[str]=None) -> Tuple[str, np.ndarray, List[int]]:
    vect = _vect("nmf", max_features, ngram_range)
    X = vect.fit_transform(docs)
    model = NMF(n_components=k, init="nndsvda", solver="cd", max_iter=400, random_state=42)
    W = model.fit_transform(X)            # doc-topic weights
    H = model.components_
    feature_names = list(vect.get_feature_names_out())
    top = {ti:[feature_names[j] for j in np.argsort(row)[::-1][:12]] for ti,row in enumerate(H)}
    tag = tag or f"nmf_k{k}_mf{max_features}"
    joblib.dump(model, MODELS_DIR / f"{tag}.joblib")
    joblib.dump(vect,  MODELS_DIR / f"{tag}.vec.joblib")
    (MODELS_DIR / f"{tag}.meta.json").write_text(json.dumps({"algo":"nmf","k":k,"top_words":top}, indent=2), encoding="utf-8")
    # counts by argmax
    argmax = np.argmax(W, axis=1)
    sizes = [int(np.sum(argmax == t)) for t in range(k)]
    return tag, W, sizes

def infer_sklearn_nmf(docs: List[str], tag: str):
    model = joblib.load(MODELS_DIR / f"{tag}.joblib")
    vect  = joblib.load(MODELS_DIR / f"{tag}.vec.joblib")
    meta  = json.loads((MODELS_DIR / f"{tag}.meta.json").read_text(encoding="utf-8"))
    W = model.transform(vect.transform(docs))
    W = W / (W.sum(axis=1, keepdims=True) + 1e-12)
    return meta, W.tolist()

# ---------- gensim LDA ----------
def train_gensim_lda(docs: List[str], k=8, max_features=5000, tag: Optional[str]=None) -> Tuple[str, List[int]]:
    from gensim import corpora, models
    tokens = [[w for w in d.lower().split() if len(w)>2 and w not in STOPWORDS_MINI] for d in docs]
    dictionary = corpora.Dictionary(tokens)
    if max_features:
        dictionary.filter_extremes(no_below=2, no_above=0.5, keep_n=max_features)
    corpus = [dictionary.doc2bow(t) for t in tokens]
    lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=k, random_state=42, passes=10)
    top = {i:[w for w,_ in lda.show_topic(i, topn=12)] for i in range(k)}
    tag = tag or f"gensim_lda_k{k}_mf{max_features}"
    joblib.dump(lda,        MODELS_DIR / f"{tag}.lda.joblib")
    joblib.dump(dictionary, MODELS_DIR / f"{tag}.dict.joblib")
    (MODELS_DIR / f"{tag}.meta.json").write_text(json.dumps({"algo":"lda_gensim","k":k,"top_words":top}, indent=2), encoding="utf-8")
    # compute per-doc argmax for distribution
    sizes = [0]*k
    for bow in corpus:
        dist = lda.get_document_topics(bow, minimum_probability=0.0)
        probs = [0.0]*k
        for ti, p in dist: probs[int(ti)] = float(p)
        sizes[int(np.argmax(probs))] += 1
    return tag, sizes

def infer_gensim_lda(docs: List[str], tag: str):
    from gensim import corpora
    lda  = joblib.load(MODELS_DIR / f"{tag}.lda.joblib")
    dic  = joblib.load(MODELS_DIR / f"{tag}.dict.joblib")
    meta = json.loads((MODELS_DIR / f"{tag}.meta.json").read_text(encoding="utf-8"))
    tokens = [[w for w in d.lower().split() if len(w)>2 and w not in STOPWORDS_MINI] for d in docs]
    corpus = [dic.doc2bow(t) for t in tokens]
    k = meta["k"]
    W = []
    for bow in corpus:
        dist = lda.get_document_topics(bow, minimum_probability=0.0)
        probs = [0.0]*k
        for ti, p in dist:
            probs[int(ti)] = float(p)
        W.append(probs)
    return meta, W
