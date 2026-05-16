"""
Day 6-7 stratified sampling.

Produces two samples from the 9,413 main corpus:
  - 50 abstracts for Day 6 cross-model benchmark
  - 500 abstracts for Day 7 schema/prompt validation

Stratification: by Day 5 topic cluster (39 real clusters, noise excluded).
Within-cluster preference: high cluster_probability (mean_prob ≥ 60th percentile),
then random within the high-confidence pool.

Exclusions:
  - noise records (cluster_id = -1)
  - records with abstract < 100 chars (too short for meaningful extraction)
  - pure review papers (we want primary HDI evidence, not review-of-reviews)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
CORPUS_PATH = DATA / "integrated_corpus.parquet"
CLUSTERS_PATH = DATA / "cluster_assignments.parquet"
OUT_50 = DATA / "llm_benchmark_50.parquet"
OUT_500 = DATA / "llm_validation_500.parquet"

SEED = 42
N_BENCHMARK = 50
N_VALIDATION = 500


def is_review_abstract(doc_type: str) -> bool:
    """Heuristic: detect review / meta-analysis from doc_type field."""
    if not isinstance(doc_type, str):
        return False
    dt = doc_type.lower()
    return any(kw in dt for kw in [
        "review", "systematic", "meta-analysis", "metaanalysis", "meta analysis"
    ])


def stratified_sample(
    df: pd.DataFrame, n_target: int, seed: int,
    cluster_col: str = "cluster_id",
    prob_col: str = "probability",
) -> pd.DataFrame:
    """Stratified sample by cluster, preferring high-probability members."""
    cluster_sizes = df.groupby(cluster_col).size()
    n_clusters = len(cluster_sizes)

    # Allocate: ≥1 per cluster, then weighted by cluster size for remainder
    base = 1 if n_target >= n_clusters else 0
    remaining = n_target - base * n_clusters
    weights = cluster_sizes / cluster_sizes.sum()
    extra = (weights * remaining).round().astype(int)

    # Reconcile rounding to land exactly on n_target
    while extra.sum() < remaining:
        idx = (weights * remaining - extra).idxmax()
        extra[idx] += 1
    while extra.sum() > remaining:
        idx = extra.idxmax()
        extra[idx] -= 1

    allocation = (base + extra)
    if base == 0:
        # When n_target < n_clusters, ensure some clusters get 0
        allocation = extra

    sampled_chunks = []
    rng_master = np.random.default_rng(seed)
    for cid, n_take in allocation.items():
        if n_take == 0:
            continue
        sub = df[df[cluster_col] == cid]
        if len(sub) == 0:
            continue
        # Prefer top 60% by probability, but ensure enough breadth
        threshold = sub[prob_col].quantile(0.40)  # top 60%
        high_conf = sub[sub[prob_col] >= threshold]
        # Fall back to all if filter too restrictive
        pool = high_conf if len(high_conf) >= n_take else sub
        seed_i = int(rng_master.integers(0, 10**9))
        picks = pool.sample(n=min(n_take, len(pool)), random_state=seed_i)
        sampled_chunks.append(picks)

    out = pd.concat(sampled_chunks, ignore_index=True)
    return out


def main():
    print("Loading corpus + cluster assignments...")
    df_corpus = pd.read_parquet(CORPUS_PATH)
    df_clusters = pd.read_parquet(CLUSTERS_PATH)
    df = df_corpus.merge(df_clusters, on="record_id", how="left")
    print(f"  Total records: {len(df):,}")

    # Filters
    mask_cluster = df["cluster_id"] >= 0
    mask_abstract = df["abstract"].apply(
        lambda x: isinstance(x, str) and len(x.strip()) >= 100
    )
    mask_not_review = ~df["doc_type"].apply(is_review_abstract)

    df_eligible = df[mask_cluster & mask_abstract & mask_not_review].copy()
    print(f"  After excluding noise:         "
          f"{int((~mask_cluster).sum()):>6,} removed")
    print(f"  After excluding short abs:     "
          f"{int((~mask_abstract & mask_cluster).sum()):>6,} removed")
    print(f"  After excluding review papers: "
          f"{int((~mask_not_review & mask_cluster & mask_abstract).sum()):>6,} removed")
    print(f"  Eligible pool: {len(df_eligible):,} "
          f"({df_eligible['cluster_id'].nunique()} clusters)")

    if len(df_eligible) < N_VALIDATION:
        print(f"FATAL: Eligible pool too small for n={N_VALIDATION}")
        sys.exit(1)

    # Sample benchmark (50) + validation (500)
    sample_50 = stratified_sample(df_eligible, N_BENCHMARK, seed=SEED)
    sample_500 = stratified_sample(df_eligible, N_VALIDATION, seed=SEED + 1)

    # Ensure benchmark ⊂ validation NOT enforced (they may overlap, that's OK
    # for now since they're used in different stages and 500 is mostly different)
    # But we DO want benchmark records labeled in the validation file if overlap
    overlap = set(sample_50["record_id"]) & set(sample_500["record_id"])
    print(f"\n  Benchmark-validation overlap: {len(overlap)} records "
          f"(acceptable; they serve different purposes)")

    cols_to_keep = [
        "record_id", "cluster_id", "year", "title", "abstract",
        "doc_type", "probability", "journal",
    ]
    cols_to_keep = [c for c in cols_to_keep if c in sample_50.columns]
    sample_50[cols_to_keep].sort_values("record_id").to_parquet(OUT_50, index=False)
    sample_500[cols_to_keep].sort_values("record_id").to_parquet(OUT_500, index=False)

    print(f"\n→ {OUT_50.relative_to(REPO)}: "
          f"{len(sample_50)} abstracts × {sample_50['cluster_id'].nunique()} clusters")
    print(f"→ {OUT_500.relative_to(REPO)}: "
          f"{len(sample_500)} abstracts × {sample_500['cluster_id'].nunique()} clusters")

    print("\nBenchmark per-cluster allocation:")
    cluster_dist = sample_50.groupby("cluster_id").size().sort_values(ascending=False)
    print(cluster_dist.describe())
    print(f"\nBenchmark sample by year:")
    print(sample_50.groupby("year").size())


if __name__ == "__main__":
    main()
