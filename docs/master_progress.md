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

------

## Day 10 (May 18, 2026): Network Analysis Trilogy ✅

**Status**: Complete **Latest commit**: <fill after commit> **Deliverables**: 3 network analysis scripts + 11 network parquets + 3 GraphML files for Cytoscape + complete trilogy spanning Herb-Drug, Herb-Target, and 3-axis Knowledge Graph perspectives

### Day 10 Headline Findings

- **Trilogy complete**: T1 (Herb × Drug), T2 (Herb × Target), T3 (3-axis KG) all built from Day 9 normalized data and exported as GraphML for Cytoscape + parquet for paper figures.

- **Network coverage**: 2,157 records in T1, 1,725 in T2, 900 in T3 (gold-standard 3-axis triples). Each successive filter increases specificity.

- **HDI literature canon validated**: Top edges in all three networks match canonical HDI references (Smolinske 1999, Markowitz 2003, Izzo 2009, Brantley 2013).

- Novel narrative twists

  :

  - In T1: doxorubicin (69) > warfarin (60) as drug hub — TCM-HDI focus is chemotherapy modulation, not just anticoagulation.
  - In T2: Hypericum drops from #1 (T1, drug-hub) to #15 (target-hub) — SJW research is NARROW-DEEP (CYP3A4-focused) while Coptis/Salvia/Panax are BROAD (multi-target).
  - In T3: 38% of gold triples are PD-effect (not just PK-exposure) — reveals TCM-HDI literature's dual focus: PK interactions AND PD synergism/antagonism.

### T1 — Herb × Drug Bipartite Network (`19_build_herb_drug_network.py`)

**Filter**: drug_known interactions (require herb_canonical_latin AND drug_canonical) **Aggregation**: by (herb, drug), counts records, computes top mechanism / direction / mean confidence / mechanism set / record IDs per edge

**Network metrics**:

- Nodes: 1,292 (727 herbs + 570 drugs)
- Edges: 1,751 (unique herb-drug pairs)
- Bipartite density: 0.42%
- Connected components: 126 (giant 79.1% = 1,022 nodes; 108 isolated pairs)
- Herb degree: mean 2.41, max 54 (*Hypericum perforatum*)
- Drug degree: mean 3.09, max 69 (doxorubicin)

**Top hub herbs** (with HGNC-mapped family):

- *Hypericum perforatum* (54, Hypericaceae)
- *Salvia miltiorrhiza* (39, Lamiaceae)
- *Panax ginseng* (36, Araliaceae)
- *Glycyrrhiza uralensis* (35, Fabaceae)
- *Coptis chinensis* (31, Ranunculaceae)
- *Curcuma longa* (29, Zingiberaceae)
- *Astragalus*, *Camellia sinensis*, *Ginkgo*, *Schisandra*, *Scutellaria*

**Top hub drugs** (with ATC class):

- doxorubicin (69, antineoplastic_anthracycline) ⭐ biggest drug hub
- warfarin (60, anticoagulant_VKA)
- cisplatin (54, antineoplastic_platinum)
- midazolam (36, benzodiazepine)
- fluorouracil (35), metformin (34, biguanide), phenacetin (28, CYP probe)

**Top edges (matching HDI literature canon)**:

- *Schisandra chinensis* × tacrolimus: 17 records (CYP_inhibition, Wuzhi clinical)
- *Hypericum perforatum* × warfarin: 12 (CYP_induction, classic case)
- *Hypericum* × cyclosporine: 9 (organ transplant case)
- *Panax ginseng* × warfarin: 9
- *Salvia* × aspirin: 9 (P-gp + receptor synergism, bleeding risk)
- *Schisandra chinensis* × acetaminophen: 8 (**organ_toxicity_modulation** — Schema v3 capture, schisandrin B hepatoprotection)

**Mechanism breakdown on 1,751 edges**:

- CYP_inhibition 307 (17.5%), unspecified 299, synergistic_efficacy 208, receptor_synergism 198, other 150 (8.6% — vs 19.9% pre-audit), CYP_induction 130, P-gp_inhibition 75, **organ_toxicity_modulation 70**, transporter_modulation 70, **signaling_pathway_modulation 60** (Schema v3 mechanisms validated)

**Most multi-mechanism edges (≥3 distinct mechs)**:

- SJW × warfarin: 4 mechs (CYP_induction|CYP_inhibition|other|unspecified, 12 records)
- SJW × cyclosporine: 4 mechs (CYP_induction|CYP_inhibition|absorption_alteration|unspecified, 9 records)
- Schisandra × acetaminophen: 4 mechs (CYP_inhibition|absorption_alteration| organ_toxicity_modulation|signaling_pathway_modulation, 8 records) — paper Discussion gold

