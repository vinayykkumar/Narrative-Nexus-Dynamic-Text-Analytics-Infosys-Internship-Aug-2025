from typing import Optional, Any
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    text_column: Optional[str] = "Airport Service Freeform Feedback"
    n_topics: Optional[int] = 5
    max_df: Optional[float] = 0.95
    min_df: Optional[int] = 2

class AnalyzeResponse(BaseModel):
    wordcloud_paths: list[str]
    topic_distribution_pie: str
    sentiment_distribution_bar: str
    topic_sentiment_bar: str
    topic_sentiment_pie: str
    enriched_csv: str
    topic_modeling_results: Optional[dict[str, Any]] = None
    sentiment_results: Optional[dict[str, Any]] = None
    dataset_summary: Optional[dict[str, Any]] = None
    report_html: Optional[str] = None
    message: Optional[str] = None

class SummarizeRequest(BaseModel):
    text: str
    method: Optional[str] = "abstractive"  # abstractive | tfidf | frequency
    max_sentences: Optional[int] = 3
    max_tokens: Optional[int] = 128
    model_name: Optional[str] = "sshleifer/distilbart-cnn-12-6"

class SummarizeResponse(BaseModel):
    original_text: str
    summary: str
    key_sentences: list[str]
    sentence_scores: dict[str, float]
    method_used: str
    compression_ratio: float
    word_count_original: int
    word_count_summary: int
