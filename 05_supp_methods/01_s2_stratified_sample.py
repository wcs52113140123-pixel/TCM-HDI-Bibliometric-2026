"""
Day 25 Block A: Supp Methods S2 - Stratified sampling for LLM extraction validation

Outputs (to results/supp_methods_s2/):
  - s2_annotator_form.xlsx     : 50 records, BLIND to LLM labels (for shimei)
  - s2_master_keyed.xlsx       : 50 records, with LLM labels (for kappa compute later)
  - s2_sampling_log.json       : reproducibility metadata (seed, filters, category counts)

Design:
  - Stratified by LLM mechanism_category, target 3 per category x ~16 = ~48
  - Random fill to 50 total
  - Filters: confidence >= 0.7, exclude catch-all (unspecified/other)
  - SEED = 20260525 (Day 25 reproducible)
  - Sample shuffled so shimei does not see categories clustered
"""

import pandas as pd
import json
import random
from pathlib import Path

REPO = Path(r"D:\Document\Research-Projects\TCM-HDI-Bibliometric-2026")
OUT_DIR = REPO / "results" / "supp_methods_s2"
OUT_DIR.mkdir(exist_ok=True, parents=True)

SEED = 20260525
TARGET_PER_CAT = 3
TOTAL_N = 50
CATCH_ALL = ['unspecified', 'other', 'unknown', 'not_specified', 'none']

# ---- Load LLM extraction ----
llm_path = REPO / "data" / "processed" / "llm_extraction" / "primary_openai__gpt-4o-mini.interactions_normalized.parquet"
print(f"Loading: {llm_path.name}")
df_llm = pd.read_parquet(llm_path)
print(f"  Shape: {df_llm.shape}")
print(f"  Columns: {df_llm.columns.tolist()}")

# Auto-detect column names
def find_col(df, candidates):
    return next((c for c in candidates if c in df.columns), None)

mech_col = find_col(df_llm, ['mechanism_category', 'mechanism', 'category', 'label', 'mechanism_type'])
conf_col = find_col(df_llm, ['confidence', 'conf', 'llm_confidence', 'score'])
pid_col  = find_col(df_llm, ['paper_id', 'doi', 'pmid', 'record_id', 'paper_uid', 'id'])

print(f"\nAuto-detected columns:")
print(f"  mechanism: {mech_col}")
print(f"  confidence: {conf_col}")
print(f"  paper_id: {pid_col}")

if not mech_col or not pid_col:
    raise SystemExit(f"\n[ERROR] Required columns missing. Available: {df_llm.columns.tolist()}")

print(f"\nMechanism distribution (Top 20):")
print(df_llm[mech_col].value_counts().head(20).to_string())

# ---- Filter ----
df_clean = df_llm.copy()
if conf_col:
    df_clean = df_clean[df_clean[conf_col] >= 0.7]
df_clean = df_clean[~df_clean[mech_col].str.lower().isin(CATCH_ALL)]
print(f"\nAfter filter (conf>=0.7, no catch-all): {len(df_clean)} records, {df_clean[mech_col].nunique()} unique categories")

# ---- Stratified sample ----
random.seed(SEED)
samples = []
for cat, cat_df in df_clean.groupby(mech_col):
    n = min(TARGET_PER_CAT, len(cat_df))
    samples.append(cat_df.sample(n=n, random_state=SEED))

sample_df = pd.concat(samples).reset_index(drop=True)
remaining = TOTAL_N - len(sample_df)
if remaining > 0:
    extra_pool = df_clean[~df_clean.index.isin(sample_df.index)]
    if len(extra_pool) >= remaining:
        extra = extra_pool.sample(n=remaining, random_state=SEED)
        sample_df = pd.concat([sample_df, extra]).reset_index(drop=True)
elif remaining < 0:
    sample_df = sample_df.sample(n=TOTAL_N, random_state=SEED).reset_index(drop=True)

sample_df = sample_df.sample(frac=1, random_state=SEED).reset_index(drop=True)
sample_df['annotator_record_id'] = [f'S2-{i+1:03d}' for i in range(len(sample_df))]

print(f"\nFinal sample: {len(sample_df)} records")
print(f"Sample category distribution:")
print(sample_df[mech_col].value_counts().to_string())

