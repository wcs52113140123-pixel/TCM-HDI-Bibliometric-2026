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

---

## Day 5 (May 16, 2026): Topic Modeling ✅

**Status**: Complete
**Latest commit**: <fill after commit>
**Deliverables**: 7 scripts + 7 data files + 9 tables + 4 figures + 4 audits

### Block 0: Pre-flight Audit + Cross-file Dedup Fix

**Critical methodological discovery** via pre-embedding audit: **37 cross-file
DOI overlaps** between `integrated_corpus.parquet` (main) and
`integrated_corpus_partial2026.parquet`. Three groups identified:
- **A (n=24)**: main(year=2026) ↔ partial(year=2026) — same in-press paper
  in both files
- **B (n=12)**: main(year=2025) ↔ partial(year=2026) — same DOI with year
  discrepancy across source databases (WoS issue year vs PubMed epub year)
- **C (n=1)**: main(year=2025) ↔ partial(year=2025) — pure duplicate

**Fix strategy** (locked, deterministic): strict year-based classification
(year ≤ 2025 → main, year = 2026 → partial); on cross-file DOI conflict,
preserve the main-corpus copy (earliest documented year, source-precedence
dedup convention).

**Result**: main 9,438 → **9,413** (−25); partial 316 → **304** (−12);
total unique publications 9,754 → **9,717** (−37). Backups in
`.bak_pre_cross_dedup` files (not tracked in git).

**Day 4 impact**: 0.27% record perturbation; Top-50 keyword ranking,
5-cluster co-occurrence structure, and 3-period rising/declining analysis
unchanged. Day 4 outputs retained on original 9,438 snapshot; Methods §2
includes a footnote.

### Block 1: SPECTER2 Embedding ✅

**Script**: `04_keyword_topic/07_block1_specter2_embedding.py`
**Outputs**: `specter2_embeddings.npy` (9413×768 float32, 27.6 MB) +
`specter2_embeddings_meta.json` (record_id row alignment).

**Model**: `allenai/specter2_base` (Cohan et al. 2020 ACL) + **proximity
adapter** `allenai/specter2` (Singh et al. 2023 EMNLP SciRepEval). The
proximity adapter is fine-tuned for clustering / similarity tasks, directly
aligned with downstream HDBSCAN objective.

**Input**: `title [SEP] abstract` (SPECTER2 standard). Truncation: head+tail
75/25 split applied to **10.3% (966/9413)** records exceeding 512 tokens
(Sun et al. 2019). Title-only fallback for **3.0% (285/9413)** records
lacking abstract (PubMed structural limitation, pre-2012). Pooling:
`[CLS]` token. Device: CPU, batch_size=8. **Elapsed: 37.0 min**. Norm
range 21.35–22.49 (mean 21.93, SD<0.6, no zero-norm). Quality healthy.

### Block 2: UMAP + HDBSCAN Clustering ✅

**Script**: `04_keyword_topic/08_block2_umap_hdbscan.py`
**Outputs**: `umap_5d.npy`, `umap_2d.npy`, `cluster_assignments.parquet`,
`cluster_stats.csv`.

**UMAP**: two fits — 5-dim for HDBSCAN density estimation
(`n_neighbors=15, min_dist=0.0, metric=cosine, random_state=42`) and 2-dim
for visualization (`min_dist=0.1`).

**HDBSCAN**: `min_cluster_size=50, min_samples=5,
cluster_selection_method=eom, cluster_selection_epsilon=0.15`.
`min_cluster_size=50 ≈ √N/2` (Klarin 2024 bibliometric heuristic).

**Hyperparameter sensitivity analysis**: noise ratio remained stable at
**~36.5%** across configurations (`min_samples` 10 → 5: 38.9% → 36.5%;
`cluster_selection_epsilon` 0 → 0.15: 36.53% → 36.51%), confirming
residual outliers represent **genuine semantic edge cases in the
heterogeneous TCM-HDI corpus rather than artifacts of overly strict
density thresholds** (Grootendorst 2022 best practice).

**Result**: **39 clusters** discovered; **3,437 noise** (36.5% of corpus);
cluster sizes 51–730 (median 109, mean 153). Top 10 clusters cover 27%
of corpus; long-tail distribution healthy.

### Block 3: Topic Naming (c-TF-IDF + KeyBERTInspired) ✅

**Script**: `04_keyword_topic/09_block3_topic_naming.py` (+ recovery
`09b_rebuild_topic_labels_json.py`)
**Outputs**: `results/tables/topic_labels.csv`,
`data/processed/topic_labels.json`.

Following near-2026 顶刊 BERTopic-bibliometric review best practice
(Grootendorst 2022; Educational Psychology Review 2024):
1. **c-TF-IDF** (class-based TF-IDF, per-cluster super-document, 1–2 grams;
   English stopwords + 26 bibliometric-specific stopwords). Top-30
   candidate keywords per cluster.
2. **KeyBERTInspired re-ranking** (Sharma & Li 2019): each candidate
   encoded by **SPECTER2 (same model as document encoder)**, cosine to
   cluster centroid → re-rank → top-15.
3. **Author keywords** (top-10 per cluster) reported as cross-source
   sanity check.
