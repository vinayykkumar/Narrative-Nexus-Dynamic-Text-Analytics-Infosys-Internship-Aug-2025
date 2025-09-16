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
    message: Optional[str] = None
