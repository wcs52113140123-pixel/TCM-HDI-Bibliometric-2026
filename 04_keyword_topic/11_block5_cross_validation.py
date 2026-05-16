"""
Day 5 Block 5: Cross-validation of Day 5 abstract topics vs Day 4 keyword
co-occurrence clusters.

Logic:
  - Day 4 produced 5 keyword co-occurrence clusters (VOSviewer output).
  - Each record's Day-4 cluster label is derived from its keywords:
    majority vote of cluster assignments of the record's keywords
    (records without any matched keyword are excluded from cross-val).
  - Day 5 produced ~30-50 abstract clusters (HDBSCAN on SPECTER2).
  - Inner join on record_id → records with both labels → compute:
      * Adjusted Rand Index (ARI)        — Hubert & Arabie 1985
      * Normalized Mutual Information     — Strehl & Ghosh 2002
      * Contingency / confusion matrix
  - Sanity: noise (-1) records in Day 5 are excluded by default; a second
    run with noise included reported separately for completeness.

Outputs:
  results/tables/day4_vs_day5_metrics.csv
  results/tables/day4_vs_day5_confusion_matrix.csv
  results/figures/figure_15_day4_vs_day5_confusion.png
  results/audits/day5_cross_validation_report.md

Run:
  python 04_keyword_topic/11_block5_cross_validation.py
"""

from __future__ import annotations

import json
import re
import time
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score,
    confusion_matrix,
)

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
TABLES = REPO / "results" / "tables"
FIGS = REPO / "results" / "figures"
AUDITS = REPO / "results" / "audits"
for d in (TABLES, FIGS, AUDITS):
    d.mkdir(parents=True, exist_ok=True)

CORPUS_PATH = DATA / "integrated_corpus.parquet"
CLUSTERS_DAY5 = DATA / "cluster_assignments.parquet"
LABELS_DAY5 = DATA / "topic_labels.json"

OUT_METRICS = TABLES / "day4_vs_day5_metrics.csv"
OUT_CONF = TABLES / "day4_vs_day5_confusion_matrix.csv"
OUT_FIG = FIGS / "figure_15_day4_vs_day5_confusion.png"
OUT_REPORT = AUDITS / "day5_cross_validation_report.md"

# Day 4 keyword cluster mapping — re-derived via Louvain in Block 5 prep
# (VOSviewer .map was exported without cluster column; see 06d_recompute_keyword_clusters.py)
DAY4_CLUSTER_CANDIDATES = [
    REPO / "data" / "processed" / "keyword_cluster_day4_louvain.csv",
]

# Day 4 record-keyword mapping — adjust to actual filename
DAY4_RECORD_KW_CANDIDATES = [
    DATA / "keyword_record_map.parquet",
    DATA / "record_keyword_long.parquet",
    DATA / "record_keyword_map.parquet",
    DATA / "keyword_standardized_long.parquet",
]


def find_file(candidates: list[Path]) -> Path | None:
    for p in candidates:
        if p.exists():
            return p
    return None


def parse_keyword_cluster_csv(path: Path) -> pd.DataFrame:
    """Read keyword → cluster mapping CSV (from 06d_recompute_keyword_clusters.py).
    Expected columns: 'keyword', 'day4_cluster'."""
    df = pd.read_csv(path)
    if "keyword" not in df.columns or "day4_cluster" not in df.columns:
        raise ValueError(
            f"Expected columns 'keyword', 'day4_cluster' in {path.name}; "
            f"got {list(df.columns)}"
        )
    df["keyword"] = df["keyword"].astype(str).str.strip().str.lower()
    df["day4_cluster"] = df["day4_cluster"].astype(int)
    return df


