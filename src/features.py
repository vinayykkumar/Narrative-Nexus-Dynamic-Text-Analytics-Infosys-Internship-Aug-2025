# src/features.py
"""
Build BoW and TF-IDF features from preprocessed docs (one doc per line).

CLI examples:
# build TF-IDF
python src/features.py --input data/processed/job_desc_clean.txt --outdir models/job_desc --tfidf --max-features 20000 --ngram 1 2 --min-df 2 --max-df 0.8

# build BoW
python src/features.py --input data/processed/resume_objectives_clean.txt --outdir models/resumes --bow --max-features 10000 --ngram 1 1 --min-df 2 --max-df 0.9

Saved artifacts:
- <outdir>/vectorizer.pkl      (CountVectorizer or TfidfVectorizer)
- <outdir>/matrix.pkl          (sparse matrix, joblib)
- <outdir>/vocab_terms.txt     (one term per line: vocabulary order)
"""

from pathlib import Path
import argparse
import joblib
from typing import Tuple, Iterable, List
import numpy as np
from collections import defaultdict

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from scipy.sparse import issparse

def read_docs_lines(path: Path) -> List[str]:
    with open(path, "r", encoding="utf8") as f:
        return [line.strip() for line in f if line.strip()]

def build_bow(corpus: Iterable[str], max_features: int = None, ngram_range: Tuple[int,int]=(1,1),
              min_df=1, max_df=1.0):
    vec = CountVectorizer(max_features=max_features, ngram_range=ngram_range, min_df=min_df, max_df=max_df)
    X = vec.fit_transform(corpus)
    return vec, X

def build_tfidf(corpus: Iterable[str], max_features: int = None, ngram_range: Tuple[int,int]=(1,1),
                min_df=1, max_df=1.0):
    vec = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range, min_df=min_df, max_df=max_df)
    X = vec.fit_transform(corpus)
    return vec, X

def save_artifacts(vec, X, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    vec_path = outdir / "vectorizer.pkl"
    mat_path = outdir / "matrix.pkl"
    vocab_path = outdir / "vocab_terms.txt"
    joblib.dump(vec, vec_path)
    # compress matrix
    joblib.dump(X, mat_path, compress=("lzma", 3))
    # save vocabulary terms in order
    try:
        terms = vec.get_feature_names_out()
    except Exception:
        # fallback: reconstruct from vocabulary_ mapping
        terms = [k for k,v in sorted(vec.vocabulary_.items(), key=lambda kv: kv[1])]
    with open(vocab_path, "w", encoding="utf8") as f:
        for t in terms:
            f.write(t + "\n")
    return vec_path, mat_path, vocab_path

def load_artifacts(outdir: Path):
    vec = joblib.load(outdir / "vectorizer.pkl")
    X = joblib.load(outdir / "matrix.pkl")
    return vec, X

def transform_new_documents(outdir: Path, docs: Iterable[str]):
    vec, _ = load_artifacts(outdir)
    return vec.transform(docs)

def parse_min_df(min_df_str):
    """
    Accept either an integer-like string '2' -> int(2) or a fractional string '0.01' -> float(0.01).
    Returns int or float.
    """
    try:
        if isinstance(min_df_str, (int, float)):
            # already parsed
            return min_df_str
        s = str(min_df_str).strip()
        if "." in s:
            val = float(s)
        else:
            val = int(s)
        return val
    except Exception:
        raise ValueError(f"Invalid min_df value: {min_df_str}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="processed input file (one doc per line)")
    parser.add_argument("--outdir", required=True, help="output folder to save vectorizer + matrix")
    parser.add_argument("--tfidf", action="store_true", help="build TF-IDF (default if not specifying --bow)")
    parser.add_argument("--bow", action="store_true", help="build Bag-of-Words (CountVectorizer)")
    parser.add_argument("--max-features", type=int, default=None, help="max features")
    parser.add_argument("--ngram", nargs=2, type=int, default=(1,1), help="ngram range, e.g. --ngram 1 2")
    parser.add_argument("--min-df", type=str, default="1", help="min_df (int absolute count or float fraction, e.g. 2 or 0.01)")
    parser.add_argument("--max-df", type=float, default=1.0, help="max_df (float fraction in (0,1] or int)")
    args = parser.parse_args()

    inp = Path(args.input)
    outdir = Path(args.outdir)
    docs = read_docs_lines(inp)
    print(f"Building features from {len(docs)} documents")

    # convert min_df properly
    try:
        min_df_val = parse_min_df(args.min_df)
    except Exception as e:
        print("Warning: couldn't parse --min-df; falling back to 1. Error:", e)
        min_df_val = 1

    build_tfidf_flag = args.tfidf or (not args.bow and not args.tfidf)
    build_bow_flag = args.bow
    ngram_range = (int(args.ngram[0]), int(args.ngram[1]))

    if build_tfidf_flag:
        print("Building TF-IDF:", ngram_range, "max_features=", args.max_features,
              "min_df=", min_df_val, "max_df=", args.max_df)
        vec, X = build_tfidf(
            docs,
            max_features=args.max_features,
            ngram_range=ngram_range,
            min_df=min_df_val,
            max_df=args.max_df
        )
        print("TF-IDF shape:", X.shape)
        saved = save_artifacts(vec, X, outdir / "tfidf")
        print("Saved TF-IDF artifacts to", saved)

    if build_bow_flag:
        print("Building BoW:", ngram_range, "max_features=", args.max_features,
              "min_df=", min_df_val, "max_df=", args.max_df)
        vec, X = build_bow(
            docs,
            max_features=args.max_features,
            ngram_range=ngram_range,
            min_df=min_df_val,
            max_df=args.max_df
        )
        print("BoW shape:", X.shape)
        saved = save_artifacts(vec, X, outdir / "bow")
        print("Saved BoW artifacts to", saved)

if __name__ == "__main__":
    main()

