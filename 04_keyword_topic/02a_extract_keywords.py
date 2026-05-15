"""
Day 4 Block 2.1: Extract and basic-normalize all keywords.

Builds a keyword inventory across 3 sources (author_keywords, keywords_plus, 
mesh_terms) with basic normalization. Outputs a thesaurus-suggestion file
for manual review in Block 2.2.

Normalization steps:
1. Lowercase
2. Strip whitespace, punctuation
3. Normalize dashes (— – – → -)
4. Drop trailing modifiers ([*therapeutic use], [genetics], etc.)
5. Singular/plural handling: leave for later thesaurus

Output:
- data/processed/keywords_raw.parquet (long format: record_id, source, raw, normalized)
- data/processed/keyword_inventory.csv (frequency table for manual review)
"""

import re
import unicodedata
from pathlib import Path
from collections import Counter

import pandas as pd


def normalize_dashes(s):
    """Convert various Unicode dashes to ASCII hyphen."""
    if not isinstance(s, str):
        return s
    dashes = ["–", "—", "−", "‒", "‐", "—"]
    for d in dashes:
        s = s.replace(d, "-")
    return s


def basic_normalize(s):
    """Basic keyword normalization. Returns normalized string or None if invalid."""
    if not isinstance(s, str):
        return None
    
    # Unicode normalize (NFD then re-compose, handles é/è issues)
    s = unicodedata.normalize("NFKC", s)
    
    # Lowercase + strip
    s = s.strip().lower()
    
    # Normalize dashes
    s = normalize_dashes(s)
    
    # Remove MeSH-style trailing modifiers: [*therapeutic use], [genetics], etc.
    s = re.sub(r"\[[^\]]*\]", "", s)
    
    # Collapse multiple whitespace
    s = re.sub(r"\s+", " ", s)
    
    # Strip trailing/leading punctuation
    s = s.strip(" ,.;:/\\\"'*")
    
    # Filter out garbage
    if len(s) < 3:
        return None
    if s.isdigit():
        return None
    if not re.search(r"[a-z]", s):
        return None
    
    return s


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 2.1: Extract + basic normalize keywords")
    print("=" * 70)
    
    # Load corpus
    print("\n[1] Loading corpus...")
    df_main = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    df_partial = pd.read_parquet(repo_root / "data/processed/integrated_corpus_partial2026.parquet")
    df = pd.concat([df_main, df_partial], ignore_index=True)
    print(f"    Total records: {len(df):,}")
    
    # Extract keywords from 3 sources
    print("\n[2] Extracting + normalizing keywords...")
    keyword_rows = []
    parse_failures = []
    
    for _, row in df.iterrows():
        rid = row["record_id"]
        
        for source_col in ["author_keywords", "keywords_plus", "mesh_terms"]:
            raw_list = row.get(source_col)
            if raw_list is None:
                continue
            # D' policy: drop Scopus keywords_plus (mixed indexing content)
            if source_col == "keywords_plus" and row.get("source_db") == "Scopus":
                continue
            try:
                items = list(raw_list)
            except (TypeError, ValueError):
                continue
            
            for raw in items:
                if not raw:
                    continue
                normalized = basic_normalize(str(raw))
                if normalized:
                    keyword_rows.append({
                        "record_id": rid,
                        "source": source_col,
                        "raw": str(raw),
                        "normalized": normalized,
                    })
                else:
                    parse_failures.append(str(raw))
    
    kw_df = pd.DataFrame(keyword_rows)
    print(f"    Total (record, keyword) pairs: {len(kw_df):,}")
    print(f"    Parse failures (filtered out): {len(parse_failures):,}")
    
    # Per source breakdown
    print(f"\n[3] By source (after normalization):")
    for src, sub in kw_df.groupby("source"):
        n_records = sub["record_id"].nunique()
        n_unique = sub["normalized"].nunique()
        print(f"    {src:20s} {len(sub):>7,} pairs, {n_records:>5,} records, {n_unique:>5,} unique keywords")
    
    # Save raw
    out_dir = repo_root / "data" / "processed"
    kw_path = out_dir / "keywords_raw.parquet"
    kw_df.to_parquet(kw_path, index=False, engine="pyarrow")
    print(f"\n[4] Saved long-format keywords: {kw_path}")
    
    # Build inventory (frequency table for thesaurus building)
    print(f"\n[5] Building keyword inventory...")
    
    # Count records per (source, normalized) — record-level, not occurrence-level
    inventory = (
        kw_df.drop_duplicates(["record_id", "source", "normalized"])
        .groupby(["normalized", "source"])
        .agg(n_records=("record_id", "count"))
        .reset_index()
    )
    
    # Pivot to wide format: one row per normalized, columns for each source's count
    pivoted = inventory.pivot(index="normalized", columns="source", values="n_records").fillna(0).astype(int)
    pivoted["total"] = pivoted.sum(axis=1)
    pivoted = pivoted.sort_values("total", ascending=False).reset_index()
    
    # Sample top entries
    print(f"\n    Total unique normalized keywords: {len(pivoted):,}")
    print(f"\n    Top 30 most frequent (by total record count):")
    print(f"    {'Rank':<5} {'Total':>6} {'Auth':>5} {'K+':>5} {'MeSH':>5}  Keyword")
    for i, row in pivoted.head(30).iterrows():
        ak = int(row.get('author_keywords', 0))
        kp = int(row.get('keywords_plus', 0))
        mh = int(row.get('mesh_terms', 0))
        print(f"    {i+1:<5} {int(row['total']):>6} {ak:>5} {kp:>5} {mh:>5}  {row['normalized']}")
    
    # Save inventory
    inv_path = out_dir / "keyword_inventory.csv"
    pivoted.to_csv(inv_path, index=False, encoding="utf-8")
    print(f"\n[6] Saved inventory for thesaurus review: {inv_path}")
    print(f"    File size: {inv_path.stat().st_size / 1024:.1f} KB")
    
    print("\n" + "=" * 70)
    print("NEXT: Block 2.2 will analyze top keywords + suggest thesaurus entries")
    print("=" * 70)


if __name__ == "__main__":
    main()
