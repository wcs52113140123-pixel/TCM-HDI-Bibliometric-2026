# Abstract — Draft v2 (BiB submission, dual-emphasis)

> Day 22 reframe. Dual-emphasis (methodology + TCM-HDI findings) modeled on:
> - LORE (BiB 2025, bbaf070, Li et al.) — framework-naming + 4-advantages structure
> - Zhao 2024 (BiB, bbad445) — clinical-anchor opening
> Abstract proper ~280 words (unstructured, matching LORE precedent).
> Key Points 3 bullets — BiB standard.

---

## Title

**From bibliometrics to mechanism: a four-method computational framework for systematic analysis of the traditional Chinese medicine herbal-drug interaction literature (2005-2026)**

## Abstract

Herbal-drug interactions (HDIs) in traditional Chinese medicine (TCM) generate substantial pharmacological complexity, yet the structural patterns of mechanism reporting at the corpus scale remain poorly characterized. Bibliometric analyses provide aggregate citation-graph views but lack mechanism granularity, while large-language-model (LLM)-based extraction enables mechanism structuring but has not been integrated with bibliometric and statistical enrichment frameworks at scale in pharmacological domains. Here we present a four-method computational framework—bibliometric convention analysis, Kleinberg citation-burst detection, Fisher exact topic × mechanism enrichment with Benjamini-Hochberg FDR correction on HDBSCAN-derived topic clusters and Schema v3 LLM-extracted mechanism categories, and three-tier herbal-taxonomy stratification—applied to an integrated 9,717-record TCM-HDI corpus assembled from Web of Science, Scopus, OpenAlex, and PubMed (2005-2026). The TCM-HDI literature is statistically bifurcated into non-overlapping pharmacokinetic and pharmacodynamic research spaces, with maximum mutual exclusion q = 10⁻⁴⁷ (topic anticancer × CYP_inhibition: 5 observed against 99.7 expected), and the bifurcation is a 22-year structural invariant rather than a recent trend, holding across all three publication eras tested. St. John's wort × CYP3A4 induction is independently recovered by all four methods, with monotonically increasing odds ratios across resolution tiers (family OR = 14.20, species OR = 14.71, compound OR = 18.73), establishing a paradigm case for cross-method validation. A mechanism-specific natural resolution layering was identified: CYP induction concentrates at the chemical-compound tier, UGT inhibition at the botanical-species tier, and transporter modulation at the botanical-family tier, indicating that different mechanism classes call for different inferential targets. The framework generalizes to any biomedical literature corpus equipped with citation-graph and controlled-vocabulary annotation, supporting resolution-aware approaches to drug-interaction risk stratification beyond TCM.

## Key Points

- We present a four-method computational framework—bibliometrics, citation-burst detection, LLM-augmented Fisher enrichment, and three-tier taxonomic stratification—applied to an integrated 9,717-record TCM herbal-drug interaction corpus, identifying a statistically extreme PK-PD bifurcation (q = 10⁻⁴⁷) that is a 22-year structural invariant rather than a recent trend.

- We identify a mechanism-specific natural resolution layering as a discoverable property of the pharmacology literature: CYP induction signals concentrate at the chemical-compound tier, UGT inhibition at the botanical-species tier, and transporter modulation at the botanical-family tier—different mechanism classes intrinsically call for different inferential resolution.

- The framework, source code, and Schema v3 mechanism taxonomy are released as open assets and generalize to any biomedical literature corpus with citation-graph and controlled-vocabulary annotation, supporting resolution-aware drug-interaction risk stratification beyond traditional Chinese medicine.