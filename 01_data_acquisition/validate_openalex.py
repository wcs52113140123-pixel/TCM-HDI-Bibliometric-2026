"""Validate OpenAlex candidate pool quality."""
import json
import random
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
jsonl_path = repo_root / "data" / "raw" / "openalex" / "openalex_candidates.jsonl"

n_total = 0
n_with_doi = 0
n_with_abstract = 0
n_with_refs = 0
n_with_concepts = 0
years = {}

with open(jsonl_path, encoding="utf-8") as fp:
    works = [json.loads(line) for line in fp]

for work in works:
    n_total += 1
    if work.get("doi"):
        n_with_doi += 1
    if work.get("abstract_inverted_index"):
        n_with_abstract += 1
    if work.get("referenced_works"):
        n_with_refs += 1
    if work.get("concepts") or work.get("topics"):
        n_with_concepts += 1
    y = work.get("publication_year")
    if y:
        years[y] = years.get(y, 0) + 1

print(f"Total records:                  {n_total:,}")
print(f"With DOI:                       {n_with_doi:,} ({100*n_with_doi/n_total:.1f}%)")
print(f"With Abstract (inverted index): {n_with_abstract:,} ({100*n_with_abstract/n_total:.1f}%)")
print(f"With referenced_works:          {n_with_refs:,} ({100*n_with_refs/n_total:.1f}%)")
print(f"With concepts/topics:           {n_with_concepts:,} ({100*n_with_concepts/n_total:.1f}%)")
print()
print("Year distribution:")
for y in sorted(years):
    bar = "#" * (years[y] // 5)
    print(f"  {y}: {years[y]:4d}  {bar}")

print("\n--- 3 random sample titles ---")
random.seed(42)
samples = random.sample(works, 3)
for i, w in enumerate(samples, 1):
    title = w.get("title", "<no title>") or "<no title>"
    print(f"\n{i}. {title[:120]}")
    print(f"   Year:  {w.get('publication_year', '?')}")
    print(f"   DOI:   {w.get('doi', 'N/A')}")
    print(f"   Type:  {w.get('type', '?')}")
    print(f"   Cited: {w.get('cited_by_count', '?')}")
    refs = w.get("referenced_works") or []
    print(f"   Refs:  {len(refs)} referenced works")