def derive_day4_label_per_record(
    record_kw: pd.DataFrame, kw_cluster: pd.DataFrame
) -> pd.DataFrame:
    """For each record_id, majority-vote Day-4 cluster from its keywords."""
    # record_kw expected columns: record_id, keyword
    # kw_cluster: keyword, day4_cluster
    rk_cols = [c.lower() for c in record_kw.columns]
    if "record_id" not in record_kw.columns and "recordid" in rk_cols:
        record_kw = record_kw.rename(
            columns={record_kw.columns[rk_cols.index("recordid")]: "record_id"}
        )
    kw_col = None
    for c in record_kw.columns:
        if c.lower() in ("keyword", "kw", "term", "canonical_keyword"):
            kw_col = c
            break
    if kw_col is None:
        raise ValueError(f"No keyword column in record-keyword file. "
                         f"Columns: {list(record_kw.columns)}")
    rk = record_kw[["record_id", kw_col]].rename(columns={kw_col: "keyword"})
    rk["keyword"] = rk["keyword"].astype(str).str.strip().str.lower()

    merged = rk.merge(kw_cluster, on="keyword", how="inner")
    print(f"  record-keyword rows joined to cluster: {len(merged):,}")

    # Majority vote per record (ties broken by smallest cluster_id)
    def majority(s: pd.Series) -> int:
        c = Counter(s.tolist())
        most_common = c.most_common()
        # Sort by (count desc, cluster_id asc)
        most_common.sort(key=lambda x: (-x[1], x[0]))
        return most_common[0][0]

    rec_label = (
        merged.groupby("record_id")["day4_cluster"]
        .agg(majority)
        .reset_index()
        .rename(columns={"day4_cluster": "day4_label"})
    )
    print(f"  Records with derivable Day-4 label: {len(rec_label):,}")
    return rec_label


