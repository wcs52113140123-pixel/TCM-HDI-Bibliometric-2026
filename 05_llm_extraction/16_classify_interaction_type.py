"""
Day 9 T4: Classify interactions by completeness for network analysis.

For each interaction, classifies based on which axes (drug / target / mechanism)
are known. This determines how the interaction can be used in Day 10+ network
analysis: as a 3-axis triple, a 2-axis edge, or as exploratory metadata.

Approach:
  drug_known     = drug_name not in {null, unknown, (unknown), ""}
  target_known   = target_canonical (from T1) is not null
  mech_specific  = mechanism not in {other, unspecified, null}

Interaction class:
  - "complete"            : drug + target both known (gold standard)
  - "herb_drug_no_target" : drug known but target null (PK study without
                             mechanism characterization in abstract)
  - "herb_target_no_drug" : target known but drug unknown (herb-target
                             mechanistic claim, e.g. "herb induces CYP3A4")
  - "fragmentary"         : neither drug nor target known (low information)

Output: adds 4 columns to interactions_normalized.parquet:
  - drug_known          : bool
  - target_known        : bool
  - mech_specific       : bool
  - interaction_class   : one of {complete, herb_drug_no_target, herb_target_no_drug, fragmentary}

Usage:
    python 05_llm_extraction/16_classify_interaction_type.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"

# Strings that should be treated as drug="unknown" (case-insensitive)
_UNKNOWN_DRUG_TOKENS = {
    "(unknown)", "unknown", "null", "none", "n/a", "na", "not specified",
    "not reported", "various drugs", "various", "unspecified drug", "",
}

# Mechanism categories that count as "specific mechanism known"
# (everything EXCEPT other / unspecified)
_NONSPECIFIC_MECH = {"other", "unspecified", None}


def is_drug_known(drug_name) -> bool:
    if pd.isna(drug_name):
        return False
    s = str(drug_name).strip().lower()
    return s not in _UNKNOWN_DRUG_TOKENS


def is_mech_specific(mechanism) -> bool:
    if pd.isna(mechanism):
        return False
    return mechanism not in _NONSPECIFIC_MECH


def classify(drug_known: bool, target_known: bool) -> str:
    """Classify based on drug × target availability."""
    if drug_known and target_known:
        return "complete"
    if drug_known and not target_known:
        return "herb_drug_no_target"
    if not drug_known and target_known:
        return "herb_target_no_drug"
    return "fragmentary"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary")
    args = ap.parse_args()

    safe = args.model.replace("/", "__").replace(".", "_")
    in_path = LLM_DIR / f"{args.prefix}_{safe}.interactions_normalized.parquet"
    if not in_path.exists():
        print(f"FATAL: {in_path.relative_to(REPO)} not found")
        print("Run 15_normalize_targets.py first.")
        return

    df = pd.read_parquet(in_path)
    n = len(df)
    print(f"{'='*72}\n  Day 9 T4: Classify interaction completeness\n{'='*72}")
    print(f"  Input:  {in_path.relative_to(REPO)} ({n:,} rows)")

    # Apply classification
    df["drug_known"] = df["drug_name"].apply(is_drug_known)
    df["target_known"] = df["target_canonical"].notna()
    df["mech_specific"] = df["mechanism"].apply(is_mech_specific)
    df["interaction_class"] = df.apply(
        lambda r: classify(r["drug_known"], r["target_known"]), axis=1
    )

    # Write back to same path (overwrite)
    df.to_parquet(in_path, index=False)
    print(f"  Output (same file, +4 columns): {in_path.relative_to(REPO)}")

    # ---- Summary ----
    print(f"\n  Boolean flags (across all {n:,} interactions):")
    print(f"    drug_known:    {int(df['drug_known'].sum()):>5,} "
          f"({df['drug_known'].mean()*100:.1f}%)")
    print(f"    target_known:  {int(df['target_known'].sum()):>5,} "
          f"({df['target_known'].mean()*100:.1f}%)")
    print(f"    mech_specific: {int(df['mech_specific'].sum()):>5,} "
          f"({df['mech_specific'].mean()*100:.1f}%)")

    print(f"\n  interaction_class distribution:")
    cls_counts = df["interaction_class"].value_counts()
    for cls, cnt in cls_counts.items():
        pct = cnt / n * 100
        bar = "█" * int(pct / 2)
        print(f"    {cls:24s} {cnt:>5,} ({pct:>5.1f}%) {bar}")

    # ---- Detailed cross-tabs ----
    print(f"\n  interaction_class × mech_specific cross-tab:")
    crosstab = pd.crosstab(df["interaction_class"], df["mech_specific"],
                            margins=True, margins_name="TOTAL")
    print(crosstab.to_string())

    print(f"\n  Top mechanisms per interaction_class:")
    for cls in ["complete", "herb_drug_no_target", "herb_target_no_drug", "fragmentary"]:
        sub = df[df["interaction_class"] == cls]
        if len(sub) == 0:
            continue
        top_mech = sub["mechanism"].value_counts().head(5)
        print(f"\n    {cls} (n={len(sub):,}):")
        for m, c in top_mech.items():
            print(f"      {m:30s} {c:>4,}")

    # ---- Network-analysis-ready stats ----
    print(f"\n  Network analysis usability:")
    n_complete = (df["interaction_class"] == "complete").sum()
    n_3axis = ((df["interaction_class"] == "complete") & df["mech_specific"]).sum()
    n_2axis_herb_drug = (df["interaction_class"] == "herb_drug_no_target").sum()
    n_2axis_herb_target = (df["interaction_class"] == "herb_target_no_drug").sum()
    n_fragment = (df["interaction_class"] == "fragmentary").sum()
    print(f"    3-axis triples ready (drug+target+mech_specific): {n_3axis:>5,} "
          f"({n_3axis/n*100:.1f}%) → core network nodes")
    print(f"    2-axis herb-drug edges (drug+mech_specific, no target): "
          f"{n_2axis_herb_drug:>5,} ({n_2axis_herb_drug/n*100:.1f}%) → "
          f"PK-effect edges")
    print(f"    2-axis herb-target edges (target+mech_specific, no drug): "
          f"{n_2axis_herb_target:>5,} ({n_2axis_herb_target/n*100:.1f}%) → "
          f"mechanistic claim edges")
    print(f"    fragmentary (low info):                            "
          f"{n_fragment:>5,} ({n_fragment/n*100:.1f}%) → exploratory only")

    print(f"\n  ✓ T4 done. Next: 17_normalize_drugs.py (T3)")


if __name__ == "__main__":
    main()
