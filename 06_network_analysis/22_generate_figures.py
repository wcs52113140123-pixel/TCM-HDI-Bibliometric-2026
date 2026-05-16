"""
Day 11 T1: Publication-quality figure generator.

Generates 8 paper-grade figures from Day 10 network data, following:
  - Nature/Science style guidelines (Arial sans-serif, 9pt body, vector output)
  - Colorblind-safe palettes (Okabe-Ito + viridis + RdBu_r)
  - TCM bibliometric review conventions (Frontiers in Pharmacology style)
  - PDF fonttype 42 (Inkscape/Illustrator editable text)

Outputs to results/figures/:
  fig5a_herb_family_x_target_family_heatmap.{png, pdf, svg}
  fig5b_target_family_x_mechanism_heatmap.{png, pdf, svg}
  fig6_mechanism_sankey.{html, png}             (plotly)
  fig8_temporal_mechanism_evolution.{png, pdf, svg}
  figS3_drug_class_x_mechanism.{png, pdf, svg}
  figS4_direction_distribution.{png, pdf, svg}
  figS5_confidence_histogram.{png, pdf, svg}
  figS6_top_hubs_panel.{png, pdf, svg}          (3-panel bar chart)

Style references:
  - Nature figure guidelines (sans-serif, viridis, 300 DPI minimum)
  - SciencePlots library (`science` + `no-latex` cascade)
  - Okabe-Ito colorblind-safe categorical palette
  - Frank Li's publication style settings (font 9pt, lines 0.5pt, etc.)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import scienceplots  # noqa: F401
    HAS_SCIENCEPLOTS = True
except ImportError:
    HAS_SCIENCEPLOTS = False

REPO = Path(__file__).resolve().parents[1]
NET_DIR = REPO / "data" / "processed" / "network"
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"
FIG_DIR = REPO / "results" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# PUBLICATION STYLE — Nature/Science compliant
# ============================================================
# Okabe-Ito colorblind-safe 8-color palette
# Source: Okabe & Ito 2008, "Color Universal Design"
# Used widely in Nature, NEJM, Cell figures
OKABE_ITO = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # green
    "#CC79A7",  # rose
    "#56B4E9",  # sky blue
    "#D55E00",  # vermillion
    "#F0E442",  # yellow
    "#000000",  # black
]

# Custom palette for biological entity types (TCM-HDI semantic)
ENTITY_COLORS = {
    "herb": "#2A9D8F",      # teal (plant-like)
    "drug": "#264653",      # dark blue (clinical)
    "target": "#E76F51",    # warm coral (mechanism)
    "mechanism": "#F4A261", # warm sand
}

# Mechanism category colors (Schema v3) — assigned thoughtfully
MECHANISM_COLORS = {
    "CYP_inhibition": "#0072B2",
    "CYP_induction": "#56B4E9",
    "P-gp_inhibition": "#009E73",
    "P-gp_induction": "#71C7BC",
    "transporter_modulation": "#9CCB86",
    "UGT_inhibition": "#E69F00",
    "UGT_induction": "#FFC966",
    "absorption_alteration": "#CC79A7",
    "receptor_synergism": "#D55E00",
    "receptor_antagonism": "#A04300",
    "synergistic_efficacy": "#D62728",
    "additive_toxicity": "#8C564B",
    "organ_toxicity_modulation": "#6A3D9A",
    "signaling_pathway_modulation": "#F0E442",
    "other": "#BBBBBB",
    "unspecified": "#888888",
}

NATURE_RC_PARAMS = {
    # Fonts (Nature requires sans-serif)
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "axes.titleweight": "bold",
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "legend.title_fontsize": 9,
    "figure.titlesize": 11,
    # Line widths (thin for elegance)
    "axes.linewidth": 0.6,
    "lines.linewidth": 0.8,
    "patch.linewidth": 0.4,
    "xtick.major.size": 3.0,
    "xtick.minor.size": 1.5,
    "ytick.major.size": 3.0,
    "ytick.minor.size": 1.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.pad": 2.5,
    "ytick.major.pad": 2.5,
    # Spines — Tufte-ish minimal
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#373737",
    "text.color": "#373737",
    "xtick.color": "#373737",
    "ytick.color": "#373737",
    # Quality
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04,
    "savefig.transparent": False,
    # Inkscape/Illustrator editable
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
}


def setup_style():
    """Configure matplotlib rcParams for publication-quality output."""
    plt.rcParams.update(NATURE_RC_PARAMS)
    sns.set_palette(OKABE_ITO)


def save_figure(fig, name: str, fmts: tuple = ("png", "pdf", "svg")):
    """Save figure in multiple formats (PNG preview, PDF/SVG for editing)."""
    for fmt in fmts:
        fig.savefig(FIG_DIR / f"{name}.{fmt}")
    plt.close(fig)
    extlist = ", ".join(fmts)
    print(f"  → results/figures/{name}.{{{extlist}}}")


def style_axes_borders(ax, keep_left: bool = True, keep_bottom: bool = True):
    """Apply minimal Tufte-style axis borders."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(keep_left)
    ax.spines["bottom"].set_visible(keep_bottom)


