# Limitations (Section 5) — Draft v2 (compress-bib-5k)

> Day 32 compression for BiB Problem solving protocols (≤5,000 words main body): 642 → ~315w.
> 5 paragraphs preserved.
> Para 2 n=200 hallucination removed (same fix as §2.4 paragraph 4 on Day 31); kappa numbers retained (n=50 from Supp Methods S2, Day 28).
> Day 20 baseline (5-paragraph, no kappa) preserved on main at 90697ce.

---

## §5 Limitations

Bibliometric and citation-burst analyses (§2.5) operated on the WoS-only subset (n = 3,091 of 9,413; 32.7%) because both bibliometrix and CiteSpace require WoS-format input fields that could not be reconstructed with comparable standardisation confidence after cross-database harmonisation. Conclusions about author productivity, journal scattering, thematic-map placement, and burst dynamics therefore reflect this subset. The near-identical mean citations per document between subset and integrated corpus (26.41 vs 25.72; 2.7% difference) supports broad representativeness, though selection effects on specific journal types remain possible.

Mechanism extraction (§2.4) relied on a single model (gpt-4o-mini), a fixed 16-category Schema v3, and confidence threshold 0.7 for downstream enrichment. Approximately 23% of returned interactions fell into the catch-all "unspecified" or "other" categories and were excluded from Fisher tests; this fraction is informative about mechanism reporting maturity but also represents a hard analytical boundary. Re-extraction with larger or more recent models, or an expanded schema, may surface mechanism categories Schema v3 did not anticipate. Extraction limitations are bounded by the independent-annotator validation in Supplementary Methods S2: Cohen's κ = 0.612 overall (47 records after excluding 3 annotator-flagged ambiguous cases) and κ = 0.867 in the high-confidence stratum, supporting reliability of LLM-extracted mechanism labels under the confidence stratification used in primary analyses.

The per-tier discovery-rate asymmetry (family 25.0%, species 15.6%, compound 4.3%; §3.6) was interpreted (§4.3) as reflecting the natural biological resolution of different mechanism classes. An alternative explanation—that the field has not yet generated sufficient single-compound mechanistic data to cross the FDR threshold—cannot be ruled out from the present data. Distinguishing the two would require either a larger compound-level corpus or external validation against curated pharmacological reference databases (DrugBank, PharmGKB).

The four databases primarily index English-language journals; while OpenAlex provides some reach into Chinese-language sources, the substantial body of TCM-HDI literature in Chinese-only journals indexed via CNKI or Wanfang was not searched directly. Findings therefore characterise the English-language and internationally indexed TCM-HDI literature, partially mitigated by Chinese pharmacological institutes publishing in English-indexed journals. A systematic comparison with Chinese-only literature would strengthen generalisation of the PK–PD bifurcation finding.

Records published in 2026 (n = 304) were retained as a partial-year extension, giving P3 (2020–2026) uneven closing-year representation. The Scheme B era boundaries (2005–2013 / 2014–2019 / 2020–2026) were chosen to align with the CiteSpace burst-era structure and balance subsample sizes, not to optimise any trajectory outcome; the dominant patterns (STABLE 18-cell backbone, EMERGING concentration in P3) should remain qualitatively robust to alternative parameterisations.