# ---- Join with corpus to get title/abstract ----
corpus_candidates = [
    REPO / "data" / "processed" / "corpus_main_2005_2025.parquet",
    REPO / "data" / "processed" / "corpus_integrated.parquet",
    REPO / "data" / "processed" / "cluster_assignments.parquet",
    REPO / "data" / "processed" / "openalex_dedup_main.parquet",
]
corpus_df = None
for cpath in corpus_candidates:
    if cpath.exists():
        corpus_df = pd.read_parquet(cpath)
        print(f"\nLoaded corpus: {cpath.name} (shape {corpus_df.shape})")
        print(f"  Columns: {corpus_df.columns.tolist()}")
        break

if corpus_df is None:
    print("\n[WARN] No corpus master parquet found. Annotator form will lack title/abstract.")
    print("  Searched: " + ", ".join(c.name for c in corpus_candidates))
    annotator_form = sample_df[['annotator_record_id', pid_col]].copy()
else:
    title_col = find_col(corpus_df, ['title', 'paper_title', 'article_title'])
    abs_col   = find_col(corpus_df, ['abstract', 'paper_abstract'])
    year_col  = find_col(corpus_df, ['year', 'publication_year', 'pub_year'])
    join_col  = pid_col if pid_col in corpus_df.columns else find_col(corpus_df, ['paper_id', 'doi', 'pmid', 'record_id'])
    
    print(f"\nCorpus columns used: title='{title_col}', abstract='{abs_col}', year='{year_col}', join='{join_col}'")
    
    if join_col:
        cols_to_merge = [join_col] + [c for c in [title_col, abs_col, year_col] if c]
        merged = sample_df.merge(corpus_df[cols_to_merge].drop_duplicates(subset=[join_col]),
                                  left_on=pid_col, right_on=join_col, how='left')
        keep = ['annotator_record_id', pid_col]
        if year_col: keep.append(year_col)
        if title_col: keep.append(title_col)
        if abs_col: keep.append(abs_col)
        annotator_form = merged[keep].copy()
        n_with_abstract = annotator_form[abs_col].notna().sum() if abs_col else 0
        print(f"  Merged successfully: {n_with_abstract}/{len(annotator_form)} records have abstract")
    else:
        print("[WARN] No join column found in corpus. Annotator form lacks title/abstract.")
        annotator_form = sample_df[['annotator_record_id', pid_col]].copy()

# ---- Add blank columns for shimei ----
annotator_form['your_mechanism_label'] = ''
annotator_form['your_alternative_label_optional'] = ''
annotator_form['your_confidence_low_med_high'] = ''
annotator_form['your_notes_optional'] = ''

# ---- Output 1: Blind annotator form ----
form_path = OUT_DIR / "s2_annotator_form.xlsx"
annotator_form.to_excel(form_path, index=False)
print(f"\n[+] {form_path.name}: {len(annotator_form)} rows")

# ---- Output 2: Master keyed file ----
master_keyed = annotator_form.copy()
master_keyed['llm_mechanism_label'] = sample_df[mech_col].values
if conf_col:
    master_keyed['llm_confidence'] = sample_df[conf_col].values
master_path = OUT_DIR / "s2_master_keyed.xlsx"
master_keyed.to_excel(master_path, index=False)
print(f"[+] {master_path.name}: {len(master_keyed)} rows (with LLM ground-truth for kappa)")

# ---- Output 3: Sampling log ----
log = {
    "day": 25,
    "date": "2026-05-25",
    "seed": SEED,
    "total_sampled": int(len(sample_df)),
    "target_per_category": TARGET_PER_CAT,
    "categories_in_sample": {str(k): int(v) for k, v in sample_df[mech_col].value_counts().to_dict().items()},
    "filters_applied": {
        "confidence_min": 0.7 if conf_col else None,
        "excluded_categories": CATCH_ALL,
    },
    "columns_detected": {
        "llm_mechanism_col": mech_col,
        "llm_confidence_col": conf_col,
        "paper_id_col": pid_col,
    },
    "files_produced": [form_path.name, master_path.name],
}
log_path = OUT_DIR / "s2_sampling_log.json"
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(log, f, indent=2, ensure_ascii=False, default=str)
print(f"[+] {log_path.name}")

print(f"\nOutput directory: {OUT_DIR}")
print(f"\nDone. Files for shimei: send {form_path.name} (BLIND). Keep {master_path.name} private.")