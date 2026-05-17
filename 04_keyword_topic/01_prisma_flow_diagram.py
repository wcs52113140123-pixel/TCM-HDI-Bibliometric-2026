"""
Day 16 Block 2c: PRISMA 2020 flow diagram (refresh with Stage 5 cross-file dedup).

Replaces the Day 4 version (generated 2026-05-15 13:34) which reflected the
pre-cross-dedup-fix corpus (9,438 main / 316 partial). Day 5 cross-file dedup
(2026-05-15 16:48) reduced this to 9,413 main / 304 partial; fig01 must reflect
the actual final analysis corpus.

Outputs (paper-grade, 3 formats):
- results/figures/figure_01_prisma_flow.pdf  (vector, paper submission)
- results/figures/figure_01_prisma_flow.svg  (vector, online supplementary)
- results/figures/figure_01_prisma_flow.png  (300 DPI raster preview)

Run:
    python 04_keyword_topic/01_prisma_flow_diagram.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# ============ Helpers ============

def draw_box(ax, x, y, width, height, text,
             facecolor="#E8E8E8", edgecolor="#333",
             fontsize=10, fontweight="normal"):
    """Rounded rectangle box with centered text."""
    box = FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=1.2,
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight,
            wrap=True, color="#1a1a1a")


def draw_arrow(ax, x1, y1, x2, y2):
    """Arrow with filled triangular head."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=15,
        color="#555", linewidth=1.2,
    )
    ax.add_patch(arrow)


# ============ Main ============

