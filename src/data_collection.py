# src/data_collection.py
"""
Functions to load dataset files into pandas DataFrames:
- CSV
- JSON / JSON Lines
- TXT (one document per line)

Also provides load_all_from_folder to bulk-load supported files.
"""

from pathlib import Path
from typing import Union, List, Dict
import pandas as pd
from .utils import RAW_DIR, ensure_dirs

ensure_dirs()

def is_json_lines(path: Path) -> bool:
    """
    Quick heuristic to detect JSON-lines (ndjson) files.
    """
    try:
        with open(path, "r", encoding="utf8", errors="ignore") as f:
            first = f.readline()
            # If first non-empty line starts with '{' or '[' and next line also looks like JSON -> likely json-lines
            return first.strip().startswith("{") or first.strip().startswith("[")
    except Exception:
        return False

def load_csv(path: Path) -> pd.DataFrame:
    # try common encodings; let pandas guess first, fallback to utf-8/latin1
    try:
        return pd.read_csv(path)
    except Exception:
        try:
            return pd.read_csv(path, encoding="utf-8", engine="python")
        except Exception:
            return pd.read_csv(path, encoding="latin1", engine="python")

def load_json(path: Path) -> pd.DataFrame:
    # try json lines first, fallback to normal json
    try:
        return pd.read_json(path, lines=True)
    except Exception:
        return pd.read_json(path)

def load_txt(path: Path) -> pd.DataFrame:
    # each non-empty line becomes one document row under column 'text'
    docs = []
    with open(path, "r", encoding="utf8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(line)
    return pd.DataFrame({"text": docs})

def load_file(path: Union[str, Path]) -> pd.DataFrame:
    """
    General loader that picks the correct loader based on file suffix.
    Returns a pandas DataFrame.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return load_csv(p)
    if suffix == ".json":
        return load_json(p)
    if suffix == ".txt":
        return load_txt(p)
    raise ValueError(f"Unsupported file type: {suffix}")

def load_all_from_folder(folder: Union[str, Path], exts: List[str] = None) -> Dict[str, pd.DataFrame]:
    """
    Load all files with supported extensions from folder.
    Returns dict: { filename: dataframe }
    """
    if exts is None:
        exts = [".csv", ".json", ".txt"]
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    dfs = {}
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in exts:
            try:
                df = load_file(p)
                dfs[p.name] = df
            except Exception as e:
                # don't raise here; just report failure for that file
                print(f"[WARN] Failed to load {p.name}: {e}")
    return dfs

# quick manual test when run directly
if __name__ == "__main__":
    print("Running quick loader test on data/raw (if files exist)...")
    folder = RAW_DIR
    results = load_all_from_folder(folder)
    for name, df in results.items():
        print(f"Loaded {name} -> shape: {df.shape}, columns: {list(df.columns)[:6]}")

