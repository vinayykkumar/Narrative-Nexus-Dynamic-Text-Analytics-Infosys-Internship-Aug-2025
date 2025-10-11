"""Sentiment modelling utilities for Narrative Nexus."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from textblob import TextBlob


try:  # pragma: no cover - import guard for optional dependency
    from tensorflow.keras.layers import Dense, Dropout, Embedding, LSTM  # type: ignore
    from tensorflow.keras.models import Sequential, load_model  # type: ignore
    from tensorflow.keras.preprocessing.sequence import pad_sequences  # type: ignore
    from tensorflow.keras.preprocessing.text import Tokenizer  # type: ignore
except ImportError:  # pragma: no cover - runtime guard
    Dense = Dropout = Embedding = LSTM = Sequential = load_model = pad_sequences = Tokenizer = None

try:  # pragma: no cover - optional dependency for transformer model
    from transformers import pipeline
except Exception:  # pragma: no cover - broader guard (covers torch version issues)
    pipeline = None


MODEL_DIR = Path("models")
MAX_WORDS = 10000
MAX_LEN = 200
EMBEDDING_DIM = 100
NEUTRAL_POLARITY_THRESHOLD = 0.08


@dataclass
class SentimentTrainingResults:
    rule_metrics: Dict[str, float]
    ml_metrics: Dict[str, float]
    dl_metrics: Dict[str, float]


@dataclass
class SentimentInferenceModels:
    ml_model: Optional[LogisticRegression]
    tfidf_vectorizer: Optional[TfidfVectorizer]
    tokenizer: Optional[Any]
    dl_model: Optional[Any]
    transformer_pipeline: Optional[Any]


def load_imdb_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={"review": "text"})
    if "sentiment" not in df.columns:
        raise ValueError("IMDB dataset must include a 'sentiment' column")
    df["sentiment"] = df["sentiment"].map({"positive": 1, "negative": 0})
    df = df.dropna(subset=["text", "sentiment"])
    df["text"] = df["text"].astype(str)
    return df


def evaluate_model(y_true, y_pred, y_prob) -> Dict[str, float]:
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else float("nan"),
        "neg_recall": recall_score(y_true, y_pred, pos_label=0, zero_division=0),
    }
    return metrics


def rule_based_sentiment(text: str) -> Dict[str, float]:
    blob = TextBlob(text)
    polarity = float(blob.sentiment.polarity)
    if polarity >= NEUTRAL_POLARITY_THRESHOLD:
        label = "positive"
    elif polarity <= -NEUTRAL_POLARITY_THRESHOLD:
        label = "negative"
    else:
        label = "neutral"
    probability = (polarity + 1) / 2  # map [-1,1] -> [0,1]
    return {
        "label": label,
        "polarity": polarity,
        "probability": probability,
        "subjectivity": float(blob.sentiment.subjectivity),
    }


def _expand_binary_probability(prob: float) -> Dict[str, float]:
    prob = max(0.0, min(1.0, float(prob)))
    neutral = max(0.0, 1.0 - abs(prob - 0.5) * 2.0)
    active = 1.0 - neutral
    positive = prob * active
    negative = (1.0 - prob) * active
    total = positive + negative + neutral
    if total <= 0:
        return {"positive": 0.5, "negative": 0.5, "neutral": 0.0}
    return {
        "positive": positive / total,
        "negative": negative / total,
        "neutral": neutral / total,
    }


def _normalise_distribution(distribution: Dict[str, float]) -> Dict[str, float]:
    positive = max(0.0, float(distribution.get("positive", 0.0)))
    negative = max(0.0, float(distribution.get("negative", 0.0)))
    neutral = max(0.0, float(distribution.get("neutral", 0.0)))
    total = positive + negative + neutral
    if total <= 0:
        return {"positive": 0.5, "negative": 0.5, "neutral": 0.0}
    return {
        "positive": positive / total,
        "negative": negative / total,
        "neutral": neutral / total,
    }


def _distribution_to_label(distribution: Dict[str, float]) -> str:
    if not distribution:
        return "neutral"
    return max(distribution.items(), key=lambda item: item[1])[0]


def _distribution_confidence(distribution: Dict[str, float]) -> float:
    label = _distribution_to_label(distribution)
    return float(distribution.get(label, 0.0))


def train_logistic_regression(X: Sequence[str], y: Sequence[int], model_dir: Path) -> Dict[str, Any]:
    tfidf = TfidfVectorizer(max_features=5000, stop_words="english")
    X_tfidf = tfidf.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=500)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = evaluate_model(y_test, y_pred, y_prob)

    joblib.dump(model, model_dir / "sentiment_ml.pkl")
    joblib.dump(tfidf, model_dir / "sentiment_tfidf.pkl")

    return {"model": model, "vectorizer": tfidf, "metrics": metrics}


def train_lstm_model(X: Sequence[str], y: Sequence[int], model_dir: Path) -> Dict[str, Any]:
    if None in (Embedding, LSTM, Sequential, Tokenizer, pad_sequences):
        raise ImportError("TensorFlow is required to train the LSTM sentiment model. Install tensorflow>=2.0.")

    tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
    tokenizer.fit_on_texts(X)

    sequences = tokenizer.texts_to_sequences(X)
    padded = pad_sequences(sequences, maxlen=MAX_LEN, padding="post")
    y_array = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(padded, y_array, test_size=0.2, random_state=42)

    model = Sequential()
    model.add(Embedding(MAX_WORDS, EMBEDDING_DIM, input_length=MAX_LEN))
    model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(1, activation="sigmoid"))

    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    model.fit(X_train, y_train, epochs=3, batch_size=64, validation_data=(X_test, y_test), verbose=1)

    y_prob = model.predict(X_test, verbose=0).flatten()
    y_pred = (y_prob >= 0.5).astype(int)
    metrics = evaluate_model(y_test, y_pred, y_prob)

    model.save(model_dir / "sentiment_lstm.h5")
    joblib.dump(tokenizer, model_dir / "sentiment_tokenizer.pkl")

    return {"model": model, "tokenizer": tokenizer, "metrics": metrics}


def train_sentiment_models(df: pd.DataFrame, model_dir: Path = MODEL_DIR) -> SentimentTrainingResults:
    model_dir.mkdir(parents=True, exist_ok=True)

    X = df["text"].astype(str)
    y = df["sentiment"].astype(int)

    rule_preds = np.array([1 if rule_based_sentiment(text)["label"] == "positive" else 0 for text in X])
    rule_probs = np.array([rule_based_sentiment(text)["probability"] for text in X])
    rule_metrics = evaluate_model(y, rule_preds, rule_probs)

    ml_artifacts = train_logistic_regression(X, y, model_dir)
    dl_artifacts = train_lstm_model(X, y, model_dir)

    return SentimentTrainingResults(
        rule_metrics=rule_metrics,
        ml_metrics=ml_artifacts["metrics"],
        dl_metrics=dl_artifacts["metrics"],
    )


def load_sentiment_models(model_dir: Path = MODEL_DIR) -> SentimentInferenceModels:
    ml_model = tfidf = tokenizer = dl_model = transformer = None

    ml_path = model_dir / "sentiment_ml.pkl"
    tfidf_path = model_dir / "sentiment_tfidf.pkl"
    lstm_path = model_dir / "sentiment_lstm.h5"
    tok_path = model_dir / "sentiment_tokenizer.pkl"

    if ml_path.exists() and tfidf_path.exists():
        ml_model = joblib.load(ml_path)
        tfidf = joblib.load(tfidf_path)

    if lstm_path.exists() and tok_path.exists() and load_model is not None:
        dl_model = load_model(lstm_path)
        tokenizer = joblib.load(tok_path)

    if pipeline is not None:
        try:  # pragma: no cover - download can fail on CI without internet
            transformer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True,
                device=-1,
                truncation=True,
                max_length=256,
            )
        except Exception as primary_exc:  # pragma: no cover - runtime guard
            print("⚠️ CardiffNLP sentiment model unavailable:", primary_exc)
            try:
                transformer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    return_all_scores=True,
                    framework="pt",
                    device=-1,
                    truncation=True,
                )
            except Exception as fallback_exc:  # pragma: no cover - runtime guard
                transformer = None
                print("⚠️ Transformer sentiment model unavailable:", fallback_exc)

    return SentimentInferenceModels(
        ml_model=ml_model,
        tfidf_vectorizer=tfidf,
        tokenizer=tokenizer,
        dl_model=dl_model,
        transformer_pipeline=transformer,
    )


def _predict_ml(texts: Sequence[str], models: SentimentInferenceModels) -> Optional[np.ndarray]:
    if models.ml_model is None or models.tfidf_vectorizer is None:
        return None
    matrix = models.tfidf_vectorizer.transform(texts)
    return models.ml_model.predict_proba(matrix)[:, 1]


def _predict_dl(texts: Sequence[str], models: SentimentInferenceModels) -> Optional[np.ndarray]:
    if models.dl_model is None or models.tokenizer is None or pad_sequences is None:
        return None
    sequences = models.tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=MAX_LEN, padding="post")
    probs = models.dl_model.predict(padded, verbose=0).flatten()
    return probs


def _predict_transformer(texts: Sequence[str], models: SentimentInferenceModels) -> Optional[List[Dict[str, float]]]:
    pipe = getattr(models, "transformer_pipeline", None)
    if pipe is None:
        return None

    try:
        outputs = pipe(list(texts), return_all_scores=True)
    except Exception as exc:
        print("⚠️ Transformer inference failed:", exc)
        return None

    distributions: List[Dict[str, float]] = []
    for result in outputs:
        entries = result if isinstance(result, list) else [result]
        probs = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        for entry in entries:
            label = str(entry["label"]).lower()
            score = float(entry["score"])
            if "pos" in label or label.endswith("_2"):
                probs["positive"] = max(probs["positive"], score)
            elif "neg" in label or label.endswith("_0"):
                probs["negative"] = max(probs["negative"], score)
            elif "neu" in label or label.endswith("_1"):
                probs["neutral"] = max(probs["neutral"], score)
        total = sum(probs.values())
        if total <= 0 and entries:
            primary = entries[0]
            base_label = str(primary["label"]).lower()
            base_score = float(primary["score"])
            if "neg" in base_label:
                probs["negative"] = base_score
                probs["positive"] = max(0.0, 1.0 - base_score)
            elif "pos" in base_label:
                probs["positive"] = base_score
                probs["negative"] = max(0.0, 1.0 - base_score)
            else:
                probs["neutral"] = max(0.0, base_score)
        distributions.append(_normalise_distribution(probs))

    return distributions


def analyze_sentiment_text(text: str, models: Optional[SentimentInferenceModels]) -> Dict[str, Any]:
    rule_raw = rule_based_sentiment(text)
    rule_distribution = _expand_binary_probability(rule_raw["probability"])
    rule_confidence = _distribution_confidence(rule_distribution)
    rule_payload: Dict[str, Any] = {
        **rule_raw,
        "distribution": rule_distribution,
        "confidence": rule_confidence,
    }

    if models is None:
        overall_label = _distribution_to_label(rule_distribution)
        overall_probability = rule_distribution["positive"]
        return {
            "overall": {
                "label": overall_label,
                "confidence": rule_confidence,
                "probability": overall_probability,
            },
            "rule_based": rule_payload,
            "ml": None,
            "dl": None,
            "transformer": None,
            "distribution": rule_distribution,
            "votes": {overall_label: 1},
            "models": [
                {
                    "name": "rule_based",
                    "weight": 1.0,
                    "label": overall_label,
                    "confidence": rule_confidence,
                    "distribution": rule_distribution,
                }
            ],
        }

    aggregate_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    total_weight = 0.0
    votes: Counter[str] = Counter()
    model_snapshots: List[Dict[str, Any]] = []

    def register_model(name: str, info: Optional[Dict[str, Any]], base_weight: float) -> None:
        nonlocal total_weight
        if info is None:
            return
        distribution = _normalise_distribution(info.get("distribution", {}))
        info["distribution"] = distribution
        info.setdefault("confidence", _distribution_confidence(distribution))
        confidence = float(info["confidence"])
        weight = base_weight * (0.4 + 0.6 * confidence)
        if votes:
            majority_label, _ = votes.most_common(1)[0]
            if distribution.get(majority_label, 0.0) < 0.34 and confidence > 0.3:
                weight *= 0.65
        for label, prob in distribution.items():
            aggregate_scores[label] += prob * weight
        total_weight += weight
        top_label = _distribution_to_label(distribution)
        votes[top_label] += 1
        model_snapshots.append(
            {
                "name": name,
                "weight": weight,
                "label": top_label,
                "confidence": confidence,
                "distribution": distribution,
            }
        )

    register_model("rule_based", rule_payload, base_weight=0.9)

    ml_info: Optional[Dict[str, Any]] = None
    ml_prob = _predict_ml([text], models)
    if ml_prob is not None:
        ml_value = float(ml_prob[0])
        ml_distribution = _expand_binary_probability(ml_value)
        ml_info = {
            "label": _distribution_to_label(ml_distribution),
            "probability": ml_value,
            "confidence": _distribution_confidence(ml_distribution),
            "distribution": ml_distribution,
        }
        register_model("ml", ml_info, base_weight=1.6)

    dl_info: Optional[Dict[str, Any]] = None
    dl_prob = _predict_dl([text], models)
    if dl_prob is not None:
        dl_value = float(dl_prob[0])
        dl_distribution = _expand_binary_probability(dl_value)
        dl_info = {
            "label": _distribution_to_label(dl_distribution),
            "probability": dl_value,
            "confidence": _distribution_confidence(dl_distribution),
            "distribution": dl_distribution,
        }
        register_model("dl", dl_info, base_weight=1.25)

    transformer_info: Optional[Dict[str, Any]] = None
    transformer_outputs = _predict_transformer([text], models)
    if transformer_outputs:
        transformer_distribution = _normalise_distribution(transformer_outputs[0])
        transformer_info = {
            "label": _distribution_to_label(transformer_distribution),
            "probability": transformer_distribution.get("positive", 0.0),
            "confidence": _distribution_confidence(transformer_distribution),
            "distribution": transformer_distribution,
        }
        register_model("transformer", transformer_info, base_weight=1.8)

    if total_weight <= 0:
        aggregated_distribution = rule_distribution
    else:
        total = sum(aggregate_scores.values())
        if total <= 0:
            aggregated_distribution = rule_distribution
        else:
            aggregated_distribution = {
                label: aggregate_scores[label] / total for label in aggregate_scores
            }

    overall_label = _distribution_to_label(aggregated_distribution)
    overall_confidence = _distribution_confidence(aggregated_distribution)
    overall_probability = aggregated_distribution.get("positive", 0.0)

    if not votes:
        votes[overall_label] += 1

    return {
        "overall": {
            "label": overall_label,
            "confidence": overall_confidence,
            "probability": overall_probability,
        },
        "rule_based": rule_payload,
        "ml": ml_info,
        "dl": dl_info,
        "transformer": transformer_info,
        "distribution": aggregated_distribution,
        "votes": dict(votes),
        "models": model_snapshots,
    }


def analyze_sentiment_batch(texts: Sequence[str], models: Optional[SentimentInferenceModels]) -> List[Dict[str, Any]]:
    return [analyze_sentiment_text(text, models) for text in texts]


if __name__ == "__main__":  # pragma: no cover - manual run helper
    data_path = Path(__file__).resolve().parents[1] / "data" / "imdb-dataset.csv"
    imdb_df = load_imdb_dataset(data_path)
    metrics = train_sentiment_models(imdb_df)
    print("Rule-based metrics:", metrics.rule_metrics)
    print("Logistic Regression metrics:", metrics.ml_metrics)
    print("LSTM metrics:", metrics.dl_metrics)