# TCM-HDI Bibliometric Project — Master Progress Document

> **Purpose**: Comprehensive snapshot of project status. Use this document to 
> seamlessly resume work in a new Claude conversation.  
> **Last updated**: 2026-05-15, end of Day 3

---

## Project Overview

- **Title**: Herb-Drug Interactions of Traditional Chinese Medicine: Bibliometric 
  and Pharmacological Network Analysis (2005-2026)
- **Target journals**: Frontiers in Pharmacology (IF 4.4 JCR 2024) / Pharmacological Research
- **Type**: 21-day side project (CV-building)
- **Owner**: Adalheiddr (graduate student, Beijing brain-dev lab)
- **Repository**: github.com/wcs52113140123-pixel/TCM-HDI-Bibliometric-2026
- **Local path**: D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026
- **Conda env**: tcm-hdi (Python 3.11.15)

## Day 3 Final Numbers (HEADLINES)

| Metric | Value |
|---|---|
| **Total publications** | 9,438 main + 316 partial 2026 = 9,754 |
| **Total citations** | 242,765 |
| **Corpus h-index** | **171** |
| **Top-cited paper** | Cabrera 2006 (1,669 citations) |
| **Country coverage** | 84.5% (with 8 distinct labels for political compliance) |
| **Institution coverage** | 83.9% (ROR-standardized + 1,029 catch-all fixes) |
| **Unique authors (D2)** | 43,472 FINI+Institution combos (vs 16,094 D1) |
| **Top author** | duan_j @ NUCM (40 papers) |
| **Top institution** | Shanghai University of TCM (244 papers) |
| **Lotka's α (D2)** | 2.63 (super-Lotka, R²=0.957) |
| **Bradford multiplier n** | 8.89 (zone1:zone2:zone3 = 25:224:1976) |

---

## Timeline

| Day | Status | Description |
|---|---|---|
| Day 0 | ✅ | Environment setup, repo init |
| Day 1 | ✅ | 4-DB acquisition (~17k raw records) |
| Day 2 | ✅ | Integration & deduplication → 9,754 unique |
| **Day 3** | ✅ | Annual + Geographic + Institutions + Authors + Journals + Citations |
| Day 4-6 | Pending | PRISMA, keyword co-occurrence, topic modeling |
| Day 7-10 | Pending | LLM mechanism extraction (Claude API) |
| Day 11-14 | Pending | Pharmacology network |
| Day 15-21 | Pending | Manuscript drafting + submission |

---

## Day 3 Complete Deliverables

### Tables (12)
- `table_01_annual_publications.csv` — Annual stats 2005-2025
- `table_01b_period_statistics.csv` — 4-phase growth CAGR
- `table_02_country_ranking.csv` — Top 30 countries with coverage stats
- `table_02b_collaboration_matrix.csv` — Bilateral country pairs (1,012)
- `table_02_country_coverage.csv` — Country attribution audit
- `table_03_top_institutions.csv` — Top 30 institutions (ROR-fixed)
- `table_03_top_authors.csv` — Top 30 D2 authors (FINI+Institution)
- `table_03b_lotka_stats.csv` — Lotka's law fit (D2: α=2.63, R²=0.957)
- `table_04_top_journals.csv` — Top 30 journals + JCR 2024 IF
- `table_04b_bradford_zones.csv` — Bradford zone stats (n=8.89)
- `table_04_all_journals.csv` — All 2,225 journals with zones
- `table_05_top_cited_papers.csv` — Top 30 most-cited papers
- `table_05b_citation_stats.csv` — Descriptive stats + h-index

### Figures (10)
- `figure_02_annual_trend.png` — Annual + 5yr MA + period CAGR
- `figure_03_top_countries.png` — Top 20 countries bar chart
- `figure_04_country_collab_network.png` — VOSviewer 6-cluster network
- `figure_04b_country_collab_density.png` — VOSviewer density heatmap
- `figure_05_top_institutions.png` — Top 20 institutions (region-colored)
- `figure_06a_top_authors.png` — Top 20 D2 authors
- `figure_06b_lotka_law.png` — Lotka log-log plot (α=2.63)
- `figure_07a_top_journals.png` — Top 20 journals + Bradford zone colors
- `figure_07b_bradford_law.png` — Bradford cumulative log-log
- `figure_08a_citation_distribution.png` — Hist + Pareto/h-index
- `figure_08b_citations_by_year.png` — Citation scatter by year

