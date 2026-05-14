# Day 2: Data Integration

This module integrates raw data from 4 databases (WoS, Scopus, OpenAlex, PubMed) 
into a single unified `integrated_corpus.parquet` dataset.

## Pipeline (5 stages)
Stage 1: Load + concatenate         16,652 records
Stage 2: DOI primary-key dedup       9,802 records
Stage 3: Fuzzy title matching        9,536 records
Stage 4: OpenAlex precision filter   9,438 records
Stage 5: Finalize + PRISMA           9,438 records (FINAL)
## Scripts (run in order)

| Script | Purpose |
|--------|---------|
| `load_wos.py` | Parse WoS plain-text export → standardized records |
| `load_scopus.py` | Parse Scopus CSV → standardized records |
| `load_openalex.py` | Parse OpenAlex JSONL → standardized records (reconstructs abstract from inverted index) |
| `load_pubmed.py` | Parse PubMed JSONL → standardized records |
| `01_load_and_concatenate.py` | Combines 4 loaders → `stage1_raw_concatenated.parquet` |
| `02_doi_deduplicate.py` | DOI primary-key dedup → `stage2_doi_deduplicated.parquet` |
| `03_fuzzy_deduplicate.py` | Fuzzy title matching (ratio>=95) → `stage3_fuzzy_deduplicated.parquet` |
| `04_openalex_filter.py` | Precision filter on OpenAlex exclusives → `stage4_quality_filtered.parquet` |
| `05_finalize.py` | Build final corpus + PRISMA data → `integrated_corpus.parquet` |

## Run full pipeline

```bash
conda activate tcm-hdi

# Main analysis (2005-2025)
python 02_data_integration/01_load_and_concatenate.py
python 02_data_integration/02_doi_deduplicate.py
python 02_data_integration/03_fuzzy_deduplicate.py
python 02_data_integration/04_openalex_filter.py
python 02_data_integration/05_finalize.py

# Partial 2026 supplement
python 02_data_integration/01_load_and_concatenate.py --partial-2026
python 02_data_integration/02_doi_deduplicate.py --partial-2026
python 02_data_integration/03_fuzzy_deduplicate.py --partial-2026
python 02_data_integration/04_openalex_filter.py --partial-2026
python 02_data_integration/05_finalize.py --partial-2026
```

## Final outputs

| File | Records | Description |
|------|---------|-------------|
| `data/processed/integrated_corpus.parquet` | 9,438 | **Final integrated dataset (input for Day 3+)** |
| `data/processed/integrated_corpus_partial2026.parquet` | 316 | 2026 supplement |
| `data/processed/prisma_flow_data.json` | — | PRISMA flow data (for Day 4 Figure 1) |
| `data/processed/integration_summary.md` | — | Human-readable summary |

## Audit trail

Each stage produces an audit log for transparency:
- `stage2_dedup_audit.csv`: per-DOI which DBs had it
- `stage3_fuzzy_matches.csv`: fuzzy-matched cluster details
- `stage4_openalex_filter_audit.csv`: OpenAlex records that failed precision filter

## Decisions applied

See `decisions.md` for the methodological choices (A1, B1, C-Standard) and 
their literature justification.