### T2 — Herb × Target Bipartite Network (`20_build_herb_target_network.py`)

**Filter**: target_known interactions (require herb_canonical_latin AND target_canonical) **Edge attributes**: count, top mechanism, top direction, top drug (context), top drug class, n distinct drugs (which drugs are involved when herb hits target) **Bonus outputs**: herb_family × target_family + target_family × mechanism cross-tabs

**Network metrics**:

- Nodes: 684 (609 herbs + 75 targets)
- Edges: 1,144 unique herb-target pairs
- Bipartite density: 2.5% (~6× higher than T1; targets are more shared)
- Giant component: 97.4% (666 nodes; high connectivity via CYP3A4 hub)
- Target degree: mean 15.25, max 238 (CYP3A4)
- Herb degree: mean 1.88, max 16 (Coptis / Salvia tied)

**Top hub targets**:

- **CYP3A4: 238 herbs** (~21% of all edges; the dominant single target)
- CYP1A2: 148, ABCB1: 114, CYP2C9: 92, CYP2D6: 65, CYP2C19: 52, CYP2E1: 42, CYP2B6: 30
- **ORGAN_liver: 26** (organ-toxicity model results)
- UGT1A1 (22), CYP1A1 (21), CYP2C8 (20), SLC22A6 (19)
- **NR1I2 / PXR: 18** ⭐ master TF regulating CYP3A4 induction
- PI3K_family (14), UGT2B7 (12), ABCG2 (11), SLCO1B1 (10)

**Top hub herbs** (different rank order from T1):

- *Coptis chinensis*, *Salvia miltiorrhiza* (both 16) — most target-diverse
- *Glycyrrhiza uralensis*, *Panax ginseng* (15)
- *Schisandra chinensis* (14), *quercetin* (12), *Catha edulis* (11)
- *Hypericum perforatum* falls to rank #15 with degree 8 ⭐ NARROW-DEEP pattern

**Top edges**:

- *Hypericum perforatum* × CYP3A4: 56 (CYP_induction via midazolam probe) — overwhelming
- *Schisandra chinensis* × CYP3A4: 19 (CYP_inhibition via tacrolimus)
- *Salvia* × ABCB1: 17 (P-gp_inhibition via verapamil)
- *Astragalus* × ABCB1: 15 (receptor_synergism via fluorouracil — chemo adjuvant)
- *Schisandra* × CYP2E1: 7 (CYP_inhibition via acetaminophen — schisandrin B hepatoprotection mechanism quantified)

**Mechanism cleanness improved**:

- CYP_inhibition 560 edges (49%), CYP_induction 152 (13%), transporter_modulation 71, P-gp_inhibition 70, UGT_inhibition 61, receptor_synergism 59, **signaling_pathway_modulation 53 + organ_toxicity_modulation 47** (Schema v3)
- 'other' + 'unspecified' = 3.5% (vs ~22% in raw)

**Family-level cross-tab (`herb_family_x_target_family.parquet`, 164 pairs)**:

- Hypericaceae → cytochrome_P450: 69 (SJW dominant lane)
- Fabaceae → cytochrome_P450: 61 (Glycyrrhiza + Astragalus + Sophora multi-source)
- Ranunculaceae → cytochrome_P450: 43, Schisandraceae → CYP: 39
- Lamiaceae → ABC_transporter: 25 ⭐ Lamiaceae has P-gp preference
- Fabaceae → ABC_transporter: 23 ⭐ Fabaceae also multi-pathway

**Herb family diversity ranking** (paper Figure 2 narrative):

- *Fabaceae*: 100 records, 22 targets, 8 families — **BROAD pattern** (Glycyrrhiza, Astragalus, Sophora, Pueraria)
- *Hypericaceae*: 75 records, 8 targets, 4 families — **NARROW-DEEP pattern** (SJW CYP3A4-focused)
- *Lamiaceae*: 72 records, 19 targets, 7 families — BROAD (Salvia, Scutellaria diversity)
- *Ranunculaceae*: 59 records, 20 targets, 7 families — BROAD (Coptis, Aconitum)

**Cross-tab `target_family_x_mechanism.parquet` (45 pairs)**:

