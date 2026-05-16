"""
Day 7 LLM extraction prompts (5-part template).

Structure (顶刊 standard, Zero-Shot Doc-Level RE 2025 + Feng et al. 2025):
  Part 1: System role / task definition
  Part 2: Entity definitions (herb, drug, interaction types)
  Part 3: Mechanism / direction / evidence enumerations with brief defs
  Part 4: Few-shot examples (2 positive, 1 negative)
  Part 5: Output format constraint (JSON schema, no prose)
"""

SYSTEM_PROMPT = """You are an expert in pharmacology and traditional Chinese medicine (TCM) literature analysis.

Your task: extract herb-drug interactions (HDIs) from biomedical abstracts following a strict structured schema.

Output ONLY valid JSON matching the AbstractExtraction schema. No prose, no markdown code fences, no commentary, no explanations outside the JSON object."""


USER_PROMPT_TEMPLATE = """# Task

Extract ALL herb-drug interactions explicitly described or strongly implied in the abstract. If no interaction is described (e.g., pure methodology paper, unrelated topic, narrative review without specific HDI), set `contains_hdi=false` and return an empty `interactions` list.

# Definitions

**Herb** = any plant-derived medicinal substance: TCM herb, herbal supplement, dietary supplement, single isolated plant compound (e.g. curcumin, resveratrol), or multi-herb formula.

**Drug** = conventional pharmaceutical drug (small molecule or biologic), referenced by generic name or class.

**Pharmacokinetic interaction** = alters absorption, distribution, metabolism, or excretion (ADME) of the partner.
**Pharmacodynamic interaction** = alters receptor/pathway response — efficacy or toxicity at the target.

**Mechanism categories** (pick the most specific):
- CYP_inhibition / CYP_induction: cytochrome P450 isoform inhibition or induction
- P-gp_inhibition / P-gp_induction: P-glycoprotein efflux pump
- UGT_inhibition / UGT_induction: UDP-glucuronosyltransferases (phase II metabolism)
- transporter_modulation: modulates membrane transporters OTHER THAN P-gp. Includes:
  efflux pumps (MRP1, MRP2, MRP3, MRP4, BCRP, BSEP, MATE1, MATE2K),
  uptake transporters (OATP1B1, OATP1B3, OATP2B1, OCT1, OCT2, OAT1, OAT3, NTCP),
  and other ABC/SLC transporters. Use this when target is named (e.g. "MRP2").
- absorption_alteration: GI absorption changes (binding, motility, pH, bile acid changes)
- protein_binding_displacement: plasma protein binding displacement
- receptor_synergism / receptor_antagonism: same-pathway PD interaction at a specific receptor
- additive_toxicity: combined toxicity > either alone (BOTH substances contribute to toxicity)
- synergistic_efficacy / antagonistic_efficacy: enhanced or reduced therapeutic effect
- signaling_pathway_modulation: NEW. Modulation of intracellular signaling pathways via
  transcription factors (PXR, CAR, AhR, NRF2, FXR, LXR, HIF-1α, p53) or kinases
  (MAPK including p38/ERK/JNK, PI3K/Akt, JAK/STAT, NF-κB, mTOR, AMPK, Wnt/β-catenin).
  Use when the mechanism is described at the pathway / transcription-factor level
  rather than at direct enzyme inhibition/induction. Often appears with phrases like
  "via Nrf2 pathway", "through NF-κB suppression", "PXR activation".
- organ_toxicity_modulation: NEW. Herb/compound alters drug-induced organ toxicity
  (hepatic, cardiac, renal, neural, hematologic, pulmonary, gonadal). Use when:
  (a) one party is a known toxic drug (e.g. doxorubicin/cardiotoxic, cisplatin/nephrotoxic,
  acetaminophen/hepatotoxic, methotrexate/hepatotoxic, CCl4/hepatotoxic) AND
  (b) the herb/compound attenuates (direction=effect_decrease, "cardioprotective",
  "hepatoprotective") or potentiates (direction=effect_increase) the toxicity.
  Distinct from additive_toxicity which implies BOTH substances are toxic.
- other: described but doesn't fit above
- unspecified: interaction reported but mechanism not detailed

**Direction**:
- exposure_increase / exposure_decrease: drug plasma exposure goes up / down
- effect_increase / effect_decrease: therapeutic or toxic effect intensifies / diminishes
- no_change: no significant interaction observed
- context_dependent: direction depends on dose, timing, or subgroup

**Evidence type**:
- in_vitro: cell lines, microsomes, recombinant enzymes
- in_vivo_animal: rats, mice, beagles, primates
- human_PK_study: healthy volunteer PK study
- clinical_trial: patient population trial
- case_report: single or few-patient anecdote
- review: secondary literature, no primary data
- in_silico: docking, network pharmacology, simulation only

# Few-shot Examples

## Example 1 — Classic PK interaction with quantitative data

ABSTRACT: "Administration of St. John's Wort (Hypericum perforatum) extract 300 mg three times daily for 14 days significantly decreased the AUC of cyclosporine by 52% (p<0.001) in 12 healthy volunteers. This interaction is attributed to potent CYP3A4 induction by hyperforin, the active constituent."

OUTPUT:
{
  "record_id": "ex_1",
  "contains_hdi": true,
  "interactions": [{
    "herb_name_latin": "Hypericum perforatum",
    "herb_common_name": "St. John's Wort",
    "herb_active_compound": "hyperforin",
    "drug_name": "cyclosporine",
    "drug_class": "immunosuppressant",
    "interaction_type": "pharmacokinetic",
    "mechanism": "CYP_induction",
    "specific_target": "CYP3A4",
    "direction": "exposure_decrease",
    "tcm_formula_name": null,
    "co_herbs": [],
    "tcm_pattern": null,
    "auc_change_pct": -52.0,
    "cmax_change_pct": null,
    "half_life_change_pct": null,
    "cl_change_pct": null,
    "sample_size": 12,
    "evidence_type": "human_PK_study",
    "clinical_significance": "high",
    "confidence": 0.95,
    "evidence_quote": "Administration of St. John's Wort (Hypericum perforatum) extract 300 mg three times daily for 14 days significantly decreased the AUC of cyclosporine by 52% (p<0.001) in 12 healthy volunteers."
  }],
  "extraction_notes": null
}

## Example 2 — TCM compound formula (multi-herb context)

ABSTRACT: "Wuzhi capsule, a TCM preparation containing Schisandra sphenanthera extract, increased the AUC of tacrolimus by 164% in 20 renal transplant recipients. The interaction is mediated by schisantherin A-induced CYP3A4 inhibition in the small intestine. Clinical implication: tacrolimus dose reduction is recommended when co-administered with Wuzhi."

OUTPUT:
{
  "record_id": "ex_2",
  "contains_hdi": true,
  "interactions": [{
    "herb_name_latin": "Schisandra sphenanthera",
    "herb_common_name": "Schisandra",
    "herb_active_compound": "schisantherin A",
    "drug_name": "tacrolimus",
    "drug_class": "immunosuppressant",
    "interaction_type": "pharmacokinetic",
    "mechanism": "CYP_inhibition",
    "specific_target": "CYP3A4",
    "direction": "exposure_increase",
    "tcm_formula_name": "Wuzhi capsule",
    "co_herbs": [],
    "tcm_pattern": null,
    "auc_change_pct": 164.0,
    "cmax_change_pct": null,
    "half_life_change_pct": null,
    "cl_change_pct": null,
    "sample_size": 20,
    "evidence_type": "clinical_trial",
    "clinical_significance": "high",
    "confidence": 0.92,
    "evidence_quote": "Wuzhi capsule, a TCM preparation containing Schisandra sphenanthera extract, increased the AUC of tacrolimus by 164% in 20 renal transplant recipients. The interaction is mediated by schisantherin A-induced CYP3A4 inhibition in the small intestine."
  }],
  "extraction_notes": null
}

## Example 3 — Negative case (methodology review, no specific HDI)

ABSTRACT: "We systematically reviewed the bibliometric literature on herb-drug interactions published from 2010 to 2020. A total of 1,234 studies were identified through PubMed and Web of Science searches. Quality varied substantially across studies. We propose a standardized reporting framework for future HDI research."

OUTPUT:
{
  "record_id": "ex_3",
  "contains_hdi": false,
  "interactions": [],
  "extraction_notes": "Methodological/bibliometric review without specific HDI cases described."
}

## Example 4 — Organ toxicity modulation (cardioprotection via pathway)

ABSTRACT: "Pre-treatment with Salvia miltiorrhiza (Danshen) extract significantly attenuated doxorubicin-induced cardiotoxicity in male Sprague-Dawley rats (n=24). Serum CK-MB levels decreased by 47% (p<0.001), and cardiac contractile function was preserved on echocardiography. The cardioprotective effect was mediated via activation of the Nrf2/HO-1 antioxidant pathway and suppression of NF-κB-driven inflammatory cytokines (TNF-α, IL-6)."

OUTPUT:
{
  "record_id": "ex_4",
  "contains_hdi": true,
  "interactions": [{
    "herb_name_latin": "Salvia miltiorrhiza",
    "herb_common_name": "Danshen",
    "herb_active_compound": null,
    "drug_name": "doxorubicin",
    "drug_class": "anthracycline",
    "interaction_type": "pharmacodynamic",
    "mechanism": "organ_toxicity_modulation",
    "specific_target": "cardiac tissue; Nrf2/HO-1, NF-κB",
    "direction": "effect_decrease",
    "tcm_formula_name": null,
    "co_herbs": [],
    "tcm_pattern": null,
    "auc_change_pct": null,
    "cmax_change_pct": null,
    "half_life_change_pct": null,
    "cl_change_pct": null,
    "sample_size": 24,
    "evidence_type": "in_vivo_animal",
    "clinical_significance": "moderate",
    "confidence": 0.88,
    "evidence_quote": "Pre-treatment with Salvia miltiorrhiza (Danshen) extract significantly attenuated doxorubicin-induced cardiotoxicity in male Sprague-Dawley rats (n=24). The cardioprotective effect was mediated via activation of the Nrf2/HO-1 antioxidant pathway and suppression of NF-κB-driven inflammatory cytokines."
  }],
  "extraction_notes": null
}

# Now extract from the following abstract.

RECORD_ID: {record_id}
TITLE: {title}
ABSTRACT: {abstract}

# Output

Return ONLY a valid JSON object matching the AbstractExtraction schema. No code fences, no markdown, no commentary."""


def build_user_prompt(record_id: str, title: str, abstract: str) -> str:
    """Render the user prompt with abstract injected.

    Uses manual .replace() instead of str.format() because the template
    contains literal JSON braces in few-shot examples that would conflict
    with format-string parsing.
    """
    return (
        USER_PROMPT_TEMPLATE
        .replace("{record_id}", str(record_id))
        .replace("{title}", (title or "").strip())
        .replace("{abstract}", (abstract or "").strip())
    )
