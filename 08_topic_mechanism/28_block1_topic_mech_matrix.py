"""Day 13 Block 1: Build Topic x Mechanism contingency matrix.

Inputs:
  - data/processed/cluster_assignments.parquet  (authoritative topic source)
  - data/processed/llm_extraction/primary_openai__gpt-4o-mini.interactions_normalized.parquet
  - data/processed/topic_labels.json

Outputs:
  - results/tables/table_topic_x_mechanism_matrix.csv          (labeled rows)
  - results/tables/table_topic_x_mechanism_matrix_numericId.csv (for downstream code)
  - results/tables/table_topic_x_mechanism_topic_marginals.csv
  - results/tables/table_topic_x_mechanism_mech_marginals.csv

Filters:
  - confidence >= 0.7  (already enforced in upstream LLM normalization)
  - drop cluster_id == -1 (HDBSCAN noise, ~36% of records)
  - drop mechanism in {"unspecified", "other"}  (~23% of interactions)
  - dedupe (record_id, mechanism) pairs  (one paper x mechanism counted once)
"""
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).parent.parent
P = REPO / "data" / "processed"
OUT = REPO / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1) Load
# ============================================================
clusters = pd.read_parquet(P / "cluster_assignments.parquet")
interactions = pd.read_parquet(
    P / "llm_extraction" / "primary_openai__gpt-4o-mini.interactions_normalized.parquet"
)
with open(P / "topic_labels.json", encoding="utf-8") as f:
    topic_labels = json.load(f)

print(f"[Load] clusters={clusters.shape}, interactions={interactions.shape}, topic_labels={len(topic_labels)}")

# ============================================================
# 2) Sanity check: interactions['cluster_id'] vs cluster_assignments
# ============================================================
sanity = interactions[["record_id", "cluster_id"]].drop_duplicates().merge(
    clusters[["record_id", "cluster_id"]],
    on="record_id", suffixes=("_int", "_clu")
)
mismatch = (sanity["cluster_id_int"] != sanity["cluster_id_clu"]).sum()
print(f"[Sanity] cluster_id mismatch (interactions vs cluster_assignments): {mismatch}")
assert mismatch == 0, f"cluster_id sources disagree on {mismatch} records -- investigate before proceeding"

# ============================================================
# 3) Build topic label lookup (top_keybert[:3] + n_docs)
# ============================================================
def make_label(cid_str):
    entry = topic_labels.get(cid_str, {})
    keybert = entry.get("top_keybert") or entry.get("top_ctfidf") or []
    label_terms = "; ".join(keybert[:3]) if keybert else "???"
    n_docs = entry.get("n_docs", "?")
    return f"#{cid_str} {label_terms} (n={n_docs})"

topic_label_map = {int(k): make_label(k) for k in topic_labels}

# ============================================================
# 4) Filter pipeline
# ============================================================
print(f"\n[Filter pipeline]")
print(f"  interactions total              : {len(interactions):,}")

NOISE_MECH = {"unspecified", "other"}
mech_clean = interactions[~interactions["mechanism"].isin(NOISE_MECH)].copy()
print(f"  after drop unspecified/other     : {len(mech_clean):,} ({len(mech_clean)/len(interactions)*100:.1f}% retained)")

# unique (record_id, mechanism) pair
rec_mech = mech_clean[["record_id", "mechanism"]].drop_duplicates()
print(f"  unique (record_id, mechanism)    : {len(rec_mech):,}")

# drop noise cluster
clusters_clean = clusters[clusters["cluster_id"] != -1][["record_id", "cluster_id"]]
print(f"  clusters (no noise -1)           : {len(clusters_clean):,} records")

# inner join
merged = rec_mech.merge(clusters_clean, on="record_id", how="inner")
print(f"  merged Topic x Mechanism rows    : {len(merged):,}")
print(f"  unique records in merged         : {merged['record_id'].nunique():,}")
print(f"  unique topics covered            : {merged['cluster_id'].nunique()} / 39")
print(f"  unique mechanisms covered        : {merged['mechanism'].nunique()} / 16")

