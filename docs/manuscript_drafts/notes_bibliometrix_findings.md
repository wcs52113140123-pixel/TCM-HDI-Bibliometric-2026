# Day 12 B — bibliometrix Findings Notes

> Living draft. Findings from the WoS-subset bibliometrix convention
> check (3,091 records) cross-referenced against the Python main
> analysis (integrated 9,438 records).

---

## Why this analysis exists (Methods §2.x)

The main TCM-HDI analysis uses a custom-integrated 4-database corpus
(WoS + Scopus + PubMed + OpenAlex; n = 9,438 main + 316 partial 2026)
processed via a Python pipeline. As a **methodological convention
check**, the WoS-only subset (n = 3,091) was re-analyzed with the
bibliometrix R package (4.x), which provides field-standard
implementations of Lotka's Law, Bradford's Law, three-fields plots,
and Callon-style thematic maps.

The bibliometrix subset is a strict subset of the main corpus
(WoS-indexed records only), so any divergence in derived statistics
reflects (a) database coverage differences and (b) author
disambiguation strategy (bibliometrix D1 FINI vs. Python D2
FINI+Institution).

---

## Finding 1 — Citation density cross-validation

| Metric | WoS subset (3,091) | Integrated (9,438) | Conclusion |
|---|---|---|---|
| Total citations | 81,637 | 242,765 | WoS = 33.6% of integrated |
| Records | 3,091 | 9,438 | WoS = 32.7% of integrated |
| **Avg cit / doc** | **26.41** | **25.72** | **Difference: 2.7%** ✓ |

**Interpretation**: WoS-indexed and non-WoS-indexed records have
near-identical mean citation density (26.41 vs. 25.72 cit/doc). This
demonstrates that the 4-database integration broadened coverage
without introducing systematic citation-density bias.

---

## Finding 2 — Lotka's Law (author productivity)

| Parameter | bibliometrix (WoS / D1) | Python (integrated / D2) | Interpretation |
|---|---|---|---|
| alpha (Beta) | 2.38 | 2.63 | Both > 2.0 → **super-Lotka** |
| R^2 | 0.960 | 0.957 | Fit quality nearly identical |
| Single-paper authors | 72.6% | (n/a) | Long-tail dominant |

**Interpretation**: TCM-HDI exhibits a super-Lotka author productivity
distribution under both disambiguation schemes. The 0.25-unit gap in
alpha (2.38 vs. 2.63) is attributable to disambiguation strategy:
bibliometrix's D1 (FINI only) merges same-name authors, inflating
high-productivity author counts and depressing alpha. The Python D2
scheme (FINI + Institution) separates same-name authors, raising
alpha. R^2 stability across schemes (0.960 vs. 0.957) confirms the
underlying long-tail shape is robust to disambiguation choice.

---

## Finding 3 — Bradford's Law (journal scattering)

| Parameter | bibliometrix (WoS) | Python (integrated) |
|---|---|---|
| Total journals | 751 | 2,225 |
| Zone 1 (core) | **13** | 25 |
| Zone 2 (mid) | **81** | 224 |
| Zone 3 (periph) | **657** | 1,976 |
| Z1->Z2 multiplier | 6.23 | 8.96 |
| Z2->Z3 multiplier | 8.11 | 8.82 |
| **Geometric mean** | **7.11** | **8.89** |
| Z1 / total | 1.73% | 1.12% |

**Interpretation**: Both corpora follow a Bradford geometric
progression. The WoS subset's lower multiplier (7.11 vs. 8.89)
reflects WoS's pre-selected inclusion criteria, which exclude long-tail
peripheral journals (Z3) that PubMed/OpenAlex bring into the
integrated corpus. Both multipliers far exceed the classical Bradford
multiplier of ~5, indicating **strong publication concentration in
the TCM-HDI field**.

### Core-zone anomalies for Methods/Discussion