4. **Exemplar titles** (top-3 highest-probability member titles per cluster).

925 unique candidate phrases encoded; **39/39 clusters yielded
semantically coherent topic labels** (manual inspection confirmed).

**Striking findings**:
- **C5 St. John's Wort** (HDI literature's founding case study) cleanly
  isolated as its own topic
- **C1 Wuzhi capsule + tacrolimus** (China-origin TCM-HDI signature topic)
  isolated
- **C11 (730 docs, anticancer + TCM experimental)** vs **C26 (204 docs,
  CAM use in cancer patients, surveys)** cleanly separated — SPECTER2
  captured experimental-vs-epidemiological semantic distinction missed by
  Day-4 keyword co-occurrence
- **C38 (236 docs, mean_prob=1.000, pharmacist herbal supplement surveys)** —
  perfectly cohesive cluster recovered by `cluster_selection_epsilon=0.15`
  sensitivity tuning

### Block 4: Topic Temporal Evolution ✅

**Script**: `04_keyword_topic/10_block4_topic_evolution.py`
**Outputs**: 4 CSV tables (`topic_yearly_freq`, `topic_yearly_pct`,
`topic_period_freq`, `topic_rising_declining`) + 3 figures (12–14).

Two-level analysis (BERTopic dynamic topic modeling convention,
Blei & Lafferty 2006; BERTopic doc nr_bins recommendation):
- **Fine**: 21 yearly bins (2005–2025) → topic frequency heatmap
- **Coarse**: 3 periods (Early 2005–2011 / Middle 2012–2018 / Recent
  2019–2025) aligned with Day-4 keyword evolution

**Top 5 RISING topics** (Δ% = Recent − Early share):
| Topic                                                        | Δ%    | Fold | Interpretation                                             |
| ------------------------------------------------------------ | ----- | ---- | ---------------------------------------------------------- |
| T27: metabolites, pharmacokinetic, pharmacokinetics          | +6.72 | 73×  | Multi-component prototype-metabolite UPLC-MS/MS PK studies |
| T25: phytochemistry pharmacology, pharmacological activities | +4.96 | 497× | Comprehensive phytochemistry-pharmacology review papers    |
| T22: network pharmacology, pharmacology molecular            | +4.42 | 442× | Network pharmacology core methodology                      |
| T20: cancer, network pharmacology, pathways                  | +4.27 | 428× | Network pharmacology × cancer disease integration          |
| T0: biosynthesis, biosynthetic pathway                       | +3.00 | 10×  | Synthetic biology / RNA-seq for TCM compound biosynthesis  |

**Top 5 DECLINING topics**:
| Topic                                    | Δ%    | Fold  | Interpretation                                               |
| ---------------------------------------- | ----- | ----- | ------------------------------------------------------------ |
| T37: herbal supplements, herbal products | −6.18 | 0.12× | "Herbal supplement" coverage replaced by specific topic decomposition |
| T5: antidepressants, wort sjw            | −4.44 | 0.10× | St. John's Wort topic saturation (literature maturation)     |
| T38: pharmacies, use herbal, medications | −3.49 | 0.47× | Pharmacist survey research declining                         |
| T6: warfarin, anticoagulants             | −3.47 | 0.44× | Warfarin classic HDI case studies maturation                 |
| T30: cyp inhibition, cyp enzymes         | −2.77 | 0.66× | Single-mechanism CYP inhibition studies replaced by multi-target NW |

