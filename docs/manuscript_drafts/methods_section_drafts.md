# Manuscript Methods — Draft Sections

> Living draft of paper Methods §2.x sections.
> Sections added incrementally as analysis Days complete.

---

## §2.5 Canonical Normalization (Schema v3)

To enable network-level analysis, four entity classes (herbs, drugs,
targets, mechanisms) extracted by large language model (LLM, §2.3)
were normalized under a unified Schema v3 ontology before aggregation.
We applied a three-tier strategy for each entity class: (i) explicit
canonical mapping against a curated reference table, (ii) pass-through
retention of LLM-extracted Latin binomials and standard names not yet
in the reference, and (iii) null assignment for unrecognizable
strings. This yielded canonical IDs for 99.6% of herb entities, 100%
of drug entities (with 72% additionally assigned a class taxonomy),
and 83% of target entities.

### Herb canonical taxonomy

The `herb_canonical` field admits three entity types:

1. **Linnaean botanical families** for single-herb records (e.g.,
   *Hypericum perforatum* → Hypericaceae; *Salvia miltiorrhiza* →
   Lamiaceae; *Panax ginseng* → Araliaceae). 18 plant families
   collectively account for approximately 80% of mapped records
   (top five: Fabaceae 182, Lamiaceae 167, Hypericaceae 133,
   Ranunculaceae 108, Araliaceae 102).

2. **`flavonoid_compound`** — a fallback canonical bucket for records
   whose herb entity is a pure phytochemical that maps ambiguously
   to multiple botanical families (e.g., quercetin, baicalein,
   resveratrol, curcumin extracted as standalone study compound
   without explicit attribution to *Curcuma longa*).

3. **`TCM_formula`** — a fallback canonical bucket for multi-herb
   prescription records (e.g., Xiao Chai Hu Tang, Liu Wei Di Huang
   Wan, Shenmai injection, Ojeok-san, Bangpungtongseong-san).

Records assigned to buckets (2) and (3) are retained for analysis but
are explicitly distinguished from family-level data in figure
annotations and discussed at a separate ontological level in
Results §3.5.

### Target canonical taxonomy

The `target_family` field is organized by molecular family using
HGNC standard nomenclature: `cytochrome_P450` (CYP1A2, CYP3A4, etc.),
`ABC_transporter` (ABCB1, ABCG2, etc.), `SLC_transporter` (SLCO1B1,
etc.), `UGT_phase_II` (UGT1A1, UGT2B7, etc.), `nuclear_receptor_TF`
(PXR/NR1I2, CAR/NR1I3), `kinase_pathway`, `inflammation_cytokine`,
`neurotransmitter_pathway`, and `organ_tissue`.

The `target_family` axis does **not** include therapeutic-area
categories such as oncology, cardiovascular disease, or
neuropsychiatry. Therapeutic-area information is carried orthogonally
by the `drug_class` axis using an ATC-aligned nomenclature with
mechanism-of-action subcategories for antineoplastics
(`antineoplastic_kinase_inhibitor`, `antineoplastic_taxane`,
`antineoplastic_anthracycline`, `antineoplastic_platinum`,
`antineoplastic_antimetabolite`, `antineoplastic_topoisomerase`).
This orthogonal design lets the same record contribute simultaneously
to molecular-mechanism analysis (Figure 5a) and therapeutic-area
analysis (Figure 6) without double-counting.

Rat CYP orthologs (CYP2C11, CYP2D1/2) frequently encountered in
*in vivo* animal studies were mapped to the closest human orthologs
(CYP2C9, CYP2D6, respectively) for cross-study harmonization. This
is reported as an interpretive choice in line with established
TCM-PK convention; affected records constitute approximately 3% of
the gold-standard triple set.

### Mechanism canonical taxonomy

The `mechanism` field uses Schema v3, an eight-category ontology
(`CYP_inhibition`, `CYP_induction`, `P-gp_inhibition`,
`UGT_inhibition`, `transporter_modulation`, `receptor_synergism`,
`organ_toxicity_modulation`, `signaling_pathway_modulation`), plus
an `other` bucket for confidence-validated but unclassified entries.
The `organ_toxicity_modulation` and `signaling_pathway_modulation`
categories were added in Schema v3 (vs. earlier purely PK-centric
schemas) to capture pharmacodynamic (PD) interactions emerging in
post-2015 TCM-HDI literature; their temporal entry into the corpus
is visualized in Figure 8.

### Confidence scoring

Per-record confidence (mean 0.87, median 0.85, range 0.70–0.95) was
preserved from the LLM extraction stage. The 900-triple gold-standard
subset (T3 knowledge-graph layer; §2.6) retained only triples with
confidence ≥ 0.7 and all four canonical fields
(`herb_canonical_latin`, `drug_canonical`, `target_canonical`,
`mechanism`) populated and non-null.

---

<!-- Future sections to draft: §2.1 Search strategy, §2.2 Deduplication,
     §2.3 LLM extraction, §2.4 Validation, §2.6 Network construction -->