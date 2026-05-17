"""
Day 15 Block 1 -- Data cleaning + 3-tier matrix construction
============================================================
Decisions (locked):
- Entity min frequency: >= 10 records
- Tier 1/2: herb_in_map = True only (same record pool for cross-tier)
- Tier 3: also restricted to herb_in_map = True (cross-tier consistency)
- Drop "null"/"unknown"/"not specified"/"" string-as-value
- Drop herb_family = "flavonoid_compound" (Schema v3 placeholder hack)
- Confidence >= 0.7 (Day 13 alignment)
- Drop mechanism in {unspecified, other}

Outputs:
- data/processed/herb_tier_clean.parquet (cleaned long-form for B2/B3)
- results/tables/table_herb_{family,species,compound}_x_mechanism_matrix.csv
- results/tables/table_herb_{family,species,compound}_{row,mech}_marginals.csv
- results/tables/table_herb_formula_supp_descriptive.csv (top-15, no Fisher)
"""

import pandas as pd
import numpy as np
from pathlib import Path

REPO = Path(r"D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026")
INPUT = REPO / "data" / "processed" / "llm_extraction" / "primary_openai__gpt-4o-mini.interactions_normalized.parquet"
TABLES_DIR = REPO / "results" / "tables"
DATA_DIR = REPO / "data" / "processed"
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Constants
ENTITY_MIN = {"family": 10, "species": 10, "compound": 5}  # heterogeneous threshold
CONF_MIN = 0.7
EXCL_MECH = {"unspecified", "other"}
NULL_STRINGS = {"null", "unknown", "not specified", "nan", "none", ""}

def section(t): print(f"\n{'='*70}\n  {t}\n{'='*70}")

# ============================================================
# 1. Load
# ============================================================
section("1. Load LLM extraction")
df = pd.read_parquet(INPUT)
print(f"Raw: {len(df):,} interactions, {df['record_id'].nunique():,} unique records")

# ============================================================
# 2. Universal filtering (Day 13 alignment)
# ============================================================
section("2. Universal filtering (confidence + mechanism)")
df_u = df[df["confidence"].astype(float) >= CONF_MIN].copy()
print(f"After confidence >= {CONF_MIN}: {len(df_u):,}")
df_u = df_u[~df_u["mechanism"].astype(str).isin(EXCL_MECH)].copy()
print(f"After drop unspec/other mechanism: {len(df_u):,} ({df_u['record_id'].nunique():,} records)")

# ============================================================
# 3. Apply herb_in_map = True restriction (for ALL three tiers)
# ============================================================
section("3. herb_in_map = True restriction")
df_mapped = df_u[df_u["herb_in_map"] == True].copy()
print(f"After in_map=True: {len(df_mapped):,} ({df_mapped['record_id'].nunique():,} records)")

# ============================================================
# 4. Tier-specific cleaning
# ============================================================
section("4. Tier-specific cleaning")

def clean_str(s):
    if pd.isna(s): return None
    s2 = str(s).strip().lower()
    if s2 in NULL_STRINGS: return None
    return s

# Tier 1: Family (exclude flavonoid_compound)
df_t1 = df_mapped[df_mapped["herb_family"].notna()].copy()
df_t1 = df_t1[df_t1["herb_family"] != "flavonoid_compound"].copy()
df_t1 = df_t1.drop_duplicates(subset=["record_id", "herb_family", "mechanism"])
print(f"Tier 1 (family): {len(df_t1):,} pairs, {df_t1['record_id'].nunique():,} records")

# Tier 2: Species (canonical_latin)
df_t2 = df_mapped.copy()
df_t2["herb_canonical_latin_clean"] = df_t2["herb_canonical_latin"].apply(clean_str)
df_t2 = df_t2[df_t2["herb_canonical_latin_clean"].notna()].copy()
df_t2 = df_t2.drop_duplicates(subset=["record_id", "herb_canonical_latin_clean", "mechanism"])
print(f"Tier 2 (species): {len(df_t2):,} pairs, {df_t2['record_id'].nunique():,} records")

