# pipeline.py
"""
Unified pipeline runner for NarrativeNexus
Run this once to prepare data and models.
"""

import os
import pandas as pd

from src.preprocessing import load_csvs, preprocess_series
from src.topic_modeling import fit_tfidf, train_nmf, train_lda, save_models
from src.summarization import extractive_summary, abstractive_summary
from src.sentiment import get_sentiment_pipeline, analyze_texts

DATA_DIR = "data"
MODEL_DIR = "models"

DATASETS = [
    os.path.join(DATA_DIR, "bbc-text.csv"),
    os.path.join(DATA_DIR, "imdb-dataset.csv"),
    os.path.join(DATA_DIR, "cnn_dailymail.csv"),
]

def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("📥 Loading datasets...")
    df = load_csvs(DATASETS)
    print(f"Loaded {len(df)} rows from {len(DATASETS)} files.")

    print("🧹 Preprocessing text...")
    df['clean_text'] = preprocess_series(df['text'])
    out_path = os.path.join(DATA_DIR, "preprocessed_all.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved preprocessed dataset -> {out_path}")

    print("📊 Training topic models...")
    texts = df['clean_text'].astype(str).tolist()
    tfidf, X = fit_tfidf(texts, max_features=10000)
    nmf, W, H = train_nmf(X, n_topics=12)
    lda, dictionary, corpus = train_lda(texts, n_topics=12)
    save_models(tfidf, nmf, lda, dictionary)
    print(f"Saved topic models -> {MODEL_DIR}")

    print("💡 Testing summarization & sentiment...")
    sample = df['clean_text'].iloc[0]
    print("Sample text:", sample[:200], "...")

    print("\nExtractive summary:")
    print(extractive_summary(sample))

    print("\nAbstractive summary:")
    print(abstractive_summary(sample))

    sentiment = get_sentiment_pipeline()
    res = analyze_texts(sentiment, [sample])
    print("\nSentiment result:", res[0])

    print("\n✅ Pipeline completed successfully!")

if __name__ == "__main__":
    main()
