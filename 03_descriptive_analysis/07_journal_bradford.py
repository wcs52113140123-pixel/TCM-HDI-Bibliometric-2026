"""
Block 4: Journal analysis + Bradford's law.

Bradford's law: Journals divided into 3 zones with ~equal article counts;
zone sizes follow geometric progression (1 : n : n²).

Output:
- results/tables/table_04_top_journals.csv
- results/tables/table_04b_bradford_zones.csv  
- results/figures/figure_07a_top_journals.png
- results/figures/figure_07b_bradford_law.png
"""

import math
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 100,
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def normalize_journal_name(s):
    """Standardize journal name capitalization and remove parenthetical info."""
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    # Strip trailing parenthetical: "Journal of X (Print)" → "Journal of X"
    import re
    s = re.sub(r"\s*\([^)]*\)\s*$", "", s)
    # Title case for readability
    return s.upper().strip()


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 4: Journal analysis + Bradford's law")
    print("=" * 70)
    
    # Load corpus
    print("\n[1] Loading corpus...")
    df_main = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    df_partial = pd.read_parquet(repo_root / "data/processed/integrated_corpus_partial2026.parquet")
    df = pd.concat([df_main, df_partial], ignore_index=True)
    print(f"    Total records: {len(df):,}")
    
    # Normalize journal names
    print("\n[2] Normalizing journal names...")
    df["journal_norm"] = df["journal"].apply(normalize_journal_name)
    
    n_with_journal = df["journal_norm"].notna().sum()
    n_unique = df["journal_norm"].nunique()
    print(f"    Records with journal name:  {n_with_journal:,} ({100*n_with_journal/len(df):.1f}%)")
    print(f"    Unique journals:            {n_unique:,}")
    
    # Per-journal stats
    print("\n[3] Computing per-journal statistics...")
    journal_groups = df[df["journal_norm"].notna()].groupby("journal_norm")
    
    stats_rows = []
    for jname, group in journal_groups:
        cited_list = []
        for c in group["cited_by"]:
            try:
                v = float(c) if c is not None else 0
                if v != v:  # NaN check (NaN != NaN)
                    v = 0
                cited_list.append(v)
            except (TypeError, ValueError):
                cited_list.append(0)
        
        stats_rows.append({
            "journal": jname,
            "n_pub": len(group),
            "total_citations": int(sum(cited_list)),
            "avg_citations": round(sum(cited_list) / len(cited_list), 1) if cited_list else 0,
            "year_first": int(group["year"].min()) if group["year"].notna().any() else None,
            "year_last": int(group["year"].max()) if group["year"].notna().any() else None,
        })
    
    rank_df = pd.DataFrame(stats_rows).sort_values("n_pub", ascending=False).reset_index(drop=True)
    rank_df["rank"] = rank_df.index + 1
    rank_df = rank_df[["rank", "journal", "n_pub", "total_citations", "avg_citations",
                       "year_first", "year_last"]]
    
    # Save Top 30
    out_tables = repo_root / "results" / "tables"
    out_figs = repo_root / "results" / "figures"
    
    top30_journals = rank_df.head(30)
    top30_journals.to_csv(out_tables / "table_04_top_journals.csv", index=False, encoding="utf-8")
    print(f"\n[4] Top 30 journals:")
    print(f"    {'Rank':<5} {'Journal':<60s} {'NPub':>5s} {'AvgCit':>7s}")
    for _, row in top30_journals.iterrows():
        print(f"    {int(row['rank']):<5} {row['journal'][:60]:<60s} "
              f"{int(row['n_pub']):>5,} {row['avg_citations']:>7.1f}")
    print(f"\n    Saved: {out_tables / 'table_04_top_journals.csv'}")
    
    # ============ Bradford's law ============
    print(f"\n[5] Computing Bradford's law...")
    
    total_articles = rank_df["n_pub"].sum()
    target_per_zone = total_articles / 3
    
    # Assign each journal to a zone (cumulative count basis)
    cumsum = 0
    zones = []
    zone_now = 1
    for _, row in rank_df.iterrows():
        cumsum += row["n_pub"]
        zones.append(zone_now)
        if cumsum >= target_per_zone * zone_now and zone_now < 3:
            zone_now += 1
    rank_df["bradford_zone"] = zones
    
    zone_stats = rank_df.groupby("bradford_zone").agg(
        n_journals=("journal", "count"),
        total_articles=("n_pub", "sum"),
    ).reset_index()
    zone_stats["pct_articles"] = round(100 * zone_stats["total_articles"] / total_articles, 1)
    
    print(f"\n    Total articles: {total_articles:,} ({total_articles/3:,.1f} per zone target)")
    print(f"\n    {'Zone':<6} {'N Journals':>12} {'N Articles':>12} {'Pct Articles':>14}")
    for _, row in zone_stats.iterrows():
        print(f"    {int(row['bradford_zone']):<6} {int(row['n_journals']):>12,} "
              f"{int(row['total_articles']):>12,} {row['pct_articles']:>13.1f}%")
    
    # Bradford multiplier n: zone sizes should be 1 : n : n²
    n_zone1 = zone_stats.iloc[0]["n_journals"]
    n_zone2 = zone_stats.iloc[1]["n_journals"]
    n_zone3 = zone_stats.iloc[2]["n_journals"]
    
    multiplier_avg = math.sqrt(n_zone3 / n_zone1) if n_zone1 > 0 else 0
    
    print(f"\n[6] Bradford multiplier (n):")
    print(f"    Theoretical: zone sizes should be 1:n:n²")
    print(f"    Zone1: {n_zone1}, Zone2: {n_zone2}, Zone3: {n_zone3}")
    print(f"    Implied n (zone2/zone1):    {n_zone2/n_zone1:.2f}")
    print(f"    Implied n (zone3/zone2):    {n_zone3/n_zone2:.2f}")
    print(f"    Geometric mean n:           {multiplier_avg:.2f}")
    
    # Save Bradford table
    zone_stats.to_csv(out_tables / "table_04b_bradford_zones.csv", index=False, encoding="utf-8")
    print(f"\n[7] Saved: {out_tables / 'table_04b_bradford_zones.csv'}")
    
    # ============ Figure 7a: Top 20 journals bar chart ============
    print(f"\n[8] Building Figure 7a (Top 20 journals)...")
    top20 = rank_df.head(20).copy().iloc[::-1]
    fig, ax = plt.subplots(figsize=(13, 8))
    
    # Color by zone
    zone_colors = {1: "#C04848", 2: "#E89C50", 3: "#5BA68D"}
    colors = [zone_colors.get(z, "#888") for z in top20["bradford_zone"]]
    
    bars = ax.barh(top20["journal"], top20["n_pub"],
                    color=colors, edgecolor="white", linewidth=0.8)
    
    for bar, n in zip(bars, top20["n_pub"]):
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2,
                 f"{int(n):,}", va="center", fontsize=9.5, color="#333")
    
    ax.set_xlabel("Number of Publications", fontweight="bold")
    ax.set_title("Top 20 Journals Publishing TCM Herb-Drug Interaction Research (2005-2025)\n"
                 "Color-coded by Bradford Zone (Red=Zone 1 Core; Orange=Zone 2; Green=Zone 3 Periphery)",
                 fontweight="bold", pad=12, fontsize=11)
    ax.set_xlim(0, top20["n_pub"].max() * 1.10)
    ax.grid(axis="x", alpha=0.3, linestyle=":")
    
    plt.tight_layout()
    fig7a_path = out_figs / "figure_07a_top_journals.png"
    plt.savefig(fig7a_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig7a_path}")
    
    # ============ Figure 7b: Bradford log-log plot ============
    print(f"\n[9] Building Figure 7b (Bradford log-log)...")
    
    # Build cumulative coverage curve
    rank_df_sorted = rank_df.sort_values("n_pub", ascending=False).reset_index(drop=True)
    rank_df_sorted["cum_articles"] = rank_df_sorted["n_pub"].cumsum()
    rank_df_sorted["cum_pct"] = 100 * rank_df_sorted["cum_articles"] / total_articles
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Plot the cumulative curve
    ranks = np.arange(1, len(rank_df_sorted) + 1)
    cum_pct = rank_df_sorted["cum_pct"].values
    
    ax.semilogx(ranks, cum_pct, color="#5B8DD6", linewidth=2.5,
                 label="Empirical Bradford curve")
    
    # Mark zones
    zone1_end = zone_stats.iloc[0]["n_journals"]
    zone2_end = zone1_end + zone_stats.iloc[1]["n_journals"]
    
    ax.axvline(zone1_end, color="#C04848", linestyle="--", alpha=0.7, 
                label=f"Zone 1 / 2 boundary (rank {int(zone1_end)})")
    ax.axvline(zone2_end, color="#E89C50", linestyle="--", alpha=0.7,
                label=f"Zone 2 / 3 boundary (rank {int(zone2_end)})")
    ax.axhline(33.3, color="gray", linestyle=":", alpha=0.5)
    ax.axhline(66.7, color="gray", linestyle=":", alpha=0.5)
    
    # Annotate
    ax.text(zone1_end * 0.8, 95, f"Zone 1\n{int(zone1_end)} journals", 
             fontsize=10, ha="right", color="#C04848", fontweight="bold")
    ax.text(math.sqrt(zone1_end * zone2_end), 60, f"Zone 2\n{int(zone_stats.iloc[1]['n_journals'])} journals",
             fontsize=10, ha="center", color="#E89C50", fontweight="bold")
    ax.text(zone2_end * 2, 30, f"Zone 3\n{int(zone_stats.iloc[2]['n_journals'])} journals",
             fontsize=10, color="#5BA68D", fontweight="bold")
    
    ax.set_xlabel("Journal Rank (log scale)", fontweight="bold")
    ax.set_ylabel("Cumulative Percentage of Articles (%)", fontweight="bold")
    ax.set_title(f"Bradford's Law of Scattering in TCM Herb-Drug Interaction Research\n"
                 f"Zone 1:2:3 = {n_zone1}:{n_zone2}:{n_zone3} journals, "
                 f"Multiplier n ≈ {multiplier_avg:.2f}\n"
                 f"Total: {total_articles:,} articles across {len(rank_df):,} journals",
                 fontweight="bold", pad=12)
    ax.set_xlim(1, len(rank_df_sorted))
    ax.set_ylim(0, 105)
    ax.legend(loc="lower right", framealpha=0.95)
    ax.grid(True, alpha=0.3, which="both", linestyle=":")
    
    plt.tight_layout()
    fig7b_path = out_figs / "figure_07b_bradford_law.png"
    plt.savefig(fig7b_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig7b_path}")
    
    # Save full ranking with zone
    rank_df.to_csv(out_tables / "table_04_all_journals.csv", index=False, encoding="utf-8")
    print(f"    {out_tables / 'table_04_all_journals.csv'} (all {len(rank_df):,} journals)")
    
    # Insights
    print(f"\n" + "=" * 70)
    print("DISCUSSION-READY INSIGHTS:")
    print("=" * 70)
    print(f"""
1. PUBLICATION DISPERSION:
   "The {total_articles:,} articles in our corpus were published across {len(rank_df):,} 
   distinct journals, with the top {int(zone1_end)} journals (Zone 1) accounting for one-third 
   of all publications. This Bradford pattern indicates moderate concentration."

2. BRADFORD MULTIPLIER:
   "The empirical Bradford multiplier was n ≈ {multiplier_avg:.2f}, indicating that each
   successive zone is approximately {multiplier_avg:.1f}x larger than the prior. This is consistent
   with broad pharmacological literatures where TCM-HDI work scatters across both
   specialized TCM journals (Zone 1 core) and general pharmacology/toxicology venues."

3. CORE JOURNALS (Zone 1 - {int(zone1_end)} journals):
   The top 5 journals are:
""")
    for _, row in top30_journals.head(5).iterrows():
        print(f"     - {row['journal']} ({int(row['n_pub'])} pub, AvgCit {row['avg_citations']:.1f})")


if __name__ == "__main__":
    main()
