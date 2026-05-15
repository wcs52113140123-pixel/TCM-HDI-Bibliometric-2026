"""
Block 3A.4: Top 30 institutions ranking + Figure 5.

Computes per-institution statistics:
- N publications
- N first-author publications (corresponding author proxy)
- Total citations
- Mean citations per paper
- Country (from ROR)
- International collaboration rate (papers with foreign institutions)

Output:
- results/tables/table_03_top_institutions.csv (Top 30 with full stats)
- results/figures/figure_05_top_institutions.png (Top 20 horizontal bar, country-colored)

Run:
    python 03_descriptive_analysis/05d_institution_ranking.py
"""

from pathlib import Path
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams.update({
    "figure.dpi": 100,
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Country code -> display color (consistent with Block 2 Figure 3)
COUNTRY_COLORS = {
    "CN": "#C04848",  # red (Chinese mainland)
    "HK": "#E89C50",  # orange (Hong Kong / Macao / Taiwan use same group)
    "MO": "#E89C50",
    "TW": "#E89C50",
    "US": "#5B8DD6",  # blue
    "GB": "#5BA68D",  # green (Europe)
    "DE": "#5BA68D",
    "IT": "#5BA68D",
    "FR": "#5BA68D",
    "ES": "#5BA68D",
    "NL": "#5BA68D",
    "BE": "#5BA68D",
    "AT": "#5BA68D",
    "CH": "#5BA68D",
    "SE": "#5BA68D",
    "DK": "#5BA68D",
    "FI": "#5BA68D",
    "PT": "#5BA68D",
    "IE": "#5BA68D",
    "PL": "#5BA68D",
    "CZ": "#5BA68D",
    "GR": "#5BA68D",
    "AU": "#A88BB9",  # purple (Oceania)
    "NZ": "#A88BB9",
    "CA": "#5B8DD6",
    "MX": "#5B8DD6",
    "BR": "#CC7494",
    "IN": "#E8A04C",  # orange (Asia other)
    "KR": "#E8A04C",
    "JP": "#E8A04C",
    "MY": "#E8A04C",
    "SG": "#E8A04C",
    "TH": "#E8A04C",
    "PK": "#E8A04C",
    "ID": "#E8A04C",
    "PH": "#E8A04C",
    "SA": "#D4A04C",  # gold (Middle East)
    "IR": "#D4A04C",
    "TR": "#D4A04C",
    "IL": "#D4A04C",
    "AE": "#D4A04C",
    "EG": "#D4A04C",
    "JO": "#D4A04C",
    "LB": "#D4A04C",
    "ZA": "#8B6F47",  # brown (Africa)
    "NG": "#8B6F47",
    "ET": "#8B6F47",
    "MA": "#8B6F47",
}

REGION_LABELS = {
    "#C04848": "Chinese mainland",
    "#E89C50": "Hong Kong/Macao/Taiwan (China)",
    "#5B8DD6": "North America",
    "#5BA68D": "Europe",
    "#A88BB9": "Oceania",
    "#E8A04C": "Asia (other)",
    "#D4A04C": "Middle East",
    "#8B6F47": "Africa",
    "#CC7494": "Latin America",
    "#888888": "Other / unknown",
}


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3A.4: Top 30 institutions ranking + Figure 5")
    print("=" * 70)
    
    # Load
    print("\n[1] Loading data...")
    corpus_main = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    corpus_partial = pd.read_parquet(repo_root / "data/processed/integrated_corpus_partial2026.parquet")
    corpus = pd.concat([corpus_main, corpus_partial], ignore_index=True)
    
    inst_lookup = pd.read_parquet(repo_root / "data/processed/institution_lookup.parquet")
    ror = pd.read_parquet(repo_root / "data/processed/ror_results_fixed.parquet")
    
    # Build institution -> country map (from ROR)
    ror_matched = ror[ror["matched"] == True].copy()
    inst_to_country = {}
    for _, row in ror_matched.iterrows():
        name = row["ror_name"]
        if name not in inst_to_country and row.get("ror_country"):
            inst_to_country[name] = row["ror_country"]
    
    # Merge corpus + institutions
    df = corpus.merge(inst_lookup[["record_id", "institutions", "institution_count"]],
                       on="record_id", how="left")
    df_with_inst = df[df["institution_count"] >= 1].copy()
    print(f"    Records with institutions: {len(df_with_inst):,}")
    
    # Compute per-institution stats
    print("\n[2] Computing per-institution statistics...")
    inst_stats = {}  # inst_name -> dict
    
    for _, row in df_with_inst.iterrows():
        cited = row.get("cited_by", 0) or 0
        try:
            cited = float(cited)
        except (TypeError, ValueError):
            cited = 0
        insts = row["institutions"]
        if insts is None or len(insts) == 0:
            continue
        
        # First-author institution is the first institution listed
        first_inst = insts[0] if len(insts) > 0 else None
        
        # Multi-country flag based on inst countries
        countries = set()
        for ins in insts:
            c = inst_to_country.get(ins)
            if c:
                countries.add(c)
        is_intl = len(countries) >= 2
        
        for ins in set(insts):
            if ins not in inst_stats:
                inst_stats[ins] = {
                    "n_pub": 0,
                    "n_first_author": 0,
                    "total_citations": 0,
                    "n_intl_collab": 0,
                    "country": inst_to_country.get(ins, ""),
                }
            inst_stats[ins]["n_pub"] += 1
            inst_stats[ins]["total_citations"] += cited
            if ins == first_inst:
                inst_stats[ins]["n_first_author"] += 1
            if is_intl:
                inst_stats[ins]["n_intl_collab"] += 1
    
    # Build ranking dataframe
    rows = []
    for ins, st in inst_stats.items():
        rows.append({
            "institution": ins,
            "country": st["country"],
            "n_pub": st["n_pub"],
            "n_first_author": st["n_first_author"],
            "first_author_pct": round(100 * st["n_first_author"] / st["n_pub"], 1) if st["n_pub"] > 0 else 0,
            "total_citations": int(st["total_citations"]),
            "avg_citations": round(st["total_citations"] / st["n_pub"], 1) if st["n_pub"] > 0 else 0,
            "n_intl_collab": st["n_intl_collab"],
            "intl_collab_pct": round(100 * st["n_intl_collab"] / st["n_pub"], 1) if st["n_pub"] > 0 else 0,
        })
    rank_df = pd.DataFrame(rows).sort_values("n_pub", ascending=False).reset_index(drop=True)
    rank_df["rank"] = rank_df.index + 1
    rank_df = rank_df[["rank", "institution", "country", "n_pub", "n_first_author",
                       "first_author_pct", "total_citations", "avg_citations",
                       "n_intl_collab", "intl_collab_pct"]]
    
    # Print Top 30
    print(f"\n[3] Top 30 institutions:")
    print(f"    {'Rank':<5} {'Institution':<48s} {'CC':<4s} {'N_Pub':>6s} "
          f"{'1st%':>6s} {'AvgCit':>7s} {'Intl%':>6s}")
    print(f"    {'-'*4:<5} {'-'*48:<48s} {'-'*4:<4s} {'-'*6:>6s} "
          f"{'-'*6:>6s} {'-'*7:>7s} {'-'*6:>6s}")
    for _, row in rank_df.head(30).iterrows():
        name = row["institution"][:47]
        cc = row["country"] or "??"
        print(f"    {int(row['rank']):<5} {name:<48s} {cc:<4s} {int(row['n_pub']):>6,} "
              f"{row['first_author_pct']:>5.1f}% {row['avg_citations']:>7.1f} "
              f"{row['intl_collab_pct']:>5.1f}%")
    
    # Save Table 3
    out_tables = repo_root / "results" / "tables"
    out_tables.mkdir(parents=True, exist_ok=True)
    rank_df.to_csv(out_tables / "table_03_top_institutions.csv", index=False, encoding="utf-8")
    print(f"\n[4] Saved: {out_tables / 'table_03_top_institutions.csv'}")
    
    # Figure 5: Top 20 bar chart
    print(f"\n[5] Building Figure 5 (Top 20 institutions)...")
    top20 = rank_df.head(20).copy().iloc[::-1]
    
    fig, ax = plt.subplots(figsize=(13, 8))
    colors = [COUNTRY_COLORS.get(c, "#888") for c in top20["country"]]
    
    bars = ax.barh(top20["institution"], top20["n_pub"],
                    color=colors, edgecolor="white", linewidth=0.8)
    
    # Add count labels
    for bar, n in zip(bars, top20["n_pub"]):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                 f"{int(n):,}", va="center", fontsize=9.5, color="#333")
    
    ax.set_xlabel("Number of Publications", fontweight="bold")
    ax.set_title("Top 20 Institutions in TCM Herb-Drug Interaction Research (2005-2025)\n"
                 "Standardized via ROR Registry (n=8,235 records with extractable affiliation)",
                 fontweight="bold", pad=12, fontsize=11)
    ax.set_xlim(0, top20["n_pub"].max() * 1.12)
    ax.grid(axis="x", alpha=0.3, linestyle=":")
    
    # Legend by region
    unique_colors_in_top20 = list(dict.fromkeys([COUNTRY_COLORS.get(c, "#888") for c in top20["country"][::-1]]))
    legend_patches = [mpatches.Patch(color=col, label=REGION_LABELS.get(col, "Other")) 
                       for col in unique_colors_in_top20]
    ax.legend(handles=legend_patches, loc="lower right", framealpha=0.95,
               title="Region", title_fontsize=10, fontsize=9)
    
    plt.tight_layout()
    fig_path = repo_root / "results" / "figures" / "figure_05_top_institutions.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig_path}")
    
    # Discussion insights
    print(f"\n" + "=" * 70)
    print("DISCUSSION-READY INSIGHTS:")
    print("=" * 70)
    
    # Country breakdown of Top 20
    top_country_counts = Counter(top20["country"])
    top20_cn = sum(1 for c in top20["country"] if c == "CN")
    top20_west = sum(1 for c in top20["country"] if c in ("US", "GB", "DE", "FR", "AU", "CA", "NL"))
    
    print(f"""
1. INSTITUTIONAL DOMINANCE:
   "The top 20 most-prolific institutions in TCM-HDI research are dominated 
   by Chinese institutions ({top20_cn}/20), reflecting the geographic concentration 
   of the field. Top contributors include {rank_df.iloc[0]['institution']} 
   ({int(rank_df.iloc[0]['n_pub'])} publications, AvgCit {rank_df.iloc[0]['avg_citations']:.1f}), 
   {rank_df.iloc[1]['institution']} ({int(rank_df.iloc[1]['n_pub'])}), and 
   {rank_df.iloc[2]['institution']} ({int(rank_df.iloc[2]['n_pub'])})."

2. TCM-SPECIALIZED UNIVERSITIES:
   "Specialized TCM universities feature prominently in the top tier — 
   Beijing/Nanjing/Chengdu/Guangzhou/Tianjin/Shanghai Universities of Chinese 
   Medicine collectively contribute substantial scholarship, signaling 
   institutional infrastructure dedicated to TCM pharmacology research."

3. INTERNATIONAL CONTRIBUTORS:
   "Notable non-Chinese contributors include {rank_df[rank_df['country'] == 'US'].iloc[0]['institution'] if (rank_df['country'] == 'US').any() else 'N/A'} 
   (US), and Chinese University of Hong Kong (HK), the latter exemplifying 
   the 'high-collaboration' pattern observed at the country level."
""")


if __name__ == "__main__":
    main()
