"""Day 14 Block 2: trajectory visualization (fig10).

Single-panel slopegraph of 40 (topic, mechanism) pairs across 3 eras:
- y: log2(OR) Haldane-corrected
- x: 3 disjoint periods
- color: trajectory class (Okabe-Ito)
- markers: filled if significant in era, open if not
- text labels for 3 EMERGING + 1 DECLINING + top 3 STABLE enrichments + top 3 STABLE depletions
"""
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

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
})

REPO = Path(__file__).parent.parent
TABLES = REPO / "results" / "tables"
FIGURES = REPO / "results" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# ============================================================
# Load
# ============================================================
era_mats = {p: pd.read_csv(TABLES / f"table_topic_x_mechanism_era_matrix_period{p}.csv", index_col=0).astype(int)
            for p in [1, 2, 3]}

df_enr = pd.read_csv(TABLES / "table_topic_x_mechanism_trajectory_enrichment.csv")
df_dep = pd.read_csv(TABLES / "table_topic_x_mechanism_trajectory_depletion.csv")
df_enr["pair_type"] = "enrichment"
df_dep["pair_type"] = "depletion"
df_all = pd.concat([df_enr, df_dep], ignore_index=True)

print(f"[Load] {len(df_all)} pairs (enr {len(df_enr)} + dep {len(df_dep)})")

# ============================================================
# Compute log2(OR) Haldane-corrected per era for visualization
# ============================================================
def haldane_log2or(mat, cid, mech):
    a = int(mat.loc[int(cid), mech])
    t = int(mat.loc[int(cid)].sum())
    m = int(mat[mech].sum())
    N = int(mat.values.sum())
    b = t - a
    c = m - a
    d = N - t - m + a
    return np.log2(((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5)))

for p in [1, 2, 3]:
    df_all[f"p{p}_log2or_h"] = df_all.apply(
        lambda r: haldane_log2or(era_mats[p], r["cluster_id"], r["mechanism"]),
        axis=1
    )

print(f"[log2_OR] range: P1 [{df_all['p1_log2or_h'].min():.1f}, {df_all['p1_log2or_h'].max():.1f}], "
      f"P2 [{df_all['p2_log2or_h'].min():.1f}, {df_all['p2_log2or_h'].max():.1f}], "
      f"P3 [{df_all['p3_log2or_h'].min():.1f}, {df_all['p3_log2or_h'].max():.1f}]")

# ============================================================
# Visual encoding by trajectory class
# ============================================================
TRAJ_COLORS = {
    "STABLE":           "#666666",
    "EMERGING":         "#D55E00",   # vermillion - Era 4 highlight
    "DECLINING":        "#0072B2",   # blue - Era 1 ghost
    "FADING":           "#56B4E9",
    "RISING":           "#E69F00",
    "TRANSIENT_MIDDLE": "#F0E442",
    "BIMODAL":          "#009E73",
    "WEAK_NONE":        "#cccccc",
}
TRAJ_LW = {
    "STABLE": 1.0, "EMERGING": 2.5, "DECLINING": 2.5,
    "FADING": 1.5, "RISING": 1.5, "TRANSIENT_MIDDLE": 1.2,
    "BIMODAL": 1.2, "WEAK_NONE": 0.8,
}
TRAJ_ALPHA = {
    "STABLE": 0.45, "EMERGING": 0.95, "DECLINING": 0.95,
    "FADING": 0.7, "RISING": 0.7, "TRANSIENT_MIDDLE": 0.55,
    "BIMODAL": 0.55, "WEAK_NONE": 0.4,
}

# ============================================================
# Figure
# ============================================================
fig, ax = plt.subplots(figsize=(14, 10))

x_pos = np.array([0.0, 1.0, 2.0])
x_labels = [
    "Period 1\n2005-2013\n(Classical case-based)",
    "Period 2\n2014-2019\n(Mechanistic deepening)",
    "Period 3\n2020-2026\n(Systems-level)",
]

