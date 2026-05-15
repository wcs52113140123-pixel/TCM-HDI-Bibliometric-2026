"""
Block 3A.1: Extract unique affiliation strings from integrated_corpus.

Splits multi-affiliation strings, deduplicates, and outputs a clean list
for ROR API matching. Also tracks which records each affiliation appears in.

Strategy:
- WoS: affiliations_raw contains "[Authors] Institution, City, Country." 
       repeated, separated by \n. Split on \n, strip [Authors] prefix.
- Scopus: affiliations_raw is "; "-separated list of full affiliations.
- OpenAlex: institutions_list is already structured; use display_name.
- PubMed: no affiliation data (0%); skipped.

Output:
- data/processed/unique_affiliations.parquet
    columns: affil_id, raw_string, normalized_string, n_records, sample_record_ids
- data/processed/affiliation_record_map.parquet
    columns: affil_id, record_id  (long format for later join)

Run:
    python 03_descriptive_analysis/05a_extract_unique_affiliations.py
"""

import re
import hashlib
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd


def normalize_affiliation(s: str) -> str:
    """Clean and normalize an affiliation string for matching/deduplication."""
    if not s:
        return ""
    # Strip [Author] prefix (WoS style)
    s = re.sub(r"^\[[^\]]+\]\s*", "", s).strip()
    # Strip trailing period
    s = s.rstrip(".")
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def split_wos_affiliations(text: str) -> list:
    """WoS C1 is newline-separated; each line is [Authors] Inst, City, Country."""
    if not text:
        return []
    parts = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            normalized = normalize_affiliation(line)
            if normalized:
                parts.append(normalized)
    return parts


def split_scopus_affiliations(text: str) -> list:
    """Scopus uses '; ' to separate affiliations."""
    if not text:
        return []
    parts = []
    for chunk in text.split(";"):
        chunk = chunk.strip()
        if chunk:
            normalized = normalize_affiliation(chunk)
            if normalized:
                parts.append(normalized)
    return parts


def get_affil_id(s: str) -> str:
    """Generate stable hash-based ID for an affiliation string."""
    return "AF_" + hashlib.md5(s.lower().encode("utf-8")).hexdigest()[:12]


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3A.1: Extract unique affiliations")
    print("=" * 70)
    
    # Load main + partial corpus
    print("\n[1] Loading corpus...")
    df_main = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    df_partial = pd.read_parquet(repo_root / "data/processed/integrated_corpus_partial2026.parquet")
    df = pd.concat([df_main, df_partial], ignore_index=True)
    print(f"    Combined: {len(df):,} records (main + partial)")
    
    # Extract affiliations per record
    print("\n[2] Extracting affiliations by source DB...")
    all_affil_strings = []  # list of (record_id, raw_string, source_db)
    
    for _, row in df.iterrows():
        rid = row["record_id"]
        db = row["source_db"]
        
        if db == "WoS":
            parts = split_wos_affiliations(row.get("affiliations_raw") or "")
        elif db == "Scopus":
            parts = split_scopus_affiliations(row.get("affiliations_raw") or "")
        elif db == "OpenAlex":
            # Use structured institutions_list — display_name is already clean
            insts = row.get("institutions_list")
            parts = []
            if insts is not None:
                try:
                    for inst in insts:
                        name = inst.get("name", "").strip() if isinstance(inst, dict) else ""
                        if name:
                            parts.append(name)
                except (TypeError, AttributeError):
                    pass
        else:  # PubMed
            parts = []
        
        # Deduplicate within a single record
        for p in set(parts):
            all_affil_strings.append((rid, p, db))
    
    print(f"    Total (record_id, affiliation) pairs: {len(all_affil_strings):,}")
    
    # Build unique affiliation set
    print("\n[3] Building unique affiliation set...")
    raw_counter = Counter()
    affil_to_records = defaultdict(set)
    
    for rid, raw, db in all_affil_strings:
        raw_counter[raw] += 1
        affil_to_records[raw].add(rid)
    
    print(f"    Unique affiliation strings: {len(raw_counter):,}")
    
    # Length distribution
    lens = [len(s) for s in raw_counter.keys()]
    print(f"    Length stats: min={min(lens)}, median={sorted(lens)[len(lens)//2]}, max={max(lens)}, mean={sum(lens)/len(lens):.0f}")
    
    # Top 10 most common
    print(f"\n[4] Top 10 most common affiliations:")
    for s, n in raw_counter.most_common(10):
        print(f"    {n:>4,}x  {s[:120]}")
    
    # Build output
    print("\n[5] Building output dataframes...")
    rows = []
    for raw, n in raw_counter.most_common():
        affil_id = get_affil_id(raw)
        record_ids = sorted(affil_to_records[raw])
        rows.append({
            "affil_id": affil_id,
            "raw_string": raw,
            "n_records": n,
            "sample_record_ids": "|".join(record_ids[:5]),
        })
    unique_df = pd.DataFrame(rows)
    
    # Record-affiliation mapping (long format)
    mapping_rows = []
    for rid, raw, db in all_affil_strings:
        mapping_rows.append({"record_id": rid, "affil_id": get_affil_id(raw), "source_db": db})
    map_df = pd.DataFrame(mapping_rows).drop_duplicates(["record_id", "affil_id"])
    
    # Save
    out_dir = repo_root / "data" / "processed"
    unique_path = out_dir / "unique_affiliations.parquet"
    map_path = out_dir / "affiliation_record_map.parquet"
    
    unique_df.to_parquet(unique_path, index=False, engine="pyarrow")
    map_df.to_parquet(map_path, index=False, engine="pyarrow")
    
    print(f"\n[6] Outputs saved:")
    print(f"    {unique_path}  ({unique_df.shape[0]:,} unique affiliations, {unique_path.stat().st_size/1024:.1f} KB)")
    print(f"    {map_path}  ({map_df.shape[0]:,} mappings, {map_path.stat().st_size/1024:.1f} KB)")
    
    # Summary by source_db
    print(f"\n[7] Mapping summary by source_db:")
    for db, sub in map_df.groupby("source_db"):
        print(f"    {db:10s}: {len(sub):,} (record, affil) pairs")
    
    print("\n" + "=" * 70)
    print(f"DONE: {len(raw_counter):,} unique affiliations ready for ROR API matching")
    print("=" * 70)


if __name__ == "__main__":
    main()
