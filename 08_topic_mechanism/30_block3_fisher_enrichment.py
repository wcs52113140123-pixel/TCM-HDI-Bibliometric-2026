"""Day 13 Block 3: Fisher exact + BH-FDR enrichment for Topic x Mechanism.

Inputs:
  - results/tables/table_topic_x_mechanism_matrix_numericId.csv

Outputs:
  - results/tables/table_topic_x_mechanism_enrichment_full.csv
       (all 592 cells, with p, q, OR, direction)
  - results/tables/table_topic_x_mechanism_enrichment_significant.csv
       (q<0.05 only, sorted by OR desc within enriched / asc within depleted)
  - results/tables/table_topic_x_mechanism_top_enriched.csv
       (top 20 strongest enrichments for paper Table)
  - results/tables/table_topic_x_mechanism_top_depleted.csv
       (top 20 strongest depletions, where expected >= 5)

Test:
  Fisher exact two-sided per cell.
  2x2 contingency:
              has_mech    no_mech
  in_topic       a           b
  not_in_topic   c           d
  N = total cell sum = 1,738.
  Multiple-testing: BH-FDR across all 592 tests.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests

# ============================================================
# Paths
# ============================================================
REPO = Path(__file__).parent.parent
TABLES = REPO / "results" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

# ============================================================
# Load
# ============================================================
matrix = pd.read_csv(TABLES / "table_topic_x_mechanism_matrix_numericId.csv", index_col=0).astype(int)
with open(REPO / "data" / "processed" / "topic_labels.json", encoding="utf-8") as f:
    topic_labels = json.load(f)

def short_label(cid):
    entry = topic_labels.get(str(cid), {})
    kb = entry.get("top_keybert", [])
    terms = " / ".join(kb[:3]) if kb else "???"
    return terms[:60]

n_rows, n_cols = matrix.shape
N = int(matrix.values.sum())
print(f"[Load] matrix={matrix.shape}, N={N:,}")

# ============================================================
# Run Fisher exact for every cell
# ============================================================
topic_totals = matrix.sum(axis=1)
mech_totals = matrix.sum(axis=0)

results = []
for topic_id in matrix.index:
    t_total = int(topic_totals.loc[topic_id])
    for mech in matrix.columns:
        a = int(matrix.loc[topic_id, mech])
        m_total = int(mech_totals.loc[mech])
        b = t_total - a
        c = m_total - a
        d = N - t_total - m_total + a

        # Sanity
        assert a + b + c + d == N, f"2x2 sum mismatch at ({topic_id}, {mech})"

        # Fisher exact two-sided
        odds_ratio, p_value = fisher_exact(
            [[a, b], [c, d]], alternative="two-sided"
        )

        # Expected
        expected = t_total * m_total / N

        # Direction
        direction = "enriched" if a > expected else ("depleted" if a < expected else "neutral")

        # log2(OR) with Haldane-Anscombe (for display, not for p)
        log2_or_haldane = np.log2(((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5)))

        results.append({
            "cluster_id": int(topic_id),
            "topic_label": short_label(topic_id),
            "mechanism": mech,
            "observed": a,
            "expected": round(expected, 2),
            "topic_total": t_total,
            "mech_total": m_total,
            "odds_ratio": odds_ratio,           # raw Fisher OR; may be inf or 0
            "log2_or_haldane": round(log2_or_haldane, 3),
            "p_value": p_value,
            "direction": direction,
        })

df = pd.DataFrame(results)
print(f"[Tests] ran {len(df)} Fisher exact tests")

# ============================================================
# BH-FDR correction (across all 592 cells)
# ============================================================
df["q_value"] = multipletests(df["p_value"], method="fdr_bh")[1]
df["significant"] = df["q_value"] < 0.05

n_sig = df["significant"].sum()
n_sig_enr = ((df["significant"]) & (df["direction"] == "enriched")).sum()
n_sig_dep = ((df["significant"]) & (df["direction"] == "depleted")).sum()
print(f"[FDR] significant (q<0.05): {n_sig} / {len(df)}")
print(f"        enriched         : {n_sig_enr}")
print(f"        depleted         : {n_sig_dep}")

# ============================================================
# Save FULL results
# ============================================================
df_sorted = df.sort_values(["q_value", "p_value"]).reset_index(drop=True)
out1 = TABLES / "table_topic_x_mechanism_enrichment_full.csv"
df_sorted.to_csv(out1, index=False, encoding="utf-8")
print(f"\n[Saved] {out1.relative_to(REPO)}  ({out1.stat().st_size/1024:.1f} KB)")

# ============================================================
# Significant-only table
# ============================================================
df_sig = df[df["significant"]].copy()
df_sig_sorted = df_sig.sort_values(
    ["direction", "log2_or_haldane"],
    ascending=[True, False]  # enriched first (since 'd' < 'e'), then sort by effect size desc
).reset_index(drop=True)
out2 = TABLES / "table_topic_x_mechanism_enrichment_significant.csv"
df_sig_sorted.to_csv(out2, index=False, encoding="utf-8")
print(f"[Saved] {out2.relative_to(REPO)}  ({out2.stat().st_size/1024:.1f} KB)")

# ============================================================
# Top 20 strong enrichments (paper main table candidate)
# Filters: q<0.05, OR>2, observed>=5
# ============================================================
mask_enr = (
    (df["significant"])
    & (df["direction"] == "enriched")
    & (df["odds_ratio"] > 2)
    & (df["observed"] >= 5)
)
df_top_enr = df[mask_enr].sort_values("log2_or_haldane", ascending=False).head(20).reset_index(drop=True)
out3 = TABLES / "table_topic_x_mechanism_top_enriched.csv"
df_top_enr.to_csv(out3, index=False, encoding="utf-8")
print(f"[Saved] {out3.relative_to(REPO)}  ({out3.stat().st_size/1024:.1f} KB)  [{len(df_top_enr)} rows]")

# ============================================================
# Top 20 strong depletions (paper Discussion candidate)
# Filters: q<0.05, OR<0.5, expected>=5
# ============================================================
mask_dep = (
    (df["significant"])
    & (df["direction"] == "depleted")
    & (df["odds_ratio"] < 0.5)
    & (df["expected"] >= 5)
)
df_top_dep = df[mask_dep].sort_values("log2_or_haldane", ascending=True).head(20).reset_index(drop=True)
out4 = TABLES / "table_topic_x_mechanism_top_depleted.csv"
df_top_dep.to_csv(out4, index=False, encoding="utf-8")
print(f"[Saved] {out4.relative_to(REPO)}  ({out4.stat().st_size/1024:.1f} KB)  [{len(df_top_dep)} rows]")

# ============================================================
# Print preview
# ============================================================
print("\n" + "=" * 80)
print("TOP 20 STRONGEST ENRICHMENTS (q<0.05, OR>2, observed>=5)")
print("=" * 80)
preview_enr = df_top_enr[["cluster_id", "topic_label", "mechanism", "observed", "expected", "odds_ratio", "log2_or_haldane", "q_value"]].copy()
preview_enr["topic_label"] = preview_enr["topic_label"].str[:40]
preview_enr["q_value"] = preview_enr["q_value"].apply(lambda x: f"{x:.2e}")
preview_enr["odds_ratio"] = preview_enr["odds_ratio"].apply(lambda x: f"{x:.1f}" if not np.isinf(x) else "inf")
with pd.option_context("display.max_columns", None, "display.width", 200):
    print(preview_enr.to_string(index=False))

print("\n" + "=" * 80)
print(f"TOP 20 STRONGEST DEPLETIONS (q<0.05, OR<0.5, expected>=5)  [{len(df_top_dep)} rows total]")
print("=" * 80)
if len(df_top_dep) > 0:
    preview_dep = df_top_dep[["cluster_id", "topic_label", "mechanism", "observed", "expected", "odds_ratio", "log2_or_haldane", "q_value"]].copy()
    preview_dep["topic_label"] = preview_dep["topic_label"].str[:40]
    preview_dep["q_value"] = preview_dep["q_value"].apply(lambda x: f"{x:.2e}")
    preview_dep["odds_ratio"] = preview_dep["odds_ratio"].apply(lambda x: f"{x:.3f}")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(preview_dep.to_string(index=False))
else:
    print("  (none meet criteria — likely because depletion rarely reaches OR<0.5 with expected>=5 in sparse matrices)")

# ============================================================
# Summary statistics for the findings doc
# ============================================================
print("\n" + "=" * 80)
print("SUMMARY STATS (for notes_day13_findings.md)")
print("=" * 80)
print(f"Total cells tested              : {len(df)}")
print(f"Significant (q<0.05) cells      : {n_sig} ({n_sig/len(df)*100:.1f}%)")
print(f"  enriched                      : {n_sig_enr}")
print(f"  depleted                      : {n_sig_dep}")
print(f"Strong enrichments (OR>2, obs>=5): {mask_enr.sum()}")
print(f"Strong depletions  (OR<0.5, exp>=5): {mask_dep.sum()}")
print(f"\nBy mechanism (n strongly enriched in any topic):")
print(df[mask_enr].groupby("mechanism").size().sort_values(ascending=False).to_string())
print(f"\nBy topic (n strongly enriched mechanisms):")
print(df[mask_enr].groupby(["cluster_id", "topic_label"]).size().sort_values(ascending=False).head(15).to_string())

print("\n[Done] Block 3.")