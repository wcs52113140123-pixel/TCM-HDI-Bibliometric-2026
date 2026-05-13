# WoS Search Strategy — DRAFT v1.0

**Date drafted**: 2026-05-13  
**Database**: Web of Science Core Collection  
**Editions**: All (SCI-EXPANDED, SSCI, ESCI, etc.)

---

## Final Query String (single-line, paste-ready)

TS=("herb-drug interaction*" OR "herb drug interaction*" OR "herbal drug interaction*" OR "herbal-drug interaction*" OR "TCM-drug interaction*" OR "TCM drug interaction*" OR "Chinese medicine drug interaction*" OR "phytochemical drug interaction*" OR "botanical drug interaction*" OR (("traditional Chinese medicine" OR "Chinese herbal medicine" OR "Chinese herbal" OR "Chinese medicine" OR "TCM" OR "Kampo" OR "herbal medicine" OR "phytomedicine" OR "phytotherapy") AND ("drug interaction*" OR "pharmacokinetic interaction*" OR "pharmacodynamic interaction*" OR "drug-drug interaction*" OR "drug drug interaction*")) OR (("traditional Chinese medicine" OR "Chinese herbal medicine" OR "Chinese herbal" OR "Chinese medicine") AND ("CYP" OR "cytochrome P450" OR "CYP3A4" OR "CYP2D6" OR "CYP1A2" OR "CYP2C9" OR "CYP2C19" OR "CYP2E1" OR "P-glycoprotein" OR "P-gp" OR "MDR1" OR "OATP" OR "OAT*" OR "MRP*" OR "BCRP" OR "UGT" OR "UDP-glucuronosyltransferase" OR "drug metabolism" OR "drug transporter*" OR "drug efflux" OR "drug absorption"))) AND PY=(2005-2026) AND DT=(Article OR Review) AND LA=(English)

---

## Design Rationale

### Date range: 2005-2026
- 2005 is the conventional starting point for modern CYP-mediated HDI research
- FDA Drug Interaction Guidance v1 published 2006
- 21-year window allows early/growth/mature phase analysis

### Language: English only
- Aligns with all major 2024-2026 same-topic bibliometric reviews in Frontiers/JEP/Phytomedicine
- Avoids dual-language methodological complexity
- Trade-off acknowledged: ~30-40% Chinese-language TCM HDI literature excluded
- This is documented as a study limitation in Discussion

### Document types: Article OR Review
- Article = original research (PK/PD experiments, clinical reports)
- Review = synthesis literature (critical for citation network analysis)
- Excludes: meeting abstracts, editorials, letters, errata, book chapters

### Included Asian traditional medicines
- Traditional Chinese Medicine (TCM): primary scope
- Kampo (Japanese herbal medicine): included — shares >95% formula base with TCM
- Korean Medicine: NOT included initially — re-evaluate if N < 1500

### Included CYP/transporter targets
- Six major CYP enzymes (3A4, 2D6, 1A2, 2C9, 2C19, 2E1)
- Major transporters (P-gp/MDR1, OATP, OAT*, MRP*, BCRP)
- Phase II enzymes (UGT)

---

## Expected N range: 1500-3000 (target zone)

If N is outside this range, contingency plans:
- N < 1500: add Korean herbal medicine keywords
- N > 3500: tighten to strictly TCM keywords
- N < 1000 or > 5000: review query for syntax error

---

## Pre-execution checklist

- [ ] Query string syntax-validated by user
- [ ] WoS Core Collection access confirmed
- [ ] Editions: All selected
- [ ] Search date recorded
- [ ] User has Endnote/RIS/tab-delimited export permission

---

## Execution log (filled after execution)

- Search executed on: ___________
- Total N (raw): ___________
- After date filter: ___________
- After DT filter: ___________
- After LA filter: ___________
- Final N: ___________
- Notes: ___________