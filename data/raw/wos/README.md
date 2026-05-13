# WoS Core Collection Raw Export Data

This directory holds raw `.txt` export files from Web of Science Core Collection.

## Why these files are NOT in version control

Clarivate Analytics Terms of Use prohibit bulk redistribution of Web of Science 
data. Raw export files are kept locally only.

## How to reproduce the dataset

1. Access webofscience.com with institutional Core Collection privileges
2. Execute the search query documented in:
   `../../../01_data_acquisition/01_wos_search_strategy.md`
3. Export records in batches (max 500 per batch) using:
   - Format: Plain text file (.txt)
   - Content: Full Record and Cited References
4. Save batch files following the naming convention listed in:
   `../../../01_data_acquisition/wos_file_inventory.csv`

## Expected output (main analysis, PY=2005-2025)

7 batch files, total 3,091 records, ~24.9 MB.

Search date: 2026-05-13.

## Naming convention

`wos_batch_NNN_START-END.txt` where:
- `NNN` is zero-padded batch number (001, 002, ...)
- `START-END` is the inclusive record range within the relevance-sorted results
