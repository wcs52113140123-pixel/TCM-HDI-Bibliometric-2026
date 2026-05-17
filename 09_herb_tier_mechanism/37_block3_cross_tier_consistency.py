"""
Day 15 Block 3 -- Cross-tier consistency analysis
==================================================
For each (mechanism, family, species, compound) co-occurrence,
look up tier-level enrichment status and classify into 8 chain classes.

Inputs:
  - Block 2 outputs: table_herb_{family,species,compound}_x_mechanism_enrichment_full.csv
  - Original parquet: interactions_normalized.parquet (for hierarchy)
Outputs:
  - table_herb_cross_tier_chains.csv  (1 row per chain link)
  - table_herb_cross_tier_consistency_summary.csv  (per-mechanism aggregate)
"""
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

REPO = Path(r"D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026")
INPUT = REPO / "data" / "processed" / "llm_extraction" / "primary_openai__gpt-4o-mini.interactions_normalized.parquet"
TABLES = REPO / "results" / "tables"

NULL_STRINGS = {"null", "unknown", "not specified", "nan", "none", ""}

def section(t): print(f"\n{'='*70}\n  {t}\n{'='*70}")

# ============================================================
# 1. Load Block 2 results + build lookups
# ============================================================
section("1. Load Block 2 Fisher results")
df_fam = pd.read_csv(TABLES / "table_herb_family_x_mechanism_enrichment_full.csv")
df_sp  = pd.read_csv(TABLES / "table_herb_species_x_mechanism_enrichment_full.csv")
df_cp  = pd.read_csv(TABLES / "table_herb_compound_x_mechanism_enrichment_full.csv")
print(f"  Family Fisher rows:   {len(df_fam):,}")
print(f"  Species Fisher rows:  {len(df_sp):,}")
print(f"  Compound Fisher rows: {len(df_cp):,}")

fam_lk = df_fam.set_index(["herb_family", "mechanism"])
sp_lk  = df_sp.set_index(["herb_canonical_latin", "mechanism"])
cp_lk  = df_cp.set_index(["herb_active_compound", "mechanism"])

retained_families  = set(df_fam["herb_family"].unique())
retained_species   = set(df_sp["herb_canonical_latin"].unique())
retained_compounds = set(df_cp["herb_active_compound"].unique())
print(f"  Retained: {len(retained_families)} families, {len(retained_species)} species, {len(retained_compounds)} compounds")

# ============================================================
# 2. Build hierarchy from interactions parquet
# ============================================================
section("2. Build family -> species -> compound hierarchy")
df = pd.read_parquet(INPUT)
df = df[
    (df["herb_in_map"] == True) &
    (df["confidence"].astype(float) >= 0.7) &
    (~df["mechanism"].astype(str).isin(["unspecified", "other"])) &
    (df["herb_family"].notna()) &
    (df["herb_family"] != "flavonoid_compound")
].copy()

def clean_str(s):
    if pd.isna(s): return None
    s2 = str(s).strip().lower()
    if s2 in NULL_STRINGS: return None
    return s

df["sp_clean"] = df["herb_canonical_latin"].apply(clean_str)
df["cp_clean"] = df["herb_active_compound"].apply(clean_str)
df = df[df["sp_clean"].notna()]

# Family -> set of species (retained only)
fam_to_sp = defaultdict(set)
for fam, sp in df[df["sp_clean"].isin(retained_species)][["herb_family", "sp_clean"]].drop_duplicates().values:
    if fam in retained_families:
        fam_to_sp[fam].add(sp)

# Species -> set of compounds (retained only)
sp_to_cp = defaultdict(set)
for sp, cp in df[df["cp_clean"].isin(retained_compounds)][["sp_clean", "cp_clean"]].drop_duplicates().values:
    if sp in retained_species:
        sp_to_cp[sp].add(cp)

