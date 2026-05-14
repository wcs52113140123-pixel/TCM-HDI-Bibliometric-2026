"""
Block 1: Annual publication trend analysis.

Reads integrated_corpus.parquet and computes:
- Annual publication counts (2005-2025) + 2026 partial
- Year-over-year growth rate
- Whole-period and sub-period CAGR
- Acceleration analysis (years with growth >= 20%)

Outputs:
- results/tables/table_01_annual_publications.csv
- results/tables/table_01b_period_statistics.csv
- results/figures/figure_02_annual_trend.png

Run:
    python 03_descriptive_analysis/01_annual_trends.py
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Publication-quality matplotlib defaults
plt.rcParams.update({
    "figure.dpi": 100,
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Day 3 Block 1: Annual Publication Trend")
    print("=" * 70)
    
    # ============ Load data ============
    print("\n[1] Loading data...")
    df_main = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    df_partial = pd.read_parquet(repo_root / "data/processed/integrated_corpus_partial2026.parquet")
    
    print(f"    Main corpus: {len(df_main):,}")
    print(f"    Partial 2026: {len(df_partial):,}")
    
    # Split out 2026 records from main (25 early-access records)
    df_main_2005_2025 = df_main[df_main["year"].between(2005, 2025)].copy()
    df_main_2026 = df_main[df_main["year"] == 2026].copy()
    
    print(f"    Main 2005-2025 (analysis range): {len(df_main_2005_2025):,}")
    print(f"    Main with year=2026 (early-access drift): {len(df_main_2026):,}")
    
    # ============ Annual counts ============
    print("\n[2] Computing annual statistics...")
    
    yr_counts = df_main_2005_2025["year"].value_counts().sort_index()
    df_yr = pd.DataFrame({
        "year": yr_counts.index.astype(int),
        "n_publications": yr_counts.values.astype(int),
    })
    total_n = int(df_yr["n_publications"].sum())
    df_yr["cumulative"] = df_yr["n_publications"].cumsum()
    df_yr["pct_of_total"] = round(100 * df_yr["n_publications"] / total_n, 2)
    df_yr["yoy_growth_pct"] = round(df_yr["n_publications"].pct_change() * 100, 1)
    df_yr["rolling_5yr_mean"] = df_yr["n_publications"].rolling(5, center=True).mean().round(1)
    
    # ============ CAGR (full + sub-periods) ============
    n_start = df_yr.iloc[0]["n_publications"]
    n_end = df_yr.iloc[-1]["n_publications"]
    n_years = int(df_yr.iloc[-1]["year"] - df_yr.iloc[0]["year"])
    cagr_full = (n_end / n_start) ** (1 / n_years) - 1
    
    periods = [
        ("Early phase (2005-2010)", 2005, 2010),
        ("Growth phase (2011-2017)", 2011, 2017),
        ("Plateau phase (2018-2023)", 2018, 2023),
        ("Recent peak (2024-2025)", 2024, 2025),
    ]
    period_stats = []
    for label, y0, y1 in periods:
        sub = df_yr[(df_yr["year"] >= y0) & (df_yr["year"] <= y1)]
        if len(sub) >= 2:
            ns, ne = sub.iloc[0]["n_publications"], sub.iloc[-1]["n_publications"]
            ny = int(sub.iloc[-1]["year"] - sub.iloc[0]["year"])
            sub_cagr = (ne / ns) ** (1 / ny) - 1 if ns > 0 else None
        else:
            sub_cagr = None
        period_stats.append({
            "period": label,
            "n_total": int(sub["n_publications"].sum()),
            "annual_mean": round(sub["n_publications"].mean(), 1),
            "cagr_pct": round(sub_cagr * 100, 1) if sub_cagr is not None else None,
        })
    
    # ============ Key Insights ============
    peak_yr = int(df_yr.loc[df_yr["n_publications"].idxmax(), "year"])
    peak_n = int(df_yr["n_publications"].max())
    
    print(f"\n[3] Key Statistics:")
    print(f"    Total publications 2005-2025:    {total_n:,}")
    print(f"    Peak year:                       {peak_yr} ({peak_n:,} pubs, "
          f"{100*peak_n/total_n:.1f}% of corpus)")
    print(f"    Whole-period CAGR (2005->2025):  {cagr_full*100:.2f}%")
    
    # Predicted 2026 full-year
    partial_count = len(df_partial)
    # Assumption: partial 2026 covers ~5 months (Jan 1 to May 13)
    months_covered = 4.5
    predicted_2026 = int(partial_count * 12 / months_covered)
    print(f"    2026 (partial through mid-May):  {partial_count} pubs")
    print(f"    2026 full-year forecast:         ~{predicted_2026:,} (linear extrapolation)")
    
    print(f"\n[4] Sub-period statistics:")
    print(f"    {'Period':<28s} {'N':>7s} {'Mean/yr':>10s} {'CAGR':>9s}")
    print(f"    {'-' * 28:<28s} {'-' * 7:>7s} {'-' * 10:>10s} {'-' * 9:>9s}")
    for p in period_stats:
        cagr_s = f"{p['cagr_pct']}%" if p["cagr_pct"] is not None else "N/A"
        print(f"    {p['period']:<28s} {p['n_total']:>7,} {p['annual_mean']:>10.1f} {cagr_s:>9s}")
    
    # Acceleration years (YoY growth >= 20%)
    print(f"\n[5] Acceleration years (YoY growth >= 20%):")
    big_jumps = df_yr[df_yr["yoy_growth_pct"] >= 20.0].copy()
    if len(big_jumps) > 0:
        for _, row in big_jumps.iterrows():
            print(f"    {int(row['year'])}: {int(row['n_publications']):>5,} "
                  f"(+{row['yoy_growth_pct']}% vs prior year)")
    else:
        print("    No years with >=20% YoY growth (steady growth pattern)")
    
    # ============ Save tables ============
    out_tables = repo_root / "results" / "tables"
    out_tables.mkdir(parents=True, exist_ok=True)
    
    df_yr.to_csv(out_tables / "table_01_annual_publications.csv", index=False, encoding="utf-8")
    pd.DataFrame(period_stats).to_csv(
        out_tables / "table_01b_period_statistics.csv", index=False, encoding="utf-8"
    )
    
    # ============ Plot Figure 2 ============
    out_figs = repo_root / "results" / "figures"
    out_figs.mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    # Main bars
    ax.bar(df_yr["year"], df_yr["n_publications"],
           color="#5B8DD6", alpha=0.85, edgecolor="white", linewidth=0.6,
           label=f"Publications 2005-2025 (n={total_n:,})")
    
    # 2026 partial bar
    ax.bar([2026], [partial_count],
           color="#E8A04C", alpha=0.8, edgecolor="white", linewidth=0.6,
           label=f"2026 partial year (n={partial_count})", hatch="//")
    
    # 5-year rolling average
    ax.plot(df_yr["year"], df_yr["rolling_5yr_mean"],
            color="#C04848", linewidth=2.5, linestyle="--",
            label="5-year moving average", alpha=0.85, zorder=10)
    
    # Annotate 2023 dip (PubMed MeSH indexing lag)
    n_2023 = int(df_yr.loc[df_yr['year'] == 2023, 'n_publications'].values[0])
    ax.annotate('PubMed\nMeSH lag',
                xy=(2023, n_2023), xytext=(2023, n_2023 - 130),
                fontsize=8.5, ha='center', color='#777', style='italic',
                arrowprops=dict(arrowstyle='-', color='#aaa', lw=0.8))
    
    # Annotate peak
    ax.annotate(f"Peak: {peak_n:,}",
                xy=(peak_yr, peak_n), xytext=(peak_yr - 3.5, peak_n + 80),
                fontsize=10, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#444", lw=1.2))
    
    ax.set_xlabel("Year", fontweight="bold")
    ax.set_ylabel("Number of Publications", fontweight="bold")
    ax.set_title("Annual Publication Trend: TCM Herb-Drug Interactions (2005-2026)",
                 fontweight="bold", pad=12)
    ax.set_xticks(list(range(2005, 2026, 2)) + [2026])
    ax.set_ylim(0, max(df_yr["n_publications"].max(), partial_count) * 1.15)
    ax.grid(axis="y", alpha=0.3, linestyle=":")
    ax.legend(loc="upper left", framealpha=0.95)
    
    footer = (f"CAGR 2005-2025: {cagr_full*100:.2f}% per year   |   "
              f"Peak year: {peak_yr}   |   "
              f"Total N = {total_n:,}")
    ax.text(0.5, -0.13, footer, transform=ax.transAxes,
            ha="center", fontsize=9, style="italic", color="#555")
    
    plt.tight_layout()
    fig_path = out_figs / "figure_02_annual_trend.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"\n[6] Outputs saved:")
    print(f"    {out_tables / 'table_01_annual_publications.csv'}")
    print(f"    {out_tables / 'table_01b_period_statistics.csv'}")
    print(f"    {fig_path}")
    
    # ============ Discussion-ready hooks ============
    print(f"\n{'=' * 70}")
    print(f"DISCUSSION-READY INSIGHTS (paste directly into your Results section):")
    print(f"{'=' * 70}")
    print(f"""
1. CORPUS SIZE & GROWTH:
   "From 2005 to 2025, {total_n:,} publications on TCM herb-drug interactions 
   were identified across four major databases (WoS, Scopus, OpenAlex, PubMed). 
   The field grew at a compound annual rate of {cagr_full*100:.1f}%, more than 
   {n_end/n_start:.1f}-fold expansion over the 21-year period."

2. RECENT ACCELERATION:
   "The {periods[3][0]} demonstrated unprecedented activity, averaging 
   {period_stats[3]['annual_mean']:.0f} publications/year — a {period_stats[3]['cagr_pct']:.0f}% 
   CAGR over this short window. The year {peak_yr} alone contributed {peak_n:,} 
   publications ({100*peak_n/total_n:.1f}% of the entire corpus)."

3. 2026 OUTLOOK:
   "Partial-year data (January-mid May 2026) already contained {partial_count} 
   publications. Linear extrapolation projects ~{predicted_2026:,} publications 
   for the full year 2026, suggesting continued and possibly accelerating growth."
""")


if __name__ == "__main__":
    main()
