# Results (Section 3) — Draft v2 (compress-bib-5k)

> Day 31 compression for BiB Problem solving protocols (≤5,000 words main body).
> §3.0 tightened; §3.1-§3.3 and §3.5 heavily condensed with descriptive tables → Supplementary Results R1.
> §3.4 (PK-PD bifurcation finding #1) and §3.6 (SJW four-method anchor finding #2 + mechanism resolution layering finding #3) retained with full numerical detail.
> Figure/Table numbering retained from Day 17 draft (Figure 1 PRISMA, Figure 8 topic-mechanism heatmap, Figure 10 three-tier herbal diverging, Figure 11 SJW FULL_CHAIN Sankey; Table 1 cross-method convergence).
> Day 17-19 v1 preserved on main at 90697ce.

---

## §3.0 Lead-in

This section presents bibliometric and analytical findings derived from the 9,413-record main corpus and 304-record partial 2026 extension (Figure 1). Sections 3.1–3.2 characterise the corpus via productivity distributions, thematic-map partitioning, and citation-burst detection identifying four historical research eras—all computed on the WoS-format subset (n = 3,091; rationale in §2.5). A convergence audit (§3.3) summarises findings supported by ≥ 3 of the four analytical methods. Sections 3.4–3.6 present the paper's principal analytical contributions: topic × mechanism Fisher enrichment (§3.4), its temporal stratification (§3.5), and three-tier herbal-taxonomy stratification (§3.6). *Hypericum perforatum* (St. John's wort) recurs across all subsections as a triangulation case study.

---

## §3.1 Corpus description

The final analysis corpus comprised 9,413 unique TCM herbal–drug interaction publications spanning 2005–2025, plus a 304-record partial 2026 extension (Figure 1; §2.2), drawn from WoS Core Collection (n = 3,091; 32.7%), Scopus (n = 7,181), OpenAlex (n = 2,513), and PubMed (n = 3,867). Mean citation density was nearly identical between the WoS-3091 subset (26.41/document) and the integrated corpus (25.72/document), indicating no systematic bias from cross-database integration.

Annual publication output grew from 261 records in 2005 to 737 in 2025 (Figure 2), exponential pre-2015 followed by post-2015 saturation toward 550–650 records/year. Author productivity followed a super-Lotka distribution (α = 2.38, R² = 0.960 under bibliometrix D1; α = 2.63, R² = 0.957 under D1 + affiliation; Figure 3a); journal scattering followed Bradford's geometric progression (multiplier 7.11–8.89, exceeding the classical ~5; Figure 3b).

