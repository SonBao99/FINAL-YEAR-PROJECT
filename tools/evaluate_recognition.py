"""Evaluate face-recognition results from kiosk logs.

Expected input CSV columns (defaults):
- timestamp: optional
- ground_truth: ground-truth student id (empty or NaN for no person)
- predicted: predicted student id (empty or NaN for no prediction)
- score: optional similarity/confidence score (higher == more likely match)

The script computes TP/FP/FN/TN, Precision, Recall, F1, FAR, FRR and, when a score
column is provided, ROC AUC and EER. It can also save a confusion matrix and plots
if matplotlib is available.

Example:
    python tools/evaluate_recognition.py logs/kiosk_run.csv --ground-col ground_truth --pred-col predicted --score-col score

"""
from __future__ import annotations

import argparse
import math
import os
from typing import Optional

import pandas as pd


def safe_str(x):
    if pd.isna(x):
        return ""
    return str(x).strip()


def compute_basic_counts(df: pd.DataFrame, ground_col: str, pred_col: str):
    TP = FP = FN = TN = 0
    per_pair = []  # for confusion matrix

    for _, row in df.iterrows():
        gt = safe_str(row.get(ground_col, ""))
        pred = safe_str(row.get(pred_col, ""))

        if gt and pred:
            if pred == gt:
                TP += 1
            else:
                # predicted someone but wrong => false accept
                FP += 1
        elif gt and not pred:
            # ground truth present but system didn't predict => miss
            FN += 1
        elif not gt and pred:
            # no ground truth, but system predicted => false accept
            FP += 1
        else:
            # no ground truth, no prediction
            TN += 1

        per_pair.append((gt or "__NONE__", pred or "__NONE__"))

    return {"TP": TP, "FP": FP, "FN": FN, "TN": TN}, per_pair


def compute_rates(counts: dict):
    TP = counts["TP"]
    FP = counts["FP"]
    FN = counts["FN"]
    TN = counts["TN"]

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) > 0 else 0.0

    FAR = FP / (FP + TN) if (FP + TN) > 0 else 0.0
    FRR = FN / (FN + TP) if (FN + TP) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "FAR": FAR,
        "FRR": FRR,
    }


def try_compute_score_metrics(df: pd.DataFrame, ground_col: str, pred_col: str, score_col: str):
    try:
        from sklearn.metrics import roc_curve, auc
    except Exception:
        print("scikit-learn is not available — skipping ROC/AUC/EER calculations.\nInstall with: pip install scikit-learn")
        return None

    # Build labels: genuine (1) if predicted==ground and ground non-empty; impostor (0) otherwise
    y_true = []
    scores = []
    for _, row in df.iterrows():
        gt = safe_str(row.get(ground_col, ""))
        pred = safe_str(row.get(pred_col, ""))
        score = row.get(score_col, None)

        if score is None or (isinstance(score, float) and math.isnan(score)):
            # cannot compute
            continue

        y_true.append(1 if (gt and pred and pred == gt) else 0)
        scores.append(float(score))

    if not scores:
        return None

    fpr, tpr, thresholds = roc_curve(y_true, scores)
    roc_auc = auc(fpr, tpr)

    # Compute EER: point where FNR ~= FPR
    fnr = 1 - tpr
    eer_idx = None
    min_diff = 1.0
    for i in range(len(fpr)):
        diff = abs(fpr[i] - fnr[i])
        if diff < min_diff:
            min_diff = diff
            eer_idx = i

    eer = (fpr[eer_idx] + fnr[eer_idx]) / 2.0 if eer_idx is not None else None

    return {"fpr": fpr, "tpr": tpr, "thresholds": thresholds, "auc": roc_auc, "eer": eer}


def save_confusion(per_pair, out_path: str):
    # Build confusion matrix dataframe
    pairs = pd.DataFrame(per_pair, columns=["ground", "predicted"])
    cm = pd.crosstab(pairs["ground"], pairs["predicted"], rownames=["ground"], colnames=["predicted"], dropna=False)
    cm.to_csv(out_path)
    print(f"Saved confusion matrix to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate recognition results from kiosk logs (CSV).")
    parser.add_argument("log_csv", help="Path to kiosk log CSV")
    parser.add_argument("--ground-col", default="ground_truth", help="Column name for ground-truth id")
    parser.add_argument("--pred-col", default="predicted", help="Column name for predicted id")
    parser.add_argument("--score-col", default=None, help="Column name for similarity/confidence score (optional)")
    parser.add_argument("--out-dir", default="evaluation_out", help="Directory to write outputs")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    df = pd.read_csv(args.log_csv)
    print(f"Loaded {len(df)} rows from {args.log_csv}")

    counts, per_pair = compute_basic_counts(df, args.ground_col, args.pred_col)
    rates = compute_rates(counts)

    print("\nCounts:")
    for k, v in counts.items():
        print(f"  {k}: {v}")

    print("\nRates:")
    for k, v in rates.items():
        print(f"  {k}: {v:.4f}")

    # Save summary
    summary = {**counts, **rates}
    summary_df = pd.DataFrame([summary])
    summary_csv = os.path.join(args.out_dir, "summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"Saved summary to {summary_csv}")

    # Confusion matrix
    cm_path = os.path.join(args.out_dir, "confusion_matrix.csv")
    save_confusion(per_pair, cm_path)

    # Score-based metrics
    if args.score_col:
        score_stats = try_compute_score_metrics(df, args.ground_col, args.pred_col, args.score_col)
        if score_stats:
            print(f"\nROC AUC: {score_stats['auc']:.4f}")
            print(f"EER (approx): {score_stats['eer']:.4f}")
            # Optionally save arrays
            import numpy as np
            np.save(os.path.join(args.out_dir, "roc_fpr.npy"), score_stats["fpr"])
            np.save(os.path.join(args.out_dir, "roc_tpr.npy"), score_stats["tpr"])
            print(f"Saved ROC arrays to {args.out_dir}")

            # Try to plot if matplotlib is available
            try:
                import matplotlib.pyplot as plt
                plt.figure()
                plt.plot(score_stats["fpr"], score_stats["tpr"], label=f"AUC={score_stats['auc']:.3f}")
                plt.xlabel("False Positive Rate")
                plt.ylabel("True Positive Rate")
                plt.title("ROC")
                plt.legend()
                plt.grid(True)
                plt.savefig(os.path.join(args.out_dir, "roc_curve.png"))
                print(f"Saved ROC plot to {os.path.join(args.out_dir, 'roc_curve.png')}")
            except Exception:
                print("matplotlib not available or plotting failed; skipping ROC plot.")


if __name__ == "__main__":
    main()
