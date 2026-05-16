"""
Day 8 Step 3: Inspect residual mechanism buckets after Schema v3 re-extraction.

Analyzes BOTH:
  - 'other' bucket        (~226 interactions after re-extraction, 7.3%)
  - 'unspecified' bucket  (~484 interactions after re-extraction, 15.6%)

Goal: determine whether there's a third hidden mechanism category worth
a Schema v4 extension, or whether the residual is genuinely heterogeneous
and should be accepted.

Output:
  console — pattern detection per bucket (top targets, herbs, drugs, keywords)
  results/llm_audit/residual_mechanism_inspection.md — 30 hand-review cases
                                                       (15 'other' + 15 'unspecified')

Usage:
    python 05_llm_extraction/14_inspect_residual.py
        [--model openai/gpt-4o-mini]
        [--prefix primary]
        [--n-sample 15]
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"
AUDIT_DIR = REPO / "results" / "llm_audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "by",
    "and", "or", "but", "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "may", "might", "shall", "should", "can", "this", "that", "these", "those",
    "it", "its", "as", "from", "into", "via", "than", "such", "which",
    "we", "our", "showed", "found", "observed", "demonstrated", "reported",
    "indicated", "suggests", "suggested", "results", "study", "studies",
    "effect", "effects", "increase", "increased", "decrease", "decreased",
    "treatment", "treated", "group", "groups", "compared", "after", "before",
    "however", "also", "no", "not", "significantly", "significant", "p", "vs",
    "rats", "mice", "cells", "level", "levels",
}


def _tokenize(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    return [w for w in re.findall(r"[a-zA-Z]{3,}", text.lower())
            if w not in _STOPWORDS]


def analyze_bucket(df: pd.DataFrame, label: str) -> dict | None:
    if len(df) == 0:
        return None
    targets = (df["specific_target"].dropna().astype(str).str.strip().str.lower()
               .value_counts())
    herbs = (df["herb_common_name"]
             .fillna(df["herb_name_latin"])
             .fillna(df["herb_active_compound"])
             .fillna("(unknown)").astype(str).str.lower().str.strip())
    drugs = df["drug_name"].fillna("(unknown)").astype(str).str.lower().str.strip()
    direction = df["direction"].value_counts()
    evidence = df["evidence_type"].value_counts()
    all_words = []
    for q in df["evidence_quote"].dropna():
        all_words.extend(_tokenize(q))
    keywords = Counter(all_words).most_common(30)
    return {
        "label": label, "n": len(df),
        "targets": targets,
        "herbs": herbs.value_counts(),
        "drugs": drugs.value_counts(),
        "direction": direction,
        "evidence_type": evidence,
        "keywords": keywords,
    }


def print_bucket(stats: dict | None, n_total: int) -> None:
    if stats is None:
        return
    pct = stats["n"] / n_total * 100
    print(f"\n{'='*72}\n  '{stats['label']}' bucket — "
          f"{stats['n']:,} interactions ({pct:.1f}% of all)\n{'='*72}")

    print(f"\n  Top 15 specific_targets:")
    for t, n in stats["targets"].head(15).items():
        print(f"    {t[:55]:55s} {n:>4d} ({n/stats['n']*100:.1f}%)")

    print(f"\n  Top 12 herbs:")
    for h, n in stats["herbs"].head(12).items():
        print(f"    {h[:50]:50s} {n:>4d}")

    print(f"\n  Top 12 drugs:")
    for d, n in stats["drugs"].head(12).items():
        print(f"    {d[:50]:50s} {n:>4d}")

    print(f"\n  Direction:")
    for d, n in stats["direction"].items():
        print(f"    {d:30s} {n:>4d}")

    print(f"\n  Evidence type:")
    for e, n in stats["evidence_type"].items():
        print(f"    {e:25s} {n:>4d}")

    print(f"\n  Top 25 informative keywords in evidence_quote "
          f"(signals possible missed category):")
    for w, n in stats["keywords"][:25]:
        print(f"    {w:30s} {n:>4d}")


def write_markdown(df_other: pd.DataFrame, df_unspec: pd.DataFrame,
                   n_total: int, output_path: Path,
                   n_sample: int = 15, seed: int = 42) -> None:
    lines = [
        "# Residual Mechanism Audit (post Schema v3 re-extraction)\n",
        f"Total interactions: **{n_total:,}**\n",
        f"- `other` bucket:       **{len(df_other):,}** ({len(df_other)/n_total*100:.1f}%)",
        f"- `unspecified` bucket: **{len(df_unspec):,}** ({len(df_unspec)/n_total*100:.1f}%)",
        "",
        "**Decision goal**: is there a third hidden mechanism category worth a",
        "Schema v4 extension? Or should residuals be accepted as-is?\n",
    ]

    def case_block(df: pd.DataFrame, label: str, n: int) -> str:
        out = [f"\n---\n\n# `{label}` bucket — {n} sample cases\n"]
        sub = df.sample(min(n, len(df)), random_state=seed).reset_index(drop=True)
        for i, row in sub.iterrows():
            herb = (row.get("herb_common_name") or row.get("herb_name_latin")
                    or row.get("herb_active_compound") or "(unknown)")
            drug = row.get("drug_name") or "(unknown)"
            target = row.get("specific_target") or "—"
            direction = row.get("direction") or "—"
            evidence = (row.get("evidence_quote") or "")[:600]
            conf = row.get("confidence")
            rid = row.get("record_id")
            year = row.get("year")
            out.append(f"\n### {label}-{i+1}: `{rid}` (year {year})\n")
            out.append(f"- **Herb**: `{herb}` × **Drug**: `{drug}`")
            out.append(f"- **Target**: `{target}` | **Direction**: `{direction}` | "
                       f"**Conf**: {conf}")
            out.append(f"- **Evidence**:\n  > {evidence}")
        return "\n".join(out)

    if len(df_other) > 0:
        lines.append(case_block(df_other, "other", n_sample))
    if len(df_unspec) > 0:
        lines.append(case_block(df_unspec, "unspecified", n_sample))

    lines += [
        "\n---\n\n## Decision framework\n",
        "After scanning the samples, choose:\n",
        "1. **Schema v4 extension** — if ≥10 `other` cases cluster into a recognizable "
        "NEW category (e.g. `immunomodulation`, `gut_microbiota_mediated`, `autophagy`, "
        "`ferroptosis`, `ER_stress`, `epigenetic_modulation`). Then extend schema "
        "and re-extract affected records (~$0.4).",
        "2. **Prompt improvement** — if `unspecified` actually contains describable "
        "mechanisms that the LLM was too cautious to categorize. Improve prompt to "
        "be more aggressive in low-confidence cases.",
        "3. **Accept residual** — if cases are genuinely heterogeneous with no clear "
        "pattern. This is normal for LLM-based extraction and acceptable in Methods.\n",
        "Tell Claude which decision to make and the proposed new category names.",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary")
    ap.add_argument("--n-sample", type=int, default=15)
    args = ap.parse_args()

    model_safe = args.model.replace("/", "__").replace(".", "_")
    interactions_path = LLM_DIR / f"{args.prefix}_{model_safe}.interactions.parquet"
    if not interactions_path.exists():
        print(f"FATAL: {interactions_path.relative_to(REPO)} not found")
        print("Run 10_parse_results.py first.")
        return

    df = pd.read_parquet(interactions_path)
    n_total = len(df)
    df_other = df[df["mechanism"] == "other"].copy()
    df_unspec = df[df["mechanism"] == "unspecified"].copy()

    print(f"{'='*72}\n  Residual mechanism audit (Day 8 Step 3)\n{'='*72}")
    print(f"  Total interactions:     {n_total:,}")
    print(f"  'other' bucket:         {len(df_other):,} "
          f"({len(df_other)/n_total*100:.1f}%)")
    print(f"  'unspecified' bucket:   {len(df_unspec):,} "
          f"({len(df_unspec)/n_total*100:.1f}%)")

    print_bucket(analyze_bucket(df_other, "other"), n_total)
    print_bucket(analyze_bucket(df_unspec, "unspecified"), n_total)

    out_md = AUDIT_DIR / "residual_mechanism_inspection.md"
    write_markdown(df_other, df_unspec, n_total, out_md,
                   n_sample=args.n_sample)
    print(f"\n  → {out_md.relative_to(REPO)} "
          f"({2*args.n_sample} sample cases, 15 each)")

    print(f"\n  NEXT:")
    print(f"     1. Read console output above for top patterns")
    print(f"     2. (Optional) Open markdown to read 30 evidence_quote samples")
    print(f"     3. Decide: Schema v4 extension? prompt fix? or accept residual?")
    print(f"     Tell Claude your call.")


if __name__ == "__main__":
    main()
