# src/visualization.py
"""
Visualize topic modeling results:
- Topic sizes bar chart
- Wordcloud per topic
- Sentiment histograms per topic (if sentiment scores provided)

Usage:
python src/visualization.py --doc-topics models/job_desc/nmf/doc_topics_with_text.csv --top-words models/job_desc/nmf/top_words.json --sent-csv models/job_desc/nmf/sentiment_scores.csv --sent-col sentiment_score --out viz/job_desc
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json
import numpy as np
from wordcloud import WordCloud


def load_doc_topics(path: Path):
    return pd.read_csv(path)


def load_top_words(path: Path):
    with open(path, "r", encoding="utf8") as f:
        return {int(k): v for k, v in json.load(f).items()}


def plot_topic_sizes(df, out_dir: Path):
    counts = df["dominant_topic"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind="bar", ax=ax)
    ax.set_xlabel("Topic")
    ax.set_ylabel("Number of documents")
    ax.set_title("Topic sizes")
    plt.tight_layout()
    out_file = out_dir / "topic_sizes.png"
    fig.savefig(out_file, dpi=200)
    plt.close(fig)
    print("Saved", out_file)


def make_wordcloud(words_list, out_file: Path):
    freqs = {w: max(1, len(words_list) - i) for i, w in enumerate(words_list)}
    wc = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(freqs)
    wc.to_file(str(out_file))
    print("Saved", out_file)


def plot_sentiment_per_topic(df, out_dir: Path, sent_col="sentiment_score"):
    grouped = df.groupby("dominant_topic")[sent_col].apply(list)
    for topic, scores in grouped.items():
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.hist(scores, bins=20, alpha=0.8)
        ax.set_title(f"Sentiment distribution — Topic {topic}")
        ax.set_xlabel("Sentiment score (VADER compound)")
        ax.set_ylabel("Count")
        plt.tight_layout()
        out_file = out_dir / f"sentiment_topic_{topic}.png"
        fig.savefig(out_file, dpi=200)
        plt.close(fig)
        print("Saved", out_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-topics", required=True)
    parser.add_argument("--top-words", required=True)
    parser.add_argument("--sent-csv", required=False, help="CSV with sentiment scores")
    parser.add_argument("--sent-col", default="sentiment_score")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_doc_topics(Path(args.doc_topics))
    top_words = load_top_words(Path(args.top_words))

    # topic sizes
    plot_topic_sizes(df, out_dir)

    # wordclouds
    for t, words in top_words.items():
        make_wordcloud(words, out_dir / f"wordcloud_topic_{t}.png")

    # sentiment histograms
    if args.sent_csv:
        df_sent = pd.read_csv(args.sent_csv)
        df = df.merge(df_sent[["doc_index", args.sent_col]], on="doc_index", how="left")
        if args.sent_col in df.columns:
            plot_sentiment_per_topic(df, out_dir, sent_col=args.sent_col)

    print("All visuals saved to", out_dir)


if __name__ == "__main__":
    main()