# ============================================================
# FIGURE 5A: Herb Family × Target Family heatmap
# ============================================================
def fig5a_herb_target_family_heatmap():
    """Top 15 herb families × top 10 target families, log-scaled if very skewed."""
    print("\n[Fig 5a] Herb Family × Target Family heatmap")
    df = pd.read_parquet(NET_DIR / "herb_family_x_target_family.parquet")
    matrix = df.pivot(index="herb_family", columns="target_family",
                      values="n_records").fillna(0).astype(int)

    # Sort by marginal totals
    row_order = matrix.sum(axis=1).sort_values(ascending=False).index
    col_order = matrix.sum(axis=0).sort_values(ascending=False).index
    matrix = matrix.loc[row_order, col_order]

    # Keep top families to keep heatmap legible
    matrix = matrix.iloc[:15, :10]

    fig, ax = plt.subplots(figsize=(7.0, 6.0))
    sns.heatmap(
        matrix,
        annot=True, fmt="g", annot_kws={"size": 7.5},
        cmap="YlOrRd",
        linewidths=0.4, linecolor="white",
        cbar_kws={"shrink": 0.7, "label": "Records (n)",
                  "pad": 0.02, "aspect": 30},
        ax=ax,
    )
    ax.set_title("Herb Family × Target Family Distribution",
                 loc="left", pad=10)
    ax.set_xlabel("Target Family", labelpad=6)
    ax.set_ylabel("Herb Family", labelpad=6)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)
    save_figure(fig, "fig5a_herb_family_x_target_family_heatmap")


# ============================================================
# FIGURE 5B: Target Family × Mechanism heatmap
# ============================================================
def fig5b_target_mechanism_heatmap():
    print("\n[Fig 5b] Target Family × Mechanism heatmap")
    df = pd.read_parquet(NET_DIR / "target_family_x_mechanism.parquet")
    matrix = df.pivot(index="target_family", columns="mechanism",
                      values="n_records").fillna(0).astype(int)

    row_order = matrix.sum(axis=1).sort_values(ascending=False).index
    col_order = matrix.sum(axis=0).sort_values(ascending=False).index
    matrix = matrix.loc[row_order, col_order]

    # Drop empty rows/cols
    matrix = matrix.loc[matrix.sum(axis=1) > 0, matrix.sum(axis=0) > 0]

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    sns.heatmap(
        matrix,
        annot=True, fmt="g", annot_kws={"size": 7.5},
        cmap="viridis",
        linewidths=0.4, linecolor="white",
        cbar_kws={"shrink": 0.7, "label": "Records (n)",
                  "pad": 0.02, "aspect": 30},
        ax=ax,
    )
    ax.set_title("Target Family × Mechanism Coupling",
                 loc="left", pad=10)
    ax.set_xlabel("Mechanism", labelpad=6)
    ax.set_ylabel("Target Family", labelpad=6)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)
    save_figure(fig, "fig5b_target_family_x_mechanism_heatmap")


