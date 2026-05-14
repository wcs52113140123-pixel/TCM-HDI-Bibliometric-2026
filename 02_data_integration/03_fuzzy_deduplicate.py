"""
Stage 3: Fuzzy title matching for DOI-less records.

After Stage 2 DOI deduplication, ~1,500 records lack DOI. Some of these are 
cross-database duplicates that fell through DOI matching (e.g., one DB indexed 
the article without DOI, another with). This stage uses fuzzy title matching 
to catch them.

Strategy (C-Standard from decisions.md):
- Threshold: title_normalized ratio >= 95 (bibliometrix default tol=0.95)
- Blocking key: (year, first_author_lastname) — 100x speedup, no precision loss
- For matched pairs: keep higher-priority DB (WoS > Scopus > PubMed > OpenAlex)
- Records without year OR without first_author treated as singletons

Output:
- data/processed/stage3_fuzzy_deduplicated.parquet
- data/processed/stage3_fuzzy_matches.csv  (audit of matched pairs)
- data/processed/stage3_summary.json

Usage:
    python 02_data_integration/03_fuzzy_deduplicate.py
    python 02_data_integration/03_fuzzy_deduplicate.py --partial-2026
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import pandas as pd
from fuzzywuzzy import fuzz

# Same priority as Stage 2
DB_PRIORITY = {"WoS": 0, "Scopus": 1, "PubMed": 2, "OpenAlex": 3}
FUZZY_THRESHOLD = 95  # bibliometrix default tol=0.95


def fuzzy_match_block(block_df, threshold=FUZZY_THRESHOLD):
    """
    Within a blocking group (same year + first_author), find fuzzy-matched pairs.
    Returns list of (idx_a, idx_b, ratio) tuples for ratio >= threshold.
    """
    matches = []
    indices = block_df.index.tolist()
    titles = block_df["title_normalized"].tolist()
    
    n = len(indices)
    for i in range(n):
        if not titles[i] or len(titles[i]) < 10:
            continue
        for j in range(i + 1, n):
            if not titles[j] or len(titles[j]) < 10:
                continue
            r = fuzz.ratio(titles[i], titles[j])
            if r >= threshold:
                matches.append((indices[i], indices[j], r))
    return matches


def merge_duplicate_records(stage2_df, fuzzy_matches):
    """
    Given fuzzy match pairs, merge duplicates:
    - For each connected component (cluster of matched records), keep 1 record
    - Priority: WoS > Scopus > PubMed > OpenAlex; tie-break by abstract length
    """
    # Union-Find for connected components
    parent = {}
    
    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x
    
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    
    for idx_a, idx_b, _ in fuzzy_matches:
        if idx_a not in parent:
            parent[idx_a] = idx_a
        if idx_b not in parent:
            parent[idx_b] = idx_b
        union(idx_a, idx_b)
    
    # Group records by component
    components = defaultdict(list)
    for idx in parent:
        components[find(idx)].append(idx)
    
    # For each component: pick the best record, mark others for removal
    indices_to_remove = set()
    merge_log = []
    
    for root, members in components.items():
        if len(members) < 2:
            continue
        
        sub = stage2_df.loc[members].copy()
        sub["_priority"] = sub["source_db"].map(DB_PRIORITY).fillna(99)
        sub["_abs_len"] = sub["abstract"].fillna("").str.len()
        sub_sorted = sub.sort_values(["_priority", "_abs_len"], ascending=[True, False])
        
        winner_idx = sub_sorted.index[0]
        losers = [idx for idx in members if idx != winner_idx]
        indices_to_remove.update(losers)
        
        merge_log.append({
            "winner_idx": winner_idx,
            "winner_db": stage2_df.loc[winner_idx, "source_db"],
            "winner_title": stage2_df.loc[winner_idx, "title"][:80],
            "year": stage2_df.loc[winner_idx, "year"],
            "first_author": stage2_df.loc[winner_idx, "first_author_lastname"],
            "n_merged": len(members),
            "loser_dbs": ";".join(stage2_df.loc[losers, "source_db"].tolist()),
        })
    
    return indices_to_remove, merge_log


def main(partial_2026=False):
    repo_root = Path(__file__).resolve().parent.parent
    in_dir = repo_root / "data" / "processed"
    suffix = "_partial2026" if partial_2026 else ""
    
    label = "PARTIAL 2026" if partial_2026 else "MAIN 2005-2025"
    print(f"\n{'='*70}")
    print(f"Stage 3: Fuzzy title matching for DOI-less records ({label})")
    print(f"Threshold: ratio >= {FUZZY_THRESHOLD}")
    print(f"{'='*70}\n")
    
    # Load Stage 2
    in_path = in_dir / f"stage2_doi_deduplicated{suffix}.parquet"
    print(f"[1] Loading: {in_path.name}")
    df = pd.read_parquet(in_path)
    print(f"    -> {len(df):,} records")
    
    # Subset: records without DOI (Stage 2 passed these through unchanged)
    no_doi_mask = df["doi"].isna() | (df["doi"].fillna("").str.strip().str.len() == 0)
    df_no_doi = df[no_doi_mask].copy()
    df_has_doi = df[~no_doi_mask].copy()
    
    print(f"\n[2] Splitting Stage 2 output:")
    print(f"    With DOI (already deduped): {len(df_has_doi):,}")
    print(f"    Without DOI (target for fuzzy):    {len(df_no_doi):,}")
    
    # Filter: must have title AND year AND first_author for fuzzy matching
    has_block_keys = (
        df_no_doi["year"].notna()
        & (df_no_doi["title_normalized"].fillna("").str.len() >= 10)
        & (df_no_doi["first_author_lastname"].fillna("").str.len() >= 2)
    )
    df_fuzzy = df_no_doi[has_block_keys].copy()
    df_pass = df_no_doi[~has_block_keys].copy()
    
    print(f"\n[3] DOI-less subset:")
    print(f"    Can be fuzzy-matched (has year + author + title): {len(df_fuzzy):,}")
    print(f"    Cannot be matched (missing block keys, keep as-is): {len(df_pass):,}")
    
    # Blocking
    print(f"\n[4] Building blocking groups (year + first_author)...")
    df_fuzzy["_block_key"] = (
        df_fuzzy["year"].astype("Int64").astype(str) 
        + "::" 
        + df_fuzzy["first_author_lastname"].str.lower().str.strip()
    )
    
    block_sizes = df_fuzzy.groupby("_block_key").size()
    multi_blocks = block_sizes[block_sizes >= 2]
    print(f"    Total blocks: {len(block_sizes):,}")
    print(f"    Blocks with >=2 records (candidates for matching): {len(multi_blocks):,}")
    print(f"    Total records in multi-blocks: {multi_blocks.sum():,}")
    
    # Fuzzy match within each multi-block
    print(f"\n[5] Running fuzzy matching within multi-blocks...")
    all_matches = []
    n_processed = 0
    for block_key, block_idx_series in df_fuzzy.groupby("_block_key").groups.items():
        if len(block_idx_series) < 2:
            continue
        block = df_fuzzy.loc[block_idx_series]
        matches = fuzzy_match_block(block, FUZZY_THRESHOLD)
        all_matches.extend(matches)
        n_processed += 1
        if n_processed % 100 == 0:
            print(f"    processed {n_processed:>4,} multi-blocks, {len(all_matches):>4,} pairs found")
    
    print(f"\n    Total fuzzy-matched pairs (ratio >= {FUZZY_THRESHOLD}): {len(all_matches):,}")
    
    # Merge duplicates
    print(f"\n[6] Resolving duplicate clusters...")
    indices_to_remove, merge_log = merge_duplicate_records(df_fuzzy, all_matches)
    print(f"    Duplicate clusters found: {len(merge_log):,}")
    print(f"    Records to remove: {len(indices_to_remove):,}")
    
    # Apply removal: keep df_fuzzy minus removed, plus df_pass, plus df_has_doi
    df_fuzzy_kept = df_fuzzy.drop(index=list(indices_to_remove))
    df_fuzzy_kept = df_fuzzy_kept.drop(columns=["_block_key"], errors="ignore")
    df_pass_clean = df_pass.drop(columns=["_block_key"], errors="ignore")
    
    df_final = pd.concat([df_has_doi, df_fuzzy_kept, df_pass_clean], ignore_index=True)
    
    print(f"\n[7] Stage 3 results:")
    print(f"    Records with DOI (preserved):       {len(df_has_doi):,}")
    print(f"    DOI-less, fuzzy-deduped (kept):     {len(df_fuzzy_kept):,}")
    print(f"    DOI-less, no block key (kept):      {len(df_pass_clean):,}")
    print(f"    TOTAL Stage 3:                      {len(df_final):,}")
    print(f"    Reduction from Stage 2:             {len(df) - len(df_final):,} "
          f"({100*(len(df)-len(df_final))/max(len(df),1):.2f}%)")
    
    # Save
    out_parquet = in_dir / f"stage3_fuzzy_deduplicated{suffix}.parquet"
    out_audit = in_dir / f"stage3_fuzzy_matches{suffix}.csv"
    out_summary = in_dir / f"stage3_summary{suffix}.json"
    
    print(f"\n[8] Saving outputs...")
    df_final.to_parquet(out_parquet, index=False, engine="pyarrow")
    print(f"    {out_parquet.name} ({out_parquet.stat().st_size/1024/1024:.1f} MB)")
    
    pd.DataFrame(merge_log).to_csv(out_audit, index=False, encoding="utf-8")
    print(f"    {out_audit.name} ({out_audit.stat().st_size/1024:.1f} KB)")
    
    summary = {
        "label": label,
        "generated_at": datetime.now().isoformat(),
        "threshold": FUZZY_THRESHOLD,
        "stage2_input": len(df),
        "with_doi_preserved": len(df_has_doi),
        "without_doi_fuzzy_input": len(df_fuzzy),
        "without_doi_kept_as_is": len(df_pass),
        "fuzzy_pairs_found": len(all_matches),
        "duplicate_clusters": len(merge_log),
        "records_removed": len(indices_to_remove),
        "stage3_output": len(df_final),
    }
    with open(out_summary, "w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2, ensure_ascii=False, default=str)
    print(f"    {out_summary.name}")
    
    print(f"\n{'='*70}")
    print(f"DONE: {len(df):,} -> {len(df_final):,} records "
          f"(removed {len(indices_to_remove)} fuzzy duplicates)")
    print(f"{'='*70}")
    
    return df_final


if __name__ == "__main__":
    partial = "--partial-2026" in sys.argv
    main(partial_2026=partial)
