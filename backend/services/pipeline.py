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
    }
