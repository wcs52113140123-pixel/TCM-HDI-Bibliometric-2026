"""
Stage 5 (FINAL): Build integrated corpus + PRISMA flow data.

This is the final stage of Day 2 integration. It:
1. Reads Stage 4 output (quality-filtered)
2. Cleans/standardizes final columns
3. Saves the FINAL integrated corpus as `integrated_corpus.parquet`
4. Builds PRISMA flow JSON (for Day 4 Figure 1)

The integrated_corpus.parquet is the SOLE INPUT for all Day 3-21 analyses.

Output:
- data/processed/integrated_corpus.parquet              (FINAL, main)
- data/processed/integrated_corpus_partial2026.parquet  (FINAL, partial)
- data/processed/prisma_flow_data.json                  (Figure 1 data)
- data/processed/integration_summary.md                 (human-readable summary)

Usage:
    python 02_data_integration/05_finalize.py
    python 02_data_integration/05_finalize.py --partial-2026
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

import pandas as pd


def build_prisma_flow(repo_root, partial_2026=False):
    """Read all stage summaries and build the PRISMA flow data."""
    in_dir = repo_root / "data" / "processed"
    suffix = "_partial2026" if partial_2026 else ""
    
    flow = {
        "label": "PARTIAL 2026" if partial_2026 else "MAIN 2005-2025",
        "generated_at": datetime.now().isoformat(),
    }
    
    # Stage 1: identification
    s1_path = in_dir / f"stage1_summary{suffix}.json"
    if s1_path.exists():
        with open(s1_path, encoding="utf-8") as fp:
            s1 = json.load(fp)
        flow["identification"] = {
            "WoS_raw": s1.get("WoS", {}).get("n_records", 0),
            "Scopus_raw": s1.get("Scopus", {}).get("n_records", 0),
            "OpenAlex_raw": s1.get("OpenAlex", {}).get("n_records", 0),
            "PubMed_raw": s1.get("PubMed", {}).get("n_records", 0),
            "total_raw": s1.get("TOTAL", {}).get("n_records", 0),
        }
    
    # Stage 2: DOI dedup
    s2_path = in_dir / f"stage2_summary{suffix}.json"
    if s2_path.exists():
        with open(s2_path, encoding="utf-8") as fp:
            s2 = json.load(fp)
        flow["doi_deduplication"] = {
            "input": s2.get("input_records", 0),
            "with_doi": s2.get("with_doi", 0),
            "without_doi": s2.get("without_doi", 0),
            "unique_dois": s2.get("unique_dois", 0),
            "duplicates_removed": s2.get("doi_duplicates_removed", 0),
            "output": s2.get("output_records", 0),
        }
    
    # Stage 3: fuzzy
    s3_path = in_dir / f"stage3_summary{suffix}.json"
    if s3_path.exists():
        with open(s3_path, encoding="utf-8") as fp:
            s3 = json.load(fp)
        flow["fuzzy_deduplication"] = {
            "input": s3.get("stage2_input", 0),
            "threshold": s3.get("threshold", 95),
            "fuzzy_pairs_found": s3.get("fuzzy_pairs_found", 0),
            "duplicate_clusters": s3.get("duplicate_clusters", 0),
            "records_removed": s3.get("records_removed", 0),
            "output": s3.get("stage3_output", 0),
        }
    
    # Stage 4: precision filter
    s4_path = in_dir / f"stage4_summary{suffix}.json"
    if s4_path.exists():
        with open(s4_path, encoding="utf-8") as fp:
            s4 = json.load(fp)
        flow["precision_filter"] = {
            "input": s4.get("stage3_input", 0),
            "openalex_exclusive": s4.get("openalex_exclusive_count", 0),
            "openalex_passed_B1B2B3": s4.get("openalex_exclusive_passed", 0),
            "openalex_dropped_no_match": s4.get("openalex_exclusive_dropped", 0),
            "block_breakdown": s4.get("block_breakdown", {}),
            "output": s4.get("stage4_output", 0),
        }
    
    # Final
    flow["final_corpus_size"] = flow.get("precision_filter", {}).get("output", 0)
    
    return flow


def main(partial_2026=False):
    repo_root = Path(__file__).resolve().parent.parent
    in_dir = repo_root / "data" / "processed"
    suffix = "_partial2026" if partial_2026 else ""
    
    label = "PARTIAL 2026" if partial_2026 else "MAIN 2005-2025"
    print(f"\n{'='*70}")
    print(f"Stage 5 (FINAL): Build integrated corpus ({label})")
    print(f"{'='*70}\n")
    
    # Load Stage 4
    in_path = in_dir / f"stage4_quality_filtered{suffix}.parquet"
    print(f"[1] Loading: {in_path.name}")
    df = pd.read_parquet(in_path)
    print(f"    -> {len(df):,} records")
    
    # Standardize columns: ensure consistent types
    print(f"\n[2] Standardizing column types...")
    
    # Convert list-type ndarray columns back to Python lists (for downstream tools)
    list_cols = [
        "authors", "author_keywords", "keywords_plus", "mesh_terms",
        "openalex_concepts", "source_db_list", "source_id_list",
    ]
    for col in list_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: list(x) if x is not None and hasattr(x, "__iter__") and not isinstance(x, str) else []
            )
    
    # Year to nullable Int
    if "year" in df.columns:
        df["year"] = df["year"].astype("Int64")
    
    # Ensure key fields are not null
    df["title"] = df["title"].fillna("").astype(str)
    df["abstract"] = df["abstract"].fillna("").astype(str)
    df["first_author_lastname"] = df["first_author_lastname"].fillna("").astype(str)
    
    print(f"    Done. Columns: {len(df.columns)}")
    
    # Show year distribution
    print(f"\n[3] Year distribution:")
    yr_counts = df["year"].value_counts().sort_index()
    for yr, n in yr_counts.items():
        bar = "#" * int(n / max(yr_counts.max() / 40, 1))
        print(f"    {yr}: {n:>5,}  {bar}")
    
    # Doc type
    print(f"\n[4] Document type distribution:")
    for dt, n in df["doc_type"].value_counts().head(10).items():
        print(f"    {dt:30s} {n:>5,}")
    
    # Source DB distribution (primary db that "won" each record)
    print(f"\n[5] Primary source DB (the DB chosen during dedup):")
    for db, n in df["source_db"].value_counts().items():
        print(f"    {db:15s} {n:>5,}")
    
    # Cross-DB coverage analysis
    print(f"\n[6] Cross-DB coverage (in how many DBs was each record found?):")
    df["n_dbs"] = df["source_db_list"].apply(len)
    for nd, n in df["n_dbs"].value_counts().sort_index().items():
        marker = " (singleton — only 1 DB)" if nd == 1 else ""
        print(f"    {nd} DB(s): {n:>5,}{marker}")
    
    # Field coverage
    print(f"\n[7] Field coverage in final corpus:")
    n = len(df)
    cov = {
        "DOI": int(df["doi"].notna().sum()),
        "Abstract (>50 chars)": int((df["abstract"].str.len() > 50).sum()),
        "Year": int(df["year"].notna().sum()),
        "First author": int((df["first_author_lastname"].str.len() > 0).sum()),
        "MeSH (PubMed)": int(df["mesh_terms"].apply(lambda x: bool(x)).sum()),
        "Concepts (OpenAlex)": int(df["openalex_concepts"].apply(lambda x: bool(x)).sum()),
        "Cited by (numeric)": int(df["cited_by"].notna().sum()),
        "References # (numeric)": int(df["references_count"].notna().sum()),
    }
    for k, v in cov.items():
        print(f"    {k:25s} {v:>5,}/{n:,} ({100*v/n:.1f}%)")
    
    # Save final corpus
    out_corpus = in_dir / f"integrated_corpus{suffix}.parquet"
    print(f"\n[8] Saving final integrated corpus...")
    df_to_save = df.drop(columns=["n_dbs"], errors="ignore")
    df_to_save.to_parquet(out_corpus, index=False, engine="pyarrow")
    mb = out_corpus.stat().st_size / 1024 / 1024
    print(f"    {out_corpus.name} ({mb:.1f} MB)")
    
    # Build PRISMA flow data
    print(f"\n[9] Building PRISMA flow data...")
    flow = build_prisma_flow(repo_root, partial_2026=partial_2026)
    prisma_path = in_dir / f"prisma_flow_data{suffix}.json"
    with open(prisma_path, "w", encoding="utf-8") as fp:
        json.dump(flow, fp, indent=2, ensure_ascii=False, default=str)
    print(f"    {prisma_path.name}")
    
    # Build summary report
    if not partial_2026:
        report = build_summary_report(repo_root, df, flow)
        report_path = in_dir / "integration_summary.md"
        with open(report_path, "w", encoding="utf-8") as fp:
            fp.write(report)
        print(f"    {report_path.name}")
    
    print(f"\n{'='*70}")
    print(f"DAY 2 INTEGRATION COMPLETE")
    print(f"  Final corpus N:        {len(df):,}")
    print(f"  File:                  {out_corpus.name}")
    print(f"  PRISMA flow:           {prisma_path.name}")
    print(f"{'='*70}")
    
    return df


def build_summary_report(repo_root, df, flow):
    """Generate a human-readable Markdown report of Day 2 integration."""
    lines = []
    lines.append("# Day 2 Data Integration — Final Summary")
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("## PRISMA Flow")
    lines.append("")
    lines.append("### Identification")
    id_data = flow.get("identification", {})
    lines.append(f"- WoS:      {id_data.get('WoS_raw', 0):,} records")
    lines.append(f"- Scopus:   {id_data.get('Scopus_raw', 0):,} records")
    lines.append(f"- OpenAlex: {id_data.get('OpenAlex_raw', 0):,} records")
    lines.append(f"- PubMed:   {id_data.get('PubMed_raw', 0):,} records")
    lines.append(f"- **Total raw: {id_data.get('total_raw', 0):,}**")
    lines.append("")
    
    lines.append("### Stage 2: DOI Primary-Key Deduplication")
    s2 = flow.get("doi_deduplication", {})
    lines.append(f"- Input: {s2.get('input', 0):,}")
    lines.append(f"- With DOI: {s2.get('with_doi', 0):,}")
    lines.append(f"- Without DOI: {s2.get('without_doi', 0):,}")
    lines.append(f"- Unique DOIs: {s2.get('unique_dois', 0):,}")
    lines.append(f"- Duplicates removed: {s2.get('duplicates_removed', 0):,}")
    lines.append(f"- **Output: {s2.get('output', 0):,}**")
    lines.append("")
    
    lines.append("### Stage 3: Fuzzy Title Matching (ratio >= 95)")
    s3 = flow.get("fuzzy_deduplication", {})
    lines.append(f"- Input: {s3.get('input', 0):,}")
    lines.append(f"- Threshold: {s3.get('threshold', 95)} (bibliometrix default tol=0.95)")
    lines.append(f"- Blocking key: year + first_author_lastname")
    lines.append(f"- Fuzzy pairs found: {s3.get('fuzzy_pairs_found', 0):,}")
    lines.append(f"- Duplicate clusters: {s3.get('duplicate_clusters', 0):,}")
    lines.append(f"- Records removed: {s3.get('records_removed', 0):,}")
    lines.append(f"- **Output: {s3.get('output', 0):,}**")
    lines.append("")
    
    lines.append("### Stage 4: OpenAlex Client-Side Precision Filter (B1)")
    s4 = flow.get("precision_filter", {})
    lines.append(f"- Input: {s4.get('input', 0):,}")
    lines.append(f"- OpenAlex exclusives: {s4.get('openalex_exclusive', 0):,}")
    lines.append(f"- Passed (matched B1/B2/B3): {s4.get('openalex_passed_B1B2B3', 0):,}")
    lines.append(f"- Dropped (no block matched): {s4.get('openalex_dropped_no_match', 0):,}")
    lines.append(f"- Block breakdown: {s4.get('block_breakdown', {})}")
    lines.append(f"- **Output: {s4.get('output', 0):,}**")
    lines.append("")
    
    lines.append("## Final Corpus")
    lines.append("")
    lines.append(f"- **N = {len(df):,} unique TCM-HDI publications (2005-2025)**")
    lines.append(f"- File: `data/processed/integrated_corpus.parquet`")
    lines.append("")
    lines.append("### Field Coverage")
    n = len(df)
    cov_items = [
        ("DOI", int(df["doi"].notna().sum())),
        ("Abstract >50 chars", int((df["abstract"].str.len() > 50).sum())),
        ("Year", int(df["year"].notna().sum())),
        ("First author", int((df["first_author_lastname"].str.len() > 0).sum())),
        ("MeSH (PubMed)", int(df["mesh_terms"].apply(lambda x: bool(x)).sum())),
        ("Concepts (OpenAlex)", int(df["openalex_concepts"].apply(lambda x: bool(x)).sum())),
    ]
    for k, v in cov_items:
        lines.append(f"- {k}: {v:,}/{n:,} ({100*v/n:.1f}%)")
    lines.append("")
    
    lines.append("### Year Distribution")
    yr = df["year"].value_counts().sort_index()
    for y, n_y in yr.items():
        lines.append(f"- {y}: {n_y:,}")
    lines.append("")
    
    lines.append("### Cross-Database Coverage")
    lines.append("")
    lines.append("Records found in N databases (higher N = higher confidence):")
    n_dbs_dist = df["source_db_list"].apply(len).value_counts().sort_index()
    for nd, count in n_dbs_dist.items():
        pct = 100 * count / n
        lines.append(f"- {nd} DB(s): {count:,} ({pct:.1f}%)")
    lines.append("")
    
    lines.append("## Decisions Applied")
    lines.append("")
    lines.append("- **A1**: DOI-less records kept; matched via fuzzy title + year + first_author (PRISMA-S standard)")
    lines.append("- **B1**: OpenAlex-exclusive records filtered using WoS-equivalent 3-block logic")
    lines.append("- **C-Standard**: Fuzzy threshold ratio>=95 (bibliometrix default tol=0.95)")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    partial = "--partial-2026" in sys.argv
    main(partial_2026=partial)