The Bradford Zone 1 (core 13 journals in the WoS subset) reveals a
quality-heterogeneous landscape:
JOURNAL OF ETHNOPHARMACOLOGY        264   ✓ TCM flagship
FRONTIERS IN PHARMACOLOGY           110   ✓ submission target validated
EVIDENCE-BASED COMPL ALT MEDICINE    96   ⚠ post-publication integrity concerns
PHYTOTHERAPY RESEARCH                78   ✓ phytomedicine core
PHYTOMEDICINE                        77   ✓ phytomedicine core
MOLECULES                            71   ⚠ MDPI low-selectivity venue
XENOBIOTICA                          60   ✓ DME core
CURRENT DRUG METABOLISM              58   ✓ DME core
LATIN AMERICAN JOURNAL OF PHARMACY   51   ⚠ regional concentrated submission
DRUG METABOLISM AND DISPOSITION      48   ✓ DME flagship
PLANTA MEDICA                        46   ✓ phytomedicine core
PHARMACEUTICAL BIOLOGY               44   ✓
J PHARM AND BIOMED ANALYSIS          34   ✓ analytical
**Three flagged anomalies** (10/13 are clean TCM/phytomedicine/DME
core; 3 warrant Discussion treatment):

1. *Evidence-Based Complementary and Alternative Medicine* — large
   retraction wave from 2019 onward; many TCM papers affected.
2. *Molecules* — MDPI mega-journal with low selectivity; legitimate
   natural-product chemistry but high heterogeneity.
3. *Latin American Journal of Pharmacy* — small regional venue with
   surprising rank-9 entry, suggesting concentrated submission
   pattern from a single research network.

**Suggested Discussion line**: "Bradford core zone composition
reveals heterogeneous quality in the TCM-HDI publication ecosystem,
with three core journals (ECAM, Molecules, Latin American Journal of
Pharmacy) representing post-publication integrity concerns,
mega-journal publishing, or regional submission concentration. This
distribution should be considered when interpreting field-level
citation metrics."

---

## Finding 4 — Thematic structure (Callon centrality-density map)

bibliometrix's thematic map identified **4 clusters** from 233
KeyWords Plus terms (minfreq=5, n=250). Quadrant assignment via
rank-based median split:

| # | Cluster (top 3 words) | Quadrant | rcent | rdens | freq | n keywords |
|---|---|---|---|---|---|---|
| 1 | in-vitro / metabolism / inhibition | **Q4 Basic** | 4 | 2 | 5,489 | 91 |
| 2 | expression / TCM / cells | **Q4 Basic** | 3 | 1 | 2,506 | 57 |
| 3 | p-glycoprotein / SJW / grapefruit | **Q2 Niche** | 1 | 4 | 1,553 | 34 |
| 4 | herb-drug interactions / drug-int / alt medicine | **Q2 Niche** | 2 | 3 | 2,156 | 51 |

### Three Discussion-worthy observations

**(a) Q1 Motor quadrant is empty.** TCM-HDI lacks a "well-developed
and central" dominant paradigm. All developed themes (Q2 Niche) are
isolated; all central themes (Q4 Basic) are thematically
underconsolidated. This is a **fragmented-but-foundationally-
consolidated** field morphology.

**(b) Classic safety cases form a structural niche.** The Q2 cluster
containing P-glycoprotein, St. John's wort, grapefruit juice, ginkgo
biloba, hypericum perforatum, milk thistle, panax ginseng, and
pregnane-X-receptor represents the canonical 1990s-2000s HDI safety
literature. Its high internal density + low centrality means this
literature has formed a **closed citation community** that mainstream
new-mechanism research no longer engages with deeply.

**(c) Network-pharmacology vocabulary is emerging as a Basic theme.**
The "expression / TCM / cells / apoptosis / oxidative stress /
multidrug-resistance / cancer / inflammation" cluster represents
broader pharmacology vocabulary entering TCM-HDI literature, with
moderate centrality but very low density (not yet thematically
consolidated). This is the **incipient paradigm shift** toward
network-pharmacology / systems-toxicology framings, but it has not
yet matured into a Motor theme.

