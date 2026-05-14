# Day 2 Log — 2026-05-14

## Completed
- 4 unified database loaders (load_wos.py + load_scopus.py + load_openalex.py + load_pubmed.py)
- 5-stage integration pipeline (concat -> DOI dedup -> fuzzy -> OpenAlex filter -> finalize)
- Final integrated_corpus.parquet: 9,438 unique TCM-HDI publications (2005-2025)
- Partial 2026 supplement: 316 publications
- PRISMA flow data: data/processed/prisma_flow_data.json
- Decisions A1+B1+C-Standard locked and documented in decisions.md

## Bugs hit & lessons
- Scopus CSV uses "; " not "," as author separator (95.2% records confirmed)
- parquet serialization converts Python list -> ndarray; downstream `==` comparison breaks
- pandas DataFrame.apply returning tuple auto-expands columns; need 2 separate .apply calls
- Each stage script must check prior parquet existence before reading (add assert next time)

## Tomorrow (Day 3)
- Block 1: publications/year trend analysis (use prisma_flow_data.json + integrated_corpus.parquet)
- Block 2-3: country + institution + author rankings
- Block 4: journal distribution + IF mapping
- Block 5: matplotlib draft figures
- Target: 4-6 hours, ~Figure 2-3 sketches by end of day

## Open questions for Day 3
- 25 records with year=2026 in MAIN dataset — keep as-is or filter? (decided to keep, but flag in Methods)
- Author name disambiguation: use ORCID where available, else use last_name + first_initial blocking
- Country extraction: simple regex from affiliations, refine with ROR API if time