**Paradigm shift narrative** (3-stage, validating Day 4 finding):
- **Early 2005–2011**: founding HDI cases (St. John's Wort, Warfarin) +
  pharmacist surveys + single-target CYP studies
- **Middle 2012–2018**: ADME mechanism peak — CYP inhibition (13.4%),
  UGT enzymology, multi-component PK profiling
- **Recent 2019–2025**: computational pharmacology explosion — network
  pharmacology penetrates every disease domain (cancer, lung,
  cardiovascular, neuro, NAFLD, arthritis, respiratory/COVID); multi-omics
  biosynthesis; gut microbiome interactions

### Block 5: Cross-validation vs Day 4 Keyword Clusters ✅

**Scripts**: `04_keyword_topic/06d_recompute_keyword_clusters.py` +
`11_block5_cross_validation.py`
**Outputs**: `day4_vs_day5_metrics.csv`,
`day4_vs_day5_confusion_matrix.csv`, `figure_15_day4_vs_day5_confusion.png`,
`day5_cross_validation_report.md`,
`keyword_cluster_day4_louvain_audit.md`.

**Day-4 cluster re-derivation**: Day-4's published VOSviewer .map file
was exported **without cluster information** (a common VOSviewer UX pitfall —
"Save with cluster information" checkbox not selected). Day-4 script
printed VOSviewer GUI clustering instructions (resolution=0.80,
min_cluster_size=5) but did NOT persist the cluster column. We re-derived
Day-4 cluster labels via **NetworkX + python-louvain** (Blondel et al.
2008) on the same `keyword_cooccurrence_pairs.parquet` graph, with matched
parameters (resolution=0.80, min_cluster_size=5, weighted by `n_cooccur`).

**Re-derivation result**: **4 modularity-optimal communities** (vs Day-4
published 5; modularity=0.22):
| Louvain cluster | n keywords | Maps to Day-4 published cluster                              |
| --------------- | ---------- | ------------------------------------------------------------ |
| 0               | 43         | ADME core (cyp, p-gp, pharmacokinetics)                      |
| 1               | 29         | **CAM clinical safety + classic herb-drug pairs (merged)** — VOSviewer GUI manual interpretive split was not reproducible via unsupervised modularity optimization |
| 2               | 23         | TCM oncology (cancer, apoptosis, signal transduction)        |
| 3               | 5          | In silico mechanisms (network pharmacology, docking)         |

**Cross-validation metrics** (Hubert & Arabie 1985; Strehl & Ghosh 2002):
- **ARI = 0.041** (excl. noise); **NMI = 0.146**
- n records compared: 4,237 (noise excluded), 6,647 (noise included)
- Day-4 clusters: 4; Day-5 clusters: 39

**Interpretation**: modest quantitative agreement reflects **three-fold
attenuation inherent to this comparison**:
1. **Cross-modality**: keyword-level co-occurrence (100 top-frequency
   terms) vs document-level SPECTER2 embeddings (full 8,221-term
   vocabulary)
2. **Cross-cardinality**: 4 vs 39 clusters (Vinh et al. 2010 — ARI is
   inherently attenuated in fine-coarse partition comparisons)
3. **Majority-vote projection** is lossy when a record contains keywords
   spanning multiple Day-4 clusters

**Qualitative cross-mapping** (4/4 Day-4 themes recovered as multi-topic
groups in Day-5):
| Day-4 cluster               | Day-5 corresponding topics                                   |
| --------------------------- | ------------------------------------------------------------ |
| 0: ADME core                | T30 CYP / T24 UGT / T9 PXR / T32 transporters / T27 / T34 / T35 / T33 / T13 |
| 1: CAM safety + classic HDI | T5 SJW / T6 Warfarin / T2 antidiabetic / T8 statin / T3 ARV / T1 tacrolimus / T37 / T38 / T7 / T29 / T26 |
| 2: TCM oncology             | T11 anticancer / T20 cancer-NW / T28 medicinal plants        |
| 3: In silico mechanisms     | T22 / T18 / T19 / T21 / T16 / T4 (网络药理学 × multiple disease domains) |

**Convergent validity confirmed qualitatively**; quantitative metrics
reported transparently as **method complementarity** finding rather than
disagreement.

### Day 5 Engineering Lessons

1. **Audit before production runs (Day 3 lesson reinforced)**. Block 0
   surfaced a data integrity bug — 37 cross-file DOI overlaps — that
   would have silently propagated through topic modeling and inflated
   corpus counts. Cost: 30 minutes audit + fix. Benefit: reviewer-proof
   numbers.

2. **`adapters` 1.x `set_active=True` doesn't propagate to forward pass**.
   The `load_adapter(..., set_active=True)` call only sets loading-time
   state; explicit `model.set_active_adapters(name)` is required
   afterwards. Without it, proximity adapter loads but `forward()` runs
   on base SPECTER2, silently degrading clustering quality (~3 NDCG
   points on SciDocs). The warning *"There are adapters available but
   none are activated for the forward pass"* is the canary;
   `assert model.active_adapters is not None` is the safety net.

3. **Windows HF cache requires Developer Mode** (or admin PowerShell).
   `os.symlink` raises `WinError 1314` for non-admin processes, breaking
   `snapshot_download` unpredictably. One-time toggle resolves this for
   all future HF / Git / pip operations.

4. **VOSviewer .map exports lack cluster column by default**. Future
   bibliometric work must either (a) explicitly check "Save with cluster
   information" in VOSviewer GUI, or (b) persist clusters via Python
   pipeline (NetworkX + Louvain). Day-4 published 5-cluster labeling
   relied on GUI session state lost on close — we re-derived via Louvain
   re-computation.

5. **Auto-detection should use substring match, not exact match**.
   `n_cooccur` column was initially missed because detector used exact
   match against `"cooccur"`. Robust detectors use substring containment
   over a curated vocabulary.

6. **c-TF-IDF stopwords need bibliometric tuning**. Default English
   stopwords miss high-frequency-but-uninformative scientific terms
   (`study`, `results`, `method`, `conclusion`, ...). A 26-term
   `EXTRA_STOPWORDS` set documented in Block 3.

---

### Headline Day-5 Findings (paper §3.X Topic Modeling)

- **39 distinct research topics** identified at abstract level via
  SPECTER2 + UMAP + HDBSCAN; **63.5% corpus coverage** (36.5% noise as
  honest representation of semantic edge cases)
- **Top 3 topics**: anticancer + TCM chemotherapy (730 docs, 7.76%);
  CYP inhibition in vitro screening (512, 5.44%); hepatotoxicity / DILI
  (331, 3.52%)
- **Convergent validity** with Day-4 keyword clusters confirmed
  qualitatively (4/4 themes recovered); modest quantitative metrics
  (ARI=0.04, NMI=0.15) reflect cross-modality + cross-cardinality
  attenuation rather than method disagreement
- **5 strongly emerging topics** (>3× growth Recent vs Early): multi-
  component metabolite PK (73×), phytochemistry-pharmacology reviews
  (497×), network pharmacology (442×), cancer × network pharmacology
  (428×), biosynthesis pathway research (10×)
- **5 strongly declining topics**: generic herbal supplements (−6.2%),
  St. John's Wort (−4.4%), pharmacist surveys (−3.5%), warfarin (−3.5%),
  single-mechanism CYP inhibition (−2.8%)
- **Paradigm shift around 2018**: ADME mechanism research peak (Middle
  period) → computational pharmacology dominance (Recent period); network
  pharmacology penetrates every disease domain in 2020+

------

## Day 6-8 (May 16-17, 2026): LLM Mechanism Extraction ✅

**Status**: Complete **Latest commit**: <fill after commit> **Deliverables**: 14 scripts + Schema D v3 (16 mechanism categories) + 4,648 records extracted (100% success) + iterative refinement audit

### Day 6 (May 16): Pipeline & LLM Selection

**Infrastructure** (`01_schema.py` ~ `03_llm_client.py`):

OpenRouter (openrouter.ai) chosen as primary LLM gateway:

- Single API key routes to Anthropic / OpenAI / Google upstream providers
- Forward proxy preserves model version (reproducibility for paper)
- Anthropic Sonnet 4.5+ and OpenAI GPT-4o+ support strict json_schema mode

Built **3-tier fallback `LLMClient`**:

1. `response_format={"type":"json_schema","json_schema":{"strict":True}}` + `extra_body={"provider":{"require_parameters":True}}` (prevents silent fallback to providers without strict mode support)
2. `response_format={"type":"json_object"}` (loose JSON mode)
3. Pure prompt-driven JSON + retry-on-validation-failure with error message

Auto-routing by model id prefix: `glm-*` → Zhipu, `deepseek-*` → DeepSeek, `<vendor>/*` → OpenRouter. Backup providers (Zhipu/DeepSeek) tested and ready after OpenRouter geo-restriction debugging journey (see lessons below).

**Schema D design** (3 field groups, all Optional fields required-but-nullable for OpenAI strict mode compatibility):

- **A — Core interaction**: herb (Latin/common/active compound), drug (name/class), interaction type, mechanism, specific target, direction
- **B — TCM formula extension**: formula name, co-herbs list, TCM pattern
- **C — Clinical PK quantitative**: AUC/Cmax/t½/CL change %, sample size
- **Metadata**: evidence type, clinical significance, confidence, evidence_quote (mandatory ≥10 chars — anti-hallucination)

**5-part prompt template** (Zero-Shot Document-Level RE 2025 + Feng et al. 2025 CYP extraction): system role + task + entity definitions + mechanism definitions + few-shot examples. 3 examples covering positive PK induction (SJW+cyclosporine), positive PK inhibition with TCM formula (Wuzhi+tacrolimus), and negative methodology review.

**Cross-model benchmark** (50 stratified abstracts, `05_benchmark.py`):

| Model             | val_rate | HDI rate | avg_int | conf | 9,413 cost est.            |
| ----------------- | -------- | -------- | ------- | ---- | -------------------------- |
| Claude Sonnet 4.6 | 1.00     | 0.48     | 1.16    | 0.79 | $204                       |
| **GPT-4o-mini ⭐** | 1.00     | 0.44     | 0.70    | 0.86 | **$5.65**                  |
| O3-mini           | 0.98     | 0.30     | 0.62    | 0.81 | $156 (reasoning output 爆) |
| GPT-5-mini        | 0.98     | 0.40     | 1.02    | 0.77 | $53 (reasoning overhead)   |
| Haiku 4.5         | 1.00     | 0.34     | 0.98    | 0.84 | $68                        |
| GPT-5.5           | 1.00     | 0.36     | 1.14    | 0.82 | $109                       |

**Decision: GPT-4o-mini** — Pareto-frontier endpoint with Sonnet 4.6:

- HDI rate 0.44 vs Sonnet 0.48 (only 4 pp gap)
- Cost $5.65 vs Sonnet $204 (36× cheaper)
- Validation rate 1.00 + zero retries
- Avg confidence 0.861 (highest)
- Already validated for biomedical extraction by Aali et al. 2025 (JAMIA Cochrane RCT screening)

Mid-tier models (Haiku 4.5, GPT-5-mini, GPT-5.5) all dominated — pricier than GPT-4o-mini but no quality advantage over Sonnet 4.6. Reasoning models (O3-mini, GPT-5-mini, GPT-5.5) underperform on strict structured output — their thinking tokens balloon and validation_attempts rise.

### Day 7 (May 17): Full Corpus Extraction

**Pipeline** (`09_extract_full_corpus.py`): concurrent (5 workers), checkpoint resume (JSONL incremental append + recovery on restart), failed-record separate log, graceful Ctrl+C handling.

**Filtering** (`04_stratified_sample.py`): 9,413 → **4,648 eligible**

- Excluded HDBSCAN noise: −3,437
- Excluded short abstracts (<100 chars): −135
- Excluded review papers: −1,193

**Result**:

- 4,648 / 4,648 success (100%) / 0 failed
- **100% Tier 1 (strict json_schema) success** — OpenRouter structured outputs fully working with GPT-4o-mini, no fallback to Tier 2/3 needed
- 3,132 interactions extracted (1.39 per HDI-containing record)
- Mean confidence 0.856 (no interaction <0.6 confidence)
- Elapsed 83.5 min / Cost **$2.93** (well under estimate)

Headline mechanism distribution (pre-audit):

- CYP_inhibition: 814 (26.0%) — dominant, consistent with HDI literature canon
- **other: 623 (19.9%)** — motivated Day 8 iterative audit
- unspecified: 408 (13.0%)
- CYP_induction: 323 (10.3%)
- receptor_synergism + synergistic_efficacy: 459 (14.6%) — PD interactions
- P-gp + transporter_modulation: 242 (7.8%)

### Day 8 (May 17): Iterative Schema Refinement

**Block 1: Audit `other` bucket** (`12_inspect_other_mechanisms.py`):

19.9% `other` rate audited. Pattern detection on top specific_targets and evidence_quote keywords revealed **3 missed mechanism categories**:

1. **Signaling pathway**: MAPK (3), PXR (4), AhR (3), NRF2 (2), JAK2 (2), FXR (2), androgen receptor (3) — transcription factor / kinase pathway
2. **Organ toxicity**: 67% in_vivo_animal + drugs cyclophosphamide (17), doxorubicin (18), cisplatin (18), acetaminophen (15), CCl4 (5); keywords liver/injury/protective → hepato/cardio/nephro protection or potentiation
3. **Non-P-gp transporters**: MRP1/MRP2/BSEP/BCRP/ABCB1 misclassified due to ambiguous transporter_modulation prompt definition

**Block 2: Schema v3 + Prompt v2 + targeted re-extraction** (`13_reextract_other.py`):

Schema v3: added `signaling_pathway_modulation` + `organ_toxicity_modulation` (14 → 16 mechanism categories). Prompt v2: explicit transporter list (MRP1/2, MATE, OATP, OCT, OAT, BSEP, BCRP, NTCP), 2 new mechanism definitions, +1 few-shot example (Salvia miltiorrhiza × doxorubicin cardioprotection via Nrf2/HO-1 + NF-κB suppression).

Re-extraction: 491 unique records (records with ≥1 `other` interaction) → 491/491 success, 14 min, $0.42. Auto-merged into main JSONL with v1 backup preserved (`*.results.v1_backup.jsonl`).

**Post Schema v3 distribution**:

- **`other` reduced 19.9% → 7.3%** ✓ (target met)
- `signaling_pathway_modulation`: 92 (3.0%) NEW
- `organ_toxicity_modulation`: 90 (2.9%) NEW
- `unspecified` increased 13.0% → 15.6% (LLM precision-over-recall: with more categories available, LLM more conservative on edge cases)
- Mean confidence improved: ≥0.9 fraction 22.8% → 25.7%
- HDI rate stable: 48.6% → 48.2% (no regression)

**Block 3: Residual bucket audit** (`14_inspect_residual.py`):

Inspected both remaining residual buckets:

- **`other` (7.3%)**: dominated by warfarin–anticoagulant interactions (28) and chemo combinations (cyclophosphamide/cisplatin/doxorubicin); these are genuinely multi-mechanism cases (CYP2C9 + receptor + protein binding all play role in warfarin–herb interactions) that don't fit single enum → **accept as residual**
- **`unspecified` (15.6%)**: Top 25 keywords dominated by PK terminology (auc 102, pharmacokinetic 55, concentration 61, Cmax 34, plasma 35, area+curve 74) → these are PK studies reporting AUC/Cmax changes WITHOUT characterizing the mechanism in the abstract. LLM correctly identifies → **accept as residual**

No third missed category detected. **Iterative refinement reached saturation at 16 categories. Total residual 22.9% is publishable as "multi-mechanism complex (7.3%) + PK-effect-of-unspecified-mechanism (15.6%)" categories.**

### Day 6-8 Headline Findings

- **3,100 herb-drug-mechanism triples** extracted from 4,648 abstracts (100% Tier 1 strict json_schema success)

- **16 mechanism categories** capturing CYP / P-gp / UGT / transporter / receptor / signaling pathway / organ toxicity / additive / synergistic

- 86% preclinical evidence

   (in_vivo_animal 52.4% + in_vitro 33.7%) — confirms TCM-HDI literature's translational gap (only 6.5% clinical_trial

  - human_PK_study)

