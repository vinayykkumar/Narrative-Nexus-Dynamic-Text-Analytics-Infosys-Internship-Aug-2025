#!/usr/bin/env python3
"""
Topic Modeling and Sentiment Analysis

This script was generated from the Jupyter notebook "Topic Modeling and Sentiment Analysis.ipynb".
It performs:
1) Data loading and cleaning
2) Topic modeling with LDA
3) Visualizations (word clouds, topic distribution)
4) Sentiment analysis with VADER
5) Topic-sentiment relationship analysis

Requires Python 3.11+ and the packages listed in require.txt.
Tested for Python 3.13 compatibility (uses only std APIs).
"""

from __future__ import annotations

import sys
import argparse
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)

# -------------------------
# Imports from notebook
# -------------------------
import pandas as pd
import numpy as np

# nltk and friends
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer

# sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

# viz
import matplotlib
# Use a non-interactive backend suitable for servers/CI before importing pyplot
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# -------------------------
# Utilities
# -------------------------

def ensure_nltk_data() -> None:
    """Ensure required NLTK resources are available."""
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")
    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        nltk.download("wordnet")
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon")


def simple_tokenize(text: str) -> list[str]:
    import re
    return re.findall(r"\b\w+\b", text.lower())


def clean_text_alternative(text: object) -> str:
    """Clean and normalize free-form text.

    - remove non-letters
    - lowercase
    - remove stopwords
    - lemmatize
    """
    import re

    if not isinstance(text, str):
        return ""
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    tokens = simple_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    return " ".join(lemmatized_tokens)


def get_sentiment(score: float) -> str:
    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    else:
        return "Neutral"


# -------------------------
# Core pipeline
# -------------------------

