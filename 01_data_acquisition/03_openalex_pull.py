"""
Second-pass OpenAlex pull with broader search terms.

The first pass (03_openalex_pull.py) used 12 OR-joined exact phrases and 
retrieved only 1,786 candidates — far below OpenAlex's expected coverage 
for this topic. Root cause: OpenAlex's title_and_abstract.search uses 
phrase matching, so long multi-word phrases miss many relevant papers.

This second-pass script uses BROADER queries:
- 4 broad queries, each capturing one core concept
- Results merged via OpenAlex work ID deduplication
- Expected final N: 6,000-15,000 (matching OpenAlex's reputation for breadth)

Output:
- data/raw/openalex/openalex_candidates.jsonl  (deduplicated merged pool)
- data/raw/openalex/openalex_pull_log.json     (search metadata)

Usage:
    conda activate tcm-hdi
    python 01_data_acquisition/03b_openalex_pull_v2.py
    python 01_data_acquisition/03b_openalex_pull_v2.py --partial-2026
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
repo_root = Path(__file__).resolve().parent.parent
load_dotenv(repo_root / ".env")

import pyalex
from pyalex import Works

EMAIL = os.getenv("OPENALEX_EMAIL", "").strip()
if EMAIL and "example.com" not in EMAIL:
    pyalex.config.email = EMAIL
    print(f"Using polite pool: {EMAIL}\n")

# ============================================================
# Mode
# ============================================================
PARTIAL_2026 = "--partial-2026" in sys.argv
if PARTIAL_2026:
    YEAR_RANGE = "2026-2026"
    OUT_DIR = repo_root / "data" / "raw" / "openalex_partial2026"
    OUT_JSONL = OUT_DIR / "openalex_partial2026_candidates.jsonl"
    OUT_LOG = OUT_DIR / "openalex_partial2026_pull_log.json"
    LABEL = "PARTIAL 2026"
else:
    YEAR_RANGE = "2005-2025"
    OUT_DIR = repo_root / "data" / "raw" / "openalex"
    OUT_JSONL = OUT_DIR / "openalex_candidates.jsonl"
    OUT_LOG = OUT_DIR / "openalex_pull_log.json"
    LABEL = "MAIN 2005-2025"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Search strategy: 4 broad queries to capture full landscape
# ============================================================
# Each query uses LOWERCASE keyword search (OpenAlex tokenizes both query
# and documents); short phrases preserved with quotes only when essential.
# Queries are designed to OVER-RETRIEVE — Day 2/3 deduplication and 
# Day 3 quality filter will narrow to final N.

QUERIES = [
    {
        "name": "Q1_direct_HDI",
        "description": "Direct herb-drug interaction phrases",
        "search": '"herb-drug interaction" OR "herbal drug interaction" OR "TCM-drug interaction" OR "phytochemical drug interaction"',
    },
    {
        "name": "Q2_TCM_with_interaction",
        "description": "TCM (broad) + interaction (broad)",
        "search": '("traditional Chinese medicine" OR "Chinese herbal medicine" OR "Chinese herbal") AND ("drug interaction" OR "pharmacokinetic interaction" OR "pharmacodynamic interaction")',
    },
    {
        "name": "Q3_TCM_with_CYP",
        "description": "TCM (broad) + CYP enzymes (broad)",
        "search": '("traditional Chinese medicine" OR "Chinese herbal medicine" OR "Chinese herbal" OR "Chinese medicine") AND ("CYP3A4" OR "CYP2D6" OR "cytochrome P450" OR "P-glycoprotein")',
    },
    {
        "name": "Q4_TCM_with_metabolism",
        "description": "TCM (broad) + drug metabolism / transporter",
        "search": '("traditional Chinese medicine" OR "Chinese herbal medicine" OR "Chinese herbal") AND ("drug metabolism" OR "drug transporter" OR "drug efflux")',
    },
]


# ============================================================
# Execute all queries, collect unique work IDs
# ============================================================

print(f"{'='*70}")
print(f"OpenAlex pull: {LABEL}")
print(f"Year range:       {YEAR_RANGE}")
print(f"Sub-queries:      {len(QUERIES)}")
print(f"{'='*70}\n")

all_works = {}  # dedup by OpenAlex work ID
per_query_counts = {}
start_time = time.time()

for q in QUERIES:
    q_start = time.time()
    print(f"\n--- {q['name']}: {q['description']} ---")
    
    try:
        query = (
            Works()
            .search_filter(title_and_abstract=q["search"])
            .filter(publication_year=YEAR_RANGE)
            .filter(type="article|review")
            .filter(language="en")
        )
        n = query.count()
        print(f"  API reports {n:,} candidates")
        per_query_counts[q["name"]] = n
        
        if n > 80_000:
            print(f"  Skipping: too many results, suggests query is too broad")
            continue
        
        # Paginate and collect
        new_count = 0
        for page in query.paginate(per_page=200, n_max=None):
            for work in page:
                wid = work.get("id")
                if wid and wid not in all_works:
                    all_works[wid] = work
                    new_count += 1
        
        elapsed_q = time.time() - q_start
        print(f"  Pulled {new_count:,} new unique works (total unique: {len(all_works):,}, query time: {elapsed_q:.0f}s)")
    
    except KeyboardInterrupt:
        print(f"\nInterrupted during {q['name']}")
        break
    except Exception as e:
        print(f"  ERROR: {e}")
        continue


# ============================================================
# Save merged dedup pool
# ============================================================

print(f"\n{'='*70}")
print(f"Writing merged pool to: {OUT_JSONL.name}")

with open(OUT_JSONL, "w", encoding="utf-8") as fp:
    for work in all_works.values():
        json.dump(work, fp, ensure_ascii=False)
        fp.write("\n")

elapsed_total = time.time() - start_time
file_size_mb = OUT_JSONL.stat().st_size / 1024 / 1024

log = {
    "label": LABEL,
    "search_date": datetime.now().isoformat(),
    "year_range": YEAR_RANGE,
    "queries": QUERIES,
    "per_query_counts": per_query_counts,
    "unique_works_merged": len(all_works),
    "elapsed_sec": round(elapsed_total, 1),
    "output_file": str(OUT_JSONL.relative_to(repo_root)).replace(os.sep, "/"),
    "file_size_mb": round(file_size_mb, 2),
    "openalex_polite_pool": bool(EMAIL and "example.com" not in EMAIL),
}
with open(OUT_LOG, "w", encoding="utf-8") as fp:
    json.dump(log, fp, indent=2, ensure_ascii=False)


# ============================================================
# Summary
# ============================================================

print(f"\n{'='*70}")
print(f"DONE")
print(f"{'='*70}")
print(f"  Per-query results:")
for name, n in per_query_counts.items():
    print(f"    {name}: {n:,}")
print(f"  Unique merged:  {len(all_works):,}")
print(f"  Elapsed:        {elapsed_total/60:.1f} min")
print(f"  File size:      {file_size_mb:.1f} MB")
print(f"  Output:         {OUT_JSONL.relative_to(repo_root)}")

