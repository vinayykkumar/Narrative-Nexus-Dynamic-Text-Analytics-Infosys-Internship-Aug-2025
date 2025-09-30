"""Insight generation module combining summarisation, topics, and sentiment."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import re

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from src.summarization import extractive_summary, abstractive_summary
from src.preprocessing import clean_text
from src.sentiment import SentimentInferenceModels, analyze_sentiment_text, rule_based_sentiment
from src.sentiment import MAX_LEN as SENTIMENT_MAX_LEN


MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


@dataclass(frozen=True)
class TopicModels:
    tfidf: TfidfVectorizer
    nmf: NMF
    lda: Optional[LatentDirichletAllocation]
    count_vectorizer: Optional[CountVectorizer]


CATEGORY_KEYWORDS: Dict[str, set[str]] = {
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
    "education": {
        "education",
        "school",
        "teacher",
        "student",
        "university",
        "college",
        "curriculum",
        "classroom",
        "learning",
        "study",
        "exam",
        "assessment",
        "lecture",
        "academy",
        "scholar",
        "training",
    },
    "environment": {
        "environment",
        "climate",
        "forest",
        "wildlife",
        "sustainability",
        "ecosystem",
        "biodiversity",
        "pollution",
        "carbon",
        "emission",
        "recycle",
        "conservation",
        "renewable",
        "green",
        "habitat",
    },
    "health": {
        "health",
        "medical",
        "medicine",
        "doctor",
        "nurse",
        "hospital",
        "wellness",
        "fitness",
        "therapy",
        "disease",
        "infection",
        "prevention",
        "exercise",
        "nutrition",
        "mental",
        "care",
    },
    "politics": {
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
        "season",
        "netflix",
        "hulu",
        "disney",
        "prime",
        "stream",
        "streaming",
        "tv",
        "television",
        "premiere",
        "trailer",
        "cast",
        "director",
        "anime",
        "binge",
        "binging",
    },
    "sports": {
        "sport",
        "sports",
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
        "astronomy",
        "innovation",
        "discovery",
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
}

CATEGORY_GROUP_MAPPING: Dict[str, str] = {
    "politics": "politics",
    "technology": "technology",
    "education": "education",
    "environment": "environment",
    "health": "health",
    "sports": "sports",
    "business": "business",
    "entertainment": "entertainment",
    "science": "science",
    "world": "world",
}

CATEGORY_DISPLAY: Dict[str, str] = {
    "politics": "Politics",
    "technology": "Technology",
    "education": "Education",
    "environment": "Environment",
    "health": "Health",
    "sports": "Sports",
    "business": "Business",
    "entertainment": "Entertainment",
    "science": "Science",
    "world": "World",
    "other": "Other",
}


def load_models(model_dir: Path | str = MODEL_DIR) -> TopicModels:
    """Load persisted topic models (TF-IDF/NMF/LDA) from disk."""

    model_path = Path(model_dir)
    tfidf = joblib.load(model_path / "tfidf_vectorizer.pkl")
    nmf = joblib.load(model_path / "nmf_model.pkl")

    lda_path = model_path / "lda_model.pkl"
    cv_path = model_path / "count_vectorizer.pkl"

    lda = joblib.load(lda_path) if lda_path.exists() else None
    count_vectorizer = joblib.load(cv_path) if cv_path.exists() else None

    return TopicModels(tfidf=tfidf, nmf=nmf, lda=lda, count_vectorizer=count_vectorizer)


def _coerce_topic_models(models: Any, nmf: Optional[Any] = None) -> TopicModels:
    if isinstance(models, TopicModels):
        return models
    if isinstance(models, tuple) and len(models) >= 2:
        tfidf, nmf_model = models[0], models[1]
        return TopicModels(tfidf=tfidf, nmf=nmf_model, lda=None, count_vectorizer=None)
    if nmf is not None:
        return TopicModels(tfidf=models, nmf=nmf, lda=None, count_vectorizer=None)
    raise ValueError("Topic models must be provided as TopicModels or (tfidf, nmf) tuple.")


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
    distribution = rule.get("distribution") or {
        "positive": max(0.0, min(1.0, 0.5 + rule.get("score", 0.0) / 2.0)),
        "negative": max(0.0, min(1.0, 0.5 - rule.get("score", 0.0) / 2.0)),
        "neutral": 0.0,
    }
    total = sum(distribution.values()) or 1.0
    normalised = {key: float(value) / total for key, value in distribution.items()}
    dominant_label = str(rule.get("label", "neutral")).lower()
    probability = normalised.get(dominant_label, max(normalised.values(), default=0.33))
    confidence = probability

    return {
        "overall": {
            "label": dominant_label,
            "confidence": confidence,
            "probability": probability,
            "score": rule.get("score", 0.0),
        },
        "rule_based": rule,
        "ml": None,
        "dl": None,
        "transformer": None,
        "distribution": normalised,
        "models": {"rule_based": rule},
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

        sentiment_counts = Counter(str(label).lower() for label in group.get("sentiment_label", []) if label)
        dominant_sentiment = "neutral"
        if sentiment_counts:
            dominant_sentiment = sentiment_counts.most_common(1)[0][0]

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
                "dominant_sentiment": dominant_sentiment.capitalize(),
                "sample_excerpt": representative_rows[0] if representative_rows else "",
            }
        )

    insights_df = pd.DataFrame(group_records)
    if not insights_df.empty:
        insights_df = insights_df.sort_values(["documents", "avg_topic_strength"], ascending=[False, False]).reset_index(drop=True)

    return insights_df


def get_topics_for_doc(text: str, models: Any, nmf: Optional[Any] = None, n_top: int = 6) -> Dict[str, Any]:
    topic_models = _coerce_topic_models(models, nmf)
    tfidf = topic_models.tfidf
    nmf_model = topic_models.nmf
    lda_model = topic_models.lda
    count_vectorizer = topic_models.count_vectorizer

    vec = tfidf.transform([text])
    topic_dist = nmf_model.transform(vec)[0]
    if topic_dist.ndim != 1:
        topic_dist = topic_dist.flatten()

    n_top = max(1, min(n_top, len(topic_dist)))
    top_idx = np.argsort(topic_dist)[::-1][:n_top]
    top_activations = float(np.sum(topic_dist[top_idx])) or 1.0

    feature_names = _feature_names(tfidf)
    keywords: List[List[str]] = []
    if feature_names is not None:
        for topic_id in top_idx:
            comps = nmf_model.components_[topic_id]
            terms = [feature_names[j] for j in comps.argsort()[-8:][::-1]]
            keywords.append(terms)

    nmf_topics: List[Dict[str, Any]] = []
    for rank, topic_id in enumerate(top_idx):
        activation = float(topic_dist[topic_id])
        share = activation / top_activations if top_activations > 0 else 0.0
        item: Dict[str, Any] = {
            "topic_id": int(topic_id),
            "rank": rank + 1,
            "score": activation,
            "share": share,
            "source": "nmf",
        }
        if keywords:
            item["keywords"] = keywords[rank]
        nmf_topics.append(item)

    lda_topics: List[Dict[str, Any]] = []
    if lda_model is not None and count_vectorizer is not None:
        lda_vec = count_vectorizer.transform([text])
        lda_dist = lda_model.transform(lda_vec)[0]
        if lda_dist.ndim != 1:
            lda_dist = lda_dist.flatten()
        lda_top_idx = np.argsort(lda_dist)[::-1][:n_top]
        for rank, topic_id in enumerate(lda_top_idx):
            score = float(lda_dist[topic_id])
            lda_item: Dict[str, Any] = {
                "topic_id": int(topic_id),
                "rank": rank + 1,
                "score": score,
                "share": score,
                "source": "lda",
                "keywords": _top_words_for_topic(lda_model, count_vectorizer, int(topic_id), top_n=8),
            }
            lda_topics.append(lda_item)

    enriched_topics: List[Dict[str, Any]] = []
    for topic in nmf_topics + lda_topics:
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
                "share": round(float(topic.get("share", 0.0)), 4),
                "original_topic_id": topic.get("topic_id"),
                "rank": topic.get("rank"),
                "source": topic.get("source", "nmf"),
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
        contribution = max(float(topic.get("score", 0.0)), 0.0)
        source = topic.get("source", "nmf")
        if source == "lda":
            contribution *= 0.85
        bucket["raw_score"] += contribution
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
    summary_results: List[Dict[str, Any]] = []

    for key, bucket in aggregated.items():
        if bucket["raw_score"] <= 0 and not bucket["matched_terms"]:
            continue
        share = bucket["raw_score"] / total_score if total_score > 0 else 0.0
        summary_results.append(
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

    if not summary_results:
        summary_results.append(
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

    summary_results.sort(key=lambda item: (item["score"], item["confidence"]), reverse=True)

    bundle: Dict[str, Any] = {
        "summary": summary_results,
        "primary": summary_results[0] if summary_results else None,
        "detailed": enriched_topics,
        "model_topics": {
            "nmf": nmf_topics,
            "lda": lda_topics,
        },
    }

    return bundle


_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    sentences = [segment.strip() for segment in _SENTENCE_SPLIT_PATTERN.split(text) if segment.strip()]
    if not sentences:
        sentences = [text.strip()]
    return sentences


def _select_snippet(sentences: Sequence[str], keywords: Sequence[str]) -> str:
    lowered_keywords = [kw.lower() for kw in keywords if kw]
    if not sentences:
        return ""
    if not lowered_keywords:
        return sentences[0]
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in lowered_keywords):
            return sentence
    return sentences[0]


def _topic_narratives(
    text: str,
    topics: Sequence[Dict[str, Any]],
    sentiment_models: Optional[SentimentInferenceModels],
) -> List[Dict[str, Any]]:
    sentences = _split_sentences(text)
    narratives: List[Dict[str, Any]] = []
    for index, topic in enumerate(topics, start=1):
        keywords = topic.get("matched_terms") or topic.get("keywords") or []
        snippet = _select_snippet(sentences, keywords)
        if sentiment_models is not None and snippet:
            snippet_sentiment = analyze_sentiment_text(snippet, sentiment_models)
        elif snippet:
            snippet_sentiment = _fallback_sentiment_result(snippet)
        else:
            snippet_sentiment = {
                "overall": {"label": "neutral", "confidence": 0.25, "probability": 0.5}
            }

        overall = snippet_sentiment.get("overall", {})
        sentiment_label = str(overall.get("label", "neutral")).capitalize()
        narratives.append(
            {
                "index": index,
                "title": topic.get("label", f"Topic {index}"),
                "headline": f"{topic.get('label', f'Topic {index}')} ({sentiment_label})",
                "sentiment_label": sentiment_label,
                "sentiment_details": snippet_sentiment,
                "snippet": snippet,
                "keywords": topic.get("keywords", []),
                "matched_terms": topic.get("matched_terms", []),
                "category_key": topic.get("category_key"),
                "score": topic.get("score"),
            }
        )

    return narratives


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


def generate_insights(
    text: str,
    sentiment_result: Dict[str, Any],
    topic_models: Any = None,
    nmf: Optional[Any] = None,
    sentiment_models: Optional[SentimentInferenceModels] = None,
) -> Dict[str, Any]:
    extractive = extractive_summary(text, max_sentences=3)
    try:
        abstractive = abstractive_summary(text)
    except Exception:
        abstractive = None

    topic_bundle: Dict[str, Any] = {"summary": [], "detailed": [], "primary": None}
    resolved_models: Optional[TopicModels] = None
    if topic_models is not None:
        try:
            resolved_models = _coerce_topic_models(topic_models, nmf)
        except ValueError:
            resolved_models = None
    if resolved_models is not None:
        topic_text = clean_text(text)
        topic_bundle = get_topics_for_doc(topic_text, resolved_models)

    topics: List[Dict[str, Any]] = list(topic_bundle.get("summary", [])) if topic_bundle else []
    detailed_topics: List[Dict[str, Any]] = list(topic_bundle.get("detailed", [])) if topic_bundle else []

    if not topics:
        fallback_topic = _classify_high_level_topic(text)
        category_key = fallback_topic.get("key", "other")
        fallback_entry = {
            "label": CATEGORY_DISPLAY.get(category_key, CATEGORY_DISPLAY["other"]),
            "category_key": category_key,
            "confidence": round(fallback_topic.get("confidence", 0.5), 4),
            "score": round(max(fallback_topic.get("confidence", 0.25), 0.25), 5),
            "share": 1.0,
            "keywords": fallback_topic.get("matched_terms", []),
            "matched_terms": fallback_topic.get("matched_terms", []),
            "mentions": 1,
        }
        topics = [fallback_entry]
        detailed_topics = [fallback_entry]
        topic_bundle = {"summary": topics, "detailed": detailed_topics, "primary": fallback_entry}

    primary_topic = topic_bundle.get("primary") or (topics[0] if topics else None)
    if primary_topic and len(topics) > 1:
        topics = [primary_topic] + [topic for idx, topic in enumerate(topics) if topic is not primary_topic and idx != 0]
    if not detailed_topics:
        detailed_topics = topics
    keywords_with_scores = _extract_keywords(text)
    keyword_terms = [item["term"] for item in keywords_with_scores]
    sentiment = _normalise_sentiment(sentiment_result)

    narratives = _topic_narratives(text, topics, sentiment_models)
    narratives = narratives[:6]

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
        "topic_details": detailed_topics,
        "topic_narratives": narratives,
        "sentiment": sentiment,
        "suggestions": suggestions,
        "keyword_cloud": keyword_terms,
        "keyword_cloud_weighted": keywords_with_scores,
        "topic_models_available": resolved_models is not None,
    }
