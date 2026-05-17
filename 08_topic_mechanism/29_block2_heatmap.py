"""Day 13 Block 2 (revised): Topic x Mechanism heatmap (Fig 9).

Fix: separate suptitle/subtitle from PK/PD group bracket labels.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LogNorm

# ============================================================
# Style
# ============================================================
try:
    plt.style.use(["science", "no-latex"])
except Exception:
    plt.style.use("seaborn-v0_8-whitegrid")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.linewidth": 0.6,
})

OK_BLUE = "#0072B2"
OK_VERM = "#D55E00"

# ============================================================
# Paths
# ============================================================
REPO = Path(__file__).parent.parent
TABLES = REPO / "results" / "tables"
FIGURES = REPO / "results" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# ============================================================
# Load
# ============================================================
matrix_num = pd.read_csv(TABLES / "table_topic_x_mechanism_matrix_numericId.csv", index_col=0)
mech_marg = pd.read_csv(TABLES / "table_topic_x_mechanism_mech_marginals.csv")
with open(REPO / "data" / "processed" / "topic_labels.json", encoding="utf-8") as f:
    topic_labels = json.load(f)

print(f"[Load] matrix={matrix_num.shape}, mech_marg={len(mech_marg)}")

# ============================================================
# Column grouping: PK | PD
# ============================================================
PK_MECHS = [
    "CYP_inhibition", "CYP_induction",
    "P-gp_inhibition", "P-gp_induction",
    "UGT_inhibition", "UGT_induction",
    "transporter_modulation", "absorption_alteration",
    "protein_binding_displacement",
]
PD_MECHS = [
    "receptor_synergism", "receptor_antagonism",
    "synergistic_efficacy", "antagonistic_efficacy",
    "signaling_pathway_modulation",
    "organ_toxicity_modulation", "additive_toxicity",
]

mech_to_n = dict(zip(mech_marg["mechanism"], mech_marg["n_records"]))
pk_cols = sorted([m for m in PK_MECHS if m in matrix_num.columns], key=lambda m: -mech_to_n.get(m, 0))
pd_cols = sorted([m for m in PD_MECHS if m in matrix_num.columns], key=lambda m: -mech_to_n.get(m, 0))
ordered_cols = pk_cols + pd_cols

assert set(matrix_num.columns) == set(PK_MECHS + PD_MECHS), "mechanism taxa mismatch"
print(f"[Groups] PK={len(pk_cols)} | PD={len(pd_cols)}")

matrix = matrix_num[ordered_cols]
n_rows, n_cols = matrix.shape

# ============================================================
# Row labels
# ============================================================
def short_label(cid):
    entry = topic_labels.get(str(cid), {})
    kb = entry.get("top_keybert", []) or entry.get("top_ctfidf", [])
    n_docs = entry.get("n_docs", "?")
    if kb:
        terms = " / ".join([t[:14] for t in kb[:2]])
    else:
        terms = "???"
    return f"#{cid:>2} {terms[:30]:30s} (n={n_docs})"

row_labels = [short_label(cid) for cid in matrix.index]

# ============================================================
# Figure layout
# ============================================================
fig_h = max(7, 0.32 * n_rows + 2.5)
fig_w = max(11, 0.65 * n_cols + 5)

fig, ax = plt.subplots(figsize=(fig_w, fig_h))

# Mask zeros
plot_mat = matrix.astype(float).copy()
plot_mat[plot_mat == 0] = np.nan

# Annotations only for cells >= 5
ANNOT_THRESHOLD = 5
annot = matrix.astype(int).astype(str).values
annot[matrix.values < ANNOT_THRESHOLD] = ""

sns.heatmap(
    plot_mat,
    ax=ax,
    cmap="YlOrRd",
    norm=LogNorm(vmin=1, vmax=float(matrix.values.max())),
    annot=annot,
    fmt="",
    annot_kws={"size": 7.5, "color": "black"},
    cbar_kws={
        "label": "Records (log scale)",
        "shrink": 0.55,
        "pad": 0.02,
        "aspect": 30,
    },
    linewidths=0.3,
    linecolor="#dddddd",
    xticklabels=matrix.columns,
    yticklabels=row_labels,
    square=False,
)

ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=8, family="monospace")

ax.set_xlabel("Mechanism (Schema v3)", fontsize=11, fontweight="bold")
ax.set_ylabel("Topic cluster (HDBSCAN, sorted by descending count)", fontsize=11, fontweight="bold")

# ============================================================
# PK / PD group bracket annotations (axes-blended transform)
# ============================================================
sep_x = len(pk_cols)
y_line = 1.010    # color line above axes
y_label = 1.025   # group label above line

# Color lines spanning each group (use blended x-data, y-axes transform)
ax.plot([0, sep_x], [y_line, y_line],
        transform=ax.get_xaxis_transform(),
        color=OK_BLUE, lw=2.5, clip_on=False, solid_capstyle="butt")
ax.plot([sep_x, n_cols], [y_line, y_line],
        transform=ax.get_xaxis_transform(),
        color=OK_VERM, lw=2.5, clip_on=False, solid_capstyle="butt")

# Group labels above the color lines
ax.text(sep_x / 2, y_label,
        f"Pharmacokinetic (n={len(pk_cols)})",
        transform=ax.get_xaxis_transform(),
        ha="center", va="bottom",
        fontsize=11, fontweight="bold", color=OK_BLUE)
ax.text(sep_x + len(pd_cols) / 2, y_label,
        f"Pharmacodynamic (n={len(pd_cols)})",
        transform=ax.get_xaxis_transform(),
        ha="center", va="bottom",
        fontsize=11, fontweight="bold", color=OK_VERM)

# Vertical separator inside heatmap between PK and PD
ax.axvline(sep_x, color="#222222", linewidth=1.5, linestyle="--", zorder=10)

# ============================================================
# Figure-level title (separate from axes annotations)
# ============================================================
fig.suptitle(
    "Topic × Mechanism contingency matrix",
    fontsize=13.5, fontweight="bold", y=0.985,
)
fig.text(
    0.5, 0.96,
    f"N = {int(matrix.values.sum()):,} (record_id × mechanism) pairs  ·  "
    f"{matrix.shape[0]} topics × {matrix.shape[1]} mechanisms  ·  "
    f"confidence ≥ 0.7",
    ha="center", va="top",
    fontsize=9.5, style="italic", color="#555555",
)

# Footnote (bottom-right)
fig.text(
    0.99, 0.005,
    f"Cells with < {ANNOT_THRESHOLD} records unannotated; zeros uncolored.",
    ha="right", va="bottom", fontsize=7, color="#555555", style="italic",
)

# ============================================================
# Layout: reserve top 7% for suptitle + subtitle + group brackets
# ============================================================
fig.tight_layout(rect=[0, 0.01, 1, 0.93])

# ============================================================
# Save
# ============================================================
print("\n[Saving]")
for ext in ["png", "pdf", "svg"]:
    path = FIGURES / f"fig9_topic_x_mechanism_heatmap.{ext}"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    sz = path.stat().st_size / 1024
    print(f"  {path.relative_to(REPO)}  {sz:7.1f} KB")

plt.close(fig)
print("\n[Done] Block 2 (revised).")