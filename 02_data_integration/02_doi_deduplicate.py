"""
Stage 2: DOI primary-key deduplication.

Strategy:
- For records WITH DOI: group by normalized DOI; keep the "best" record per group.
- For records WITHOUT DOI: pass through unchanged (will be handled in Stage 3 fuzzy matching).
- Track all source_db memberships in source_db_list field for audit.

Priority for "best record" selection (when multiple records share same DOI):
1. WoS (most complete bibliographic + citation data)
2. Scopus (most complete abstract + references)
3. PubMed (NLM curated, has MeSH)
4. OpenAlex (CC0, has concepts but lower abstract coverage)

Output:
- data/processed/stage2_doi_deduplicated.parquet
- data/processed/stage2_dedup_audit.csv (per-DOI: which DBs had it)
- data/processed/stage2_summary.json

Usage:
    python 02_data_integration/02_doi_deduplicate.py
    python 02_data_integration/02_doi_deduplicate.py --partial-2026
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

import pandas as pd

# Priority order (lower index = higher priority)
DB_PRIORITY = {"WoS": 0, "Scopus": 1, "PubMed": 2, "OpenAlex": 3}


def select_best_per_doi_group(group_df):
    """
    From a DataFrame of records sharing the same DOI, pick the 'best' one.
    
    Strategy:
    1. Sort by DB priority (WoS > Scopus > PubMed > OpenAlex)
    2. Within same DB, prefer the one with longer abstract (richer metadata)
    3. Return the single best row, but enrich it with cross-DB info
    """
    # Add priority column
    g = group_df.copy()
    g["_priority"] = g["source_db"].map(DB_PRIORITY).fillna(99)
    g["_abs_len"] = g["abstract"].fillna("").str.len()
    
    # Sort: priority asc, abstract length desc
    g_sorted = g.sort_values(["_priority", "_abs_len"], ascending=[True, False])
    
    # Best record (top row)
    best = g_sorted.iloc[0].copy()
    
    # Enrich: which DBs had this DOI
    db_list = sorted(g["source_db"].unique().tolist())
    best["source_db_list"] = db_list
    best["source_db_count"] = len(db_list)
    
    # Collect all source_ids for cross-reference
    best["source_id_list"] = [
        f"{db}:{sid}" for db, sid in zip(g["source_db"], g["source_id"])
    ]
    
    # Combine MeSH from PubMed (if available)
    mesh_pubmed = g[g["source_db"] == "PubMed"]["mesh_terms"].tolist()
    if mesh_pubmed and isinstance(mesh_pubmed[0], list) and mesh_pubmed[0]:
        best["mesh_terms"] = mesh_pubmed[0]
    
    # Combine OpenAlex concepts (if available)
    concepts_oa = g[g["source_db"] == "OpenAlex"]["openalex_concepts"].tolist()
    if concepts_oa and isinstance(concepts_oa[0], list) and concepts_oa[0]:
        best["openalex_concepts"] = concepts_oa[0]
    
    # Use the most informative cited_by (max non-null)
    cb_vals = g["cited_by"].dropna()
    if len(cb_vals) > 0:
        best["cited_by"] = int(cb_vals.max())
    
    # Use the most informative references_count (max non-null)
    rc_vals = g["references_count"].dropna()
    if len(rc_vals) > 0:
        best["references_count"] = int(rc_vals.max())
    
    # Drop helper columns
    best = best.drop(["_priority", "_abs_len"], errors="ignore")
    
    return best


def main(partial_2026=False):
    repo_root = Path(__file__).resolve().parent.parent
    in_dir = repo_root / "data" / "processed"
    suffix = "_partial2026" if partial_2026 else ""
    
    label = "PARTIAL 2026" if partial_2026 else "MAIN 2005-2025"
    print(f"\n{'='*70}")
    print(f"Stage 2: DOI primary-key deduplication ({label})")
    print(f"{'='*70}\n")
    
    # Load Stage 1
    in_path = in_dir / f"stage1_raw_concatenated{suffix}.parquet"
    print(f"[1] Loading: {in_path.name}")
    df = pd.read_parquet(in_path)
    print(f"    -> {len(df):,} records loaded")
    
    # Split: with DOI vs without DOI
    has_doi = df["doi"].notna() & (df["doi"].str.strip().str.len() > 0)
    df_with_doi = df[has_doi].copy()
    df_without_doi = df[~has_doi].copy()
    
    print(f"\n[2] Splitting:")
    print(f"    With DOI:    {len(df_with_doi):,} ({100*len(df_with_doi)/len(df):.1f}%)")
    print(f"    Without DOI: {len(df_without_doi):,} ({100*len(df_without_doi)/len(df):.1f}%)")
    
    # DOI dedup
    print(f"\n[3] Grouping by DOI...")
    n_unique_dois = df_with_doi["doi"].nunique()
    print(f"    Unique DOIs: {n_unique_dois:,}")
    print(f"    Records to merge: {len(df_with_doi) - n_unique_dois:,}")
    
    # DOI duplicates distribution
    doi_counts = df_with_doi["doi"].value_counts()
    print(f"\n[4] DOI duplicate distribution (records per DOI):")
    dup_dist = doi_counts.value_counts().sort_index()
    for count, n in dup_dist.items():
        marker = " (singleton)" if count == 1 else f" (in {count} DBs)"
        print(f"    {count}x: {n:>5,} DOIs{marker}")
    
    # Apply dedup
    print(f"\n[5] Selecting best record per DOI group...")
    dedup_records = []
    audit_records = []
    for doi, group in df_with_doi.groupby("doi"):
        best = select_best_per_doi_group(group)
        dedup_records.append(best)
        
        # Audit log
        audit_records.append({
            "doi": doi,
            "n_records_merged": len(group),
            "source_dbs": ";".join(sorted(group["source_db"].unique())),
            "chosen_db": best["source_db"],
            "chosen_record_id": best["record_id"],
            "year": best.get("year"),
            "title_first50": (best["title"][:50] if best["title"] else ""),
        })
    
    df_dedup = pd.DataFrame(dedup_records)
    
    # For records WITHOUT DOI: add dummy source_db_list field for schema consistency
    df_without_doi["source_db_list"] = df_without_doi["source_db"].apply(lambda x: [x])
    df_without_doi["source_db_count"] = 1
    df_without_doi["source_id_list"] = df_without_doi.apply(
        lambda r: [f"{r['source_db']}:{r['source_id']}"], axis=1
    )
    
    # Combine
    df_final = pd.concat([df_dedup, df_without_doi], ignore_index=True)
    print(f"\n[6] After DOI dedup:")
    print(f"    DOI-matched unique: {len(df_dedup):,}")
    print(f"    Non-DOI (passed through): {len(df_without_doi):,}")
    print(f"    TOTAL Stage 2:       {len(df_final):,}")
    print(f"    Reduction from Stage 1: {len(df) - len(df_final):,} "
          f"({100*(len(df)-len(df_final))/len(df):.1f}%)")
    
    # Cross-DB overlap analysis
    print(f"\n[7] Cross-database overlap (DOI-matched records):")
    overlap_counter = Counter()
    for db_list in df_dedup["source_db_list"]:
        if isinstance(db_list, list):
            key = "+".join(sorted(db_list))
            overlap_counter[key] += 1
    for combo, n in overlap_counter.most_common(15):
        print(f"    {combo:40s} {n:>5,}")
    
    # Save
    out_parquet = in_dir / f"stage2_doi_deduplicated{suffix}.parquet"
    out_audit = in_dir / f"stage2_dedup_audit{suffix}.csv"
    out_summary = in_dir / f"stage2_summary{suffix}.json"
    
    print(f"\n[8] Saving outputs...")
    df_final.to_parquet(out_parquet, index=False, engine="pyarrow")
    print(f"    {out_parquet.name} ({out_parquet.stat().st_size/1024/1024:.1f} MB)")
    
    pd.DataFrame(audit_records).to_csv(out_audit, index=False, encoding="utf-8")
    print(f"    {out_audit.name} ({out_audit.stat().st_size/1024:.1f} KB)")
    
    summary = {
        "label": label,
        "generated_at": datetime.now().isoformat(),
        "input_records": len(df),
        "with_doi": len(df_with_doi),
        "without_doi": len(df_without_doi),
        "unique_dois": n_unique_dois,
        "doi_duplicates_removed": len(df_with_doi) - n_unique_dois,
        "output_records": len(df_final),
        "reduction_pct": round(100*(len(df)-len(df_final))/len(df), 2),
        "cross_db_overlap": dict(overlap_counter),
    }
    with open(out_summary, "w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2, ensure_ascii=False, default=str)
    print(f"    {out_summary.name}")
    
    print(f"\n{'='*70}")
    print(f"DONE: {len(df):,} -> {len(df_final):,} records "
          f"(removed {len(df) - len(df_final):,} DOI duplicates)")
    print(f"{'='*70}")
    
    return df_final


if __name__ == "__main__":
    partial = "--partial-2026" in sys.argv
    main(partial_2026=partial)
