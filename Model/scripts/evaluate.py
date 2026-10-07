#!/usr/bin/env python3
"""
Comprehensive Evaluation Pipeline for JOBSAFE.
Evaluates Rule-only, ML-only, and Hybrid models on independent risk datasets.

Metrics:
- Macro F1, Weighted F1, Balanced Accuracy
- Ordinal Confusion Matrix (LOW, MEDIUM, HIGH)
- High-Risk Precision, Recall, F1, and False Positive Rate (FPR) with Wilson 95% Confidence Intervals
- Slice Analysis across key domains: Startup/UMKM, Personal WA, Generic Email, Overseas, High Salary, Short/Long Text, Verification Status.
"""
import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    balanced_accuracy_score, confusion_matrix, f1_score,
    precision_score, recall_score
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jobsafe import JobsafeEngine, JobsafeHybridEngine
from jobsafe.ml_model import CLASSES

def wilson_interval(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Calculate Wilson score interval with continuity correction."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z**2 / n
    center = p + z**2 / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lower = max(0.0, (center - margin) / denom)
    upper = min(1.0, (center + margin) / denom)
    return round(lower, 4), round(upper, 4)

def calculate_binary_metrics(y_true: List[bool], y_pred: List[bool], title: str) -> Dict[str, Any]:
    tp = sum(t and p for t, p in zip(y_true, y_pred))
    fp = sum((not t) and p for t, p in zip(y_true, y_pred))
    fn = sum(t and (not p) for t, p in zip(y_true, y_pred))
    tn = sum((not t) and (not p) for t, p in zip(y_true, y_pred))
    
    prec = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
    rec = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 and not math.isnan(prec) and not math.isnan(rec) else float("nan")
    fpr = fp / (fp + tn) if (fp + tn) > 0 else float("nan")
    
    prec_ci = wilson_interval(tp, tp + fp)
    rec_ci = wilson_interval(tp, tp + fn)
    fpr_ci = wilson_interval(fp, fp + tn)
    
    print(f"\n[{title}]")
    print(f"  TP={tp} | FP={fp} | FN={fn} | TN={tn} (Total={len(y_true)})")
    print(f"  Precision: {prec:.4f} (95% CI: {prec_ci[0]:.3f} - {prec_ci[1]:.3f})")
    print(f"  Recall:    {rec:.4f} (95% CI: {rec_ci[0]:.3f} - {rec_ci[1]:.3f})")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"  FPR:       {fpr:.4f} (95% CI: {fpr_ci[0]:.3f} - {fpr_ci[1]:.3f})")
    
    return {
        "title": title, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": prec, "precision_ci95": prec_ci,
        "recall": rec, "recall_ci95": rec_ci,
        "f1": f1, "fpr": fpr, "fpr_ci95": fpr_ci
    }

def run_slice_analysis(df: pd.DataFrame):
    print("\n" + "=" * 65)
    print("SUB-POPULATION SLICE & ROBUSTNESS ANALYSIS")
    print("=" * 65)
    
    # 1. Verification status slice
    if "verif_status" in df.columns:
        print("\n[Slice 1] Performance by Verification Status:")
        for v_status, group in df.groupby("verif_status"):
            acc = (group["gold_level"] == group["pred_level"]).mean() * 100
            fp = sum((group["gold_level"] == "LOW") & (group["pred_level"] != "LOW"))
            print(f"  - {v_status} (n={len(group)}): Accuracy={acc:.1f}%, False Positives={fp}")

    # 2. Text length slice (Short < 100, Medium 100-500, Long > 500)
    df["len_bucket"] = pd.cut(df["text"].str.len(), bins=[0, 100, 500, 100000], labels=["Short (<100)", "Medium (100-500)", "Long (>500)"])
    print("\n[Slice 2] Performance by Text Length:")
    for l_bucket, group in df.groupby("len_bucket", observed=False):
        if len(group) > 0:
            acc = (group["gold_level"] == group["pred_level"]).mean() * 100
            print(f"  - {l_bucket} (n={len(group)}): Accuracy={acc:.1f}%")

    # 3. Tags / Sub-slices if present
    if "tag" in df.columns:
        print("\n[Slice 3] Specific Tag / Edge Case Accuracy:")
        tag_stats = df.groupby("tag").apply(
            lambda g: pd.Series({
                "n": len(g),
                "gold": g["gold_level"].iloc[0],
                "pred_match": sum(g["gold_level"] == g["pred_level"]),
                "accuracy": (g["gold_level"] == g["pred_level"]).mean() * 100
            })
        )
        print(tag_stats.to_string())

