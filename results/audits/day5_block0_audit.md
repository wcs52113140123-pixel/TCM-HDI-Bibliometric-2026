# Day 5 Block 0 — Audit Report

- Repo root: `D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026`
- Python: `3.11.15` @ `C:\Users\wcs\.conda\envs\tcm-hdi\python.exe`

## A. Environment Check

| Package | Installed | Version | Purpose |
|---|---|---|---|
| `torch` | ✅ | `2.11.0` | PyTorch (CPU build is fine) |
| `transformers` | ✅ | `4.57.6` | HuggingFace transformers (loads SPECTER2) |
| `sentence_transformers` | ✅ | `2.5.1` | sentence-transformers (optional alt encoder) |
| `adapters` | ✅ | `1.3.0` | adapter-transformers (for SPECTER2 task-specific adapter) |
| `umap` | ✅ | `imported, version unknown` | umap-learn (UMAP dimensionality reduction) |
| `hdbscan` | ✅ | `0.8.33` | HDBSCAN clustering |
| `sklearn` | ✅ | `imported, version unknown` | scikit-learn (TF-IDF for topic labels) |
| `bertopic` | ❌ | `MISSING` | BERTopic (optional all-in-one wrapper) |
| `plotly` | ✅ | `5.18.0` | plotly (topic viz) |
| `matplotlib` | ✅ | `3.8.2` | matplotlib |
| `seaborn` | ✅ | `0.13.2` | seaborn |

**Missing packages**: `bertopic`
Install hint (CPU-only):
```
pip install bertopic
```

### SPECTER2 tokenizer reachability

✅ SPECTER2 tokenizer loaded successfully (HuggingFace reachable).

## B. Data Files

- ✅ `data\processed\integrated_corpus.parquet` (13.0 MB)
- ✅ `data\processed\integrated_corpus_partial2026.parquet` (0.6 MB)

## C. Main Corpus Schema (9,438 expected)

- Shape: **9,438 rows × 25 cols**
- Columns: `['record_id', 'source_db', 'source_id', 'doi', 'title', 'title_normalized', 'year', 'first_author_lastname', 'authors', 'journal', 'abstract', 'doc_type', 'language', 'cited_by', 'references_count', 'author_keywords', 'keywords_plus', 'mesh_terms', 'openalex_concepts', 'affiliations_raw', 'reprint_address', 'institutions_list', 'source_db_list', 'source_db_count', 'source_id_list']`

- Detected abstract column: `abstract`
- Detected title column:    `title`
- Detected year column:     `year`

## D. Coverage (title / abstract)

- Title:    9,438 / 9,438 = **100.0%**
- Abstract: 9,153 / 9,438 = **97.0%**
- Both title+abstract: 9,153 / 9,438 = **97.0%**

## E. Abstract Token Length (SPECTER2 max=512)

_(sampled 1,000 of 9,153 non-empty abstracts)_
- mean:   346
- median: 329
- p95:    561
- p99:    718
- max:    4049
- **>512 tokens (will need truncation): 73/1000 = 7.3%**

## F. Abstract Coverage by Year

| Year | n records | with abstract | coverage |
|---|---|---|---|
| 2005 | 261 | 220 | 84.3% |
| 2006 | 262 | 240 | 91.6% |
| 2007 | 300 | 280 | 93.3% |
| 2008 | 277 | 251 | 90.6% |
| 2009 | 314 | 281 | 89.5% |
| 2010 | 340 | 325 | 95.6% |
| 2011 | 356 | 336 | 94.4% |
| 2012 | 423 | 412 | 97.4% |
| 2013 | 437 | 426 | 97.5% |
| 2014 | 501 | 487 | 97.2% |
| 2015 | 449 | 433 | 96.4% |
| 2016 | 453 | 442 | 97.6% |
| 2017 | 443 | 437 | 98.6% |
| 2018 | 467 | 456 | 97.6% |
| 2019 | 538 | 527 | 98.0% |
| 2020 | 550 | 547 | 99.5% |
| 2021 | 611 | 608 | 99.5% |
| 2022 | 591 | 586 | 99.2% |
| 2023 | 471 | 469 | 99.6% |
| 2024 | 632 | 632 | 100.0% |
| 2025 | 737 | 733 | 99.5% |
| 2026 | 25 | 25 | 100.0% |

## G. Partial 2026 Status

- Shape: 316 rows
- Abstract coverage: 314/316 = 99.4%
- **Decision**: excluded from primary topic modeling (per Donthu 2021 / Yao 2025 complete-year cutoff convention)

## H. Recommendations for Block 1

- Abstract coverage **97.0%** is acceptable. Proceed with `title [SEP] abstract` for records with both; use title-only fallback for the rest.
- For records with token>512, use **head+tail truncation** (first 384 + last 128 tokens) — preserves intro context + conclusions, standard for long scientific abstracts.
- Embedding output target: `data/processed/specter2_embeddings.npy` (float32, ~28 MB for 9,438 docs × 768 dims).
