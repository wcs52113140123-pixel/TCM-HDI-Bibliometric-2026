# TCM-HDI Bibliometric Analysis 2026

> A bibliometric and pharmacological network analysis of traditional Chinese medicine 
> (TCM) herb-drug interactions (2005-2026), integrating four databases 
> (Web of Science + Scopus + OpenAlex + PubMed), LLM-assisted metadata extraction, 
> and three-layer pharmacological network construction.

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE-MIT)
[![License: CC BY 4.0](https://img.shields.io/badge/Content-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![R 4.5](https://img.shields.io/badge/R-4.5.2-blue.svg)](https://www.r-project.org/)

---

## Overview

This repository contains the **complete reproducible workflow** for a bibliometric 
review covering 2005-2026 publications on herb-drug interactions (HDI) involving 
traditional Chinese medicine. The work targets submission to *Frontiers in Pharmacology* 
(IF 5.6) with potential escalation to *Journal of Ethnopharmacology*, *Phytomedicine*, 
or *Pharmacological Research* depending on results.

The methodological contribution is three-fold:

1. **Four-database integration** (WoS + Scopus + OpenAlex + PubMed) with an 
   automated deduplication pipeline (DOI matching + fuzzy title matching).
2. **LLM-assisted structured metadata extraction** of HDI-specific fields 
   (TCM herb, active compound, Western drug, CYP enzymes, transporters, 
   study type, clinical outcome, risk level) using Claude Sonnet with 
   prompt-engineered structured JSON output and human-annotated ground truth 
   validation (100 papers, target F1 > 0.80).
3. **Three-layer pharmacological network construction** linking TCM active 
   compounds → CYP enzymes/transporters → Western drugs, integrating DrugBank, 
   GeneCards, SwissTargetPrediction, and STRING PPI data, visualized in Cytoscape.

This combination — to our knowledge — has not been applied to TCM-HDI bibliometrics 
previously. The last comprehensive review (Pharmacological Research, 2016) is now 
10 years stale.

---

## Repository Structure
TCM-HDI-Bibliometric-2026/
├── 00_setup/                      # Environment configuration & dependency locks
├── 01_data_acquisition/           # Database search strategies & API pull scripts
├── 02_data_integration/           # Cross-database deduplication & quality control
├── 03_basic_bibliometrics/        # R bibliometrix + VOSviewer + CiteSpace
├── 04_topic_modeling/             # Embedding-based topic clustering (BGE + UMAP + HDBSCAN)
├── 05_llm_extraction/             # Prompts, ground truth, batch extraction, validation
├── 06_pharmacology_network/       # DrugBank + GeneCards + SwissTarget + STRING → Cytoscape
├── 07_subgroup_analysis/          # HDI mechanism stratification (PK-CYP / PK-transporter / PD / dual)
├── 08_citation_burst/             # Citation network + temporal centrality + burst detection
├── 09_figures/                    # Main figure generation scripts (Fig 1-9)
├── 10_tables/                     # Main table generation scripts (Tab 1-5)
├── 11_supplementary/              # Supplementary figures & tables
├── 12_manuscript/                 # Manuscript drafts, cover letter, response to reviewers
├── data/                          # Data files (raw excluded; see .gitignore)
│   ├── raw/                       # WoS/Scopus/OpenAlex/PubMed exports (gitignored)
│   ├── processed/                 # Cleaned, deduplicated, integrated datasets
│   ├── llm_output/                # LLM extraction results
│   └── pharmacology/              # DrugBank/GeneCards/STRING data
├── docs/                          # Project documentation
│   ├── software_versions.md       # Exact versions of all software/packages used
│   ├── reproducibility_guide.md   # Step-by-step reproduction instructions
│   └── data_dictionary.md         # Field definitions for all datasets
├── requirements.txt -> 00_setup/  # Python dependency lock
├── renv.lock                      # R dependency lock
├── .env.example                   # Template for API key configuration
├── LICENSE-MIT                    # MIT License (applies to code)
└── LICENSE-CC-BY-4.0              # CC-BY-4.0 (applies to documentation/figures/data)
---

## Quick Start

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| OS | Windows 11 / macOS / Linux | Tested on Windows 11 Pro 25H2 |
| Python | 3.11 (via conda) | Data integration, LLM extraction, network analysis |
| R | 4.5.2 + RStudio 2024.04.2+764 | Bibliometrix analyses, ggplot2 figures |
| VOSviewer | 1.6.20 | Co-occurrence networks |
| CiteSpace | 6.4.R1 Advanced | Citation networks, dual-map, burst detection |
| Cytoscape | 3.10.4 | Pharmacological network visualization |
| Inkscape | 1.3.2 | Final figure post-processing |
| Zotero | 8.0.4 | Reference management |

API access required:
- **Anthropic Claude API** (or compatible third-party proxy) for Day 8-10 LLM extraction
- **NCBI E-utilities** (free, registration recommended for higher rate limit)
- **OpenAlex** (free, email registration for polite pool)

### Setup

```bash
# 1. Clone the repository
git clone git@github.com:wcs52113140123-pixel/TCM-HDI-Bibliometric-2026.git
cd TCM-HDI-Bibliometric-2026

# 2. Python environment
conda create -n tcm-hdi python=3.11 -y
conda activate tcm-hdi
pip install -r 00_setup/requirements.txt

# 3. R environment (in RStudio)
# Open TCM-HDI-Bibliometric-2026.Rproj, then in R console:
renv::restore()

# 4. API configuration
cp .env.example .env
# Edit .env with your actual API keys (this file is gitignored)

# 5. Verify environment
python 00_setup/check_environment.py
# All "blocker" checks should pass before Day 1.
```

---

## Reproducibility Workflow

All analyses are fully scripted. The 21-day execution plan:

| Phase | Days | Activities | Outputs |
|-------|------|------------|---------|
| **Setup** | Day 0 | Environment, GitHub, software | Locked dependencies, this repo |
| **Data acquisition** | Day 1-3 | WoS/Scopus/OpenAlex/PubMed pulls, dedup, PRISMA | Figure 1, merged dataset |
| **Basic bibliometrics** | Day 4-7 | bibliometrix, country/institution/journal networks, topic modeling | Figures 2-5, 8 |
| **LLM extraction** | Day 8-10 | Prompt design, 100-paper ground truth, full batch run | Structured HDI metadata |
| **Pharmacology network** | Day 11-13 | DrugBank/GeneCards/STRING, three-layer Cytoscape, KEGG | Figures 6-7 (cover) |
| **Citation analysis** | Day 14-15 | Citation networks, burst, regulatory coverage | Figure 9 |
| **Supplementary** | Day 16 | Bradford, Lotka, cross-database validation | Supp Fig S1-S5 |
| **Writing** | Day 17-19 | Methods, Results, Discussion, Intro, Abstract | Manuscript draft |
| **Submission** | Day 20-21 | Polish, cover letter, submit to Frontiers in Pharmacology | v1.0 tag |

See `docs/reproducibility_guide.md` for complete step-by-step instructions.

To reproduce results from raw data:

```bash
# Data acquisition (mix of manual exports and automated pulls)
python 01_data_acquisition/03_openalex_pull.py
python 01_data_acquisition/04_pubmed_pull.py

# Integration
python 02_data_integration/02_deduplication.py

# Basic bibliometrics
Rscript 03_basic_bibliometrics/01_bibliometrix_run.R

# (Full pipeline documented in docs/reproducibility_guide.md)
```

---

## Methodological Innovations

### 1. Four-database integration

Most TCM bibliometric reviews use Web of Science alone. We integrate four databases 
with an explicit deduplication audit trail:

- DOI exact match (primary)
- Title fuzzy matching via Levenshtein distance ≥ 0.9 (secondary)
- Author + year + journal tuple matching (tertiary)
- Full deduplication log retained for audit

### 2. LLM-assisted structured HDI metadata extraction

Eight structured fields are extracted per article via prompt-engineered Claude Sonnet:

```json
{
  "tcm_herb_main": ["..."],
  "tcm_active_compound": ["..."],
  "western_drug": ["..."],
  "hdi_mechanism": "PK | PD | dual",
  "cyp_enzymes": ["CYP3A4", "..."],
  "transporters": ["P-gp", "OATP1B1", "..."],
  "study_type": "in_vitro | in_vivo_animal | clinical_trial | case_report | review",
  "clinical_outcome": "potentiation | reduction | adverse_event | no_effect",
  "risk_level": "high | moderate | low | unclear"
}
```

Validation against 100 manually annotated papers establishes per-field F1 scores 
(target: F1 > 0.80 for objective fields).

### 3. Three-layer pharmacological network

Layer 1 (TCM): herbs and active compounds  
Layer 2 (PK targets): CYP enzymes, transporters, conjugating enzymes  
Layer 3 (Western drugs): clinically prescribed drugs  

Edges weighted by reported frequency across the literature pool. 
Network topology metrics (degree centrality, betweenness, modularity) identify 
high-risk hubs. Sankey diagrams visualize TCM → CYP → drug flows.

---

## Project Status

**Current phase**: Day 0 — environment setup  
**Target submission**: 2026 (3 weeks from start)  
**Target journal**: *Frontiers in Pharmacology* (IF 5.6)

Daily commit history in this repo reflects actual progress.

---

## Citation

If you use this code, methodology, or extracted dataset, please cite:

```bibtex
@unpublished{tcm_hdi_2026,
  title  = {Herb-drug interactions of traditional Chinese medicine: 
            a bibliometric and pharmacological network analysis (2005-2026)},
  author = {Adalheiddr and collaborators},
  year   = {2026},
  note   = {Manuscript in preparation. Code: https://github.com/wcs52113140123-pixel/TCM-HDI-Bibliometric-2026}
}
```

---

## License

This project uses **dual licensing**:

- **Code** (Python scripts, R scripts, configuration): [MIT License](LICENSE-MIT)
- **Documentation, figures, extracted data, manuscript drafts**: 
  [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)

This dual structure follows the convention for academic open-source projects: 
maximally permissive for code reuse, attribution-required for scholarly outputs.

---

## Contact

**Adalheiddr**  
Brain development and neuroimmunology laboratory  
Beijing, China  

For technical issues with the code, please open a GitHub Issue.  
For research collaboration inquiries, please email directly.

---

## Acknowledgments

- Anthropic for Claude API access  
- The CWTS team at Leiden University for VOSviewer  
- Chaomei Chen (Drexel University) for CiteSpace  
- The Cytoscape Consortium  
- The bibliometrix R package developers (M. Aria & C. Cuccurullo)  
- All public databases queried: Web of Science, Scopus, OpenAlex, PubMed, 
  DrugBank, GeneCards, SwissTargetPrediction, STRING, KEGG
