import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `src.*` imports work when run from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.preprocessing import load_csvs, preprocess_series

DATA_DIR = "data"
DATASETS = [
    os.path.join(DATA_DIR, "bbc-text.csv"),
    os.path.join(DATA_DIR, "imdb-dataset.csv"),
    os.path.join(DATA_DIR, "cnn_dailymail.csv"),
]

def main():
    print("[1/5] Preprocessing: loading datasets...")
    df = load_csvs(DATASETS)
    print(f" - Loaded {len(df)} rows from {len(DATASETS)} files.")
    print("[1/5] Cleaning + token reducing (fast porter)...")
    # Use fast Porter stemming by default for speed; set PREPROCESS_METHOD=spacy to switch
    df['clean_text'] = preprocess_series(df['text'], method=os.getenv('PREPROCESS_METHOD', 'porter'))
    out_path = os.path.join(DATA_DIR, "preprocessed_all.csv")
    df.to_csv(out_path, index=False)
    print(f"[1/5] Saved preprocessed dataset -> {out_path}")

if __name__ == "__main__":
    main()
