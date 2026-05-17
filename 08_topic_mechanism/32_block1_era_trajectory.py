"""Day 14 Block 1: era-stratified matrices + trajectory classification.

For each Day 13 strong enrichment (n=30) and strong depletion (n=29) pair,
compute per-era Fisher exact + BH-FDR within era, then classify temporal
trajectory across 3 disjoint periods.

Era scheme (from Day 14 Block 0):
  Period 1 (2005-2013) - Classical case-based era
  Period 2 (2014-2019) - Mechanistic deepening era
  Period 3 (2020-2026) - Systems-level era
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests

REPO = Path(__file__).parent.parent
P = REPO / "data" / "processed"
TABLES = REPO / "results" / "tables"

# ============================================================
# Era definition
# ============================================================
ERAS = [
    ("Period 1", 2005, 2013, "Classical case-based"),
    ("Period 2", 2014, 2019, "Mechanistic deepening"),
    ("Period 3", 2020, 2026, "Systems-level"),
]

TRAJECTORY_MAP = {
    (1, 1, 1): "STABLE",
    (0, 0, 1): "EMERGING",
    (1, 0, 0): "DECLINING",
    (0, 1, 1): "RISING",
    (1, 1, 0): "FADING",
    (0, 1, 0): "TRANSIENT_MIDDLE",
    (1, 0, 1): "BIMODAL",
    (0, 0, 0): "WEAK_NONE",
}

# ============================================================
# Load
# ============================================================
interactions = pd.read_parquet(P / "llm_extraction" / "primary_openai__gpt-4o-mini.interactions_normalized.parquet")
clusters = pd.read_parquet(P / "cluster_assignments.parquet")
with open(P / "topic_labels.json", encoding="utf-8") as f:
    topic_labels = json.load(f)

df_enr = pd.read_csv(TABLES / "table_topic_x_mechanism_top_enriched.csv")
df_dep = pd.read_csv(TABLES / "table_topic_x_mechanism_top_depleted.csv")
ref_matrix = pd.read_csv(TABLES / "table_topic_x_mechanism_matrix_numericId.csv", index_col=0).astype(int)

# Day 13 filter pipeline
NOISE_MECH = {"unspecified", "other"}
mech_clean = interactions[~interactions["mechanism"].isin(NOISE_MECH)]
rec_mech = mech_clean[["record_id", "mechanism", "year"]].drop_duplicates(subset=["record_id", "mechanism"])
clusters_clean = clusters[clusters["cluster_id"] != -1][["record_id", "cluster_id"]]
merged = rec_mech.merge(clusters_clean, on="record_id", how="inner")

print(f"[Load] {len(merged)} pairs, {merged['record_id'].nunique()} records")
print(f"[Day 13 reference] {len(df_enr)} enrichments + {len(df_dep)} depletions")

# ============================================================
# Build per-era matrices (37 topics x 16 mechs each, fill 0)
# ============================================================
era_matrices = {}
for label, start, end, _ in ERAS:
    era_df = merged[(merged["year"] >= start) & (merged["year"] <= end)]
    mat = era_df.groupby(["cluster_id", "mechanism"]).size().unstack(fill_value=0).astype(int)
    mat = mat.reindex(index=ref_matrix.index, columns=ref_matrix.columns, fill_value=0)
    era_matrices[label] = mat

    p_n = label.split()[-1]
    out_path = TABLES / f"table_topic_x_mechanism_era_matrix_period{p_n}.csv"
    mat.to_csv(out_path)
    print(f"[{label} {start}-{end}] N={mat.values.sum():,}, "
          f"non-zero {(mat > 0).sum().sum()} cells -> {out_path.name}")

# ============================================================
# Helpers
# ============================================================
def short_label(cid):
    entry = topic_labels.get(str(cid), {})
    kb = entry.get("top_keybert", [])
    return " / ".join(kb[:3])[:55] if kb else "???"

def fisher_one_cell(mat, topic_id, mech):
    a = int(mat.loc[topic_id, mech])
    t_total = int(mat.loc[topic_id].sum())
    m_total = int(mat[mech].sum())
    N = int(mat.values.sum())
    b = t_total - a
    c = m_total - a
    d = N - t_total - m_total + a
    if N == 0 or t_total == 0 or m_total == 0:
        return {"observed": a, "expected": 0.0, "OR": np.nan, "p": 1.0}
    or_val, p = fisher_exact([[a, b], [c, d]], alternative="two-sided")
    expected = t_total * m_total / N
    return {"observed": a, "expected": expected, "OR": or_val, "p": p}

def trajectory_analysis(df_pairs, mode, name):
    """
    mode: 'enrichment' (obs > exp) or 'depletion' (obs < exp).
    """
    rows = []
    for _, r in df_pairs.iterrows():
        cid = int(r["cluster_id"])
        mech = r["mechanism"]
        row = {
            "cluster_id": cid,
            "topic_label": short_label(cid),
            "mechanism": mech,
            "global_OR": r["odds_ratio"],
            "global_q": r["q_value"],
        }
        for label, _, _, _ in ERAS:
            stats = fisher_one_cell(era_matrices[label], cid, mech)
            p_n = label.split()[-1]
            row[f"p{p_n}_obs"] = stats["observed"]
            row[f"p{p_n}_exp"] = round(stats["expected"], 2)
            row[f"p{p_n}_OR"] = stats["OR"]
            row[f"p{p_n}_p"] = stats["p"]
        rows.append(row)

    out = pd.DataFrame(rows)

    # BH-FDR within each era's test family
    for p_n in ["1", "2", "3"]:
        out[f"p{p_n}_q"] = multipletests(out[f"p{p_n}_p"], method="fdr_bh")[1]
        # Significant requires q<0.05 AND correct direction
        if mode == "enrichment":
            out[f"p{p_n}_sig"] = (out[f"p{p_n}_q"] < 0.05) & (out[f"p{p_n}_obs"] > out[f"p{p_n}_exp"])
        else:  # depletion
            out[f"p{p_n}_sig"] = (out[f"p{p_n}_q"] < 0.05) & (out[f"p{p_n}_obs"] < out[f"p{p_n}_exp"])

    # Classify trajectory
    out["trajectory"] = out.apply(
        lambda r: TRAJECTORY_MAP[(int(r["p1_sig"]), int(r["p2_sig"]), int(r["p3_sig"]))],
        axis=1
    )

    out_path = TABLES / f"table_topic_x_mechanism_trajectory_{name}.csv"
    out.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\n[{name}] saved -> {out_path.name}  ({len(out)} pairs)")

    # Summary
    print(f"  trajectory distribution:")
    for t, n in out["trajectory"].value_counts().items():
        print(f"    {t:<20s} {n}")
    return out

# ============================================================
# Run
# ============================================================
print("\n" + "=" * 70)
print("ENRICHMENT TRAJECTORIES (Day 13's 30 strong enrichments)")
print("=" * 70)
df_enr_traj = trajectory_analysis(df_enr, "enrichment", "enrichment")

print("\n" + "=" * 70)
print("DEPLETION TRAJECTORIES (Day 13's 29 strong depletions)")
print("=" * 70)
df_dep_traj = trajectory_analysis(df_dep, "depletion", "depletion")

# ============================================================
# Preview
# ============================================================
print("\n" + "=" * 70)
print("PREVIEW: 10 most informative enrichment trajectories (mixed classes)")
print("=" * 70)
cols = ["cluster_id", "topic_label", "mechanism",
        "p1_obs", "p2_obs", "p3_obs",
        "p1_sig", "p2_sig", "p3_sig", "trajectory"]
# Order by trajectory then by observed sum desc
pv = df_enr_traj.copy()
pv["topic_label"] = pv["topic_label"].str[:35]
pv["_total"] = pv["p1_obs"] + pv["p2_obs"] + pv["p3_obs"]
pv = pv.sort_values(["trajectory", "_total"], ascending=[True, False])
with pd.option_context("display.max_columns", None, "display.width", 200):
    print(pv[cols].head(15).to_string(index=False))

print("\n" + "=" * 70)
print("PREVIEW: depletion trajectories (key insight: are depletions stable?)")
print("=" * 70)
pv2 = df_dep_traj.copy()
pv2["topic_label"] = pv2["topic_label"].str[:35]
pv2["_total"] = pv2["p1_obs"] + pv2["p2_obs"] + pv2["p3_obs"]
pv2 = pv2.sort_values(["trajectory"])
with pd.option_context("display.max_columns", None, "display.width", 200):
    print(pv2[cols].head(15).to_string(index=False))

print("\n[Done] Block 1.")