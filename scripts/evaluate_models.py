"""Comprehensive evaluation harness for Narrative Nexus models.

This script reports quantitative metrics for sentiment, topic modelling, and
summarisation components.  It is intentionally lightweight so it can be run in
development environments without re-training the models.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"

if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

import joblib
import numpy as np
import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from rouge_score import rouge_scorer

from src.sentiment import (
	SentimentInferenceModels,
	analyze_sentiment_text,
	evaluate_model,
	load_imdb_dataset,
	load_sentiment_models,
)
from src.summarization import abstractive_summary, extractive_summary, get_abstractive_summarizer
from src.topic_modeling import describe_topics


def _summarise_scores(rows: Iterable[Dict[str, float]]) -> Dict[str, float]:
	aggregated: Dict[str, List[float]] = {}
	for row in rows:
		for metric, value in row.items():
			aggregated.setdefault(metric, []).append(float(value))
	return {
		metric: float(statistics.mean(values)) if values else float("nan")
		for metric, values in aggregated.items()
	}


def evaluate_sentiment_models(
	dataset_path: Path,
	sample_size: Optional[int],
	random_state: int = 42,
) -> Dict[str, Any]:
	df = load_imdb_dataset(dataset_path)
	if sample_size and len(df) > sample_size:
		df = df.sample(sample_size, random_state=random_state).reset_index(drop=True)

	models: SentimentInferenceModels = load_sentiment_models(MODEL_DIR)

	component_records: Dict[str, Dict[str, List[float]]] = {}
	for key in ("overall", "rule_based", "ml", "dl", "transformer"):
		component_records[key] = {"y_true": [], "y_prob": []}

	for row in df.itertuples(index=False):
		insight = analyze_sentiment_text(str(row.text), models)
		label = int(row.sentiment)

		for key in component_records.keys():
			payload = insight.get(key)
			if payload is None:
				continue
			probability = payload.get("probability")
			if probability is None:
				continue
			component_records[key]["y_true"].append(label)
			component_records[key]["y_prob"].append(float(probability))

	metrics: Dict[str, Any] = {"samples": len(df)}
	for key, record in component_records.items():
		if not record["y_true"]:
			continue
		y_true = np.array(record["y_true"])
		y_prob = np.array(record["y_prob"])
		y_pred = (y_prob >= 0.5).astype(int)
		metrics[key] = evaluate_model(y_true, y_pred, y_prob)
		metrics[key]["support"] = int(y_true.size)

	return metrics


def evaluate_summarisation_models(
	dataset_path: Path,
	sample_size: Optional[int],
	random_state: int = 42,
) -> Dict[str, Any]:
	df = pd.read_csv(dataset_path).dropna(subset=["article", "summary"])
	if sample_size and len(df) > sample_size:
		df = df.sample(sample_size, random_state=random_state).reset_index(drop=True)

	scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

	extractive_scores: List[Dict[str, float]] = []
	abstractive_scores: List[Dict[str, float]] = []

	abstractive_available = get_abstractive_summarizer() is not None

	for row in df.itertuples(index=False):
		article = str(row.article)
		reference = str(row.summary)

		extractive = extractive_summary(article)
		extractive_result = scorer.score(reference, extractive)
		extractive_scores.append({metric: values.fmeasure for metric, values in extractive_result.items()})

		if abstractive_available:
			try:
				abstractive = abstractive_summary(article)
			except Exception as exc:  # pragma: no cover - runtime guard
				abstractive_available = False
				print(f"⚠️ Abstractive summariser unavailable mid-run: {exc}")
			else:
				abstractive_result = scorer.score(reference, abstractive)
				abstractive_scores.append({metric: values.fmeasure for metric, values in abstractive_result.items()})

	results: Dict[str, Any] = {"samples": len(df)}
	results["extractive"] = _summarise_scores(extractive_scores)
	if abstractive_scores:
		results["abstractive"] = _summarise_scores(abstractive_scores)
	else:
		results["abstractive"] = {"status": "not_available"}

	return results


def _compute_coherence(topics: List[List[str]], tokenised_texts: List[List[str]], dictionary: Dictionary) -> float:
	coherence_model = CoherenceModel(topics=topics, texts=tokenised_texts, dictionary=dictionary, coherence="c_v")
	return float(coherence_model.get_coherence())


def evaluate_topic_models(
	dataset_path: Path,
	model_dir: Path,
	sample_size: Optional[int],
	random_state: int = 42,
) -> Dict[str, Any]:
	df = pd.read_csv(dataset_path).dropna(subset=["clean_text"])
	if sample_size and len(df) > sample_size:
		df = df.sample(sample_size, random_state=random_state).reset_index(drop=True)

	clean_texts = df["clean_text"].astype(str).tolist()
	tokenised_texts = [text.split() for text in clean_texts]
	dictionary = Dictionary(tokenised_texts)

	count_vectorizer = joblib.load(model_dir / "count_vectorizer.pkl")
	tfidf_vectorizer = joblib.load(model_dir / "tfidf_vectorizer.pkl")
	lda = joblib.load(model_dir / "lda_model.pkl")
	nmf = joblib.load(model_dir / "nmf_model.pkl")

	count_matrix = count_vectorizer.transform(clean_texts)
	tfidf_matrix = tfidf_vectorizer.transform(clean_texts)

	lda_topics = describe_topics(lda, count_vectorizer, top_n=10)
	nmf_topics = describe_topics(nmf, tfidf_vectorizer, top_n=10)

	metrics: Dict[str, Any] = {"samples": len(clean_texts)}
	metrics["lda"] = {
		"perplexity": float(lda.perplexity(count_matrix)),
		"coherence": _compute_coherence(lda_topics, tokenised_texts, dictionary),
	}
	metrics["nmf"] = {
		"coherence": _compute_coherence(nmf_topics, tokenised_texts, dictionary),
	}

	return metrics


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Evaluate Narrative Nexus models")
	parser.add_argument("--sentiment-samples", type=int, default=2000, help="Number of IMDB rows to sample for sentiment evaluation (0 for all)")
	parser.add_argument("--summarisation-samples", type=int, default=25, help="Number of CNN/DailyMail rows to sample for summarisation evaluation (0 for all)")
	parser.add_argument("--topic-samples", type=int, default=5000, help="Number of preprocessed rows to use for topic evaluation (0 for all)")
	parser.add_argument("--output", type=Path, default=None, help="Optional path to write the evaluation JSON report")
	parser.add_argument("--random-state", type=int, default=42, help="Random seed for sampling")
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	sentiment_samples = None if not args.sentiment_samples or args.sentiment_samples <= 0 else args.sentiment_samples
	summarisation_samples = None if not args.summarisation_samples or args.summarisation_samples <= 0 else args.summarisation_samples
	topic_samples = None if not args.topic_samples or args.topic_samples <= 0 else args.topic_samples

	report = {
		"sentiment": evaluate_sentiment_models(DATA_DIR / "imdb-dataset.csv", sentiment_samples, random_state=args.random_state),
		"summarisation": evaluate_summarisation_models(DATA_DIR / "cnn_dailymail.csv", summarisation_samples, random_state=args.random_state),
		"topics": evaluate_topic_models(DATA_DIR / "merged_preprocessed.csv", MODEL_DIR, topic_samples, random_state=args.random_state),
	}

	print(json.dumps(report, indent=2))

	if args.output:
		args.output.parent.mkdir(parents=True, exist_ok=True)
		args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
	main()

