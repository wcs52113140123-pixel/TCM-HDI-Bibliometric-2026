# Abstract — Draft

> Living draft. Day 20 Block C. Structured 4-section abstract (~280 words), compatible with Frontiers in Pharmacology and Pharmacological Research conventions.

---

## Abstract

**Background**: Traditional Chinese medicine (TCM) preparations are widely used alongside conventional pharmacotherapy, generating a substantial body of literature on herbal–drug interactions (HDIs) with clinical implications for risk stratification. The internal structure of this literature—which mechanisms attract sustained attention, which herbs dominate the mechanistic record, and how research focus has shifted over time—has not previously been characterised at the corpus level through integrated bibliometric and structured mechanism extraction.

**Methods**: We assembled an integrated 9,717-record corpus from Web of Science, Scopus, OpenAlex, and PubMed (publication window 2005–2026) and applied four complementary analytical methods: bibliometric convention analysis (bibliometrix R package), citation-burst detection (CiteSpace, Kleinberg algorithm), Fisher exact enrichment of HDBSCAN-derived topic clusters against large-language-model-extracted mechanism categories with Benjamini–Hochberg FDR correction, and a three-tier herbal-taxonomy enrichment analysis at the botanical-family, species, and chemical-compound levels.

**Results**: The TCM-HDI literature is statistically bifurcated into non-overlapping pharmacokinetic and pharmacodynamic research spaces, with maximum mutual exclusion q = 10⁻⁴⁷ (topic #11 anticancer × CYP_inhibition: 5 observed against 99.7 expected). The bifurcation is a 22-year structural invariant rather than a recent trend, with 18 of 40 trajectory-classifiable cells significant in all three publication eras tested. St. John's wort × CYP3A4 induction is independently recovered by all four methods, with monotonically increasing odds ratios across resolution tiers (family OR = 14.20, species OR = 14.71, compound OR = 18.73). A mechanism-specific natural resolution layering was identified: CYP induction concentrates at the compound tier, UGT inhibition at the species tier, and transporter modulation at the family tier.

**Conclusions**: The four-method triangulation framework introduced here is portable beyond TCM and supports a resolution-aware approach to herbal–drug interaction risk stratification, with different mechanism classes calling for different inferential targets.