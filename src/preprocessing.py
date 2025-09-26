"""Utilities for loading and preprocessing raw text corpora.

The functions in this module mirror the data preparation steps that are
implemented inside the Narrative Nexus notebook, but provide a cleaner API
for use inside the application codebase.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


_NLTK_PACKAGES = ("stopwords", "punkt", "wordnet")


def _ensure_nltk_packages() -> None:
    """Download the NLTK resources used by the preprocessing step."""

    for package in _NLTK_PACKAGES:
        try:
            nltk.data.find(f"corpora/{package}")
        except LookupError:  # pragma: no cover - network guard
            nltk.download(package, quiet=True)


def _load_single_dataset(path: Path, source: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    rename_map: Dict[str, str] = {
        "article": "text",
        "review": "text",
        "body": "text",
        "content": "text",
    }
    for original, replacement in rename_map.items():
        if original in df.columns and "text" not in df.columns:
            df = df.rename(columns={original: replacement})

    if "text" not in df.columns:
        raise ValueError(f"Dataset {path} is missing a text column")

    drop_candidates = {"summary", "sentiment", "label", "labels"}
    existing_drop = [c for c in drop_candidates if c in df.columns]
    if existing_drop:
        df = df.drop(columns=existing_drop)

    df = df[["text"]].copy()
    df["source"] = source
    return df


def load_and_merge_datasets(
    bbc_path: Path,
    cnn_path: Path,
    imdb_path: Path,
) -> pd.DataFrame:
    """Load the BBC, CNN and IMDB corpora and combine them into one DataFrame."""

    datasets = [
        _load_single_dataset(bbc_path, "bbc"),
        _load_single_dataset(cnn_path, "cnn"),
        _load_single_dataset(imdb_path, "imdb"),
    ]
    merged = pd.concat(datasets, ignore_index=True)
    merged = merged.dropna(subset=["text"]).reset_index(drop=True)
    return merged


def build_preprocess_assets() -> Tuple[set, WordNetLemmatizer]:
    """Instantiate the stop-word list and lemmatizer used for cleaning text."""

    _ensure_nltk_packages()
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    return stop_words, lemmatizer


def preprocess_text(text: str, stop_words: Iterable[str], lemmatizer: WordNetLemmatizer) -> str:
    """Clean, tokenize and lemmatize a single string."""

    text = clean_text(text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(tok) for tok in tokens if tok not in stop_words]
    return " ".join(tokens)


def apply_preprocessing(df: pd.DataFrame, text_column: str = "text") -> pd.DataFrame:
    """Return a new DataFrame with an additional `clean_text` column."""

    stop_words, lemmatizer = build_preprocess_assets()
    df = df.copy()
    df[text_column] = df[text_column].astype(str)
    df["clean_text"] = df[text_column].apply(lambda x: preprocess_text(x, stop_words, lemmatizer))
    return df


def save_preprocessed_dataset(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def clean_text(text: str) -> str:
    """Basic textual cleanup used by both preprocessing and API ingress."""

    text = re.sub(r"[^a-zA-Z\s]", " ", str(text).lower())
    text = re.sub(r"\s+", " ", text)
    return text.strip()


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    data_dir = Path(__file__).resolve().parents[1] / "data"
    merged = load_and_merge_datasets(
        data_dir / "bbc-text.csv",
        data_dir / "cnn_dailymail.csv",
        data_dir / "imdb-dataset.csv",
    )
    processed = apply_preprocessing(merged)
    save_preprocessed_dataset(processed, data_dir / "merged_preprocessed.csv")
    print(processed.head())