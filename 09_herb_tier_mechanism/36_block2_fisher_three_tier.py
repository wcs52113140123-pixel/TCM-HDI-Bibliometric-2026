"""
Day 15 Block 2 -- Three-tier Fisher exact + within-tier BH-FDR
==============================================================
For each tier (family, species, compound):
  1. Read matrix from results/tables/
  2. Per-cell Fisher exact two-sided
  3. BH-FDR within tier
  4. Classify strong enrichment / depletion (Day 13 thresholds)
  5. Save 4 CSVs per tier: full, significant, top_enriched, top_depleted

Total: 12 output files.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests

REPO = Path(r"D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026")
TABLES = REPO / "results" / "tables"

TIERS = {
    "family":   "table_herb_family_x_mechanism_matrix.csv",
    "species":  "table_herb_species_x_mechanism_matrix.csv",
    "compound": "table_herb_compound_x_mechanism_matrix.csv",
}
ENTITY_LABEL = {
    "family":   "herb_family",
    "species":  "herb_canonical_latin",
    "compound": "herb_active_compound",
}

# Day 13 thresholds (locked)
Q_ALPHA = 0.05
OR_ENR = 2.0
OR_DEP = 0.5
OBS_MIN_ENR = 5
EXP_MIN_DEP = 5
HA = 0.5  # Haldane-Anscombe correction for log2(OR) display

def section(t): print(f"\n{'='*70}\n  {t}\n{'='*70}")

def fisher_one_tier(mat, tier_name, entity_label):
    """Run per-cell Fisher exact + BH-FDR on a single tier matrix."""
    rows = mat.index.tolist()
    cols = mat.columns.tolist()
    N = mat.values.sum()  # total pairs in this tier
    row_tot = mat.sum(axis=1)
    col_tot = mat.sum(axis=0)
    
    results = []
    for ent in rows:
        for mech in cols:
            obs = int(mat.at[ent, mech])
            row_t = int(row_tot[ent])
            col_t = int(col_tot[mech])
            # 2x2 table:
            #              mech    !mech
            #   entity    [ a       b   ]
            #  !entity    [ c       d   ]
            a = obs
            b = row_t - obs
            c = col_t - obs
            d = N - row_t - col_t + obs
            
            if a + b == 0 or c + d == 0 or a + c == 0 or b + d == 0:
                # degenerate — skip
                continue
            
            exp = row_t * col_t / N if N else 0
            OR_raw, p = fisher_exact([[a, b], [c, d]], alternative="two-sided")
            # Haldane-Anscombe for stable log display
            OR_ha = ((a + HA) * (d + HA)) / ((b + HA) * (c + HA))
            log2_OR_ha = np.log2(OR_ha)
            
            results.append({
                "tier": tier_name,
                entity_label: ent,
                "mechanism": mech,
                "obs": obs,
                "expected": exp,
                "row_total": row_t,
                "col_total": col_t,
                "N_tier": N,
                "OR_raw": OR_raw,
                "OR_ha": OR_ha,
                "log2_OR_ha": log2_OR_ha,
                "p": p,
            })
    
    df = pd.DataFrame(results)
    # BH-FDR within tier
    _, q, _, _ = multipletests(df["p"].values, method="fdr_bh")
    df["q"] = q
    
    # Classification
    def classify(row):
        if row["q"] < Q_ALPHA:
            if row["OR_raw"] > OR_ENR and row["obs"] >= OBS_MIN_ENR:
                return "strong_enrichment"
            if row["OR_raw"] < OR_DEP and row["expected"] >= EXP_MIN_DEP:
                return "strong_depletion"
            return "weak_sig"
        return "ns"
    df["classification"] = df.apply(classify, axis=1)
    return df

section("1. Run Fisher per tier")
all_results = {}
for tier, fname in TIERS.items():
    fpath = TABLES / fname
    mat = pd.read_csv(fpath, index_col=0).astype(int)
    print(f"\n[{tier}]  matrix {mat.shape}, N_tier={mat.values.sum():,}")
    df = fisher_one_tier(mat, tier, ENTITY_LABEL[tier])
    all_results[tier] = df
    n_se = (df["classification"] == "strong_enrichment").sum()
    n_sd = (df["classification"] == "strong_depletion").sum()
    n_w  = (df["classification"] == "weak_sig").sum()
    n_ns = (df["classification"] == "ns").sum()
    print(f"  cells tested: {len(df):,}")
    print(f"  strong enrichment: {n_se}   strong depletion: {n_sd}   weak_sig: {n_w}   ns: {n_ns}")

section("2. Save 4 CSVs per tier")
for tier, df in all_results.items():
    base = f"table_herb_{tier}_x_mechanism"
    
    # Full
    full_path = TABLES / f"{base}_enrichment_full.csv"
    df.sort_values(["q", "p"]).to_csv(full_path, index=False)
    
    # Significant (q<0.05)
    df_sig = df[df["q"] < Q_ALPHA].sort_values(["q", "p"])
    sig_path = TABLES / f"{base}_enrichment_significant.csv"
    df_sig.to_csv(sig_path, index=False)
    
    # Top 20 enriched
    df_enr = df[df["classification"] == "strong_enrichment"].copy()
    df_enr = df_enr.sort_values("log2_OR_ha", ascending=False).head(20)
    enr_path = TABLES / f"{base}_top_enriched.csv"
    df_enr.to_csv(enr_path, index=False)
    
    # Top 20 depleted
    df_dep = df[df["classification"] == "strong_depletion"].copy()
    df_dep = df_dep.sort_values("log2_OR_ha", ascending=True).head(20)
    dep_path = TABLES / f"{base}_top_depleted.csv"
    df_dep.to_csv(dep_path, index=False)
    
    print(f"  [{tier}] full={len(df)}  sig={len(df_sig)}  enr={len(df_enr)}  dep={len(df_dep)}")

section("3. Diagnostics -- top-5 enriched per tier")
for tier, df in all_results.items():
    df_enr = df[df["classification"] == "strong_enrichment"].sort_values("log2_OR_ha", ascending=False)
    print(f"\n[{tier}] top-5 enrichments:")
    if len(df_enr) == 0:
        print("  (none)")
        continue
    entity_col = ENTITY_LABEL[tier]
    for _, r in df_enr.head(5).iterrows():
        print(f"  {str(r[entity_col]):<32s} x {r['mechanism']:<32s}  obs={int(r['obs']):>3}  OR={r['OR_raw']:>8.2f}  q={r['q']:.2e}")

section("4. Diagnostics -- top-5 depleted per tier")
for tier, df in all_results.items():
    df_dep = df[df["classification"] == "strong_depletion"].sort_values("log2_OR_ha", ascending=True)
    print(f"\n[{tier}] top-5 depletions:")
    if len(df_dep) == 0:
        print("  (none)")
        continue
    entity_col = ENTITY_LABEL[tier]
    for _, r in df_dep.head(5).iterrows():
        print(f"  {str(r[entity_col]):<32s} x {r['mechanism']:<32s}  obs={int(r['obs']):>3}  OR={r['OR_raw']:>8.2f}  q={r['q']:.2e}")

section("5. SJW chain enrichment check")
# Hypericaceae / Hypericum perforatum / hyperforin x CYP_induction
targets = [
    ("family",   "Hypericaceae",          "CYP_induction"),
    ("species",  "Hypericum perforatum",  "CYP_induction"),
    ("compound", "hyperforin",            "CYP_induction"),
]
for tier, ent, mech in targets:
    df = all_results[tier]
    entity_col = ENTITY_LABEL[tier]
    row = df[(df[entity_col] == ent) & (df["mechanism"] == mech)]
    if len(row) == 0:
        print(f"  [{tier}] {ent} x {mech}: NOT FOUND")
        continue
    r = row.iloc[0]
    print(f"  [{tier:<8}] {ent:<24s} x {mech}  obs={int(r['obs']):>3}  exp={r['expected']:>6.2f}  OR={r['OR_raw']:>8.2f}  q={r['q']:.2e}  cls={r['classification']}")

print("\n=== Block 2 COMPLETE ===")