# ============================================================
# FIGURE 6: Mechanism Sankey diagram (herb_family → mech → drug_class)
# ============================================================
def fig6_sankey():
    print("\n[Fig 6] Mechanism Sankey diagram")
    if not HAS_PLOTLY:
        print("  ⚠ plotly not installed; skipping. Run: pip install plotly kaleido")
        return

    df = pd.read_parquet(NET_DIR / "kg_chain_summary.parquet")
    # Keep top chains to avoid clutter
    df = df.sort_values("n_records", ascending=False).head(50).copy()

    # Build node list (herb_family / mechanism / drug_class are separate columns)
    hf = df["herb_family"].unique().tolist()
    me = df["mechanism"].unique().tolist()
    dc = df["drug_class"].unique().tolist()

    # Order columns so each appears in own "tier"
    nodes = [f"HF:{x}" for x in hf] + [f"M:{x}" for x in me] + [f"D:{x}" for x in dc]
    node_idx = {n: i for i, n in enumerate(nodes)}
    labels = [n.split(":", 1)[1] for n in nodes]
    node_colors = (
        ["#2A9D8F"] * len(hf)        # herbs: teal
        + ["#F4A261"] * len(me)      # mechs: warm sand
        + ["#264653"] * len(dc)      # drugs: dark blue
    )

    # Build links (herb_family → mechanism + mechanism → drug_class)
    sources, targets, values, link_colors = [], [], [], []
    # Stage 1: herb_family → mechanism (aggregate over drug_class)
    hf_to_m = df.groupby(["herb_family", "mechanism"])["n_records"].sum().reset_index()
    for _, r in hf_to_m.iterrows():
        sources.append(node_idx[f"HF:{r['herb_family']}"])
        targets.append(node_idx[f"M:{r['mechanism']}"])
        values.append(int(r["n_records"]))
        link_colors.append("rgba(42,157,143,0.35)")
    # Stage 2: mechanism → drug_class (aggregate over herb_family)
    m_to_d = df.groupby(["mechanism", "drug_class"])["n_records"].sum().reset_index()
    for _, r in m_to_d.iterrows():
        sources.append(node_idx[f"M:{r['mechanism']}"])
        targets.append(node_idx[f"D:{r['drug_class']}"])
        values.append(int(r["n_records"]))
        link_colors.append("rgba(244,162,97,0.35)")

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=14, thickness=18,
            line=dict(color="black", width=0.4),
            label=labels,
            color=node_colors,
        ),
        link=dict(
            source=sources, target=targets,
            value=values, color=link_colors,
        ),
    ))
    fig.update_layout(
        title=dict(text="<b>Mechanism Flow:</b> Herb Family → Mechanism → Drug Class<br>"
                        "<span style='font-size:11px'>"
                        "Top 50 chains, n_records aggregated</span>",
                   x=0.02, xanchor="left", font=dict(size=14)),
        font=dict(family="Arial", size=10, color="#373737"),
        height=720, width=1100,
        margin=dict(l=10, r=10, t=70, b=10),
        paper_bgcolor="white",
    )
    html_path = FIG_DIR / "fig6_mechanism_sankey.html"
    fig.write_html(html_path)
    print(f"  → results/figures/fig6_mechanism_sankey.html")
    try:
        png_path = FIG_DIR / "fig6_mechanism_sankey.png"
        fig.write_image(png_path, scale=2.5)
        print(f"  → results/figures/fig6_mechanism_sankey.png")
    except Exception as e:
        print(f"  ⚠ PNG export failed ({e}); install kaleido: pip install kaleido")


# ============================================================
# FIGURE 8: Temporal mechanism evolution
# ============================================================
def fig8_temporal_evolution():
    print("\n[Fig 8] Temporal mechanism evolution")
    df = pd.read_parquet(NET_DIR / "kg_triples.parquet")
    df = df.dropna(subset=["year", "mechanism"]).copy()
    df["year"] = df["year"].astype(int)

    # Bin years to handle sparse early years
    yr_min = max(2000, df["year"].min())
    df = df[df["year"] >= yr_min].copy()

    # Top mechanisms across all triples
    top_mechs = df["mechanism"].value_counts().head(8).index.tolist()
    df["mech_grouped"] = df["mechanism"].where(df["mechanism"].isin(top_mechs), "other")

    # Wide pivot
    pivot = (
        df.groupby(["year", "mech_grouped"]).size()
        .unstack(fill_value=0).sort_index()
    )

    # Reorder columns by total contribution (most frequent on bottom for stacked area)
    col_order = pivot.sum(axis=0).sort_values(ascending=False).index.tolist()
    if "other" in col_order:
        col_order.remove("other")
        col_order.append("other")  # 'other' on top
    pivot = pivot[col_order]

    # Color mapping
    colors = [MECHANISM_COLORS.get(m, "#999999") for m in pivot.columns]

    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.stackplot(pivot.index, pivot.T.values, labels=pivot.columns,
                 colors=colors, alpha=0.85, edgecolor="white", linewidth=0.3)
    ax.set_title("Temporal Evolution of Gold-standard Mechanism Triples",
                 loc="left", pad=10)
    ax.set_xlabel("Year", labelpad=6)
    ax.set_ylabel("Number of triples", labelpad=6)
    ax.set_xlim(pivot.index.min(), pivot.index.max())
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0),
              frameon=False, fontsize=7.5, title="Mechanism")
    style_axes_borders(ax)
    save_figure(fig, "fig8_temporal_mechanism_evolution")


