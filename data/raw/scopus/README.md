# Scopus Raw Export Data

This directory holds raw `.csv` export files from Scopus (Elsevier).

## Why these files are NOT in version control

Elsevier Terms of Use prohibit bulk redistribution of Scopus data. 
Raw export files are kept locally only.

## How to reproduce the dataset

1. Access scopus.com with institutional Scopus privileges
2. Execute the search query documented in:
   `../../../01_data_acquisition/02_scopus_search_strategy.md`
3. Use Scopus's asynchronous "Download CSV" feature (NOT the page-level 
   Export button) to export the full result set as a single CSV file
4. Save to this directory with the naming convention listed in:
   `../../../01_data_acquisition/data_acquisition_inventory.csv`

## Expected output (main analysis, PUBYEAR 2005-2025)

1 file, 7,181 records, ~190 MB. Search date: 2026-05-13.