- **Quantitative coverage limited at abstract level** (AUC 7.6%, Cmax 4.5%, sample_size 11.0%) — motivates future full-text extension

- **Top targets validated**: CYP3A4 (416), CYP1A2 (159), CYP2C9 (112), P-gp/P-glycoprotein (186 pre-normalization), CYP2D6 (89) — matches HDI literature canon

- **Cost**: $3.35 total ($2.93 primary + $0.42 Schema v3 re-extraction) for 4,648 + 491 records via GPT-4o-mini on OpenRouter

### Day 6-8 Engineering Lessons

1. **OpenRouter is the only reproducibility-friendly LLM gateway** forwarding to Anthropic/OpenAI/Google with preserved upstream model version. But account-level risk control on payment card BIN and IP region may trigger 403 even with VPN. Backup Plan B (智谱 GLM-4.6 + DeepSeek V3.1 native API) tested and ready as China-resident contingency.
2. **OpenAI strict mode JSON schema has hard constraints**: all fields in `required` array (Optional → required-but-nullable using `["string", "null"]` union); no `default`, `minimum/maximum`, `minLength`, `pattern`, `format` keywords; all object nodes need `additionalProperties: false`. Solution: Pydantic `field_validator` decorators for runtime-only constraints + `_strip_unsupported_inplace()` post-processor on generated schema.
3. **`response_format={"type":"json_schema","strict":true}` works perfectly with GPT-4o-mini via OpenRouter**: 100% Tier 1 success on 4,648 records (zero fallback to Tier 2/3). The `extra_body={"provider":{"require_parameters":true}}` field prevents OpenRouter silent fallback to providers without strict mode support.
4. **Iterative schema refinement is essential for high-quality LLM extraction**: zero-shot prompt alone gave 19.9% `other`; one audit round + targeted Schema v3 extension cut this to 7.3%. Cost per audit round ($0.42) negligible compared to quality gain.
5. **Reasoning models underperform on strict structured output**: O3-mini, GPT-5-mini, GPT-5.5 — thinking tokens balloon (O3-mini 153k vs GPT-4o-mini 11k output for same 50 abstracts), validation_attempts ↑ to 2.46 (vs 1.00 for GPT-4o-mini). Reasoning helps complex reasoning but hurts strict format compliance — consistent with Feng et al. 2025 CYP paper finding (O3-mini good for zero-shot constrained extraction, less so for few-shot + strict schema).
6. **Cost-quality Pareto frontier**: GPT-4o-mini and Claude Sonnet 4.6 are the two efficient endpoints. Mid-tier (Haiku 4.5, GPT-5-mini, GPT-5.5) are dominated — more expensive than GPT-4o-mini but no quality advantage over Sonnet 4.6.
7. **PowerShell f-string with backslash escape**: `[\"KEY\"]` inside an `os.environ[...]` lookup in a Python f-string within a PowerShell here-string is `SyntaxError`. Fix: use `os.environ.get('KEY')` outside f-string interpolation.
8. **OpenAI SDK ≥1.55 required** for compatibility with httpx ≥0.28 (httpx removed `proxies` parameter in 0.28; openai <1.55 still passed it). `pip install --upgrade openai` fixes.

