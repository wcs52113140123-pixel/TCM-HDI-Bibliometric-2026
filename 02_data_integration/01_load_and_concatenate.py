"""
Stage 1: Load and concatenate 4 databases into a unified DataFrame.

Reads 4 normalized loaders (WoS, Scopus, OpenAlex, PubMed), concatenates into 
a single DataFrame with unified schema, adds derived fields (normalized title 
for fuzzy matching, unique record_id), saves to parquet.

Output:
- data/processed/stage1_raw_concatenated.parquet      (main analysis)
- data/processed/stage1_summary.json                  (counts + coverage)

Usage:
    conda activate tcm-hdi
    python 02_data_integration/01_load_and_concatenate.py
    python 02_data_integration/01_load_and_concatenate.py --partial-2026
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_wos import load_all_wos
from load_scopus import load_all_scopus
from load_openalex import load_all_openalex
from load_pubmed import load_all_pubmed


def normalize_title_for_fuzzy(title):
    """Normalize title for fuzzy matching: lowercase, strip prefixes, remove punct."""
    if not title:
        return ""
    t = title.lower().strip()
    for prefix in [
        "ethnopharmacological relevance:", "abstract:", "background:",
        "introduction:", "objective:", "purpose:",
    ]:
        if t.startswith(prefix):
            t = t[len(prefix):].strip()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main(partial_2026=False):
    repo_root = Path(__file__).resolve().parent.parent
    
    label = "PARTIAL 2026" if partial_2026 else "MAIN 2005-2025"
    print(f"\n{'='*70}")
    print(f"Stage 1: Load + concatenate 4 databases ({label})")
    print(f"{'='*70}\n")
    
    print("[1] Loading WoS...")
    wos_recs = load_all_wos(repo_root, partial_2026=partial_2026)
    print(f"    -> {len(wos_recs):,} records\n")
    
    print("[2] Loading Scopus...")
    scopus_recs = load_all_scopus(repo_root, partial_2026=partial_2026)
    print(f"    -> {len(scopus_recs):,} records\n")
    
    print("[3] Loading OpenAlex...")
    openalex_recs = load_all_openalex(repo_root, partial_2026=partial_2026)
    print(f"    -> {len(openalex_recs):,} records\n")
    
    print("[4] Loading PubMed...")
    pubmed_recs = load_all_pubmed(repo_root, partial_2026=partial_2026)
    print(f"    -> {len(pubmed_recs):,} records\n")
    
    all_records = wos_recs + scopus_recs + openalex_recs + pubmed_recs
    print(f"[5] Total concatenated: {len(all_records):,}")
    
    print("\n[6] Adding derived fields (title_normalized, record_id)...")
    for rec in all_records:
        rec["title_normalized"] = normalize_title_for_fuzzy(rec["title"])
        rec["record_id"] = f"{rec['source_db']}:{rec['source_id']}"
    
    print("[7] Converting to pandas DataFrame...")
    df = pd.DataFrame(all_records)
    
    primary_cols = [
        "record_id", "source_db", "source_id",
        "doi", "title", "title_normalized", "year",
        "first_author_lastname", "authors",
        "journal", "abstract", "doc_type", "language",
        "cited_by", "references_count",
        "author_keywords", "keywords_plus",
        "mesh_terms", "openalex_concepts",
    ]
    cols = [c for c in primary_cols if c in df.columns] + \
           [c for c in df.columns if c not in primary_cols]
    df = df[cols]
    
    print(f"\n[8] Summary by database:")
    summary = {"label": label, "generated_at": datetime.now().isoformat()}
    for db in ["WoS", "Scopus", "OpenAlex", "PubMed"]:
        sub = df[df["source_db"] == db]
        n = len(sub)
        if n == 0:
            continue
        n_doi = int(sub["doi"].notna().sum())
        n_abs = int((sub["abstract"].fillna("").str.len() > 50).sum())
        n_yr = int(sub["year"].notna().sum())
        n_aut = int(sub["first_author_lastname"].fillna("").str.len().gt(0).sum())
        s = {
            "n_records": n,
            "n_with_doi": n_doi,
            "doi_coverage_pct": round(100 * n_doi / n, 1),
            "n_with_abstract": n_abs,
            "abstract_coverage_pct": round(100 * n_abs / n, 1),
            "n_with_year": n_yr,
            "n_with_first_author": n_aut,
        }
        summary[db] = s
        print(f"   {db:10s}: N={n:,}  DOI={s['doi_coverage_pct']}%  "
              f"Abs={s['abstract_coverage_pct']}%  Yr={n_yr}  Author={n_aut}")
    summary["TOTAL"] = {"n_records": len(df)}
    
    out_dir = repo_root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    suffix = "_partial2026" if partial_2026 else ""
    parquet_path = out_dir / f"stage1_raw_concatenated{suffix}.parquet"
    summary_path = out_dir / f"stage1_summary{suffix}.json"
    
    print(f"\n[9] Saving to {parquet_path.name}...")
    df.to_parquet(parquet_path, index=False, engine="pyarrow")
    mb = parquet_path.stat().st_size / 1024 / 1024
    print(f"    Size: {mb:.1f} MB")
    
    with open(summary_path, "w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2, ensure_ascii=False)
    print(f"    Summary: {summary_path.name}")
    
    print(f"\n{'='*70}")
    print(f"DONE: {len(df):,} records concatenated and saved")
    print(f"  WoS:      {summary.get('WoS', {}).get('n_records', 0):,}")
    print(f"  Scopus:   {summary.get('Scopus', {}).get('n_records', 0):,}")
    print(f"  OpenAlex: {summary.get('OpenAlex', {}).get('n_records', 0):,}")
    print(f"  PubMed:   {summary.get('PubMed', {}).get('n_records', 0):,}")
    print(f"  TOTAL:    {len(df):,}")
    print(f"{'='*70}")
    
    return df


if __name__ == "__main__":
    partial = "--partial-2026" in sys.argv
    main(partial_2026=partial)
