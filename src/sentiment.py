"""Sentiment modelling utilities for Narrative Nexus."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

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
    label = "positive" if polarity >= 0 else "negative"
    probability = (polarity + 1) / 2  # map [-1,1] -> [0,1]
    return {
        "label": label,
        "polarity": polarity,
        "probability": probability,
        "subjectivity": float(blob.sentiment.subjectivity),
    }


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
                model="distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True,
                framework="pt",
                device=-1,
                truncation=True,
            )
        except Exception as exc:  # pragma: no cover - runtime guard
            transformer = None
            print("⚠️ Transformer sentiment model unavailable:", exc)

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


def _predict_transformer(texts: Sequence[str], models: SentimentInferenceModels) -> Optional[Tuple[List[float], List[str]]]:
    pipe = getattr(models, "transformer_pipeline", None)
    if pipe is None:
        return None

    try:
        outputs = pipe(list(texts))
    except Exception as exc:
        print("⚠️ Transformer inference failed:", exc)
        return None
    probabilities: List[float] = []
    labels: List[str] = []

    for result in outputs:
        entries = result if isinstance(result, list) else [result]
        pos_entry = next((item for item in entries if str(item["label"]).upper().startswith("POS")), None)
        neg_entry = next((item for item in entries if str(item["label"]).upper().startswith("NEG")), None)

        if pos_entry is not None:
            prob = float(pos_entry["score"])
        elif neg_entry is not None:
            prob = 1.0 - float(neg_entry["score"])
        else:
            prob = float(entries[0]["score"])

        label = "positive" if prob >= 0.5 else "negative"
        probabilities.append(prob)
        labels.append(label)

    return probabilities, labels


def _prob_to_label(prob: float) -> str:
    return "positive" if prob >= 0.5 else "negative"


def analyze_sentiment_text(text: str, models: Optional[SentimentInferenceModels]) -> Dict[str, Any]:
    rule_info = rule_based_sentiment(text)
    rule_info["confidence"] = abs(float(rule_info["probability"]) - 0.5) * 2

    if models is None:
        avg_prob = float(rule_info["probability"])
        label = rule_info["label"]
        confidence = abs(avg_prob - 0.5) * 2
        neutral_weight = max(0.0, 1.0 - confidence)
        active_weight = 1.0 - neutral_weight
        positive_weight = max(0.0, avg_prob * active_weight)
        negative_weight = max(0.0, (1.0 - avg_prob) * active_weight)
        total_weight = positive_weight + negative_weight + neutral_weight
        if total_weight > 0:
            distribution = {
                "positive": positive_weight / total_weight,
                "neutral": neutral_weight / total_weight,
                "negative": negative_weight / total_weight,
            }
        else:
            distribution = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}

        return {
            "overall": {"label": label, "confidence": confidence, "probability": avg_prob},
            "rule_based": rule_info,
            "ml": None,
            "dl": None,
            "transformer": None,
            "distribution": distribution,
        }

    ml_prob = _predict_ml([text], models)
    ml_info = None
    if ml_prob is not None:
        ml_prob = float(ml_prob[0])
        ml_confidence = abs(ml_prob - 0.5) * 2
        ml_info = {"label": _prob_to_label(ml_prob), "probability": ml_prob, "confidence": ml_confidence}

    dl_prob = _predict_dl([text], models)
    dl_info = None
    if dl_prob is not None:
        dl_prob = float(dl_prob[0])
        dl_confidence = abs(dl_prob - 0.5) * 2
        dl_info = {"label": _prob_to_label(dl_prob), "probability": dl_prob, "confidence": dl_confidence}

    transformer_probs = _predict_transformer([text], models)
    transformer_info = None
    if transformer_probs is not None:
        prob = float(transformer_probs[0][0])
        label = transformer_probs[1][0]
        transformer_confidence = abs(prob - 0.5) * 2
        transformer_info = {"label": label, "probability": prob, "confidence": transformer_confidence}

    contributions: List[Tuple[float, float]] = []
    votes: Counter[str] = Counter()

    rule_prob = float(rule_info["probability"])
    rule_weight = 1.3
    contributions.append((rule_prob, rule_weight))
    votes[_prob_to_label(rule_prob)] += 1

    def _register_model(info: Optional[Dict[str, float]], base_weight: float) -> None:
        if info is None:
            return
        prob = float(info["probability"])
        confidence = abs(prob - 0.5) * 2
        adaptive_weight = base_weight * (0.35 + 0.65 * confidence)
        disagreement = abs(prob - rule_prob)
        if disagreement >= 0.35:
            adaptive_weight *= 0.3
        elif disagreement >= 0.2:
            adaptive_weight *= 0.55
        contributions.append((prob, adaptive_weight))
        votes[_prob_to_label(prob)] += 1

    _register_model(ml_info, base_weight=0.9)
    _register_model(dl_info, base_weight=0.9)
    _register_model(transformer_info, base_weight=1.6)

    if contributions:
        total_weight = sum(weight for _, weight in contributions)
        weighted_sum = sum(prob * weight for prob, weight in contributions)
        avg_prob = weighted_sum / total_weight if total_weight else rule_prob
    else:
        avg_prob = rule_prob

    overall_label = _prob_to_label(avg_prob)
    if votes:
        voted_label, vote_count = votes.most_common(1)[0]
        if vote_count >= 2 or len(votes) == 1:
            overall_label = voted_label

    confidence = abs(avg_prob - 0.5) * 2

    neutral_weight = max(0.0, 1.0 - confidence)
    active_weight = 1.0 - neutral_weight
    positive_weight = max(0.0, avg_prob * active_weight)
    negative_weight = max(0.0, (1.0 - avg_prob) * active_weight)
    total_weight = positive_weight + negative_weight + neutral_weight

    if total_weight > 0:
        distribution = {
            "positive": positive_weight / total_weight,
            "neutral": neutral_weight / total_weight,
            "negative": negative_weight / total_weight,
        }
    else:
        distribution = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}

    return {
        "overall": {"label": overall_label, "confidence": confidence, "probability": avg_prob},
        "rule_based": rule_info,
        "ml": ml_info,
        "dl": dl_info,
        "transformer": transformer_info,
        "distribution": distribution,
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