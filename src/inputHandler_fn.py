import pandas as pd
from io import StringIO
from typing import Dict, Any

TEXT_COL_NAME_HINTS = {"text", "content", "body", "summary", "description", "headline", "title"}

def _csv_to_text(df: pd.DataFrame, max_chars: int = 150_000) -> str:
    """Flatten likely text columns to a single string (capped)."""
    lower_cols = {c.lower(): c for c in df.columns}
    preferred = [lower_cols[c] for c in lower_cols.keys() & TEXT_COL_NAME_HINTS]
    use_cols = preferred if preferred else [c for c in df.columns if df[c].dtype == "object"]
    if not use_cols:
        use_cols = list(df.columns[:3])

    pieces = []
    for col in use_cols:
        pieces.append(" ".join(df[col].astype(str).tolist()))
    text = " ".join(pieces)
    return text[:max_chars] if len(text) > max_chars else text

def _read_txt(file) -> str:
    try:
        file.seek(0)
    except Exception:
        pass
    data = file.read()
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="ignore")
    return str(data)

def _read_csv_preview(file, nrows: int = 800, encodings=("utf-8", "latin1")) -> pd.DataFrame:
    last_err = None
    for enc in encodings:
        try:
            try:
                file.seek(0)
            except Exception:
                pass
            return pd.read_csv(file, nrows=nrows, dtype=str, encoding=enc, low_memory=False)
        except Exception as e:
            last_err = e
    if last_err:
        raise last_err
    raise ValueError("Could not read CSV.")

def read_file(uploaded_file, *, csv_rows_preview: int = 800, csv_char_cap: int = 150_000) -> Dict[str, Any]:
    """
    Reads .txt, .csv, .docx safely and returns:
      {
        "text": str,
        "df_preview": pd.DataFrame|None,
        "meta": {"source_type": "txt|csv|docx"}
      }
    """
    name = (uploaded_file.name or "").lower()

    if name.endswith(".txt"):
        return {"text": _read_txt(uploaded_file), "df_preview": None, "meta": {"source_type": "txt"}}

    if name.endswith(".csv"):
        # Read small preview and flatten to text (keeps memory small)
        df = _read_csv_preview(uploaded_file, nrows=csv_rows_preview)
        text = _csv_to_text(df, max_chars=csv_char_cap)
        return {"text": text, "df_preview": df, "meta": {"source_type": "csv"}}

    if name.endswith(".docx"):
        # Lazy import so users without docx still can run for txt/csv
        try:
            from docx import Document
            try:
                uploaded_file.seek(0)
            except Exception:
                pass
            doc = Document(uploaded_file)
            text = "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            raise RuntimeError("Install `python-docx` for .docx support: pip install python-docx")
        return {"text": text, "df_preview": None, "meta": {"source_type": "docx"}}

    raise ValueError("Unsupported file format. Please upload .txt, .csv, or .docx")
