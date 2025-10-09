# src/topic_modeling.py
"""
Compact topic modelling (load matrix + vectorizer -> train LDA/NMF -> save model + doc topics)

Usage:
python src/topic_modeling.py <matrix.pkl> <vectorizer.pkl> <out_dir> <algo:nmf|lda> <n_topics>

Example:
python src/topic_modeling.py models/job_desc/tfidf/matrix.pkl models/job_desc/tfidf/vectorizer.pkl models/job_desc/nmf nmf 10
"""
import sys
from pathlib import Path
import joblib
import numpy as np

from sklearn.decomposition import NMF, LatentDirichletAllocation

def print_top_terms(model, terms, top_n=10):
    for i, comp in enumerate(model.components_):
        idx = np.argsort(comp)[-top_n:][::-1]
        print(f"Topic {i:02d}:", " | ".join(terms[j] for j in idx))

def main():
    if len(sys.argv) < 6:
        print("Usage: python topic_modeling.py <matrix.pkl> <vectorizer.pkl> <out_dir> <algo:nmf|lda> <n_topics>")
        sys.exit(1)

    matrix_path = Path(sys.argv[1])
    vectorizer_path = Path(sys.argv[2])
    out_dir = Path(sys.argv[3])
    algo = sys.argv[4].lower()
    n_topics = int(sys.argv[5])

    if not matrix_path.exists():
        raise FileNotFoundError(f"Matrix file not found: {matrix_path}")
    if not vectorizer_path.exists():
        raise FileNotFoundError(f"Vectorizer file not found: {vectorizer_path}")

    # load
    X = joblib.load(matrix_path)
    vec = joblib.load(vectorizer_path)
    try:
        terms = vec.get_feature_names_out()
    except Exception:
        terms = [k for k,v in sorted(vec.vocabulary_.items(), key=lambda kv: kv[1])]

    print("Loaded matrix shape:", getattr(X, "shape", None))

    # train
    if algo == "nmf":
        model = NMF(n_components=n_topics, init="nndsvd", random_state=42, max_iter=200)
        model.fit(X)
    elif algo == "lda":
        model = LatentDirichletAllocation(n_components=n_topics, random_state=42, learning_method="batch", max_iter=10)
        model.fit(X)
    else:
        raise ValueError("algo must be 'nmf' or 'lda'")

    # print top terms
    print_top_terms(model, terms, top_n=12)

    # save model
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / f"{algo}_model.pkl"
    joblib.dump(model, model_path)
    print("Saved model ->", model_path)

    # infer topics for each document and save dominant topic per doc
    try:
        doc_topic_dist = model.transform(X)   # shape (n_docs, n_topics)
        dominant = doc_topic_dist.argmax(axis=1)
        csv_path = out_dir / "doc_topics.csv"
        with open(csv_path, "w", encoding="utf8") as fw:
            fw.write("doc_index,dominant_topic\n")
            for i, t in enumerate(dominant):
                fw.write(f"{i},{int(t)}\n")
        print("Saved document topics ->", csv_path)
    except Exception as e:
        print("Warning: could not compute/save doc topics:", e)

if __name__ == "__main__":
    main()