### Scripts (12 in 03_descriptive_analysis/)
- `01_annual_trends.py`
- `02_country_extraction.py`, `03_country_ranking.py`, `04_export_vosviewer.py`
- `05a_extract_unique_affiliations.py` (21,367 unique)
- `05b_ror_api_matcher.py` (ROR 15h41min, 98.7% match)
- `05b2_postprocess_ror.py` (706 manual rule fixes)
- `05b3_catchall_detector.py` (323 automatic catch-all fixes)
- `05c_standardize_institutions.py`, `05d_institution_ranking.py`
- `06a_author_normalize.py` (D1 FINI)
- `06c_author_d2_upgrade.py` (D2 FINI+Institution)
- `06d_author_ranking_lotka_d2.py`
- `07_journal_bradford.py`
- `08_citation_hindex.py`

### Data files (data/processed/)
- `integrated_corpus.parquet` (9,438 main) + `_partial2026.parquet` (316)
- `country_lookup.parquet`, `country_collaboration_pairs.parquet`
- `unique_affiliations.parquet` (21,367)
- `affiliation_record_map.parquet` (24,116)
- `ror_results.parquet` (raw 21,341 from ROR API)
- `ror_results_fixed.parquet` (post-processed, 20,555 matched)
- `ror_postprocess_audit.csv` (706 manual fixes log)
- `ror_catchall_audit.csv` (catch-all detector results)
- `institution_lookup.parquet` (8,180 records with insts)
- `author_lookup.parquet` (16,094 D1 FINIs)
- `author_lookup_d2.parquet` (43,472 D2 IDs)
- `author_record_map.parquet` + `_d2.parquet`
- `journal_if_template.csv` (Top 30 with JCR 2024 IF, manually verified)

---

## Locked Methodological Decisions

| ID | Decision |
|---|---|
| A1 | DOI-less records retained, fuzzy-matched via title+year+first_author |
| B1 | OpenAlex-exclusive records re-filtered with WoS-equivalent 3-block boolean |
| C-Standard | Fuzzy threshold ratio>=95 |
| **D1** | Author disambiguation: FINI only (ORCID lost in Day 2 normalize) |
| **D2** | **D1 + Institution-based FINI partition (final method)** |
| E1+ | Country: OpenAlex inst > regex > reprint fallback |
| F1 | Journal IF: JCR 2024 manual lookup (Top 30, done) |
| **G2** | Institution standardization: ROR API + post-processing |
| H1 | Catch-all detection: 5-criterion algorithm, ≥2 triggers flag |

### Political Compliance (Day 3)
- "Chinese Mainland" / "Hong Kong (China)" / "Taiwan (China)" / "Macao (China)"
- All HK/MO/TW are distinct analytical units but labeled with (China)
- Methods note: WHO/UN convention

---

## Engineering Lessons Learned

### Day 2
1. `"C1".isalpha()` returns False — must check per-character
2. Day 2 loaders over-pruned affiliations — Day 3 patched + re-ran
3. WoS C1 split on \n; Scopus on ; ; OpenAlex pre-structured

### Day 3
1. **ORCID was lost in Day 2 normalize** — D1+ degraded to D1 (FINI only). 
   FINI alone fails for Chinese surnames → D2 upgrade required (FINI+Institution).
2. **ROR API 98.7% match rate ≠ 98.7% accuracy** — Chinese TCM institutions had 
   ~38% systematic misrouting due to ROR's short-name preference.
3. **Score-based filtering insufficient for ROR errors** — high-score matches still 
   wrong; needed pattern-based post-processing.
4. **ROR catch-all buckets confirmed**: Shanghai University (006teas31), Israel Cancer 
   Association USA (02ga6zq31), People's Hospital of Rizhao, HEC Pharm, 
   State Key Lab Digital Medical Eng.
5. **Lesson — always audit external APIs on 10-50 sample before production runs**. 
   15h ROR run could have been 4-6h if pre-audited.
6. **Automated catch-all detector with 5 criteria** works well (3/91 detected, 
   no false positives in Top 10 spot-check).

---

## Headline Results (for paper §3)

