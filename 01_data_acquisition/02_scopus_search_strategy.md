# Scopus Search Strategy — Final v1.0

**Status**: EXECUTED  
**Database**: Scopus (Elsevier)  
**Platform**: scopus.com (institutional access)  
**Search date**: 2026-05-13  

---

## 1. Final Query String
TITLE-ABS-KEY("herb-drug interaction*" OR "herb drug interaction*" OR "herbal drug interaction*" OR "herbal-drug interaction*" OR "TCM-drug interaction*" OR "TCM drug interaction*" OR "Chinese medicine drug interaction*" OR "phytochemical drug interaction*" OR "botanical drug interaction*" OR (("traditional Chinese medicine" OR "Chinese herbal medicine" OR "Chinese herbal" OR "Chinese medicine" OR "TCM" OR "Kampo" OR "herbal medicine" OR "phytomedicine" OR "phytotherapy") AND ("drug interaction*" OR "pharmacokinetic interaction*" OR "pharmacodynamic interaction*" OR "drug-drug interaction*" OR "drug drug interaction*")) OR (("traditional Chinese medicine" OR "Chinese herbal medicine" OR "Chinese herbal" OR "Chinese medicine") AND ("CYP" OR "cytochrome P450" OR "CYP3A4" OR "CYP2D6" OR "CYP1A2" OR "CYP2C9" OR "CYP2C19" OR "CYP2E1" OR "P-glycoprotein" OR "P-gp" OR "MDR1" OR "OATP" OR "OAT*" OR "MRP*" OR "BCRP" OR "UGT" OR "UDP-glucuronosyltransferase" OR "drug metabolism" OR "drug transporter*" OR "drug efflux" OR "drug absorption"))) AND PUBYEAR > 2004 AND PUBYEAR < 2026 AND (DOCTYPE(ar) OR DOCTYPE(re)) AND LANGUAGE("English")
For the 2026 partial-year supplement, the same TITLE-ABS-KEY / DOCTYPE / LANGUAGE constraints were applied with `PUBYEAR = 2026`.

---

## 2. Field Code Reference (Scopus syntax)

| Code | Meaning | Equivalent WoS |
|------|---------|----------------|
| TITLE-ABS-KEY() | Title + Abstract + Indexed Keywords + Author Keywords | TS= |
| PUBYEAR > / < / = | Publication year comparison | PY= |
| DOCTYPE(ar) | Article | DT=(Article) |
| DOCTYPE(re) | Review | DT=(Review) |
| LANGUAGE("English") | English-language documents | LA=(English) |

---

## 3. Inclusion / Exclusion criteria

Identical to the WoS search (see `01_wos_search_strategy.md` § 3-4). 
Both queries are designed to be semantically equivalent across the two 
platforms, allowing meaningful cross-database integration after deduplication.

---

## 4. Execution log

### 4.1 Main analysis (PUBYEAR 2005-2025)

| Item | Value |
|------|-------|
| Total raw results | 7,181 |
| Articles | 5,619 |
| Reviews | 1,562 |
| Records exported | 7,181 (single batch via "Download CSV") |
| Export format | CSV |
| Fields exported | 45 fields (including Abstract, References, DOI, Author Keywords, Funding, Affiliations) |
| Abstract coverage | 97.7% records with substantive content (>100 chars) |
| References coverage | 98.1% records with substantive content (>100 chars) |
| DOI coverage | 94.8% |
| File size | ~190 MB (estimate; actual size in inventory CSV) |

### 4.2 Partial-year extension (PUBYEAR = 2026)

| Item | Value |
|------|-------|
| Total results | 230 |
| Search date | 2026-05-13 |
| Coverage | 2026-01-01 to 2026-05-13 (partial year) |
| Use case | Discussion-level commentary on emerging trends only |
| File size | 4.84 MB |
| Abstract coverage | 100% (>100 chars) |
| References coverage | 99% (228/230 with >100 chars) |

### 4.3 Comparison with WoS

| Metric | WoS | Scopus | Scopus / WoS |
|--------|-----|--------|--------------|
| Main analysis N | 3,091 | 7,181 | 232% |
| 2026 partial N | 83 | 230 | 277% |
| Article share | 81.8% | 78.2% | similar |
| Review share | 18.2% | 21.8% | similar |

Scopus consistently retrieves more records than WoS for the same query, 
consistent with its broader coverage of Asia-Pacific pharmaceutical and 
chemistry journals. Substantial overlap between the two databases is 
expected and will be quantified during the deduplication step.

---

## 5. Export workflow

Unlike WoS (which requires per-batch manual export of ≤500 records), 
Scopus offers an asynchronous "Download CSV" feature that exports the 
entire result set as a single CSV file. This was used for both the main 
analysis (N=7,181) and the 2026 partial supplement (N=230).

The Download CSV feature, as of May 2026, includes the References field 
by default — a recent improvement that simplifies workflow compared with 
earlier (pre-2024) Scopus export behavior.

---

## 6. Output files

| Purpose | Path | Records | Size |
|---------|------|---------|------|
| Main analysis | `data/raw/scopus/scopus_all_7181.csv` | 7,181 | ~190 MB |
| Partial 2026 | `data/raw/scopus_partial2026/scopus_partial2026_all.csv` | 230 | 4.84 MB |

Complete machine-readable inventory: `01_data_acquisition/data_acquisition_inventory.csv`

---

## 7. Data redistribution policy

Scopus raw CSV exports are **NOT version-controlled** in this repository, 
in accordance with Elsevier's Terms of Use, which restrict bulk 
redistribution of Scopus data. The query string in § 1, search date, 
and sample-level metadata in § 4 provide sufficient information for a 
third party with Scopus access to fully reproduce the dataset.

---

## 8. Reproducibility note

To reproduce this search:

1. Access scopus.com with institutional Scopus privileges  
2. Navigate to Documents → Advanced document search  
3. Paste the query string (§ 1) into the search box  
4. Click Search; result count should match § 4.1 within a few percent 
   (counts grow slowly due to ongoing Scopus indexing)  
5. From the result page, click the "Download CSV" icon in the saved 
   search panel (NOT the page-level Export button, which has a 2,000-record 
   limit and requires manual page selection)  
6. Wait for the asynchronous export job to complete (typically 1-5 minutes 
   for a 7K-record result set); download the generated CSV file  
7. Save to `data/raw/scopus/` following the naming convention  

---

## 9. Methods section draft

> Scopus (Elsevier) was searched on May 13, 2026, using a TITLE-ABS-KEY 
> query semantically equivalent to the Web of Science strategy 
> (Supplementary File S1). The search retrieved 7,181 records published 
> between 2005 and 2025 (Articles and Reviews in English). All records 
> were exported in CSV format via Scopus's "Download CSV" feature, 
> including the References field for downstream citation network analysis. 
> An additional supplementary search for 2026 partial-year publications 
> (January 1 - May 13) returned 230 records. Abstract coverage was 97.7% 
> and References coverage was 98.1% for the main dataset.
