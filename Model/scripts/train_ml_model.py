#!/usr/bin/env python3
"""
Train and Cross-Validate JOBSAFE ML Risk Classifier.
Uses:
- Word (1-2) + Character (3-5) TF-IDF + Structural Metadata
- Regularized / Calibrated Logistic Regression
- GroupKFold on group_id / company cluster to prevent data leakage
- Evaluates Macro-F1, Balanced Accuracy, High-Risk Precision, High-Risk Recall, and Confusion Matrix
"""
import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix, f1_score, balanced_accuracy_score,
    precision_score, recall_score
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jobsafe.ml_model import JobsafeMLModel, CLASSES

def train_and_evaluate(
    data_csv: str,
    output_model_path: str = "config/jobsafe_ml_model.pkl",
    n_splits: int = 4,
    group_col: str = "group_id"
):
    csv_p = Path(data_csv) if Path(data_csv).is_absolute() else ROOT / data_csv
    df = pd.read_csv(csv_p)
    
    # Identify target label column
    label_col = None
    for candidate in ["expected_level", "gold_risk_level", "gold_level", "risk_level"]:
        if candidate in df.columns:
            label_col = candidate
            break
            
    if label_col is None:
        sys.exit(f"[ERROR] No valid risk level column found in {csv_p}. Expected one of: expected_level, gold_risk_level, gold_level, risk_level")
        
    text_col = "text" if "text" in df.columns else "model_text" if "model_text" in df.columns else "ocr_text"
    
    # Filter valid rows
    df = df[df[text_col].notna() & df[label_col].isin(CLASSES)].copy()
    n_samples = len(df)
    print("=" * 65)
    print(f"JOBSAFE ML MODEL TRAINING & GROUP-AWARE CV (n={n_samples})")
    print(f"Data source: {csv_p.name}")
    print(f"Class distribution:\n{df[label_col].value_counts().to_dict()}")
    print("=" * 65)
    
    if n_samples < 6:
        sys.exit("[ERROR] Too few samples to perform cross-validation (need >= 6).")
        
    texts = df[text_col].tolist()
    labels = df[label_col].tolist()
    
    # Grouping setup
    if group_col in df.columns and df[group_col].nunique() >= n_splits:
        groups = df[group_col].astype(str).tolist()
        cv = GroupKFold(n_splits=min(n_splits, df[group_col].nunique()))
        cv_iter = cv.split(texts, labels, groups)
        print(f"Cross-Validation: GroupKFold on '{group_col}' (k={n_splits})")
    else:
        cv = StratifiedKFold(n_splits=min(n_splits, min(df[label_col].value_counts())), shuffle=True, random_state=42)
        cv_iter = cv.split(texts, labels)
        print(f"Cross-Validation: StratifiedKFold (k={n_splits})")

    oof_preds = [""] * n_samples
    oof_probas = np.zeros((n_samples, len(CLASSES)))
    
    for fold, (train_idx, val_idx) in enumerate(cv_iter):
        train_texts = [texts[i] for i in train_idx]
        train_labels = [labels[i] for i in train_idx]
        val_texts = [texts[i] for i in val_idx]
        val_labels = [labels[i] for i in val_idx]
        
        fold_model = JobsafeMLModel(c_reg=1.0)
        fold_model.fit(train_texts, train_labels, calibrate=False)
        
        val_preds = fold_model.predict(val_texts)
        val_probas = fold_model.predict_proba(val_texts)
        
        for idx_pos, orig_idx in enumerate(val_idx):
            oof_preds[orig_idx] = val_preds[idx_pos]
            oof_probas[orig_idx] = val_probas[idx_pos]

    # Out-Of-Fold Evaluation Metrics
    macro_f1 = f1_score(labels, oof_preds, labels=CLASSES, average="macro")
    weighted_f1 = f1_score(labels, oof_preds, labels=CLASSES, average="weighted")
    bal_acc = balanced_accuracy_score(labels, oof_preds)
    
    # High-Risk specific metrics
    is_high_true = [l == "HIGH" for l in labels]
    is_high_pred = [p == "HIGH" for p in oof_preds]
    high_prec = precision_score(is_high_true, is_high_pred, zero_division=0)
    high_rec = recall_score(is_high_true, is_high_pred, zero_division=0)
    
    cm = confusion_matrix(labels, oof_preds, labels=CLASSES)
    
    print("\n--- OUT-OF-FOLD (OOF) CV EVALUATION RESULTS ---")
    print(f"Macro F1-Score:         {macro_f1:.4f}")
    print(f"Weighted F1-Score:      {weighted_f1:.4f}")
    print(f"Balanced Accuracy:      {bal_acc:.4f}")
    print(f"High-Risk Precision:    {high_prec:.4f}")
    print(f"High-Risk Recall:       {high_rec:.4f}")
    
    print("\nConfusion Matrix (Rows=True, Cols=Pred) [LOW, MEDIUM, HIGH]:")
    print(pd.DataFrame(cm, index=[f"True_{c}" for c in CLASSES], columns=[f"Pred_{c}" for c in CLASSES]))
    
    print("\nDetailed Classification Report:")
    print(classification_report(labels, oof_preds, labels=CLASSES, zero_division=0))
    
    # Train final full model and save
    print(f"Training final full model on all {n_samples} samples...")
    final_model = JobsafeMLModel(c_reg=1.0)
    final_model.fit(texts, labels, calibrate=True)
    
    out_p = Path(output_model_path) if Path(output_model_path).is_absolute() else ROOT / output_model_path
    final_model.save(out_p)
    print(f"[OK] Trained and saved JOBSAFE ML model to '{out_p}'")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Train JOBSAFE ML Risk Classifier")
    parser.add_argument("--data", default="data/gold_regression_cases.csv", help="Input labeled CSV")
    parser.add_argument("--output", default="config/jobsafe_ml_model.pkl", help="Path to save trained model")
    parser.add_argument("--folds", type=int, default=4, help="Number of CV folds")
    args = parser.parse_args()

    train_and_evaluate(args.data, args.output, args.folds)

if __name__ == "__main__":
    main()
