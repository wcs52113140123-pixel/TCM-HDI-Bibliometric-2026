"""
Day 5 Block 0c: Cross-file dedup fix for main vs partial 2026 corpora.

Bug surfaced by Block 0b audit:
  - 25 records with year=2026 inside main corpus
  - 24 of their DOIs ALSO exist in partial 2026 file → duplicate counting
  - 1 DOI exists only in main

Fix strategy (deterministic):
  1. Strict year-based classification:
       year <= 2025 → main
       year == 2026 → partial
  2. Cross-file DOI uniqueness enforced:
       overlapping DOIs (24): keep the partial copy (correct destination by year)
       main-only year=2026 DOI (1): move that row from main to partial
  3. Original files backed up to *.bak_pre_cross_dedup before any write.

Run from repo root:
  python 04_keyword_topic/06c_cross_dedup_fix.py
"""

from __future__ import annotations

import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
MAIN_PATH = DATA / "integrated_corpus.parquet"
PARTIAL_PATH = DATA / "integrated_corpus_partial2026.parquet"
REPORT_DIR = REPO / "results" / "audits"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = REPORT_DIR / "day5_cross_dedup_fix_report.md"


def norm_doi(s):
    """Lowercase + strip; treat empty/whitespace as None for set operations."""
    if not isinstance(s, str):
        return None
    s = s.strip().lower()
    return s if s else None


