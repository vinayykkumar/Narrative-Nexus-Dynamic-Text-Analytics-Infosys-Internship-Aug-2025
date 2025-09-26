"""Insight generation module combining summarisation, topics, and sentiment."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from src.summarization import extractive_summary, abstractive_summary
from src.preprocessing import clean_text
from src.sentiment import SentimentInferenceModels, analyze_sentiment_text, rule_based_sentiment
from src.sentiment import MAX_LEN as SENTIMENT_MAX_LEN


MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


CATEGORY_KEYWORDS: Dict[str, set[str]] = {
    "political": {
        "government",
        "policy",
        "election",
        "minister",
        "president",
        "parliament",
        "congress",
        "senate",
        "campaign",
        "vote",
        "diplomacy",
        "legislation",
        "referendum",
        "council",
        "constitution",
        "manifesto",
    },
    "world": {
        "conflict",
        "war",
        "geopolitics",
        "international",
        "global",
        "treaty",
        "crisis",
        "embassy",
        "border",
        "alliance",
        "sanction",
        "summit",
    },
    "science": {
        "science",
        "research",
        "study",
        "scientist",
        "experiment",
        "laboratory",
        "biology",
        "physics",
        "chemistry",
        "genetics",
        "space",
        "nasa",
        "astronomy",
        "climate",
        "ecosystem",
        "innovation",
        "discovery",
        "medicine",
        "health",
        "biotech",
    },
    "technology": {
        "technology",
        "tech",
        "software",
        "hardware",
        "robot",
        "robotics",
        "artificial",
        "intelligence",
        "ai",
        "data",
        "digital",
        "startup",
        "engineering",
        "computer",
        "cyber",
        "quantum",
        "silicon",
        "innovation",
    },
    "sport": {
        "sport",
        "match",
        "game",
        "league",
        "player",
        "team",
        "coach",
        "goal",
        "score",
        "win",
        "victory",
        "season",
        "tournament",
        "cup",
        "championship",
        "athlete",
        "olympic",
        "cricket",
        "football",
        "soccer",
        "basketball",
        "tennis",
        "golf",
        "baseball",
    },
    "business": {
        "market",
        "company",
        "corporate",
        "stock",
        "stocks",
        "finance",
        "financial",
        "bank",
        "revenue",
        "profit",
        "loss",
        "earnings",
        "investment",
        "investor",
        "economy",
        "trade",
        "industry",
        "merger",
        "acquisition",
        "startup",
        "valuation",
    },
    "entertainment": {
        "film",
        "movie",
        "cinema",
        "music",
        "concert",
        "festival",
        "show",
        "series",
        "episode",
        "celebrity",
        "actor",
        "actress",
        "drama",
        "comedy",
        "album",
        "hollywood",
        "bollywood",
        "entertainment",
        "theatre",
    },
}

CATEGORY_GROUP_MAPPING: Dict[str, str] = {
    "political": "political",
    "world": "political",
    "science": "science",
    "technology": "science",
    "sport": "sport",
    "business": "other",
    "entertainment": "other",
}

CATEGORY_DISPLAY: Dict[str, str] = {
    "political": "Political",
    "science": "Science",
    "sport": "Sport",
    "other": "Other",
}


def load_models(model_dir: Path | str = MODEL_DIR):
    """Load the TF-IDF vectorizer and NMF topic model."""

    model_path = Path(model_dir)
    tfidf = joblib.load(model_path / "tfidf_vectorizer.pkl")
    nmf = joblib.load(model_path / "nmf_model.pkl")
    return tfidf, nmf


def _feature_names(tfidf) -> Optional[np.ndarray]:
    if hasattr(tfidf, "get_feature_names_out"):
        return tfidf.get_feature_names_out()
    if hasattr(tfidf, "get_feature_names"):
        return np.array(tfidf.get_feature_names())
    return None


def _tokenise_for_topics(text: str) -> List[str]:
    return [token for token in clean_text(text).split() if token]


def _classify_high_level_topic(text: str, seed_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    tokens = _tokenise_for_topics(text)
    group_counts: Dict[str, int] = defaultdict(int)
    group_matches: Dict[str, set[str]] = defaultdict(set)

    def register_token(token: str) -> None:
        if not token:
            return
        for base_category, lexicon in CATEGORY_KEYWORDS.items():
            if token in lexicon:
                group = CATEGORY_GROUP_MAPPING.get(base_category, "other")
                group_counts[group] += 1
                group_matches[group].add(token)

    for token in tokens:
        register_token(token)

    if seed_keywords:
        for keyword in seed_keywords:
            cleaned = clean_text(keyword)
            for sub_token in cleaned.split():
                register_token(sub_token)

    if not group_counts:
        return {
            "label": CATEGORY_DISPLAY["other"],
            "key": "other",
            "confidence": 0.25,
            "matched_terms": [],
            "total_hits": 0,
        }

    best_group = max(group_counts.items(), key=lambda item: item[1])[0]
    best_hits = group_counts[best_group]
    total_hits = max(sum(group_counts.values()), 1)
    raw_confidence = best_hits / total_hits
    scaled_confidence = min(0.99, 0.25 + raw_confidence * 0.75 + (0.05 if total_hits > 4 else 0.0))

    return {
        "label": CATEGORY_DISPLAY[best_group],
        "key": best_group,
        "confidence": round(scaled_confidence, 4),
        "matched_terms": sorted(group_matches[best_group]),
        "total_hits": total_hits,
    }


def _top_words_for_topic(lda_model, vectorizer, topic_index: int, top_n: int = 8) -> List[str]:
    feature_names = vectorizer.get_feature_names_out()
    weights = lda_model.components_[topic_index]
    top_indices = weights.argsort()[-top_n:][::-1]
    return [feature_names[i] for i in top_indices]


def _ensure_sentiment_models(
    sentiment_source: Optional[Any],
    tokenizer: Optional[Any],
    max_len: int,
    explicit_models: Optional[SentimentInferenceModels],
) -> Optional[SentimentInferenceModels]:
    if explicit_models is not None:
        return explicit_models

    if isinstance(sentiment_source, SentimentInferenceModels):
        return sentiment_source

    dl_model = sentiment_source
    if dl_model is None and tokenizer is None:
        return None

    return SentimentInferenceModels(
        ml_model=None,
        tfidf_vectorizer=None,
        tokenizer=tokenizer,
        dl_model=dl_model,
        transformer_pipeline=None,
    )


def _fallback_sentiment_result(text: str) -> Dict[str, Any]:
    rule = rule_based_sentiment(text)
    prob = float(rule["probability"])
    confidence = abs(prob - 0.5) * 2
    neutral_weight = max(0.0, 1.0 - confidence)
    active_weight = 1.0 - neutral_weight
    positive_weight = max(0.0, prob * active_weight)
    negative_weight = max(0.0, (1.0 - prob) * active_weight)
    total = positive_weight + negative_weight + neutral_weight
    if total > 0:
        distribution = {
            "positive": positive_weight / total,
            "neutral": neutral_weight / total,
            "negative": negative_weight / total,
        }
    else:
        distribution = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}

    return {
        "overall": {"label": rule["label"], "confidence": confidence, "probability": prob},
        "rule_based": rule,
        "ml": None,
        "dl": None,
        "transformer": None,
        "distribution": distribution,
    }


def attach_topic_sentiment(
    df: pd.DataFrame,
    lda_model,
    count_vectorizer,
    sentiment_source: Optional[Any] = None,
    tokenizer: Optional[Any] = None,
    max_len: int = SENTIMENT_MAX_LEN,
    sentiment_models: Optional[SentimentInferenceModels] = None,
) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("attach_topic_sentiment expects a pandas DataFrame as the first argument")

    result = df.copy().reset_index(drop=True)
    if "clean_text" not in result.columns:
        raise ValueError("Input DataFrame must include a 'clean_text' column produced by preprocessing")

    clean_texts = result["clean_text"].astype(str).tolist()
    count_matrix = count_vectorizer.transform(clean_texts)
    topic_distribution = lda_model.transform(count_matrix)
    dominant_topics = topic_distribution.argmax(axis=1)
    dominant_scores = topic_distribution.max(axis=1)

    topic_keyword_cache: Dict[int, List[str]] = {}

    def topic_keywords(idx: int) -> List[str]:
        if idx not in topic_keyword_cache:
            topic_keyword_cache[idx] = _top_words_for_topic(lda_model, count_vectorizer, idx, top_n=8)
        return topic_keyword_cache[idx]

    topic_keywords_list = [topic_keywords(int(idx)) for idx in dominant_topics]

    sentiment_models_to_use = _ensure_sentiment_models(sentiment_source, tokenizer, max_len, sentiment_models)

    sentiment_results: List[Dict[str, Any]] = []
    if sentiment_models_to_use is not None:
        for text in clean_texts:
            sentiment_results.append(analyze_sentiment_text(text, sentiment_models_to_use))
    else:
        sentiment_results = [_fallback_sentiment_result(text) for text in clean_texts]

    result["topic_distribution"] = [row.tolist() for row in topic_distribution]
    result["dominant_topic"] = dominant_topics.astype(int)
    result["dominant_topic_score"] = dominant_scores.astype(float)
    result["topic_keywords"] = topic_keywords_list
    result["sentiment_payload"] = sentiment_results
    result["sentiment_label"] = [payload.get("overall", {}).get("label", "unknown") for payload in sentiment_results]
    result["sentiment_probability"] = [
        float(payload.get("overall", {}).get("probability", 0.5)) for payload in sentiment_results
    ]
    result["sentiment_confidence"] = [
        float(payload.get("overall", {}).get("confidence", 0.0)) for payload in sentiment_results
    ]
    result["sentiment_distribution"] = [payload.get("distribution", {}) for payload in sentiment_results]
    result["sentiment_positive_share"] = [dist.get("positive", 0.0) for dist in result["sentiment_distribution"]]

    classifications = [
        _classify_high_level_topic(" ".join(keywords) if keywords else text, keywords)
        for keywords, text in zip(topic_keywords_list, clean_texts)
    ]

    result["topic_category"] = [item["key"] for item in classifications]
    result["topic_category_label"] = [item["label"] for item in classifications]
    result["topic_category_confidence"] = [item["confidence"] for item in classifications]
    result["topic_matched_terms"] = [item["matched_terms"] for item in classifications]

    return result


def build_topic_insights(integrated_df: pd.DataFrame) -> pd.DataFrame:
    if "topic_category" not in integrated_df.columns:
        raise ValueError("Integrated DataFrame must contain 'topic_category' column. Did you run attach_topic_sentiment first?")

    working = integrated_df.copy()
    group_records: List[Dict[str, Any]] = []

    for category, group in working.groupby("topic_category"):
        label = CATEGORY_DISPLAY.get(category, category.title())
        doc_count = len(group)
        avg_sentiment = float(group["sentiment_probability"].astype(float).mean()) if doc_count else 0.5
        positive_share = float((group["sentiment_label"].astype(str).str.lower() == "positive").mean()) if doc_count else 0.0
        avg_topic_strength = float(group["dominant_topic_score"].astype(float).mean()) if doc_count else 0.0
        avg_confidence = float(group["topic_category_confidence"].astype(float).mean()) if doc_count else 0.0

        keyword_counter: Counter[str] = Counter()
        keyword_series = group.get("topic_keywords")
        if keyword_series is not None:
            for keywords in keyword_series.tolist():
                if isinstance(keywords, (list, tuple)):
                    keyword_counter.update(str(token) for token in keywords if token)

        matched_term_counter: Counter[str] = Counter()
        matched_series = group.get("topic_matched_terms")
        if matched_series is not None:
            for terms in matched_series.tolist():
                if isinstance(terms, (list, tuple)):
                    matched_term_counter.update(str(token) for token in terms if token)

        top_keywords = ", ".join([token for token, _ in keyword_counter.most_common(10)]) if keyword_counter else ""
        top_matched_terms = ", ".join([token for token, _ in matched_term_counter.most_common(6)]) if matched_term_counter else ""

        text_column = "text" if "text" in group.columns else "clean_text"
        representative_rows = (
            group.sort_values("dominant_topic_score", ascending=False)[text_column].dropna().astype(str).head(3).tolist()
        )
        representative_excerpt = " || ".join(representative_rows)

        group_records.append(
            {
                "category_key": category,
                "label": label,
                "documents": int(doc_count),
                "avg_sentiment_probability": round(avg_sentiment, 4),
                "positive_share": round(positive_share, 4),
                "avg_topic_strength": round(avg_topic_strength, 4),
                "avg_confidence": round(avg_confidence, 4),
                "top_keywords": top_keywords,
                "matched_terms": top_matched_terms,
                "representative_examples": representative_excerpt,
            }
        )

    insights_df = pd.DataFrame(group_records)
    if not insights_df.empty:
        insights_df = insights_df.sort_values(["documents", "avg_topic_strength"], ascending=[False, False]).reset_index(drop=True)

    return insights_df


def get_topics_for_doc(text: str, tfidf, nmf, n_top: int = 3) -> List[Dict[str, Any]]:
    vec = tfidf.transform([text])
    topic_dist = nmf.transform(vec)[0]
    top_idx = np.argsort(topic_dist)[::-1][:n_top]

    feature_names = _feature_names(tfidf)
    keywords: List[List[str]] = []
    if feature_names is not None:
        for topic_id in top_idx:
            comps = nmf.components_[topic_id]
            terms = [feature_names[j] for j in comps.argsort()[-5:][::-1]]
            keywords.append(terms)

    topics: List[Dict[str, Any]] = []
    for rank, topic_id in enumerate(top_idx):
        item: Dict[str, Any] = {"topic_id": int(topic_id), "score": float(topic_dist[topic_id])}
        if keywords:
            item["keywords"] = keywords[rank]
        topics.append(item)

    enriched_topics: List[Dict[str, Any]] = []
    for topic in topics:
        candidate_keywords = topic.get("keywords", [])
        classifier_input = " ".join(candidate_keywords) if candidate_keywords else text
        classification = _classify_high_level_topic(classifier_input, candidate_keywords)
        enriched_topics.append(
            {
                "label": classification["label"],
                "category_key": classification["key"],
                "confidence": classification["confidence"],
                "keywords": candidate_keywords,
                "matched_terms": classification["matched_terms"],
                "score": topic.get("score", 0.0),
                "original_topic_id": topic.get("topic_id"),
            }
        )

    base_classification = _classify_high_level_topic(text)

    aggregated: Dict[str, Dict[str, Any]] = {}
    for key, label in CATEGORY_DISPLAY.items():
        aggregated[key] = {
            "label": label,
            "category_key": key,
            "raw_score": 0.0,
            "confidence": 0.0,
            "keywords": set(),
            "matched_terms": set(),
            "mentions": 0,
        }

    def _ingest(topic: Dict[str, Any]) -> None:
        key = topic.get("category_key", "other")
        if key not in aggregated:
            key = "other"
        bucket = aggregated[key]
        bucket["raw_score"] += max(float(topic.get("score", 0.0)), 0.0)
        bucket["confidence"] = max(bucket["confidence"], float(topic.get("confidence", 0.0)))
        bucket["keywords"].update(topic.get("keywords", []))
        bucket["matched_terms"].update(topic.get("matched_terms", []))
        bucket["mentions"] += 1

    for topic in enriched_topics:
        _ingest(topic)

    if base_classification:
        baseline_topic = {
            "category_key": base_classification.get("key", "other"),
            "score": base_classification.get("confidence", 0.0) + 0.25,
            "confidence": base_classification.get("confidence", 0.0),
            "keywords": base_classification.get("matched_terms", []),
            "matched_terms": base_classification.get("matched_terms", []),
        }
        _ingest(baseline_topic)

    total_score = sum(bucket["raw_score"] for bucket in aggregated.values())
    results: List[Dict[str, Any]] = []

    for key, bucket in aggregated.items():
        if bucket["raw_score"] <= 0 and not bucket["matched_terms"]:
            continue
        share = bucket["raw_score"] / total_score if total_score > 0 else 0.0
        results.append(
            {
                "label": bucket["label"],
                "category_key": key,
                "score": round(bucket["raw_score"], 5),
                "share": round(share, 4),
                "confidence": round(max(bucket["confidence"], share), 4),
                "keywords": sorted(bucket["keywords"])[0:8],
                "matched_terms": sorted(bucket["matched_terms"])[0:8],
                "mentions": bucket["mentions"],
            }
        )

    if not results:
        results.append(
            {
                "label": CATEGORY_DISPLAY[base_classification.get("key", "other")],
                "category_key": base_classification.get("key", "other"),
                "score": round(base_classification.get("confidence", 0.25), 5),
                "share": 1.0,
                "confidence": round(base_classification.get("confidence", 0.5), 4),
                "keywords": base_classification.get("matched_terms", []),
                "matched_terms": base_classification.get("matched_terms", []),
                "mentions": 1,
            }
        )

    results.sort(key=lambda item: (item["score"], item["confidence"]), reverse=True)
    return results


def _extract_keywords(text: str, top_k: int = 15) -> List[Dict[str, Any]]:
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform([text])
    except ValueError:
        tokens = _tokenise_for_topics(text)
        unique_tokens = list(dict.fromkeys(tokens))[:top_k]
        return [{"term": token, "score": 0.3} for token in unique_tokens]
    scores = matrix.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()
    top_indices = scores.argsort()[::-1][:top_k]
    keywords: List[Dict[str, Any]] = []
    for idx in top_indices:
        weight = float(scores[idx])
        term = feature_names[idx]
        if weight <= 0:
            continue
        keywords.append({"term": term, "score": weight})

    if not keywords:
        tokens = _tokenise_for_topics(text)
        unique_tokens = list(dict.fromkeys(tokens))[:top_k]
        keywords = [{"term": token, "score": 0.25} for token in unique_tokens]

    return keywords


def _normalise_sentiment(sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
    sentiment = sentiment_result.copy() if sentiment_result else {}
    label = sentiment.get("label")
    score = sentiment.get("score")

    overall = sentiment.get("overall", {}) if isinstance(sentiment.get("overall"), dict) else {}
    if label is None:
        label = overall.get("label")
    if score is None:
        score = overall.get("confidence")

    if label is not None:
        sentiment.setdefault("label", label)
    if score is not None:
        sentiment.setdefault("score", score)
    return sentiment


def generate_insights(text: str, sentiment_result: Dict[str, Any], tfidf=None, nmf=None) -> Dict[str, Any]:
    extractive = extractive_summary(text, max_sentences=3)
    try:
        abstractive = abstractive_summary(text)
    except Exception:
        abstractive = None

    topics: List[Dict[str, Any]] = []
    if tfidf is not None and nmf is not None:
        topic_text = clean_text(text)
        topics = get_topics_for_doc(topic_text, tfidf, nmf)

    if not topics:
        fallback_topic = _classify_high_level_topic(text)
        category_key = fallback_topic.get("key", "other")
        topics = [
            {
                "label": CATEGORY_DISPLAY.get(category_key, CATEGORY_DISPLAY["other"]),
                "category_key": category_key,
                "confidence": round(fallback_topic.get("confidence", 0.5), 4),
                "score": round(max(fallback_topic.get("confidence", 0.25), 0.25), 5),
                "share": 1.0,
                "keywords": fallback_topic.get("matched_terms", []),
                "matched_terms": fallback_topic.get("matched_terms", []),
                "mentions": 1,
            }
        ]

    primary_topic = topics[0] if topics else None
    keywords_with_scores = _extract_keywords(text)
    keyword_terms = [item["term"] for item in keywords_with_scores]
    sentiment = _normalise_sentiment(sentiment_result)

    label = str(sentiment.get("label", "")).upper()
    score = sentiment.get("score")

    suggestions: List[str] = []
    if label == "NEGATIVE" or (isinstance(score, (int, float)) and score < 0.6):
        suggestions.append("Investigate causes of negative sentiment, prioritize frequently mentioned terms.")
    else:
        suggestions.append("Leverage positive trends; identify frequently mentioned strengths for promotion.")

    return {
        "extractive_summary": extractive,
        "abstractive_summary": abstractive,
        "topics": topics,
        "primary_topic": primary_topic,
        "sentiment": sentiment,
        "suggestions": suggestions,
        "keyword_cloud": keyword_terms,
        "keyword_cloud_weighted": keywords_with_scores,
    }