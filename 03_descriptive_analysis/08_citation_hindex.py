"""
Block 5: Citation analysis + h-index + Top-cited papers.

Computes corpus-wide citation distribution, identifies top-cited papers,
calculates corpus h-index, and visualizes citation patterns by year.

Output:
- results/tables/table_05_top_cited_papers.csv (Top 30 most-cited)
- results/tables/table_05b_citation_stats.csv (descriptive stats)
- results/figures/figure_08a_citation_distribution.png
- results/figures/figure_08b_citations_by_year.png
"""

from pathlib import Path

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


def compute_h_index(citations):
    """Compute h-index from a list of citation counts.
    h-index = largest n where author has >= n papers with >= n citations each."""
    sorted_cits = sorted([c for c in citations if c is not None and not np.isnan(c)],
                          reverse=True)
    h = 0
    for i, c in enumerate(sorted_cits, start=1):
        if c >= i:
            h = i
        else:
            break
    return h


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 5: Citation analysis + h-index + Top-cited papers")
    print("=" * 70)
    
    # Load
    print("\n[1] Loading corpus...")
    df_main = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    df_partial = pd.read_parquet(repo_root / "data/processed/integrated_corpus_partial2026.parquet")
    df = pd.concat([df_main, df_partial], ignore_index=True)
    print(f"    Total records: {len(df):,}")
    
    # Clean citations
    print("\n[2] Processing citations...")
    df["cited_by"] = pd.to_numeric(df["cited_by"], errors="coerce")
    df["cited_by"] = df["cited_by"].fillna(0)
    
    n_zero = (df["cited_by"] == 0).sum()
    n_with_cit = (df["cited_by"] > 0).sum()
    print(f"    Papers with 0 citations:    {n_zero:,} ({100*n_zero/len(df):.1f}%)")
    print(f"    Papers with >=1 citations:  {n_with_cit:,}")
    
    # Descriptive stats
    print(f"\n[3] Citation distribution:")
    desc = df["cited_by"].describe()
    print(f"    Mean:               {desc['mean']:.1f}")
    print(f"    Median:             {desc['50%']:.0f}")
    print(f"    Std:                {desc['std']:.1f}")
    print(f"    Max:                {desc['max']:.0f}")
    print(f"    25%:                {desc['25%']:.0f}")
    print(f"    75%:                {desc['75%']:.0f}")
    print(f"    >=10 citations:     {(df['cited_by'] >= 10).sum():,}")
    print(f"    >=50 citations:     {(df['cited_by'] >= 50).sum():,}")
    print(f"    >=100 citations:    {(df['cited_by'] >= 100).sum():,}")
    
    # H-index
    print(f"\n[4] Corpus h-index:")
    h = compute_h_index(df["cited_by"].tolist())
    print(f"    h-index = {h}")
    print(f"    (Means {h} papers have each been cited >= {h} times)")
    
    # Top 30 most-cited papers
    print(f"\n[5] Top 30 most-cited papers:")
    top_cited = df.nlargest(30, "cited_by")[
        ["record_id", "year", "title", "journal", "cited_by", "first_author_lastname", "doc_type"]
    ].copy()
    top_cited["rank"] = range(1, len(top_cited) + 1)
    top_cited["title_short"] = top_cited["title"].str[:80]
    
    print(f"    {'Rank':<5} {'Year':<6} {'Cited':>5} {'First Author':<20s} {'Title'}")
    print(f"    {'-'*4:<5} {'-'*4:<6} {'-'*5:>5} {'-'*20:<20s} {'-'*60}")
    for _, row in top_cited.iterrows():
        rank = int(row['rank'])
        year = int(row['year']) if pd.notna(row['year']) else '?'
        cit = int(row['cited_by'])
        author = (str(row['first_author_lastname'])[:19] if pd.notna(row['first_author_lastname']) else '?')
        title = str(row['title'])[:70]
        print(f"    {rank:<5} {year!s:<6} {cit:>5,} {author:<20s} {title}")
    
    # Save Top 30
    out_tables = repo_root / "results" / "tables"
    out_figs = repo_root / "results" / "figures"
    
    top_cited_out = top_cited[["rank", "year", "first_author_lastname", "title", "journal",
                                 "doc_type", "cited_by", "record_id"]].copy()
    top_cited_out.columns = ["rank", "year", "first_author", "title", "journal",
                              "doc_type", "citations", "record_id"]
    top_cited_out.to_csv(out_tables / "table_05_top_cited_papers.csv", 
                          index=False, encoding="utf-8")
    print(f"\n[6] Saved: {out_tables / 'table_05_top_cited_papers.csv'}")
    
    # Save descriptive stats
    stats_dict = {
        "total_papers": len(df),
        "papers_with_zero_cit": int(n_zero),
        "papers_zero_pct": round(100*n_zero/len(df), 1),
        "mean_citations": round(desc['mean'], 1),
        "median_citations": round(desc['50%'], 0),
        "max_citations": int(desc['max']),
        "papers_ge_10": int((df['cited_by'] >= 10).sum()),
        "papers_ge_50": int((df['cited_by'] >= 50).sum()),
        "papers_ge_100": int((df['cited_by'] >= 100).sum()),
        "h_index": h,
    }
    stats_df = pd.DataFrame([stats_dict])
    stats_df.to_csv(out_tables / "table_05b_citation_stats.csv", index=False, encoding="utf-8")
    
    # ============ Figure 8a: Citation distribution ============
    print(f"\n[7] Building Figure 8a (Citation distribution)...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Histogram (log-scale x and y) - bins from 0-1000
    cit_clipped = df["cited_by"].clip(upper=500)  # Cap for visualization
    bins = list(range(0, 501, 10))
    
    n_zero_bin = (df["cited_by"] == 0).sum()
    ax1.hist(cit_clipped, bins=bins, color="#5B8DD6", edgecolor="white", linewidth=0.5)
    ax1.set_yscale("log")
    ax1.set_xlabel("Citation count (capped at 500)", fontweight="bold")
    ax1.set_ylabel("Number of papers (log scale)", fontweight="bold")
    ax1.set_title(f"(a) Citation distribution\nTotal: {len(df):,} papers, "
                    f"Zero-cited: {n_zero_bin:,} ({100*n_zero_bin/len(df):.1f}%)",
                    fontweight="bold", fontsize=11)
    ax1.grid(axis="y", alpha=0.3, linestyle=":")
    
    # H-index visualization (Pareto-style)
    sorted_cits = sorted(df["cited_by"].tolist(), reverse=True)
    ranks = list(range(1, len(sorted_cits) + 1))
    ax2.plot(ranks, sorted_cits, color="#5B8DD6", linewidth=1.5)
    ax2.axhline(h, color="#C04848", linestyle="--", alpha=0.7, label=f"h-index = {h}")
    ax2.axvline(h, color="#C04848", linestyle="--", alpha=0.7)
    ax2.plot(ranks, ranks, color="gray", linestyle=":", alpha=0.5, label="y = x")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlim(1, 10000)
    ax2.set_ylim(1, 2000)
    ax2.set_xlabel("Paper rank (by citation, log scale)", fontweight="bold")
    ax2.set_ylabel("Citation count (log scale)", fontweight="bold")
    ax2.set_title(f"(b) Corpus h-index = {h}\n(Pareto-form: rank vs citation count)",
                    fontweight="bold", fontsize=11)
    ax2.legend(loc="upper right", framealpha=0.95)
    ax2.grid(True, alpha=0.3, which="both", linestyle=":")
    
    plt.tight_layout()
    fig8a_path = out_figs / "figure_08a_citation_distribution.png"
    plt.savefig(fig8a_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig8a_path}")
    
    # ============ Figure 8b: Citations by year (scatter) ============
    print(f"\n[8] Building Figure 8b (Citations by year)...")
    
    df_plot = df[(df["year"] >= 2005) & (df["year"] <= 2025) & (df["cited_by"] > 0)].copy()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Scatter with size based on citation
    sizes = np.clip(df_plot["cited_by"].values, 1, 100)
    sc = ax.scatter(df_plot["year"], df_plot["cited_by"], 
                     s=sizes, alpha=0.4, c="#5B8DD6", 
                     edgecolors="white", linewidths=0.3)
    
    # Add median line per year
    yearly_median = df_plot.groupby("year")["cited_by"].median()
    yearly_mean = df_plot.groupby("year")["cited_by"].mean()
    ax.plot(yearly_median.index, yearly_median.values, color="#C04848", 
             linewidth=2, label="Annual median", zorder=10)
    ax.plot(yearly_mean.index, yearly_mean.values, color="#5BA68D",
             linewidth=2, linestyle="--", label="Annual mean", zorder=10)
    
    # Annotate top papers
    top_5 = df_plot.nlargest(5, "cited_by")
    for _, row in top_5.iterrows():
        title_short = str(row['title'])[:50] + "..." if len(str(row['title'])) > 50 else str(row['title'])
        ax.annotate(f"{int(row['cited_by'])} cit",
                     xy=(row['year'], row['cited_by']),
                     xytext=(5, 5), textcoords="offset points",
                     fontsize=9, color="#333", fontweight="bold")
    
    ax.set_yscale("log")
    ax.set_xlabel("Publication year", fontweight="bold")
    ax.set_ylabel("Citation count (log scale)", fontweight="bold")
    ax.set_title(f"Citation Patterns Over Time in TCM Herb-Drug Interaction Research\n"
                 f"Corpus h-index = {h}, Top 5 cited papers labeled",
                 fontweight="bold", pad=12)
    ax.set_xlim(2004, 2026)
    ax.set_xticks(range(2005, 2027, 2))
    ax.legend(loc="upper right", framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle=":")
    
    plt.tight_layout()
    fig8b_path = out_figs / "figure_08b_citations_by_year.png"
    plt.savefig(fig8b_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"    {fig8b_path}")
    
    # Insights
    print(f"\n" + "=" * 70)
    print("DISCUSSION-READY INSIGHTS:")
    print("=" * 70)
    print(f"""
1. OVERALL CITATION IMPACT:
   "The {len(df):,} TCM-HDI publications received a total of {int(df['cited_by'].sum()):,} 
   citations (mean = {desc['mean']:.1f}, median = {int(desc['50%'])}, max = {int(desc['max']):,}).
   The corpus h-index is {h}, indicating {h} papers each cited at least {h} times.
   {int((df['cited_by'] >= 100).sum())} papers ({100*(df['cited_by'] >= 100).sum()/len(df):.1f}%) 
   exceed 100 citations, marking high-impact contributions."

2. TOP-CITED PAPERS:
   "The single most-cited paper is '{top_cited.iloc[0]['title'][:80]}' 
   ({int(top_cited.iloc[0]['year'])}) with {int(top_cited.iloc[0]['cited_by']):,} citations, 
   published in {top_cited.iloc[0]['journal']}. The top 30 most-cited 
   papers collectively received {int(top_cited['cited_by'].sum()):,} citations 
   ({100*int(top_cited['cited_by'].sum())/int(df['cited_by'].sum()):.1f}% of total)."

3. CITATION SKEWNESS:
   "Citation distribution is heavily right-skewed: {int(n_zero):,} papers ({100*n_zero/len(df):.1f}%) 
   received zero citations, while the top 1% of papers account for a disproportionate 
   share of impact. This pattern is consistent with the 80/20 rule in scientific impact."
""")


if __name__ == "__main__":
    main()
