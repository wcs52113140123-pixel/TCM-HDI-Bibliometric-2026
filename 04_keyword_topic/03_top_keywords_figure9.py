"""
Day 4 Block 3: Top 50 keywords table + Figure 9.

Output:
- results/tables/table_06_top_keywords.csv (Top 50)
- results/figures/figure_09a_top_keywords.png (Top 30 horizontal bar)
- results/figures/figure_09b_keywords_by_source.png (stacked source breakdown)
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
    print("Block 3: Top 50 keywords + Figure 9")
    print("=" * 70)
    
    # Load
    print("\n[1] Loading data...")
    lookup = pd.read_parquet(repo_root / "data/processed/keyword_lookup.parquet")
    print(f"    Total unique keywords: {len(lookup):,}")
    
    # Top 50 table
    top50 = lookup.head(50).copy()
    top50["pct_records"] = (100 * top50["n_records"] / 9754).round(2)
    
    print(f"\n[2] Top 50 keywords:")
    print(f"    {'Rank':<5} {'N':>5} {'%':>6} {'Auth':>4} {'K+':>4} {'MeSH':>4}  Keyword")
    print(f"    {'-'*4:<5} {'-'*5:>5} {'-'*6:>6} {'-'*4:>4} {'-'*4:>4} {'-'*4:>4}  {'-'*40}")
    for _, row in top50.iterrows():
        ak = int(row.get('n_author_keywords', 0))
        kp = int(row.get('n_keywords_plus', 0))
        mh = int(row.get('n_mesh_terms', 0))
        print(f"    {int(row['rank']):<5} {int(row['n_records']):>5,} "
              f"{row['pct_records']:>5.1f}% {ak:>4} {kp:>4} {mh:>4}  {row['keyword']}")
    
    # Save Table 6
    out_tables = repo_root / "results" / "tables"
    out_tables.mkdir(parents=True, exist_ok=True)
    top50_out = top50[["rank", "keyword", "n_records", "pct_records",
                        "n_author_keywords", "n_keywords_plus", "n_mesh_terms"]]
    top50_out.columns = ["rank", "keyword", "n_records", "pct_records",
                          "n_author_kw", "n_keywords_plus", "n_mesh"]
    top50_out.to_csv(out_tables / "table_06_top_keywords.csv", index=False, encoding="utf-8")
    print(f"\n[3] Saved: {out_tables / 'table_06_top_keywords.csv'}")
    
    # ============ Figure 9a: Top 30 horizontal bar with source breakdown ============
    print(f"\n[4] Building Figure 9a (Top 30 keywords stacked bar)...")
    top30 = lookup.head(30).copy().iloc[::-1]
    
    fig, ax = plt.subplots(figsize=(13, 11))
    
    # Stacked bars
    ak = top30["n_author_keywords"].values
    kp = top30["n_keywords_plus"].values
    mh = top30["n_mesh_terms"].values
    
    y_pos = np.arange(len(top30))
    
    ax.barh(y_pos, ak, color="#5B8DD6", edgecolor="white", linewidth=0.5, 
             label=f"Author Keywords (n={ak.sum():,})")
    ax.barh(y_pos, kp, left=ak, color="#C04848", edgecolor="white", linewidth=0.5,
             label=f"WoS Keywords Plus (n={kp.sum():,})")
    ax.barh(y_pos, mh, left=ak+kp, color="#5BA68D", edgecolor="white", linewidth=0.5,
             label=f"MeSH Terms (n={mh.sum():,})")
    
    # Total label at end of bars
    totals = top30["n_records"].values
    for y, total in zip(y_pos, totals):
        ax.text(total + 15, y, f"{int(total):,}", va="center", fontsize=9.5, color="#333")
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top30["keyword"].values)
    ax.set_xlabel("Number of Records", fontweight="bold")
    ax.set_title("Top 30 Most-Frequent Keywords in TCM Herb-Drug Interaction Research\n"
                 "(2005-2025, post-thesaurus consolidation; stacked by source)",
                 fontweight="bold", pad=12, fontsize=11.5)
    ax.set_xlim(0, totals.max() * 1.12)
    ax.legend(loc="lower right", framealpha=0.95)
    ax.grid(axis="x", alpha=0.3, linestyle=":")
    
    plt.tight_layout()
    fig9a_path = repo_root / "results/figures/figure_09a_top_keywords.png"
    plt.savefig(fig9a_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig9a_path}")
    
    # ============ Figure 9b: Source composition pie + breakdown ============
    print(f"\n[5] Building Figure 9b (Keyword source composition)...")
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    
    # Subplot 1: Overall source breakdown (all keywords)
    src_totals = {
        "Author Keywords": lookup["n_author_keywords"].sum(),
        "WoS Keywords Plus": lookup["n_keywords_plus"].sum(),
        "MeSH Terms": lookup["n_mesh_terms"].sum(),
    }
    colors_pie = ["#5B8DD6", "#C04848", "#5BA68D"]
    
    axes[0].pie(src_totals.values(), labels=src_totals.keys(), autopct="%1.1f%%",
                 colors=colors_pie, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    axes[0].set_title(f"(a) Overall keyword source distribution\n"
                       f"Total (record, kw) pairs: {sum(src_totals.values()):,}",
                       fontweight="bold", fontsize=12)
    
    # Subplot 2: Top 30 source breakdown stacked
    top30_for_pie = lookup.head(30)
    src_top30 = {
        "Author Keywords": top30_for_pie["n_author_keywords"].sum(),
        "WoS Keywords Plus": top30_for_pie["n_keywords_plus"].sum(),
        "MeSH Terms": top30_for_pie["n_mesh_terms"].sum(),
    }
    
    axes[1].pie(src_top30.values(), labels=src_top30.keys(), autopct="%1.1f%%",
                 colors=colors_pie, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    axes[1].set_title(f"(b) Top 30 keyword source composition\n"
                       f"Top 30 pairs: {sum(src_top30.values()):,}",
                       fontweight="bold", fontsize=12)
    
    plt.suptitle("Keyword Source Composition in TCM-HDI Research", 
                  fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    
    fig9b_path = repo_root / "results/figures/figure_09b_keywords_by_source.png"
    plt.savefig(fig9b_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig9b_path}")
    
    # Insights
    print(f"\n" + "=" * 70)
    print("DISCUSSION-READY INSIGHTS:")
    print("=" * 70)
    print(f"""
