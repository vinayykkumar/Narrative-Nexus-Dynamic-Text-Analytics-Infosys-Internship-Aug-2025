import os
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.topic_modeling import fit_tfidf, train_nmf, train_lda, save_models

DATA_DIR = "data"
MODEL_DIR = "models"

def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    print("[2/5] Topic modeling: loading preprocessed data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "preprocessed_all.csv"))
    texts = df['clean_text'].astype(str).tolist()
    print(f" - Docs: {len(texts)}")
    print("[2/5] Fitting TF-IDF...")
    tfidf, X = fit_tfidf(texts, max_features=10000)
    print("[2/5] Training NMF...")
    nmf, W, H = train_nmf(X, n_topics=12)
    print("[2/5] Training LDA (gensim)...")
    lda, dictionary, corpus = train_lda(texts, n_topics=12)
    save_models(tfidf, nmf, lda, dictionary)
    print(f"[2/5] Saved topic models -> {MODEL_DIR}")

if __name__ == "__main__":
    main()