A Callon-style thematic map (Figure 4) partitioned 233 KeyWords Plus terms into four clusters. The Q2 'Niche' quadrant (high density, low centrality) anchored the canonical safety-case literature—P-glycoprotein, *Hypericum perforatum* (St. John's wort), grapefruit juice—as a structurally isolated citation community. The Q4 'Basic' quadrant (high centrality, low density) held the foundational mechanistic vocabulary (in-vitro metabolism, gene expression). The Q1 'Motor' quadrant was empty, indicating an incipient but incomplete paradigm shift. Full descriptive tables (cross-database overlap, Bradford core composition, three-fields plot) are in Supplementary Results R1.1.

---

## §3.2 Temporal-thematic structure

CiteSpace 6.4.R1 applied to the WoS-3091 subset (§2.5) produced a keyword co-occurrence network of 667 nodes and 3,336 edges (modularity Q = 0.3802; weighted silhouette S = 0.6935; Figure 7). The burst-detection algorithm identified 220 keywords with significant emergence or decline phases. The two strongest bursts are temporally inverted but quantitatively near-identical: *Hypericum perforatum* (St. John's wort) burst 2005–2012 with strength 27.01—the foundational case-study era—while network pharmacology burst 2023–present with strength 27.59. The eleven-year gap, paired with their near-equal strength, marks a 22-year paradigm shift from case-driven safety research to systems-level methodology.

The 220 bursts cluster temporally into four eras (Figures 5, 6). **Era 1 (2005–2012)**: safety-case studies under CAM framing (St. John's wort 27.01, ginkgo biloba 9.72, milk thistle, grapefruit juice). **Era 2 (2010–2018)**: mechanistic depth (gene-expression 7.52, glucuronidation 7.07, tandem mass spectrometry 10.18). **Era 3 (2017–2022)**: in-vivo pharmacokinetics with drug-transporter and animal-model foci. **Era 4 (2020–2026, ongoing)**: integrative systems-biology (oxidative stress 10.75, molecular docking 16.1, network pharmacology 27.59, gut microbiota 8.74), all in active burst at corpus closure.

Three of the most-cited TCM-HDI keywords—cytochrome P450 (302 total occurrences), P-glycoprotein (270), and pregnane X receptor (81)—did not appear in the top-25 burst list. This non-bursting infrastructure pattern, paired with the strong Era 4 methodological bursts, demarcates a stable mechanistic foundation distinct from an actively expanding methodological frontier. Full modularity-cluster trajectories (11 clusters, mean-year migration 2010 → 2017) are in Supplementary Results R1.2.

---

## §3.3 Multi-method convergence audit

Findings emerging independently across multiple analytical methods are treated as robust to any single approach's limitations. Table 1 summarises cross-method support for principal findings.

**Table 1.** Cross-method convergence of principal findings. "Methods" = number of approaches independently supporting each finding.

| Finding | bibliometrix (§3.1) | CiteSpace (§3.2) | Topic × Mech Fisher (§3.4–§3.5) | Three-tier herb (§3.6) | Methods |
|---|---|---|---|---|---|
| *H. perforatum* (SJW) as CYP induction case | Q2 Niche frontier anchor | Era 1 burst, 27.01 (2005–2012) | Topic #5 × CYP_ind, OR = 26.7, q = 9.5 × 10⁻¹⁵ | FULL_CHAIN exemplar, monotone OR family→species→compound | 4 |
| Systems-biology methodology (network pharmacology, oxidative stress, gut microbiota) | Q4 Basic frontier, central but underconsolidated | Era 4 ongoing burst, 27.59 | 3 EMERGING enrichments, all P3 | — | 3 |
| Foundation infrastructure (CYP450, P-gp, PXR) | High frequency, no thematic concentration | Top-30 frequency, no burst | Strong enrichment across multiple topics | Mechanism-specific resolution layers | 3 |
| Warfarin × additive_toxicity declining | — | — | Topic #6, DECLINING 4→1→0 | — | 1 |
| Hepatotoxicity bridge cluster | — | — | Topic #17 mixed-mechanism | — | 1 |

The strongest convergence concerns *Hypericum perforatum* (St. John's wort), recovered independently by all four methods. Two secondary findings appear across three methods each: the systems-biology methodological frontier and the structural distinction between non-bursting infrastructure terms and topic-level enrichment patterns. Convergent findings (Methods ≥ 3) are emphasised in subsequent sections as robust to method-specific limitations; method-specific signals (Methods = 1) are explicitly flagged. Notes on method-specific findings (Bradford core anomalies, cluster mean-year migration, warfarin DECLINING, hepatotoxicity bridge) are in Supplementary Results R1.3.

---

## §3.4 Topic × mechanism static enrichment

The principal analytical contribution is a statistical cross-analysis between literature topics (HDBSCAN clusters of SPECTER2 embeddings) and pharmacological mechanisms (LLM-extracted under 16-category Schema v3 at confidence ≥ 0.7; §2.3, §2.4, §2.6). The 37 × 16 contingency matrix tested 592 cells with Fisher exact + BH-FDR correction; 63 cells (10.6%) reached q < 0.05, with 30 strong enrichments (OR > 2, observed ≥ 5) and 29 strong depletions (OR < 0.5, expected ≥ 5; Figure 8; Table 2; Supplementary Tables S7–S8).

The combination of strong enrichments and depletions revealed a previously undescribed structural property: the TCM herbal–drug interaction literature is statistically bifurcated into two non-overlapping research spaces. Four mechanism-named topics—#30 (cyp inhibition), #24 (inhibition ugt), #32 (drug transporters), #9 (pxr cyp)—each strongly enriched their corresponding mechanism (OR = 17.6 to 505.1) while statistically rejecting major pharmacodynamic mechanisms. Three clinical-application-named topics—#11 (anticancer; n = 730, the largest topic), #23 (antimicrobial), #28 (medicinal plants / anxiolytic)—each strongly enriched a pharmacodynamic mechanism (receptor_synergism OR = 16.2 to 22.6) while rejecting major pharmacokinetic mechanisms. The most extreme single depletion was topic #11 × CYP_inhibition: 5 observed against 99.7 expected (q = 1.9 × 10⁻⁴⁷). We refer to this finding as the **PK–PD bifurcation** and return to its implications in §4.1.

Internal validation by topic–mechanism semantic self-alignment confirmed pipeline consistency, with four extreme self-aligning enrichments: topic #24 × UGT_inhibition (OR = 505.1, q = 2.83 × 10⁻⁸²), #30 × CYP_inhibition (q = 9.4 × 10⁻¹²⁰), #32 × transporter_modulation (OR = 188.2), and #9 × CYP_induction (OR = 27.6)—confirming that SPECTER2 topic clustering and LLM mechanism extraction independently agree despite operating on different signal sources.

Three enrichments recovered established textbook biology: topic #5 (antidepressants / wort sjw) × CYP_induction (OR = 26.7; q = 9.5 × 10⁻¹⁵), the canonical SJW–CYP3A4 relationship; topic #9 (pxr cyp) × CYP_induction (OR = 27.6; q = 1.2 × 10⁻²²), the PXR–CYP3A4 axis; and topic #8 (statins) × transporter_modulation (OR = 11.0), OATP-mediated statin uptake. Topic #17 (hepatoprotective / hepatotoxicity) bridges the bifurcation: strongly enriched for organ_toxicity_modulation (OR = 41.3; q = 9.5 × 10⁻⁴⁶) while simultaneously enriching CYP_inhibition, CYP_induction, and signaling_pathway_modulation—mechanistically interpretable because drug-induced liver injury intrinsically requires both PK substrate and PD consequence.

---

## §3.5 Temporal stratification

To assess temporal stability, we stratified the 1,738 (record, mechanism) pairs into three disjoint publication eras—P1 (2005–2013, n = 517), P2 (2014–2019, n = 687), P3 (2020–2026, n = 534)—aligned with the CiteSpace burst-era structure (§3.2). Of 40 trajectory-classifiable cells, 18 (45%) were STABLE: significant in all three eras (Figure 9; Supplementary Table S10). The strongest stable backbone cells anchored the PK–PD bifurcation: topic #30 × CYP_inhibition (P1/P2/P3 = 96/166/76 records), #24 × UGT_inhibition, #32 × transporter_modulation, #9 × CYP_induction, and their pharmacodynamic counterparts (topics #11, #23, #28 × receptor_synergism). Critically, the strong depletions of §3.4 were not transient: topic #30 contained zero records of synergistic_efficacy, receptor_synergism, or absorption_alteration in every era. The PK–PD bifurcation is therefore a 22-year structural feature rather than recent fashion.

Three EMERGING cells were concentrated in P3 (2020–2026): topic #27 × absorption_alteration (P1/P2/P3 = 0/0/10), #10 × signaling_pathway_modulation (0/0/7), and most informatively #20 (cancer / network pharmacology) × signaling_pathway_modulation (0/1/5)—the first cell in which a clinical-application-named topic co-enriches a signalling-mechanism category, marking the bifurcation's first visible erosion (consistent with §3.2 Era 4 systems-biology burst). Four DECLINING cells included topic #6 (warfarin / coumadin) × additive_toxicity (P1/P2/P3 = 4/1/0): the canonical warfarin–herb additive-bleeding paradigm has visibly faded. The early case-report paradigm has been replaced rather than disappeared—the P3 EMERGING cells point to its successor in network-pharmacology signalling research. Full 40-cell trajectory tables and keyword–mechanism lag analyses (topic #15 microbiome, #22 network pharmacology) are in Supplementary Results R1.4.

---

## §3.6 Three-tier herbal-taxonomy stratification

To examine whether the herbal entities underlying topic clusters resolve at botanical-family, species, or chemical-compound level, we performed a parallel enrichment analysis using the herb-taxonomy fields extracted by Schema v3 (§2.4). The 1,676 records with at least one taxonomic identifier were tested at three tiers—family (24 families with n ≥ 10), species (32 species with n ≥ 10), and compound (23 compounds with n ≥ 5)—yielding 1,241 Fisher exact tests with BH-FDR correction. Thirteen cells were enriched (Family 6, Species 5, Compound 1) and one family-tier cell was depleted; the 15 significantly enriched chains were dominated by FAMILY_PERVASIVE (8), SPECIES_SPECIFIC (3), and a single FULL_CHAIN (Figure 10; Supplementary Table S11).

The only FULL_CHAIN—significant enrichment at family, species, and compound tiers for the same mechanism—was *Hypericum perforatum* and CYP_induction (Figure 11). The chain showed monotonic odds-ratio escalation across resolution layers: Hypericaceae × CYP_induction (OR = 14.20; q = 2.9 × 10⁻¹⁷), *H. perforatum* × CYP_induction (OR = 14.71; q = 4.4 × 10⁻¹⁷), and hyperforin × CYP_induction (OR = 18.73; q = 3.9 × 10⁻⁵). The OR increase indicates that within Hypericaceae the CYP_induction signal is concentrated in *H. perforatum* rather than diluted across congeners, and within *H. perforatum* in hyperforin rather than diluted across other constituents. This is the same case anchored by the bibliometric (§3.1, Q2), CiteSpace (§3.2, Era 1), static topic (§3.4, topic #5), and temporal (§3.5, STABLE) analyses—now reproduced as a four-tier hierarchy in the herbal-taxonomy frame.

The eight FAMILY_PERVASIVE chains were dominated by Lamiaceae, enriched for both P-glycoprotein_inhibition and transporter_modulation; the species-tier signal within Lamiaceae did not concentrate in a single member but distributed across multiple species, indicating a family-wide compound-class-mediated mechanism rather than a species-specific effect. The per-tier discovery rate was strongly asymmetric: family 6/24 = 25.0%, species 5/32 = 15.6%, compound 1/23 = 4.3%. The compound-tier sparsity is itself a finding: papers reporting on a herbal species rarely report the implicated compound in a form recoverable by Schema v3.

Three SPECIES_SPECIFIC chains were observed; the clearest was *Glycyrrhiza uralensis* × UGT_inhibition—significant at the species tier but not at the Fabaceae family tier, where the licorice signal is diluted by *Astragalus*, *Pueraria*, and *Sophora* species reporting unrelated mechanisms. Across all 13 significant cells, the resolution scale varied systematically with mechanism class: CYP_induction concentrated at compound resolution (hyperforin); UGT_inhibition concentrated at species resolution (*G. uralensis*); P-glycoprotein and transporter modulation concentrated at family resolution (Lamiaceae). We interpret this as a substantive claim about the biological scale of action—enzyme-induction mechanisms depending on specific inducer compounds; transporter-modulation mechanisms acting through structural classes shared across a botanical family; UGT-inhibition occupying an intermediate species-scoped scale. The herbal-taxonomy stratification thus identifies the natural scale at which each HDI mechanism class is best resolved, a synthesis developed further in §4.3.