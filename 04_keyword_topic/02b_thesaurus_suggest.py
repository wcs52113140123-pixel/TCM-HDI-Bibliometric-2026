"""
Day 4 Block 2.2 (v3 - clean): Build thesaurus with strict transitive closure.

Algorithm:
1. Start with KNOWN_VARIANTS as the canonical mappings (manually curated)
2. Use fuzzy matching to FIND ADDITIONAL variants, but ALL must point to
   final canonical (transitive closure)
3. Final output: ONE row per variant. Variant != canonical. No duplicates.
"""

import re
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process


STOPWORD_SEEDS = {
    "humans", "human", "animals", "animal", "male", "female",
    "rats", "rat", "mice", "mouse", "rabbits", "rabbit",
    "in vitro", "in vivo",
    "adult", "aged", "middle aged", "young adult", "child",
    "expression", "metabolism", "chemistry",
    "drug effect", "drug effects", "biology",
    "review",
}


# KNOWN_VARIANTS: each entry maps variant -> CANONICAL (preferred form)
# IMPORTANT: canonical is the LINGUISTICALLY preferred form (singular, no hyphen variants)
KNOWN_VARIANTS = {
    # === Herb-drug interaction family ===
    "herb-drug interactions": "herb-drug interaction",  # plural -> singular
    "herb drug interaction": "herb-drug interaction",
    "herb drug interactions": "herb-drug interaction",
    
    # === Drug interaction family ===
    "drug interactions": "drug interaction",
    "drug-interactions": "drug interaction",
    "drug-interaction": "drug interaction",
    
    # === Drug-drug interaction family ===
    "drug-drug interactions": "drug-drug interaction",
    "drug drug interaction": "drug-drug interaction",
    
    # === TCM family (collapse everything) ===
    "drugs, chinese herbal": "traditional chinese medicine",
    "herbal medicine": "traditional chinese medicine",
    "herbal medicines": "traditional chinese medicine",
    "chinese medicine": "traditional chinese medicine",
    "chinese herbal medicine": "traditional chinese medicine",
    "medicine, chinese traditional": "traditional chinese medicine",
    "tcm": "traditional chinese medicine",
    
    # === Plant extract family ===
    "plant extracts": "plant extract",
    "plants, medicinal": "medicinal plants",
    
    # === CYP family ===
    "cyp": "cytochrome p450",
    "cyp450": "cytochrome p450",
    "cytochrome p-450": "cytochrome p450",
    "cytochrome-p450": "cytochrome p450",
    "cytochrome p 450": "cytochrome p450",
    "p450": "cytochrome p450",
    # CYP3A4 specifically is KEPT as is — it's a distinct subfamily isoform
    # Do NOT merge cyp3a4 into cytochrome p450
    
    # === P-glycoprotein family ===
    "p-gp": "p-glycoprotein",
    "pgp": "p-glycoprotein",
    "p glycoprotein": "p-glycoprotein",
    
    # === Hyperycum family ===
    "st-john's-wort": "st johns wort",
    "st-johns-wort": "st johns wort",
    "st johns-wort": "st johns wort",
    "hypericum perforatum": "st johns wort",
    
    # === In vitro/vivo (these are stopwords later, but normalize first) ===
    "in-vitro": "in vitro",
    "in-vivo": "in vivo",
    
    # === Standardization variants ===
    "pharmacokinetic": "pharmacokinetics",
    "mechanisms": "mechanism",
    "antioxidants": "antioxidant",
    "extracts": "extract",
    "medicines": "medicine",
    "drugs": "drug",
    "interactions": "interaction",  # caution - very generic
    "dietary-supplements": "dietary supplements",
    "multidrug-resistance": "multidrug resistance",
    "metabolites": "metabolite",
    "transporters": "transporter",
}


# Semantic blacklist: pairs that LOOK similar but mean different things
SEMANTIC_BLACKLIST = {
    ("expression", "depression"),
    ("depression", "expression"),
    ("lc-ms/ms", "uplc-ms/ms"),
    ("uplc-ms/ms", "lc-ms/ms"),
    ("hplc-ms", "lc-ms"),
    ("lc-ms", "hplc-ms"),
    ("cyp3a", "cyp3a4"),     # different subfamily
    ("cyp3a4", "cytochrome p450"),  # don't collapse isoform into parent
    ("cytochrome p450", "cyp3a4"),
    ("transporter", "transport"),  # different concepts
    ("transport", "transporter"),
}


