"""
Block 2B: Country ranking + international collaboration analysis.

Inputs:
- data/processed/integrated_corpus.parquet
- data/processed/country_lookup.parquet

Outputs:
- results/tables/table_02_country_ranking.csv (Top-30 with publication, citation, MCP stats)
- results/tables/table_02b_collaboration_matrix.csv (country x country co-authorship)
- results/figures/figure_03_top_countries.png (Top-20 bar chart, color-coded by region)
- data/processed/country_collaboration_pairs.parquet (for Block 2C VOSviewer export)

Run:
    python 03_descriptive_analysis/03_country_ranking.py
"""

from pathlib import Path
from collections import Counter
from itertools import combinations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Country full names (for table readability)
COUNTRY_NAMES = {
    "CN": "Chinese Mainland", "US": "United States", "IN": "India", "HK": "Hong Kong (China)",
    "KR": "South Korea", "GB": "United Kingdom", "JP": "Japan", "TW": "Taiwan (China)",
    "AU": "Australia", "DE": "Germany", "CA": "Canada", "SA": "Saudi Arabia",
    "MO": "Macao (China)", "IT": "Italy", "ZA": "South Africa", "MY": "Malaysia",
    "SG": "Singapore", "TH": "Thailand", "BR": "Brazil", "NL": "Netherlands",
    "ES": "Spain", "FR": "France", "IR": "Iran",
    "IQ": "Iraq", "EG": "Egypt", "TR": "Turkey",
    "BE": "Belgium", "CH": "Switzerland", "SE": "Sweden", "NO": "Norway",
    "DK": "Denmark", "RS": "Serbia",
    "IL": "Israel", "PT": "Portugal", "PL": "Poland",
    "AT": "Austria", "FI": "Finland", "IE": "Ireland", "GR": "Greece",
    "PK": "Pakistan", "ID": "Indonesia", "PH": "Philippines", "VN": "Vietnam",
    "NZ": "New Zealand", "MX": "Mexico", "AR": "Argentina", "CL": "Chile",
    "RU": "Russia", "UA": "Ukraine", "RO": "Romania", "HU": "Hungary",
    "CZ": "Czech Republic", "BG": "Bulgaria", "JO": "Jordan", "LB": "Lebanon",
    "AE": "UAE", "QA": "Qatar", "MA": "Morocco", "NG": "Nigeria", "KE": "Kenya",
    "ET": "Ethiopia", "GH": "Ghana", "TN": "Tunisia", "DZ": "Algeria",
    "NP": "Nepal", "LK": "Sri Lanka", "BD": "Bangladesh", "MM": "Myanmar",
    "KZ": "Kazakhstan", "MN": "Mongolia",
    # Late additions (Day 3 patch — countries with >=10 publications)
    "PS": "Palestine",
    "ZW": "Zimbabwe",
    "CU": "Cuba",
    "MU": "Mauritius",
    "BW": "Botswana",
    "NA": "Namibia",
}

# Region groupings for color coding
REGION_GROUPS = {
    "China (mainland & regions)": {"CN", "HK", "TW", "MO"},
    "Asia (other)":  {"IN", "KR", "JP", "MY", "SG", "TH", "VN", "PH", "ID",
                      "PK", "BD", "LK", "NP", "MM", "MN", "KZ", "ID"},
    "North America": {"US", "CA", "MX"},
    "Europe":        {"GB", "DE", "IT", "ES", "FR", "NL", "BE", "CH", "AT",
                      "SE", "NO", "DK", "FI", "IE", "PT", "PL", "CZ", "HU",
                      "RO", "BG", "GR", "UA", "RU"},
    "Oceania":       {"AU", "NZ"},
    "Middle East":   {"SA", "IR", "TR", "IL", "AE", "QA", "LB", "JO", "EG"},
    "Africa":        {"ZA", "NG", "KE", "ET", "GH", "TN", "DZ", "MA"},
    "Latin America": {"BR", "AR", "CL"},
}

REGION_COLORS = {
    "China (mainland & regions)": "#C04848",   # red
    "Asia (other)":  "#E89C50",   # orange
    "North America": "#5B8DD6",   # blue
    "Europe":        "#5BA68D",   # green
    "Oceania":       "#A88BB9",   # purple
    "Middle East":   "#D4A04C",   # gold
    "Africa":        "#8B6F47",   # brown
    "Latin America": "#CC7494",   # pink
    "Other":         "#888888",   # gray
}