### §3.1 Annual Trends
- CAGR 5.3%, 4-phase pattern, 2025 peak (737), 2024 acceleration (+34.2%)
- PubMed MeSH indexing lag explains 2023 dip

### §3.2 Geographic Distribution
- 84.5% country coverage
- Chinese mainland 54.1%, US 13.7%, India 6.7%
- China aggregated (mainland + HK + MO + TW): 61.4%
- 18.3% multi-country collaboration rate overall
- HK/MO 67-89% intl collaboration vs CN mainland 17.5%
- 6 distinct collaboration clusters

### §3.3 Institutions
- 8,180/9,754 (83.9%) records with extractable institutions
- Top 1: Shanghai University of TCM (244)
- 19/20 of top institutions are Chinese mainland
- CUHK has highest first-author rate (81.9%) and intl rate (41.7%) in Top 30
- Naval Medical University: highest AvgCit in Top 20 (43.3)

### §3.4 Authors (D2 disambiguation)
- 43,472 distinct D2 IDs (vs 16,094 D1) — 2.70x splitting
- Top 1: duan_j @ NUCM (40 papers)
- 5 King Saud University researchers in Top 30
- Efferth (Mainz) and Lee (Kyungpook) represent European/Korean leadership
- Lotka α=2.63 (super-Lotka), R²=0.957
- 85.7% one-paper authors, 0.43% with ≥10, 0.099% with ≥20

### §3.5 Journals (Bradford)
- 9,687 with journal info, 2,225 unique journals
- Top 3: JEP (682), Frontiers Pharmacol (249), Phytomedicine (205)
- Bradford zones: 25 | 224 | 1,976 (multiplier n=8.89)
- Top 30 Q distribution: Q1=13, Q2=8, Q3=4, Q4=2, unranked=3
- Mean IF = 3.69, Median = 3.80
- 53.3% of Top 30 publications in Q1 journals

### §3.6 Citations
- 242,765 total citations, mean=24.9, median=10
- **Corpus h-index = 171**
- 425 papers (4.4%) with ≥100 citations
- Top-cited: Cabrera 2006 Green Tea Review (1,669)
- 21.7% zero-cited (normal for 20-yr corpus)

---

## NEXT STEPS (Day 4+)

### Block 6 (immediate, before next session)
- [ ] Update master_progress.md (this file)
- [ ] Git commit + push Day 3 work
- [ ] Backup ror_results_fixed.parquet (irreproducible without 15h API run)

### Day 4 — PRISMA flow diagram + keyword analysis
- Build PRISMA 2020 flow diagram with N at each stage
- Author keywords + Keywords Plus extraction
- Keyword frequency Top 50 + co-occurrence network (VOSviewer)
- Estimated 4-5h

### Day 5-6 — Topic modeling
- BGE-M3 multilingual embeddings on title + abstract
- HDBSCAN clustering, topic labels via TF-IDF top terms
- Topic evolution over time (3-period split)
- Estimated 6-8h

### Day 7-10 — LLM mechanism extraction
- Claude Sonnet API extraction of HDI mechanisms (CYP/transporter level)
- 300-500 records randomly sampled, prompt-engineered for structured output
- Validation: manual coding on 50 records
- Estimated 12-15h (mostly API runtime)

### Day 11-14 — Network analyses
- Herb-drug interaction network from LLM extractions
- Mechanism-target heatmap
- Country-level temporal evolution
- Estimated 8-10h

### Day 15-21 — Manuscript drafting + revision + submission
- §1 Introduction, §2 Methods, §3 Results, §4 Discussion
- Figures finalization (300 dpi, color-blind safe palette)
- Submit to Frontiers in Pharmacology (preferred) or Pharmacological Research
- Estimated 15-20h

---

## RESUME INSTRUCTIONS (for new Claude conversation)

> **Use this when starting a new chat to continue work:**
I'm continuing the TCM-HDI bibliometric project. Day 3 is complete (all blocks).
Please read docs/master_progress.md for full context.
Repo: D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026
Latest commit: [will be filled after Day 3 commit]
Now starting Day 4: PRISMA flow + keyword analysis + co-occurrence networks.
Working language: 中文 with English code/output.
---

## Outstanding Issues (Day 4+ to address)

1. **2,225 unique journals** likely contains name variants (J Pharm Sci vs Journal 
   of Pharmaceutical Sciences). Top 30 unaffected; long-tail can be fuzzy-cleaned 
   in Day 14 if needed.
