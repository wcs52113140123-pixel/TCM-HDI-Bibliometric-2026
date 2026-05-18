# Back Matter — Draft v1 (compress-bib-5k, Day 32)

> Mandatory back-matter sections for BiB submission.
> "Use of Large Language Models" disclosure and "Data Availability" statement are required by BiB author guidelines.
> Placeholders (Funding, Author Contributions) for Day 33 fill at submission.

---

## Use of Large Language Models

Large-language-model (LLM)-based pharmacological mechanism extraction was an analytical step in this study, using OpenAI's `gpt-4o-mini` accessed via the OpenRouter API (extraction window May 2026; §2.4). The extraction returned structured JSON conforming to a fixed 16-category Schema v3 mechanism taxonomy. Extraction performance was validated by independent human annotation of a stratified 50-record sample, returning Cohen's κ = 0.612 overall (47 records after excluding 3 annotator-flagged ambiguous cases) and κ = 0.867 in the high-confidence stratum (Supplementary Methods S2). Full prompt text, category definitions, model parameters, and annotator instructions are deposited in the repository linked under Data Availability.

LLM assistance was additionally used for editorial support during manuscript preparation: section structure refinement, prose tightening for word-limit compliance with the journal's 5,000-word ceiling for Problem solving protocols, and consistency checking across cross-references between main text and supplementary materials. All substantive scientific content—including study design, analytical pipeline development, statistical methodology, finding interpretation, figure design, and citation of prior literature—was conceived, conducted, and validated by the author. Every numerical claim and citation in the manuscript was independently verified against the underlying analytical outputs and against the cited primary literature.

This disclosure is made in accordance with the International Society for Computational Biology Policy for Acceptable Use of Large Language Models and the COPE position statement on Authorship and AI. No LLM is listed as an author.

---

## Data Availability

The integrated 9,717-record TCM herbal–drug interaction corpus (publication-year, DOI, title, abstract, journal, country, citation count, and source-database provenance fields), all analytical pipeline code (Python and R), the Schema v3 mechanism-extraction prompts and per-category definitions, all derivative analytical tables (cross-database overlap, Lotka/Bradford fits, BERTopic cluster labels, topic × mechanism enrichment, era-stratified trajectories, three-tier herbal-taxonomy chains), and the figure-rendering scripts supporting the findings of this study are openly available at the project GitHub repository: [https://github.com/wcs52113140123-pixel/TCM-HDI-Bibliometric-2026].

Raw mechanism-extraction outputs from `gpt-4o-mini` are deposited as record-keyed parquet files in the repository (`/data/processed/llm_extraction/`) to permit deterministic re-parsing of the extraction layer without re-querying the model. The independent-annotator validation set (n = 50 records; Supplementary Methods S2) is provided as `s2_master_keyed.xlsx` with both primary and alternative-label assignments retained.

Bibliometric and CiteSpace analyses (§2.5) were performed on the Web of Science Core Collection-only subset (n = 3,091; §2.5 rationale). Under WoS subscription license terms, raw WoS source records cannot be redistributed in the repository; however, the subset is reproducibly retrievable by re-running the documented Boolean queries (Supplementary Methods S1.1) against a WoS Core Collection subscription within the corpus date window (1 January 2005 through 14 May 2026).

---

## Funding

[To be filled at submission. Per BiB author guidelines: "This work was supported by..." with full official funding agency names and grant numbers in brackets.]

---

## Author Contributions

[To be filled at submission per ICMJE roles. Single-author submission: conceptualization, methodology, data collection, software, formal analysis, investigation, writing — original draft, writing — review & editing, visualization, project administration.]

---

## Conflict of Interest

The author declares no competing financial or non-financial interests in connection with this work.

---

## Acknowledgements

[Optional. To be filled at submission if technical assistance, computational resources, or annotator contributions warrant acknowledgement. Note: the independent annotator for Supplementary Methods S2 should be acknowledged here.]