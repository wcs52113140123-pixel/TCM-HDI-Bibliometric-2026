# PubMed Raw Export Data

This directory holds raw `.jsonl` export files from PubMed via NCBI E-utilities.

## Why these files ARE in version control

PubMed data is in the **U.S. public domain** (managed by the National Library 
of Medicine). There are no redistribution restrictions; these files are 
committed to this repository for full reproducibility.

## Files

| File | Records | Description |
|------|---------|-------------|
| pubmed_records.jsonl | 3,867 | Main analysis pool (2005-2025) |
| pubmed_pull_log.json | - | Search metadata + query string |

## Reproducibility

```bash
conda activate tcm-hdi
python 01_data_acquisition/04_pubmed_pull.py
```

See `01_data_acquisition/04_pubmed_search_strategy.md` for full details.

## Data format

JSONL: one JSON object per line. Each record contains:
- `pmid`: PubMed ID
- `title`, `year`, `journal`, `abstract`
- `authors`: list of "LastName Initials" strings
- `mesh_terms`: list of MeSH descriptor names (PubMed's unique strength)
- `doi`, `language`, `publication_types`