# Tier 3: Compound
df_t3 = df_mapped.copy()
df_t3["herb_active_compound_clean"] = df_t3["herb_active_compound"].apply(clean_str)
df_t3 = df_t3[df_t3["herb_active_compound_clean"].notna()].copy()
df_t3 = df_t3.drop_duplicates(subset=["record_id", "herb_active_compound_clean", "mechanism"])
print(f"Tier 3 (compound): {len(df_t3):,} pairs, {df_t3['record_id'].nunique():,} records")

# Supp: Formula (NO in_map restriction -- formula has independent normalization)
df_sf = df_u.copy()
df_sf["tcm_formula_name_clean"] = df_sf["tcm_formula_name"].apply(clean_str)
df_sf = df_sf[df_sf["tcm_formula_name_clean"].notna()].copy()
df_sf = df_sf.drop_duplicates(subset=["record_id", "tcm_formula_name_clean", "mechanism"])
print(f"Supp  (formula): {len(df_sf):,} pairs, {df_sf['record_id'].nunique():,} records")

# ============================================================
# 5. Entity frequency filtering (>= ENTITY_MIN records per entity)
# ============================================================
section(f"5. Entity frequency filter (per-tier: {ENTITY_MIN})")

def filter_by_min(d, col, min_n):
    counts = d.groupby(col)["record_id"].nunique()
    keep = counts[counts >= min_n].index
    d2 = d[d[col].isin(keep)].copy()
    return d2, len(keep), len(counts), counts

df_t1_f, n_f, tot_f, _ = filter_by_min(df_t1, "herb_family", ENTITY_MIN["family"])
df_t2_f, n_s, tot_s, _ = filter_by_min(df_t2, "herb_canonical_latin_clean", ENTITY_MIN["species"])
df_t3_f, n_c, tot_c, _ = filter_by_min(df_t3, "herb_active_compound_clean", ENTITY_MIN["compound"])
print(f"Family:   kept {n_f:>3,} / {tot_f:>3,} entities  ({len(df_t1_f):,} pairs)")
print(f"Species:  kept {n_s:>3,} / {tot_s:>3,} entities  ({len(df_t2_f):,} pairs)")
print(f"Compound: kept {n_c:>3,} / {tot_c:>3,} entities  ({len(df_t3_f):,} pairs)")

# ============================================================
# 6. Build matrices (count of unique records per entity x mechanism)
# ============================================================
section("6. Build entity x mechanism matrices")

def build_matrix(d, col):
    return d.groupby([col, "mechanism"])["record_id"].nunique().unstack(fill_value=0).astype(int)

mat_f = build_matrix(df_t1_f, "herb_family")
mat_s = build_matrix(df_t2_f, "herb_canonical_latin_clean")
mat_c = build_matrix(df_t3_f, "herb_active_compound_clean")
print(f"Family matrix:   {mat_f.shape[0]:>3} entities x {mat_f.shape[1]:>2} mechanisms = {mat_f.size:>4} cells")
print(f"Species matrix:  {mat_s.shape[0]:>3} entities x {mat_s.shape[1]:>2} mechanisms = {mat_s.size:>4} cells")
print(f"Compound matrix: {mat_c.shape[0]:>3} entities x {mat_c.shape[1]:>2} mechanisms = {mat_c.size:>4} cells")
print(f"TOTAL Fisher tests across 3 tiers: {mat_f.size + mat_s.size + mat_c.size:,}")

# ============================================================
# 7. Save matrices + marginals
# ============================================================
section("7. Save matrices + marginals")

def save_tier(mat, base_name, entity_label):
    # Order rows by total (descending), cols by total
    mat = mat.copy()
    mat.index.name = entity_label
    row_tot = mat.sum(axis=1).sort_values(ascending=False)
    col_tot = mat.sum(axis=0).sort_values(ascending=False)
    mat_ordered = mat.loc[row_tot.index, col_tot.index]
    
    mat_path = TABLES_DIR / f"table_herb_{base_name}_x_mechanism_matrix.csv"
    mat_ordered.to_csv(mat_path)
    
    row_tot.rename("total_records").to_csv(TABLES_DIR / f"table_herb_{base_name}_row_marginals.csv", header=True)
    col_tot.rename("total_records").to_csv(TABLES_DIR / f"table_herb_{base_name}_mech_marginals.csv", header=True)
    
    print(f"  {base_name:>9}: {mat_path.name}")
    return row_tot, col_tot

