# PubMed Search Strategy — Final v1.0

**Status**: EXECUTED  
**Database**: PubMed (NLM/NCBI)  
**Platform**: NCBI E-utilities via Biopython Entrez  
**Search date**: 2026-05-13  

---

## 1. Final Query (PubMed 2026 syntax, paste-ready for web UI)
("herb-drug interaction"[TIAB] OR "herb-drug interactions"[TIAB] OR "herb drug interaction"[TIAB] OR "herb drug interactions"[TIAB] OR "herbal drug interaction"[TIAB] OR "herbal drug interactions"[TIAB] OR "Herb-Drug Interactions"[MH] OR (("traditional Chinese medicine"[TIAB] OR "Chinese herbal medicine"[TIAB] OR "Chinese herbal"[TIAB] OR "TCM"[TIAB] OR "Medicine, Chinese Traditional"[MH] OR "Drugs, Chinese Herbal"[MH]) AND ("drug interaction"[TIAB] OR "drug interactions"[TIAB] OR "pharmacokinetic interaction"[TIAB] OR "pharmacodynamic interaction"[TIAB] OR "Drug Interactions"[MH])) OR (("traditional Chinese medicine"[TIAB] OR "Chinese herbal medicine"[TIAB] OR "Medicine, Chinese Traditional"[MH] OR "Drugs, Chinese Herbal"[MH]) AND ("CYP3A4"[TIAB] OR "CYP2D6"[TIAB] OR "CYP1A2"[TIAB] OR "CYP2C9"[TIAB] OR "CYP2C19"[TIAB] OR "cytochrome P450"[TIAB] OR "P-glycoprotein"[TIAB] OR "P-gp"[TIAB] OR "Cytochrome P-450 Enzyme System"[MH] OR "drug metabolism"[TIAB] OR "drug transporter"[TIAB] OR "drug transporters"[TIAB]))) AND 2005/01/01:2025/12/31[PDAT] AND english[LA] AND ("journal article"[PT] OR "review"[PT]) NOT ("comment"[PT] OR "editorial"[PT] OR "letter"[PT])
For 2026 partial-year supplement: replace `2005/01/01:2025/12/31[PDAT]` with `2026/01/01:2026/12/31[PDAT]`.

---

## 2. Field Tag Reference (PubMed 2026 syntax)

| Tag | Meaning | Notes |
|-----|---------|-------|
| [TIAB] | Title + Abstract | Most common keyword field |
| [MH] | MeSH heading (with explosion) | Maps controlled vocabulary |
| [PT] | Publication Type | Article/Review/Editorial filter |
| [LA] | Language | Two-letter code or full name |
| [PDAT] | Publication Date | Date-range with `:` separator |

Boolean operators (AND, OR, NOT) must be UPPERCASE per PubMed 2026 requirements.

---

## 3. Verified MeSH headings used

| MeSH heading | Tree | Use case |
|--------------|------|----------|
| Herb-Drug Interactions | D27.505 (Pharmacological Phenomena) | Core MeSH for HDI (introduced 2004) |
| Medicine, Chinese Traditional | E02 (Therapeutics) | Direct TCM concept |
| Drugs, Chinese Herbal | D26 (Pharmaceutical Preparations) | TCM herbal preparations |
| Drug Interactions | G07 (Chemicals and Drugs) | General drug-drug interaction |
| Cytochrome P-450 Enzyme System | D08.244 (Enzymes) | Note the hyphenated form |

---

## 4. Hybrid TIAB + MeSH strategy rationale

PubMed unique strength: human-curated MeSH terms applied to every indexed citation 
(typically 6-12 months after publication). The strategy combines:

- **TIAB** keywords for recent papers not yet MeSH-indexed (i.e., the last 6-12 months)
- **MeSH** headings to capture older papers using consistent terminology even where 
  authors phrased the topic differently

This hybrid approach achieves higher recall than either component alone.

---

## 5. Execution log

### 5.1 Main analysis (PDAT 2005-2025)

| Item | Value |
|------|-------|
| API reported | 3,870 |
| PMIDs retrieved | 3,870 |
| Records saved | 3,867 |
| Skipped (XML parse error) | 3 (0.08%) |
| Errors | 0 |
| Elapsed | 10.7 min |
| File size | 8.4 MB |
| Rate limit used | 10 req/sec (with NCBI API key) |
| Fields extracted per record | pmid, title, year, journal, abstract, authors, mesh_terms, doi, language, publication_types |

### 5.2 Partial-year extension (PDAT 2026)

| Item | Value |
|------|-------|
| API reported | 106 |
| Records saved | 106 |
| Errors | 0 |
| Elapsed | 0.5 min |
| File size | 0.3 MB |

### 5.3 Cross-database comparison (main analysis only)

| Metric | WoS | Scopus | OpenAlex | PubMed |
|--------|-----|--------|----------|--------|
| Main N (2005-2025) | 3,091 | 7,181 | 2,513 | 3,867 |
| Partial 2026 N | 83 | 230 | 95 | 106 |
| Abstract coverage | ~95% | 97.7% | 73.3% | high (TIAB-filtered) |
| References field | yes | 98.1% | 75.8% | not extracted |
| **Unique strength** | citation network | breadth | concepts/topics | **MeSH terms** |
| Redistribution | restricted | restricted | CC0 | NLM public domain |

---

## 6. Data redistribution policy

**PubMed data is in the U.S. public domain** (National Library of Medicine). 
All PubMed raw JSONL files are version-controlled in this repository for 
full reproducibility, alongside the OpenAlex CC0 data.

---

## 7. Reproducibility note

To reproduce this search:

1. Install Biopython: `pip install biopython`
2. Set `NCBI_EMAIL=your.email@example.com` in `.env` (required by NCBI terms)
3. Optional but recommended: get a free NCBI API key from 
   https://www.ncbi.nlm.nih.gov/account/settings/ to lift rate limit to 10/sec
4. Set `NCBI_API_KEY=your_key` in `.env`
5. Run: `python 01_data_acquisition/04_pubmed_pull.py`
6. For 2026 partial: `python 01_data_acquisition/04_pubmed_pull.py --partial-2026`
7. For N-count verification only: `python 01_data_acquisition/04_pubmed_pull.py --count-only`

Output JSONL has one record per line; each record is a JSON object containing 
pmid, title, year, journal, abstract, authors[], mesh_terms[], doi, 
language[], publication_types[].

---

## 8. Methods section draft

> PubMed was queried via NCBI E-utilities on May 13, 2026, using a hybrid 
> TIAB-keyword and MeSH-heading strategy. The query combined direct 
> herb-drug interaction phrases with controlled vocabulary terms 
> ("Herb-Drug Interactions"[MH], "Medicine, Chinese Traditional"[MH], 
> "Drugs, Chinese Herbal"[MH]) and was further refined by including TCM 
> keyword × CYP/transporter mechanism combinations to maximize recall for 
> mechanism-focused literature. Filters limited results to English-language 
> Articles and Reviews published 2005-2025. The search retrieved 3,870 
> records, of which 3,867 were successfully parsed from MEDLINE XML (99.92% 
> recovery). MeSH terms — PubMed's unique strength — were extracted for 
> all records and will serve as an independent benchmark for topic 
> modeling validation in subsequent analysis. An additional supplementary 
> search for 2026 partial-year publications (January 1 - May 13) returned 
> 106 records. All PubMed raw JSONL files are version-controlled in the 
> project repository as PubMed data is in the U.S. public domain.