def main():
    repo_root = Path(__file__).resolve().parent.parent

    print("=" * 70)
    print("Day 16 Block 2c: PRISMA 2020 flow diagram (refresh, 5 stages)")
    print("=" * 70)

    # Load PRISMA data
    print("\n[1] Loading prisma_flow_data.json...")
    with open(repo_root / "data/processed/prisma_flow_data.json", encoding="utf-8") as f:
        data = json.load(f)

    ident      = data["identification"]
    doi_step   = data["doi_deduplication"]
    fuzzy_step = data["fuzzy_deduplication"]
    prec_step  = data["precision_filter"]
    cross_step = data["cross_file_deduplication"]
    final_n    = data["final_corpus_size"]
    partial_n  = data["partial_2026_corpus_size"]
    total_n    = data["total_corpus_size"]

    prec_dropped = prec_step["block_breakdown"]["B0_none"]

    print(f"    Raw total (4 DBs):      {ident['total_raw']:,}")
    print(f"    After DOI dedup:        {doi_step['output']:,}  (-{doi_step['duplicates_removed']:,})")
    print(f"    After fuzzy dedup:      {fuzzy_step['output']:,}  (-{fuzzy_step['records_removed']:,})")
    print(f"    After precision filter: {prec_step['output']:,}  (-{prec_dropped:,})")
    print(f"    After cross-file:       {cross_step['output_main']:,}  (-{cross_step['records_removed_from_main']:,})  [Stage 5, NEW]")
    print(f"    Final main:             {final_n:,}")
    print(f"    Partial 2026:           {partial_n:,}")
    print(f"    Total analysis corpus:  {total_n:,}")

    # ============ Build diagram ============
    print("\n[2] Building diagram (5 stages + 4 sidearms + final box)...")

    fig, ax = plt.subplots(figsize=(13, 17))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 17)
    ax.set_aspect("equal")
    ax.axis("off")

    # PRISMA 2020 color scheme
    C_ID     = "#D4E8F0"
    C_SCREEN = "#FFE9B3"
    C_ELIG   = "#F8D5A0"
    C_INCL   = "#A8D8A8"
    C_SIDE   = "#F0F0F0"

    # Geometry
    PHASE_X = 0.5
    CX      = 4.5
    MAIN_W  = 5.0
    MAIN_H  = 1.1
    SIDE_X  = 9.5
    SIDE_W  = 3.5
    SIDE_H  = 1.0

    # Title
    ax.text(6.0, 16.7,
            "Figure 1. PRISMA 2020 flow diagram for TCM-herbal-drug interaction "
            "bibliometric review",
            ha="center", va="center", fontsize=13, fontweight="bold")
    ax.text(6.0, 16.2,
            "(Web of Science + Scopus + OpenAlex + PubMed; 2005-2026, search executed 2026-05-14)",
            ha="center", va="center", fontsize=10, color="#555", style="italic")

    # Phase labels (rotated 90 deg, left margin)
    phase_kw = dict(rotation=90, ha="center", va="center",
                    fontsize=12, fontweight="bold", color="#444")
    ax.text(PHASE_X, 15.0, "IDENTIFICATION", **phase_kw)
    ax.text(PHASE_X, 11.0, "SCREENING",      **phase_kw)
    ax.text(PHASE_X, 6.7,  "ELIGIBILITY",    **phase_kw)
    ax.text(PHASE_X, 3.0,  "INCLUDED",       **phase_kw)

    # ============ Identification: 4 DB boxes ============
    db_y = 15.4
    db_w, db_h = 1.8, 0.85
    db_data = [
        (2.0, "Web of Science",  ident["WoS_raw"]),
        (4.2, "Scopus",           ident["Scopus_raw"]),
        (6.4, "OpenAlex",         ident["OpenAlex_raw"]),
        (8.6, "PubMed",           ident["PubMed_raw"]),
    ]
    for x, name, n in db_data:
        draw_box(ax, x, db_y, db_w, db_h,
                 f"{name}\nn = {n:,}",
                 facecolor=C_ID, fontsize=9)

    # ID merge box
    id_merge_y = 13.7
    draw_box(ax, CX, id_merge_y, MAIN_W, MAIN_H,
             f"Records identified from 4 databases\nN = {ident['total_raw']:,}",
             facecolor=C_ID, fontsize=11, fontweight="bold")

    # Arrows: 4 DBs -> ID merge
    for x, _, _ in db_data:
        draw_arrow(ax, x, db_y - db_h/2, CX, id_merge_y + MAIN_H/2)

    # ============ Screening: Stages 2 + 3 ============
    s2_y = 11.7
    draw_box(ax, CX, s2_y, MAIN_W, MAIN_H,
             f"Records after DOI deduplication\nN = {doi_step['output']:,}",
             facecolor=C_SCREEN, fontsize=11)
    draw_box(ax, SIDE_X, s2_y, SIDE_W, SIDE_H,
             f"DOI duplicates removed:\nn = {doi_step['duplicates_removed']:,}",
             facecolor=C_SIDE, fontsize=9)
    draw_arrow(ax, CX + MAIN_W/2, s2_y, SIDE_X - SIDE_W/2, s2_y)
    draw_arrow(ax, CX, id_merge_y - MAIN_H/2, CX, s2_y + MAIN_H/2)

    s3_y = 9.7
    draw_box(ax, CX, s3_y, MAIN_W, MAIN_H,
             f"Records after fuzzy title deduplication\nN = {fuzzy_step['output']:,}",
             facecolor=C_SCREEN, fontsize=11)
    draw_box(ax, SIDE_X, s3_y, SIDE_W, SIDE_H,
             f"Fuzzy duplicates removed\n(ratio >= {fuzzy_step['threshold']}):\nn = {fuzzy_step['records_removed']:,}",
             facecolor=C_SIDE, fontsize=9)
    draw_arrow(ax, CX + MAIN_W/2, s3_y, SIDE_X - SIDE_W/2, s3_y)
    draw_arrow(ax, CX, s2_y - MAIN_H/2, CX, s3_y + MAIN_H/2)

    # ============ Eligibility: Stages 4 + 5 ============
    s4_y = 7.5
    draw_box(ax, CX, s4_y, MAIN_W, MAIN_H + 0.15,
             f"Records after OpenAlex precision filter\n"
             f"(WoS-equivalent 3-block boolean)\nN = {prec_step['output']:,}",
             facecolor=C_ELIG, fontsize=10)
    draw_box(ax, SIDE_X, s4_y, SIDE_W, SIDE_H,
             f"OpenAlex exclusives, no-match:\nn = {prec_dropped:,}",
             facecolor=C_SIDE, fontsize=9)
    draw_arrow(ax, CX + MAIN_W/2, s4_y, SIDE_X - SIDE_W/2, s4_y)
    draw_arrow(ax, CX, s3_y - MAIN_H/2, CX, s4_y + (MAIN_H+0.15)/2)

    # Stage 5 (NEW) -- cross-file dedup
    s5_y = 5.3
    draw_box(ax, CX, s5_y, MAIN_W, MAIN_H + 0.25,
             f"Records after cross-file deduplication\n"
             f"(main 2005-2025 vs partial 2026)\nN = {cross_step['output_main']:,}",
             facecolor=C_ELIG, fontsize=10, fontweight="bold")
    draw_box(ax, SIDE_X, s5_y, SIDE_W, SIDE_H + 0.35,
             f"Year-misassigned main records\n(year=2026): n = {cross_step['year_2026_misassigned_main']:,}\n"
             f"  dropped (in partial): {cross_step['of_which_dropped_dup_with_partial']:,}\n"
             f"  reassigned to partial: {cross_step['of_which_reassigned_to_partial']:,}",
             facecolor=C_SIDE, fontsize=8)
    draw_arrow(ax, CX + MAIN_W/2, s5_y, SIDE_X - SIDE_W/2, s5_y)
    draw_arrow(ax, CX, s4_y - (MAIN_H+0.15)/2, CX, s5_y + (MAIN_H+0.25)/2)

    # ============ Included ============
    f_y = 2.5
    draw_box(ax, CX, f_y, MAIN_W + 0.4, MAIN_H + 0.6,
             f"Final analysis corpus\n"
             f"Main (2005-2025): N = {final_n:,}\n"
             f"Partial 2026 extension: N = {partial_n:,}\n"
             f"Total: N = {total_n:,}",
             facecolor=C_INCL, fontsize=11, fontweight="bold")
    draw_arrow(ax, CX, s5_y - (MAIN_H+0.25)/2, CX, f_y + (MAIN_H+0.6)/2)

    # Footer
    ax.text(6.0, 0.6,
            "DOI primary-key deduplication (exact) -> fuzzy title matching (ratio >= 95, "
            "blocking on year + first-author surname) ->\n"
            "OpenAlex precision filter (3-block boolean: B1 TCM + drug + interaction; "
            "B2 TCM + interaction; B3 TCM + CYP) ->\n"
            "cross-file year-DOI reconciliation between main and partial 2026 corpora.",
            ha="center", va="center", fontsize=8, color="#555", style="italic")

    # ============ Save ============
    print("\n[3] Saving outputs (PDF + SVG + PNG)...")
    fig_dir = repo_root / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    out_pdf = fig_dir / "figure_01_prisma_flow.pdf"
    out_svg = fig_dir / "figure_01_prisma_flow.svg"
    out_png = fig_dir / "figure_01_prisma_flow.png"

    plt.savefig(out_pdf, dpi=300, bbox_inches="tight")
    plt.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"    [+] {out_pdf.relative_to(repo_root)}  ({out_pdf.stat().st_size/1024:.1f} KB)")
    print(f"    [+] {out_svg.relative_to(repo_root)}  ({out_svg.stat().st_size/1024:.1f} KB)")
    print(f"    [+] {out_png.relative_to(repo_root)}  ({out_png.stat().st_size/1024:.1f} KB)")

    print("\n[DONE] PRISMA flow diagram refreshed.")


if __name__ == "__main__":
    main()