print("\nFamily -> retained species:")
for fam in sorted(fam_to_sp):
    sps = sorted(fam_to_sp[fam])
    print(f"  {fam:<22s}: {sps}")

print("\nSpecies -> retained compounds:")
for sp in sorted(sp_to_cp):
    cps = sorted(sp_to_cp[sp])
    if cps:
        print(f"  {sp:<28s}: {cps}")

# ============================================================
# 3. Build chain rows (one per family-mechanism with downstream walk)
# ============================================================
section("3. Walk chains per (mechanism, family) -> species -> compound")

def get(lk, key, field, default=None):
    try:
        return lk.loc[key, field]
    except (KeyError, IndexError):
        return default

mechanisms = sorted(set(df_fam["mechanism"]) | set(df_sp["mechanism"]) | set(df_cp["mechanism"]))
chain_rows = []

for mech in mechanisms:
    for fam in sorted(retained_families):
        fam_key = (fam, mech)
        f_obs = get(fam_lk, fam_key, "obs", 0)
        f_or  = get(fam_lk, fam_key, "OR_raw", np.nan)
        f_q   = get(fam_lk, fam_key, "q", np.nan)
        f_cls = get(fam_lk, fam_key, "classification", "ns")
        f_sig = (f_cls == "strong_enrichment")
        
        species_under_fam = sorted(fam_to_sp.get(fam, []))
        
        if not species_under_fam:
            # Family with no retained species under it (rare)
            chain_rows.append({
                "mechanism": mech,
                "family": fam, "family_obs": f_obs, "family_OR": f_or, "family_q": f_q, "family_sig": f_sig,
                "species": None, "species_obs": None, "species_OR": None, "species_q": None, "species_sig": False,
                "compound": None, "compound_obs": None, "compound_OR": None, "compound_q": None, "compound_sig": False,
            })
            continue
        
        for sp in species_under_fam:
            sp_key = (sp, mech)
            s_obs = get(sp_lk, sp_key, "obs", 0)
            s_or  = get(sp_lk, sp_key, "OR_raw", np.nan)
            s_q   = get(sp_lk, sp_key, "q", np.nan)
            s_cls = get(sp_lk, sp_key, "classification", "ns")
            s_sig = (s_cls == "strong_enrichment")
            
            compounds_under_sp = sorted(sp_to_cp.get(sp, []))
            if not compounds_under_sp:
                chain_rows.append({
                    "mechanism": mech,
                    "family": fam, "family_obs": f_obs, "family_OR": f_or, "family_q": f_q, "family_sig": f_sig,
                    "species": sp, "species_obs": s_obs, "species_OR": s_or, "species_q": s_q, "species_sig": s_sig,
                    "compound": None, "compound_obs": None, "compound_OR": None, "compound_q": None, "compound_sig": False,
                })
            else:
                for cp in compounds_under_sp:
                    cp_key = (cp, mech)
                    c_obs = get(cp_lk, cp_key, "obs", 0)
                    c_or  = get(cp_lk, cp_key, "OR_raw", np.nan)
                    c_q   = get(cp_lk, cp_key, "q", np.nan)
                    c_cls = get(cp_lk, cp_key, "classification", "ns")
                    c_sig = (c_cls == "strong_enrichment")
                    
                    chain_rows.append({
                        "mechanism": mech,
                        "family": fam, "family_obs": f_obs, "family_OR": f_or, "family_q": f_q, "family_sig": f_sig,
                        "species": sp, "species_obs": s_obs, "species_OR": s_or, "species_q": s_q, "species_sig": s_sig,
                        "compound": cp, "compound_obs": c_obs, "compound_OR": c_or, "compound_q": c_q, "compound_sig": c_sig,
                    })

df_chain = pd.DataFrame(chain_rows)

# ============================================================
# 4. Classify chains
# ============================================================
section("4. Classify chains (8-class)")