1. CORE TERMINOLOGY:
   "The top 5 keywords — 'traditional chinese medicine' (n={int(lookup.iloc[0]['n_records']):,}), 
   'herb-drug interaction' ({int(lookup.iloc[1]['n_records']):,}), 'pharmacokinetics' 
   ({int(lookup.iloc[2]['n_records']):,}), 'drug interaction' ({int(lookup.iloc[3]['n_records']):,}), 
   and 'cytochrome p450' ({int(lookup.iloc[4]['n_records']):,}) — form a coherent terminology 
   pyramid reflecting the field's research focus on pharmacokinetic drug interactions 
   between TCM products and conventional drugs."

2. METHODOLOGICAL PARADIGMS:
   "Network pharmacology (n={int(lookup[lookup['keyword']=='network pharmacology']['n_records'].iloc[0]):,}) 
   and molecular docking (n={int(lookup[lookup['keyword']=='molecular docking']['n_records'].iloc[0]):,}) 
   appear among the Top 30, indicating widespread adoption of in silico methods 
   in TCM-HDI research, particularly after 2015."

3. ADME PATHWAY FOCUS:
   "Cytochrome P450 ({int(lookup[lookup['keyword']=='cytochrome p450']['n_records'].iloc[0]):,}) 
   and P-glycoprotein ({int(lookup[lookup['keyword']=='p-glycoprotein']['n_records'].iloc[0]):,}) 
   constitute the dominant mechanistic foci, reflecting the field's emphasis on 
   pharmacokinetic interactions through Phase I metabolism and ABC transporters."

4. CLINICAL ENDPOINTS:
   "Liver toxicity, cancer/apoptosis, and oxidative stress emerge as the principal 
   biological outcomes investigated, consistent with TCM's therapeutic spectrum."
""")


if __name__ == "__main__":
    main()
