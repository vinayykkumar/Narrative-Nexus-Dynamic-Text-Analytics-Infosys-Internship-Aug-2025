# src/sentiment_analysis.py
"""
Compute sentiment scores for documents using NLTK VADER.

Usage:
python src/sentiment_analysis.py --input models/job_desc/nmf/doc_topics_with_text.csv --out models/job_desc/nmf/sentiment_scores.csv --text-col doc
"""

import argparse
import pandas as pd
from pathlib import Path

# try import VADER
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk
    nltk.download("vader_lexicon", quiet=True)
    _HAS_VADER = True
except Exception:
    _HAS_VADER = False


def compute_sentiment_vader(texts):
    sia = SentimentIntensityAnalyzer()
    return [sia.polarity_scores(t)["compound"] for t in texts]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV with doc text")
    parser.add_argument("--out", required=True, help="output CSV path with sentiment scores")
    parser.add_argument("--text-col", default="doc", help="column name containing text")
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    if args.text_col not in df.columns:
        raise ValueError(f"Column '{args.text_col}' not found in {args.input}. Available: {df.columns.tolist()}")

    if not _HAS_VADER:
        raise ImportError("NLTK VADER not available. Run `pip install nltk` and `nltk.download('vader_lexicon')`.")

    scores = compute_sentiment_vader(df[args.text_col].astype(str).tolist())
    df_out = df.copy()
    df_out["sentiment_score"] = scores
    out_path = Path(args.out)
    df_out.to_csv(out_path, index=False)
    print("Saved sentiment scores ->", out_path)


if __name__ == "__main__":
    main()
