import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline

nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

def vader_sentiment(text: str) -> dict:
    """Rule-based sentiment with VADER"""
    scores = sia.polarity_scores(text)
    if scores['compound'] >= 0.05:
        label = 'positive'
    elif scores['compound'] <= -0.05:
        label = 'negative'
    else:
        label = 'neutral'
    return {**scores, 'label': label}

def transformer_sentiment(model_name: str = 'distilbert-base-uncased-finetuned-sst-2-english'):
    """Transformer-based sentiment pipeline"""
    return pipeline('sentiment-analysis', model=model_name)
