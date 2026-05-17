# Methods (Section 2) -- Draft

> Living draft. Day 16 Block 2c.C (revised). Section 2 lead-in + 6 subsection skeleton.
> Lead-in compressed to ~140 words; triangulation framing moved to discussion_section4_lead_draft.md;
> data availability statement moved to data_availability_statement_draft.md.
> Subsections to be filled in Day 17+ blocks.

---

## §2.0 Lead-in (~140 words, procedural enumeration only)

This study integrates four complementary computational approaches to characterize 
the corpus of literature on traditional Chinese medicine (TCM) herbal-drug 
interactions published between 2005 and 2026. A search across Web of Science 
Core Collection, Scopus, OpenAlex, and PubMed was assembled into a single 
integrated corpus through a five-stage deduplication and precision-filter 
pipeline (Figure 1; Section 2.1-2.2), yielding 9,413 main-period records 
(2005-2025) and a 304-record partial 2026 extension. We then applied 
SPECTER2-embedding topic modeling (Section 2.3), large-language-model-based 
mechanism extraction under a fixed 16-category schema (Section 2.4), 
and two families of subsequent analyses: bibliometric convention and 
citation-burst analysis on the corpus as a whole (Section 2.5), and 
Fisher-exact enrichment testing across topic x mechanism x era and 
herbal-taxonomy tiers (Section 2.6).

---

## §2.1 Data sources and search strategy

[TODO -- Day 17 Block A]

Subsections to cover:
- 4 databases: WoS Core Collection, Scopus, OpenAlex, PubMed
- Date range: 2005-01-01 to 2026-05-14 (search execution date)
- Search strategy per DB (Boolean structure, fields targeted)
- TCM-specific term coverage (herb names, formula names, CYP isoforms, drug-interaction predicates)
- Why 4 DBs (coverage diversity, language reach, free-vs-paid spectrum)
- Reference: 01_data_acquisition/01_wos_search_strategy.md etc.

---

## §2.2 Corpus integration and deduplication

[TODO -- Day 17 Block A]

Subsections to cover:
- 5-stage pipeline summary (referenced to Figure 1)
- DOI primary-key deduplication (exact match on lowercase, prefix-stripped DOI)
- Fuzzy title matching (ratio >= 95, blocking on year + first-author surname, bibliometrix default tol=0.95)
- OpenAlex 3-block precision filter (B1 direct TCM+drug+interaction; B2 TCM+interaction; B3 TCM+CYP; B0 dropped as no-match)
- Cross-file deduplication (main 2005-2025 vs partial 2026): year-DOI reconciliation
- Final corpus: N = 9,413 main (2005-2025) + N = 304 partial 2026 = N = 9,717 total
- Field coverage table (DOI 87.1%, Abstract >= 50 chars 97.0%, etc.)
- Cross-database coverage (1-DB / 2-DB / 3-DB / 4-DB record counts)

---

## §2.3 Topic modeling

[TODO -- Day 17 Block B]

Subsections to cover:
- SPECTER2 (allenai/specter2) for title+abstract embedding (768-dim)
- UMAP for dimensionality reduction (target 15D, n_neighbors=30, min_dist=0.0, metric=cosine)
- HDBSCAN clustering (min_cluster_size=80, min_samples=10, cluster_selection_method=eom)
- LLM-assisted topic naming (gpt-4o-mini, 5 sampled documents per cluster, 3-pass prompt with cross-cluster term decontamination)
- Resulting 39-40 thematic clusters; -1 noise cluster handling
- Embedding caching (avoid re-runs across script iterations)

---

## §2.4 LLM-based mechanism extraction

[TODO -- Day 17 Block C]

Subsections to cover:
- Schema v3 design (16 mechanism categories, structured JSON output, validation enums)
- LLM choice: openai/gpt-4o-mini (rationale: cost/accuracy balance for ~9.7k abstracts)
- Provider routing via OpenRouter (failover and IP diagnostics)
- Stratified sampling pre-benchmark (year + topic + journal-tier strata, n=200 for human-eval)
- Full corpus extraction (3,100 returned interactions after parsing; ~33% of abstracts contain extractable HDI claims)
- Validation subset (residual inspection, target normalization, re-extraction of "other" category)
- Cache architecture (raw response per record stored as parquet; deterministic rerun)

---

## §2.5 Bibliometric and citation-burst analyses

[TODO -- Day 17 Block D]

Subsections to cover:
- bibliometrix R package (Aria & Cuccurullo 2017, *J Informetrics* 11(4):959-975)
- Why a WoS-only subset (n = 3,091 of 9,413 main): bibliometrix tooling assumes WoS-format fields (C1 affiliations, TC citation counts, ID/DE keyword separation); cross-database harmonization for these fields was infeasible with the same standardization confidence
- Conventions applied: annual production curve, Lotka's law (author productivity), Bradford's law (journal core-zone partitioning), thematic map (centrality x density), three-fields plot (authors-keywords-journals)
- CiteSpace 6.4.R1 (Chen 2006, *J Am Soc Inf Sci Technol* 57(3):359-377)
- Citation-burst detection: Kleinberg's burst algorithm (Kleinberg 2003) with gamma = 1.0, minimum burst duration = 2 years
- Same WoS subset used (CiteSpace requires WoS export format)
- 4 historical eras identified from burst clustering
- Cross-tool consistency check between bibliometrix three-fields and CiteSpace burst-keyword overlap

---

## §2.6 Statistical enrichment analyses

[TODO -- Day 17 Block E]

Subsections to cover:
- Fisher exact test for each cell of topic x mechanism contingency table (2x2 collapsed)
- Benjamini-Hochberg FDR correction (q<0.05 threshold; strong-enrichment additional filter: OR>2 AND obs>=5)
- Era stratification (Scheme B disjoint periods: 2005-2013 / 2014-2019 / 2020-2026)
- 8-class trajectory typology (STABLE / FADING / EMERGING / DECLINING / TRANSIENT / WEAK_NONE / RISING / BIMODAL)
- Three-tier herbal taxonomy enrichment (Family >= 10 records; Species >= 10; Compound >= 5; in_map=True restriction)
- Cross-tier chain consistency typology (8 chain classes: FULL_CHAIN / FAMILY_PERVASIVE / SPECIES_SPECIFIC / FAMILY_SPECIES_NO_COMPOUND_DATA / F_S_COMPOUND_NOT_SIG / etc.)
- All analyses on the integrated 9,413 main corpus (no WoS-subset restriction); rationale: enrichment tests depend on topic + mechanism labels available across all DBs