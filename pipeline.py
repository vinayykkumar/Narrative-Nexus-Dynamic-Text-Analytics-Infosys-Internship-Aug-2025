# pipeline.py
"""End-to-end orchestration for Narrative Nexus model training."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.insights import attach_topic_sentiment, build_topic_insights
from src.preprocessing import (
    apply_preprocessing,
    load_and_merge_datasets,
    save_preprocessed_dataset,
)
from src.sentiment import MAX_LEN, load_imdb_dataset, load_sentiment_models, train_sentiment_models
from src.topic_modeling import train_topic_models


DATA_DIR = Path("data")
MODEL_DIR = Path("models")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("📥 Loading and merging datasets (BBC, CNN, IMDB)...")
    merged_df = load_and_merge_datasets(
        DATA_DIR / "bbc-text.csv",
        DATA_DIR / "cnn_dailymail.csv",
        DATA_DIR / "imdb-dataset.csv",
    )
    print(f"Merged dataset shape: {merged_df.shape}")

    print("🧹 Applying preprocessing and lemmatization...")
    processed_df = apply_preprocessing(merged_df)
    merged_path = DATA_DIR / "merged_preprocessed.csv"
    save_preprocessed_dataset(processed_df, merged_path)
    if merged_path.exists():
        try:
            merged_display = merged_path.resolve().relative_to(Path.cwd())
        except ValueError:
            merged_display = merged_path.resolve()
    else:
        merged_display = merged_path
    print(f"Saved preprocessed dataset -> {merged_display}")

    print("📊 Training topic models (LDA & NMF)...")
    topic_artifacts = train_topic_models(processed_df["clean_text"].astype(str).tolist(), n_topics=5, model_dir=MODEL_DIR)
    print(f"LDA Perplexity: {topic_artifacts.lda_perplexity:.4f}")
    print(f"LDA Coherence: {topic_artifacts.lda_coherence:.4f}")
    print(f"NMF Coherence: {topic_artifacts.nmf_coherence:.4f}")

    print("🧠 Training sentiment models (Rule-based, Logistic Regression, LSTM)...")
    imdb_df = load_imdb_dataset(DATA_DIR / "imdb-dataset.csv")
    sentiment_metrics = train_sentiment_models(imdb_df, model_dir=MODEL_DIR)
    print("Rule-based metrics:", sentiment_metrics.rule_metrics)
    print("Logistic Regression metrics:", sentiment_metrics.ml_metrics)
    print("LSTM metrics:", sentiment_metrics.dl_metrics)

    print("🔗 Integrating topics with sentiment signals...")
    sentiment_models = load_sentiment_models(MODEL_DIR)
    integrated_df = attach_topic_sentiment(
        processed_df,
        topic_artifacts.lda,
        topic_artifacts.count_vectorizer,
        sentiment_models.dl_model,
        sentiment_models.tokenizer,
        max_len=MAX_LEN,
    )

    insights_df = build_topic_insights(integrated_df)
    insights_path = DATA_DIR / "topic_insights.csv"
    insights_df.to_csv(insights_path, index=False)
    if insights_path.exists():
        try:
            insights_display = insights_path.resolve().relative_to(Path.cwd())
        except ValueError:
            insights_display = insights_path.resolve()
    else:
        insights_display = insights_path
    print(f"💾 Topic-level insights saved -> {insights_display}")

    print("\n✅ Narrative Nexus pipeline completed successfully!")


if __name__ == "__main__":
    main()