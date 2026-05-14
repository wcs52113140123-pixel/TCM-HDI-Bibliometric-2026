# Day 3 Log (Block 1-2 complete) — 2026-05-14

## Pre-flight decisions
- D1+: FINI (lastname + first initial) + ORCID validation for author dedup
- E1+: WoS country field > Scopus affiliation regex > manual dict normalization
- F1:  JCR 2024/2025 manual lookup for journal IF
- Politically compliant naming: Chinese Mainland / Hong Kong (China) / Taiwan (China) / Macao (China)

## Engineering fixes today
1. WoS C1 parser bug: `"C1".isalpha()` returns False (contains digit) 
   -> patched to per-char check (line[0].isalpha() AND line[1].isdigit())
2. Day 2 loaders missing affiliation fields 
   -> extended 4 loaders, full pipeline rerun, SHA updated
3. COUNTRY_NAMES dict expanded: added IQ, RS, ZW, CU, PS, MU, BW, NA, IL, AE
   after VOSviewer exposed ISO code remnants

## Block 1 - Annual trends
- Figure 2: Annual publication trend 2005-2026 with 5-yr MA, 2026 partial, MeSH lag note
- Table 1, 1b: Annual statistics + sub-period CAGR
- Key insights:
  - 4-phase growth: 2005-10 (5.4%) / 2011-17 (3.7%) / 2018-23 (0.2%) / 2024-25 (16.6%)
  - 2024 = +34.2% YoY surge (only acceleration year above 20%)
  - 2026 forecast ~842 publications (continuing growth)
  - 2023 dip explained as PubMed MeSH indexing lag

## Block 2A - Country extraction
- 200+ country alias dictionary with HK/TW/MO priority handling
- Final coverage: 7,976 / 9,438 (84.5%) records
- Methods note: 15.5% missing = predominantly PubMed records without affiliation

## Block 2B - Country ranking + collaboration
- Table 2: Top 30 countries (N_pub, %, AvgCit, MCP%, region)
- Table 2b: Bilateral collaboration matrix (1,012 unique pairs)
- Figure 3: Top 20 country horizontal bar chart (region-color coded)
- Key insights:
  - Chinese Mainland 54.1%, US 13.7%, India 6.7%
  - China (aggregated) = 61.4%
  - Chinese mainland MCP 17.5% (low) vs HK 67.6% / MO 88.9% (very high)
  - Italy AvgCit 86.9 vs Chinese Mainland 25.9 = quality vs quantity divide
  - Top bilateral: CN-US 257, CN-HK 129, CN-MO 92, CN-TW 81

## Block 2C - VOSviewer international collaboration network
- First successful VOSviewer workflow: Python -> map.txt + network.txt
- Final params: Resolution 0.50, Min cluster 2, Merge small, Min strength 5
- Figure 4a: Network visualization (6 clusters)
- Figure 4b: Density visualization (3 hot-spots: CN, US, India)
- Cluster structure:
  1. Chinese hub (Chinese Mainland, HK, MO, MN, FR, NO)
  2. South Asian-Middle East (India + Saudi/Pakistan/Egypt/UAE/etc + Japan)
  3. US-Africa-Russia (US, Israel, South Africa, Zimbabwe, Russia)
  4. European core (UK, Germany, Italy, Spain, surrounding Mediterranean)
  5. Commonwealth bridge (Australia, Canada, Singapore, New Zealand)
  6. East Asian Sinographic (South Korea, Taiwan (China), Vietnam)

## Documents added
- 03_descriptive_analysis/01_annual_trends.py
- 03_descriptive_analysis/02_country_extraction.py
- 03_descriptive_analysis/03_country_ranking.py
- 03_descriptive_analysis/04_export_vosviewer.py
- 03_descriptive_analysis/diagnose_affiliations.py
- results/tables/table_01_annual_publications.csv
- results/tables/table_01b_period_statistics.csv
- results/tables/table_02_country_coverage.csv
- results/tables/table_02_country_ranking.csv
- results/tables/table_02b_collaboration_matrix.csv
- results/figures/figure_02_annual_trend.png
- results/figures/figure_03_top_countries.png
- results/figures/figure_04_country_collab_network.png
- results/figures/figure_04b_country_collab_density.png
- results/vosviewer/country_collab_map.txt
- results/vosviewer/country_collab_network.txt
- data/processed/country_lookup.parquet
- data/processed/country_extraction_audit.csv
- data/processed/country_collaboration_pairs.parquet
- docs/day3_block1_2_discussion_drafts.md
- docs/day3_log.md

## Day 3 Block 3-5 (tomorrow)
- Block 3: Institution + author rankings, Lotka's law (bibliometrix R)
- Block 4: Journal analysis + Bradford's law + IF mapping
- Block 5: Citation analysis + h-index + top-cited papers
- Block 6: Sanity check + Day 3 final commit
- Estimated: 4 hours
