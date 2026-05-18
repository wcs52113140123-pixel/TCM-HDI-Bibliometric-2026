# Supplementary Results R1 — Corpus descriptives and analytical detail tables

> Created Day 31 (compress-bib-5k) — holds tabular and descriptive detail moved out of main §3.1, §3.2, §3.3, §3.5 for ≤5,000 word main-body compliance.
> Main-text §3 retains 3 substantive findings (PK-PD bifurcation §3.4, SJW four-method anchor §3.6, mechanism resolution layering §3.6).

---

## R1.1 Corpus descriptives — full detail

### Field coverage
- DOI: 87.1%
- Abstract (≥ 50 characters): 97.0%
- Publication year: 100.0%

### Cross-database coverage
- 5,797 records (61.4%) in a single database
- 1,567 (16.6%) in two databases
- 949 (10.1%) in three databases
- 1,125 (11.9%) in all four databases

### Author productivity — Lotka distribution

| Disambiguation scheme | Corpus | α | R² | Single-paper authors |
|---|---|---|---|---|
| D1 (first-initial + surname) | WoS-3091 | 2.38 | 0.960 | 72.6% |
| D2 (D1 + institutional affiliation) | Integrated | 2.63 | 0.957 | — |

Both exceed the classical Lotka value (α = 2.0), indicating concentration of output among a small high-productivity author subset. The 0.25-unit α gap between schemes is attributable to disambiguation policy: surname–initial collisions under D1 merge same-name authors and inflate high-productivity bins (depressing α), while D2 separates these collisions and recovers a steeper tail. Near-identical R² (Δ = 0.003) confirms the long-tailed shape is robust to disambiguation choice.

### Journal scattering — Bradford zones

| Corpus | Unique journals | Core / Mid / Peripheral | Multiplier |
|---|---|---|---|
| WoS-3091 | 751 | 13 / 81 / 657 | 7.11 |
| Integrated | 2,225 | 25 / 224 / 1,976 | 8.89 |

Both multipliers exceed the classical Bradford value (~5), indicating strong publication concentration.

### Bradford core composition (WoS-3091; 13 core journals)

**Flagship venues:**
- *Journal of Ethnopharmacology* (n = 264)
- *Frontiers in Pharmacology* (n = 110)
- *Phytotherapy Research* (n = 78)
- *Phytomedicine* (n = 77)
- *Drug Metabolism and Disposition* (n = 48)

**Methodologically heterogeneous (interpretive caution):**
- *Evidence-Based Complementary and Alternative Medicine* (n = 96) — substantial post-2019 retraction wave
- *Molecules* (n = 71) — MDPI mega-journal admitting chemically-focused work of uneven topical fit
- *Latin American Journal of Pharmacy* (n = 51) — concentrated regional submission pattern

### Three-fields plot (countries × authors × KeyWords Plus)

- **China**: dominant production around TCM pharmacokinetic vocabulary
- **United States**: more strongly connected to grapefruit, warfarin, and CYP3A4 keywords (clinical-pharmacokinetics tradition)
- **Europe (Germany, UK, Italy)**: bridge to in-vitro metabolism keywords (mechanistic phytochemistry tradition)

---

## R1.2 Cluster temporal trajectories — full detail

### CiteSpace network properties (WoS-3091; 22 one-year slices, 2005–2026)
- 667 nodes, 3,336 edges
- Density: 0.015
- 99% of nodes (n = 663) in largest connected component
- Modularity Q = 0.3802 (> 0.3 standard for clear community structure)
- Weighted silhouette S = 0.6935 (> 0.5 standard; approaching 0.7 high-quality benchmark)

### Modularity-based community detection (11 clusters of ≥ 10 members)

| Region | Cluster IDs | Combined members | LLR vocabulary |
|---|---|---|---|
| CAM context | #0 | 96 | dietary supplement |
| Classical drug-metabolising enzymes | #2 + #4 + #8 | 192 | metabolizing enzyme / HLM / aspirin hydrolysis |
| TCM-specific herb and product | #1 + #3 + #6 + #10 | 231 | kaempferia / astragalus / evodia / aidi injection |
| Systems pharmacology | #5 + #7 + #9 | 144 | network pharmacology / IBD model / LPS toxicity |

### Cluster mean-year migration
- Earliest: cluster #4 (HLM) — mean year 2010
- Latest: cluster #10 (aidi injection) — mean year 2017
- Seven-year migration consistent with Era 1 → Era 4 burst trajectory