- cytochrome_P450 ↔ CYP_inhibition 389 + CYP_induction 178 (567 records, dominant axis)
- ABC_transporter ↔ P-gp_inhibition 75 + transporter_modulation 19
- UGT_phase_II ↔ UGT_inhibition 41
- SLC_transporter ↔ transporter_modulation 34
- organ_tissue ↔ organ_toxicity_modulation 14
- nuclear_receptor_TF ↔ signaling_pathway_modulation 11

### T3 — 3-axis Knowledge Graph (`21_build_knowledge_graph.py`)

**Filter**: `interaction_class == 'complete' AND mech_specific == True AND herb_canonical_latin / drug_canonical / target_canonical / mechanism all not null` **Result**: **900 gold-standard triples** (out of 3,100 total interactions)

**Output structure**:

- `kg_triples.parquet`: 900 rows, long-format 4-tuples (herb, drug, target, mechanism) with direction / confidence / evidence_type / clinical_significance / quote
- `kg_multigraph.graphml`: heterogeneous multigraph (683 nodes = 353 herbs + 268 drugs + 62 targets; 1,930 mechanism-labeled edges)
- `drug_target_edges.parquet`: 421 drug-target pairs (the third bipartite, completing T1+T2+T3 trio)
- `drug_class_x_mechanism.parquet`: 189 (drug_class, mechanism) pairs
- `target_family_x_drug_class.parquet`: 141 pairs
- `kg_chain_summary.parquet`: 344 herb_family → mechanism → drug_class chains (for Sankey diagram or paper Figure 3c)

**Top 6 gold-standard 4-tuples** (most-replicated):

- *Hypericum perforatum* × midazolam → CYP3A4 via CYP_induction (6) — THE canonical SJW probe
- *Schisandra chinensis* × tacrolimus → CYP3A4 via CYP_inhibition (6) — Wuzhi clinical
- *Salvia miltiorrhiza* × verapamil → ABCB1 via P-gp_inhibition (4)
- *Hypericum* × indinavir → CYP3A4 via CYP_induction (3) — SJW-protease inhibitor classic
- *Hypericum* × cyclosporine → CYP3A4 via CYP_induction (3)
- *Schisandra* × acetaminophen → CYP2E1 via CYP_inhibition (3) — **schisandrin B hepatoprotection mechanism quantified at gold-standard rigor**

**Top mechanistic chains** (herb_family → mechanism → drug_class):

- Hypericaceae → CYP_induction → "other" 19, benzodiazepine 8, immunosuppressant 4 — multi-drug-class SJW story
- Schisandraceae → CYP_inhibition → immunosuppressant 11 — Wuzhi niche
- Fabaceae → CYP_inhibition → "other" 8, benzodiazepine 5 — Glycyrrhiza multi-target
- Lamiaceae → transporter_modulation → lipid_lowering_statin 5 — Salvia statin interaction

**Direction distribution in gold-standard triples** (reveals dual PK+PD nature):

- exposure_increase: 312 (34.7%) ┐ PK-level
- exposure_decrease: 223 (24.8%) ┘ → 59.5%
- effect_increase: 218 (24.2%) ┐ PD-level
- effect_decrease: 128 (14.2%) ┘ → 38.4%
- no_change: 17 (1.9%), context_dependent: 2 (0.2%)

**Confidence distribution**: mean 0.87, median 0.85, range 0.70-0.95; 99.7% of triples have confidence ≥ 0.8.

**Temporal coverage**: 2005-2025, peak years 2014 (98 triples), 2016 (72), 2020 (62), 2012 (59), 2019 (55).

**Top 15 drug × target hubs** (the 'mechanistic' anchors):

- doxorubicin × ABCB1: 46 (top herb: Magnolia officinalis, P-gp_inhibition)
- midazolam × CYP3A4: 46 (top herb: Hypericum, CYP3A4 probe canonical)
- phenacetin × CYP1A2: 30 (CYP1A2 probe drug)
- tolbutamide × CYP2C9: 20 (CYP2C9 probe)
- diclofenac × CYP2C9: 15
- verapamil × ABCB1: 14
- acetaminophen × CYP2E1: 12 (toxicity model)
- zidovudine × UGT2B7: 11 (UGT2B7 substrate)
- tacrolimus × CYP3A4: 11 (immunosuppressant probe)
- metoprolol × CYP2D6: 10

### Day 10 Output Schema

`data/processed/network/`:

