import os
import sys
from pathlib import Path
import pandas as pd

# Prevent TF probing for transformers pipelines
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.summarization import extractive_summary, abstractive_summary

DATA_DIR = "data"

def main():
    print("[3/5] Summarization test: loading preprocessed data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "preprocessed_all.csv"))
    sample = df['clean_text'].astype(str).iloc[0]
    print(" - Sample text:", sample[:220], "...")
    print("\n[3/5] Extractive summary:")
    print(extractive_summary(sample))
    print("\n[3/5] Abstractive summary:")
    try:
        print(abstractive_summary(sample))
    except Exception as e:
        print("[WARN] Abstractive summarization unavailable:", e)

if __name__ == "__main__":
    main()
