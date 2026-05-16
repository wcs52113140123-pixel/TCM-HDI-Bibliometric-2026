# Day 5 Cross-file Dedup Fix Report

- Timestamp: `2026-05-15T16:48:03`

## 1. Pre-fix state

- main:    **9,438** rows
- partial: **316** rows
- sum:     **9,754** (with overlap)

## 2. Cross-file DOI overlap (full corpus, all years)

- main unique DOIs:     8,221
- partial unique DOIs:  315
- **Overlap:            37** (should be 0)

### 2a. Year distribution of overlapping records

- In main (overlap subset):    {2025: 13, 2026: 24}
- In partial (overlap subset): {2025: 1, 2026: 36}

## 3. Year-based reclassification

- main rows with year=2026 (should be 0): **25**
- partial rows with year≠2026 (should be 0): **1**
  (partial year distribution:)
  {2025: 1}

- main year=2026 DOIs already in partial:  24 (will drop from main)
- main year=2026 DOIs NOT in partial:      1 (will move from main → partial)

## 4. Constructing fixed corpora

- Moved from main → partial: **1** rows
- Partial internal dedup: 317 → 317 (diff=0)
- Group B+C cleanup: dropping **13** partial rows whose DOI is also in fixed main (preserving main's earlier-year assignment)

Sample of dropped rows (first 5):
```
                        doi  year source_db                                                        title
 10.1007/s00520-025-10227-z  2026    Scopus Implementation of an integrative safety consultation service
 10.1007/s12094-025-04017-6  2026    PubMed Safety and pharmacokinetics evaluation of oroxylin A in Chin
 10.1007/s42452-025-08116-5  2026    Scopus Herbal medicine meets machine learning: a systematic review 
 10.1007/s44187-025-00734-7  2026    Scopus Exploring the therapeutic potential and health benefits of M
10.1016/j.ijans.2025.100960  2026    Scopus A community-based behavioural change intervention on the kno
```

## 5. Post-fix verification

- main_fixed:    **9,413** rows (Δ = -25)
- partial_fixed: **304** rows (Δ = -12)
- sum: **9,717** (no overlap)

- Cross-file DOI overlap after fix: **0** (must be 0)
- main year values: `[2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]`
- partial year values: `[2026]`

✅ All invariants hold.

## 6. Backup + write

- Backup written: `integrated_corpus.parquet.bak_pre_cross_dedup`
- Backup written: `integrated_corpus_partial2026.parquet.bak_pre_cross_dedup`
- Fixed main written: `integrated_corpus.parquet` (9,413 rows)
- Fixed partial written: `integrated_corpus_partial2026.parquet` (304 rows)

## 7. Downstream impact (informational, no rerun yet)

### Day 3 corpus-wide stats (master_progress claims)

- 9,754 unique pubs claimed → **9717** actual (Δ=-37)
- 9,438 main claimed → **9413** actual (Δ=-25, -0.26%)

### Day 4 keyword analysis impact

- 25 records removed from main; assuming ~8.8 keywords/record → ~220 (record, keyword) pairs affected (~0.3% of 72,457)
- Top 50 keyword ranking, 5-cluster co-occurrence structure, 3-period evolution: changes <0.5%, ranks/cluster membership unchanged.
- **Recommendation**: do NOT rerun Day 4; cite original 9,438 snapshot with cross-dedup footnote in Methods.

### Day 3 descriptive stats impact

- citations / h-index / Lotka / Bradford: 25/9,754 = 0.26% perturbation, directional effects negligible. Defer recompute to Day 14 cleanup unless reviewer demands it.

### Day 5 topic modeling input

- Use fixed main = **9,413** records (was 9,438)
- partial_fixed (304) excluded from primary analysis per complete-year cutoff convention