2. **Manual ROR ID verification deferred** — 19 hardcoded ROR IDs in 05b2 based on 
   memory; should verify against ror.org for strict Methods compliance.
3. **9,754 records have 0 affiliations from PubMed** — structural limitation, 
   noted in Methods.
4. **D2 still imperfect** — position-aware institution assignment uses first 
   institution if author position > inst count (heuristic).

---

## Day 4 (May 14-15, 2026): PRISMA + Keyword Analysis ✅

**Status**: Complete  
**Duration**: ~5 hours hands-on work  
**Deliverables**: 6 scripts + 8 data files + 3 tables + 6 figures + 3 VOSviewer files

### Block 1: PRISMA 2020 Flow Diagram ✅

**Script**: `04_keyword_topic/01_prisma_flow_diagram.py`  
**Output**: `results/figures/figure_01_prisma_flow.png`

PRISMA-compliant flow diagram constructed programmatically (matplotlib) for full reproducibility:
- Identification: 4 DBs (WoS 3,091 / Scopus 7,181 / OpenAlex 2,513 / PubMed 3,867 → 16,652)
- Screening: DOI dedup -6,850 → 9,802 → fuzzy -266 → 9,536
- Eligibility: OpenAlex precision filter -98 → 9,438
- Included: 9,438 (main 2005-2025) + 316 (partial 2026) = 9,754 total

### Block 2: Keyword Extraction + Standardization ✅

**Scripts**: `02a_extract_keywords.py`, `02b_thesaurus_suggest.py`, `02c_apply_thesaurus.py`

**Critical methodological discovery**: Initial inspection revealed that the `keywords_plus` field in Scopus-origin records contained mixed indexing content (mean 58 keywords/record, range 1-334, including MeSH descriptors, chemical entities, and Scopus indexing terms). WoS Keywords Plus was confirmed clean (median 10, range 1-13). **Decision D'**: drop Scopus `keywords_plus` from main analysis; retain author keywords + WoS Keywords Plus + MeSH terms (supplementary).

**Standardization pipeline**:
1. Basic normalization: lowercase, dash unification, MeSH-modifier removal
2. Thesaurus construction (v3 clean rewrite): 38 KNOWN + 113 fuzzy = 151 variant→canonical mappings
3. Stopword filter: 16 generic MeSH/study-type descriptors (humans, animals, male, female, rats, mice, etc.)
4. Semantic blacklist: prevent false-positive merges (expression≠depression, lc-ms/ms≠uplc-ms/ms, cyp3a4≠cytochrome p450)
5. Transitive closure: variants chain to final canonical in single step

**Final keyword corpus**: 21,083 unique standardized keywords across 72,457 (record, keyword) pairs; 8,244 records with ≥1 keyword (84.5% coverage); mean 8.8 keywords/record.

### Block 3: Top 50 Keywords + Figure 9 ✅

**Script**: `04_keyword_topic/03_top_keywords_figure9.py`  
**Outputs**: `table_06_top_keywords.csv`, `figure_09a_top_keywords.png`, `figure_09b_keywords_by_source.png`

**Top 5 keywords** form a coherent terminology pyramid:
- traditional chinese medicine (n=1,671, 17.1%)
- herb-drug interaction (1,370, 14.1%)
- pharmacokinetics (1,284, 13.2%)
- drug interaction (635, 6.5%)
- cytochrome p450 (629, 6.5%)

**Five-layer ontology** emerges from Top 50:
1. Foundational terminology: TCM, HDI, pharmacokinetics
2. Interaction mechanisms: CYP450, P-gp, drug synergism
3. Computational methodologies: network pharmacology (n=385), molecular docking (199), metabolomics (160)
4. Biological endpoints: apoptosis, cancer, oxidative stress, hepatotoxicity
5. Model herb-drug case studies: St. John's wort, warfarin, ginkgo

**Source composition**: consistent between full corpus and Top 30 (no source bias):
- Author Keywords: 50.9% / 50.0%
- WoS Keywords Plus: 31.8% / 32.3%
- MeSH Terms: 17.4% / 17.7%

### Block 4: Keyword Co-occurrence Network (VOSviewer) ✅