# Draw all 40 lines
for _, r in df_all.iterrows():
    y = [r[f"p{p}_log2or_h"] for p in [1, 2, 3]]
    sig = [r[f"p{p}_sig"] for p in [1, 2, 3]]
    color = TRAJ_COLORS[r["trajectory"]]
    lw = TRAJ_LW[r["trajectory"]]
    alpha = TRAJ_ALPHA[r["trajectory"]]
    z = 3 + lw  # thicker lines on top

    ax.plot(x_pos, y, color=color, lw=lw, alpha=alpha, zorder=z, solid_capstyle="round")

    for xi, yi, si in zip(x_pos, y, sig):
        if si:
            ax.scatter(xi, yi, s=36, color=color, edgecolor="black",
                       linewidth=0.4, alpha=alpha, zorder=z + 1)
        else:
            ax.scatter(xi, yi, s=24, color="white", edgecolor=color,
                       linewidth=0.9, alpha=alpha, zorder=z + 1)

# Zero line
ax.axhline(0, color="black", linestyle="-", linewidth=0.5, alpha=0.3, zorder=1)

# Background zone shading (subtle)
y_min, y_max = -10, 11
ax.fill_between([-0.3, 3.5], 0, y_max, color="#D55E00", alpha=0.04, zorder=0)
ax.fill_between([-0.3, 3.5], y_min, 0, color="#0072B2", alpha=0.04, zorder=0)

ax.text(-0.27, 8.5, "Enrichment\nzone", fontsize=9.5, fontweight="bold",
        color="#D55E00", va="center", ha="left", alpha=0.55)
ax.text(-0.27, -7, "Depletion\nzone", fontsize=9.5, fontweight="bold",
        color="#0072B2", va="center", ha="left", alpha=0.55)

# ============================================================
# Annotate key pairs with anti-collision (1D repel + leader lines)
# ============================================================
labels_data = []

# 3 EMERGING (paper highlight)
for _, r in df_all[df_all["trajectory"] == "EMERGING"].iterrows():
    labels_data.append({
        "cid": int(r["cluster_id"]),
        "mech": r["mechanism"],
        "y_target": r["p3_log2or_h"],
        "traj": r["trajectory"],
    })

# 1 DECLINING (#6 warfarin)
for _, r in df_all[df_all["trajectory"] == "DECLINING"].iterrows():
    labels_data.append({
        "cid": int(r["cluster_id"]),
        "mech": r["mechanism"],
        "y_target": r["p3_log2or_h"],
        "traj": r["trajectory"],
    })

# Top 3 STABLE enrichments
df_all["avg_log2or"] = df_all[["p1_log2or_h", "p2_log2or_h", "p3_log2or_h"]].mean(axis=1)
top_stable_enr = df_all[(df_all["trajectory"] == "STABLE") & (df_all["pair_type"] == "enrichment")].nlargest(3, "avg_log2or")
for _, r in top_stable_enr.iterrows():
    labels_data.append({
        "cid": int(r["cluster_id"]),
        "mech": r["mechanism"],
        "y_target": r["p3_log2or_h"],
        "traj": r["trajectory"],
    })

# Top 3 STABLE depletions
top_stable_dep = df_all[(df_all["trajectory"] == "STABLE") & (df_all["pair_type"] == "depletion")].nsmallest(3, "avg_log2or")
for _, r in top_stable_dep.iterrows():
    labels_data.append({
        "cid": int(r["cluster_id"]),
        "mech": r["mechanism"],
        "y_target": r["p3_log2or_h"],
        "traj": r["trajectory"],
    })

# Prepare text + styling (shorten longer mechanism names)
for ld in labels_data:
    m = ld["mech"]
    m = m.replace("_modulation", "_mod").replace("_inhibition", "_inh").replace("_induction", "_ind")
    m = m.replace("synergistic_efficacy", "synerg_efficacy").replace("receptor_synergism", "recep_synerg")
    ld["text"] = f"#{ld['cid']} × {m}"
    ld["color"] = TRAJ_COLORS[ld["traj"]]
    ld["weight"] = "bold" if ld["traj"] in ("EMERGING", "DECLINING") else "normal"
    ld["y_label"] = ld["y_target"]

