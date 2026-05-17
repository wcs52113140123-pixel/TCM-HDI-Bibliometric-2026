"""
Day 15 Block 4b -- fig12: cross-tier chain sankey
==================================================
Plotly sankey: Family -> Species -> Compound, with mechanism-colored links.
Only chains where at least one tier is sig are shown.

Outputs:
  results/figures/fig12_cross_tier_chain_sankey.{html,pdf,png}
"""
import pandas as pd
import numpy as np
from pathlib import Path

import plotly.graph_objects as go

REPO = Path(r"D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026")
TABLES = REPO / "results" / "tables"
FIGURES = REPO / "results" / "figures"

df_chain = pd.read_csv(TABLES / "table_herb_cross_tier_chains.csv")
print(f"Loaded {len(df_chain)} sig chain rows")

# Okabe-Ito-ish palette for 6 sig mechanisms
MECH_COLORS = {
    "CYP_induction":              "#D55E00",  # vermillion -- SJW signature
    "CYP_inhibition":             "#0072B2",  # blue -- PK inhibition
    "P-gp_inhibition":            "#009E73",  # green -- Lamiaceae
    "transporter_modulation":     "#56B4E9",  # sky blue -- Lamiaceae companion
    "UGT_inhibition":             "#E69F00",  # orange -- Glycyrrhiza
    "receptor_synergism":         "#CC79A7",  # pink -- Animal_derived
}

# Chain class -> line opacity (sig stronger, partial fainter)
CLASS_OPACITY = {
    "FULL_CHAIN":                       1.0,
    "FAMILY_SPECIES_NO_COMPOUND_DATA":  0.85,
    "F_S_COMPOUND_NOT_SIG":             0.65,
    "FAMILY_PERVASIVE":                 0.80,
    "SPECIES_SPECIFIC":                 0.80,
}

def hex_to_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha:.2f})"

# Collect unique nodes per column
families = sorted(df_chain["family"].dropna().unique())
species  = sorted(df_chain["species"].dropna().unique())
compounds = sorted(df_chain["compound"].dropna().unique())

# Position nodes: family at x=0.01, species at x=0.5, compound at x=0.99
node_labels, node_x, node_y, node_colors = [], [], [], []

def assign_y_positions(items):
    """Distribute items along y in [0.05, 0.95]"""
    n = len(items)
    if n == 1: return [0.5]
    return list(np.linspace(0.05, 0.95, n))

fam_y = assign_y_positions(families)
sp_y  = assign_y_positions(species)
cp_y  = assign_y_positions(compounds)

fam_idx = {}
sp_idx = {}
cp_idx = {}

for i, f in enumerate(families):
    fam_idx[f] = len(node_labels)
    node_labels.append(f)
    node_x.append(0.01)
    node_y.append(fam_y[i])
    node_colors.append("#777777")

for i, s in enumerate(species):
    sp_idx[s] = len(node_labels)
    node_labels.append(s)
    node_x.append(0.5)
    node_y.append(sp_y[i])
    node_colors.append("#777777")

for i, c in enumerate(compounds):
    cp_idx[c] = len(node_labels)
    node_labels.append(c)
    node_x.append(0.99)
    node_y.append(cp_y[i])
    node_colors.append("#777777")

print(f"Nodes: {len(families)} families + {len(species)} species + {len(compounds)} compounds = {len(node_labels)}")

# Build links
links_source, links_target, links_value, links_color, links_label = [], [], [], [], []

for _, r in df_chain.iterrows():
    mech = r["mechanism"]
    cls = r["chain_class"]
    color_hex = MECH_COLORS.get(mech, "#888888")
    alpha = CLASS_OPACITY.get(cls, 0.5)
    rgba = hex_to_rgba(color_hex, alpha)

    fam, sp, cp = r["family"], r["species"], r["compound"]

    # F -> S link
    if pd.notna(sp):
        val = max(int(r["species_obs"] or 0), 1)
        links_source.append(fam_idx[fam])
        links_target.append(sp_idx[sp])
        links_value.append(val)
        links_color.append(rgba)
        links_label.append(f"{mech} | {cls} | obs={int(r['species_obs'])}")

    # S -> C link
    if pd.notna(cp):
        val = max(int(r["compound_obs"] or 0), 1)
        links_source.append(sp_idx[sp])
        links_target.append(cp_idx[cp])
        links_value.append(val)
        links_color.append(rgba)
        links_label.append(f"{mech} | {cls} | obs={int(r['compound_obs'])}")

print(f"Links: {len(links_source)}")

# Build figure
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=18,
        thickness=22,
        line=dict(color="black", width=0.5),
        label=node_labels,
        color=node_colors,
        x=node_x,
        y=node_y,
    ),
    link=dict(
        source=links_source,
        target=links_target,
        value=links_value,
        color=links_color,
        label=links_label,
        hovertemplate="%{label}<br>flow=%{value}<extra></extra>",
    ),
)])

# Column header annotations
fig.update_layout(
    title=dict(
        text="<b>Cross-tier consistency chains: Family → Species → Compound</b><br>"
             "<sup>Links colored by mechanism; opacity by chain class. n = 15 significant chains across 6 mechanisms.</sup>",
        x=0.02, xanchor="left",
        font=dict(size=14),
    ),
    annotations=[
        dict(text="<b>Family</b>",   x=0.01, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=12)),
        dict(text="<b>Species</b>",  x=0.50, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=12)),
        dict(text="<b>Compound</b>", x=0.99, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=12)),
    ],
    font=dict(size=12),
    width=1700,
    height=1100,
    margin=dict(l=30, r=30, t=130, b=130),
    paper_bgcolor="white",
    plot_bgcolor="white",
)

# Native Plotly legend via invisible scatter traces (one per mechanism)
for mech, color in MECH_COLORS.items():
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="lines",
        line=dict(color=color, width=10),
        name=mech.replace("_", " "),
        showlegend=True,
        hoverinfo="skip",
    ))

fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="top", y=-0.10,
        xanchor="center", x=0.5,
        font=dict(size=11),
        bgcolor="rgba(255,255,255,0)",
        bordercolor="rgba(0,0,0,0)",
        itemsizing="constant",
        title=dict(text="<b>Mechanism</b>  ", side="left"),
    )
)

# Hide scatter-trace auto axes (the dummy legend traces leaked tick numbers 0/1/-1/etc.)
fig.update_xaxes(visible=False, showgrid=False, zeroline=False, showticklabels=False)
fig.update_yaxes(visible=False, showgrid=False, zeroline=False, showticklabels=False)

# Save outputs
out_html = FIGURES / "fig12_cross_tier_chain_sankey.html"
fig.write_html(out_html)
print(f"  saved: {out_html.name}  ({out_html.stat().st_size/1024:.1f} KB)")

# Kaleido <1.0.0 + new Plotly hangs on Chromium subprocess; skip static export.
# HTML interactive is the primary deliverable for paper review.
# For paper-grade static PDF, options:
#   (a) Open HTML in browser, use Plotly camera icon for static export
#   (b) Upgrade: pip install 'kaleido>=1.0.0' then re-enable this block
#   (c) Build a matplotlib-based static fig12 in Block 5 polish step
print("  static PDF/PNG export skipped (kaleido<1.0 hang issue)")
print(f"  HTML deliverable: {out_html}")

print("\n=== Block 4b fig12 COMPLETE ===")