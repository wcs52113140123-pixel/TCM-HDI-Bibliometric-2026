# Supplementary Methods S2: Independent Validation of LLM Mechanism Extraction

## S2.1 Sampling

To validate the GPT-4o-mini mechanism extraction (Section 2.4), we randomly sampled 50 records from the 2,390 records that passed the primary filter (extraction confidence >= 0.7, excluding the catch-all categories 'unspecified' and 'other'). Sampling was stratified by the LLM-assigned mechanism category, targeting three records per category, with random selection to fill the remaining slots to a total of 50. The sampling seed (20260525) and category distribution are documented in `s2_sampling_log.json`. All 16 substantive Schema v3 mechanism categories were represented in the sample.

## S2.2 Annotation Protocol

An independent annotator with a biomedical background, blinded to the LLM-generated labels, classified each record into one of the 16 Schema v3 mechanism categories using only the paper title and abstract. The annotator could additionally mark records as 'unsure_ambiguous' when the abstract was too brief, multiple categories were equally applicable without a clear primary, or external information would have been required for confident classification. Annotators also recorded confidence (low/medium/high) and could optionally specify a secondary applicable category. External sources (full text, web search) were not permitted to ensure parity with the LLM input. Detailed instructions are provided as supplementary file `s2_annotation_instructions.md`.

## S2.3 Inter-method Agreement

Of the 50 records, the annotator marked 3 (6%) as 'unsure_ambiguous'; these were excluded from primary agreement calculations as they represent cases where confident classification from the abstract alone was not feasible. For the remaining 47 records, the raw agreement between the annotator and the LLM was 63.8%, and Cohen's kappa was 0.612, indicating substantial agreement (Landis & Koch 1977 benchmark).

| Annotator confidence | N | Raw agreement | Cohen's kappa | Interpretation |
|---|---|---|---|---|
| high   | 25 | 88.0% | 0.867 | almost perfect |
| medium | 19  | 42.1%  | 0.367  | fair |
| low    | 3  | 0.0%  | 0.000  | slight |

When alternative labels (where the annotator marked a secondary applicable category) were counted as agreement if either the primary or secondary annotator label matched the LLM label, the relaxed agreement rate was 78.7%.

## S2.4 Disagreement Analysis

Of the 47 records included in the primary analysis, 17 (36%) showed primary-label disagreement between the annotator and the LLM. Inspection of each case revealed three distinct origins of disagreement that map onto separate design features of the validation.

The single recurring disagreement pattern (3/17 cases) was LLM-assigned `antagonistic_efficacy` reclassified by the annotator as `synergistic_efficacy`. All three underlying abstracts describe multi-component or multi-drug combinations in which both synergistic and antagonistic interactions are reported within the same paper but for different pairings—for example, synergism with one antibiotic and antagonism with another in the same checkerboard assay (S2-038), or isobolographic analyses across multiple natural-compound × statin combinations (S2-044). Single-label extraction necessarily collapses such papers to one of the two effect classes; the annotator marked `antagonistic_efficacy` as the secondary applicable category in all three cases, so under the relaxed metric these three cases resolve to agreement. The pattern thus reflects a single-label-extraction constraint applied to genuinely multi-mechanism papers, rather than a directional bias in the LLM.

The remaining 14 disagreements distributed across two classes. The first comprises nested Schema v3 categories in which the LLM selected a finer-grained mechanism (e.g., `P-gp_inhibition`) while the annotator selected an adjacent coarser-grained mechanism (e.g., `absorption_alteration` or `transporter_modulation`) or vice versa; in 4 of the 14 the annotator marked the LLM label as the alternative, again resolving under the relaxed metric. The second class comprises three direction-flip cases. In two of these (S2-030 on CYP, S2-031 on P-gp), the abstract did not unambiguously state the direction of modulation, and the annotator assigned medium or low confidence accordingly. In the third (S2-037), the abstract explicitly stated "icariin was shown to inhibit UDP-glucuronosyltransferases"; the LLM correctly extracted `UGT_inhibition`, and the annotator coded `UGT_induction` with low confidence—precisely the failure mode that the confidence-stratification analysis in Section S2.3 identifies (low-tier kappa = 0.000 versus high-tier kappa = 0.867).
## S2.5 Interpretation

The substantial overall kappa value (0.612), combined with substantially higher agreement in the high-confidence tier (0.867) than in the low-confidence tier (0.000), validates two design choices in our primary analysis (Sections 2.4 and 3.4): (a) the use of GPT-4o-mini for mechanism extraction at corpus scale, and (b) the use of the LLM's self-reported confidence (threshold >= 0.7) as a stratification variable. The relaxed agreement of 78.7% when allowing alternative annotator labels further supports the position that most LLM-annotator disagreements reflect genuine multi-category abstracts rather than systematic LLM errors. Records marked 'unsure_ambiguous' by the human annotator (3/50 = 6%) are consistent with the 22.9% corpus-wide catch-all rate reported in Section 5.2, suggesting that the LLM and the human annotator face the same fundamental limit of abstract-level information density rather than the LLM systematically over-confidently classifying ambiguous records.