row_f, col_f = save_tier(mat_f, "family", "herb_family")
row_s, col_s = save_tier(mat_s, "species", "herb_canonical_latin")
row_c, col_c = save_tier(mat_c, "compound", "herb_active_compound")

# ============================================================
# 8. Supp formula descriptive (top-15, no Fisher)
# ============================================================
section("8. Supplementary formula descriptive (top-15)")
top15_f = df_sf.groupby("tcm_formula_name_clean")["record_id"].nunique().sort_values(ascending=False).head(15).index
df_sf_top = df_sf[df_sf["tcm_formula_name_clean"].isin(top15_f)].copy()
sup_mat = df_sf_top.groupby(["tcm_formula_name_clean", "mechanism"])["record_id"].nunique().unstack(fill_value=0).astype(int)
sup_mat.index.name = "tcm_formula"
sup_row_tot = sup_mat.sum(axis=1).sort_values(ascending=False)
sup_mat = sup_mat.loc[sup_row_tot.index]
sup_mat.to_csv(TABLES_DIR / "table_herb_formula_supp_descriptive.csv")
print(f"Supp formula matrix (top-15): {sup_mat.shape[0]} formulas x {sup_mat.shape[1]} mechanisms")
print(f"Row totals (records per formula): min={sup_row_tot.min()}, median={sup_row_tot.median():.0f}, max={sup_row_tot.max()}")

# ============================================================
# 9. Save clean long-form parquet (for Block 2/3)
# ============================================================
section("9. Save clean long-form parquet")
clean_parts = [
    df_t1_f[["record_id", "year", "cluster_id", "mechanism", "confidence", "herb_family"]]
        .rename(columns={"herb_family": "_entity"})
        .assign(_tier="family"),
    df_t2_f[["record_id", "year", "cluster_id", "mechanism", "confidence", "herb_canonical_latin_clean"]]
        .rename(columns={"herb_canonical_latin_clean": "_entity"})
        .assign(_tier="species"),
    df_t3_f[["record_id", "year", "cluster_id", "mechanism", "confidence", "herb_active_compound_clean"]]
        .rename(columns={"herb_active_compound_clean": "_entity"})
        .assign(_tier="compound"),
]
df_clean = pd.concat(clean_parts, ignore_index=True)
clean_path = DATA_DIR / "herb_tier_clean.parquet"
df_clean.to_parquet(clean_path)
print(f"Saved: {clean_path}  ({len(df_clean):,} rows)")
print(f"  Tier breakdown: {df_clean['_tier'].value_counts().to_dict()}")

# ============================================================
# 10. Diagnostic snapshots
# ============================================================
section("10. Diagnostics -- Top-10 entities per tier (record totals)")
print("\n[Family] top-10 by record total:")
print(row_f.head(10).to_string())

print("\n[Species] top-10 by record total:")
print(row_s.head(10).to_string())

print("\n[Compound] top-10 by record total:")
print(row_c.head(10).to_string())

section("11. Mechanism marginals (records per mechanism across tiers)")
mech_summary = pd.DataFrame({
    "family": col_f,
    "species": col_s,
    "compound": col_c,
}).fillna(0).astype(int)
mech_summary["sum"] = mech_summary.sum(axis=1)
mech_summary = mech_summary.sort_values("sum", ascending=False)
print(mech_summary.to_string())

section("12. Sanity check -- SJW signature preview")
# Pull SJW species row + Hypericaceae family row + hyperforin compound row
sjw_targets = {
    "family": ("Hypericaceae", row_f, mat_f),
    "species": ("Hypericum perforatum", row_s, mat_s),
    "compound": ("hyperforin", row_c, mat_c),
}
for tier, (ent, row_tot, mat) in sjw_targets.items():
    if ent in mat.index:
        print(f"\n[{tier}] '{ent}' (total {row_tot[ent]} records):")
        cell_row = mat.loc[ent].sort_values(ascending=False)
        for mech, cnt in cell_row.items():
            if cnt > 0:
                print(f"    {mech:<32s} {cnt:>4}")
    else:
        print(f"\n[{tier}] '{ent}' NOT in retained matrix (below ENTITY_MIN threshold?)")

print("\n=== Block 1 COMPLETE ===")