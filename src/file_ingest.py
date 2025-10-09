from __future__ import annotations
from pathlib import Path
import io

def _try_pdf_bytes(b: bytes) -> str:
    try:
        from pdfminer.high_level import extract_text
        with io.BytesIO(b) as bio:
            return extract_text(bio) or ""
    except Exception:
        return ""

def _try_docx_bytes(b: bytes) -> str:
    try:
        import docx  # python-docx
        with io.BytesIO(b) as bio:
            doc = docx.Document(bio)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip()) or ""
    except Exception:
        return ""

def _try_csv_bytes(b: bytes) -> str:
    try:
        import pandas as pd
        with io.BytesIO(b) as bio:
            df = pd.read_csv(bio, encoding_errors="ignore")
        text_cols = [c for c in df.columns if "text" in str(c).lower() or "content" in str(c).lower()]
        if text_cols:
            series = df[text_cols[0]].dropna().astype(str)
            return "\n".join(series.tolist())[:500000]
        return "\n".join(df.astype(str).fillna("").agg(" ".join, axis=1).tolist())[:500000]
    except Exception:
        return ""

def _try_txt_bytes(b: bytes) -> str:
    try:
        return b.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def sniff_text_from_upload(filename: str, blob: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        txt = _try_pdf_bytes(blob)
        if txt.strip(): return txt
    if name.endswith(".docx"):
        txt = _try_docx_bytes(blob)
        if txt.strip(): return txt
    if name.endswith(".csv"):
        txt = _try_csv_bytes(blob)
        if txt.strip(): return txt
    return _try_txt_bytes(blob)