- **Edge tables**: `herb_drug_edges.parquet`, `herb_target_edges.parquet`, `drug_target_edges.parquet` (aggregated edge lists with metadata)
- **Node tables**: `herb_drug_nodes.parquet`, `herb_target_nodes.parquet`
- **Cross-tab matrices**: `herb_family_x_target_family.parquet`, `target_family_x_mechanism.parquet`, `drug_class_x_mechanism.parquet`, `target_family_x_drug_class.parquet`, `kg_chain_summary.parquet`
- **Knowledge graph**: `kg_triples.parquet` (900 long-format 4-tuples)
- **GraphML**: `herb_drug.graphml`, `herb_target.graphml`, `kg_multigraph.graphml` (Cytoscape / Gephi compatible)

### Day 10 Engineering Lessons

1. **Filter ordering**: filter NaN values explicitly before groupby aggregation, otherwise networkx will create nodes with no attributes when the edge loop references them. The 3-axis KG specifically needs `notna()` on all four canonical fields (herb, drug, target, mechanism), not just relying on `interaction_class == 'complete'`.
2. **Pandas deprecation handling**: `groupby.apply()` operating on grouping columns is deprecated. Use `groupby(..., group_keys=False).apply(func, include_groups=False)` for forward compatibility.
3. **Bipartite network density patterns**: T2's density (2.5%) is ~6× higher than T1's (0.42%) because targets are highly shared across herbs (CYP3A4 alone has 238 herb partners), while drugs are more idiosyncratic. The T2 giant component is 97% vs T1's 79% for the same reason.
4. **Heterogeneous multigraph for KG**: Using nx.MultiGraph with prefixed node IDs (`herb::`, `drug::`, `target::`) keeps node types distinguishable in GraphML export. Multi-edges allow representing different mechanisms between the same pair, important for cases like SJW-warfarin (4 mechanisms).
5. **Network analytics for paper narrative**: comparing hub ranks across T1 (drug-level) vs T2 (target-level) revealed the NARROW-DEEP (Hypericum) vs BROAD (Coptis, Salvia, Panax) herb research patterns — a finding that would be invisible from either network alone.
6. **Direction analysis as paper finding**: the 60-40 split of PK (exposure) vs PD (effect) direction labels in gold-standard triples is novel evidence that TCM-HDI research is genuinely dual-track, not just PK-focused. Cited reviews (Izzo 2009, Brantley 2013) emphasize PK; this finding adds PD nuance.
7. **Family-level cross-tabs as Figure 2 sources**: aggregating at family level (herb_family × target_family) reduces 1,144 individual herb-target edges to 164 family-family flows, ideal for heatmap visualization in manuscript. The most informative cells (Hypericaceae→P450, Lamiaceae→ABC, Fabaceae→multi) drive Figure 2 narrative.
8. **Cytoscape integration**: GraphML export uses str() casting on all attributes (NaN → ""; ints kept as int) to avoid `xml.etree.ElementTree` serialization errors. All node/edge attributes preserved for Cytoscape Style mapping (node_type, family_or_class, in_map, n_records, top_mechanism, etc.).

### Files Produced (Day 10)

- 3 scripts (06_network_analysis/19, 20, 21)
- 11 parquet files (data/processed/network/)
- 3 GraphML files (data/processed/network/)

### What Day 10 Enables (Days 11-21)

- **Day 11**: CiteSpace + R bibliometrix parallel workstreams from raw WoS data (different data source than LLM-derived networks; complementary not duplicate)
- **Day 12-13**: Mechanism × Topic cross-analysis (intersect with Day 5 HDBSCAN clusters for thematic mechanism distribution)
- **Day 14-15**: Time trend analysis (using kg_triples year_min/year_max spans + cross-tab matrices for stacked area charts)
- **Day 17**: Paper figure stage — open the 3 GraphML files in Cytoscape, apply Force-Directed Spring Embedded layout with edge_weight, node_type color mapping, degree-based size mapping; export to SVG; polish in Inkscape for Figures 1, 2, 3
---

## Day 11 (May 16, 2026): Publication-quality figure generation ✅

**Status**: Complete
**Latest commit**: <fill after commit>
**Deliverables**: 4 main + 4 supplementary publication-quality figures,
plus figure captions draft and Methods §2.5 (canonical normalization)
draft. Style stack: SciencePlots + Okabe-Ito colorblind-safe palette +
PDF fonttype 42 (Illustrator-editable) + 300 DPI raster output. The
fig6 Sankey uses a browser print-to-PDF fallback for vector export
(kaleido status detailed in Engineering Notes).

### Day 11 Headline Outputs