# ============================================================
# FIG S3: Drug Class × Mechanism heatmap
# ============================================================
def figS3_drug_class_mechanism():
    print("\n[Fig S3] Drug Class × Mechanism heatmap")
    df = pd.read_parquet(NET_DIR / "drug_class_x_mechanism.parquet")
    matrix = df.pivot(index="drug_class", columns="mechanism",
                      values="n_records").fillna(0).astype(int)

    row_order = matrix.sum(axis=1).sort_values(ascending=False).index
    col_order = matrix.sum(axis=0).sort_values(ascending=False).index
    matrix = matrix.loc[row_order, col_order]

    # Top 18 drug classes × top 12 mechanisms
    matrix = matrix.iloc[:18, :12]

    fig, ax = plt.subplots(figsize=(8.5, 7.0))
    sns.heatmap(
        matrix,
        annot=True, fmt="g", annot_kws={"size": 7},
        cmap="rocket_r",
        linewidths=0.3, linecolor="white",
        cbar_kws={"shrink": 0.6, "label": "Records (n)",
                  "pad": 0.02, "aspect": 30},
        ax=ax,
    )
    ax.set_title("Drug Class × Mechanism Coupling (gold-standard triples)",
                 loc="left", pad=10)
    ax.set_xlabel("Mechanism", labelpad=6)
    ax.set_ylabel("Drug Class", labelpad=6)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)
    save_figure(fig, "figS3_drug_class_x_mechanism")


# ============================================================
# FIG S4: Direction distribution (PK vs PD)
# ============================================================
def figS4_direction_distribution():
    print("\n[Fig S4] Direction distribution")
    df = pd.read_parquet(NET_DIR / "kg_triples.parquet")
    df = df.dropna(subset=["direction"]).copy()

    # Classify direction as PK or PD
    pk_dirs = {"exposure_increase", "exposure_decrease"}
    pd_dirs = {"effect_increase", "effect_decrease"}
    df["axis"] = df["direction"].apply(
        lambda d: "PK (exposure)" if d in pk_dirs
        else ("PD (effect)" if d in pd_dirs else "Other")
    )

    counts = df.groupby(["axis", "direction"]).size().reset_index(name="n")
    counts = counts.sort_values(["axis", "n"], ascending=[True, False])

    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    palette_map = {
        "exposure_increase": "#0072B2",
        "exposure_decrease": "#56B4E9",
        "effect_increase": "#D55E00",
        "effect_decrease": "#E69F00",
        "no_change": "#BBBBBB",
        "context_dependent": "#888888",
    }
    colors = [palette_map.get(d, "#999999") for d in counts["direction"]]

    bars = ax.barh(counts["direction"], counts["n"], color=colors,
                   edgecolor="white", linewidth=0.5)
    ax.set_title("Direction Distribution in Gold-standard Triples",
                 loc="left", pad=10)
    ax.set_xlabel("Records (n)", labelpad=6)
    ax.set_ylabel("")
    ax.invert_yaxis()

    # Annotate counts to right of bars
    for bar, val in zip(bars, counts["n"]):
        ax.text(bar.get_width() + 4, bar.get_y() + bar.get_height()/2,
                f"{val} ({val/len(df)*100:.1f}%)",
                va="center", ha="left", fontsize=8, color="#373737")

    ax.set_xlim(0, counts["n"].max() * 1.18)
    style_axes_borders(ax)
    save_figure(fig, "figS4_direction_distribution")


