# Cover Letter — Briefings in Bioinformatics submission

**Manuscript title:** From bibliometrics to mechanism: a four-method computational framework for systematic analysis of the traditional Chinese medicine herbal-drug interaction literature (2005-2026)

**Submission date:** [DATE — fill at submission]

**To:** Editor-in-Chief, *Briefings in Bioinformatics*

---

Dear Editor-in-Chief,

We submit for consideration the original research manuscript titled "From bibliometrics to mechanism: a four-method computational framework for systematic analysis of the traditional Chinese medicine herbal-drug interaction literature (2005-2026)" for publication in *Briefings in Bioinformatics*.

The work introduces a four-method computational framework that integrates bibliometric structural mining, citation-burst temporal analysis, large-language-model-augmented topic × mechanism enrichment with false-discovery-rate correction, and three-tier taxonomic stratification. The framework addresses a methodological gap between aggregate bibliometric views and mechanism-resolved per-paper analysis that has limited systematic literature-scale analyses in pharmacological domains.

We demonstrate the framework's efficacy through application to an integrated 9,717-record traditional Chinese medicine herbal–drug interaction corpus assembled from four databases over 2005–2026. The application recovers three substantive structural properties not previously documented at the corpus level: a statistically extreme pharmacokinetic–pharmacodynamic bifurcation (maximum mutual exclusion q = 10⁻⁴⁷, a 22-year structural invariant rather than a recent trend); a four-method-anchored St. John's wort × CYP3A4 paradigm case with monotonically increasing odds ratios across taxonomic resolution tiers (family OR = 14.20, species OR = 14.71, compound OR = 18.73); and a mechanism-specific natural resolution layering in which CYP induction concentrates at the chemical-compound tier, UGT inhibition at the botanical-species tier, and transporter modulation at the botanical-family tier.

An independent-annotator validation of the LLM mechanism extraction (Supplementary Methods S2) showed substantial inter-method agreement (Cohen's kappa = 0.612 overall, 0.867 in the high-confidence stratum, 78.7% relaxed agreement when allowing alternative annotator labels), bounding the per-record uncertainty introduced by automated extraction. We release the open-source analytical pipeline, the Schema v3 mechanism taxonomy, and the curated cross-database corpus as reusable assets that complement existing drug-interaction databases. All data, code, and intermediate artifacts are publicly available at [GITHUB URL — fill at submission] under an open-source license.

The framework is designed to be portable beyond the traditional Chinese medicine context to any biomedical literature corpus equipped with citation-graph and controlled-vocabulary annotation. Recent BiB articles applying large language models to disease–gene relation extraction (Li et al., 2025), to drug–drug interaction prediction (Zhao et al., 2024), and to LLM applications across bioinformatics broadly (Lin et al., 2025) establish the journal as a natural venue for methodology-rich, reproducibility-oriented work in this space.

We confirm that this manuscript represents original work, has not been previously published, and is not under consideration for publication elsewhere. The authors have no conflicts of interest to declare. We thank the editors and reviewers in advance for their time.

## Suggested reviewers

We respectfully suggest the following reviewers, none of whom have collaborated with our group within the past five years:

1. **Jia-Hsin Huang, PhD** — Taiwan AI Labs, Taipei, Taiwan — [email: verify from paper PDF, https://doi.org/10.1093/bib/bbaf070]
   Corresponding author of the LORE framework (Li et al., 2025, BiB 26(1) bbaf070); direct methodological peer on LLM-based biomedical relation extraction at corpus scale.

2. **Peng Luo, PhD** — Department of Oncology, Zhujiang Hospital, Southern Medical University, Guangzhou, China; Li Ka Shing Faculty of Medicine, The University of Hong Kong — [email: verify from paper PDF, https://doi.org/10.1093/bib/bbaf357]
   Senior corresponding author of the comprehensive BiB review on LLM applications in bioinformatics (Lin et al., 2025, BiB 26(4) bbaf357); cross-domain expertise in LLM applications across bioinformatics.

3. **Xing Chen, PhD** — School of Science, Jiangnan University, Wuxi 214122, China — [email: verify from paper PDF, https://doi.org/10.1093/bib/bbad445]
   Senior author of the BiB review on drug–drug interaction prediction methodologies (Zhao et al., 2024, BiB 25(1) bbad445); expertise in DDI databases, web servers, and computational benchmarking.

4. **Andy Wai Kan Yeung, DDS, PhD** — Faculty of Dentistry, The University of Hong Kong, Hong Kong SAR, China — [email: verify from paper PDF, https://doi.org/10.3389/fphar.2018.00215]
   First author of the foundational ethnopharmacology bibliometric analysis (Yeung et al., 2018, Front. Pharmacol. 9: 215); expertise in citation analysis and bibliometric methodology applied to natural-product pharmacology.
## Reviewers we ask the editors to exclude

We ask the editors to exclude reviewers in the following categories from consideration: current or past PhD/postdoctoral advisors of any author, current members of any author's laboratory or research group, and direct co-authors on any peer-reviewed publication within the past five years.

---

Sincerely,

**[AUTHOR NAME]**
[POSITION], [AFFILIATION]
[EMAIL] | [ORCID]
[DATE]

**Co-authors (if applicable):**
- [Name 2] — [Affiliation] — [Email]
- [Name 3] — [Affiliation] — [Email]