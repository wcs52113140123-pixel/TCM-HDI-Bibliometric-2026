# Day 2 Data Integration — Final Summary

Generated: 2026-05-14T10:08:58.292897

## PRISMA Flow

### Identification
- WoS:      3,091 records
- Scopus:   7,181 records
- OpenAlex: 2,513 records
- PubMed:   3,867 records
- **Total raw: 16,652**

### Stage 2: DOI Primary-Key Deduplication
- Input: 16,652
- With DOI: 15,162
- Without DOI: 1,490
- Unique DOIs: 8,312
- Duplicates removed: 6,850
- **Output: 9,802**

### Stage 3: Fuzzy Title Matching (ratio >= 95)
- Input: 9,802
- Threshold: 95 (bibliometrix default tol=0.95)
- Blocking key: year + first_author_lastname
- Fuzzy pairs found: 358
- Duplicate clusters: 200
- Records removed: 266
- **Output: 9,536**

### Stage 4: OpenAlex Client-Side Precision Filter (B1)
- Input: 9,536
- OpenAlex exclusives: 773
- Passed (matched B1/B2/B3): 675
- Dropped (no block matched): 773
- Block breakdown: {'B1_direct': 439, 'B3_tcm_cyp': 131, 'B2_tcm_interaction': 105, 'B0_none': 98}
- **Output: 9,438**

## Final Corpus

- **N = 9,438 unique TCM-HDI publications (2005-2025)**
- File: `data/processed/integrated_corpus.parquet`

### Field Coverage
- DOI: 8,221/9,438 (87.1%)
- Abstract >50 chars: 9,152/9,438 (97.0%)
- Year: 9,438/9,438 (100.0%)
- First author: 9,387/9,438 (99.5%)
- MeSH (PubMed): 1,021/9,438 (10.8%)
- Concepts (OpenAlex): 675/9,438 (7.2%)

### Year Distribution
- 2005: 261
- 2006: 262
- 2007: 300
- 2008: 277
- 2009: 314
- 2010: 340
- 2011: 356
- 2012: 423
- 2013: 437
- 2014: 501
- 2015: 449
- 2016: 453
- 2017: 443
- 2018: 467
- 2019: 538
- 2020: 550
- 2021: 611
- 2022: 591
- 2023: 471
- 2024: 632
- 2025: 737
- 2026: 25

### Cross-Database Coverage

Records found in N databases (higher N = higher confidence):
- 1 DB(s): 5,797 (61.4%)
- 2 DB(s): 1,567 (16.6%)
- 3 DB(s): 949 (10.1%)
- 4 DB(s): 1,125 (11.9%)

## Decisions Applied

- **A1**: DOI-less records kept; matched via fuzzy title + year + first_author (PRISMA-S standard)
- **B1**: OpenAlex-exclusive records filtered using WoS-equivalent 3-block logic
- **C-Standard**: Fuzzy threshold ratio>=95 (bibliometrix default tol=0.95)