- **Main figures (paper §3)**:
  - Fig 5a — Herb family × target family heatmap (T2, 1,725 records → 164 family pairs)
  - Fig 5b — Target family × mechanism heatmap (T2)
  - Fig 6  — Mechanism Sankey: herb_family → mechanism → drug_class (T3, 344 chains from 900 gold triples)
  - Fig 8  — Temporal mechanism evolution 2005–2025 (T3 by year)
- **Supplementary figures**:
  - Fig S3 — Drug class × mechanism heatmap
  - Fig S4 — Direction distribution by herb family
  - Fig S5 — Confidence distribution histogram
  - Fig S6 — Top hubs 3-panel bar chart (herbs / drugs / targets)
- **Style stack**: SciencePlots `science + no-latex` cascade,
  Okabe-Ito colorblind-safe categorical palette, YlOrRd / viridis /
  RdBu_r sequential maps, 300 DPI PNG + PDF fonttype 42
  (Illustrator/Inkscape editable) + SVG (for the seven matplotlib
  figures); fig6 outputs HTML (plotly) + PDF (browser-exported,
  vector-preserved)
- **Captions**: drafted in `results/figures/captions.md`,
  schema-aware (fallback canonical buckets + drug_class/target_family
  orthogonality explicitly noted for reviewer-proofing)
- **Methods §2.5 draft**: `docs/manuscript_drafts/methods_section_drafts.md`
  covers canonical normalization for herb / target / mechanism axes
  (Schema v3 ontology, three-tier mapping strategy, rat-CYP ortholog
  harmonization, confidence threshold ≥ 0.7)

### Day 11 Engineering Notes

1. **kaleido / plotly Sankey export — browser print-to-PDF fallback**:
   plotly 5.18.0 paired with kaleido 1.3.0 raised ImportError on
   `fig.write_image()`. Downgrade to `kaleido==0.2.1` cleared the
   ImportError (replaced by a DeprecationWarning) but kaleido 0.2.1
   still failed silently on this Windows host — likely a bundled-
   Chromium subprocess issue, swallowed by the figure script's
   try/except so only the HTML file was actually produced.
   **Workaround**: open `fig6_mechanism_sankey.html` in Chromium-based
   browser → Ctrl+P → Save as PDF → produces a vector PDF (plotly SVG
   primitives preserved end-to-end). This is the documented plotly-
   community fallback for Sankey export on Windows systems where
   kaleido is problematic. Root-cause kaleido fix deferred to
   post-paper phase; PDF is publication-acceptable for Frontiers in
   Pharmacology and equivalent journals.
2. **Schema-aware captions**: two figure ambiguities flagged during
   review were resolved at caption level rather than data level:
   (a) `flavonoid_compound` and `TCM_formula` appearing on the herb
   family axis are legitimate Schema v3 fallback canonical buckets,
   not data leakage; (b) the empty `oncology_target` column reflects
   the orthogonal placement of therapeutic-area information on the
   `drug_class` axis (Figure 6), not literature absence.
3. **All figures regenerated from Day 10 parquet/GraphML sources**;
   no manual data editing — full re-runnability preserved. The
   figure script (`06_network_analysis/22_generate_figures.py`)
   supports `--only N` flag for selective regeneration of a single
   figure (used to refresh fig6 without re-running the full set).

### Outstanding (Day 12+)

1. **CiteSpace keyword burst / timezone** (Fig 7) — separate tool,
   requires WoS `.txt` export from Day 1; planned for Day 12
   parallel workstream
2. **R bibliometrix** publication trends + Lotka/Bradford
   supplementary visuals (Fig 2 + Supp S6 alternative) — Day 12
   parallel workstream
3. **Cytoscape network rendering** (Main F4 + Supp S1, S2) — Day 17
4. **PRISMA flow** (Fig 1) — Inkscape, Day 16-17
5. **kaleido root-cause fix** — defer to post-paper; skip if fig6 is
   the only plotly-Sankey artifact in the project
6. **Header timestamp** of this document still reads
   "Last updated: 2026-05-15, end of Day 3" (now stale through
   Day 11) — to be refreshed at Day 14 mid-point checkpoint

### Files Produced (Day 11)

- 1 script: `06_network_analysis/22_generate_figures.py`
- 7 matplotlib figures (`fig5a`, `fig5b`, `fig8`, `figS3`, `figS4`,
  `figS5`, `figS6`): PNG (300 DPI) + PDF (fonttype 42) + SVG, all via
  the SciencePlots stack
- 1 plotly Sankey (`fig6_mechanism_sankey`): HTML (interactive,
  ~4.9 MB) + PDF (vector, browser-exported via Chrome print-to-PDF)
