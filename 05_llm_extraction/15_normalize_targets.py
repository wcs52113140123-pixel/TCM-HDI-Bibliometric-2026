"""
Day 9 T1: Target normalization.

Maps free-text `specific_target` values to canonical HGNC gene symbols and
groups them into functional families for downstream network analysis.

Approach:
  1. Lowercase + strip + remove non-essential chars (hyphens, periods)
  2. Look up alias map (e.g., "p-gp" → "ABCB1", "cyp3a" → "CYP3A4")
  3. Split multi-target strings on comma/semicolon/"and"/"/"
  4. Categorize each canonical target into a functional family

Output columns added to interactions parquet:
  - target_list      : pipe-delimited canonical target list (multi-target)
  - target_canonical : primary canonical target (first in list)
  - target_family    : functional family of primary target
  - target_n         : count of canonical targets in this interaction

Coverage goal: ≥85% of named targets mapped (long-tail unmapped → 'unknown_target')

Usage:
    python 05_llm_extraction/15_normalize_targets.py
        [--model openai/gpt-4o-mini]
        [--prefix primary]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"


# =====================================================================
# ALIAS MAP — keys are LOWERCASE alias, values are canonical HGNC symbol
# (or non-HGNC standardized name for non-gene targets like 'liver', 'MAPK')
# =====================================================================
ALIAS_MAP: dict[str, str] = {
    # ----- Cytochrome P450 (human standard) -----
    "cyp1a1": "CYP1A1", "cyp1a2": "CYP1A2", "cyp1b1": "CYP1B1",
    "cyp2a6": "CYP2A6", "cyp2b6": "CYP2B6", "cyp2c8": "CYP2C8",
    "cyp2c9": "CYP2C9", "cyp2c19": "CYP2C19", "cyp2d6": "CYP2D6",
    "cyp2e1": "CYP2E1", "cyp3a4": "CYP3A4", "cyp3a5": "CYP3A5",
    "cyp3a7": "CYP3A7", "cyp19": "CYP19A1", "cyp19a1": "CYP19A1",
    # CYP3A subfamily (when not disambiguated, default to CYP3A4 = dominant isoform)
    "cyp3a": "CYP3A4",
    # Rodent CYPs (lowercase 'a' is HGNC convention for non-human orthologs)
    "cyp1a": "CYP1A2", "cyp2b": "CYP2B6", "cyp2c": "CYP2C9",
    "cyp3a1": "CYP3A4", "cyp3a2": "CYP3A4", "cyp1a2/3a1": "CYP1A2",
    "cyp2b1/2": "CYP2B6", "cyp2b1": "CYP2B6", "cyp2b2": "CYP2B6",
    # Generic "P450" placeholders
    "cyp": "CYP_family", "cyps": "CYP_family",
    "cyp enzymes": "CYP_family", "cytochrome p450": "CYP_family",
    "cytochromes p450": "CYP_family", "p450": "CYP_family",
    "p450 enzymes": "CYP_family", "cyp450": "CYP_family",

    # ----- ABC transporters -----
    "p-gp": "ABCB1", "pgp": "ABCB1", "p-glycoprotein": "ABCB1",
    "p glycoprotein": "ABCB1", "mdr1": "ABCB1", "mdr-1": "ABCB1",
    "abcb1": "ABCB1", "multidrug resistance protein 1": "ABCB1",
    "multidrug resistance protein": "ABCB1", "multidrug resistance protein-1": "ABCB1",
    "bcrp": "ABCG2", "abcg2": "ABCG2", "breast cancer resistance protein": "ABCG2",
    "bsep": "ABCB11", "abcb11": "ABCB11", "bile salt export pump": "ABCB11",
    "mrp1": "ABCC1", "abcc1": "ABCC1",
    "mrp2": "ABCC2", "abcc2": "ABCC2", "cmoat": "ABCC2",
    "mrp3": "ABCC3", "abcc3": "ABCC3",
    "mrp4": "ABCC4", "abcc4": "ABCC4",
    "mrp5": "ABCC5", "abcc5": "ABCC5",

    # ----- SLC transporters -----
    "oatp1b1": "SLCO1B1", "slco1b1": "SLCO1B1",
    "oatp1b3": "SLCO1B3", "slco1b3": "SLCO1B3",
    "oatp2b1": "SLCO2B1", "slco2b1": "SLCO2B1",
    "oct1": "SLC22A1", "slc22a1": "SLC22A1",
    "oct2": "SLC22A2", "slc22a2": "SLC22A2",
    "oat1": "SLC22A6", "slc22a6": "SLC22A6", "hoat1": "SLC22A6",
    "oat3": "SLC22A8", "slc22a8": "SLC22A8", "hoat3": "SLC22A8",
    "mate1": "SLC47A1", "slc47a1": "SLC47A1",
    "mate2k": "SLC47A2", "slc47a2": "SLC47A2",
    "ntcp": "SLC10A1", "slc10a1": "SLC10A1",
    "pept1": "SLC15A1", "slc15a1": "SLC15A1",

    # ----- UGTs -----
    "ugt1a1": "UGT1A1", "ugt1a3": "UGT1A3", "ugt1a4": "UGT1A4",
    "ugt1a6": "UGT1A6", "ugt1a9": "UGT1A9",
    "ugt2b7": "UGT2B7", "ugt2b15": "UGT2B15", "ugt2b17": "UGT2B17",
    "ugt": "UGT_family", "ugts": "UGT_family",
    "ugt enzymes": "UGT_family",
    "udp-glucuronosyltransferase": "UGT_family",
    "udp-glucuronosyltransferases": "UGT_family",

    # ----- SULTs -----
    "sult1a1": "SULT1A1", "sult1e1": "SULT1E1",
    "sult": "SULT_family", "sults": "SULT_family",

    # ----- GSTs -----
    "gst": "GST_family", "gsts": "GST_family",
    "gstp1": "GSTP1", "gsta1": "GSTA1",

    # ----- Nuclear receptors / transcription factors -----
    "pxr": "NR1I2", "hpxr": "NR1I2", "nr1i2": "NR1I2",
    "car": "NR1I3", "nr1i3": "NR1I3",
    "fxr": "NR1H4", "nr1h4": "NR1H4",
    "lxr": "NR1H3", "nr1h3": "NR1H3",
    "ahr": "AHR", "aryl hydrocarbon receptor": "AHR",
    "nrf2": "NFE2L2", "nfe2l2": "NFE2L2",
    "keap1": "KEAP1",
    "ppar": "PPARG", "pparα": "PPARA", "ppara": "PPARA",
    "pparγ": "PPARG", "pparg": "PPARG",
    "hif-1α": "HIF1A", "hif1α": "HIF1A", "hif1a": "HIF1A", "hif-1a": "HIF1A",
    "p53": "TP53", "tp53": "TP53",
    "androgen receptor": "AR", "ar": "AR",
    "estrogen receptor": "ESR1", "er": "ESR1", "esr1": "ESR1",
    "glucocorticoid receptor": "NR3C1", "gr": "NR3C1",
    "vitamin d receptor": "VDR", "vdr": "VDR",

    # ----- MAPK / kinase signaling -----
    "mapk": "MAPK_family", "mapks": "MAPK_family",
    "mapk signaling pathway": "MAPK_family",
    "erk1/2": "MAPK_family", "erk": "MAPK_family",
    "p38": "MAPK14", "mapk14": "MAPK14",
    "jnk": "MAPK8", "mapk8": "MAPK8",
    "jak1": "JAK1", "jak2": "JAK2", "jak3": "JAK3",
    "jak/stat": "JAK_STAT_pathway", "jak-stat": "JAK_STAT_pathway",
    "stat1": "STAT1", "stat3": "STAT3", "stat5": "STAT5",
    "akt": "AKT1", "akt1": "AKT1", "p-akt": "AKT1", "pkb": "AKT1",
    "pi3k": "PI3K_family", "pi3k/akt": "PI3K_AKT_pathway",
    "mtor": "MTOR",
    "ampk": "PRKAA1", "prkaa1": "PRKAA1",
    "wnt/β-catenin": "WNT_pathway", "β-catenin": "CTNNB1", "ctnnb1": "CTNNB1",

    # ----- NF-κB / inflammation -----
    "nf-κb": "NFKB_pathway", "nf-kappab": "NFKB_pathway",
    "nfkb": "NFKB_pathway", "nf kappa b": "NFKB_pathway",
    "nfκb": "NFKB_pathway", "nfkb1": "NFKB1", "rela": "RELA",
    "p65": "RELA",
    "tnf-α": "TNF", "tnf-alpha": "TNF", "tnfα": "TNF", "tnf": "TNF",
    "il-1": "IL1B", "il-1β": "IL1B", "il1b": "IL1B",
    "il-6": "IL6", "il6": "IL6",
    "il-10": "IL10", "il10": "IL10",
    "ifn-γ": "IFNG", "ifng": "IFNG",
    "cox-2": "PTGS2", "ptgs2": "PTGS2",
    "cox-1": "PTGS1", "ptgs1": "PTGS1",
    "inos": "NOS2", "nos2": "NOS2",
    "enos": "NOS3",
    "icam-1": "ICAM1", "icam1": "ICAM1",
    "vcam-1": "VCAM1", "vcam1": "VCAM1",
    "mcp-1": "CCL2", "ccl2": "CCL2",
    "cxcl8": "CXCL8", "il-8": "CXCL8",

    # ----- Apoptosis / cell death -----
    "bcl-2": "BCL2", "bcl2": "BCL2",
    "bax": "BAX",
    "bcl-xl": "BCL2L1", "bclxl": "BCL2L1",
    "caspase-3": "CASP3", "casp3": "CASP3",
    "caspase-9": "CASP9", "casp9": "CASP9",
    "caspase-8": "CASP8", "casp8": "CASP8",
    "parp": "PARP1", "parp-1": "PARP1", "parp1": "PARP1",
    "cytochrome c": "CYCS", "cycs": "CYCS",

    # ----- Antioxidant / redox -----
    "ho-1": "HMOX1", "hmox1": "HMOX1", "heme oxygenase-1": "HMOX1",
    "sod": "SOD_family", "sod1": "SOD1", "sod2": "SOD2",
    "gpx": "GPX_family", "gpx1": "GPX1",
    "catalase": "CAT", "cat": "CAT",
    "nqo1": "NQO1",
    "gclc": "GCLC", "gclm": "GCLM",

    # ----- Other targets -----
    "5-ht": "5HT_pathway", "serotonin": "5HT_pathway",
    "dopamine": "DA_pathway", "5-ht2a": "HTR2A",
    "gaba": "GABA_pathway",
    "acetylcholinesterase": "ACHE", "ache": "ACHE",
    "tubulin": "TUBB_family",
    "topoisomerase ii": "TOP2_family",
    "bcr-abl": "BCR_ABL1",
    "egfr": "EGFR", "her2": "ERBB2", "erbb2": "ERBB2",
    "vegf": "VEGFA", "vegfa": "VEGFA",

    # ----- Organ / tissue-level (NOT genes — keep as descriptors) -----
    "liver": "ORGAN_liver", "hepatic tissue": "ORGAN_liver",
    "kidney": "ORGAN_kidney", "renal": "ORGAN_kidney",
    "heart": "ORGAN_heart", "cardiac tissue": "ORGAN_heart",
    "brain": "ORGAN_brain", "neural": "ORGAN_brain",
    "intestine": "ORGAN_intestine", "gut": "ORGAN_intestine",
    "lung": "ORGAN_lung",
    "bone marrow": "ORGAN_bone_marrow",
    "hematopoietic stem cells": "hematopoietic_progenitor",

    # ----- Glucose / insulin (TCM frequent) -----
    "insulin": "INS", "ins": "INS", "ins1": "INS",
    "pdx1": "PDX1", "glut4": "SLC2A4", "slc2a4": "SLC2A4",

    # ----- Misc TCM-relevant -----
    "absorption enhancement": "absorption_modulation",
    "permeability": "membrane_permeability",
    "alcohol metabolizing enzymes": "ADH_family",
    "adh": "ADH_family",
    "aldehyde dehydrogenase": "ALDH_family", "aldh": "ALDH_family",
    "monoamine oxidase": "MAO_family", "mao": "MAO_family",
    "mao-a": "MAOA", "mao-b": "MAOB",
}


# =====================================================================
# FAMILY MAP — canonical target → functional family
# =====================================================================
FAMILY_MAP: dict[str, str] = {}

# Build family map programmatically
_CYP_LIKE = {"CYP_family", "CYP1A1", "CYP1A2", "CYP1B1", "CYP2A6", "CYP2B6",
             "CYP2C8", "CYP2C9", "CYP2C19", "CYP2D6", "CYP2E1",
             "CYP3A4", "CYP3A5", "CYP3A7", "CYP19A1"}
for k in _CYP_LIKE:
    FAMILY_MAP[k] = "cytochrome_P450"

_ABC = {"ABCB1", "ABCB11", "ABCG2", "ABCC1", "ABCC2", "ABCC3", "ABCC4", "ABCC5"}
for k in _ABC:
    FAMILY_MAP[k] = "ABC_transporter"

_SLC = {"SLCO1B1", "SLCO1B3", "SLCO2B1", "SLC22A1", "SLC22A2",
        "SLC22A6", "SLC22A8", "SLC47A1", "SLC47A2", "SLC10A1", "SLC15A1",
        "SLC2A4"}
for k in _SLC:
    FAMILY_MAP[k] = "SLC_transporter"

_UGT = {"UGT_family", "UGT1A1", "UGT1A3", "UGT1A4", "UGT1A6", "UGT1A9",
        "UGT2B7", "UGT2B15", "UGT2B17"}
for k in _UGT:
    FAMILY_MAP[k] = "UGT_phase_II"

for k in ["SULT_family", "SULT1A1", "SULT1E1"]:
    FAMILY_MAP[k] = "SULT_phase_II"
for k in ["GST_family", "GSTP1", "GSTA1"]:
    FAMILY_MAP[k] = "GST_phase_II"

_NUC_RCPT = {"NR1I2", "NR1I3", "NR1H4", "NR1H3", "AHR", "PPARA", "PPARG",
             "VDR", "AR", "ESR1", "NR3C1", "HIF1A", "TP53", "NFE2L2", "KEAP1"}
for k in _NUC_RCPT:
    FAMILY_MAP[k] = "nuclear_receptor_TF"

_KINASE_PATHWAY = {"MAPK_family", "MAPK14", "MAPK8", "JAK1", "JAK2", "JAK3",
                   "STAT1", "STAT3", "STAT5", "AKT1", "PI3K_family", "MTOR",
                   "PRKAA1", "JAK_STAT_pathway", "PI3K_AKT_pathway",
                   "WNT_pathway", "CTNNB1"}
for k in _KINASE_PATHWAY:
    FAMILY_MAP[k] = "kinase_pathway"

_INFLAMM = {"NFKB_pathway", "NFKB1", "RELA", "TNF", "IL1B", "IL6", "IL10",
            "IFNG", "PTGS2", "PTGS1", "NOS2", "NOS3", "ICAM1", "VCAM1",
            "CCL2", "CXCL8"}
for k in _INFLAMM:
    FAMILY_MAP[k] = "inflammation_cytokine"

_APOPTOSIS = {"BCL2", "BAX", "BCL2L1", "CASP3", "CASP9", "CASP8",
              "PARP1", "CYCS"}
for k in _APOPTOSIS:
    FAMILY_MAP[k] = "apoptosis"

_REDOX = {"HMOX1", "SOD_family", "SOD1", "SOD2", "GPX_family", "GPX1",
          "CAT", "NQO1", "GCLC", "GCLM"}
for k in _REDOX:
    FAMILY_MAP[k] = "antioxidant_redox"

_ORGAN = {"ORGAN_liver", "ORGAN_kidney", "ORGAN_heart", "ORGAN_brain",
          "ORGAN_intestine", "ORGAN_lung", "ORGAN_bone_marrow"}
for k in _ORGAN:
    FAMILY_MAP[k] = "organ_tissue"

for k in ["5HT_pathway", "DA_pathway", "GABA_pathway",
          "HTR2A", "ACHE", "MAO_family", "MAOA", "MAOB"]:
    FAMILY_MAP[k] = "neurotransmitter_pathway"

for k in ["INS", "PDX1", "ADH_family", "ALDH_family"]:
    FAMILY_MAP[k] = "endocrine_metabolism"

for k in ["TUBB_family", "TOP2_family", "BCR_ABL1",
          "EGFR", "ERBB2", "VEGFA"]:
    FAMILY_MAP[k] = "oncology_target"

for k in ["hematopoietic_progenitor", "membrane_permeability",
          "absorption_modulation"]:
    FAMILY_MAP[k] = "other_physiological"


# =====================================================================
# Splitting & normalization functions
# =====================================================================
# Order matters: try longer delimiters first
_SPLIT_REGEX = re.compile(r"\s*(?:,|;|/|\band\b|\bor\b|\+)\s*", re.IGNORECASE)
_CLEAN_REGEX = re.compile(r"[\(\)\[\]\"']")


def normalize_token(token: str) -> str | None:
    """Normalize a single target token to canonical form."""
    if not token or not isinstance(token, str):
        return None
    t = token.strip().lower()
    t = _CLEAN_REGEX.sub("", t)
    t = re.sub(r"\s+", " ", t)
    if not t or t in {"null", "none", "n/a", "na", "-", "—"}:
        return None
    # Direct lookup
    if t in ALIAS_MAP:
        return ALIAS_MAP[t]
    # Try without dashes (e.g. "p-gp" → "pgp" lookup)
    t_no_dash = t.replace("-", "").replace(" ", "")
    if t_no_dash in ALIAS_MAP:
        return ALIAS_MAP[t_no_dash]
    # Greedy CYP detection (e.g. "cyp 3a4" → "cyp3a4")
    m = re.match(r"^(cyp)\s*(\d+[a-z]\d*)$", t)
    if m and (m.group(1) + m.group(2)) in ALIAS_MAP:
        return ALIAS_MAP[m.group(1) + m.group(2)]
    return None


def split_and_normalize(field: str) -> list[str]:
    """Split a multi-target string and return list of canonical targets."""
    if not field or not isinstance(field, str):
        return []
    parts = _SPLIT_REGEX.split(field)
    canon = []
    seen = set()
    for p in parts:
        c = normalize_token(p)
        if c and c not in seen:
            canon.append(c)
            seen.add(c)
    return canon


def get_family(canonical: str | None) -> str | None:
    if not canonical:
        return None
    return FAMILY_MAP.get(canonical, "unmapped")


# =====================================================================
# Main pipeline
# =====================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary")
    args = ap.parse_args()

    safe = args.model.replace("/", "__").replace(".", "_")
    in_path = LLM_DIR / f"{args.prefix}_{safe}.interactions.parquet"
    out_path = LLM_DIR / f"{args.prefix}_{safe}.interactions_normalized.parquet"

    if not in_path.exists():
        print(f"FATAL: {in_path.relative_to(REPO)} not found")
        return

    df = pd.read_parquet(in_path)
    n = len(df)
    print(f"{'='*72}\n  Day 9 T1: Target normalization\n{'='*72}")
    print(f"  Input:  {in_path.relative_to(REPO)} ({n:,} rows)")

    # Apply
    df["target_list"] = df["specific_target"].apply(
        lambda s: split_and_normalize(s) if pd.notna(s) else []
    )
    df["target_canonical"] = df["target_list"].apply(
        lambda lst: lst[0] if lst else None
    )
    df["target_family"] = df["target_canonical"].apply(get_family)
    df["target_n"] = df["target_list"].apply(len)
    # Store list as pipe-delimited for parquet portability
    df["target_list_str"] = df["target_list"].apply(
        lambda lst: "|".join(lst) if lst else None
    )
    df_out = df.drop(columns=["target_list"]).rename(
        columns={"target_list_str": "target_list"}
    )

    df_out.to_parquet(out_path, index=False)

    # ------- Summary stats -------
    n_with_target = df["specific_target"].notna().sum()
    n_normalized = df["target_canonical"].notna().sum()
    n_multi = (df["target_n"] >= 2).sum()
    print(f"\n  Output: {out_path.relative_to(REPO)} ({len(df_out):,} rows)")
    print(f"\n  Coverage:")
    print(f"    Records with specific_target (non-null):   {n_with_target:,} "
          f"({n_with_target/n*100:.1f}%)")
    print(f"    Records normalized to canonical:           {n_normalized:,} "
          f"({n_normalized/n*100:.1f}%, {n_normalized/n_with_target*100:.1f}% of named)")
    print(f"    Records with multi-target (n≥2):           {n_multi:,} "
          f"({n_multi/n*100:.1f}%)")

    # Family distribution
    print(f"\n  target_family distribution (canonical primary target):")
    fam_counts = df["target_family"].value_counts(dropna=False)
    for fam, cnt in fam_counts.items():
        print(f"    {(fam or '(null)'):30s} {cnt:>5,} "
              f"({cnt/n*100:.1f}%)")

    # Top canonical targets
    print(f"\n  Top 25 canonical targets:")
    for tgt, cnt in df["target_canonical"].value_counts().head(25).items():
        fam = get_family(tgt)
        print(f"    {tgt:30s} {cnt:>5,}   [{fam}]")

    # Unmapped audit: see what original strings failed to map
    unmapped = df[
        df["specific_target"].notna() & df["target_canonical"].isna()
    ]["specific_target"]
    if len(unmapped) > 0:
        print(f"\n  ⚠️  Unmapped (manual review candidates, top 20):")
        for tgt, cnt in unmapped.value_counts().head(20).items():
            print(f"    {tgt[:55]:55s} {cnt:>4,}")
        print(f"\n    Total unmapped: {len(unmapped):,} interactions "
              f"({len(unmapped)/n*100:.1f}%)")
        print(f"    Tip: add aliases to ALIAS_MAP and re-run if any of "
              f"the above are recurring.")

    print(f"\n  ✓ Done. Next: 16_classify_interaction_type.py (T4)")


if __name__ == "__main__":
    main()