**Script**: `04_keyword_topic/04_keyword_cooccurrence.py`  
**Outputs**: `keyword_cooccur_map.txt`, `keyword_cooccur_network.txt`, `figure_10_keyword_cooccur.png`

**Network statistics**: 100 nodes, 1,485 edges, density 0.300, max weight 325, min weight 5.

**VOSviewer parameters**: Association strength normalization; attraction=2, repulsion=0; resolution=0.80; min cluster size=5.

**Top co-occurrence pairs**:
1. drug synergism + TCM (325)
2. herb-drug interaction + pharmacokinetics (310)
3. cytochrome p450 + herb-drug interaction (205)
4. drug interaction + TCM (171)
5. herb-drug interaction + TCM (167)

**Five thematic clusters** identified:
- 🔴 Red (ADME core): CYP450, P-gp, pharmacokinetics, inhibition, UPLC-MS/MS, drug-drug interaction
- 🔵 Blue (TCM oncology): traditional chinese medicine, drug synergism, apoptosis, cell line tumor
- 🟢 Green (CAM clinical safety): alternative medicine, dietary supplements, cancer, safety, double-blind
- 🟡 Yellow (in silico mechanisms): network pharmacology, molecular docking, oxidative stress, hepatotoxicity, metabolomics
- 🟣 Purple (classic herb-drug pairs): warfarin, st johns wort, grapefruit juice, ginkgo biloba

### Block 5: Keyword Temporal Evolution ✅

**Script**: `04_keyword_topic/05_keyword_evolution.py`  
**Outputs**: `table_07_keyword_evolution.csv`, `figure_11a_keyword_evolution_heatmap.png`, `figure_11b_rising_declining_keywords.png`

**Three research paradigms identified**:

| Period | n records | Dominant paradigm |
|---|---|---|
| Early (2005-2011) | 1,642 | Case-report + supplementary medicine |
| Middle (2012-2018) | 2,644 | ADME mechanism (Phase I + ABC transporters) |
| Recent (2019-2025) | 3,677 | Computational pharmacology (network + docking) |

**Top 5 RISING keywords (Δ% Recent - Early)**:
- network pharmacology: +9.27% (0.1% → 9.3%, **91-fold increase**)
- molecular docking: +4.52% (0.2% → 4.7%, 25-fold)
- pharmacokinetics: +3.77% (11.8% → 15.6%)
- mechanism: +3.43% (1.0% → 4.4%)
- drug-drug interaction: +2.55% (0.9% → 3.4%)

**Top 5 DECLINING keywords**:
- herb-drug interaction (as keyword): -16.78% (terminology specialization, not topic decline)
- drug interaction: -7.90%
- phytotherapy: -6.93%
- plant extract: -6.18%
- dietary supplements: -4.55%

**Discussion-ready narrative**: Field underwent a **paradigm shift around 2018** from case-pair clinical observation toward systems-level in silico mechanism prediction. ADME terminology (CYP450, P-gp) persists but is now embedded within network pharmacology frameworks rather than studied as standalone targets.

### Day 4 Engineering Lessons

1. **Scopus `keywords_plus` is not WoS Keywords Plus**: Scopus exports indexing terms (median 58/record) including MeSH/chemical/clinical descriptors mixed with author terms. WoS Keywords Plus is algorithmically curated (median 10/record). **Always audit DB field semantics before assuming equivalence across exports.**

2. **Fuzzy matching needs semantic blacklist**: RapidFuzz `token_sort_ratio >= 88` catches `depression`↔`expression` (different concepts, similar characters). Manual SEMANTIC_BLACKLIST is mandatory.

3. **Thesaurus needs transitive closure**: `herbal medicines` → `herbal medicine` → `traditional chinese medicine` must resolve in 1 step to avoid multi-hop variants. Implementation: `while s in known_map and s not in visited: s = known_map[s]`.

4. **Bidirectional fuzzy pairs need explicit dedup**: For variants A↔B, naive collection produces 2 entries (A→B with canonical_n=X; B→A with canonical_n=Y). Solution: sort tuple `(min, max)` as unique key, then assign canonical = max(record count).

5. **PRISMA 2020 figure construction**: matplotlib `FancyBboxPatch` + manual coordinate placement gives publication-ready output in 30min vs 1h for R package PRISMA2020Flowdiag, with no R dependency.

---