# Iterative 1D anti-collision (vertical only)
MIN_GAP = 0.85
for _ in range(200):
    labels_data.sort(key=lambda x: -x["y_label"])
    changed = False
    for i in range(len(labels_data) - 1):
        gap = labels_data[i]["y_label"] - labels_data[i+1]["y_label"]
        if gap < MIN_GAP:
            shift = (MIN_GAP - gap) / 2
            labels_data[i]["y_label"] += shift
            labels_data[i+1]["y_label"] -= shift
            changed = True
    if not changed:
        break

# Clip to plot y-range
for ld in labels_data:
    ld["y_label"] = max(y_min + 0.6, min(y_max - 0.6, ld["y_label"]))

# Draw leader lines + label text
LABEL_X = 2.22
for ld in labels_data:
    ax.plot(
        [2.05, LABEL_X - 0.03],
        [ld["y_target"], ld["y_label"]],
        color=ld["color"],
        linewidth=0.55,
        alpha=0.5,
        zorder=4,
        solid_capstyle="round",
    )
    ax.text(
        LABEL_X, ld["y_label"],
        ld["text"],
        fontsize=8.4,
        color=ld["color"],
        ha="left",
        va="center",
        fontweight=ld["weight"],
        zorder=5,
    )

# ============================================================
# Axes & legend
# ============================================================
ax.set_xticks(x_pos)
ax.set_xticklabels(x_labels, fontsize=9.5)
ax.set_xlim(-0.3, 3.4)
ax.set_ylim(y_min, y_max)
ax.set_ylabel("log2(Odds Ratio), Haldane–Anscombe corrected", fontsize=11, fontweight="bold")
ax.tick_params(axis="y", labelsize=9)
ax.grid(True, axis="y", alpha=0.25, linestyle="--", linewidth=0.4)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Two-block legend (trajectory + significance)
traj_classes_in_data = df_all["trajectory"].value_counts()
legend_traj = [
    Line2D([0], [0], color=TRAJ_COLORS[t], lw=TRAJ_LW[t],
           label=f"{('TRANSIENT' if t == 'TRANSIENT_MIDDLE' else t)}  (n={n})")
    for t, n in traj_classes_in_data.items()
]
legend_sig = [
    Line2D([0], [0], marker="o", color="gray", markersize=7, linestyle="",
           markerfacecolor="gray", markeredgecolor="black",
           label="q < 0.05 within era"),
    Line2D([0], [0], marker="o", color="gray", markersize=7, linestyle="",
           markerfacecolor="white", markeredgecolor="gray",
           label="not significant"),
]

leg1 = ax.legend(handles=legend_traj, loc="upper left", bbox_to_anchor=(1.02, 1.0),
                 fontsize=8.5, frameon=False, title="Trajectory class")
leg1.get_title().set_fontweight("bold")
ax.add_artist(leg1)
ax.legend(handles=legend_sig, loc="upper left", bbox_to_anchor=(1.02, 0.42),
          fontsize=8.5, frameon=False, title="Era-level significance").get_title().set_fontweight("bold")

# ============================================================
# Title
# ============================================================
fig.suptitle("Topic × Mechanism enrichment / depletion trajectories across three TCM-HDI eras",
             fontsize=13, fontweight="bold", y=0.985)
fig.text(0.5, 0.955,
         "n = 40 pairs (Day 13 top 20 enrichments + top 20 depletions)  ·  "
         "per-era Fisher exact (two-sided) + BH-FDR within era",
         ha="center", va="top", fontsize=9, style="italic", color="#555555")

fig.tight_layout(rect=[0, 0.02, 0.85, 0.93])

# ============================================================
# Save
# ============================================================
print("\n[Saving]")
for ext in ["png", "pdf", "svg"]:
    p = FIGURES / f"fig10_topic_x_mechanism_x_era_trajectory.{ext}"
    fig.savefig(p, dpi=300, bbox_inches="tight")
    print(f"  {p.relative_to(REPO)}  {p.stat().st_size/1024:7.1f} KB")
plt.close(fig)
print("\n[Done] Block 2.")