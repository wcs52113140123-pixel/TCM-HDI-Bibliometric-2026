"""
Day 7 LLM extraction results parser.

Reads `*.results.jsonl` (and optionally `*.failed.jsonl`) and produces two
parquet tables:
  - {prefix}_{model}.records.parquet       — one row per abstract
  - {prefix}_{model}.interactions.parquet  — one row per extracted interaction
                                              (long table, ready for KG / SQL)

Also prints quick QC stats: total counts, mechanism distribution,
evidence-type distribution, top herbs / drugs, confidence summary.

Usage:
    python 05_llm_extraction/10_parse_results.py
        [--model openai/gpt-4o-mini]
        [--prefix primary]    # 'primary' or 'secondary' (cross-validation)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"


# ----------------------------------------------------------------------
def parse_jsonl(path: Path) -> tuple[list[dict], list[dict]]:
    """Return (record_rows, interaction_rows) lists."""
    record_rows: list[dict] = []
    interaction_rows: list[dict] = []
    if not path.exists():
        return record_rows, interaction_rows

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            extraction = r.get("extraction") or {}

            record_rows.append({
                "record_id": r.get("record_id"),
                "year": r.get("year"),
                "cluster_id": r.get("cluster_id"),
                "ok": bool(r.get("ok")),
                "contains_hdi": extraction.get("contains_hdi"),
                "n_interactions": len(extraction.get("interactions") or []),
                "tier_used": r.get("tier_used"),
                "n_attempts": r.get("n_attempts"),
                "validation_failures": r.get("validation_failures"),
                "input_tokens": r.get("input_tokens"),
                "output_tokens": r.get("output_tokens"),
                "elapsed_s": r.get("elapsed_s"),
                "extraction_notes": extraction.get("extraction_notes"),
                "error": r.get("error"),
            })

            for idx, iv in enumerate(extraction.get("interactions") or []):
                interaction_rows.append({
                    "record_id": r.get("record_id"),
                    "year": r.get("year"),
                    "cluster_id": r.get("cluster_id"),
                    "interaction_idx": idx,
                    # A: core
                    "herb_name_latin": iv.get("herb_name_latin"),
                    "herb_common_name": iv.get("herb_common_name"),
                    "herb_active_compound": iv.get("herb_active_compound"),
                    "drug_name": iv.get("drug_name"),
                    "drug_class": iv.get("drug_class"),
                    "interaction_type": iv.get("interaction_type"),
                    "mechanism": iv.get("mechanism"),
                    "specific_target": iv.get("specific_target"),
                    "direction": iv.get("direction"),
                    # B: TCM formula
                    "tcm_formula_name": iv.get("tcm_formula_name"),
                    # store list[str] as pipe-delimited string for parquet portability
                    "co_herbs": "|".join(iv.get("co_herbs") or []),
                    "tcm_pattern": iv.get("tcm_pattern"),
                    # C: clinical quantitative
                    "auc_change_pct": iv.get("auc_change_pct"),
                    "cmax_change_pct": iv.get("cmax_change_pct"),
                    "half_life_change_pct": iv.get("half_life_change_pct"),
                    "cl_change_pct": iv.get("cl_change_pct"),
                    "sample_size": iv.get("sample_size"),
                    # metadata
                    "evidence_type": iv.get("evidence_type"),
                    "clinical_significance": iv.get("clinical_significance"),
                    "confidence": iv.get("confidence"),
                    "evidence_quote": iv.get("evidence_quote"),
                })

    return record_rows, interaction_rows


# ----------------------------------------------------------------------
def print_summary(records_df: pd.DataFrame, interactions_df: pd.DataFrame) -> None:
    n_total = len(records_df)
    n_ok = int(records_df["ok"].sum()) if "ok" in records_df else 0
    n_hdi = int((records_df["contains_hdi"] == True).sum()) if "contains_hdi" in records_df else 0
    n_int = len(interactions_df)

    print(f"\n{'='*72}\n  EXTRACTION SUMMARY\n{'='*72}")
    print(f"  Records:                        {n_total:>7,}")
    print(f"  Successful extractions:         {n_ok:>7,} ({n_ok/n_total*100:.1f}%)")
    print(f"  Records flagged contains_hdi:   {n_hdi:>7,} ({n_hdi/n_total*100:.1f}%)")
    print(f"  Total interactions extracted:   {n_int:>7,}")
    if n_hdi > 0:
        print(f"  Avg interactions / HDI record:  {n_int/n_hdi:>7.2f}")

    if "tier_used" in records_df:
        print(f"\n  Tier distribution (which response_format mode worked):")
        for tier, n in records_df["tier_used"].value_counts(dropna=False).sort_index().items():
            label = {1: "T1 json_schema (strict)", 2: "T2 json_object (loose)",
                     3: "T3 prompt-only"}.get(tier, f"Tier {tier} (None=failed)")
            print(f"    {label:35s} {n:>6,}")

    if n_int == 0:
        return

    # Mechanism distribution
    print(f"\n  Mechanism distribution (top 12):")
    for mech, n in interactions_df["mechanism"].value_counts().head(12).items():
        print(f"    {(mech or '(null)'):35s} {n:>5,} ({n/n_int*100:.1f}%)")

    # Evidence type
    print(f"\n  Evidence type distribution:")
    for et, n in interactions_df["evidence_type"].value_counts().items():
        print(f"    {(et or '(null)'):25s} {n:>5,} ({n/n_int*100:.1f}%)")

    # Direction distribution
    print(f"\n  Direction distribution:")
    for d, n in interactions_df["direction"].value_counts().items():
        print(f"    {(d or '(null)'):28s} {n:>5,}")

    # Clinical significance
    print(f"\n  Clinical significance:")
    for cs, n in interactions_df["clinical_significance"].value_counts().items():
        print(f"    {(cs or '(null)'):20s} {n:>5,}")

    # Top herbs (best-effort fallback chain: common → latin → compound)
    herb = (
        interactions_df["herb_common_name"]
        .fillna(interactions_df["herb_name_latin"])
        .fillna(interactions_df["herb_active_compound"])
        .fillna("(unknown)")
        .astype(str).str.lower().str.strip()
    )
    print(f"\n  Top 20 herbs (by interaction count, pre-normalization):")
    for h, n in herb.value_counts().head(20).items():
        print(f"    {h[:50]:50s} {n:>5,}")

    # Top drugs
    drug = interactions_df["drug_name"].fillna("(unknown)").astype(str).str.lower().str.strip()
    print(f"\n  Top 20 drugs (by interaction count, pre-normalization):")
    for d, n in drug.value_counts().head(20).items():
        print(f"    {d[:50]:50s} {n:>5,}")

    # Specific targets
    if interactions_df["specific_target"].notna().any():
        print(f"\n  Top 15 specific targets:")
        targets = interactions_df["specific_target"].dropna().astype(str).str.strip()
        for t, n in targets.value_counts().head(15).items():
            print(f"    {t[:30]:30s} {n:>5,}")

    # Confidence
    conf = interactions_df["confidence"].dropna()
    print(f"\n  Confidence statistics (n={len(conf)}):")
    print(f"    mean   = {conf.mean():.3f}")
    print(f"    median = {conf.median():.3f}")
    print(f"    std    = {conf.std():.3f}")
    print(f"    < 0.6  = {int((conf < 0.6).sum()):,} interactions ({int((conf < 0.6).sum())/len(conf)*100:.1f}%)")
    print(f"    ≥ 0.9  = {int((conf >= 0.9).sum()):,} interactions ({int((conf >= 0.9).sum())/len(conf)*100:.1f}%)")

    # Quantitative coverage
    print(f"\n  Quantitative field coverage (% of interactions with non-null):")
    for col in ["auc_change_pct", "cmax_change_pct", "half_life_change_pct",
                "cl_change_pct", "sample_size"]:
        pct = interactions_df[col].notna().sum() / len(interactions_df) * 100
        print(f"    {col:25s} {pct:>5.1f}%")

    # TCM-specific
    print(f"\n  TCM formula coverage:")
    n_formula = interactions_df["tcm_formula_name"].notna().sum()
    n_coherb = (interactions_df["co_herbs"] != "").sum()
    n_pattern = interactions_df["tcm_pattern"].notna().sum()
    print(f"    With tcm_formula_name: {n_formula:>5,} ({n_formula/n_int*100:.1f}%)")
    print(f"    With co_herbs:         {n_coherb:>5,} ({n_coherb/n_int*100:.1f}%)")
    print(f"    With tcm_pattern:      {n_pattern:>5,} ({n_pattern/n_int*100:.1f}%)")


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary",
                    help="'primary' (main extraction) or 'secondary' (cross-validation)")
    args = ap.parse_args()

    model_safe = args.model.replace("/", "__").replace(".", "_")
    results_jsonl = LLM_DIR / f"{args.prefix}_{model_safe}.results.jsonl"
    failed_jsonl = LLM_DIR / f"{args.prefix}_{model_safe}.failed.jsonl"

    records_out = LLM_DIR / f"{args.prefix}_{model_safe}.records.parquet"
    interactions_out = LLM_DIR / f"{args.prefix}_{model_safe}.interactions.parquet"

    print(f"{'='*72}\n  Parse LLM extraction results\n{'='*72}")
    print(f"  Model:   {args.model}")
    print(f"  Prefix:  {args.prefix}")
    print(f"  Results JSONL:  {results_jsonl.relative_to(REPO)}")
    if failed_jsonl.exists():
        print(f"  Failed JSONL:   {failed_jsonl.relative_to(REPO)}")

    if not results_jsonl.exists():
        print(f"\nFATAL: {results_jsonl.relative_to(REPO)} not found.")
        return

    rec_rows, int_rows = parse_jsonl(results_jsonl)
    print(f"\n  Loaded from results.jsonl:  {len(rec_rows):,} records, {len(int_rows):,} interactions")

    # Merge in failed records (no interactions, but record-level info preserved)
    if failed_jsonl.exists():
        f_rec, _ = parse_jsonl(failed_jsonl)
        for r in f_rec:
            r["ok"] = False
        rec_rows.extend(f_rec)
        print(f"  Loaded from failed.jsonl:   {len(f_rec):,} failed records")

    records_df = pd.DataFrame(rec_rows)
    interactions_df = pd.DataFrame(int_rows)

    # De-duplicate records (if user re-ran and same record appears twice in JSONL,
    # keep the latest = highest n_interactions or last seen)
    if "record_id" in records_df:
        n_before = len(records_df)
        records_df = records_df.drop_duplicates(subset="record_id", keep="last")
        n_dup = n_before - len(records_df)
        if n_dup:
            print(f"  De-duplicated records (kept latest): -{n_dup:,}")

    records_df.to_parquet(records_out, index=False)
    interactions_df.to_parquet(interactions_out, index=False)
    print(f"\n  → {records_out.relative_to(REPO)}      ({len(records_df):,} rows)")
    print(f"  → {interactions_out.relative_to(REPO)} ({len(interactions_df):,} rows)")

    print_summary(records_df, interactions_df)


if __name__ == "__main__":
    main()
