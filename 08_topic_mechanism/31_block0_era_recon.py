"""Day 14 Block 0: temporal stratification recon.

Goal: examine year distribution of the Day 13 matrix records (1,662 unique
records contributing 1,738 record-mechanism pairs), and compare 3 candidate
era-binning schemes to pick the one with best sample balance.
"""
import pandas as pd
from pathlib import Path

REPO = Path(__file__).parent.parent
P = REPO / "data" / "processed"

# ============================================================
# Load (same filter pipeline as Day 13 Block 1)
# ============================================================
interactions = pd.read_parquet(
    P / "llm_extraction" / "primary_openai__gpt-4o-mini.interactions_normalized.parquet"
)
clusters = pd.read_parquet(P / "cluster_assignments.parquet")

NOISE_MECH = {"unspecified", "other"}
mech_clean = interactions[~interactions["mechanism"].isin(NOISE_MECH)]
# Keep year by dedupe on (record_id, mechanism) but take min year (any year is fine since each record has one year)
rec_mech = mech_clean[["record_id", "mechanism", "year"]].drop_duplicates(subset=["record_id", "mechanism"])
clusters_clean = clusters[clusters["cluster_id"] != -1][["record_id", "cluster_id"]]
merged = rec_mech.merge(clusters_clean, on="record_id", how="inner")

print(f"[Load] matrix-eligible pairs: {len(merged):,}, "
      f"records: {merged['record_id'].nunique():,}, "
      f"year range: {merged['year'].min()} - {merged['year'].max()}")

# ============================================================
# Year distribution
# ============================================================
print("\n[Year distribution] (pairs per year)")
year_counts = merged["year"].value_counts().sort_index()
for y, n in year_counts.items():
    bar = "#" * int(n / max(year_counts) * 50)
    print(f"  {y}: {n:>4}  {bar}")

# ============================================================
# Cumulative % (helps spot natural breakpoints)
# ============================================================
print(f"\n[Cumulative %] (helps spot natural breakpoints)")
cum = year_counts.cumsum() / year_counts.sum() * 100
for y, p in cum.items():
    print(f"  thru {y}: {p:5.1f}%")

# ============================================================
# 3 candidate era-binning schemes
# ============================================================
schemes = {
    "Scheme A (3-era symmetric ~7y bins)": [
        ("Period 1: early", 2005, 2012),
        ("Period 2: middle", 2013, 2019),
        ("Period 3: late", 2020, 2026),
    ],
    "Scheme B (3-era, balanced N target)": [
        ("Period 1: early", 2005, 2013),
        ("Period 2: middle", 2014, 2019),
        ("Period 3: late", 2020, 2026),
    ],
    "Scheme C (4-era, Day 12 A disjoint)": [
        ("Era 1: classical (2005-2011)", 2005, 2011),
        ("Era 2: mechanistic (2012-2017)", 2012, 2017),
        ("Era 3: transition (2018-2021)", 2018, 2021),
        ("Era 4: systems (2022-2026)", 2022, 2026),
    ],
}

for scheme_name, eras in schemes.items():
    print(f"\n=== {scheme_name} ===")
    print(f"  {'Era':<32s}  {'pairs':>7s}  {'records':>8s}  {'topics':>6s}  {'mechs':>5s}")
    for label, start, end in eras:
        in_era = merged[(merged["year"] >= start) & (merged["year"] <= end)]
        if len(in_era) == 0:
            print(f"  {label:<32s}  ({'empty':>7s})")
            continue
        n_pairs = len(in_era)
        n_records = in_era["record_id"].nunique()
        n_topics = in_era["cluster_id"].nunique()
        n_mechs = in_era["mechanism"].nunique()
        print(f"  {label:<32s}  {n_pairs:>7,}  {n_records:>8,}  {n_topics:>6d}  {n_mechs:>5d}")
    total = sum(
        len(merged[(merged["year"] >= s) & (merged["year"] <= e)])
        for _, s, e in eras
    )
    print(f"  {'TOTAL covered':<32s}  {total:>7,}  (of {len(merged):,})")

# ============================================================
# Per-topic year distribution: which topics are "early" vs "late"?
# (Quick preview - will help validate era boundary choice)
# ============================================================
print(f"\n[Topic mean-year] (descending; reveals temporal centroid)")
topic_yr = merged.groupby("cluster_id").agg(
    n_pairs=("year", "size"),
    median_year=("year", "median"),
    p25_year=("year", lambda x: x.quantile(0.25)),
    p75_year=("year", lambda x: x.quantile(0.75)),
).sort_values("median_year")

# Print top 5 earliest + top 5 latest
print("\n  5 earliest topics (by median year):")
print(topic_yr.head(5).to_string())
print("\n  5 latest topics (by median year):")
print(topic_yr.tail(5).to_string())

print("\n[Done] Block 0 recon.")