"""
Improved Summarization for SmartInsights

- Extractive: TextRank (sumy)
- Abstractive: HuggingFace transformers (pipeline "summarization")
- NEW Hybrid: extractive first → single abstractive pass on the condensed text
- Abstractive uses CHUNKED summarization and returns all partial summaries joined.
"""

import argparse
import json
from pathlib import Path
import pandas as pd

# Try import sumy for extractive TextRank
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.text_rank import TextRankSummarizer
    _HAS_SUMY = True
except Exception:
    _HAS_SUMY = False

# Try transformers for abstractive summarization
try:
    from transformers import pipeline
    _HAS_TRANSFORMERS = True
except Exception:
    _HAS_TRANSFORMERS = False

_single_summarizer = None


def _extractive_top_sentences(text: str, k: int = 10) -> str:
    """Return top-k sentences using TextRank (or a lead fallback)."""
    if not text.strip():
        return ""
    if _HAS_SUMY:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = TextRankSummarizer()
        sentences = summarizer(parser.document, k)
        return " ".join(str(s) for s in sentences)
    # fallback: lead-3/5 sentences
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    return ". ".join(sentences[: max(3, min(k, 5))]).strip()


def summarize_text(
    text: str,
    mode: str = "abstractive",
    model_name: str = "sshleifer/distilbart-cnn-12-6",
    chunk_size: int = 400,      # words per chunk
    max_length: int = 150,      # summary length per chunk
    min_length: int = 60        # minimum per chunk
) -> str:
    """
    Summarize long text.

    Modes:
      - "extractive": TextRank (sumy) or fallback to lead-3 sentences
      - "abstractive": transformers pipeline on chunks (joined)
      - "hybrid": extractive top sentences → single abstractive pass on that condensed text
    """
    global _single_summarizer
    if not text.strip():
        return ""

    # ------------------------------
    # Extractive only
    # ------------------------------
    if mode == "extractive" or (mode != "abstractive" and not _HAS_TRANSFORMERS):
        return _extractive_top_sentences(text, k=10)

    # ------------------------------
    # Hybrid: extract then abstract
    # ------------------------------
    if mode == "hybrid":
        try:
            condensed = _extractive_top_sentences(text, k=10)
            if not condensed.strip():
                condensed = text[:1200]
            if _single_summarizer is None:
                _single_summarizer = pipeline("summarization", model=model_name)
            res = _single_summarizer(
                condensed,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            return res[0]["summary_text"]
        except Exception as e:
            print("Hybrid summarization failed, fallback to extractive:", e)
            return _extractive_top_sentences(text, k=10)

    # ------------------------------
    # Abstractive (chunked)
    # ------------------------------
    try:
        if _single_summarizer is None:
            _single_summarizer = pipeline("summarization", model=model_name)

        words = text.split()
        chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

        chunk_summaries = []
        for chunk in chunks:
            try:
                res = _single_summarizer(
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                chunk_summaries.append(res[0]["summary_text"])
            except Exception as e:
                print("Chunk summarization failed:", e)

        if not chunk_summaries:
            # fallback to extractive if abstractive fails entirely
            return _extractive_top_sentences(text, k=10)

        return " ".join(chunk_summaries)

    except Exception as e:
        print("❌ Abstractive summarization failed:", e)
        return _extractive_top_sentences(text, k=10)


# ============================================================
# Summarize per-topic (used in training pipeline)
# ============================================================
def summarize_by_topic(df, mode="extractive", per_topic=5, sentences=3,
                       abstractive_model="sshleifer/distilbart-cnn-12-6",
                       max_length=150, min_length=60):
    """
    df: DataFrame with columns 'dominant_topic' and 'doc' (text).
    Returns dict: {topic_idx: summary_text}
    """
    summaries = {}
    for t, group in df.groupby("dominant_topic"):
        docs = group["doc"].astype(str).tolist()[:per_topic]
        if not docs:
            summaries[int(t)] = ""
            continue
        try:
            text = " ".join(docs)
            s = summarize_text(
                text,
                mode=mode,
                model_name=abstractive_model,
                max_length=max_length,
                min_length=min_length,
            )
        except Exception as e:
            s = f"[ERROR generating summary: {e}]"
        summaries[int(t)] = s
    return summaries


def save_summaries(summaries: dict, out_dir: Path, mode: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"summaries_{mode}.json"
    with open(json_path, "w", encoding="utf8") as fw:
        json.dump(summaries, fw, ensure_ascii=False, indent=2)
    # also save per-topic text files
    for t, s in summaries.items():
        txt = out_dir / f"topic_{t}_{mode}.txt"
        txt.write_text(s, encoding="utf8")
    return json_path


# ============================================================
# CLI entry point
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="doc_topics CSV (must contain 'dominant_topic' and 'doc' columns)")
    parser.add_argument("--out", required=True, help="output folder for summaries")
    parser.add_argument("--mode", choices=["extractive", "abstractive", "hybrid"], default="extractive")
    parser.add_argument("--per-topic", type=int, default=5, help="number of docs per topic to include in the summary")
    parser.add_argument("--sentences", type=int, default=3, help="(extractive legacy) number of sentences in summary")
    parser.add_argument("--abstractive-model", type=str, default="sshleifer/distilbart-cnn-12-6", help="HuggingFace model name for abstractive summarization")
    parser.add_argument("--max-length", type=int, default=150, help="abstractive/hybrid: max tokens per summary")
    parser.add_argument("--min-length", type=int, default=60, help="abstractive/hybrid: min tokens per summary")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if "dominant_topic" not in df.columns or "doc" not in df.columns:
        raise ValueError("Input CSV must contain 'dominant_topic' and 'doc' columns. If you have a 'doc_index' and text column name is different, rename it to 'doc' first.")

    summaries = summarize_by_topic(
        df,
        mode=args.mode,
        per_topic=args.per_topic,
        sentences=args.sentences,
        abstractive_model=args.abstractive_model,
        max_length=args.max_length,
        min_length=args.min_length,
    )

    out_dir = Path(args.out)
    saved = save_summaries(summaries, out_dir, args.mode)
    print("Saved summaries JSON ->", saved)
    print("Saved per-topic txt files in", out_dir)


if __name__ == "__main__":
    main()