def classify(row):
    f, s, c = row["family_sig"], row["species_sig"], row["compound_sig"]
    has_c = row["compound"] is not None
    if f and s and c: return "FULL_CHAIN"
    if f and s and not has_c: return "FAMILY_SPECIES_NO_COMPOUND_DATA"
    if f and s and has_c and not c: return "F_S_COMPOUND_NOT_SIG"
    if f and not s: return "FAMILY_PERVASIVE"
    if not f and s and c: return "SPECIES_COMPOUND_NO_FAMILY"
    if not f and s: return "SPECIES_SPECIFIC"
    if not f and not s and c: return "COMPOUND_ORPHAN"
    return "ALL_NS"

df_chain["chain_class"] = df_chain.apply(classify, axis=1)

# Only keep rows where AT LEAST ONE tier is sig (drop the all-ns noise)
df_chain_sig = df_chain[df_chain["chain_class"] != "ALL_NS"].copy()
print(f"\nChain rows: {len(df_chain):,} total, {len(df_chain_sig):,} with >=1 tier sig")
print(f"\nChain class distribution (sig-only):")
print(df_chain_sig["chain_class"].value_counts().to_string())

# Save
chain_path = TABLES / "table_herb_cross_tier_chains.csv"
df_chain_sig.sort_values(["mechanism", "family", "species", "compound"]).to_csv(chain_path, index=False)
print(f"\nSaved: {chain_path.name}")

# ============================================================
# 5. Per-mechanism summary
# ============================================================
section("5. Per-mechanism consistency summary")

summary_rows = []
for mech in sorted(df_chain_sig["mechanism"].unique()):
    sub = df_chain_sig[df_chain_sig["mechanism"] == mech]
    summary_rows.append({
        "mechanism": mech,
        "n_chains": len(sub),
        "n_FULL_CHAIN": (sub["chain_class"] == "FULL_CHAIN").sum(),
        "n_FAMILY_SPECIES_NO_COMPOUND_DATA": (sub["chain_class"] == "FAMILY_SPECIES_NO_COMPOUND_DATA").sum(),
        "n_F_S_COMPOUND_NOT_SIG": (sub["chain_class"] == "F_S_COMPOUND_NOT_SIG").sum(),
        "n_FAMILY_PERVASIVE": (sub["chain_class"] == "FAMILY_PERVASIVE").sum(),
        "n_SPECIES_SPECIFIC": (sub["chain_class"] == "SPECIES_SPECIFIC").sum(),
        "n_SPECIES_COMPOUND_NO_FAMILY": (sub["chain_class"] == "SPECIES_COMPOUND_NO_FAMILY").sum(),
        "n_COMPOUND_ORPHAN": (sub["chain_class"] == "COMPOUND_ORPHAN").sum(),
        "families_involved": ", ".join(sorted(sub["family"].unique())),
    })
df_summary = pd.DataFrame(summary_rows).sort_values("n_chains", ascending=False)
summary_path = TABLES / "table_herb_cross_tier_consistency_summary.csv"
df_summary.to_csv(summary_path, index=False)
print(df_summary.to_string(index=False))
print(f"\nSaved: {summary_path.name}")

# ============================================================
# 6. Narrative print: each significant chain
# ============================================================
section("6. Narrative -- each significant chain")
for mech in sorted(df_chain_sig["mechanism"].unique()):
    sub = df_chain_sig[df_chain_sig["mechanism"] == mech]
    print(f"\n--- {mech} ---")
    for _, r in sub.iterrows():
        fs = "F+" if r["family_sig"] else "F-"
        ss = "S+" if r["species_sig"] else ("S-" if r["species"] else "S?")
        cs = "C+" if r["compound_sig"] else ("C-" if r["compound"] else "C?")
        print(f"  [{fs}{ss}{cs}] {r['chain_class']:<35s}  {r['family']:<22s} > {str(r['species']):<28s} > {str(r['compound'])}")

print("\n=== Block 3 COMPLETE ===")