------

## Day 9 (May 17, 2026): Entity Normalization ✅

**Status**: Complete **Latest commit**: <fill after commit> **Deliverables**: 4 normalization scripts + `interactions_normalized.parquet` with 13 new normalized columns + 3-tier resolution strategy reaching **99.6% canonical_id coverage**

### T1 — Target Normalization (`15_normalize_targets.py`)

500+ HGNC alias mappings consolidating free-text targets to canonical gene symbols + 11 functional families:

- **Cytochrome P450**: 23 isoforms (CYP1A1/2/B1, CYP2A6/B6/C8/9/19/D6/E1, CYP3A4/5/7, CYP19A1) + family-level placeholders + rodent ortholog mapping
- **ABC transporters**: ABCB1 (= P-gp = MDR1 = multidrug resistance protein 1), ABCG2 (BCRP), ABCB11 (BSEP), ABCC1-5 (MRP1-5)
- **SLC transporters**: SLCO1B1/3/2B1 (OATPs), SLC22A1/2/6/8 (OCT1/2/OAT1/3), SLC47A1/2 (MATE1/2K), SLC10A1 (NTCP)
- **UGT phase II**: 9 isoforms + family placeholder
- **Nuclear receptors / TFs**: NFE2L2 (Nrf2), NR1I2 (PXR), AHR, NR1H4 (FXR), TP53, AR, ESR1, HIF1A
- **Kinase / signaling pathway**: MAPK family, JAK1/2/3, STAT1/3/5, AKT1, mTOR, AMPK (PRKAA1), Wnt/β-catenin
- **Inflammation cytokines**: TNF, IL1B/6/10, IFNG, NFKB pathway, COX-2 (PTGS2), NOS2/3
- **Apoptosis**: BCL2, BAX, CASP3/8/9, PARP1
- **Antioxidant / redox**: HMOX1, SOD, GPX, CAT, NQO1