def resolve_canonical(s, known_map):
    """Walk through KNOWN_VARIANTS to find final canonical (transitive)."""
    visited = set()
    while s in known_map and s not in visited:
        visited.add(s)
        s = known_map[s]
    return s


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 2.2 (v3 clean): Build thesaurus with strict transitive closure")
    print("=" * 70)
    
    # Load inventory
    print("\n[1] Loading keyword inventory...")
    inv = pd.read_csv(repo_root / "data/processed/keyword_inventory.csv")
    inv = inv[["normalized", "total"]].copy()
    print(f"    Total unique keywords: {len(inv):,}")
    
    count_lookup = dict(zip(inv["normalized"], inv["total"].astype(int)))
    top500 = inv.nlargest(500, "total")["normalized"].tolist()
    top1500 = inv.nlargest(1500, "total")["normalized"].tolist()
    
    # ============ Stopwords ============
    print("\n[2] Identifying stopword candidates...")
    stopword_rows = []
    for kw in top500:
        if kw in STOPWORD_SEEDS:
            stopword_rows.append({
                "keyword": kw,
                "n_records": count_lookup.get(kw, 0),
                "decision": "DROP",
            })
    stopword_df = pd.DataFrame(stopword_rows).sort_values("n_records", ascending=False)
    sw_path = repo_root / "data/processed/stopwords_suggestions.csv"
    stopword_df.to_csv(sw_path, index=False, encoding="utf-8")
    print(f"    Stopword candidates: {len(stopword_df)}")
    
    # ============ Build final thesaurus ============
    print("\n[3] Building final thesaurus with transitive closure...")
    
    # Start with KNOWN_VARIANTS (manual mappings)
    final_map = {}  # variant -> canonical (after resolution)
    
    for variant in KNOWN_VARIANTS:
        if variant not in count_lookup:
            continue
        canonical = resolve_canonical(variant, KNOWN_VARIANTS)
        if canonical in count_lookup and canonical != variant:
            final_map[variant] = canonical
    
    print(f"    KNOWN_VARIANTS resolved: {len(final_map)} variants")
    
    # ============ Fuzzy fill: find NEW variants not in KNOWN_VARIANTS ============
    print("\n[4] Adding fuzzy-detected variants...")
    
    for base_kw in top500:
        if base_kw in STOPWORD_SEEDS:
            continue
        if base_kw in final_map:
            continue  # already mapped to a canonical
        
        matches = process.extract(
            base_kw, top1500,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=88,
            limit=10,
        )
        for match_kw, score, _ in matches:
            if match_kw == base_kw:
                continue
            if match_kw in STOPWORD_SEEDS:
                continue
            # Skip semantic blacklist (both directions)
            if (base_kw, match_kw) in SEMANTIC_BLACKLIST:
                continue
            if (match_kw, base_kw) in SEMANTIC_BLACKLIST:
                continue
            
            base_n = count_lookup.get(base_kw, 0)
            match_n = count_lookup.get(match_kw, 0)
            
            # Canonical = the one with HIGHER count (or already in final_map's value side)
            if match_n > base_n:
                # base_kw -> match_kw
                if base_kw not in final_map:
                    final_map[base_kw] = resolve_canonical(match_kw, final_map)
            elif base_n > match_n:
                # match_kw -> base_kw, but only if match_kw doesn't have a canonical yet
                if match_kw not in final_map and match_kw not in final_map.values():
                    final_map[match_kw] = resolve_canonical(base_kw, final_map)
            # tie: skip (no clear canonical)
    
    print(f"    Total variants in thesaurus: {len(final_map)}")
    
    # ============ Apply transitive closure on final_map itself ============
    print("\n[5] Final transitive closure pass...")
    closed_map = {}
    for variant, canonical in final_map.items():
        closed_map[variant] = resolve_canonical(canonical, final_map)
    final_map = closed_map
    
    # Remove self-loops
    final_map = {v: c for v, c in final_map.items() if v != c}
    
    print(f"    After closure: {len(final_map)} variants (each pointing to canonical)")
    
    # ============ Build output dataframe ============
    rows = []
    for variant, canonical in final_map.items():
        rows.append({
            "variant": variant,
            "canonical": canonical,
            "variant_n": count_lookup.get(variant, 0),
            "canonical_n": count_lookup.get(canonical, 0),
            "decision": "MERGE",
            "note": "KNOWN" if variant in KNOWN_VARIANTS else "fuzzy",
        })
    
    pairs_df = pd.DataFrame(rows).sort_values("variant_n", ascending=False).reset_index(drop=True)
    
    print(f"\n[6] Final thesaurus: {len(pairs_df)} unique (variant -> canonical) pairs")
    print(f"\n    Top 30 by variant impact:")
    print(f"    {'Note':<6} {'CanonN':>7} {'VarN':>5}  Variant  =>  Canonical")
    print(f"    {'-'*5:<6} {'-'*7:>7} {'-'*5:>5}  {'-'*40}")
    for _, row in pairs_df.head(30).iterrows():
        print(f"    {row['note']:<6} {row['canonical_n']:>7} {row['variant_n']:>5}  "
              f"{row['variant']:30s} => {row['canonical']}")
    
    # Verify no duplicates / no self-loops
    n_self_loops = (pairs_df["variant"] == pairs_df["canonical"]).sum()
    n_duplicate_variants = pairs_df["variant"].duplicated().sum()
    print(f"\n[7] Sanity check:")
    print(f"    Self-loops:         {n_self_loops}  (must be 0)")
    print(f"    Duplicate variants: {n_duplicate_variants}  (must be 0)")
    
    # Save
    ths_path = repo_root / "data/processed/thesaurus_suggestions.csv"
    pairs_df.to_csv(ths_path, index=False, encoding="utf-8")
    print(f"\n[8] Saved: {ths_path}")
    
    print("\n" + "=" * 70)
    print(f"REVIEW: {ths_path}")
    print(f"        {sw_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
