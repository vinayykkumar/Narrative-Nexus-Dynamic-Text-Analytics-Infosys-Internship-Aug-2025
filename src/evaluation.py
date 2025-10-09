# src/evaluation.py
"""
Evaluate topic assignments against ground-truth labels.

Usage:
python src/evaluation.py --pred models/job_desc/nmf/doc_topics.csv --labels data/raw/job_title_des.csv --label-col "Job Title" --out eval/job_desc --w models/job_desc/quick_nmf/W.pkl

Notes:
- If label CSV length differs from pred CSV, we align by index (with a warning) or by matching a text column if provided.
- If --w (W matrix) is provided, ROC-AUC (one-vs-rest) will be computed using W scores.
"""

import argparse
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score
)
from sklearn.preprocessing import label_binarize

def load_preds(pred_csv: Path):
    df = pd.read_csv(pred_csv)
    # expect columns: doc_index, dominant_topic
    if 'dominant_topic' not in df.columns:
        # try second column
        df.columns = [c.strip() for c in df.columns]
        if len(df.columns) >= 2:
            df = df.rename(columns={df.columns[1]: 'dominant_topic'})
        else:
            raise ValueError("Cannot find 'dominant_topic' column in predictions CSV.")
    return df

def align_labels(pred_df: pd.DataFrame, label_csv: Path, label_col: str, text_col: str = None):
    labels_df = pd.read_csv(label_csv)
    # if text_col provided, try to match by text (best-effort)
    if text_col and text_col in labels_df.columns:
        # create mapping of text -> label (first occurrence)
        mapping = labels_df.set_index(text_col)[label_col].to_dict()
        # try map by docs if 'doc' column exists in pred_df
        if 'doc' in pred_df.columns:
            mapped = pred_df['doc'].map(mapping)
            if mapped.notna().sum() > 0:
                # use mapped where available, otherwise fallback to index alignment
                pred_labels = []
                for i, row in pred_df.iterrows():
                    if pd.notna(mapped.iat[i]):
                        pred_labels.append(str(mapped.iat[i]))
                    elif i < len(labels_df):
                        pred_labels.append(str(labels_df.iloc[i][label_col]))
                    else:
                        pred_labels.append(None)
                return pd.Series(pred_labels)
    # fallback: align by index (truncate to shortest)
    n = min(len(pred_df), len(labels_df))
    if len(pred_df) != len(labels_df):
        print(f"Warning: prediction rows ({len(pred_df)}) and label rows ({len(labels_df)}) differ. Aligning by index and truncating to {n}.")
    return labels_df[label_col].astype(str).iloc[:n].reset_index(drop=True)

def compute_metrics(y_true, y_pred, labels_unique=None, W_scores=None):
    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred).astype(int)
    acc = accuracy_score(y_true_arr, y_pred_arr)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(y_true_arr, y_pred_arr, average='macro', zero_division=0)
    per_label = {}
    if labels_unique is not None:
        # compute per-label scores
        p, r, f, sup = precision_recall_fscore_support(y_true_arr, y_pred_arr, labels=labels_unique, zero_division=0)
        for lab, pp, rr, ff, s in zip(labels_unique, p, r, f, sup):
            per_label[int(lab)] = {"precision": float(pp), "recall": float(rr), "f1": float(ff), "support": int(s)}
    metrics = {
        "accuracy": float(acc),
        "precision_macro": float(precision_macro),
        "recall_macro": float(recall_macro),
        "f1_macro": float(f1_macro),
        "per_label": per_label
    }

    # ROC-AUC using W_scores if provided (one-vs-rest)
    if W_scores is not None:
        try:
            # ensure W_scores shape (n_samples, n_classes)
            W = np.asarray(W_scores)
            n_classes = W.shape[1]
            # binarize true labels by class indices 0..n_classes-1
            y_bin = label_binarize(y_true_arr, classes=list(range(n_classes)))
            if y_bin.shape[1] != n_classes:
                # pad or truncate as needed
                print("Warning: y_bin shape differs from W columns; skipping ROC-AUC.")
            else:
                auc = roc_auc_score(y_bin, W, average='macro', multi_class='ovr')
                metrics['roc_auc_macro'] = float(auc)
        except Exception as e:
            print("Could not compute ROC-AUC:", e)
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", required=True, help="predictions CSV (doc_topics.csv)")
    parser.add_argument("--labels", required=True, help="ground truth labels CSV")
    parser.add_argument("--label-col", required=True, help="column name in label CSV with true labels")
    parser.add_argument("--text-col", default=None, help="optional text column name to align by text")
    parser.add_argument("--w", default=None, help="optional W matrix (joblib .pkl) with topic scores per doc")
    parser.add_argument("--out", default="eval_out", help="output folder to save metrics")
    args = parser.parse_args()

    pred_df = load_preds(Path(args.pred))
    # align labels
    y_true_series = align_labels(pred_df, Path(args.labels), args.label_col, text_col=args.text_col)
    # predicted topics (truncate to same length)
    y_pred = pred_df['dominant_topic'].astype(int).iloc[:len(y_true_series)].tolist()

    # optional W scores
    W_scores = None
    if args.w:
        try:
            import joblib
            W_scores = joblib.load(args.w)
            # if W has more rows than aligned set, truncate
            if W_scores.shape[0] > len(y_pred):
                W_scores = W_scores[:len(y_pred)]
        except Exception as e:
            print("Could not load W matrix:", e)
            W_scores = None

    # ensure numeric labels start at 0..k-1 if they are strings, map to ints
    unique_labels = sorted(list(pd.Index(y_true_series).unique()))
    label_map = {lab: i for i, lab in enumerate(unique_labels)}
    y_true_mapped = [label_map[l] for l in y_true_series]
    metrics = compute_metrics(y_true_mapped, y_pred, labels_unique=list(range(len(unique_labels))), W_scores=W_scores)

    outp = Path(args.out)
    outp.mkdir(parents=True, exist_ok=True)
    # save confusion matrix CSV
    cm = confusion_matrix(y_true_mapped, y_pred)
    cm_df = pd.DataFrame(cm, index=[f"true_{i}" for i in range(cm.shape[0])], columns=[f"pred_{i}" for i in range(cm.shape[1])])
    cm_df.to_csv(outp / "confusion_matrix.csv", index=True)
    # save metrics json
    with open(outp / "metrics.json", "w", encoding="utf8") as fw:
        json.dump(metrics, fw, indent=2)
    print("Saved metrics ->", outp / "metrics.json")
    print("Saved confusion matrix ->", outp / "confusion_matrix.csv")
    print("Summary:")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
