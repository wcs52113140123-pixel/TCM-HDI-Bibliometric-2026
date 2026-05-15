"""
Day 4 Block 1: PRISMA 2020 flow diagram.

Constructs a PRISMA 2020-compliant flow diagram from prisma_flow_data.json
showing identification, screening, eligibility, and inclusion phases.

Output:
- results/figures/figure_01_prisma_flow.png

Run:
    python 04_keyword_topic/01_prisma_flow_diagram.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import FancyArrowPatch


def draw_box(ax, x, y, width, height, text, color="#E8E8E8", edge_color="#333", fontsize=10, fontweight="normal"):
    """Draw a rounded rectangle box with centered text."""
    box = FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        facecolor=color, edgecolor=edge_color, linewidth=1.2
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, 
             fontweight=fontweight, wrap=True, color="#1a1a1a")


def draw_arrow(ax, x1, y1, x2, y2, label=None):
    """Draw arrow with optional label."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=15, color="#555", linewidth=1.2
    )
    ax.add_patch(arrow)
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x + 0.05, mid_y, label, fontsize=9, color="#666", style="italic")


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Day 4 Block 1: PRISMA 2020 flow diagram")
    print("=" * 70)
    
    # Load PRISMA data
    print("\n[1] Loading prisma_flow_data.json...")
    with open(repo_root / "data/processed/prisma_flow_data.json", encoding="utf-8") as f:
        data = json.load(f)
    
    ident = data["identification"]
    doi_step = data["doi_deduplication"]
    fuzzy_step = data["fuzzy_deduplication"]
    prec_step = data["precision_filter"]
    
    print(f"    Raw total: {ident['total_raw']:,}")
    print(f"    Final corpus: {data['final_corpus_size']:,}")
    
    # ============ Build the diagram ============
    print("\n[2] Building PRISMA flow diagram...")
    
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.set_aspect("equal")
    ax.axis("off")
    
    # Color scheme
    color_id = "#D4E8F0"      # Identification - light blue
    color_screen = "#FFE9B3"  # Screening - light orange
    color_elig = "#F8D5A0"    # Eligibility - medium orange
    color_incl = "#A8D8A8"    # Included - light green
    color_excl = "#F5C5C5"    # Excluded - light red
    
    # === Phase labels (left side bars) ===
    phase_labels = [
        (0.6, 12.5, "IDENTIFICATION", color_id),
        (0.6, 9.5, "SCREENING", color_screen),
        (0.6, 6.5, "ELIGIBILITY", color_elig),
        (0.6, 2.5, "INCLUDED", color_incl),
    ]
    for x, y, lbl, col in phase_labels:
        box = FancyBboxPatch(
            (x - 0.5, y - 0.4), 1.0, 0.8,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=col, edgecolor="#333", linewidth=1.2
        )
        ax.add_patch(box)
        ax.text(x, y, lbl, ha="center", va="center", fontsize=10,
                 fontweight="bold", rotation=90, color="#1a1a1a")
    
    # === IDENTIFICATION boxes (top, 4 databases) ===
    db_y = 12.8
    box_w_db = 1.7
    box_h_db = 1.4
    db_data = [
        (2.5, db_y, "Web of Science\nCore Collection", ident["WoS_raw"]),
        (4.4, db_y, "Scopus", ident["Scopus_raw"]),
        (6.3, db_y, "OpenAlex", ident["OpenAlex_raw"]),
        (8.2, db_y, "PubMed/MEDLINE", ident["PubMed_raw"]),
    ]
    for x, y, name, n in db_data:
        draw_box(ax, x, y, box_w_db, box_h_db,
                 f"{name}\nn = {n:,}",
                 color=color_id, fontsize=9.5)
    
    # Arrows from databases to merged total
    for x, y, _, _ in db_data:
        ax.plot([x, 5.35], [y - 0.7, 11.3], color="#777", linewidth=1, alpha=0.6)
    
    # === Merged total box ===
    draw_box(ax, 5.35, 10.7, 4.5, 1.0,
             f"Records identified from databases\nn = {ident['total_raw']:,}",
             color=color_id, fontsize=10.5, fontweight="bold")
    
    draw_arrow(ax, 5.35, 10.2, 5.35, 9.8)
    
    # === SCREENING: DOI dedup ===
    draw_box(ax, 5.35, 9.3, 4.5, 1.0,
             f"Records after DOI-based deduplication\nn = {doi_step['output']:,}",
             color=color_screen, fontsize=10.5, fontweight="bold")
    
    # Excluded box (DOI dedup)
    draw_box(ax, 8.7, 9.85, 2.2, 1.0,
             f"DOI duplicates removed\nn = {doi_step['duplicates_removed']:,}",
             color=color_excl, fontsize=9)
    draw_arrow(ax, 7.6, 9.85, 7.6, 9.85)  # placeholder
    
    # Connection: merged -> dedup -> excluded
    ax.plot([7.6, 7.6], [10.7, 9.85], color="#777", linewidth=1)
    ax.annotate("", xy=(7.6, 9.85), xytext=(7.6, 10.4),
                 arrowprops=dict(arrowstyle="->", color="#777"))
    
    draw_arrow(ax, 5.35, 8.8, 5.35, 8.4)
    
    # === Fuzzy dedup ===
    draw_box(ax, 5.35, 7.9, 4.5, 1.0,
             f"Records after fuzzy title-year-author deduplication\n"
             f"(RapidFuzz threshold ≥{fuzzy_step['threshold']}%)\nn = {fuzzy_step['output']:,}",
             color=color_screen, fontsize=10, fontweight="bold")
    
    # Excluded fuzzy dedup
    draw_box(ax, 8.7, 8.45, 2.2, 1.0,
             f"Fuzzy duplicates\nremoved\nn = {fuzzy_step['records_removed']:,}",
             color=color_excl, fontsize=9)
    ax.plot([7.6, 7.6], [8.9, 8.45], color="#777", linewidth=1)
    ax.annotate("", xy=(7.6, 8.45), xytext=(7.6, 8.7),
                 arrowprops=dict(arrowstyle="->", color="#777"))
    
    draw_arrow(ax, 5.35, 7.4, 5.35, 7.0)
    
    # === ELIGIBILITY: Precision filter ===
    draw_box(ax, 5.35, 6.4, 4.5, 1.2,
             f"OpenAlex-exclusive records re-screened\n"
             f"via B1+B2+B3 boolean filter\n"
             f"({prec_step['openalex_passed_B1B2B3']:,} retained from "
             f"{prec_step['openalex_exclusive']:,} candidates)",
             color=color_elig, fontsize=10, fontweight="bold")
    
    # Excluded precision
    excluded_oa = prec_step['openalex_exclusive'] - prec_step['openalex_passed_B1B2B3']
    draw_box(ax, 8.7, 6.95, 2.2, 1.2,
             f"OpenAlex records\nfailing precision filter\nn = {excluded_oa:,}",
             color=color_excl, fontsize=9)
    ax.plot([7.6, 7.6], [7.4, 6.95], color="#777", linewidth=1)
    ax.annotate("", xy=(7.6, 6.95), xytext=(7.6, 7.2),
                 arrowprops=dict(arrowstyle="->", color="#777"))
    
    draw_arrow(ax, 5.35, 5.8, 5.35, 5.4)
    
    # === Sub-corpus assignment ===
    draw_box(ax, 5.35, 4.8, 4.5, 1.0,
             f"Records partitioned: Main (2005-2025) + Partial (2026)\n"
             f"Main: 9,438  |  Partial: 316",
             color=color_elig, fontsize=10, fontweight="bold")
    
    draw_arrow(ax, 5.35, 4.3, 5.35, 3.9)
    
    # === INCLUDED ===
    draw_box(ax, 5.35, 3.3, 5.5, 1.2,
             f"Studies included in bibliometric analysis\n"
             f"Total: 9,438 (main 2005-2025)\n"
             f"Plus 316 partial 2026 records",
             color=color_incl, fontsize=11, fontweight="bold")
    
    # Bottom: data sources for analysis
    draw_box(ax, 2.5, 1.4, 2.5, 1.2,
             f"4-database integrated\ncorpus\n9,754 unique records",
             color=color_incl, fontsize=10)
    draw_box(ax, 5.35, 1.4, 2.5, 1.2,
             f"Source attribution:\nWoS / Scopus /\nOpenAlex / PubMed",
             color=color_incl, fontsize=10)
    draw_box(ax, 8.2, 1.4, 2.5, 1.2,
             f"Citation, journal,\nauthor, affiliation,\nkeyword fields",
             color=color_incl, fontsize=10)
    
    ax.plot([5.35, 2.5], [2.7, 2.0], color="#777", linewidth=1)
    ax.plot([5.35, 5.35], [2.7, 2.0], color="#777", linewidth=1)
    ax.plot([5.35, 8.2], [2.7, 2.0], color="#777", linewidth=1)
    
    # === Title ===
    fig.suptitle("PRISMA 2020 Flow Diagram\n"
                 "TCM Herb-Drug Interaction Bibliometric Analysis (2005-2025)",
                 fontsize=13, fontweight="bold", y=0.97)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    out_path = repo_root / "results" / "figures" / "figure_01_prisma_flow.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"\n[3] Saved: {out_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("PRISMA Summary:")
    print(f"  Identified across 4 DBs:     {ident['total_raw']:,}")
    print(f"  After DOI dedup:             {doi_step['output']:,}  (-{doi_step['duplicates_removed']:,})")
    print(f"  After fuzzy dedup:           {fuzzy_step['output']:,}  (-{fuzzy_step['records_removed']:,})")
    print(f"  After precision filter:      {prec_step['output']:,}  (-{excluded_oa:,})")
    print(f"  FINAL CORPUS:                {data['final_corpus_size']:,}")
    print("=" * 70)


if __name__ == "__main__":
    main()
