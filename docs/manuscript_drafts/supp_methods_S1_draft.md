# Supplementary Methods S1 — Corpus integration and analytical pipeline details

> Created Day 31 (compress-bib-5k) — holds detail moved out of main §2.1, §2.2, §2.3, §2.5 for ≤5,000 word main-body compliance.
> Main-text §2 retains method overview + key parameters; this file holds full reproducibility detail.

---

## S1.1 Database search strategy and Boolean queries

The four-database design reflects three complementary objectives: maximizing coverage of biomedical and pharmacology journals via curated subscription services (WoS, Scopus); capturing open-metadata reach into regional and Chinese-language TCM sources via OpenAlex; and ensuring complete coverage of clinical and pharmacological case reports indexed by the NLM via PubMed. WoS and Scopus were used in combination rather than substitution because their journal-coverage and citation-indexing scopes are known to differ for non-English regional pharmacology literature; OpenAlex provided open reach into sources underindexed by subscription databases; PubMed contributed the MeSH controlled vocabulary for biomedical concept matching.

### TCM-term axis
- Free-text TCM terms: "traditional Chinese medicine", "Chinese herbal medicine", "Chinese materia medica", "TCM herb", "Chinese formula"
- Botanical Linnaean genera prominently used in TCM: *Hypericum*, *Ginkgo*, *Panax*, *Astragalus*, *Glycyrrhiza*, *Salvia*, *Curcuma* (and others)
- Named TCM formula categories

### Herb–drug interaction axis
- Interaction predicates: "drug interaction", "herb–drug interaction", "pharmacokinetic interaction", "pharmacodynamic interaction"
- Drug-metabolizing targets: CYP1A2, CYP2C9, CYP2C19, CYP2D6, CYP2E1, CYP3A4, UGT family
- Transporter targets: P-glycoprotein, PXR, BCRP
- Bioavailability and absorption-modulation vocabulary

### Database-specific syntax
- **WoS**: Topic (TS=) field searches across title, abstract, author keywords, and KeywordPlus
- **Scopus**: TITLE-ABS-KEY field searches
- **OpenAlex**: full-text-indexed metadata with concept tagging
- **PubMed**: MeSH-augmented combinations with explosion

### Date window
- Records dated 1 January 2005 through 31 December 2025 retained as main 21-year complete-year corpus
- Records dated 2026 retained as partial-year extension (2026 indexing incomplete at search execution: 14 May 2026)

[Note: Full executable Boolean query strings per database are deposited in the project repository.]

---

## S1.2 Five-stage deduplication and precision-filtering pipeline

The pipeline was deliberately ordered so that high-confidence identifier-based deduplication (Stages 1–2) preceded text-similarity deduplication (Stage 3), which in turn preceded the precision filter applied specifically to OpenAlex (Stage 4) and the cross-file reconciliation between the main and 2026-partial subcorpora (Stage 5).

### Stage 1 — Import and normalize
Imported per-database raw exports and normalized field schemas across WoS-Core, Scopus, OpenAlex, and PubMed formats.

### Stage 2 — DOI deduplication
Primary key: digital object identifier (DOI), lowercased with `https://doi.org/` URL prefixes stripped for canonical comparison. Records without a DOI advanced to subsequent stages.

### Stage 3 — Fuzzy title deduplication
Token-level Levenshtein similarity, threshold ≥ 0.95. Blocked on publication year and first-author surname to constrain the comparison space. Follows the default tolerance (`tol = 0.95`) implemented in the bibliometrix R package, substantially reducing false-merge risk vs. naive all-pairs comparison.

### Stage 4 — OpenAlex precision filter
Addresses the higher false-positive rate observed in OpenAlex retrievals during pilot inspection. Four-block classification of OpenAlex records by title and abstract content:
- **B1**: matched TCM × drug × interaction conjunction — retained
- **B2**: matched TCM × interaction but not drug — retained
- **B3**: matched TCM × CYP/transporter but no explicit interaction predicate — retained
- **B0**: matched none of the three patterns — dropped (98 records)

### Stage 5 — Cross-file reconciliation
Resolved records independently retrieved into both the main 2005–2025 subcorpus and the 2026 partial-year extension:
- 25 main-corpus records dated 2026 reassigned/dropped: 24 dropped as duplicates of partial-corpus entries; 1 reassigned to the partial subcorpus
- 13 partial-corpus records dropped due to DOI overlap with main-corpus entries