- 1 captions document: `results/figures/captions.md`
- 1 methods draft: `docs/manuscript_drafts/methods_section_drafts.md`
---

## Day 12 B (May 17, 2026): R bibliometrix convention check ✅

**Status**: Complete (Day 12 A — CiteSpace — pending)
**Latest commit**: <fill after commit>
**Deliverables**: 4 R analysis scripts + 6 paper-quality figures
(13 files across formats) + 7 supporting tables + 1 findings
document spanning 5 paper-worthy findings. Methodological
convention check on WoS subset (n = 3,091) cross-validated
against the Python main analysis (integrated n = 9,438).

### Day 12 B Headline Findings

1. **Citation density cross-validation** — avg cit/doc 26.41 (WoS)
   vs 25.72 (integrated); 2.7% difference confirms 4-DB integration
   did not introduce systematic citation bias.
2. **Super-Lotka under both disambiguation schemes** — alpha = 2.38
   (D1 FINI, WoS bibliometrix) vs 2.63 (D2 FINI+Inst, Python);
   both > 2.0; R^2 = 0.960 vs 0.957 (nearly identical fit quality).
3. **Bradford geometric mean 7.11 (WoS) vs 8.89 (integrated)** —
   both far exceed classical Bradford multiplier of ~5, indicating
   strong publication concentration; 3 Zone-1 anomalies flagged
   (ECAM post-publication concerns, Molecules MDPI mega-journal,
   Latin American Journal of Pharmacy regional concentration).
4. **Thematic map: Q1 Motor and Q3 Emerging both empty** — only
   Q2 Niche (classic safety cases + CAM literature) and Q4 Basic
   (in-vitro metabolism + cellular biology) are populated, revealing
   a fragmented-but-foundationally-consolidated field morphology
   with no unified motor paradigm.
5. **Classic safety cases form a structural niche** — SJW + grapefruit
   + P-gp + ginkgo + milk thistle + ginseng cluster shows high
   internal density + low centrality, indicating a closed citation
   community no longer engaged by mainstream new-mechanism research.

### Files Produced (Day 12 B)

- **Scripts** (`07_bibliometrix_r/`): 23 / 24 / 25 / 26 — load,
  biblioAnalysis summary, Lotka+Bradford, three-field + thematic map
- **Figures** (`results/figures_bibliometrix/`):
  - `fig2_alt_annual_production.{pdf, png}` (with 2026 partial-year annotation)
  - `fig2_alt_avg_citations_per_article.{pdf, png}`
  - `figS_alt_lotka.{pdf, png}`
  - `figS_alt_bradford.{pdf, png}`
  - `fig_thematicMap_keywords.{pdf, png}` (custom ggrepel layout)
  - `fig_threeFields_country_author_keyword.{html, pdf}` (browser-exported PDF)
- **Tables**: 7 CSV (top sources / authors / countries / cited papers
  / Lotka fit / Bradford zones / thematic clusters)
- **Findings document**: `docs/manuscript_drafts/notes_bibliometrix_findings.md`

### Engineering Notes

1. **bibliometrix 4.x API changes** — `lotka()` now takes `M`
   (bibliometrixDB class) not the `results` object. `L$AuthorProd`
   column names renamed to "Documents written" / "N. of Authors" /
   "Proportion of Authors". Block 3 .R file patched for re-runnability
   independent of an open R session.
2. **Default thematicMap plot inadequate for 2-quadrant-populated
   case** — bibliometrix's corner quadrant labels overlap with cluster
   labels and watermark when only 2 of 4 quadrants are populated.
   Replaced with custom ggrepel-based layout matching Okabe-Ito
   palette from Day 11 figures.
3. **plotly htmlwidget for threeFieldsPlot** — kaleido-free HTML
   output; browser print-to-PDF for the static PDF version,
   same fallback workflow as Day 11 fig6 Sankey.
4. **Three intermediate .rds files excluded from git** — `M.rds`
   (10 MB), `biblio_results.rds` (430 KB), `themat.rds` (13 MB)
   are large reproducible caches; `.gitignore` updated to exclude
   `results/figures_bibliometrix/*.rds`.

### Outstanding (Day 12 A — same Day, parallel workstream)

**CiteSpace keyword burst + timezone view** — separate Java GUI tool,
uses same WoS `.txt` export as bibliometrix Block 1. Produces Fig 7
(keyword burst detection 2005-2026 + thematic timezone view).
Estimated 4-5h including ~30min learning curve. To start after
Day 12 B commit.

