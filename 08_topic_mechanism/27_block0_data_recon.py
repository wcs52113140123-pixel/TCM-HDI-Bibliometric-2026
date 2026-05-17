"""Day 13 Block 0: data schema recon for Topic x Mechanism analysis."""
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).parent.parent
P = REPO / "data" / "processed"

def header(name):
    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

# ============================================================
# 1) cluster_assignments.parquet -- record_id x topic_id (39 cluster)
# ============================================================
header("1) cluster_assignments.parquet")
df = pd.read_parquet(P / "cluster_assignments.parquet")
print(f"shape: {df.shape}")
print(f"columns: {list(df.columns)}")
print(f"dtypes:\n{df.dtypes}\n")
print(f"head 3:\n{df.head(3).to_string()}\n")
# topic distribution
for col in df.columns:
    if df[col].dtype.kind in 'iu':
        n_uniq = df[col].nunique()
        print(f"  {col!r}: {n_uniq} unique values")
        if 5 < n_uniq < 100:
            vc = df[col].value_counts()
            print(f"    top 5: {dict(vc.head(5))}")
            print(f"    bottom 3: {dict(vc.tail(3))}")
            print(f"    contains -1 (HDBSCAN noise)? {(df[col] == -1).any()}")

# ============================================================
# 2) topic_labels.json
# ============================================================
header("2) topic_labels.json")
with open(P / "topic_labels.json", encoding="utf-8") as f:
    labels = json.load(f)
print(f"type: {type(labels).__name__}")
if isinstance(labels, dict):
    print(f"n_entries: {len(labels)}")
    keys = list(labels.keys())[:5]
    print(f"first 5 keys: {keys}")
    for k in keys[:3]:
        v = labels[k]
        if isinstance(v, dict):
            print(f"  [{k}]: dict with keys {list(v.keys())}")
            print(f"        sample: {dict(list(v.items())[:3])}")
        else:
            print(f"  [{k}]: {repr(v)[:200]}")
elif isinstance(labels, list):
    print(f"n_entries: {len(labels)}")
    print(f"first 3: {labels[:3]}")

# ============================================================
# 3) interactions_normalized.parquet -- record-level mechanism data
# ============================================================
header("3) primary_openai__gpt-4o-mini.interactions_normalized.parquet")
df_int = pd.read_parquet(P / "llm_extraction" / "primary_openai__gpt-4o-mini.interactions_normalized.parquet")
print(f"shape: {df_int.shape}")
print(f"columns: {list(df_int.columns)}")
print(f"dtypes:\n{df_int.dtypes}\n")
print(f"head 3:\n{df_int.head(3).to_string()}\n")

# mechanism column candidates
for c in ["mechanism", "mechanism_canonical", "mechanism_normalized", "mechanism_v3"]:
    if c in df_int.columns:
        print(f"\n  >>> '{c}' value_counts (full):")
        print(df_int[c].value_counts().to_string())
        break

# confidence
for c in ["confidence", "conf", "confidence_score"]:
    if c in df_int.columns:
        print(f"\n  >>> '{c}' describe:")
        print(df_int[c].describe().to_string())
        print(f"  >>> records with conf >= 0.7: {(df_int[c] >= 0.7).sum()} / {len(df_int)}")
        break

# record_id column candidates
for c in ["record_id", "doi", "id"]:
    if c in df_int.columns:
        print(f"\n  >>> '{c}' unique count: {df_int[c].nunique()}")
        break

# ============================================================
# 4) records.parquet -- record-level summary
# ============================================================
header("4) primary_openai__gpt-4o-mini.records.parquet")
df_rec = pd.read_parquet(P / "llm_extraction" / "primary_openai__gpt-4o-mini.records.parquet")
print(f"shape: {df_rec.shape}")
print(f"columns: {list(df_rec.columns)}")
print(f"head 2:\n{df_rec.head(2).to_string()}")

# ============================================================
# 5) Compatibility check: cluster_assignments record_id vs interactions record_id
# ============================================================
header("5) Compatibility -- record_id overlap")
ca_id_col = next((c for c in df.columns if c.lower() in ("record_id", "doi", "id")), None)
int_id_col = next((c for c in df_int.columns if c.lower() in ("record_id", "doi", "id")), None)

if ca_id_col and int_id_col:
    ca_ids = set(df[ca_id_col].astype(str))
    int_ids = set(df_int[int_id_col].astype(str))
    overlap = ca_ids & int_ids
    print(f"  cluster_assignments['{ca_id_col}'] unique: {len(ca_ids):,}")
    print(f"  interactions['{int_id_col}']      unique: {len(int_ids):,}")
    print(f"  overlap                           : {len(overlap):,}")
    print(f"  cluster-only (no mechanism)       : {len(ca_ids - int_ids):,}")
    print(f"  mechanism-only (no cluster)       : {len(int_ids - ca_ids):,}")