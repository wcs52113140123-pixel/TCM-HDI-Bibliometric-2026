"""
Block 3B.2+3B.3 (D2 final): Top 30 authors + Lotka's law with D2 method.

Uses author_lookup_d2.parquet (FINI + Institution disambiguation) to produce
final author ranking and productivity distribution.

Output (overwrites preliminary FINI-only versions):
- results/tables/table_03_top_authors.csv       (FINAL, D2)
- results/tables/table_03b_lotka_stats.csv       (FINAL, D2)
- results/figures/figure_06a_top_authors.png     (FINAL, D2)
- results/figures/figure_06b_lotka_law.png       (FINAL, D2)

Run:
    python 03_descriptive_analysis/06d_author_ranking_lotka_d2.py
"""

from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams.update({
    "figure.dpi": 100,
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3B.2+3B.3 (FINAL): Top 30 authors + Lotka (D2)")
    print("=" * 70)
    
    # Load D2
    print("\n[1] Loading D2 author data...")
    d2_df = pd.read_parquet(repo_root / "data/processed/author_lookup_d2.parquet")
    print(f"    Total D2 authors: {len(d2_df):,}")
    print(f"    Excluding @unknown: {(~d2_df['is_unknown_inst']).sum():,}")
    
    # ============ Step 1: Top 30 (exclude unknown institutions) ============
    d2_known = d2_df[~d2_df['is_unknown_inst']].copy().sort_values("n_records", ascending=False).reset_index(drop=True)
    
    top30 = d2_known.head(30).copy()
    top30["rank"] = top30.index + 1
    top30["display_name"] = top30["fini_id"] + " @ " + top30["institution"].str[:40]
    
    print(f"\n[2] Top 30 D2 authors (saved to table):")
    print(f"    {'Rank':<5} {'FINI':<14s} {'Institution':<45s} {'NPub':>5s} {'1st':>5s}")
    print(f"    {'-'*4:<5} {'-'*14:<14s} {'-'*45:<45s} {'-'*5:>5s} {'-'*5:>5s}")
    for _, row in top30.iterrows():
        inst_short = row["institution"][:44]
        print(f"    {int(row['rank']):<5} {row['fini_id'][:13]:<14s} {inst_short:<45s} "
              f"{int(row['n_records']):>5,} {int(row['first_author_count']):>5,}")
    
    # Save Top 30 table
    out_tables = repo_root / "results" / "tables"
    out_tables.mkdir(parents=True, exist_ok=True)
    out_figs = repo_root / "results" / "figures"
    out_figs.mkdir(parents=True, exist_ok=True)
    
    top30_out = top30[["rank", "fini_id", "institution", "n_records",
                       "first_author_count", "d2_id"]].copy()
    top30_out.columns = ["rank", "fini_id", "institution", "n_publications",
                          "n_first_author", "d2_id"]
    top30_out.to_csv(out_tables / "table_03_top_authors.csv", index=False, encoding="utf-8")
    print(f"\n[3] Saved: {out_tables / 'table_03_top_authors.csv'}")
    
    # ============ Step 2: Figure 6a (Top 20 bar chart) ============
    print(f"\n[4] Building Figure 6a (Top 20 D2 authors)...")
    top20 = top30.head(20).copy().iloc[::-1]
    
    # Color by institution country (Chinese mainland=red, HK=orange, SA=gold, US=blue, DE=green, KR=orange)
    def get_color(inst):
        inst_l = inst.lower()
        if "hong kong" in inst_l:
            return "#E89C50"
        elif "saud" in inst_l:
            return "#D4A04C"
        elif "mississippi" in inst_l:
            return "#5B8DD6"
        elif "mainz" in inst_l or "gutenberg" in inst_l:
            return "#5BA68D"
        elif "kyungpook" in inst_l:
            return "#E8A04C"
        else:
            return "#C04848"  # Chinese mainland default
    
    colors = [get_color(inst) for inst in top20["institution"]]
    
    fig, ax = plt.subplots(figsize=(12, 9))
    bars = ax.barh(top20["display_name"], top20["n_records"],
                    color=colors, edgecolor="white", linewidth=0.8)
    
    for bar, n in zip(bars, top20["n_records"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                 f"{int(n)}", va="center", fontsize=9.5, color="#333")
    
    ax.set_xlabel("Number of Publications", fontweight="bold")
    ax.set_title("Top 20 Most-Prolific Authors in TCM Herb-Drug Interaction Research (2005-2025)\n"
                 "D2 Disambiguation: FINI + Institutional Context",
                 fontweight="bold", fontsize=11, pad=12)
    ax.set_xlim(0, top20["n_records"].max() * 1.10)
    ax.grid(axis="x", alpha=0.3, linestyle=":")
    
    plt.tight_layout()
    fig_a_path = out_figs / "figure_06a_top_authors.png"
    plt.savefig(fig_a_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig_a_path}")
    
    # ============ Step 3: Lotka's law (D2) ============
    print(f"\n[5] Computing Lotka's law on D2 distribution...")
    
    # Use all D2 authors (including unknown - they still count)
    n_pub_counter = Counter(d2_df["n_records"])
    n_values = sorted(n_pub_counter.keys())
    f_values = [n_pub_counter[n] for n in n_values]
    
    total_authors = sum(f_values)
    print(f"    Total D2 authors:    {total_authors:,}")
    print(f"    Productivity range:  1 - {max(n_values)} papers")
    
    # Lotka fit (log-log linear regression)
    log_n = np.log10(n_values)
    log_f = np.log10(f_values)
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_n, log_f)
    alpha = -slope
    C = 10 ** intercept
    
    print(f"\n[6] D2 Lotka fit:")
    print(f"    alpha (slope):       {alpha:.4f}")
    print(f"    C (intercept):       {C:.2f}")
    print(f"    R-squared:           {r_value**2:.4f}")
    print(f"    p-value:             {p_value:.2e}")
    
    if alpha < 1.8:
        interp = "Sub-Lotka (gentler distribution)"
    elif alpha > 2.5:
        interp = "Super-Lotka (steeper distribution)"
    else:
        interp = "Classic Lotka regime"
    print(f"    Interpretation:      {interp}")
    
    # K-S test
    empirical_authors = np.array([n_pub_counter[n] for n in sorted(n_pub_counter)])
    cdf_empirical = np.cumsum(empirical_authors) / sum(empirical_authors)
    theoretical = np.array([C / np.power(n, alpha) for n in sorted(n_pub_counter)])
    theoretical_normed = theoretical / theoretical.sum()
    cdf_theoretical = np.cumsum(theoretical_normed)
    ks_stat = np.max(np.abs(cdf_empirical - cdf_theoretical))
    ks_critical_05 = 1.36 / np.sqrt(total_authors)
    ks_pass = ks_stat < ks_critical_05
    
    print(f"\n[7] K-S test:")
    print(f"    K-S statistic:    {ks_stat:.4f}")
    print(f"    Critical (0.05):  {ks_critical_05:.4f}")
    print(f"    Conclusion:       {'PASS (data fits Lotka)' if ks_pass else 'FAIL (significant deviation)'}")
    
    # ============ Step 4: Figure 6b (log-log Lotka) ============
    print(f"\n[8] Building Figure 6b (D2 Lotka log-log)...")
    fig, ax = plt.subplots(figsize=(9, 7))
    
    ax.scatter(n_values, f_values, s=35, c="#5B8DD6", alpha=0.75,
                edgecolors="white", linewidths=0.5, zorder=10, label="Empirical (D2 disambiguation)")
    
    n_smooth = np.logspace(np.log10(1), np.log10(max(n_values)), 100)
    f_fitted = C / np.power(n_smooth, alpha)
    ax.plot(n_smooth, f_fitted, color="#C04848", linewidth=2.0, linestyle="--",
             label=f"Lotka fit: f(n) = {C:.0f}/n^{alpha:.2f}  (R² = {r_value**2:.3f})", zorder=5)
    
    f_theory = C / np.power(n_smooth, 2.0)
    ax.plot(n_smooth, f_theory, color="#5BA68D", linewidth=1.5, linestyle=":",
             label="Classic Lotka (α=2.0)", alpha=0.75, zorder=4)
    
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Number of publications (n)", fontweight="bold")
    ax.set_ylabel("Number of authors with n publications", fontweight="bold")
    ax.set_title(f"Lotka's Law of Scientific Productivity (D2 Disambiguation)\n"
                 f"TCM Herb-Drug Interactions (2005-2025), N={total_authors:,} authors\n"
                 f"Fitted α = {alpha:.2f}, R² = {r_value**2:.3f}, K-S {'PASS' if ks_pass else 'FAIL'} at p=0.05",
                 fontweight="bold", pad=12)
    ax.legend(loc="upper right", framealpha=0.95)
    ax.grid(True, alpha=0.3, which="both", linestyle=":")
    
    plt.tight_layout()
    fig_b_path = out_figs / "figure_06b_lotka_law.png"
    plt.savefig(fig_b_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig_b_path}")
    
    # Save Lotka stats
    stats_df = pd.DataFrame([{
        "method": "D2 FINI + Institution",
        "total_authors": total_authors,
        "alpha": round(alpha, 4),
        "C": round(C, 2),
        "r_squared": round(r_value**2, 4),
        "ks_statistic": round(ks_stat, 4),
        "ks_critical_05": round(ks_critical_05, 4),
        "ks_pass": ks_pass,
        "interpretation": interp,
    }])
    stats_df.to_csv(out_tables / "table_03b_lotka_stats.csv", index=False, encoding="utf-8")
    print(f"    {out_tables / 'table_03b_lotka_stats.csv'}")
    
    # Insights
    print(f"\n" + "=" * 70)
    print("DISCUSSION-READY INSIGHTS (D2):")
    print("=" * 70)
    print(f"""
1. LOTKA'S LAW (D2):
   "The TCM-HDI authorship distribution closely follows Lotka's law of
   scientific productivity: the number of authors publishing n papers
   scales as f(n) ∝ 1/n^{alpha:.2f} (R² = {r_value**2:.3f}, N={total_authors:,} disambiguated authors).
   The fitted exponent α = {alpha:.2f} {'matches the classical Lotka value of 2.0' if 1.8 < alpha < 2.2 else 'differs from the classical Lotka value'}."

2. PRODUCTIVITY CONCENTRATION:
   "Of {total_authors:,} D2 author identifiers, 
   {(d2_df['n_records'] == 1).sum():,} ({100*(d2_df['n_records'] == 1).sum()/total_authors:.1f}%) 
   contributed exactly one paper, {(d2_df['n_records'] >= 10).sum():,} 
   ({100*(d2_df['n_records'] >= 10).sum()/total_authors:.2f}%) authored 
   10 or more, and {(d2_df['n_records'] >= 20).sum():,} 
   ({100*(d2_df['n_records'] >= 20).sum()/total_authors:.3f}%) authored 20 or more."

3. INTERNATIONAL LEADERSHIP:
   Top 30 D2 authors span {top30['institution'].nunique()} institutions across multiple countries:
   - China mainland (TCM specialized universities + comprehensive): {(top30['institution'].str.contains('Chinese Medicine|TCM|Sun Yat|Pharmaceut|Heilongjiang')).sum()}
   - Hong Kong: {(top30['institution'].str.contains('Hong Kong')).sum()}
   - Saudi Arabia: {(top30['institution'].str.contains('Saud')).sum()}
   - Other international: {(~top30['institution'].str.contains('Chinese|Sun Yat|Pharmaceut|Hong Kong|Heilongjiang')).sum() - (top30['institution'].str.contains('Saud')).sum()}
""")


if __name__ == "__main__":
    main()