def get_region(country_code):
    for region, codes in REGION_GROUPS.items():
        if country_code in codes:
            return region
    return "Other"


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 2B: Country Ranking + International Collaboration")
    print("=" * 70)
    
    # Load data
    print("\n[1] Loading data...")
    df_corpus = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    df_cl = pd.read_parquet(repo_root / "data/processed/country_lookup.parquet")
    df = df_corpus.merge(
        df_cl[["record_id", "country_codes", "country_count"]],
        on="record_id", how="left"
    )
    print(f"    Total records: {len(df):,}")
    
    # Filter to records WITH country
    df_with_country = df[df["country_count"] > 0].copy()
    print(f"    Records with country: {len(df_with_country):,} "
          f"({100*len(df_with_country)/len(df):.1f}%)")
    
    # ============ Step 2: Country-level stats ============
    print("\n[2] Computing country-level statistics...")
    
    country_pub_count = Counter()
    country_citations = Counter()  # sum of citations
    country_pub_list = {}  # country -> list of cited_by for averaging
    country_mcp_count = Counter()  # multi-country publications
    
    for _, row in df_with_country.iterrows():
        countries = row["country_codes"]
        cited = row.get("cited_by", 0) or 0
        is_mcp = len(countries) > 1
        
        for c in countries:
            country_pub_count[c] += 1
            country_citations[c] += cited
            country_pub_list.setdefault(c, []).append(cited)
            if is_mcp:
                country_mcp_count[c] += 1
    
    # Build ranking dataframe
    ranking = []
    for c in country_pub_count:
        n_pub = country_pub_count[c]
        n_mcp = country_mcp_count[c]
        total_cit = country_citations[c]
        avg_cit = round(total_cit / n_pub, 1) if n_pub > 0 else 0
        ranking.append({
            "country_code": c,
            "country_name": COUNTRY_NAMES.get(c, c),
            "region": get_region(c),
            "n_publications": n_pub,
            "pct_of_attributed": round(100 * n_pub / len(df_with_country), 2),
            "n_total_citations": int(total_cit),
            "avg_citations": avg_cit,
            "n_mcp_publications": n_mcp,
            "mcp_ratio_pct": round(100 * n_mcp / n_pub, 1) if n_pub > 0 else 0,
        })
    
    rank_df = pd.DataFrame(ranking).sort_values("n_publications", ascending=False).reset_index(drop=True)
    rank_df["rank"] = rank_df.index + 1
    rank_df = rank_df[["rank", "country_code", "country_name", "region",
                       "n_publications", "pct_of_attributed",
                       "n_total_citations", "avg_citations",
                       "n_mcp_publications", "mcp_ratio_pct"]]
    
    # Print Top 30
    print(f"\n[3] Top 30 countries by publication count:")
    print(f"    {'Rank':<5} {'Country':<20s} {'Region':<18s} {'N_Pub':>7s} {'%':>6s} "
          f"{'AvgCit':>7s} {'MCP%':>6s}")
    print(f"    {'-'*4:<5} {'-'*20:<20s} {'-'*18:<18s} {'-'*7:>7s} {'-'*6:>6s} "
          f"{'-'*7:>7s} {'-'*6:>6s}")
    for _, row in rank_df.head(30).iterrows():
        print(f"    {int(row['rank']):<5} {row['country_name']:<20s} {row['region']:<18s} "
              f"{int(row['n_publications']):>7,} {row['pct_of_attributed']:>5.1f}% "
              f"{row['avg_citations']:>7.1f} {row['mcp_ratio_pct']:>5.1f}%")
    
    # ============ Step 3: Single-country vs Multi-country ============
    print(f"\n[4] Single-Country (SCP) vs Multi-Country (MCP) Publications:")
    n_scp = (df_with_country["country_count"] == 1).sum()
    n_mcp_total = (df_with_country["country_count"] >= 2).sum()
    print(f"    SCP (single country):       {n_scp:,} ({100*n_scp/len(df_with_country):.1f}%)")
    print(f"    MCP (multi-country):        {n_mcp_total:,} ({100*n_mcp_total/len(df_with_country):.1f}%)")
    print(f"    Mean countries per MCP:     {df_with_country[df_with_country['country_count']>=2]['country_count'].mean():.2f}")
    
    # ============ Step 4: Bilateral collaboration matrix ============
    print(f"\n[5] Building bilateral collaboration matrix...")
    pair_counter = Counter()
    for _, row in df_with_country.iterrows():
        countries = row["country_codes"]
        if len(countries) >= 2:
            for c1, c2 in combinations(sorted(set(countries)), 2):
                pair_counter[(c1, c2)] += 1
    
    pair_df = pd.DataFrame([
        {"country_a": a, "country_b": b, "co_publications": n}
        for (a, b), n in pair_counter.most_common()
    ])
    print(f"    Unique bilateral pairs: {len(pair_df):,}")
    print(f"\n    Top 15 collaboration pairs:")
    for _, row in pair_df.head(15).iterrows():
        ca, cb = row["country_a"], row["country_b"]
        name_a = COUNTRY_NAMES.get(ca, ca)
        name_b = COUNTRY_NAMES.get(cb, cb)
        print(f"    {name_a:>20s} <-> {name_b:<20s} {int(row['co_publications']):>5,}")
    
    # ============ Step 5: Save outputs ============
    out_tables = repo_root / "results" / "tables"
    out_figs = repo_root / "results" / "figures"
    out_data = repo_root / "data" / "processed"
    
    rank_df.to_csv(out_tables / "table_02_country_ranking.csv", index=False, encoding="utf-8")
    pair_df.to_csv(out_tables / "table_02b_collaboration_matrix.csv", index=False, encoding="utf-8")
    pair_df.to_parquet(out_data / "country_collaboration_pairs.parquet", index=False)
    
    # ============ Step 6: Figure 3 — Top 20 bar chart ============
    print(f"\n[6] Building Figure 3 (Top-20 country bar chart)...")
    top20 = rank_df.head(20).copy()
    top20 = top20.iloc[::-1]  # reverse for horizontal bar (Top at top)
    
    fig, ax = plt.subplots(figsize=(11, 8.5))
    
    # Color bars by region
    colors = [REGION_COLORS.get(r, "#888") for r in top20["region"]]
    bars = ax.barh(top20["country_name"], top20["n_publications"],
                    color=colors, edgecolor="white", linewidth=0.8)
    
    # Add count labels
    for bar, n in zip(bars, top20["n_publications"]):
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                f"{int(n):,}", va="center", fontsize=9.5, color="#333")
    
    ax.set_xlabel("Number of Publications", fontweight="bold")
    ax.set_title("Top 20 Countries Contributing to TCM Herb-Drug Interaction Research\n(2005-2025, n=7,976 records with extractable affiliation)",
                 fontweight="bold", pad=12, fontsize=12)
    ax.set_xlim(0, top20["n_publications"].max() * 1.1)
    ax.grid(axis="x", alpha=0.3, linestyle=":")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    # Legend by region
    regions_in_top20 = list(dict.fromkeys(top20["region"][::-1]))  # preserve order, unique
    legend_patches = [mpatches.Patch(color=REGION_COLORS[r], label=r) for r in regions_in_top20]
    ax.legend(handles=legend_patches, loc="lower right", framealpha=0.95,
              title="Region", title_fontsize=10, fontsize=9)
    
    # Footer
    n_scp_pct = round(100 * n_scp / len(df_with_country), 1)
    n_mcp_pct = round(100 * n_mcp_total / len(df_with_country), 1)
    footer = (f"Single-country publications: {n_scp_pct}%   |   "
              f"Multi-country (international) collaboration: {n_mcp_pct}%   |   "
              f"Country attribution: {len(df_with_country):,}/{len(df):,} records")
    fig.text(0.5, 0.01, footer, ha="center", fontsize=9, style="italic", color="#555")
    
    plt.tight_layout()
    fig_path = out_figs / "figure_03_top_countries.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"\n[7] Outputs saved:")
    print(f"    {out_tables / 'table_02_country_ranking.csv'}")
    print(f"    {out_tables / 'table_02b_collaboration_matrix.csv'}")
    print(f"    {out_data / 'country_collaboration_pairs.parquet'}")
    print(f"    {fig_path}")
    
    # ============ Discussion-ready insights ============
    print("\n" + "=" * 70)
    print("DISCUSSION-READY INSIGHTS:")
    print("=" * 70)
    
    top1 = rank_df.iloc[0]
    top2 = rank_df.iloc[1]
    top3 = rank_df.iloc[2]
    china_total_n = sum(rank_df[rank_df['country_code'].isin(['CN','HK','TW','MO'])]['n_publications'])
    
    print(f"""
1. GEOGRAPHIC LANDSCAPE:
   "Geographic analysis of {len(df_with_country):,} records with extractable affiliation
   revealed an Asia-Pacific-centered research landscape. {top1['country_name']} 
   ({int(top1['n_publications']):,} publications, {top1['pct_of_attributed']}% of attributed)
   dominated, followed by {top2['country_name']} (n={int(top2['n_publications']):,}, 
   {top2['pct_of_attributed']}%) and {top3['country_name']} (n={int(top3['n_publications']):,},
   {top3['pct_of_attributed']}%)."

2. CHINA (AGGREGATED):
   "China collectively—including the Chinese mainland, Hong Kong (China), Taiwan (China), and Macao (China)—
   contributed {china_total_n:,} publications, accounting for 
   {100*china_total_n/len(df_with_country):.1f}% of country-attributed records."

3. INTERNATIONAL COLLABORATION:
   "Of the {len(df_with_country):,} country-attributed publications, 
   {n_mcp_total:,} ({n_mcp_pct}%) involved international collaboration, 
   spanning {len(pair_df):,} unique bilateral partnerships."
""")


if __name__ == "__main__":
    main()