---

## Day 12 A — CiteSpace keyword co-occurrence + burst analysis (2026-05-17)

### Status: ✅ COMPLETED

### Workspace
- Project home: `data/citespace_workspace/project/` (**gitignored**, 中间文件)
- Output: `results/figures_citespace/` (git-tracked, 8 files)
- 输入：`data/raw/wos/wos_batch_*.txt` (7 batches, 3091 records)，复制重命名为 `download_001-007.txt` 进 CiteSpace data 目录

### Parameters
- CiteSpace 6.4.R1, Time slicing 2005-2026 (1 yr/slice, 22 slices)
- Node Type: Keyword (Title + Abstract + DE + ID 四源)
- Selection: g-index k=25
- Links: Cosine within slices
- Pruning: Pathfinder + Pruning sliced networks
- Burst: γ=0.5, min duration=2 → **220 keywords detected**

### Network statistics
- N=667, E=3336, Density=0.015
- Largest CC=663 (99%)
- **Modularity Q = 0.3802** (> 0.3 标准)
- **Weighted Silhouette S = 0.6935** (> 0.5, 近 0.7)
- Clusters reported: 11 (size ≥ 10)

### Deliverables (8 files in results/figures_citespace/)
| File | Type | Size | Purpose |
|---|---|---|---|
| fig7_top25_keyword_bursts.pdf | Vector PDF | 101 KB | Paper Fig 7 (待美化) |
| fig7_top25_keyword_bursts.html | HTML | 9 KB | Render source |
| table_citespace_top25_bursts.tsv | TSV | 2 KB | Paper Table |
| table_citespace_all220_bursts.tsv | TSV | 17 KB | Supp Table |
| table_citespace_cluster_summary.csv | CSV | 2 KB | Cluster metadata |
| network_keyword_667.graphml | GraphML | 698 KB | Cytoscape Day 17 |
| citespace_burstness_raw.out | Binary | 12 KB | Reproducibility |
| README.md | Markdown | 6 KB | Figure beautifier handoff |

### 5 paper-worthy findings (详见 docs/manuscript_drafts/notes_citespace_findings.md)
1. **Strongest burst symmetry**: SJW (27.01, 2005-2012) ↔ network pharmacology (27.59, 2023-2026 ongoing) — paper 核心 narrative
2. **4 burst eras**: case-based (Era 1) → mechanistic (Era 2) → transition (Era 3) → systems (Era 4 ongoing)
3. **6 ongoing bursts (End=2026)**: oxidative stress, inflammation, natural products, molecular docking, network pharmacology, gut microbiota
4. **Cross-tool 1:1 validation**: CiteSpace Era 1 ↔ bibliometrix Q2 Niche; CiteSpace Era 4 ↔ bibliometrix Q4 Basic — 方法学三角验证
5. **Non-burst foundations**: CYP3A4 / P-gp / PXR 高频但从未 burst = 永恒基石词

### Findings document
- `docs/manuscript_drafts/notes_citespace_findings.md` (~12 KB)
- 5 findings + Methods §2.x + Discussion §4 4 段草稿

### Engineering notes
- Save Cluster Information 静默写入 project 文件夹（folders 0-10 per cluster），不弹保存对话框
- `CitationBurst.out` 在 GO 阶段已自动算过一次 (γ=1.0)，重跑 γ=0.5 覆盖
- Cluster Explorer 只显示 size ≥ 10 的 cluster (11/14)
- Timeline View 信息密度高，工具内 label threshold 对 timeline 不生效（CiteSpace UX 缺陷）→ 放弃 inline 精修
- **不出 cluster network / timeline 图片**（per Day 12 A 决策），交美化协作者基于数据重绘

### 跨工具一致性 (Day 12 B vs Day 12 A)
| 维度 | bibliometrix (Day 12 B) | CiteSpace (Day 12 A) | 一致 |
|---|---|---|---|
| 时间-主题分层 | 4 thematic clusters in 2 quadrants | 4 burst eras | ✓ |
| 早期 niche 主题 | Q2 Niche: SJW + grapefruit + P-gp + ginkgo | Era 1: SJW + grapefruit + ginkgo + milk thistle | ✓ 1:1 |
| 新兴主题 | Q4 Basic: network pharm + oxidative stress | Era 4: network pharm + oxidative stress + gut microbiota | ✓ 1:1 |
| 网络药理学定位 | 嫩芽阶段 (低密度高中心度) | strength 27.59 持续 burst | ✓ 同一现象 |

