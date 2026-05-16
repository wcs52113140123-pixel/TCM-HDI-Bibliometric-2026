"""
Day 5 Block 0b: Micro-audit two anomalies surfaced by Block 0.

  1. 25 records with year=2026 inside main corpus (PRISMA says main = 2005-2025)
  2. Abstract length outliers (max=4049 tokens, p95=561) — possibly fulltext
     mis-stored in abstract field

Run from repo root:
  python 04_keyword_topic/06b_anomaly_audit.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DF_PATH = REPO / "data" / "processed" / "integrated_corpus.parquet"
PARTIAL_PATH = REPO / "data" / "processed" / "integrated_corpus_partial2026.parquet"

pd.set_option("display.max_colwidth", 90)
pd.set_option("display.width", 200)


def main():
    df = pd.read_parquet(DF_PATH)
    df_partial = pd.read_parquet(PARTIAL_PATH) if PARTIAL_PATH.exists() else None

    # =====================================================================
    # ANOMALY 1: year=2026 records inside "main" corpus
    # =====================================================================
    print("=" * 78)
    print("ANOMALY 1: year=2026 records inside main corpus (expected 2005-2025)")
    print("=" * 78)

    df_2026 = df[df["year"] == 2026].copy()
    print(f"\nCount: {len(df_2026)} (should be 0 if PRISMA strict; partial file has 316)\n")

    if len(df_2026) > 0:
        print("--- Per-record details ---")
        cols = ["record_id", "source_db", "doi", "year", "journal"]
        # Truncate journal for readability
        display = df_2026[cols].copy()
        display["title_short"] = df_2026["title"].astype(str).str.slice(0, 70)
        print(display.to_string(index=False))

        print("\n--- By source_db (which DB tagged them as 2026?) ---")
        print(df_2026["source_db"].value_counts().to_string())

        print("\n--- By source_db_count (1=single source, ≥2=appeared in multiple DBs) ---")
        if "source_db_count" in df_2026.columns:
            print(df_2026["source_db_count"].value_counts().to_string())

        print("\n--- Multi-source records: which DB list and IDs? ---")
        if "source_db_list" in df_2026.columns:
            multi = df_2026[df_2026["source_db_count"] >= 2]
            if len(multi) > 0:
                print(f"  {len(multi)} multi-source records (dedup survivors)")
                for _, r in multi.head(10).iterrows():
                    print(f"  - {r['record_id']}: source_db_list={r['source_db_list']}")
            else:
                print("  No multi-source records — all 25 are single-DB.")

        # Check DOI overlap with partial 2026 file (should be disjoint)
        if df_partial is not None and "doi" in df_partial.columns:
            main_dois = set(df_2026["doi"].dropna().tolist())
            partial_dois = set(df_partial["doi"].dropna().tolist())
            overlap = main_dois & partial_dois
            print(f"\n--- DOI overlap with partial2026 file ---")
            print(f"  main-2026 DOIs: {len(main_dois)}")
            print(f"  partial-2026 DOIs: {len(partial_dois)}")
            print(f"  Overlap: {len(overlap)} "
                  f"(should be 0 if dedup was correct across main/partial)")
            if overlap:
                print(f"  Overlapping DOIs (first 5): {list(overlap)[:5]}")

    # =====================================================================
    # ANOMALY 2: Extreme-length abstract outliers
    # =====================================================================
    print("\n" + "=" * 78)
    print("ANOMALY 2: Extreme-length abstract outliers (max=4049 tokens)")
    print("=" * 78)

    df_abs = df[df["abstract"].apply(
        lambda x: isinstance(x, str) and bool(x.strip())
    )].copy()
    df_abs["n_chars"] = df_abs["abstract"].str.len()
    df_abs["n_words"] = df_abs["abstract"].str.split().str.len()

    print(f"\nNon-empty abstracts: {len(df_abs):,}")
    print(f"Char length stats: mean={df_abs['n_chars'].mean():.0f}, "
          f"median={df_abs['n_chars'].median():.0f}, "
          f"p95={df_abs['n_chars'].quantile(0.95):.0f}, "
          f"p99={df_abs['n_chars'].quantile(0.99):.0f}, "
          f"max={df_abs['n_chars'].max():.0f}")

    print("\n--- Top 15 longest abstracts (by char count) ---")
    cols2 = ["record_id", "source_db", "year", "journal", "n_chars", "n_words"]
    top = df_abs.nlargest(15, "n_chars")[cols2 + ["title", "doc_type"]]
    for _, r in top.iterrows():
        print(f"\n  [{r['n_chars']:>5} ch / {r['n_words']:>4} w] "
              f"{r['source_db']} | {r['year']} | doc_type={r.get('doc_type', 'NA')}")
        print(f"  Journal: {str(r['journal'])[:80]}")
        print(f"  Title:   {str(r['title'])[:100]}")

    print("\n--- Distribution of doc_type for very long abstracts (>3000 chars) ---")
    long_abs = df_abs[df_abs["n_chars"] > 3000]
    print(f"  n = {len(long_abs)}")
    if "doc_type" in long_abs.columns and len(long_abs) > 0:
        print(long_abs["doc_type"].value_counts().to_string())

    print("\n--- Source DB for very long abstracts ---")
    if len(long_abs) > 0:
        print(long_abs["source_db"].value_counts().to_string())


if __name__ == "__main__":
    main()
