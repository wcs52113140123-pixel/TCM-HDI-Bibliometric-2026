"""
Day 4 Block 2.3: Apply thesaurus + stopwords to keywords_raw.

Produces the final, standardized keyword data ready for Top N analysis 
and co-occurrence networks.

Pipeline:
1. Load keywords_raw.parquet (long format with normalized column)
2. Load thesaurus_suggestions.csv and stopwords_suggestions.csv
3. For each keyword:
   a. If in stopwords -> drop
   b. If in thesaurus -> replace with canonical
4. Re-aggregate; dedupe at (record_id, source, canonical_keyword) level
5. Output:
   - data/processed/keywords_final.parquet (long format)
   - data/processed/keyword_record_map.parquet (for co-occurrence)
   - data/processed/keyword_lookup.parquet (frequency stats)
"""

from pathlib import Path

import pandas as pd


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 2.3: Apply thesaurus + stopwords")
    print("=" * 70)
    
    # Load inputs
    print("\n[1] Loading inputs...")
    kw_raw = pd.read_parquet(repo_root / "data/processed/keywords_raw.parquet")
    thesaurus = pd.read_csv(repo_root / "data/processed/thesaurus_suggestions.csv")
    stopwords_df = pd.read_csv(repo_root / "data/processed/stopwords_suggestions.csv")
    
    print(f"    Raw keyword pairs:   {len(kw_raw):,}")
    print(f"    Thesaurus entries:   {len(thesaurus):,}")
    print(f"    Stopword entries:    {len(stopwords_df):,}")
    
    # Filter to MERGE/DROP decisions only
    thesaurus = thesaurus[thesaurus["decision"] == "MERGE"]
    stopwords = set(stopwords_df[stopwords_df["decision"] == "DROP"]["keyword"].tolist())
    
    # Build variant -> canonical map
    variant_map = dict(zip(thesaurus["variant"], thesaurus["canonical"]))
    print(f"\n    Active thesaurus rules: {len(variant_map)}")
    print(f"    Active stopwords:       {len(stopwords)}")
    
    # ============ Apply transformations ============
    print("\n[2] Applying stopword filter + thesaurus...")
    
    kw_raw["after_thesaurus"] = kw_raw["normalized"].apply(
        lambda x: variant_map.get(x, x)
    )
    kw_raw["is_stopword"] = kw_raw["after_thesaurus"].isin(stopwords)
    
    # Drop stopwords
    kw_clean = kw_raw[~kw_raw["is_stopword"]].copy()
    kw_clean["final"] = kw_clean["after_thesaurus"]
    
    print(f"    Pairs dropped (stopword):  {kw_raw['is_stopword'].sum():,}")
    print(f"    Pairs after cleaning:      {len(kw_clean):,}")
    
    # ============ Dedupe within record ============
    # Same (record_id, source, canonical) → keep one
    print("\n[3] Deduplicating within (record_id, source, canonical)...")
    kw_clean = kw_clean.drop_duplicates(["record_id", "source", "final"])
    print(f"    After dedup:               {len(kw_clean):,}")
    
    # ============ Build outputs ============
    
    # Output 1: keywords_final.parquet (long format)
    out_final = kw_clean[["record_id", "source", "final"]].rename(
        columns={"final": "keyword"}
    )
    out_path1 = repo_root / "data/processed/keywords_final.parquet"
    out_final.to_parquet(out_path1, index=False, engine="pyarrow")
    print(f"\n[4] Saved long-format: {out_path1}")
    
    # Output 2: keyword_record_map.parquet (just record_id + keyword, no source)
    record_kw_map = (
        out_final[["record_id", "keyword"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    out_path2 = repo_root / "data/processed/keyword_record_map.parquet"
    record_kw_map.to_parquet(out_path2, index=False, engine="pyarrow")
    print(f"    Saved record-keyword map: {out_path2}")
    
    # Output 3: keyword_lookup.parquet (frequency stats)
    lookup = (
        record_kw_map.groupby("keyword")
        .agg(n_records=("record_id", "count"))
        .sort_values("n_records", ascending=False)
        .reset_index()
    )
    
    # Add by-source breakdown
    src_breakdown = (
        out_final.drop_duplicates(["record_id", "source", "keyword"])
        .groupby(["keyword", "source"])
        .size()
        .unstack(fill_value=0)
    )
    src_breakdown.columns = [f"n_{col}" for col in src_breakdown.columns]
    lookup = lookup.merge(src_breakdown, on="keyword", how="left").fillna(0)
    for c in src_breakdown.columns:
        lookup[c] = lookup[c].astype(int)
    lookup["rank"] = range(1, len(lookup) + 1)
    
    out_path3 = repo_root / "data/processed/keyword_lookup.parquet"
    lookup.to_parquet(out_path3, index=False, engine="pyarrow")
    print(f"    Saved keyword lookup:     {out_path3}")
    
    # ============ Summary stats ============
    print(f"\n[5] Final keyword statistics:")
    print(f"    Total unique keywords:        {len(lookup):,}")
    print(f"    Total (record, keyword) pairs: {len(record_kw_map):,}")
    print(f"    Records with at least 1 kw:   {record_kw_map['record_id'].nunique():,}")
    
    avg_kw_per_record = len(record_kw_map) / record_kw_map['record_id'].nunique()
    print(f"    Avg keywords per record:      {avg_kw_per_record:.1f}")
    
    print(f"\n[6] Top 30 final keywords (post-thesaurus, post-stopword):")
    print(f"    {'Rank':<5} {'Total':>5} {'Auth':>4} {'K+':>4} {'MeSH':>4}  Keyword")
    print(f"    {'-'*4:<5} {'-'*5:>5} {'-'*4:>4} {'-'*4:>4} {'-'*4:>4}  {'-'*40}")
    
    for _, row in lookup.head(30).iterrows():
        ak = int(row.get('n_author_keywords', 0))
        kp = int(row.get('n_keywords_plus', 0))
        mh = int(row.get('n_mesh_terms', 0))
        print(f"    {int(row['rank']):<5} {int(row['n_records']):>5,} "
              f"{ak:>4} {kp:>4} {mh:>4}  {row['keyword']}")
    
    print("\n" + "=" * 70)
    print("DONE: Ready for Block 3 (Top 50 keywords + Figure 9)")
    print("=" * 70)


if __name__ == "__main__":
    main()
