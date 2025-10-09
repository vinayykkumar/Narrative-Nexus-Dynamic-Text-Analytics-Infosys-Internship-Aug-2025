# src/fix_doc_topics.py
"""
Fix malformed doc_topics_with_text.csv that has no proper header (or entire doc became header).
This will produce a cleaned CSV with columns: doc_index,dominant_topic,doc
Usage:
python src/fix_doc_topics.py --input models/job_desc/nmf/doc_topics_with_text.csv --out models/job_desc/nmf/doc_topics_fixed.csv
"""
import argparse, csv
from pathlib import Path
import pandas as pd

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    inp = Path(args.input)
    out = Path(args.out)

    rows = []
    with open(inp, "r", encoding="utf8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            # parse with csv to handle quoted JSON with commas
            try:
                parsed = next(csv.reader([line]))
            except Exception:
                # fallback: naive split (last part is JSON/text)
                parts = line.split(",", 2)
                parsed = parts if len(parts) >= 3 else (parts + [""])
            # normalize length
            if len(parsed) == 1:
                # maybe header collapsed; try to split by first two commas
                parts = parsed[0].split(",", 2)
                parsed = parts if len(parts) >= 3 else (parts + [""])
            if len(parsed) < 3:
                # pad
                parsed = (parsed + ["", ""])[:3]
            # strip whitespace from doc_index and dominant_topic
            doc_index = parsed[0].strip()
            dominant = parsed[1].strip()
            doc = parsed[2].strip()
            # if doc is quoted JSON string, remove leading/trailing quotes
            if len(doc) >=2 and ((doc[0] == '"' and doc[-1] == '"') or (doc[0] == "'" and doc[-1] == "'")):
                doc = doc[1:-1]
            rows.append({"doc_index": doc_index, "dominant_topic": dominant, "doc": doc})

    df = pd.DataFrame(rows)
    # If doc_index are numeric strings, convert
    try:
        df["doc_index"] = df["doc_index"].astype(int)
    except Exception:
        pass
    df.to_csv(out, index=False, encoding="utf8")
    print(f"Saved fixed CSV -> {out} (rows: {len(df)})")

if __name__ == "__main__":
    main()