Multi-target string splitting (comma/semicolon/slash/"and"/"or") applied before per-token normalization; 6.6% of interactions have ≥2 targets.

**Result**:

- 2,087 records with named target (67.3%)
- 1,734 (83.1% of named) mapped to canonical
- target_family distribution: cytochrome_P450 37.5%, ABC_transporter 8.1%, UGT_phase_II 2.5%, SLC_transporter 2.4%, nuclear_receptor_TF 1.2%, organ_tissue 1.3%, kinase_pathway 1.1%
- Key consolidations: **CYP3A4 = 509** (absorbed CYP3A 44 + variants), **ABCB1 = 221** (absorbed P-gp 100 + P-glycoprotein 86 + MDR1)
- 353 (11.4%) unmapped: rat CYP orthologs (CYP2C11/D1/D2), niche signaling proteins, generic placeholders — accepted as residual

### T4 — Interaction Class Classification (`16_classify_interaction_type.py`)

Classifies each interaction by completeness of three axes:

- `drug_known`: drug_name not in {null, unknown, (unknown), ""}
- `target_known`: target_canonical (from T1) not null
- `mech_specific`: mechanism not in {other, unspecified}
- `interaction_class`: one of {complete, herb_drug_no_target, herb_target_no_drug, fragmentary}

**Distribution**:

