"""
Day 5 Block 4: Topic temporal evolution analysis.

Two-level analysis (顶刊 BERTopic-bibliometric standard):
  - Fine: 21 yearly bins (2005-2025), for trend detection and heatmap viz
  - Coarse: 3 periods (Early/Middle/Recent), aligned with Day 4 keyword
            evolution for cross-validation. Drives Discussion paradigm-shift
            narrative.

Outputs:
  results/tables/topic_yearly_freq.csv     # (cluster × year) doc counts
  results/tables/topic_yearly_pct.csv      # row-normalized per cluster
  results/tables/topic_period_freq.csv     # (cluster × period) doc counts
  results/tables/topic_rising_declining.csv # ΔRecent% - ΔEarly%
  results/figures/figure_12_topic_yearly_heatmap.png
  results/figures/figure_13_topic_evolution_3period.png
  results/figures/figure_14_topic_rising_declining.png

Citations:
  - Blei & Lafferty 2006. Dynamic Topic Models. ICML.
  - Grootendorst 2022. BERTopic dynamic topic modeling.
  - Donthu et al. 2021. Bibliometric methodology guidelines.

Run:
  python 04_keyword_topic/10_block4_topic_evolution.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
TABLES = REPO / "results" / "tables"
FIGS = REPO / "results" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

CORPUS_PATH = DATA / "integrated_corpus.parquet"
CLUSTERS_PATH = DATA / "cluster_assignments.parquet"
LABELS_PATH = DATA / "topic_labels.json"

OUT_YR_FREQ = TABLES / "topic_yearly_freq.csv"
OUT_YR_PCT = TABLES / "topic_yearly_pct.csv"
OUT_PER_FREQ = TABLES / "topic_period_freq.csv"
OUT_RISING = TABLES / "topic_rising_declining.csv"
FIG_HEATMAP = FIGS / "figure_12_topic_yearly_heatmap.png"
FIG_PERIODS = FIGS / "figure_13_topic_evolution_3period.png"
FIG_RISING = FIGS / "figure_14_topic_rising_declining.png"

# 3-period boundaries (aligned with Day 4 keyword evolution)
PERIODS = [
    ("Early (2005-2011)", 2005, 2011),
    ("Middle (2012-2018)", 2012, 2018),
    ("Recent (2019-2025)", 2019, 2025),
]

N_TOP_TOPICS_VIZ = 20  # show top-N topics in heatmap/bar charts


def assign_period(year: int) -> str | None:
    for name, lo, hi in PERIODS:
        if lo <= year <= hi:
            return name
    return None


def short_label(cid: int, labels: dict, max_terms: int = 3) -> str:
    """Compact topic label for figure axes: 'C{id}: term1, term2, term3'."""
    if str(cid) in labels:
        terms = labels[str(cid)]["top_keybert"][:max_terms]
    elif cid in labels:
        terms = labels[cid]["top_keybert"][:max_terms]
    else:
        terms = []
    return f"T{cid}: " + ", ".join(terms) if terms else f"T{cid}"


def main():
    t0 = time.time()

    # --- Load -------------------------------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Loading inputs...")
    df = pd.read_parquet(CORPUS_PATH)[["record_id", "year"]]
    clusters = pd.read_parquet(CLUSTERS_PATH)
    df = df.merge(clusters, on="record_id", how="left")
    df["period"] = df["year"].apply(assign_period)

    if LABELS_PATH.exists():
        with open(LABELS_PATH, encoding="utf-8") as f:
            labels = json.load(f)
    else:
        print("  WARNING: topic_labels.json not found, falling back to C{id}")
        labels = {}

    df_real = df[df["cluster_id"] >= 0].copy()
    print(f"  Records with valid cluster: {len(df_real):,} "
          f"(noise excluded from evolution)")
    print(f"  Clusters: {df_real['cluster_id'].nunique()}")

    # --- Yearly frequency table -------------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Yearly frequency table...")
    yr_freq = df_real.pivot_table(
        index="cluster_id", columns="year", values="record_id",
        aggfunc="count", fill_value=0,
    ).astype(int)
    # Ensure all years 2005-2025 present
    for y in range(2005, 2026):
        if y not in yr_freq.columns:
            yr_freq[y] = 0
    yr_freq = yr_freq[sorted(yr_freq.columns)]
    yr_freq.to_csv(OUT_YR_FREQ)
    print(f"  → {OUT_YR_FREQ.name} shape={yr_freq.shape}")

    # Row-normalized (cluster's distribution over years)
    yr_pct = yr_freq.div(yr_freq.sum(axis=1), axis=0) * 100
    yr_pct.round(2).to_csv(OUT_YR_PCT)
    print(f"  → {OUT_YR_PCT.name}")

    # --- Period frequency table ------------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Period (3-bin) table...")
    per_freq = df_real.pivot_table(
        index="cluster_id", columns="period", values="record_id",
        aggfunc="count", fill_value=0,
    )
    period_order = [p[0] for p in PERIODS]
    per_freq = per_freq[period_order]

    # Compute period totals for %-of-period normalization
    period_totals = df_real.groupby("period").size().reindex(period_order)
    per_pct = per_freq.div(period_totals, axis=1) * 100

    per_freq.to_csv(OUT_PER_FREQ)
    print(f"  → {OUT_PER_FREQ.name}")

    # --- Rising / declining topics ---------------------------------------
    rising = pd.DataFrame({
        "cluster_id": per_pct.index,
        "early_pct": per_pct[period_order[0]].values.round(3),
        "middle_pct": per_pct[period_order[1]].values.round(3),
        "recent_pct": per_pct[period_order[2]].values.round(3),
    })
    rising["delta_recent_minus_early"] = (
        rising["recent_pct"] - rising["early_pct"]
    ).round(3)
    rising["fold_change"] = (
        (rising["recent_pct"] + 0.01) / (rising["early_pct"] + 0.01)
    ).round(2)
    rising["short_label"] = rising["cluster_id"].apply(
        lambda c: short_label(c, labels)
    )
    rising = rising.sort_values("delta_recent_minus_early", ascending=False)
    rising.to_csv(OUT_RISING, index=False)
    print(f"  → {OUT_RISING.name}")

    print(f"\n  Top 5 RISING topics:")
    for _, r in rising.head(5).iterrows():
        print(f"    {r['short_label']}: "
              f"{r['early_pct']:.2f}% → {r['recent_pct']:.2f}% "
              f"(Δ={r['delta_recent_minus_early']:+.2f}%, "
              f"fold={r['fold_change']:.1f}x)")
    print(f"\n  Top 5 DECLINING topics:")
    for _, r in rising.tail(5).iterrows():
        print(f"    {r['short_label']}: "
              f"{r['early_pct']:.2f}% → {r['recent_pct']:.2f}% "
              f"(Δ={r['delta_recent_minus_early']:+.2f}%, "
              f"fold={r['fold_change']:.1f}x)")

    # --- Figure 12: yearly heatmap ---------------------------------------
    print(f"\n[{time.strftime('%H:%M:%S')}] Plotting yearly heatmap...")
    # Top N topics by total volume for readability
    topic_totals = yr_freq.sum(axis=1).sort_values(ascending=False)
    top_topics = topic_totals.head(N_TOP_TOPICS_VIZ).index.tolist()
    yr_pct_top = yr_pct.loc[top_topics]
    yr_pct_top.index = [short_label(c, labels) for c in yr_pct_top.index]

    fig, ax = plt.subplots(figsize=(13, max(6, len(top_topics) * 0.35)))
    sns.heatmap(
        yr_pct_top, cmap="YlOrRd", linewidths=0.4, linecolor="white",
        cbar_kws={"label": "% of cluster's docs in that year"},
        ax=ax, annot=False,
    )
    ax.set_title(f"Topic Evolution by Year — Top {N_TOP_TOPICS_VIZ} Topics "
                 "(% of each topic's lifetime in year)", fontsize=11)
    ax.set_xlabel("Year")
    ax.set_ylabel("Topic")
    plt.tight_layout()
    plt.savefig(FIG_HEATMAP, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → {FIG_HEATMAP.name}")

    # --- Figure 13: 3-period grouped bar ---------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Plotting 3-period bar chart...")
    per_pct_top = per_pct.loc[top_topics].copy()
    per_pct_top.index = [short_label(c, labels) for c in per_pct_top.index]

    fig, ax = plt.subplots(figsize=(13, max(6, len(top_topics) * 0.35)))
    per_pct_top.plot(kind="barh", ax=ax, width=0.78,
                     color=["#7fb069", "#f4a261", "#e63946"])
    ax.set_xlabel("% of period's documents")
    ax.set_ylabel("Topic")
    ax.set_title(f"Topic Share Across 3 Periods — Top {N_TOP_TOPICS_VIZ} Topics",
                 fontsize=11)
    ax.legend(title="", loc="lower right")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(FIG_PERIODS, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → {FIG_PERIODS.name}")

    # --- Figure 14: rising / declining horizontal bar --------------------
    print(f"[{time.strftime('%H:%M:%S')}] Plotting rising/declining chart...")
    top_n = 10
    top_rising = rising.head(top_n)
    top_declining = rising.tail(top_n)[::-1]
    combo = pd.concat([top_rising, top_declining])

    fig, ax = plt.subplots(figsize=(11, max(6, len(combo) * 0.35)))
    colors = ["#2a9d8f" if d > 0 else "#e76f51"
              for d in combo["delta_recent_minus_early"]]
    ax.barh(combo["short_label"], combo["delta_recent_minus_early"],
            color=colors, edgecolor="black", linewidth=0.4)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_xlabel("Δ % (Recent 2019-2025 share − Early 2005-2011 share)")
    ax.set_title(f"Top {top_n} Rising vs Top {top_n} Declining Topics",
                 fontsize=11)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(FIG_RISING, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → {FIG_RISING.name}")

    print(f"\n[{time.strftime('%H:%M:%S')}] Block 4 complete. "
          f"Total: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
