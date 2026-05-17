# Data Availability Statement -- Draft

> Day 16 Block 2c.C: Moved from Methods §2.0 lead-in (where it was structurally inappropriate per Frontiers / Elsevier conventions).
>
> Submission-routing notes:
> - **Frontiers in Pharmacology**: Do NOT include this section in the source file. Frontiers auto-generates the Data Availability Statement at submission from a questionnaire (per Frontiers Help Center: "you do not need to include a data statement in your source file"). The text below is reference material for filling in the questionnaire.
> - **Pharmacological Research (Elsevier)**: Include as a separate "Data availability" statement under Declarations, placed before the References section, per Elsevier's research data policy (effective 2020+).

---

## Statement text (draft, ~120 words)

All search queries, integration and analysis scripts, processed datasets 
(Parquet format), LLM extraction outputs (with cached raw responses for full 
reproducibility of the schema-extraction step), figures, and statistical tables 
are publicly deposited at the project repository 
(https://github.com/wcs52113140123-pixel/TCM-HDI-Bibliometric-2026). The conda 
environment specification (00_setup/requirements.txt), the LLM extraction schema 
definition (05_llm_extraction/01_schema.py, Schema v3, 16-category controlled 
vocabulary), and the bibliometrix R session snapshot are versioned to the git 
tag corresponding to the final corpus snapshot reported here. Raw bibliographic 
exports from the four source databases are not redistributed due to licensing 
restrictions; corresponding query specifications and search-execution dates 
are documented in 01_data_acquisition/ for independent re-acquisition.