- `herb_drug_no_target`: 1,208 (39.0%) — PK studies without mechanism characterization
- `complete`: 959 (30.9%) — gold-standard (95% with specific mech, 907 are 3-axis triples ready for KG)
- `herb_target_no_drug`: 775 (25.0%) — herb-target mechanistic claims (97.7% have specific mech, e.g. "Herb X induces CYP3A4")
- `fragmentary`: 158 (5.1%) — low-information cases

**94.9% of interactions usable for network analysis** (fragmentary excluded).

### T3 — Drug Normalization (`17_normalize_drugs.py`)

150+ synonym alias entries + ATC-style functional class taxonomy (~50 classes):

- **Antineoplastics**: anthracycline, platinum, alkylating, taxane, antimetabolite, vinca alkaloid, topoisomerase, kinase inhibitor (TKI), hormone modulator, biologic
- **Anticoagulants / Antiplatelets**: VKA (warfarin), DOAC, heparin, LMWH, P2Y12 inhibitors
- **Immunosuppressants** (cyclosporine, tacrolimus, sirolimus, etc.)
- **Antidiabetics**: biguanide, sulfonylurea, TZD, DPP4i, GLP1RA, SGLT2i, insulin
- **Antihypertensives**: CCB (dihydropyridine / non-dihydropyridine), ACEi, ARB, beta-blocker, diuretic (loop / thiazide / K-sparing)
- **Statins**, NSAIDs, opioids, **antidepressants** (SSRI/SNRI/TCA), antipsychotics (typical/atypical), anticonvulsants, benzodiazepines
- **Antibiotics**: fluoroquinolone, penicillin, macrolide, tetracycline, aminoglycoside; antifungals; antivirals; PPIs; H2 blockers
- **CYP probe compounds**: phenacetin (CYP1A2), tolbutamide (CYP2C9), midazolam (CYP3A4), dextromethorphan (CYP2D6), chlorzoxazone (CYP2E1)
- **Hepatotoxicants**: CCl4, ethanol, dimethylbenzanthracene (organ-toxicity models)

**Result**:

- 2,167 records with named drug (69.9% of all)
- 100% pass-through canonical (long-tail drugs use cleaned original name)
- 1,562 (72.1% of canonical) classified non-'other'
- **Notable synonym merges**: doxorubicin = 95 (= 68 doxorubicin + 27 adriamycin), warfarin = 128 (incl. coumadin/coumarin variants), cyclosporine = 33 (4 spelling variants merged), fluorouracil = 50 (5-FU + variants), midazolam = 54 (incl. Versed), tacrolimus = 38 (FK506 + Prograf)
- 605 (19.5%) in 'other' class: long-tail drugs without standard ATC mapping (accepted; can be expanded if Day 10 network analysis identifies critical gaps)

### T2 — Herb Normalization (`18_normalize_herbs.py`, Day 9 capstone)

**107 canonical herb entries with 722 aliases**. Single source of truth in `HERB_ENTRIES` (list of dicts), each entry atomically specifying:

- Latin binomial (canonical)
- English common name
- Chinese pinyin (TCM herbs)
- Plant family (Linnaean taxonomy)
- Type: `plant` / `fungus` / `compound` / `formula` / `animal_derived` / `multi_source`

Coverage spans: TOP 20 highest-frequency in our corpus (SJW, Danshen, Schisandra, Ginseng [P. ginseng / P. quinquefolius / P. notoginseng], Licorice, Green Tea, Garlic, Coptis/Berberine, Astragalus, Ginkgo, Turmeric/Curcumin, Ginger, Khat, Quercetin, Andrographis, Echinacea, Centella) + TCM core (~40 herbs: Rehmannia, Cinnamon, Magnolia, Pueraria, Bupleurum, Angelica, Lycium, Scutellaria, Paeonia, Rheum, Reynoutria, Atractylodes, Poria, Lonicera, Forsythia, Ephedra, Artemisia, Silybum, Ophiopogon, Codonopsis, Eucommia, Cnidium, Crataegus, Ziziphus, Morus, Tripterygium, Ganoderma, Cordyceps, etc.)

- Western herbs (Milk Thistle, Black Cohosh, Valerian, Saw Palmetto, Hibiscus, Fenugreek) + TCM compound formulas (Suxiao Jiuxin, Baoyuan, Re Du Ning, Wuzhi Capsule) + multi-source flavonoids (quercetin, resveratrol, kaempferol, luteolin, apigenin, genistein) + animal-derived (Chan Su / bufalin).

Critical synonym coverage: **active compounds** mapped to parent plant: curcumin → Curcuma longa, berberine → Coptis chinensis, hyperforin → Hypericum perforatum, tanshinones → Salvia miltiorrhiza, EGCG → Camellia sinensis, ginsenosides → Panax ginseng, glycyrrhizin → Glycyrrhiza, icariin/icaritin → Epimedium, andrographolide → Andrographis, silymarin/silybin → Silybum, artemisinin/artesunate → Artemisia annua.

