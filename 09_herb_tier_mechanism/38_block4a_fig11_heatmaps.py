"""
Day 15 Block 4a -- fig11: three-tier heatmaps (family/species/compound)
========================================================================
Single figure with 3 horizontal panels (A/B/C), shared diverging colormap,
PK/PD column grouping with bracket annotations + dashed separator.
Asterisks on strong_enrichment cells, "x" on strong_depletion.

Output: results/figures/fig11_three_tier_heatmaps.{png,pdf,svg}
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

# SciencePlots removed -- it activates text.usetex=True which requires LaTeX
mpl.rcParams.update({
    "text.usetex": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 8,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
})

REPO = Path(r"D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026")
TABLES = REPO / "results" / "tables"
FIGURES = REPO / "results" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# Mechanism order: PK first, PD second (Day 13 convention)
PK = ["CYP_inhibition", "CYP_induction", "UGT_inhibition", "UGT_induction",
      "P-gp_inhibition", "P-gp_induction", "absorption_alteration",
      "transporter_modulation", "protein_binding_displacement"]
PD = ["receptor_antagonism", "receptor_synergism", "synergistic_efficacy",
      "antagonistic_efficacy", "additive_toxicity",
      "signaling_pathway_modulation", "organ_toxicity_modulation"]
MECH_ORDER = PK + PD  # 16

# Compact display names to avoid x-axis label collisions across 3 panels
MECH_DISPLAY = {
    "CYP_inhibition": "CYP_inh", "CYP_induction": "CYP_ind",
    "UGT_inhibition": "UGT_inh", "UGT_induction": "UGT_ind",
    "P-gp_inhibition": "P-gp_inh", "P-gp_induction": "P-gp_ind",
    "absorption_alteration": "absorption",
    "transporter_modulation": "transporter",
    "protein_binding_displacement": "prot_binding",
    "receptor_antagonism": "rec_antag",
    "receptor_synergism": "rec_synerg",
    "synergistic_efficacy": "synerg_eff",
    "antagonistic_efficacy": "antag_eff",
    "additive_toxicity": "add_tox",
    "signaling_pathway_modulation": "signaling",
    "organ_toxicity_modulation": "organ_tox",
}

TIERS = [
    ("family",   "herb_family",            "table_herb_family_x_mechanism_enrichment_full.csv",   "A. Family"),
    ("species",  "herb_canonical_latin",   "table_herb_species_x_mechanism_enrichment_full.csv",  "B. Species"),
    ("compound", "herb_active_compound",   "table_herb_compound_x_mechanism_enrichment_full.csv", "C. Compound"),
]

# Load all 3
data = {}
for tier_name, entity_col, fname, title in TIERS:
    df = pd.read_csv(TABLES / fname)
    log_OR = df.pivot_table(index=entity_col, columns="mechanism", values="log2_OR_ha", fill_value=0)
    cls    = df.pivot_table(index=entity_col, columns="mechanism", values="classification", aggfunc="first").fillna("ns")
    obs    = df.pivot_table(index=entity_col, columns="mechanism", values="obs", fill_value=0).astype(int)
    # Reindex columns to full mechanism order
    for m in MECH_ORDER:
        if m not in log_OR.columns: log_OR[m] = 0
        if m not in cls.columns:    cls[m] = "ns"
        if m not in obs.columns:    obs[m] = 0
    log_OR = log_OR[MECH_ORDER]
    cls = cls[MECH_ORDER]
    obs = obs[MECH_ORDER]
    # Sort rows by total obs descending
    row_order = obs.sum(axis=1).sort_values(ascending=False).index
    log_OR = log_OR.loc[row_order]
    cls    = cls.loc[row_order]
    obs    = obs.loc[row_order]
    data[tier_name] = {"log_OR": log_OR, "cls": cls, "obs": obs, "title": title}
    print(f"[{tier_name}] {log_OR.shape[0]} entities, log2_OR range: [{log_OR.values.min():.2f}, {log_OR.values.max():.2f}]")

# Determine common color scale (symmetric around 0)
all_vals = np.concatenate([data[t]["log_OR"].values.flatten() for t in data])
vmax = max(abs(all_vals.min()), abs(all_vals.max()))
vmax = min(vmax, 8)  # cap to avoid extreme outliers compressing dynamic range
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
print(f"Color scale: log2_OR in [{-vmax:.2f}, {vmax:.2f}]")

# Build figure: 1 row x 3 cols, height proportional to row count of each panel
fig = plt.figure(figsize=(22, 11))
gs = fig.add_gridspec(1, 4, width_ratios=[24, 32, 23, 1.0], wspace=0.95)

axes = []
for i, (tier_name, _, _, title) in enumerate(TIERS):
    d = data[tier_name]
    mat = d["log_OR"]
    cls = d["cls"]
    obs = d["obs"]
    ax = fig.add_subplot(gs[0, i])
    im = ax.imshow(mat.values, aspect="auto", cmap="RdBu_r", norm=norm, interpolation="none")
    ax.set_xticks(range(len(MECH_ORDER)))
    ax.set_xticklabels([MECH_DISPLAY.get(m, m) for m in MECH_ORDER], rotation=55, ha="right", fontsize=7)
    ax.set_yticks(range(len(mat.index)))
    ax.set_yticklabels(mat.index, fontsize=6.5)
    ax.set_title(title, loc="left", fontweight="bold", pad=18)

    # PK/PD dashed separator
    ax.axvline(len(PK) - 0.5, color="black", linestyle="--", linewidth=0.7, alpha=0.6)

    # PK/PD bracket annotations at top (in axes-fraction coords)
    pk_x = (len(PK) - 1) / 2 / (len(MECH_ORDER) - 1)
    pd_x = (len(PK) + (len(PD) - 1) / 2) / (len(MECH_ORDER) - 1)
    ax.annotate("PK", xy=(pk_x, 1.06), xycoords="axes fraction",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color="#0072B2")
    ax.annotate("PD", xy=(pd_x, 1.06), xycoords="axes fraction",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color="#D55E00")

    # Annotations: asterisks for sig
    for ri, ent in enumerate(mat.index):
        for ci, mech in enumerate(MECH_ORDER):
            c = cls.at[ent, mech]
            o = obs.at[ent, mech]
            if c == "strong_enrichment":
                marker = "***"
            elif c == "strong_depletion":
                marker = "x"
            elif c == "weak_sig":
                marker = "*"
            else:
                marker = ""
            if marker:
                # Choose text color based on cell brightness for legibility
                v = mat.at[ent, mech]
                txt_color = "white" if abs(v) > vmax * 0.55 else "black"
                ax.text(ci, ri, marker, ha="center", va="center",
                        fontsize=6.5 if marker == "***" else 7,
                        color=txt_color, fontweight="bold")

    ax.tick_params(axis="both", which="both", length=0)
    axes.append(ax)

# Shared colorbar
cbar_ax = fig.add_subplot(gs[0, 3])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.set_label("log$_2$(Odds Ratio), Haldane-Anscombe", fontsize=8)
cbar.ax.tick_params(labelsize=7)

fig.suptitle("Three-tier herb x mechanism enrichment landscape",
             fontsize=12, fontweight="bold", y=0.995)
plt.figtext(0.5, 0.01,
            "n = 79 entities (24 families + 32 species + 23 compounds) x 16 mechanisms; per-cell Fisher exact + within-tier BH-FDR\n"
            "*** strong enrichment (q<0.05, OR>2, obs>=5)  |  x strong depletion  |  * weak significance",
            ha="center", fontsize=7.5, style="italic")

for ext in ["png", "pdf", "svg"]:
    out = FIGURES / f"fig11_three_tier_heatmaps.{ext}"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"  saved: {out.name}  ({out.stat().st_size/1024:.1f} KB)")

plt.close(fig)
print("\n=== Block 4a fig11 COMPLETE ===")