# src/sentiment.py
import os
import warnings

# Prefer PyTorch; prevent TF import attempts that require keras
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

try:
    from transformers import pipeline
except Exception as e:
    pipeline = None
    warnings.warn(f"transformers unavailable for sentiment: {e}")

_sentiment_pipeline = None
MODEL_DIR = "../models"

def get_sentiment_pipeline(model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
    global _sentiment_pipeline
    if _sentiment_pipeline is not None:
        return _sentiment_pipeline
    if pipeline is None:
        raise RuntimeError("transformers is not available; cannot create sentiment pipeline")
    try:
        _sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, device=-1, framework="pt")
        return _sentiment_pipeline
    except Exception as e:
        raise RuntimeError(f"Failed to init sentiment pipeline: {e}")

def analyze_texts(sent_pipeline, texts: list, batch_size: int = 16, max_length: int = 256):
    """Run sentiment with safe truncation for speed and to avoid max length errors."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # Let the tokenizer handle truncation/padding efficiently
        res = sent_pipeline(batch, truncation=True, padding=True, max_length=max_length)
        results.extend(res)
    return results

if __name__ == "__main__":
    from preprocessing import load_csvs, preprocess_series
    paths = ["../data/imdb-dataset.csv"]
    df = load_csvs(paths)
    df['clean_text'] = preprocess_series(df['text'])
    sentiment = get_sentiment_pipeline()
    out = analyze_texts(sentiment, df['clean_text'].tolist()[:200])
    print(out[:5])