def evaluate_dataset(
    csv_path: str,
    mode: str = "rule_only", # 'rule_only' | 'ml_only' | 'hybrid'
    output_json: Optional[str] = None
):
    csv_p = Path(csv_path) if Path(csv_path).is_absolute() else ROOT / csv_path
    if not csv_p.exists():
        sys.exit(f"[ERROR] File not found: {csv_p}")
        
    df = pd.read_csv(csv_p)
    
    # Identify gold column
    gold_col = None
    for col in ["gold_risk_level", "gold_level", "expected_level", "risk_level"]:
        if col in df.columns:
            gold_col = col
            break
            
    if not gold_col:
        sys.exit(f"[ERROR] No gold label column found in {csv_p}. Expected gold_risk_level, gold_level, or expected_level.")
        
    text_col = "text" if "text" in df.columns else "ocr_text" if "ocr_text" in df.columns else "model_text"
    
    # Filter valid rows
    df = df[df[text_col].notna() & df[gold_col].isin(CLASSES)].copy()
    if df.empty:
        sys.exit(f"[ERROR] No rows with valid text and gold labels (LOW/MEDIUM/HIGH) in {csv_p}.")
        
    df = df.rename(columns={text_col: "text", gold_col: "gold_level"})
    n_total = len(df)
    
    print("=" * 65)
    print(f"JOBSAFE EVALUATION PIPELINE (Mode: {mode.upper()}, n={n_total})")
    print(f"Dataset: {csv_p.name}")
    print(f"Ground Truth Distribution:\n{df['gold_level'].value_counts().to_dict()}")
    print("=" * 65)
    
    # Initialize Engine
    if mode == "rule_only":
        engine = JobsafeEngine()
    else:
        engine = JobsafeHybridEngine()

    preds = []
    scores = []
    verif_statuses = []
    
    for text in df["text"]:
        if mode == "rule_only":
            res = engine.analyze(text)
        else:
            res = engine.analyze(text, mode=mode)
            
        preds.append(res["risk_level"])
        scores.append(res["risk_score"])
        verif_statuses.append(res["verification_status"]["status"])

    df["pred_level"] = preds
    df["pred_score"] = scores
    df["verif_status"] = verif_statuses
    
    # Handle insufficient input
    valid_mask = df["pred_level"].isin(CLASSES)
    n_insufficient = sum(~valid_mask)
    if n_insufficient > 0:
        print(f"[!] Warning: {n_insufficient} inputs resulted in INSUFFICIENT_INPUT and were excluded from metric calculation.")

    eval_df = df[valid_mask].copy()
    y_true = eval_df["gold_level"].tolist()
    y_pred = eval_df["pred_level"].tolist()
    
    # Core Ordinal & Multi-class Metrics
    macro_f1 = f1_score(y_true, y_pred, labels=CLASSES, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, labels=CLASSES, average="weighted", zero_division=0)
    bal_acc = balanced_accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    
    print("\n--- MULTI-CLASS ORDINAL RISK METRICS ---")
    print(f"Macro F1-Score:    {macro_f1:.4f}")
    print(f"Weighted F1-Score: {weighted_f1:.4f}")
    print(f"Balanced Accuracy: {bal_acc:.4f}")
    
    print("\nConfusion Matrix (Rows=Gold Ground Truth, Cols=Predicted Risk):")
    cm_df = pd.DataFrame(cm, index=[f"Gold_{c}" for c in CLASSES], columns=[f"Pred_{c}" for c in CLASSES])
    print(cm_df)
    
    # Binary evaluations
    high_true = [g == "HIGH" for g in y_true]
    high_pred = [p == "HIGH" for p in y_pred]
    high_metrics = calculate_binary_metrics(high_true, high_pred, "POSITIVE = HIGH (Critical Scam Alert)")
    
    warn_true = [g in ("MEDIUM", "HIGH") for g in y_true]
    warn_pred = [p in ("MEDIUM", "HIGH") for p in y_pred]
    warn_metrics = calculate_binary_metrics(warn_true, warn_pred, "POSITIVE = MEDIUM + HIGH (Verification Warning Required)")
    
    # Slice analysis
    run_slice_analysis(df)
    
    report = {
        "dataset": csv_p.name,
        "mode": mode,
        "n_samples": n_total,
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "balanced_accuracy": float(bal_acc),
        "confusion_matrix": cm.tolist(),
        "classes": CLASSES,
        "high_risk_metrics": high_metrics,
        "warning_metrics": warn_metrics
    }
    
    if output_json:
        out_j = Path(output_json) if Path(output_json).is_absolute() else ROOT / output_json
        with open(out_j, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n[OK] Saved evaluation report to '{out_j}'")
        
    print("\n" + "=" * 65)
    return report

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Evaluation Pipeline for JOBSAFE")
    parser.add_argument("--csv", default="data/gold_regression_cases.csv", help="Input evaluation CSV")
    parser.add_argument("--mode", default="rule_only", choices=["rule_only", "ml_only", "hybrid"], help="Evaluation mode")
    parser.add_argument("--output_json", help="Optional path to save JSON evaluation report")
    args = parser.parse_args()

    evaluate_dataset(args.csv, args.mode, args.output_json)

if __name__ == "__main__":
    main()