def run_pipeline(
    excel_path: Path,
    text_column: str = "Airport Service Freeform Feedback",
    n_topics: int = 5,
    max_df: float = 0.95,
    min_df: int = 2,
    output_dir: Path | None = None,
    show_plots: bool = True,
):
    output_dir = Path(output_dir) if output_dir else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Python executable: {sys.executable}")
    print(f"Loading data from: {excel_path}")

    # Load data
    data = pd.read_excel(excel_path)
    if text_column not in data.columns:
        raise KeyError(
            f"Column '{text_column}' not found in file. Available columns: {list(data.columns)}"
        )

    # Prepare NLTK
    ensure_nltk_data()

    # Clean text
    print("Cleaning text...")
    data["cleaned_text"] = data[text_column].apply(clean_text_alternative)

    # If cleaning resulted in entirely empty strings (e.g., very short dataset), fallback to raw text
    if data["cleaned_text"].fillna("").str.len().sum() == 0:
        data["cleaned_text"] = data[text_column].astype(str)

    # Vectorize (TF-IDF for NMF)
    print("Vectorizing with TfidfVectorizer...")
    n_docs = int(len(data))
    # Clamp min_df for very small datasets (e.g., single .txt document)
    eff_min_df = 1 if n_docs <= 2 else min_df
    eff_max_df = max_df if n_docs > 1 else 1.0
    vectorizer = TfidfVectorizer(max_df=eff_max_df, min_df=eff_min_df, stop_words="english")
    try:
        X = vectorizer.fit_transform(data["cleaned_text"])  # TF-IDF matrix
    except ValueError:
        # Empty vocabulary or invalid min_df — fallback to lenient settings on raw text
        vectorizer = TfidfVectorizer(max_df=1.0, min_df=1)
        X = vectorizer.fit_transform(data[text_column].astype(str))
    if X.shape[1] == 0:
        # Still no features, inject a dummy token to avoid downstream crashes
        data["__dummy__"] = "text"
        vectorizer = TfidfVectorizer(min_df=1)
        X = vectorizer.fit_transform(data["__dummy__"])  

    # NMF
    # Ensure n_components is valid w.r.t features/docs (must be >=1 and <= n_features)
    n_features = int(X.shape[1])
    eff_topics = max(1, min(int(n_topics), n_features))
    print(f"Fitting NMF with n_topics={eff_topics} (requested={n_topics}, features={n_features})...")
    nmf_model = NMF(n_components=eff_topics, random_state=42, init="nndsvda", max_iter=200)
    nmf_model.fit(X)

    # Topic word clouds
    print("Generating word clouds per topic...")
    wc_dir = output_dir / "wordclouds"
    wc_dir.mkdir(exist_ok=True)
    # Prepare topic modeling JSON summary container
    topics_summary: list[dict] = []
    for topic_idx, topic in enumerate(nmf_model.components_):
        top_indices = topic.argsort()[:-11:-1]
        topic_words = [vectorizer.get_feature_names_out()[i] for i in top_indices]
        # Normalize weights for readability
        top_weights = topic[top_indices]
        total_weight = float(top_weights.sum()) if float(top_weights.sum()) != 0 else 1.0
        normalized_weights = [float(w) / total_weight for w in top_weights]
        topics_summary.append({
            "topic_id": int(topic_idx),
            "topic_label": f"Topic {topic_idx}",
            "top_words": list(zip(topic_words, normalized_weights)),
            "keywords": topic_words,
            "description": ", ".join(topic_words)
        })
        word_cloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            stopwords=set(stopwords.words("english")),
        ).generate(" ".join(topic_words))

        plt.figure(figsize=(10, 7))
        plt.imshow(word_cloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Topic #{topic_idx}")
        fig_path = wc_dir / f"topic_{topic_idx}_wordcloud.png"
        plt.savefig(fig_path, bbox_inches="tight")
        if show_plots:
            plt.show()
        plt.close()

    # Topic distribution pie
    print("Computing topic distribution pie chart...")
    topic_distribution = nmf_model.transform(X)
    topic_totals = topic_distribution.sum(axis=0)
    labels = [f"Topic {i}" for i in range(topic_totals.shape[0])]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        topic_totals,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=plt.cm.tab10.colors,
    )
    ax.set_title("Topic Distribution Across All Documents")
    pie_path = output_dir / "topic_distribution_pie.png"
    plt.savefig(pie_path, bbox_inches="tight")
    if show_plots:
        plt.show()
    plt.close()

    # Sentiment analysis
    print("Running VADER sentiment analysis...")
    sia = SentimentIntensityAnalyzer()
    # Compute full VADER scores for structured output
    vader_scores = data["cleaned_text"].apply(lambda x: sia.polarity_scores(x))
    data["sentiments"] = vader_scores.apply(lambda s: s["compound"])  # compound for legacy usage
    data["pos_score"] = vader_scores.apply(lambda s: s.get("pos", 0.0))
    data["neg_score"] = vader_scores.apply(lambda s: s.get("neg", 0.0))
    data["neu_score"] = vader_scores.apply(lambda s: s.get("neu", 0.0))
    data["sentiment_category"] = data["sentiments"].apply(get_sentiment)

    # Sentiment distribution countplot
    plt.figure(figsize=(8, 6))
    ax = sns.countplot(x=data["sentiment_category"])
    ax.set_title("Distribution of Sentiments")
    ax.set_xlabel("Sentiment Category")
    ax.set_ylabel("Frequency")
    sent_dist_path = output_dir / "sentiment_distribution_bar.png"
    plt.savefig(sent_dist_path, bbox_inches="tight")
    if show_plots:
        plt.show()
    plt.close()

    # Combine topic + sentiment
    print("Analyzing topic-sentiment relationship...")
    data["dominant_topic"] = np.argmax(topic_distribution, axis=1)
    topic_sentiment_distribution = (
        data.groupby(["dominant_topic", "sentiment_category"]).size().unstack(fill_value=0)
    )

    # Bar charts per topic
    n_topics_found = len(topic_sentiment_distribution.index)
    fig, axes = plt.subplots(ncols=n_topics_found, figsize=(3 * n_topics_found, 5), sharey=True)
    if n_topics_found == 1:
        axes = [axes]
    fig.suptitle("Sentiment Distribution Across Topics")
    for idx, (topic, sentiment_counts) in enumerate(topic_sentiment_distribution.iterrows()):
        ax = axes[idx]
        sentiment_counts.plot(kind="bar", ax=ax, title=f"Topic {topic}")
        ax.set_xlabel("Sentiment Category")
        ax.set_ylabel("Frequency")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    bar_path = output_dir / "topic_sentiment_bar.png"
    plt.savefig(bar_path, bbox_inches="tight")
    if show_plots:
        plt.show()
    plt.close()

    # Pie charts per topic
    fig, axes = plt.subplots(ncols=n_topics_found, figsize=(3 * n_topics_found, 5))
    if n_topics_found == 1:
        axes = [axes]
    fig.suptitle("Sentiment Distribution Across Topics (Pie Chart)")
    for idx, (topic, sentiment_counts) in enumerate(topic_sentiment_distribution.iterrows()):
        ax = axes[idx]
        sentiment_counts.plot(kind="pie", ax=ax, autopct="%1.1f%%", startangle=90)
        ax.set_ylabel("")
        ax.set_xlabel(f"Topic {topic}")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    pie_topics_path = output_dir / "topic_sentiment_pie.png"
    plt.savefig(pie_topics_path, bbox_inches="tight")
    if show_plots:
        plt.show()
    plt.close()

    # Save enriched dataset
    out_csv = output_dir / "enriched_topic_sentiment.csv"
    data.to_csv(out_csv, index=False)

    # Build structured JSON outputs for API/frontend consumption
    # Topic modeling structured result
    topic_modeling_results = {
        "algorithm": "NMF (scikit-learn, TF-IDF)",
        "num_topics": int(n_topics),
        "topics": topics_summary,
    }

    # Sentiment structured result
    dist = data["sentiment_category"].value_counts(normalize=True)
    counts = data["sentiment_category"].value_counts()
    overall_sentiment = str(dist.idxmax()) if not dist.empty else "Neutral"
    # Confidence as average absolute compound score
    overall_confidence = float(np.clip(np.abs(data["sentiments"]).mean() if len(data) else 0.0, 0.0, 1.0))

    # Construct sentence-level (sampled) results to limit payload size
    max_samples = 100
    results_rows = data.head(max_samples)
    detailed_results = [
        {
            "sentence": str(row.get(text_column, "")),
            "sentiment": str(row.get("sentiment_category", "Neutral")),
            "confidence": float(abs(row.get("sentiments", 0.0))),
            "positive_score": float(row.get("pos_score", 0.0)),
            "negative_score": float(row.get("neg_score", 0.0)),
            "neutral_score": float(row.get("neu_score", 0.0)),
        }
        for _, row in results_rows.iterrows()
    ]

    sentiment_results = {
        "overall_sentiment": overall_sentiment,
        "overall_confidence": overall_confidence,
        "sentiment_distribution": {
            "positive": float(dist.get("Positive", 0.0)),
            "negative": float(dist.get("Negative", 0.0)),
            "neutral": float(dist.get("Neutral", 0.0)),
        },
        # Placeholder emotional indicators (VADER is not emotion-aware)
        "emotional_indicators": {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
        },
        "results": detailed_results,
        "summary": {
            "total_sentences": int(len(data)),
            "positive_sentences": int(counts.get("Positive", 0)),
            "negative_sentences": int(counts.get("Negative", 0)),
            "neutral_sentences": int(counts.get("Neutral", 0)),
            "average_confidence": overall_confidence,
        },
    }

    # Persist structured results for reference/debugging
    try:
        import json
        with (output_dir / "structured_results.json").open("w", encoding="utf-8") as f:
            json.dump({
                "topic_modeling_results": topic_modeling_results,
                "sentiment_results": sentiment_results,
            }, f, indent=2)
    except Exception:
        # Non-fatal if JSON writing fails
        pass

    print("Done.")
    print("Artifacts written:")
    for p in [
        *sorted(wc_dir.glob("*.png")),
        pie_path,
        sent_dist_path,
        bar_path,
        pie_topics_path,
        out_csv,
    ]:
        print(" -", p)

    # Return structured results for callers (e.g., FastAPI service)
    return {
        "topic_modeling_results": topic_modeling_results,
        "sentiment_results": sentiment_results,
    }


# -------------------------
# Entrypoint
# -------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Topic Modeling and Sentiment Analysis")
    parser.add_argument(
        "--excel",
        type=Path,
        default=Path("Airport feedback.xlsx"),
        help="Path to Excel file containing a column with free-form feedback.",
    )
    parser.add_argument(
        "--text-column",
        type=str,
        default="Airport Service Freeform Feedback",
        help="Name of the text column in the Excel file.",
    )
    parser.add_argument("--topics", type=int, default=5, help="Number of LDA topics.")
    parser.add_argument("--max-df", type=float, default=0.95, help="CountVectorizer max_df")
    parser.add_argument("--min-df", type=int, default=2, help="CountVectorizer min_df")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs"),
        help="Directory to write images and enriched CSV.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not display plots interactively (still saved to disk).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    show_plots = not args.no_show

    run_pipeline(
        excel_path=args.excel,
        text_column=args.text_column,
        n_topics=args.topics,
        max_df=args.max_df,
        min_df=args.min_df,
        output_dir=args.out,
        show_plots=show_plots,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
