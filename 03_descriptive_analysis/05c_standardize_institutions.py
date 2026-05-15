"""
Block 3A.3: Standardize all records' institutions using ROR results.

Reads ror_results.parquet (21,341 standardized affiliations) and applies
the mapping back to all 9,754 records via affiliation_record_map.

Output:
- data/processed/institution_lookup.parquet
    columns: record_id, source_db, institutions (list of ROR-canonical names),
             ror_ids (list of ROR IDs), institution_count
"""

from pathlib import Path
from collections import defaultdict

import pandas as pd


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3A.3: Standardize institutions using ROR results")
    print("=" * 70)
    
    # Load 3 inputs
    print("\n[1] Loading inputs...")
    corpus = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    partial = pd.read_parquet(repo_root / "data/processed/integrated_corpus_partial2026.parquet")
    df_records = pd.concat([corpus, partial], ignore_index=True)
    print(f"    Corpus records:           {len(df_records):,}")
    
    map_df = pd.read_parquet(repo_root / "data/processed/affiliation_record_map.parquet")
    print(f"    Record-affiliation map:   {len(map_df):,} pairs")
    
    ror = pd.read_parquet(repo_root / "data/processed/ror_results_fixed.parquet")
    print(f"    ROR results:              {len(ror):,} (matched: {ror['matched'].sum():,})")
    
    # Build affil_id -> (ror_name, ror_id) lookup
    print("\n[2] Building affil_id -> ROR lookup...")
    ror_matched = ror[ror["matched"] == True].copy()
    affil_to_ror = dict(zip(
        ror_matched["affil_id"],
        zip(ror_matched["ror_name"], ror_matched["ror_id"], ror_matched["ror_country"])
    ))
    print(f"    Lookup size: {len(affil_to_ror):,} matched affiliations")
    
    # For each record, aggregate institutions
    print("\n[3] Aggregating institutions per record...")
    record_to_insts = defaultdict(lambda: {"names": [], "ids": [], "countries": []})
    
    for _, row in map_df.iterrows():
        rid = row["record_id"]
        aid = row["affil_id"]
        if aid in affil_to_ror:
            name, ror_id, country = affil_to_ror[aid]
            record_to_insts[rid]["names"].append(name)
            record_to_insts[rid]["ids"].append(ror_id)
            if country:
                record_to_insts[rid]["countries"].append(country)
    
    # Deduplicate within each record (one institution can appear multiple times via different affiliations)
    print("\n[4] Deduplicating within-record institutions...")
    final_rows = []
    for rid, insts in record_to_insts.items():
        unique_names = list(dict.fromkeys(insts["names"]))  # preserve order, dedupe
        unique_ids = list(dict.fromkeys(insts["ids"]))
        unique_countries = sorted(set(insts["countries"]))
        final_rows.append({
            "record_id": rid,
            "institutions": unique_names,
            "ror_ids": unique_ids,
            "institution_count": len(unique_names),
            "countries_from_ror": unique_countries,
        })
    
    inst_lookup = pd.DataFrame(final_rows)
    
    # Stats
    n_records_with_inst = len(inst_lookup)
    n_total = len(df_records)
    print(f"\n[5] Coverage stats:")
    print(f"    Records with at least 1 institution: {n_records_with_inst:,}/{n_total:,} "
          f"({100*n_records_with_inst/n_total:.1f}%)")
    
    if n_records_with_inst > 0:
        avg_insts = inst_lookup["institution_count"].mean()
        print(f"    Average institutions per record:     {avg_insts:.2f}")
        print(f"    Single-institution records:          "
              f"{(inst_lookup['institution_count'] == 1).sum():,}")
        print(f"    Multi-institution records:           "
              f"{(inst_lookup['institution_count'] >= 2).sum():,}")
        print(f"    Max institutions in a record:        {inst_lookup['institution_count'].max()}")
    
    # Save
    out_path = repo_root / "data" / "processed" / "institution_lookup.parquet"
    inst_lookup.to_parquet(out_path, index=False, engine="pyarrow")
    print(f"\n[6] Saved: {out_path}")
    print(f"    File size: {out_path.stat().st_size / 1024:.1f} KB")
    
    print("\n" + "=" * 70)
    print("DONE: Ready for Block 3A.4 (Top 30 institutions ranking)")
    print("=" * 70)


if __name__ == "__main__":
    main()