# ============================================================
# FIG S5: Confidence histogram
# ============================================================
def figS5_confidence_histogram():
    print("\n[Fig S5] Confidence histogram")
    df = pd.read_parquet(NET_DIR / "kg_triples.parquet")
    conf = df["confidence"].dropna()

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    n, bins, patches = ax.hist(conf, bins=np.arange(0.0, 1.02, 0.05),
                                edgecolor="white", linewidth=0.6,
                                color="#0072B2", alpha=0.85)
    # Mean + median lines
    mean_v, med_v = conf.mean(), conf.median()
    ax.axvline(mean_v, color="#D55E00", linestyle="--", linewidth=1.0,
               label=f"Mean = {mean_v:.3f}")
    ax.axvline(med_v, color="#009E73", linestyle=":", linewidth=1.0,
               label=f"Median = {med_v:.3f}")

    ax.set_title("Confidence Distribution in Gold-standard Triples",
                 loc="left", pad=10)
    ax.set_xlabel("LLM-assigned confidence score", labelpad=6)
    ax.set_ylabel("Triples (n)", labelpad=6)
    ax.set_xlim(0, 1.0)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    style_axes_borders(ax)
    save_figure(fig, "figS5_confidence_histogram")


# ============================================================
# FIG S6: Top hubs panel (3-panel bar chart)
# ============================================================
def figS6_top_hubs_panel():
    print("\n[Fig S6] Top hubs 3-panel bar chart")
    edges_hd = pd.read_parquet(NET_DIR / "herb_drug_edges.parquet")
    edges_ht = pd.read_parquet(NET_DIR / "herb_target_edges.parquet")

    # Top hub herbs (from herb_drug network - distinct drugs partner count)
    hub_herbs = (
        edges_hd.groupby("herb").size().sort_values(ascending=False).head(15)
    )
    # Top hub drugs
    hub_drugs = (
        edges_hd.groupby("drug").size().sort_values(ascending=False).head(15)
    )
    # Top hub targets
    hub_targets = (
        edges_ht.groupby("target").size().sort_values(ascending=False).head(15)
    )

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 5.0))
    palette3 = ["#2A9D8F", "#264653", "#E76F51"]

    for ax, (data, title, color, xlab) in zip(
        axes,
        [
            (hub_herbs, "Top Hub Herbs", palette3[0], "Distinct drugs (degree)"),
            (hub_drugs, "Top Hub Drugs", palette3[1], "Distinct herbs (degree)"),
            (hub_targets, "Top Hub Targets", palette3[2], "Distinct herbs (degree)"),
        ],
    ):
        bars = ax.barh(data.index[::-1], data.values[::-1], color=color,
                       edgecolor="white", linewidth=0.5)
        ax.set_title(title, loc="left", pad=10)
        ax.set_xlabel(xlab, labelpad=6)
        # Annotate counts
        for bar in bars:
            ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height()/2,
                    f"{int(bar.get_width())}",
                    va="center", ha="left", fontsize=7, color="#373737")
        ax.set_xlim(0, data.max() * 1.13)
        style_axes_borders(ax)
        # Truncate long labels
        ylabels = [str(s)[:25] + ("…" if len(str(s)) > 25 else "")
                   for s in data.index[::-1]]
        ax.set_yticks(range(len(ylabels)))
        ax.set_yticklabels(ylabels, fontsize=7)

    plt.tight_layout()
    save_figure(fig, "figS6_top_hubs_panel")


# ============================================================
# MAIN
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-sankey", action="store_true",
                    help="Skip Fig 6 Sankey (if plotly/kaleido not installed)")
    ap.add_argument("--only", nargs="+",
                    choices=["5a", "5b", "6", "8", "s3", "s4", "s5", "s6"],
                    help="Run only specified figures")
    args = ap.parse_args()

    print(f"{'='*72}\n  Day 11 T1: Publication-quality figure generation\n{'='*72}")
    print(f"  scienceplots available: {HAS_SCIENCEPLOTS}")
    print(f"  plotly available:        {HAS_PLOTLY}")
    print(f"  Output dir: {FIG_DIR.relative_to(REPO)}")

    setup_style()

    figs = {
        "5a": fig5a_herb_target_family_heatmap,
        "5b": fig5b_target_mechanism_heatmap,
        "6": fig6_sankey,
        "8": fig8_temporal_evolution,
        "s3": figS3_drug_class_mechanism,
        "s4": figS4_direction_distribution,
        "s5": figS5_confidence_histogram,
        "s6": figS6_top_hubs_panel,
    }

    if args.only:
        run = {k: figs[k] for k in args.only}
    else:
        run = figs
        if args.skip_sankey:
            run = {k: v for k, v in run.items() if k != "6"}

    for code, func in run.items():
        try:
            func()
        except Exception as e:
            print(f"  ❌ Fig {code} failed: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n  ✓ Figure generation done. {len(list(FIG_DIR.iterdir()))} files in "
          f"{FIG_DIR.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