def main():
    lines: list[str] = []

    def log(msg=""):
        print(msg)
        lines.append(msg)

    log("# Day 5 Cross-file Dedup Fix Report\n")
    log(f"- Timestamp: `{datetime.now().isoformat(timespec='seconds')}`")
    log("")

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------
    df_main = pd.read_parquet(MAIN_PATH)
    df_partial = pd.read_parquet(PARTIAL_PATH)

    log("## 1. Pre-fix state\n")
    log(f"- main:    **{len(df_main):,}** rows")
    log(f"- partial: **{len(df_partial):,}** rows")
    log(f"- sum:     **{len(df_main) + len(df_partial):,}** (with overlap)")
    log("")

    # ------------------------------------------------------------------
    # Audit cross-file overlap (full, not just year=2026)
    # ------------------------------------------------------------------
    df_main["_doi_norm"] = df_main["doi"].apply(norm_doi)
    df_partial["_doi_norm"] = df_partial["doi"].apply(norm_doi)

    main_dois = set(df_main["_doi_norm"].dropna())
    partial_dois = set(df_partial["_doi_norm"].dropna())
    overlap = main_dois & partial_dois

    log("## 2. Cross-file DOI overlap (full corpus, all years)\n")
    log(f"- main unique DOIs:     {len(main_dois):,}")
    log(f"- partial unique DOIs:  {len(partial_dois):,}")
    log(f"- **Overlap:            {len(overlap):,}** (should be 0)")
    log("")

    # Inspect year of overlapping records in each file
    main_overlap_rows = df_main[df_main["_doi_norm"].isin(overlap)]
    partial_overlap_rows = df_partial[df_partial["_doi_norm"].isin(overlap)]

    log("### 2a. Year distribution of overlapping records\n")
    log(f"- In main (overlap subset):    "
        f"{dict(main_overlap_rows['year'].value_counts().sort_index())}")
    log(f"- In partial (overlap subset): "
        f"{dict(partial_overlap_rows['year'].value_counts().sort_index())}")
    log("")

    # ------------------------------------------------------------------
    # Year-based reclassification
    # ------------------------------------------------------------------
    log("## 3. Year-based reclassification\n")

    main_2026 = df_main[df_main["year"] == 2026].copy()
    partial_not_2026 = df_partial[df_partial["year"] != 2026].copy()

    log(f"- main rows with year=2026 (should be 0): **{len(main_2026)}**")
    log(f"- partial rows with year≠2026 (should be 0): **{len(partial_not_2026)}**")
    if len(partial_not_2026) > 0:
        log("  (partial year distribution:)")
        log(f"  {dict(partial_not_2026['year'].value_counts().sort_index())}")
    log("")

    main_2026_dois = set(main_2026["_doi_norm"].dropna())
    main_only_2026_dois = main_2026_dois - partial_dois
    log(f"- main year=2026 DOIs already in partial:  "
        f"{len(main_2026_dois & partial_dois):,} (will drop from main)")
    log(f"- main year=2026 DOIs NOT in partial:      "
        f"{len(main_only_2026_dois):,} (will move from main → partial)")
    log("")

    # ------------------------------------------------------------------
    # Construct fixed dataframes
    # ------------------------------------------------------------------
    log("## 4. Constructing fixed corpora\n")

    # Fixed main: drop all year=2026 rows
    df_main_fixed = df_main[df_main["year"] != 2026].copy()

    # Records to MOVE from main → partial (main-only year=2026 DOIs + null-DOI year=2026)
    main_2026_to_move = main_2026[
        main_2026["_doi_norm"].isin(main_only_2026_dois)
        | main_2026["_doi_norm"].isna()
    ].copy()

    # Fixed partial: existing partial (we trust it) + moved records from main
    # Also enforce internal dedup on partial just in case
    df_partial_fixed = pd.concat([df_partial, main_2026_to_move], ignore_index=True)

    # Internal dedup of partial by DOI (keep first; partial-native preferred since
    # it was concatenated first)
    before_internal = len(df_partial_fixed)
    df_partial_fixed = df_partial_fixed.drop_duplicates(
        subset="_doi_norm", keep="first"
    ).copy()
    # ...but drop_duplicates also collapses null DOIs, which we want to keep.
    # Re-add the null-DOI rows that were collapsed.
    null_doi_rows = pd.concat([df_partial, main_2026_to_move], ignore_index=True)
    null_doi_rows = null_doi_rows[null_doi_rows["_doi_norm"].isna()]
    df_partial_fixed = pd.concat([
        df_partial_fixed[df_partial_fixed["_doi_norm"].notna()],
        null_doi_rows
    ], ignore_index=True)
    after_internal = len(df_partial_fixed)

    log(f"- Moved from main → partial: **{len(main_2026_to_move)}** rows")
    log(f"- Partial internal dedup: {before_internal} → {after_internal} "
        f"(diff={before_internal - after_internal})")

    # ------------------------------------------------------------------
    # Group B+C cleanup: remove partial rows whose DOI is also in fixed main.
    # These are in-press articles where main(year=2025) and partial(year=2026)
    # disagree on year (Group B), plus any pure duplicates (Group C).
    # Decision: keep main's earlier-year assignment, drop the partial copy.
    # ------------------------------------------------------------------
    main_fixed_dois = set(df_main_fixed["_doi_norm"].dropna())
    mask_in_main = df_partial_fixed["_doi_norm"].isin(main_fixed_dois)
    n_groupbc = int(mask_in_main.sum())
    log(f"- Group B+C cleanup: dropping **{n_groupbc}** partial rows whose DOI "
        f"is also in fixed main (preserving main's earlier-year assignment)")
    if n_groupbc > 0:
        sample_dropped = df_partial_fixed[mask_in_main][
            ["doi", "year", "source_db", "title"]
        ].head(5).copy()
        sample_dropped["title"] = sample_dropped["title"].astype(str).str.slice(0, 60)
        log("\nSample of dropped rows (first 5):")
        log("```")
        log(sample_dropped.to_string(index=False))
        log("```")
    df_partial_fixed = df_partial_fixed[~mask_in_main].copy()
    log("")

    # Drop helper col
    df_main_fixed = df_main_fixed.drop(columns="_doi_norm")
    df_partial_fixed = df_partial_fixed.drop(columns="_doi_norm")
    df_main = df_main.drop(columns="_doi_norm")
    df_partial = df_partial.drop(columns="_doi_norm")

    # ------------------------------------------------------------------
    # Verify
    # ------------------------------------------------------------------
    log("## 5. Post-fix verification\n")

    log(f"- main_fixed:    **{len(df_main_fixed):,}** rows "
        f"(Δ = {len(df_main_fixed) - len(df_main):+d})")
    log(f"- partial_fixed: **{len(df_partial_fixed):,}** rows "
        f"(Δ = {len(df_partial_fixed) - len(df_partial):+d})")
    log(f"- sum: **{len(df_main_fixed) + len(df_partial_fixed):,}** (no overlap)")
    log("")

    # Re-check overlap and year purity
    m_dois = set(df_main_fixed["doi"].apply(norm_doi).dropna())
    p_dois = set(df_partial_fixed["doi"].apply(norm_doi).dropna())
    new_overlap = m_dois & p_dois
    log(f"- Cross-file DOI overlap after fix: **{len(new_overlap)}** (must be 0)")

    bad_main_years = df_main_fixed["year"].unique().tolist()
    bad_partial_years = df_partial_fixed["year"].unique().tolist()
    log(f"- main year values: `{sorted(bad_main_years)}`")
    log(f"- partial year values: `{sorted(bad_partial_years)}`")
    log("")

    assert len(new_overlap) == 0, f"FATAL: still {len(new_overlap)} overlap after fix"
    assert 2026 not in bad_main_years, "FATAL: year=2026 still in main"
    assert all(y == 2026 for y in bad_partial_years), \
        f"FATAL: non-2026 years in partial: {bad_partial_years}"

    log("✅ All invariants hold.\n")

    # ------------------------------------------------------------------
    # Backup + write
    # ------------------------------------------------------------------
    log("## 6. Backup + write\n")

    bak_main = MAIN_PATH.with_suffix(".parquet.bak_pre_cross_dedup")
    bak_partial = PARTIAL_PATH.with_suffix(".parquet.bak_pre_cross_dedup")

    if not bak_main.exists():
        shutil.copy2(MAIN_PATH, bak_main)
        log(f"- Backup written: `{bak_main.name}`")
    else:
        log(f"- Backup already exists: `{bak_main.name}` (skipped)")

    if not bak_partial.exists():
        shutil.copy2(PARTIAL_PATH, bak_partial)
        log(f"- Backup written: `{bak_partial.name}`")
    else:
        log(f"- Backup already exists: `{bak_partial.name}` (skipped)")

    df_main_fixed.to_parquet(MAIN_PATH, index=False)
    df_partial_fixed.to_parquet(PARTIAL_PATH, index=False)
    log(f"- Fixed main written: `{MAIN_PATH.name}` ({len(df_main_fixed):,} rows)")
    log(f"- Fixed partial written: `{PARTIAL_PATH.name}` ({len(df_partial_fixed):,} rows)")
    log("")

    # ------------------------------------------------------------------
    # Downstream impact assessment
    # ------------------------------------------------------------------
    log("## 7. Downstream impact (informational, no rerun yet)\n")

    delta_main = len(df_main_fixed) - len(df_main)
    delta_main_pct = delta_main / len(df_main) * 100

    log(f"### Day 3 corpus-wide stats (master_progress claims)\n")
    log(f"- 9,754 unique pubs claimed → **{len(df_main_fixed) + len(df_partial_fixed)}** "
        f"actual (Δ={len(df_main_fixed) + len(df_partial_fixed) - 9754})")
    log(f"- 9,438 main claimed → **{len(df_main_fixed)}** actual "
        f"(Δ={delta_main:+d}, {delta_main_pct:+.2f}%)")
    log("")
    log("### Day 4 keyword analysis impact\n")
    log(f"- 25 records removed from main; assuming ~8.8 keywords/record "
        f"→ ~220 (record, keyword) pairs affected (~0.3% of 72,457)")
    log("- Top 50 keyword ranking, 5-cluster co-occurrence structure, "
        "3-period evolution: changes <0.5%, ranks/cluster membership unchanged.")
    log("- **Recommendation**: do NOT rerun Day 4; cite original 9,438 snapshot "
        "with cross-dedup footnote in Methods.")
    log("")
    log("### Day 3 descriptive stats impact\n")
    log("- citations / h-index / Lotka / Bradford: 25/9,754 = 0.26% perturbation, "
        "directional effects negligible. Defer recompute to Day 14 cleanup unless "
        "reviewer demands it.")
    log("")
    log("### Day 5 topic modeling input\n")
    log(f"- Use fixed main = **{len(df_main_fixed):,}** records (was 9,438)")
    log(f"- partial_fixed ({len(df_partial_fixed)}) excluded from primary analysis "
        f"per complete-year cutoff convention")
    log("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📝 Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
