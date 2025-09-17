import shutil
from pathlib import Path
from typing import Optional
import sys
import os
import pandas as pd

# Defer heavy import until needed; keep root on path for resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def _get_run_pipeline():
    from topic_modeling_sentiment import run_pipeline  # local import to avoid startup failures
    return run_pipeline


def _prepare_excel_input(file_path: Path, text_column: Optional[str]) -> tuple[Path, str]:
    """Normalize various input formats to an Excel file path and decide text column.

    Supports: .xlsx/.xls (pass-through), .csv, .txt
    For .csv: if text_column not provided or missing, picks the first object/string column.
    For .txt: creates a single-row DataFrame with column 'text'.
    """
    suffix = file_path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        # Use as-is; default text column might be provided by client
        return file_path, text_column or "Airport Service Freeform Feedback"

    out_excel = file_path.with_suffix(".converted.xlsx")

    if suffix == ".csv":
        df = pd.read_csv(file_path)
        chosen_col = text_column
        if not chosen_col or chosen_col not in df.columns:
            # pick first object dtype column
            obj_cols = [c for c in df.columns if df[c].dtype == "object"]
            if obj_cols:
                chosen_col = obj_cols[0]
            else:
                # fallback: first column
                chosen_col = str(df.columns[0])
        df.to_excel(out_excel, index=False)
        return out_excel, chosen_col

    if suffix == ".txt":
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        df = pd.DataFrame({"text": [content]})
        df.to_excel(out_excel, index=False)
        return out_excel, "text"

    raise ValueError(f"Unsupported file format: {suffix}. Please upload .xlsx, .xls, .csv, or .txt")

def run_analysis(
    file_path: Path,
    text_column: str = "Airport Service Freeform Feedback",
    n_topics: int = 5,
    max_df: float = 0.95,
    min_df: int = 2,
    output_dir: Optional[Path] = None,
    show_plots: bool = False,
    fast_mode: bool = False,
):
    output_dir = Path(output_dir) if output_dir else Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    run_pipeline = _get_run_pipeline()

    # Normalize input to Excel for compatibility with existing pipeline
    excel_input, chosen_text_col = _prepare_excel_input(file_path, text_column)

    structured = run_pipeline(
        excel_path=excel_input,
        text_column=chosen_text_col,
        n_topics=n_topics,
        max_df=max_df,
        min_df=min_df,
        output_dir=output_dir,
        show_plots=show_plots,
    )
    # Collect artifact paths
    wc_dir = output_dir / "wordclouds"
    wordcloud_paths = [str(p) for p in sorted(wc_dir.glob("*.png"))]
    topic_distribution_pie = str(output_dir / "topic_distribution_pie.png")
    sentiment_distribution_bar = str(output_dir / "sentiment_distribution_bar.png")
    topic_sentiment_bar = str(output_dir / "topic_sentiment_bar.png")
    topic_sentiment_pie = str(output_dir / "topic_sentiment_pie.png")
    enriched_csv = str(output_dir / "enriched_topic_sentiment.csv")

    # --- Per-topic abstractive summaries (with graceful fallback) ---
    dataset_summary: dict | None = None
    try:
        # Load enriched CSV to get dominant_topic and original text
        df_enriched = pd.read_csv(enriched_csv)
        topics_struct = structured.get("topic_modeling_results") if isinstance(structured, dict) else None
        if isinstance(topics_struct, dict) and isinstance(topics_struct.get("topics"), list):
            # Local import to avoid heavy startup cost unless needed
            from .summarization import summarize_text

            # Build a map from topic_id to combined text
            topic_texts: dict[int, str] = {}
            if "dominant_topic" in df_enriched.columns and chosen_text_col in df_enriched.columns:
                for topic_id, group in df_enriched.groupby("dominant_topic"):
                    texts = group[chosen_text_col].dropna().astype(str).tolist()
                    combined = " ".join(texts)
                    topic_texts[int(topic_id)] = combined

            # Attach summaries
            for topic in topics_struct["topics"]:
                try:
                    tid = int(topic.get("topic_id"))
                except Exception:
                    continue
                combined_text = topic_texts.get(tid, "")
                if not combined_text:
                    topic["summary"] = ""
                    topic["summary_method"] = "none"
                    continue
                try:
                    method = "frequency" if fast_mode else "abstractive"
                    summary, _key_sents, _scores, used = summarize_text(
                        combined_text,
                        method=method,
                        max_sentences=3,
                        max_tokens=128,
                    )
                except Exception:
                    # Any unexpected failure: safe fallback
                    summary = combined_text[:600] + ("..." if len(combined_text) > 600 else "")
                    used = "fallback:truncated"
                topic["summary"] = summary
                topic["summary_method"] = used

            # Compute overall dataset summary using all texts combined
            try:
                all_texts = df_enriched[chosen_text_col].dropna().astype(str).tolist()
                combined_all = " ".join(all_texts)
                if combined_all:
                    # Always use extractive frequency for dataset summary (fast and dependency-light)
                    ds_summary_text, ds_key, ds_scores, ds_used = summarize_text(
                        combined_all,
                        method="frequency",
                        max_sentences=5,
                        max_tokens=160,
                    )
                    dataset_summary = {
                        "summary": ds_summary_text,
                        "method_used": ds_used,
                        "key_sentences": ds_key,
                        "sentence_scores": ds_scores,
                    }
            except Exception:
                pass

            # Persist updated structured results for reference
            try:
                import json
                with (output_dir / "structured_results.json").open("w", encoding="utf-8") as f:
                    json.dump({
                        "topic_modeling_results": topics_struct,
                        "sentiment_results": structured.get("sentiment_results") if isinstance(structured, dict) else None,
                        "dataset_summary": dataset_summary,
                    }, f, indent=2)
            except Exception:
                pass
    except Exception:
        # Non-fatal; if anything goes wrong we just skip per-topic summaries
        pass

    return {
        "wordcloud_paths": wordcloud_paths,
        "topic_distribution_pie": topic_distribution_pie,
        "sentiment_distribution_bar": sentiment_distribution_bar,
        "topic_sentiment_bar": topic_sentiment_bar,
        "topic_sentiment_pie": topic_sentiment_pie,
        "enriched_csv": enriched_csv,
        # Structured results returned by pipeline
        "topic_modeling_results": structured.get("topic_modeling_results") if isinstance(structured, dict) else None,
        "sentiment_results": structured.get("sentiment_results") if isinstance(structured, dict) else None,
        "dataset_summary": dataset_summary,
    }