→ 两个独立算法栈对 TCM-HDI 时间-主题骨架判断**完全一致**，paper Methods 段强力方法学三角验证 argument。

### 时间消耗
- ~3h (CiteSpace 学习曲线 + 11 cluster + Burst 220 + 数据 wrap-up)
- 1 conversation
- 决策放弃 inline 图片精修 → 节省 ~1h，交美化协作者用源数据重绘

### Project progress
- **12/21 天 (~57%)**
- 下一节点：Day 13-15 Topic × Mechanism cross-analysis


---

## Day 13 — Topic × Mechanism cross-analysis (static, 2026-05-18)

### Status: ✅ COMPLETED

### Data dimensions
- Topic source: HDBSCAN over UMAP(SPECTER2), 39 real topics (+ -1 noise)
- Mechanism source: LLM Schema v3, 16 mechanism categories (after dropping unspecified/other)
- Matrix: 37 topics × 16 mechanisms = 592 cells
- N = 1,738 (record_id × mechanism) pairs from 1,662 unique records
- Sparsity: 63.3% non-zero cells

### Method
- Filter: confidence ≥ 0.7; drop HDBSCAN noise cluster (-1); drop mechanism in {unspecified, other}
- Test: Fisher exact two-sided per cell (592 tests)
- Correction: BH-FDR
- Significance: q < 0.05
- Strong enrichment: q < 0.05 AND OR > 2 AND observed ≥ 5
- Strong depletion: q < 0.05 AND OR < 0.5 AND expected ≥ 5

### Statistics
- 63 significant cells (10.6%) — balanced 34 enriched + 29 depleted
- 30 strong enrichments + 29 strong depletions

### Deliverables (results/)
| File | Type | Notes |
|---|---|---|
| figures/fig9_topic_x_mechanism_heatmap.{png,pdf,svg} | Fig | log-scale, PK/PD column groups, Okabe-Ito |
| tables/table_topic_x_mechanism_matrix*.csv (4 files) | Tables | Block 1 outputs |
| tables/table_topic_x_mechanism_enrichment_full.csv | Table | 592 rows |
| tables/table_topic_x_mechanism_enrichment_significant.csv | Table | 63 rows |
| tables/table_topic_x_mechanism_top_enriched.csv | Table | 20 rows (paper Table 4 source) |
| tables/table_topic_x_mechanism_top_depleted.csv | Table | 20 rows (Supp S9) |

### 8 paper-grade findings (详见 docs/manuscript_drafts/notes_day13_findings.md)
1. F9 — Strongest enrichment: #24 UGT × UGT_inhibition (OR=505, q=2.8e-82)
2. F10 — PK-pure topics: #30/#24/#32/#9 — mechanism-named, statistically reject all PD mechanisms
3. F11 — PD-pure topics: #11/#23/#28 — clinical-named, statistically reject all PK mechanisms (#11 × CYP_inh: q=1.9e-47!)
4. F12 — **Structural bifurcation** (paper §4 core narrative): PK space vs PD space, near-zero cross-talk
5. F13 — Bridge clusters: #17 hepatotoxicity is the strongest translational interface
6. F14 — Internal validation: tautological mechanism-name × mechanism enrichments (#30, #24, #32, #9) confirm topic model + LLM extraction agree
7. F15 — Three null-enrichment topics (#25 phytochem, #38 pharmacies, #37 herbal supp): TCM context literature, not mechanism research
8. F16 — Three-tool triangulation: SJW–warfarin paradigm consistent across bibliometrix Q2, CiteSpace Era 1, Day 13 #5 × CYP_induction (q=9.5e-15)

### Discussion drafts in notes doc
- §4.x.1 PK/PD structural bifurcation
- §4.x.2 Bridge clusters & translational interfaces
- §4.x.3 Mechanism-name alignment as internal validation
- §4.x.4 Three-method triangulation

### Engineering notes
- N = 1,738 (cell sum, pair-units) used for Fisher test — consistent with matrix construction
- Haldane-Anscombe (+0.5) for log2_OR display only; raw Fisher p uses exact hypergeometric
- Depletion threshold uses expected ≥ 5 (not observed ≥ 5)
- 2 topics (#0, #29) absent from matrix — small clusters with no confidence ≥ 0.7 mechanism extraction
- New script dir 08_topic_mechanism/ (3 scripts: Block 1 / 2 / 3)

### Project progress
- **13/21 days (~62%)**
- Next: Day 14 — Topic × Mechanism × Burst Era (temporal stratification)
