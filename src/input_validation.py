# src/input_validation.py
"""
Basic validation & sanitization utilities for uploaded dataset files.

Functions:
- validate_extension(filename) -> bool
- detect_encoding(file_path) -> str
- basic_schema_check(df, required_cols=None) -> (bool, message)
- sanitize_dataframe(df, text_columns=None) -> df
- save_uploaded_file(fileobj, filename) -> Path (saves bytes)
"""

from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import chardet

from .utils import RAW_DIR, secure_filename

ALLOWED_EXT = {".csv", ".json", ".txt"}
MAX_SIZE_MB = 200  # unused here but available for checks

def validate_extension(filename: str) -> bool:
    """Return True if filename has allowed extension."""
    return Path(filename).suffix.lower() in ALLOWED_EXT

def detect_encoding(file_path: Path) -> str:
    """Detect encoding of a file using chardet (reads first 100k bytes)."""
    with open(file_path, "rb") as f:
        raw = f.read(100000)
    enc = chardet.detect(raw)
    return enc.get("encoding", "utf-8")

def basic_schema_check(df: pd.DataFrame, required_cols: Optional[list] = None) -> Tuple[bool, str]:
    """
    Basic checks:
    - If required_cols provided, ensure they exist.
    - Ensure dataframe is not empty.
    Returns: (ok: bool, message: str)
    """
    if df is None:
        return False, "DataFrame is None"
    if df.shape[0] == 0:
        return False, "Empty dataframe (0 rows)"
    if required_cols:
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return False, f"Missing required columns: {missing}"
    return True, "OK"

def sanitize_dataframe(df: pd.DataFrame, text_columns: Optional[list] = None) -> pd.DataFrame:
    """
    Sanitize df:
    - If text_columns given, drop rows where all those columns are NA/empty
    - Drop exact duplicate rows
    - Reset index
    """
    if text_columns:
        df = df.dropna(subset=text_columns, how="all")
    df = df.drop_duplicates().reset_index(drop=True)
    return df

def save_uploaded_file(fileobj, filename: str) -> Path:
    """
    Save an uploaded file-like object (with .read()) into RAW_DIR using a secure filename.
    Returns the Path to saved file.
    """
    safe = secure_filename(filename)
    dest = RAW_DIR / safe
    # Ensure dir exists (utils.ensure_dirs() should be called elsewhere)
    with open(dest, "wb") as f:
        f.write(fileobj.read())
    return dest
