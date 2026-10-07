#!/usr/bin/env python3
"""
Generate Human Risk Annotation Dataset for JOBSAFE.
Samples stratified candidates across sectors from REAL_800_Broad_Candidates.csv.
Output CSV includes standard columns for independent annotator grading, R1-R10 indicator checks,
verification status, and adjudication notes.
"""
import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def prepare_annotation_dataset(input_csv: str, output_csv: str, n_samples: int = 200, seed: int = 42):
    in_p = Path(input_csv)
    if not in_p.is_absolute():
        in_p = ROOT / input_csv
    
    out_p = Path(output_csv)
    if not out_p.is_absolute():
        out_p = ROOT / output_csv

    df = pd.read_csv(in_p)
    sector_col = "sampling_sector" if "sampling_sector" in df.columns else "category_scraped"
    
    # Stratified sampling by sector
    sectors = df[sector_col].unique()
    n_sectors = len(sectors)
    per_sector = max(1, n_samples // n_sectors)
    
    sampled_dfs = []
    for sec in sectors:
        sec_df = df[df[sector_col] == sec]
        sample_k = min(len(sec_df), per_sector)
        sampled_dfs.append(sec_df.sample(n=sample_k, random_state=seed))
    
    sampled = pd.concat(sampled_dfs, ignore_index=True).head(n_samples)

    out_df = pd.DataFrame({
        "record_id": sampled["record_id"],
        "job_title": sampled["job_title"],
        "company_name": sampled["company_name"],
        "sector": sampled[sector_col],
        "group_id": sampled["group_id"] if "group_id" in sampled.columns else sampled["company_name"],
        "text": sampled["model_text"],
        "annotator_1_level": "",
        "annotator_2_level": "",
        "gold_risk_level": "",  # LOW | MEDIUM | HIGH
        "verification_status": "",  # VERIFIED | UNVERIFIED | CONTRADICTORY
        "annotation_status": "PENDING",  # PENDING | ANNOTATED | ADJUDICATED
    })

    # Indicator columns for granular evidence
    for i in range(1, 11):
        out_df[f"R{i}"] = ""  # 0 or 1
        out_df[f"R{i}_evidence"] = ""  # text span

    out_df["adjudicated_by"] = ""
    out_df["notes"] = ""

    out_df.to_csv(out_p, index=False, encoding="utf-8-sig")
    print(f"[OK] Generated annotation dataset at '{out_p}' with {len(out_df)} records across {n_sectors} sectors.")

def main():
    parser = argparse.ArgumentParser(description="Prepare JOBSAFE human annotation dataset")
    parser.add_argument("--input", default="data/REAL_800_Broad_Candidates.csv", help="Source candidates CSV")
    parser.add_argument("--output", default="data/risk_annotation_sample_200.csv", help="Output annotation CSV")
    parser.add_argument("--n", type=int, default=200, help="Total sample size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    prepare_annotation_dataset(args.input, args.output, args.n, args.seed)

if __name__ == "__main__":
    main()
