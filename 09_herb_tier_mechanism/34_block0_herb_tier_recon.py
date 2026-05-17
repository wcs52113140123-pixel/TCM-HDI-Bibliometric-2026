"""
Day 15 Block 0 -- Herb tier x Mechanism RECON
=============================================
Discovery only. Goals:
1. Map Schema v3 herb-tier fields across LLM extraction parquets
2. Quantify per-field density (non-null, unique, top-20 entities)
3. Build coverage Venn (records by tier-combination presence)
4. Verify joinability with cluster_assignments (Day 13 N=9,413)
5. Pilot Fisher: top entity per tier x 16 mechanisms -- magnitude check

NO files written. NO commit. Output to console for decision-making.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import fisher_exact

REPO = Path(r"D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026")
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"
CLUSTERS = REPO / "data" / "processed" / "cluster_assignments.parquet"

# Tight substring patterns (avoid false positives)
HERB_TIER_PATTERNS = {
    "botanical":  ["family", "genus", "species", "latin", "binomial", "scientific_name", "plant_name"],
    "compound":   ["compound", "phytochem", "constituent", "ingredient", "flavonoid", "alkaloid", "saponin", "active_component"],
    "formula":    ["formula", "prescription", "decoction", "tcm_formula"],
    "herb_name":  ["herb_name", "common_name", "english_name", "chinese_name", "pinyin", "botanical_name", "herb"],
}

def section(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)

# ============================================================
# Section 1: Directory listing
# ============================================================
section("Section 1 -- LLM extraction directory contents")
if not LLM_DIR.exists():
    print(f"!! NOT FOUND: {LLM_DIR}")
    sys.exit(1)
for f in sorted(LLM_DIR.iterdir()):
    if f.is_file():
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:60s} ({size_kb:>10,.1f} KB)")

# ============================================================
# Section 2: Schema per parquet
# ============================================================
section("Section 2 -- Schema discovery (columns / dtype / non-null / unique)")
parquets = sorted(LLM_DIR.glob("*.parquet"))
schemas = {}
for p in parquets:
    try:
        df = pd.read_parquet(p)
        schemas[p.name] = df
        print(f"\n[{p.name}]  rows={len(df):,}  cols={len(df.columns)}")
        for col in df.columns:
            n_nn = df[col].notna().sum()
            try:
                n_uq = df[col].nunique(dropna=True)
            except Exception:
                n_uq = -1  # unhashable (list/dict)
            pct = 100 * n_nn / len(df) if len(df) else 0
            dt = str(df[col].dtype)
            uq_str = f"{n_uq:>6,}" if n_uq >= 0 else "  (lst?)"
            print(f"  - {col:35s} dtype={dt:15s}  nn={n_nn:>6,} ({pct:5.1f}%)  uq={uq_str}")
    except Exception as e:
        print(f"!! Failed to read {p.name}: {e}")

# Pick primary working parquet
PRIMARY = None
for n in schemas:
    if "normalized" in n.lower() and "interaction" in n.lower():
        PRIMARY = n; break
if PRIMARY is None and schemas:
    PRIMARY = list(schemas.keys())[0]
print(f"\n>> Primary parquet: {PRIMARY}")
df_p = schemas.get(PRIMARY)

# ============================================================
# Section 3: Herb-tier field detection
# ============================================================
section("Section 3 -- Herb-tier field detection (substring match per tier)")
herb_fields = {}  # parquet -> {tier: [cols]}
for pname, df in schemas.items():
    matches = {}
    for tier, pats in HERB_TIER_PATTERNS.items():
        m = [c for c in df.columns if any(pat in c.lower() for pat in pats)]
        if m:
            matches[tier] = m
    if matches:
        print(f"\n[{pname}]")
        for tier, cols in matches.items():
            print(f"  Tier '{tier:10s}': {cols}")
        herb_fields[pname] = matches
    else:
        print(f"\n[{pname}]  (no herb-tier fields matched)")

# ============================================================
# Section 4: Per-tier density on PRIMARY (top-20 entities)
# ============================================================
section("Section 4 -- Per-tier density (top-20 entities on PRIMARY parquet)")
tier_field_picks = {}
if df_p is not None and PRIMARY in herb_fields:
    for tier, cols in herb_fields[PRIMARY].items():
        for col in cols:
            print(f"\n[{tier}] field='{col}'")
            ser = df_p[col]
            n_nn = ser.notna().sum()
            print(f"  non-null: {n_nn:,} / {len(df_p):,}  ({100*n_nn/len(df_p):.1f}%)")
            # try scalar value_counts; fall back to explode for list-type
            try:
                top = ser.dropna().value_counts().head(20)
            except (TypeError, ValueError):
                top = ser.dropna().explode().value_counts().head(20)
            try:
                n_uq = ser.dropna().nunique()
            except Exception:
                n_uq = ser.dropna().explode().nunique()
            print(f"  unique:   {n_uq:,}")
            print("  top-20:")
            for ent, cnt in top.items():
                s = str(ent)[:55]
                print(f"    {s:<55s} {cnt:>6,}")
            # Pick FIRST field per tier as representative for downstream
            if tier not in tier_field_picks:
                tier_field_picks[tier] = col

# ============================================================
# Section 5: Coverage Venn (records by tier presence on PRIMARY)
# ============================================================
section("Section 5 -- Coverage Venn (records by tier-combination on PRIMARY)")
if df_p is not None and tier_field_picks:
    print(f"Tier-representative fields used:")
    for t, c in tier_field_picks.items():
        print(f"  {t:12s} -> {c}")
    # boolean presence per record per tier
    presence = pd.DataFrame(index=df_p.index)
    for t, c in tier_field_picks.items():
        ser = df_p[c]
        # treat empty string / empty list as null too
        def _present(v):
            if v is None: return False
            if isinstance(v, float) and np.isnan(v): return False
            if isinstance(v, (list, tuple, set)) and len(v) == 0: return False
            if isinstance(v, str) and v.strip() == "": return False
            return True
        presence[t] = ser.map(_present)
    presence["combo"] = presence[list(tier_field_picks)].apply(
        lambda r: "+".join([t for t in tier_field_picks if r[t]]) or "(none)", axis=1
    )
    counts = presence["combo"].value_counts()
    print("\nCoverage combinations:")
    for combo, cnt in counts.items():
        pct = 100 * cnt / len(df_p)
        print(f"  {combo:<55s} {cnt:>6,} ({pct:5.1f}%)")

# ============================================================
# Section 6: Inner join with cluster_assignments
# ============================================================
section("Section 6 -- Inner join with cluster_assignments (Day 13 N=9,413)")
if CLUSTERS.exists() and df_p is not None:
    df_c = pd.read_parquet(CLUSTERS)
    print(f"cluster_assignments: rows={len(df_c):,}, cols={list(df_c.columns)}")
    # Find common id-like columns
    common_ids = [c for c in df_p.columns if c in df_c.columns]
    print(f"Common columns: {common_ids}")
    join_key_cands = [c for c in common_ids if "id" in c.lower() or c.lower() in ("pmid","doi","uid")]
    print(f"Likely join keys: {join_key_cands}")
    if join_key_cands:
        key = join_key_cands[0]
        # join unique records on key (left side may have multi-mechanism rows)
        df_p_records = df_p[[key]].drop_duplicates()
        merged = df_p_records.merge(df_c[[key]].drop_duplicates() if key in df_c.columns else df_c, on=key, how="inner")
        print(f"Inner join on '{key}': {len(merged):,} unique records retained")
else:
    print("(cluster_assignments not found or primary missing)")

# ============================================================
# Section 7: Pilot Fisher per tier (top entity x 16 mechanisms)
# ============================================================
section("Section 7 -- Pilot Fisher: top-1 entity per tier x mechanism")
# Locate mechanism field
mech_field = None
for cand in ["mechanism", "mechanism_normalized", "mechanism_category", "mech"]:
    if df_p is not None and cand in df_p.columns:
        mech_field = cand; break
print(f"Mechanism field: {mech_field}")

if df_p is not None and mech_field and tier_field_picks:
    df_pi = df_p[~df_p[mech_field].astype(str).isin(["unspecified", "other", "None", "nan", ""])].copy()
    if "confidence" in df_pi.columns:
        df_pi = df_pi[df_pi["confidence"].astype(float) >= 0.7]
    print(f"Pilot subset (drop unspec/other + conf>=0.7): {len(df_pi):,}")
    mechanisms = sorted(df_pi[mech_field].dropna().unique().tolist())
    print(f"Mechanisms ({len(mechanisms)}): {mechanisms}")

    for tier, col in tier_field_picks.items():
        print(f"\n--- Tier '{tier}', field '{col}' ---")
        # top entity (handle list-type)
        try:
            vc = df_pi[col].dropna().value_counts()
        except (TypeError, ValueError):
            vc = df_pi[col].dropna().explode().value_counts()
        if len(vc) == 0:
            print("  no entities, skip")
            continue
        ent, n_ent = vc.index[0], vc.iloc[0]
        print(f"Top entity: '{ent}' (n_records={n_ent})")
        print(f"  {'mechanism':<32s}{'obs':>6s}{'exp':>10s}{'OR':>10s}{'p':>14s}")

        # entity-membership mask (handles list-type via .apply)
        def _has_ent(v, ent=ent):
            if v is None: return False
            if isinstance(v, (list, tuple, set)): return ent in v
            return v == ent
        mask_ent_full = df_pi[col].apply(_has_ent)
        N = len(df_pi)
        n_e = mask_ent_full.sum()
        for mech in mechanisms:
            mask_m = (df_pi[mech_field] == mech)
            a = (mask_ent_full & mask_m).sum()
            b = (mask_ent_full & ~mask_m).sum()
            c = (~mask_ent_full & mask_m).sum()
            d = (~mask_ent_full & ~mask_m).sum()
            if (a+b) == 0 or (c+d) == 0:
                continue
            exp = (a+b)*(a+c)/N if N else 0
            if a < 2 and exp < 1:
                continue
            try:
                OR, p = fisher_exact([[a,b],[c,d]], alternative="two-sided")
                marker = " *" if (p < 0.05 and OR > 2) else ("  " if p < 0.05 else "")
                print(f"  {mech:<32s}{a:>6}{exp:>10.2f}{OR:>10.2f}{p:>14.2e}{marker}")
            except Exception as e:
                print(f"  {mech:<32s} fisher fail: {e}")

print("\n=== Block 0 RECON COMPLETE ===")
print("Decision points for next step:")
print("  (a) Which tier(s) have density >= 30%? (proceed with those)")
print("  (b) Pilot Fisher OR magnitude: >5? >10? (vs Day 13's OR=505 for UGT)")
print("  (c) Are tier fields list-type or scalar? (affects analysis design)")
print("  (d) Cross-tier overlap from Venn: do same records carry multiple tiers?")