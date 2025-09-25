import os
import sys
from pathlib import Path
import pandas as pd

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

# Ensure project root is on sys.path so `src.*` imports work when run from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sentiment import get_sentiment_pipeline, analyze_texts

DATA_DIR = "data"

def main():
    print("[4/5] Sentiment test: loading preprocessed data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "preprocessed_all.csv"))
    texts = df['clean_text'].astype(str).head(5).tolist()
    print(f" - Running on {len(texts)} samples")
    sp = get_sentiment_pipeline()
    out = analyze_texts(sp, texts)
    for i, (t, r) in enumerate(zip(texts, out), 1):
        print(f"[{i}] {t[:80]}...")
        print("    ->", r)

if __name__ == "__main__":
    main()