### Final corpus
- 9,413 main records (2005–2025) + 304 partial 2026 records = 9,717 total
- Field coverage: 87.1% DOI, 97.0% abstract (≥ 50 characters), 100% publication year
- Multi-database overlap: 61.4% in 1 database, 16.6% in 2, 10.1% in 3, 11.9% in 4

---

## S1.3 Topic modeling: full BERTopic configuration

The three-stage embedding-and-clustering pipeline replaces classical bag-of-words topic models (LDA, NMF) with embedding-space clustering on the rationale that scientific abstracts use specialized terminology with high lexical variation but compact semantic signature, which dense pre-trained scientific-paper encoders capture more efficiently than sparse-token methods.

### SPECTER2 document embedding
- Model: `allenai/specter2` (Transformer encoder pre-trained on scientific paper citation contexts)
- Output: 768-dimensional embedding per (title, abstract) pair
- Selection rationale: pre-training objective explicitly optimizes scientific-document similarity rather than generic semantic similarity
- Input format: title and abstract concatenated with a separator token before encoding (SPECTER2 reference protocol)
- Caching: embeddings computed once and cached to disk as a record-keyed parquet file for deterministic re-runs of downstream clustering

### UMAP non-linear dimensionality reduction
- Algorithm: Uniform Manifold Approximation and Projection
- Parameters: `n_neighbors = 30`, `min_dist = 0.0`, `metric = "cosine"`, output dimension 15
- Rationale: prioritizes preservation of local neighbourhood structure (appropriate for downstream density-based clustering) over global geometric fidelity

### HDBSCAN density-based clustering
- Algorithm: Hierarchical Density-Based Spatial Clustering of Applications with Noise
- Parameters: `min_cluster_size = 80`, `min_samples = 10`, `cluster_selection_method = "eom"`
- Rationale for min_cluster_size = 80: produces thematically interpretable clusters at corpus scale. Smaller thresholds produced unstable micro-clusters in pilot runs; larger thresholds collapsed distinct thematic subareas into composite groups.
- Output: 39 thematic clusters (cluster ids 0–38); 3,437 records (~36% of corpus) assigned to noise cluster (cluster_id = -1)

### Cluster labeling
1. KeyBERT extracts top n-gram terms per cluster
2. LLM-based decontamination (gpt-4o-mini, OpenAI) given five randomly sampled abstracts from each cluster + the candidate term list, asked to remove terms that appear frequently across multiple clusters (e.g., "study", "method", "analysis")
3. Three iterative passes per cluster to converge on a stable, cluster-distinctive label
4. Output format: space-separated top-three term combinations (e.g., "cyp inhibition / cyp enzymes / cyp isoforms" for cluster #30)

### Noise interpretation
The noise assignment (cluster_id = -1) is an intrinsic feature of density-based clustering and identifies records whose semantic position is not sufficiently close to any dense neighbourhood; it is not a clustering failure and is retained as a corpus property. Downstream analyses operated on the 39 thematic clusters and treated the -1 noise as a separate analytical category, with the Fisher enrichment analysis additionally restricting to the 37 clusters with sufficient mechanism-extraction support (§2.6).

---

## S1.4 Bibliometric and citation-burst analytical configurations

### bibliometrix R-package analyses
Default parameter values throughout. Outputs:
- Annual publication production curves
- Lotka's-law author productivity distributions (slope α and R² goodness-of-fit)
- Bradford's-law journal core-zone partitioning (multiplier and zone counts)
- Thematic map (centrality × density quadrant plot of keyword clusters)
- Three-fields plot (authors–keywords–journals correspondence)

### CiteSpace v6.4.R1 citation-burst detection
- Algorithm: Kleinberg's burst detection
- Time slicing: 22 one-year slices spanning 2005–2026
- Node selection: g-index (k = 25)
- Link strength: cosine
- Network pruning: Pathfinder
- Cluster detection: modularity-based
- Label extraction: log-likelihood-ratio (LLR)
- Burst parameters: γ = 0.5, minimum burst duration 2 years

### Rationale for γ = 0.5 (vs. default γ = 1.0)
Pilot inspection with the more conservative default γ = 1.0 produced very few bursts in this corpus, missing several keywords that visibly underwent rise-and-fall dynamics in the annual production data. γ = 0.5 captured these temporal signatures while maintaining bursts within interpretable historical eras.

### Cross-tool consistency check
A check between the bibliometrix three-fields plot and the CiteSpace burst-keyword set independently identified the same historically prominent keywords for the 2005–2012 era—St. John's wort, ginkgo biloba, milk thistle, and grapefruit juice—supporting the analytical robustness of each method.