# ============================================================
# 5) Build matrix (sorted: topics by n desc, mechanisms by n desc)
# ============================================================
matrix = (
    merged.groupby(["cluster_id", "mechanism"])
    .size().unstack(fill_value=0).astype(int)
)

topic_totals = matrix.sum(axis=1).sort_values(ascending=False)
mech_totals = matrix.sum(axis=0).sort_values(ascending=False)
matrix = matrix.loc[topic_totals.index, mech_totals.index]

print(f"\n[Matrix] {matrix.shape[0]} topics x {matrix.shape[1]} mechanisms")
print(f"  total cells           : {matrix.size}")
print(f"  non-zero cells        : {(matrix > 0).sum().sum()} ({(matrix > 0).sum().sum()/matrix.size*100:.1f}%)")
print(f"  total record-mech     : {topic_totals.sum():,}")
print(f"  max cell value        : {matrix.values.max()}")
print(f"  median nonzero cell   : {matrix.values[matrix.values > 0].astype(int).tolist() and int(pd.Series(matrix.values[matrix.values > 0]).median())}")

# ============================================================
# 6) Save (4 files)
# ============================================================
# 6a) labeled matrix
matrix_lab = matrix.copy()
matrix_lab.index = [topic_label_map.get(cid, f"#{cid}") for cid in matrix.index]
matrix_lab.index.name = "topic_label"
(OUT / "table_topic_x_mechanism_matrix.csv").write_text(
    matrix_lab.to_csv(), encoding="utf-8"
)

# 6b) numeric-id matrix (downstream code)
matrix.index.name = "cluster_id"
(OUT / "table_topic_x_mechanism_matrix_numericId.csv").write_text(
    matrix.to_csv(), encoding="utf-8"
)

# 6c) topic marginals
pd.DataFrame({
    "cluster_id": matrix.index,
    "topic_label": [topic_label_map.get(c, f"#{c}") for c in matrix.index],
    "n_records": topic_totals.values,
}).to_csv(OUT / "table_topic_x_mechanism_topic_marginals.csv", index=False, encoding="utf-8")

# 6d) mechanism marginals
pd.DataFrame({
    "mechanism": mech_totals.index,
    "n_records": mech_totals.values,
}).to_csv(OUT / "table_topic_x_mechanism_mech_marginals.csv", index=False, encoding="utf-8")

print(f"\n[Saved 4 files to results/tables/]")
for f in [
    "table_topic_x_mechanism_matrix.csv",
    "table_topic_x_mechanism_matrix_numericId.csv",
    "table_topic_x_mechanism_topic_marginals.csv",
    "table_topic_x_mechanism_mech_marginals.csv"
]:
    sz = (OUT / f).stat().st_size / 1024
    print(f"  {f:60s} {sz:6.1f} KB")

# ============================================================
# 7) Preview: top topics + mechanism marginals + heatmap snippet
# ============================================================
print("\n[Preview] Top 8 topics by total record-mechanism count:")
top_topics = pd.DataFrame({
    "cluster_id": topic_totals.head(8).index,
    "topic_label": [topic_label_map.get(c, "?")[:55] for c in topic_totals.head(8).index],
    "n": topic_totals.head(8).values,
})
print(top_topics.to_string(index=False))

print("\n[Preview] All 16 mechanism marginals:")
print(pd.DataFrame({
    "mechanism": mech_totals.index,
    "n_records": mech_totals.values,
}).to_string(index=False))

print("\n[Preview] Heatmap top-left corner (top 10 topics x top 8 mechanisms):")
preview = matrix.head(10).iloc[:, :8].copy()
preview.index = [f"#{c}" for c in preview.index]
with pd.option_context("display.max_columns", None, "display.width", 200):
    print(preview.to_string())