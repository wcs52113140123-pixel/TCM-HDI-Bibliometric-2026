# Software Versions Used in This Project

Last updated: 2026-05-13

This document records the exact version of every software, package, and service used 
in the TCM-HDI bibliometric analysis project. All versions are pinned for reproducibility.

---

## Operating System

- **OS**: Windows 11 Pro, version 25H2
- **Build**: 26200.8037
- **Experience pack**: Windows Feature Experience Pack 1000.26100.300.0
- **Architecture**: x64 (Intel Core i7-14650HX, 2.20 GHz)
- **RAM**: 32.0 GB

---

## Python Environment

- **Python**: 3.11.x (managed via conda)
- **Environment name**: `tcm-hdi`
- **Dependency lock file**: `00_setup/requirements.txt`

To restore: 
```bash
conda create -n tcm-hdi python=3.11 -y
conda activate tcm-hdi
pip install -r 00_setup/requirements.txt
```

---

## R Environment

- **R**: version 4.5.2 (2025-10-31 ucrt) `Unsuffered Bonhomie`
- **RStudio**: 2024.04.2+764
- **Dependency lock file**: `renv.lock`

To restore:
```r
# In RStudio, open the .Rproj file
renv::restore()
```

---

## Bibliometric Analysis Software

| Software | Version | Release Date | Purpose |
|----------|---------|--------------|---------|
| **VOSviewer** | 1.6.20 | 2023-10-31 | Country/institution/journal/keyword co-occurrence networks |
| **CiteSpace** | 6.4.R1 | 2024 | Citation networks, dual-map overlay, citation burst detection |
| **Cytoscape** | 3.10.4 | 2024-10-24 | Three-layer pharmacological network (TCM-CYP-drug) |

### Cytoscape Apps installed
- stringApp (STRING PPI integration)
- CytoHubba (centrality analysis)
- yFiles Layout Algorithms (advanced layouts)

---

## Reference Management

- **Zotero**: 8.0.4 (64-bit)

---

## Figure Editing

- **Inkscape**: 1.3.2 (vector graphics post-processing for final figures)

---

## API Services

To be confirmed on Day 8 (LLM extraction phase).

- **Anthropic Claude API**: [official / third-party proxy — TBD]
  - Model: `claude-sonnet-4-5` (or compatible)
- **OpenAI API**: [official / third-party proxy — TBD]
  - Available as backup / cross-validation only
- **OpenAlex API**: free, registered to `[email]` for polite pool
- **NCBI E-utilities**: free, API key registered

---

## File Conventions

- **Encoding**: UTF-8 throughout
- **Line endings**: LF (Unix-style) for cross-platform compatibility  
- **Figure resolution**: 300 DPI minimum (PNG) + SVG vector backup
- **Color profile**: sRGB

---

## Reproducibility Note

When citing this project or reporting results, the Methods section will state:

> Bibliometric analyses were performed using R-Bibliometrix (version locked in 
> `renv.lock`), VOSviewer 1.6.20, and CiteSpace 6.4.R1. Pharmacological network 
> integration was conducted in Cytoscape 3.10.4 with stringApp. All Python-based 
> analyses used the environment specified in `requirements.txt`. Final figures 
> were edited in Inkscape 1.3.2. Complete reproducibility instructions are 
> available at: [GitHub URL]
