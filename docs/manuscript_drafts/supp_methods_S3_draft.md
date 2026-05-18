# Supplementary Methods S3 — Statistical enrichment methodology

> Created Day 31 (compress-bib-5k) — holds detail moved out of main §2.6 for ≤5,000 word main-body compliance.
> Main-text §2.6 retains 3-stratification overview + key sample sizes; this file holds full statistical reproducibility detail.

---

## S3.1 Contingency-table construction

### Static topic × mechanism analysis
- Contingency matrix: 37 × 16
- Input: N = 1,738 (record, mechanism) pairs spanning 1,662 unique records
- Excluded: 2 HDBSCAN topics with insufficient mechanism-extraction support
- Per cell: 2 × 2 tabulation (in-topic vs. not-in-topic) × (has-mechanism vs. no-mechanism)
- Statistical test: two-sided Fisher exact test using exact hypergeometric distribution
- Total simultaneous tests: 592

### Era-stratified topic × mechanism × era analysis
- Same 1,738 (record, mechanism) pairs partitioned into three disjoint publication eras (Scheme B):

| Era | Year range | Pairs |
|-----|------------|-------|
| P1  | 2005–2013  | 517   |
| P2  | 2014–2019  | 687   |
| P3  | 2020–2026  | 534   |

- Era boundaries chosen by two simultaneous criteria: alignment with the CiteSpace burst-era structure reported in §3.2; approximate balance in subsample size across eras

### Three-tier herbal-taxonomy analysis
- Separate contingency matrices at botanical-family, species, and chemical-compound tiers
- Minimum-occurrence thresholds:
  - Families: 24 meeting n ≥ 10
  - Species: 32 meeting n ≥ 10
  - Compounds: 23 meeting n ≥ 5
- Rationale for compound-tier lower threshold: heterogeneous per-compound record distribution (median ~1.8 records per compound); single-compound mechanistic studies do not aggregate per-compound the way per-species or per-family studies do
- All three tiers restricted to the same 1,676-record pool with at least one mapped taxonomic identifier (`in_map = True` restriction), so resolution-tier comparisons across the same chain of identifiers (family → species → compound) reflect biological resolution rather than coverage-driven artefacts
- Total cells across three matrices: 1,241 (384 + 512 + 345)

---

## S3.2 Benjamini–Hochberg FDR correction

BH-FDR correction applied across simultaneous tests within each analysis:
- Static topic × mechanism: across all 592 cells
- Era-stratified: BH applied per era within the (topic × mechanism × era) family
- Three-tier herbal: across all 1,241 cells of the three matrices simultaneously, producing a single corpus-wide q-value distribution comparable across tiers

### Significance thresholds
- Cell-level significance: q < 0.05
- Strong enrichment additionally required: OR > 2 and ≥ 5 observed in-topic-with-mechanism records
- Strong depletion additionally required: OR < 0.5 and ≥ 5 expected in-topic-with-mechanism records

### Haldane–Anscombe correction (visualization only)
For the Figure 8 heatmap, log2 odds ratio was computed using a Haldane–Anscombe correction (adding 0.5 to all four cells of the 2 × 2 table) to avoid undefined values when cells contained zero observations. This correction was applied **only to the visualization** and was not used to compute Fisher p-values, which remained based on the exact hypergeometric distribution.

---

## S3.3 Trajectory classification (era-stratified)

Across the 40 cells reaching significance in at least one era, an eight-class trajectory typology was applied:

| Class       | Definition                                                                |
|-------------|---------------------------------------------------------------------------|
| STABLE      | Significant in all three eras                                             |
| FADING      | Significant in P1 only                                                    |
| TRANSIENT   | Significant in P2 only                                                    |
| EMERGING    | Significant in P3 only                                                    |
| DECLINING   | Monotonically decreasing observed count across eras                       |
| RISING      | Monotonically increasing observed count across eras                       |
| BIMODAL     | Significant in P1 and P3 but not P2                                       |
| WEAK_NONE   | Significant in ≥ 1 era but with no consistent across-era pattern          |

---

## S3.4 Three-tier herbal-taxonomy chain typology

For each herb chain (family → species → compound for the same herb), an eight-class chain typology classified the cross-tier resolution pattern:

| Class                  | Definition                                              |
|------------------------|---------------------------------------------------------|
| FULL_CHAIN             | Significant at all three tiers for the same mechanism   |
| FAMILY_PERVASIVE       | Significant only at family tier                         |
| SPECIES_SPECIFIC       | Significant only at species tier                        |
| COMPOUND_ONLY          | Significant only at compound tier                       |
| FAMILY_AND_SPECIES     | Significant at family and species but not compound      |
| SPECIES_AND_COMPOUND   | Significant at species and compound but not family      |
| FAMILY_AND_COMPOUND    | Significant at family and compound but not species      |
| NONE                   | Not significant at any tier                             |

---

## S3.5 Multi-method anchoring convention

Findings significant in two or more methods (bibliometric, citation-burst, static Fisher, era-stratified Fisher) are reported as multi-method-anchored and summarized in Table 1 (§3.3). Cases significant in one method only are explicitly flagged as method-specific. This convention provides a consistent reporting standard for the trade-off between statistical sensitivity (more findings) and methodological robustness (more durable findings).