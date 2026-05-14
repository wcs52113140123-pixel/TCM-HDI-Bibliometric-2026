"""
Stage 4: OpenAlex client-side precision filter (B1).

Applies WoS-equivalent 3-block logic to records that ONLY come from OpenAlex
(not cross-validated by WoS/Scopus/PubMed).

Block 1 (direct HDI phrases) | Block 2 (TCM × interaction) | Block 3 (TCM × CYP/transporter)
ANY match -> keep. None -> drop.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

import pandas as pd

DIRECT_HDI = [
    "herb-drug interaction", "herb drug interaction",
    "herbal drug interaction", "herbal-drug interaction",
    "tcm-drug interaction", "tcm drug interaction",
    "phytochemical drug interaction", "phytochemical-drug interaction",
]

TCM_TERMS = [
    "traditional chinese medicine", "chinese herbal medicine",
    "chinese herbal", "chinese medicine",
]

TCM_ACRONYM = [" tcm ", " tcm.", " tcm,", "(tcm)", "[tcm]", "tcm-"]

INTERACTION_TERMS = [
    "drug interaction", "drug-drug interaction",
    "pharmacokinetic interaction", "pharmacodynamic interaction",
    "drug interactions",
]

CYP_TERMS = [
    "cyp3a4", "cyp2d6", "cyp1a2", "cyp2c9", "cyp2c19",
    "cytochrome p450", "cytochrome p-450", "cytochrome p 450",
    "p-glycoprotein", "p glycoprotein", "p-gp", "p gp",
    "drug metabolism", "drug-metabolizing",
    "drug transporter", "drug transporters", "drug efflux",
    "udp-glucuronosyltransferase", "ugt enzyme",
]


def contains_any(text, terms):
    return any(t in text for t in terms)


def tcm_present(text):
    return contains_any(text, TCM_TERMS) or contains_any(text, TCM_ACRONYM)


def evaluate_relevance(row):
    """Return (is_relevant: bool, matched_block: str)."""
    parts = [row.get("title") or "", row.get("abstract") or ""]
    
    keywords = row.get("author_keywords")
    if keywords is not None:
        if hasattr(keywords, "__iter__") and not isinstance(keywords, str):
            parts.append(" ".join(str(k) for k in keywords))
    
    concepts = row.get("openalex_concepts")
    if concepts is not None:
        if hasattr(concepts, "__iter__") and not isinstance(concepts, str):
            parts.append(" ".join(str(c) for c in concepts))
    
    text = " ".join(parts).lower()
    
    if contains_any(text, DIRECT_HDI):
        return (True, "B1_direct")
    if tcm_present(text) and contains_any(text, INTERACTION_TERMS):
        return (True, "B2_tcm_interaction")
    if tcm_present(text) and contains_any(text, CYP_TERMS):
        return (True, "B3_tcm_cyp")
    return (False, "B0_none")


def is_openalex_exclusive(db_list):
    """
    Robust check: db_list may be a Python list, numpy array, or pandas object.
    OpenAlex exclusive means: contains exactly one element == "OpenAlex".
    """
    if db_list is None:
        return False
    try:
        items = list(db_list)  # coerce to Python list
    except TypeError:
        return False
    if len(items) != 1:
        return False
    return str(items[0]) == "OpenAlex"


def main(partial_2026=False):
    repo_root = Path(__file__).resolve().parent.parent
    in_dir = repo_root / "data" / "processed"
    suffix = "_partial2026" if partial_2026 else ""
    
    label = "PARTIAL 2026" if partial_2026 else "MAIN 2005-2025"
    print(f"\n{'='*70}")
    print(f"Stage 4: OpenAlex client-side precision filter (B1) ({label})")
    print(f"{'='*70}\n")
    
    in_path = in_dir / f"stage3_fuzzy_deduplicated{suffix}.parquet"
    print(f"[1] Loading: {in_path.name}")
    df = pd.read_parquet(in_path)
    print(f"    -> {len(df):,} records")
    
    # Identify OpenAlex-exclusive (robust to parquet ndarray vs list)
    is_oa_excl_series = df["source_db_list"].apply(is_openalex_exclusive)
    n_oa_excl = int(is_oa_excl_series.sum())
    
    print(f"\n[2] Identifying OpenAlex-exclusive records:")
    print(f"    OpenAlex exclusive (subject to filter): {n_oa_excl:,}")
    print(f"    Cross-validated (auto-pass):            {len(df) - n_oa_excl:,}")
    
    # Sanity check: if 0, debug source_db_list type
    if n_oa_excl == 0:
        print(f"\n    WARNING: 0 OpenAlex exclusives detected. Debugging type:")
        sample = df["source_db_list"].iloc[0]
        print(f"    First row source_db_list: {repr(sample)} (type: {type(sample).__name__})")
        # Show all distinct singleton values
        from collections import Counter
        c = Counter()
        for val in df["source_db_list"]:
            try:
                items = list(val) if val is not None else []
                if len(items) == 1:
                    c[str(items[0])] += 1
            except TypeError:
                pass
        print(f"    Distinct singletons: {dict(c)}")
        if not c.get("OpenAlex", 0):
            print(f"    No OpenAlex singletons found. Filter is a no-op; skipping to save.")
    
    # Apply filter ONLY to OpenAlex-exclusive
    df = df.copy()
    df["_is_oa_excl"] = is_oa_excl_series.values
    
    if n_oa_excl > 0:
        print(f"\n[3] Applying WoS-equivalent 3-block logic to OpenAlex exclusives...")
        oa_excl_mask = df["_is_oa_excl"]
        # CRITICAL FIX: use result_type='expand' to get a DataFrame, then assign columns separately
        results = df.loc[oa_excl_mask].apply(evaluate_relevance, axis=1)
        # results is a Series of tuples; unpack manually
        df.loc[oa_excl_mask, "_is_relevant"] = results.apply(lambda x: x[0]).values
        df.loc[oa_excl_mask, "_matched_block"] = results.apply(lambda x: x[1]).values
        
        # For non-OA-exclusive, force is_relevant=True (auto-pass)
        df.loc[~oa_excl_mask, "_is_relevant"] = True
        df.loc[~oa_excl_mask, "_matched_block"] = "auto_pass"
        
        # Block breakdown for OA exclusives
        oa_blocks = df.loc[oa_excl_mask, "_matched_block"].value_counts()
        print(f"\n[4] OpenAlex-exclusive: which block matched?")
        for block in ["B1_direct", "B2_tcm_interaction", "B3_tcm_cyp", "B0_none"]:
            n = int(oa_blocks.get(block, 0))
            marker = "PASS" if block != "B0_none" else "FAIL"
            print(f"    {block:25s}: {n:>5,}  [{marker}]")
        
        n_oa_pass = int((df["_is_oa_excl"] & df["_is_relevant"]).sum())
        n_oa_fail = int((df["_is_oa_excl"] & ~df["_is_relevant"]).sum())
        print(f"\n    PASS (kept):  {n_oa_pass:,} ({100*n_oa_pass/n_oa_excl:.1f}%)")
        print(f"    FAIL (drop):  {n_oa_fail:,} ({100*n_oa_fail/n_oa_excl:.1f}%)")
    else:
        df["_is_relevant"] = True
        df["_matched_block"] = "auto_pass"
        n_oa_pass, n_oa_fail = 0, 0
        oa_blocks = pd.Series()
    
    # Build outputs
    df_dropped = df[df["_is_oa_excl"] & ~df["_is_relevant"]].copy()
    df_final = df[df["_is_relevant"]].drop(
        columns=["_is_oa_excl", "_is_relevant", "_matched_block"]
    ).reset_index(drop=True)
    
    print(f"\n[5] Stage 4 results:")
    print(f"    Stage 3 input:                       {len(df):,}")
    print(f"    OpenAlex exclusives dropped:          {n_oa_fail:,}")
    print(f"    TOTAL Stage 4 (quality-filtered):     {len(df_final):,}")
    print(f"    Reduction from Stage 3:              {len(df) - len(df_final):,} "
          f"({100*(len(df)-len(df_final))/max(len(df),1):.2f}%)")
    
    # Save
    out_parquet = in_dir / f"stage4_quality_filtered{suffix}.parquet"
    out_audit = in_dir / f"stage4_openalex_filter_audit{suffix}.csv"
    out_summary = in_dir / f"stage4_summary{suffix}.json"
    
    print(f"\n[6] Saving outputs...")
    df_final.to_parquet(out_parquet, index=False, engine="pyarrow")
    print(f"    {out_parquet.name} ({out_parquet.stat().st_size/1024/1024:.1f} MB)")
    
    if len(df_dropped) > 0:
        audit_cols = ["record_id", "title", "year", "first_author_lastname",
                      "_matched_block", "openalex_concepts"]
        # Keep only columns that exist
        audit_cols = [c for c in audit_cols if c in df_dropped.columns]
        df_dropped[audit_cols].to_csv(out_audit, index=False, encoding="utf-8")
    else:
        pd.DataFrame().to_csv(out_audit, index=False, encoding="utf-8")
    print(f"    {out_audit.name} ({out_audit.stat().st_size/1024:.1f} KB)")
    
    summary = {
        "label": label,
        "generated_at": datetime.now().isoformat(),
        "stage3_input": len(df),
        "openalex_exclusive_count": n_oa_excl,
        "openalex_exclusive_passed": n_oa_pass,
        "openalex_exclusive_dropped": n_oa_fail,
        "stage4_output": len(df_final),
        "block_breakdown": {k: int(v) for k, v in oa_blocks.items()} if len(oa_blocks) > 0 else {},
    }
    with open(out_summary, "w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2, ensure_ascii=False, default=str)
    print(f"    {out_summary.name}")
    
    print(f"\n{'='*70}")
    print(f"DONE: {len(df):,} -> {len(df_final):,} records")
    print(f"{'='*70}")
    
    return df_final


if __name__ == "__main__":
    partial = "--partial-2026" in sys.argv
    main(partial_2026=partial)
