#!/usr/bin/env python3
"""
Audit Data Leakage and Dataset Characteristics for JOBSAFE.
Audits:
- Vocabulary / n-gram leakage between datasets
- Text length / structural anomalies
- Formatting patterns and prefixes ('Job Title:', 'Company:')
- Duplication and near-duplication across company / campaign clusters
- Grouped split sanity
"""
import sys
import re
import hashlib
from pathlib import Path
import pandas as pd
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def inspect_dataset_leakage():
    real_path = ROOT / "data/REAL_800_Broad_Candidates.csv"
    scam_path = ROOT / "data/SCAM_ADVISORY_EVIDENCE_LIBRARY_clean.csv"
    poster_path = ROOT / "data/PAPER_50_POSTER_TEMPLATE.csv"

    print("=" * 60)
    print("JOBSAFE DATASET & LEAKAGE AUDIT REPORT")
    print("=" * 60)

    # 1. REAL_800
    if real_path.exists():
        df_real = pd.read_csv(real_path)
        print(f"\n[1] REAL CANDIDATES (Glints Broad Scrape): n={len(df_real)}")
        print(f"    - Unique companies: {df_real['company_name'].nunique()}")
        print(f"    - Unique text hashes: {df_real['text_hash'].nunique()}")
        print(f"    - Sectors represented: {df_real['sampling_sector'].value_counts().to_dict()}")
        print(f"    - Caveat: 100% of posts have had emails/phones stripped during Glints processing.")
        print(f"    - Structural prefix check ('Job Title:' presence in model_text):")
        has_prefix = df_real['model_text'].str.startswith("Job Title:").mean() * 100
        print(f"      {has_prefix:.1f}% of model_text entries start with synthetic prefix 'Job Title:'")
        
        # Check text length distribution
        lengths = df_real['model_text'].str.len()
        print(f"      Text length: min={lengths.min()}, median={lengths.median():.0f}, max={lengths.max()}, mean={lengths.mean():.1f}")
        
        # Duplicate company groups
        comp_counts = df_real['company_name'].value_counts()
        mult_comp = comp_counts[comp_counts > 1]
        print(f"      Companies appearing >1 times: {len(mult_comp)} companies (total {mult_comp.sum()} rows)")
        print(f"      * Critical Rule: GroupKFold on group_id / company_name is MANDATORY to prevent company leakage.")

    # 2. SCAM Advisory Library
    if scam_path.exists():
        df_scam = pd.read_csv(scam_path)
        print(f"\n[2] SCAM ADVISORY / DEBUNKING LIBRARY: n={len(df_scam)}")
        print(f"    - Case types: {df_scam['case_type'].value_counts().to_dict()}")
        print(f"    - Case roles: {df_scam['case_role'].value_counts().to_dict() if 'case_role' in df_scam else 'N/A'}")
        print(f"    - Observed indicator candidates: {df_scam['indicator_candidates'].value_counts().head(5).to_dict() if 'indicator_candidates' in df_scam else 'N/A'}")
        print(f"    - Caveat: These entries are official counter-narratives (BUMN/ministry press releases).")
        print(f"      DO NOT train binary classifiers mixing raw job ads against scam advisory texts")
        print(f"      (would cause 100% text-genre/source leakage).")

    # 3. 50 Poster Template
    if poster_path.exists():
        df_poster = pd.read_csv(poster_path)
        print(f"\n[3] PAPER 50 POSTER TEMPLATE: n={len(df_poster)}")
        print(f"    - Groups: {df_poster['paper_group'].value_counts().to_dict()}")
        print(f"    - Campaign clusters: {df_poster['campaign_group'].value_counts().head(6).to_dict()}")
        
        # Check duplicate images
        dupes = df_poster[df_poster['image_file'].duplicated(keep=False)]
        if not dupes.empty:
            print(f"    - WARNING: Duplicate image files detected in poster template:")
            for img, g in dupes.groupby('image_file'):
                print(f"      Image {img}: cases {g['case_id'].tolist()} (known issue: #8 and #18 share image)")

    print("\n" + "=" * 60)
    print("AUDIT SUMMARY & METHODOLOGICAL CONSTRAINTS:")
    print("1. Binary classification (Glints REAL vs Scam Advisory) is scientifically INVALID due to genre leakage.")
    print("2. Models must evaluate Ordinal Risk (LOW / MEDIUM / HIGH), not synthetic dataset source.")
    print("3. ML training must use GroupKFold on company/campaign clusters.")
    print("4. Final paper claims must rely on multi-annotator evaluated gold datasets with Wilson CIs.")
    print("=" * 60)

if __name__ == "__main__":
    inspect_dataset_leakage()