### Draft Discussion §4.x prose

> *"The thematic structure of TCM-HDI literature reveals a fragmented
> landscape. Classical safety case-driven research (St. John's wort,
> grapefruit juice, P-glycoprotein modulators) forms a well-developed
> but isolated niche, while mainstream in-vitro metabolism research
> remains structurally central yet thematically underconsolidated,
> with no fully-developed motor theme bridging the two. Emerging
> molecular-biology vocabulary (gene expression, apoptosis, oxidative
> stress, multidrug-resistance) is entering as a transitional
> cluster, suggesting an incipient but incomplete paradigm shift
> toward network-pharmacology framings."*

---

## Finding 5 — Three-Field Plot (country -> author -> keyword)

Three-field plot saved as interactive HTML
(`fig_threeFields_country_author_keyword.html`, 3.6 MB) and static
PDF (browser print-to-PDF export). Top countries connect to top
authors, who in turn connect to top keywords; flow widths reveal:

- *Chinese institutional networks* dominate left-axis; multiple
  high-productivity authors (Duan J, Xu Y, Wang W) cluster around
  TCM-PK keywords
- *US authors* connect more heavily to keywords on grapefruit juice,
  warfarin, and CYP3A4 (regulatory and clinical-PK research traditions)
- *European contributors* (Germany, UK, Italy) bridge to "in-vitro
  metabolism" keywords (mechanistic phytochemistry traditions)

This is a useful supplementary figure for paper §3 but not a primary
finding — interpret as descriptive context.

---

## Files produced (Day 12 B)
results/figures_bibliometrix/
Intermediate (excluded from git via .gitignore):
M.rds                                          (10.3 MB)
biblio_results.rds                              (430 KB)
themat.rds                                      (~50 KB)Figures:
fig2_alt_annual_production.{pdf, png}           (Fig 2 alt + 2026 annotation)
fig2_alt_avg_citations_per_article.{pdf, png}   (extra)
figS_alt_lotka.{pdf, png}                       (Fig S Lotka alt)
figS_alt_bradford.{pdf, png}                    (Fig S Bradford alt)
fig_thematicMap_keywords.{pdf, png}             (custom ggrepel layout)
fig_threeFields_country_author_keyword.html     (interactive)
fig_threeFields_country_author_keyword.pdf      (browser-exported)Tables:
table_bibliometrix_top_sources.csv              (top 20 journals)
table_bibliometrix_top_authors.csv              (top 20 authors)
table_bibliometrix_top_countries.csv            (top 20 countries)
table_bibliometrix_top_cited_papers.csv         (top 20 papers)
table_lotka_fit.csv                             (alpha + R^2)
table_bradford_zones.csv                        (751 journals)
table_thematic_clusters.csv                     (4 clusters)07_bibliometrix_r/
23_bibliometrix_block1_load.R
24_bibliometrix_block2_summary.R
25_bibliometrix_block3_laws.R                     (v2, 4.x compatible)
26_bibliometrix_block4_threeField_thematic.R      (v2, custom plot)
---

## What this enables downstream

- Paper §2.x Methods: "We additionally re-analyzed the WoS subset
  (n=3,091) using the bibliometrix R package (4.x) for methodological
  convention check..."
- Paper §3.x Results: Fig 2 alt, Fig S Lotka, Fig S Bradford as
  supplementary or main figures (TBD by reviewer preference)
- Paper §4 Discussion: 4 Findings ready to drop in (citation density
  cross-validation, super-Lotka under both schemes, Bradford
  concentration + 3 core-zone anomalies, thematic Q1-empty +
  Q2-isolated-niche finding)
- Day 12 A (CiteSpace): orthogonal analysis on same WoS data
  (keyword burst + timezone view, Fig 7)