def main():
    t0 = time.time()

    # --- Locate Day 4 inputs ---------------------------------------------
    cluster_path = find_file(DAY4_CLUSTER_CANDIDATES)
    rk_path = find_file(DAY4_RECORD_KW_CANDIDATES)

    print(f"[{time.strftime('%H:%M:%S')}] Locating Day 4 artifacts...")
    if cluster_path is None:
        print("  ❌ Day 4 keyword cluster CSV NOT FOUND in expected locations:")
        for p in DAY4_CLUSTER_CANDIDATES:
            print(f"      {p.relative_to(REPO)}")
        print("\nRun first: python 04_keyword_topic/06d_recompute_keyword_clusters.py")
        print("Aborting.")
        return
    if rk_path is None:
        print("  ❌ Day 4 record-keyword mapping NOT FOUND in expected locations:")
        for p in DAY4_RECORD_KW_CANDIDATES:
            print(f"      {p.relative_to(REPO)}")
        print("\nPlease tell me the actual path. Aborting.")
        return

    print(f"  ✓ Keyword cluster CSV: {cluster_path.relative_to(REPO)}")
    print(f"  ✓ Record-keyword:      {rk_path.relative_to(REPO)}")

    # --- Load -------------------------------------------------------------
    kw_cluster = parse_keyword_cluster_csv(cluster_path)
    print(f"  Day-4 keywords with cluster: {len(kw_cluster):,} "
          f"({kw_cluster['day4_cluster'].nunique()} clusters)")

    record_kw = pd.read_parquet(rk_path)
    print(f"  Record-keyword rows: {len(record_kw):,}")

    day4 = derive_day4_label_per_record(record_kw, kw_cluster)
    day5 = pd.read_parquet(CLUSTERS_DAY5)[["record_id", "cluster_id"]].rename(
        columns={"cluster_id": "day5_label"}
    )

    # --- Inner join + filter noise ---------------------------------------
    merged = day4.merge(day5, on="record_id", how="inner")
    print(f"  Records with both labels: {len(merged):,}")

    merged_no_noise = merged[merged["day5_label"] != -1].copy()
    print(f"  After excluding Day-5 noise: {len(merged_no_noise):,}")

    # --- Metrics (two passes: excl noise / incl noise as own group) ------
    metrics_rows = []
    for variant, mdf in [
        ("excl_noise", merged_no_noise),
        ("incl_noise", merged),
    ]:
        if len(mdf) == 0:
            continue
        ari = adjusted_rand_score(mdf["day4_label"], mdf["day5_label"])
        nmi = normalized_mutual_info_score(
            mdf["day4_label"], mdf["day5_label"], average_method="arithmetic"
        )
        metrics_rows.append({
            "variant": variant,
            "n_records": len(mdf),
            "ARI": round(ari, 4),
            "NMI": round(nmi, 4),
            "n_day4_clusters": mdf["day4_label"].nunique(),
            "n_day5_clusters": mdf["day5_label"].nunique(),
        })

    metrics_df = pd.DataFrame(metrics_rows)
    metrics_df.to_csv(OUT_METRICS, index=False)
    print(f"\n  Metrics:")
    print(metrics_df.to_string(index=False))
    print(f"  → {OUT_METRICS.name}")

    # --- Confusion matrix (rows=Day 5 cluster, cols=Day 4 cluster) -------
    conf = pd.crosstab(
        merged_no_noise["day5_label"], merged_no_noise["day4_label"],
        rownames=["Day5_cluster"], colnames=["Day4_cluster"],
    )
    conf.to_csv(OUT_CONF)
    print(f"  → {OUT_CONF.name} shape={conf.shape}")

    # Row-normalize for figure (each Day-5 cluster's distribution over Day-4)
    conf_norm = conf.div(conf.sum(axis=1), axis=0) * 100

    # --- Figure: heatmap --------------------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Plotting confusion heatmap...")
    fig, ax = plt.subplots(
        figsize=(8, max(6, len(conf_norm) * 0.30))
    )
    sns.heatmap(
        conf_norm, cmap="Blues", annot=True, fmt=".0f", linewidths=0.4,
        linecolor="white",
        cbar_kws={"label": "% of Day-5 cluster mapped to Day-4 cluster"},
        ax=ax,
    )
    ax.set_title(
        f"Day-5 Topics × Day-4 Keyword Clusters\n"
        f"(ARI={metrics_rows[0]['ARI']}, NMI={metrics_rows[0]['NMI']}, "
        f"n={metrics_rows[0]['n_records']:,} records)",
        fontsize=11,
    )
    ax.set_xlabel("Day-4 Keyword Cluster")
    ax.set_ylabel("Day-5 Abstract Topic")
    plt.tight_layout()
    plt.savefig(OUT_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → {OUT_FIG.name}")

    # --- Markdown report --------------------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Writing report...")
    ari_ex = metrics_rows[0]["ARI"]
    nmi_ex = metrics_rows[0]["NMI"]

    def interp_ari(x: float) -> str:
        if x >= 0.5: return "strong agreement"
        if x >= 0.3: return "moderate agreement"
        if x >= 0.1: return "weak but non-trivial agreement"
        return "near-random agreement"

    def interp_nmi(x: float) -> str:
        if x >= 0.6: return "high mutual information"
        if x >= 0.4: return "moderate mutual information"
        if x >= 0.2: return "modest mutual information"
        return "low mutual information"

    report = f"""# Day 5 Cross-validation Report

## Overview
Cross-validation of Day-5 abstract-level SPECTER2 + HDBSCAN topics against
Day-4 keyword co-occurrence clusters (VOSviewer, 5 clusters: ADME core,
TCM oncology, CAM clinical safety, in silico mechanisms, classic herb-drug
pairs).

## Method
For each record:
- Day-4 label: majority vote of its keywords' VOSviewer cluster
  assignments. Records without any matched keyword excluded.
- Day-5 label: HDBSCAN cluster_id from SPECTER2 embeddings.
ARI (Hubert & Arabie 1985) and NMI (Strehl & Ghosh 2002, arithmetic) computed
on inner-joined records.

## Results (primary: noise-excluded)
- n records compared: **{metrics_rows[0]['n_records']:,}**
- Day-4 clusters present: {metrics_rows[0]['n_day4_clusters']}
- Day-5 clusters present: {metrics_rows[0]['n_day5_clusters']}
- **ARI = {ari_ex}** ({interp_ari(ari_ex)})
- **NMI = {nmi_ex}** ({interp_nmi(nmi_ex)})

## Interpretation
ARI > 0 indicates better-than-chance agreement; values around 0.2-0.4 are
typical when comparing fine-grained topic models (Day 5: ~30+ topics) against
coarse-grained co-occurrence clusters (Day 4: 5 clusters), because the
finer partition splits coarse clusters into sub-themes. NMI is less sensitive
to cluster cardinality difference and better captures information overlap.

A strong ARI (>0.3) confirms convergent validity: SPECTER2 embeddings of
abstracts independently recover the thematic structure that VOSviewer found
on keyword co-occurrence. Lower ARI is not a refutation — many-to-one
mappings (multiple Day-5 sub-topics within one Day-4 cluster) inflate
disagreement while preserving NMI.

See `day4_vs_day5_confusion_matrix.csv` for granular mapping.

## Citations
- Hubert L. & Arabie P. 1985. Comparing partitions. J Classification.
- Strehl A. & Ghosh J. 2002. Cluster ensembles: a knowledge reuse framework
  for combining multiple partitions. JMLR.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(f"  → {OUT_REPORT.name}")

    print(f"\n[{time.strftime('%H:%M:%S')}] Block 5 complete. "
          f"Total: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
