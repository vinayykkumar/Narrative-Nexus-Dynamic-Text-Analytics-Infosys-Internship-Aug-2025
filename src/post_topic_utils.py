# src/post_topic_utils.py
"""
Generate top_words.json and doc_topics_with_text.csv from saved artifacts.

Usage:
python src/post_topic_utils.py --matrix models/job_desc/tfidf/matrix.pkl \
    --vectorizer models/job_desc/tfidf/vectorizer.pkl \
    --model models/job_desc/nmf/nmf_model.pkl \
    --docs data/processed/job_desc_clean.txt \
    --out models/job_desc/nmf \
    --top-n 20
"""

import argparse, joblib, json
from pathlib import Path
import numpy as np

def load_terms(vec_path):
    vec = joblib.load(vec_path)
    try:
        return vec.get_feature_names_out()
    except Exception:
        return [k for k,v in sorted(vec.vocabulary_.items(), key=lambda kv: kv[1])]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--matrix", required=True)
    p.add_argument("--vectorizer", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--docs", required=False, help="processed docs file (one doc per line) to include in doc_topics output")
    p.add_argument("--out", required=True, help="output folder to save top_words.json and doc_topics_with_text.csv")
    p.add_argument("--top-n", type=int, default=20)
    args = p.parse_args()

    matrix = joblib.load(args.matrix)  # not used for top words but useful to check size
    terms = load_terms(args.vectorizer)
    model = joblib.load(args.model)
    comps = model.components_  # shape (n_topics, n_terms)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    # top words per topic
    top_n = args.top_n
    top_words = {}
    for t_idx, comp in enumerate(comps):
        idx = np.argsort(comp)[-top_n:][::-1]
        top_words[t_idx] = [terms[i] for i in idx]
    (outdir / "top_words.json").write_text(json.dumps(top_words, ensure_ascii=False, indent=2), encoding="utf8")
    print("Saved top_words.json ->", outdir / "top_words.json")

    # doc topics (dominant) - use model.transform on matrix
    try:
        doc_topic_dist = model.transform(matrix)
        dominant = doc_topic_dist.argmax(axis=1).tolist()
    except Exception as e:
        print("Failed to transform matrix with model:", e)
        dominant = None

    # write doc_topics_with_text.csv (if docs provided)
    docs_path = Path(args.docs) if args.docs else None
    csv_out = outdir / "doc_topics_with_text.csv"
    with open(csv_out, "w", encoding="utf8") as fw:
        if docs_path and docs_path.exists():
            with open(docs_path, "r", encoding="utf8") as fr:
                for i, line in enumerate(fr):
                    text = line.strip()
                    t = dominant[i] if dominant is not None and i < len(dominant) else ""
                    # escape tabs/newlines by quoting JSON-style
                    fw.write(f"{i},{t},{json.dumps(text, ensure_ascii=False)}\n")
        else:
            # just write indices and dominant topic
            fw.write("doc_index,dominant_topic,doc\n")
            for i, t in enumerate(dominant if dominant is not None else []):
                fw.write(f"{i},{t},\"\"\n")
    print("Saved doc_topics_with_text.csv ->", csv_out)

if __name__ == "__main__":
    main()