### Full top-burst keywords per era

**Era 1 (2005–2012)**: St. John's wort 27.01, herb–drug interactions 13.1, ginkgo biloba 9.72, milk thistle 7.78, grapefruit juice 6.97, dietary supplements 6.2

**Era 2 (2010–2018)**: tandem mass spectrometry 10.18, multidrug resistance 7.94, gene-expression 7.52, glucuronidation 7.07

**Era 3 (2017–2022)**: mice 7.28, transporters 7.03, rat plasma 6.71

**Era 4 (2020–2026, ongoing)**: network pharmacology 27.59, molecular docking 16.1, oxidative stress 10.75, gut microbiota 8.74, inflammation 7.42, natural products 7.3

### Cross-method alignment with thematic-map quadrants
- Q2 Niche ↔ Era 1 (St. John's wort safety-case literature)
- Q4 Basic ↔ Era 4 (network pharmacology / systems biology vocabulary)

---

## R1.3 Method-specific signals — extended notes

These findings appear in only one analytical method (Methods = 1 in Table 1 of §3.3) and are explicitly flagged as requiring further validation:

### Bradford core-zone composition anomalies (bibliometrix only)
- Three core journals warrant interpretive caution: retraction-affected EBCAM, mega-journal Molecules, concentrated-regional LatinAmJPharm
- Detail in R1.1 above

### Cluster mean-year migration trajectory (CiteSpace only)
- Seven-year migration from cluster #4 HLM (mean 2010) to cluster #10 aidi injection (mean 2017)
- Single-method signal; not corroborated by static or three-tier analyses

### Warfarin DECLINING and hepatotoxicity-bridge findings (topic-modelling only)
- Topic #6 (warfarin / coumadin) × additive_toxicity P1/P2/P3 = 4/1/0 — see §3.4–§3.5
- Topic #17 (hepatoprotective / hepatotoxicity) multi-mechanism bridge — see §3.4

---

## R1.4 Era-stratified mechanism shift — full trajectory typology

### STABLE backbone (anchoring the PK–PD bifurcation, 18 of 40 cells)

| Topic | Mechanism | P1 | P2 | P3 |
|---|---|---|---|---|
| #30 (cyp inhibition) | CYP_inhibition | 96 | 166 | 76 |
| #24 (inhibition ugt) | UGT_inhibition | 23 | 36 | 6 |
| #32 (drug transporters) | transporter_modulation | stable | stable | stable |
| #9 (pxr cyp) | CYP_induction | stable | stable | stable |
| #11 (anticancer) | receptor_synergism | stable | stable | stable |
| #23 (antimicrobial) | synergistic_efficacy | stable | stable | stable |
| #28 (medicinal plants) | receptor_synergism | stable | stable | stable |

Strong depletions also stable across eras: topic #30 contained 0 records of synergistic_efficacy, receptor_synergism, or absorption_alteration in every era; topic #23 (antimicrobial) showed 0 CYP_inhibition records in every era.

### EMERGING cells (P3 2020–2026 concentration; first visible erosion of bifurcation)

| Topic | Mechanism | P1 | P2 | P3 |
|---|---|---|---|---|
| #27 (metabolites / pharmacokinetic) | absorption_alteration | 0 | 0 | 10 |
| #10 (hormone / testosterone / estrogenic) | signaling_pathway_modulation | 0 | 0 | 7 |
| #20 (cancer / network pharmacology) | signaling_pathway_modulation | 0 | 1 | 5 |

### DECLINING cells

| Topic | Mechanism | P1 | P2 | P3 |
|---|---|---|---|---|
| #6 (warfarin / coumadin) | additive_toxicity | 4 | 1 | 0 |

The canonical warfarin–herb additive-bleeding paradigm—prominent in the SJW–warfarin case literature of the 2000s—has visibly faded.

### Keyword–mechanism lag (high topical frequency, no significant mechanism enrichment)

Two large topics that one might expect to dominate the recent era showed no significant mechanism enrichment in any era:

- **Topic #15 (gut microbiome / microbiota)**: increasingly indexed but LLM mechanism extractor frequently classified content as "unspecified" or "other"
- **Topic #22 (network pharmacology / systems biology)**: same pattern

This is interpretable as a keyword–mechanism lag in which clinical and methodological vocabulary precedes the maturation of structured mechanism reporting in the literature.