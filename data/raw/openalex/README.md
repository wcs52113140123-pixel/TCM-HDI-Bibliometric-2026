# OpenAlex Raw Export Data

This directory holds raw `.jsonl` export files from OpenAlex API queries.

## Why these files ARE in version control

Unlike WoS (Clarivate) and Scopus (Elsevier), OpenAlex data is licensed 
under **CC0 (public domain)**. There are no redistribution restrictions, 
and these files are committed to this repository for full reproducibility.

## Files

| File | Records | Description |
|------|---------|-------------|
| openalex_candidates.jsonl | 2,513 | Main analysis pool (2005-2025) |
| openalex_pull_log.json | - | Search metadata + sub-query stats |

## Reproducibility

To regenerate these files:

```bash
conda activate tcm-hdi
python 01_data_acquisition/03_openalex_pull.py
```

See `01_data_acquisition/03_openalex_search_strategy.md` for full details.

## Data format

JSONL: one JSON object per line, each representing a single Work entity 
from OpenAlex (https://docs.openalex.org/api-entities/works).
