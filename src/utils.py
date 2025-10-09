# src/utils.py
"""
Utility functions for file paths and safe filenames.
"""

import os
from pathlib import Path

# Base project directory (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parents[1]

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

def ensure_dirs():
    """Make sure data/raw and data/processed directories exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def secure_filename(fname: str) -> str:
    """
    Clean a filename so it's safe to save.
    Removes unwanted characters.
    """
    return "".join(c for c in fname if c.isalnum() or c in (" ", ".", "_", "-")).rstrip()
