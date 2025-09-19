# src/sentiment.py
from transformers import pipeline
import joblib
import os

MODEL_DIR = "../models"

def get_sentiment_pipeline(model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
    sentiment = pipeline("sentiment-analysis", model=model_name, device=-1)  # device=-1 for CPU
    return sentiment

def analyze_texts(sent_pipeline, texts: list, batch_size:int=16):
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        res = sent_pipeline(batch)
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
