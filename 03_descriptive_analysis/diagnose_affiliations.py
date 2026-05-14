"""Diagnose what affiliation/country fields exist in stage1_raw_concatenated."""
from pathlib import Path
import pandas as pd

repo_root = Path(__file__).resolve().parent.parent
df = pd.read_parquet(repo_root / "data/processed/stage1_raw_concatenated.parquet")

# Wait — Stage 1 was gitignored! Try the integrated_corpus instead
print(f"Available columns in stage1_raw_concatenated:")
print(list(df.columns))
print(f"\nTotal records: {len(df):,}")

# Check non-unified columns
unified_cols = {"doi", "title", "title_normalized", "year", "abstract",
                "authors", "first_author_lastname", "journal", "doc_type",
                "language", "cited_by", "references_count", "author_keywords",
                "keywords_plus", "mesh_terms", "openalex_concepts",
                "record_id", "source_db", "source_id"}
extra_cols = [c for c in df.columns if c not in unified_cols]
print(f"\nNon-unified (extra) columns: {extra_cols}")

# For each DB, show first 2 records' extra-column values
for db in ["WoS", "Scopus", "OpenAlex", "PubMed"]:
    sub = df[df["source_db"] == db].head(2)
    print(f"\n{'='*70}\n{db} - first 2 records' extra fields:\n{'='*70}")
    for idx, row in sub.iterrows():
        print(f"\n--- Record {idx} ---")
        for col in extra_cols:
            val = row[col]
            if val is not None and (not isinstance(val, str) or val.strip()):
                print(f"  [{col}]: {str(val)[:250]}")
