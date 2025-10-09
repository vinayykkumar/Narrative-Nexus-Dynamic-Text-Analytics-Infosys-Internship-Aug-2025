# src/classification.py
"""
Train a supervised classifier on TF-IDF features and report metrics.

Usage:
python src/classification.py --matrix models/job_desc/tfidf/matrix.pkl --labels data/raw/job_title_des.csv --label-col "Job Title" --out results/job_desc --test-size 0.2 --random-state 42

Outputs saved in --out:
- model.pkl         (trained classifier)
- metrics.json      (accuracy, precision/recall/f1, roc_auc if computed)
- confusion_matrix.csv
"""
import argparse
from pathlib import Path
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, label_binarize
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    roc_auc_score
)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--matrix", required=True, help="path to matrix.pkl (sparse matrix) from features.py")
    p.add_argument("--vectorizer", required=False, help="optional vectorizer path (not required here)")
    p.add_argument("--labels", required=True, help="CSV with ground truth labels aligned by index")
    p.add_argument("--label-col", required=True, help="column name holding the label (e.g., 'Job Title')")
    p.add_argument("--out", required=True, help="output folder to save model + metrics")
    p.add_argument("--test-size", type=float, default=0.2)
    p.add_argument("--random-state", type=int, default=42)
    args = p.parse_args()

    outp = Path(args.out); outp.mkdir(parents=True, exist_ok=True)

    print("Loading feature matrix:", args.matrix)
    X = joblib.load(args.matrix)  # sparse matrix
    print("Matrix shape:", getattr(X, "shape", None))

    print("Loading labels CSV:", args.labels)
    df = pd.read_csv(args.labels)
    if args.label_col not in df.columns:
        raise ValueError(f"Label column '{args.label_col}' not found. Available columns: {df.columns.tolist()}")

    # align by index: assume processed docs (matrix rows) match CSV order
    y_raw = df[args.label_col].astype(str).reset_index(drop=True)
    n = X.shape[0]
    if len(y_raw) < n:
        raise ValueError(f"Label CSV has fewer rows ({len(y_raw)}) than feature rows ({n}).")
    if len(y_raw) > n:
        print(f"Warning: Label CSV longer ({len(y_raw)}) than feature rows ({n}). Truncating labels to match.")
        y_raw = y_raw.iloc[:n]

    # encode labels
    le = LabelEncoder()
    y = le.fit_transform(y_raw.values)
    class_names = list(le.classes_)
    print("Number of classes:", len(class_names))

    # train/test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y if len(np.unique(y))>1 else None
    )
    print("Train/test sizes:", X_train.shape[0], X_test.shape[0])

    # classifier: Logistic Regression (multinomial) with balanced class weight
    clf = LogisticRegression(max_iter=1000, multi_class="multinomial", solver="saga", class_weight="balanced", random_state=args.random_state)
    print("Training classifier...")
    clf.fit(X_train, y_train)

    print("Predicting on test set...")
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    per_class = {}
    p_arr, r_arr, f_arr, s_arr = precision_recall_fscore_support(y_test, y_pred, average=None, zero_division=0)
    for idx, name in enumerate(class_names):
        per_class[name] = {"precision": float(p_arr[idx]) if idx < len(p_arr) else 0.0,
                           "recall": float(r_arr[idx]) if idx < len(r_arr) else 0.0,
                           "f1": float(f_arr[idx]) if idx < len(f_arr) else 0.0,
                           "support": int(s_arr[idx]) if idx < len(s_arr) else 0}

    # confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)
    cm_df.to_csv(outp / "confusion_matrix.csv", index=True)

    # try ROC-AUC (one-vs-rest) using predict_proba if available and multiclass
    roc_auc = None
    try:
        if hasattr(clf, "predict_proba"):
            probs = clf.predict_proba(X_test)  # shape (n_samples, n_classes)
            # binarize y_test
            if probs.shape[1] == len(np.unique(y_test)):
                y_test_bin = label_binarize(y_test, classes=range(probs.shape[1]))
                roc_auc = float(roc_auc_score(y_test_bin, probs, average="macro", multi_class="ovr"))
    except Exception as e:
        print("Could not compute ROC-AUC:", e)

    metrics = {
        "accuracy": float(acc),
        "precision_macro": float(prec_macro),
        "recall_macro": float(rec_macro),
        "f1_macro": float(f1_macro),
        "roc_auc_macro": roc_auc,
        "per_class": per_class
    }

    # save metrics and model
    (outp / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf8")
    joblib.dump(clf, outp / "model.pkl")
    # save label encoder classes
    (outp / "label_classes.json").write_text(json.dumps(class_names, indent=2), encoding="utf8")

    print("Saved metrics ->", outp / "metrics.json")
    print("Saved model ->", outp / "model.pkl")
    if roc_auc is not None:
        print("ROC-AUC (macro):", roc_auc)
    print("Done.")

if __name__ == "__main__":
    main()
