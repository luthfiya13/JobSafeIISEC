#!/usr/bin/env python3
"""
Adjudicate Multi-Annotator Labels and Compute Agreement Metrics for JOBSAFE.
Calculates:
- Cohen's Kappa (between 2 annotators)
- Percent Agreement
- Confusion matrix of annotators
- Consensus adjudication logic (auto-assign if agreement, flag for manual adjudication if disagreement)
"""
import argparse
import math
from pathlib import Path
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]

def compute_inter_annotator_agreement(df: pd.DataFrame):
    valid = df[df["annotator_1_level"].isin(["LOW", "MEDIUM", "HIGH"]) & 
               df["annotator_2_level"].isin(["LOW", "MEDIUM", "HIGH"])]
    
    n = len(valid)
    print("=" * 60)
    print(f"INTER-ANNOTATOR AGREEMENT REPORT (n={n})")
    print("=" * 60)
    
    if n == 0:
        print("[!] No completed dual-annotated rows found (annotator_1_level and annotator_2_level).")
        return None
    
    y1 = valid["annotator_1_level"]
    y2 = valid["annotator_2_level"]
    
    labels = ["LOW", "MEDIUM", "HIGH"]
    cm = confusion_matrix(y1, y2, labels=labels)
    agreement = (y1 == y2).mean() * 100
    kappa = cohen_kappa_score(y1, y2, labels=labels)
    
    # Quadratic weighted kappa for ordinal risk
    try:
        quad_kappa = cohen_kappa_score(y1, y2, labels=labels, weights="quadratic")
    except Exception:
        quad_kappa = None

    print(f"Percentage Agreement: {agreement:.2f}% ({sum(y1 == y2)}/{n})")
    print(f"Cohen's Kappa (unweighted): {kappa:.4f}")
    if quad_kappa is not None:
        print(f"Cohen's Kappa (quadratic weighted / ordinal): {quad_kappa:.4f}")
    
    print("\nConfusion Matrix (Rows=Annotator 1, Cols=Annotator 2):")
    print(pd.DataFrame(cm, index=[f"A1_{l}" for l in labels], columns=[f"A2_{l}" for l in labels]))
    
    # Interpretation
    interpretation = "Poor"
    if kappa > 0.8: interpretation = "Almost Perfect"
    elif kappa > 0.6: interpretation = "Substantial"
    elif kappa > 0.4: interpretation = "Moderate"
    elif kappa > 0.2: interpretation = "Fair"
    elif kappa > 0.0: interpretation = "Slight"
    print(f"\nAgreement Interpretation: {interpretation} (Landis & Koch, 1977)")
    print("=" * 60)
    
    return {"n": n, "agreement": agreement, "kappa": kappa, "quad_kappa": quad_kappa}

def adjudicate(df: pd.DataFrame, adjudicator_name: str = "Lead Adjudicator"):
    df = df.copy()
    agreed = 0
    disagreed = 0
    
    for idx, row in df.iterrows():
        a1 = str(row.get("annotator_1_level", "")).strip().upper()
        a2 = str(row.get("annotator_2_level", "")).strip().upper()
        existing_gold = str(row.get("gold_risk_level", "")).strip().upper()
        
        if existing_gold in ["LOW", "MEDIUM", "HIGH"]:
            continue
            
        if a1 in ["LOW", "MEDIUM", "HIGH"] and a2 in ["LOW", "MEDIUM", "HIGH"]:
            if a1 == a2:
                df.at[idx, "gold_risk_level"] = a1
                df.at[idx, "annotation_status"] = "ADJUDICATED_CONSENSUS"
                df.at[idx, "adjudicated_by"] = "Auto-Consensus"
                agreed += 1
            else:
                df.at[idx, "annotation_status"] = "DISAGREEMENT_NEEDS_REVIEW"
                disagreed += 1

    print(f"\nAuto-Adjudication Summary:")
    print(f"  - Automatic consensus assigned: {agreed}")
    print(f"  - Disagreements flagged for expert review: {disagreed}")
    return df

def main():
    parser = argparse.ArgumentParser(description="Adjudicate JOBSAFE annotations and calculate Kappa")
    parser.add_argument("--input", required=True, help="Path to annotated CSV")
    parser.add_argument("--output", help="Path to save adjudicated output CSV")
    parser.add_argument("--adjudicator", default="Research Team", help="Adjudicator identifier")
    args = parser.parse_args()

    in_p = Path(args.input)
    if not in_p.is_absolute(): in_p = ROOT / args.input

    df = pd.read_csv(in_p)
    compute_inter_annotator_agreement(df)
    
    adjudicated_df = adjudicate(df, args.adjudicator)
    
    out_p = Path(args.output) if args.output else in_p
    if not out_p.is_absolute(): out_p = ROOT / out_p
    adjudicated_df.to_csv(out_p, index=False, encoding="utf-8-sig")
    print(f"[OK] Saved adjudicated dataset to '{out_p}'")

if __name__ == "__main__":
    main()