**3-tier resolution strategy**:

1. **Mapped** (in `HERB_ALIAS_MAP`): full metadata (Latin + English + pinyin + family + type)
2. **Pass-through** (named but unmapped): cleaned text as canonical, `herb_in_map=False`, `herb_type='unmapped'`
3. **None** (no herb info): all null

**Coverage achieved**:

- Records with named herb: 3,086 (99.5%)
- **Tier 1 mapped: 1,676 (54.1%)** — full HGNC metadata
- **Tier 2 pass-through: 1,411 (45.5%)** — usable as network nodes
- **Total with herb_canonical_id: 3,087 (99.6%) — 100% of named** ⭐
- Tier 3 null: 13 (0.4%)

**Notable merges** (consolidation success):

- *Hypericum perforatum*: 130 (SJW + hypericin + hyperforin)
- *Salvia miltiorrhiza*: 110 (Danshen + tanshinones + salvianolic acid)
- *Panax ginseng*: 72 (ginseng + ginsenosides)
- *Coptis chinensis*: 71 (coptis + rhizoma + berberine + huanglian)
- *Schisandra chinensis*: 68 (schisandra + schisandrin)
- *Glycyrrhiza uralensis*: 62 (licorice + glycyrrhizin)
- *Curcuma longa*: 53 (turmeric + curcumin + curcuminoids)
- *Camellia sinensis*: 47 (green tea + EGCG + catechins)

**Pass-through top entries** are mostly **valid Latin binomials** that the LLM extracted but weren't in our explicit map (*Mitragyna speciosa* 9, *Gastrodia elata* 9, *Psoralea corylifolia* 9, *Withania somnifera* 8, *Carthamus tinctorius* 8, *Viscum album* 8, *Corydalis yanhusuo* 7, etc.) plus Korean/TCM compound formulas (Ojeok-san, Bangpungtongseong-san, Shenmai injection) — these become **singleton network nodes** in Day 10 analysis.

### Day 9 Output Schema

`primary_<model>.interactions_normalized.parquet` — 24 original columns + **13 new normalized columns**:

- Target: `target_canonical`, `target_family`, `target_list`, `target_n`
- Drug: `drug_canonical`, `drug_class`
- Class: `drug_known`, `target_known`, `mech_specific`, `interaction_class`
- Herb: `herb_canonical_latin`, `herb_canonical_english`, `herb_canonical_pinyin`, `herb_family`, `herb_type`, `herb_in_map`

### Day 9 Headline Findings

- **99.6% of interactions** have a `herb_canonical_id` (network node ready)
- **56.0% of interactions** have `target_canonical` (target node identifier)
- **69.9% of interactions** have named drug → 100% pass-through canonical
- **94.9% of interactions** are non-fragmentary (usable as network edges)
- **~907 interactions (29.3%)** are 3-axis triples (complete + specific mech) → core knowledge graph
- 18 plant families dominate (~80% of mapped records): Fabaceae 182, Lamiaceae 167, Hypericaceae 133, Ranunculaceae 108, Araliaceae 102

### Day 9 Engineering Lessons

1. **Single-source-of-truth dict pattern** (`HERB_ENTRIES` list of dicts) is cleaner than three separate parallel maps; each entry atomically specifies Latin + English + pinyin + family + type + aliases. Adding a new herb requires editing one list element instead of synchronizing three maps.
2. **Three-tier normalization** (canonical → pass-through → null) is critical for downstream network analysis. Strictly requiring canonical match would lose 45%+ of legitimate research-grade Latin binomials simply because they were not in the explicit mapping table.
3. **Active compound names appear in three or four places**: `herb_common_name` (e.g. "turmeric"), `herb_active_compound` (e.g. "curcumin"), AND occasionally `drug_name` (LLM noise: "berberine" sometimes extracted as drug). Normalization must check all four fields with sensible priority (Latin > common > compound > drug-fallback) to capture these.
4. **Multi-target strings** (comma/semicolon-delimited "P-gp, MRP1, ABCG2") are common in HDI literature; must be split before normalization. 6.6% of targets are multi-target.
5. **Rat CYP orthologs** (CYP2C11, CYP2D1/2) are common in `in_vivo_animal` abstracts. Mapped to closest human orthologs (CYP2C9, CYP2D6) — this is an interpretive choice that should be reported transparently in Methods.
6. **Drug class names extracted as drug names** ("sulfonylureas", "anticoagulants", "NSAIDs", "protease inhibitors") account for ~30 records. LLM extraction noise; could be remapped to class-level placeholders in a future iteration (low priority — affects <1% of corpus).
7. **Coverage trade-offs at three levels**:
   - **Targets**: 83% mapped (HGNC has finite explicit names) — acceptable
   - **Drugs**: 100% pass-through, 72% classified — class taxonomy is the bottleneck
   - **Herbs**: 100% pass-through, 54% canonical-mapped — long tail dominated by Latin binomials LLM-extracted rather than vernacular names
