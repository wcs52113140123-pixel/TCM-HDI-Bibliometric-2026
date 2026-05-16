"""
Day 5 Block 2: UMAP dimensionality reduction + HDBSCAN clustering.

Pipeline:
  768-dim SPECTER2 → UMAP 5-dim (for HDBSCAN density estimation)
                  ↘ UMAP 2-dim (for scatter visualization, separate fit)
  HDBSCAN on 5-dim with min_cluster_size=50, min_samples=10

Citations:
  - McInnes et al. 2018. UMAP: Uniform Manifold Approximation and Projection
    for Dimension Reduction. arXiv:1802.03426
  - Campello et al. 2013. Density-Based Clustering Based on Hierarchical
    Density Estimates. PAKDD.
  - Grootendorst 2022. BERTopic: Neural topic modeling with a class-based
    TF-IDF procedure. arXiv:2203.05794
  - Klarin 2024 (heuristic for min_cluster_size ≈ sqrt(N)/2)

Inputs:
  data/processed/specter2_embeddings.npy
  data/processed/specter2_embeddings_meta.json
  data/processed/integrated_corpus.parquet

Outputs:
  data/processed/umap_5d.npy                 # (9413, 5) for HDBSCAN
  data/processed/umap_2d.npy                 # (9413, 2) for viz
  data/processed/cluster_assignments.parquet # record_id, cluster_id, prob, outlier
  results/tables/cluster_stats.csv           # per-cluster size / quality

Run:
  python 04_keyword_topic/08_block2_umap_hdbscan.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import umap
import hdbscan

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
TABLES = REPO / "results" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

EMB_PATH = DATA / "specter2_embeddings.npy"
META_PATH = DATA / "specter2_embeddings_meta.json"
CORPUS_PATH = DATA / "integrated_corpus.parquet"

OUT_5D = DATA / "umap_5d.npy"
OUT_2D = DATA / "umap_2d.npy"
OUT_CLUSTERS = DATA / "cluster_assignments.parquet"
OUT_STATS = TABLES / "cluster_stats.csv"

# Hyperparameters (locked from prior decision)
UMAP_HDBSCAN_PARAMS = dict(
    n_neighbors=15,
    min_dist=0.0,
    n_components=5,
    metric="cosine",
    random_state=42,
)
UMAP_VIZ_PARAMS = dict(
    n_neighbors=15,
    min_dist=0.1,
    n_components=2,
    metric="cosine",
    random_state=42,
)
HDBSCAN_PARAMS = dict(
    min_cluster_size=50,
    min_samples=5,
    metric="euclidean",
    cluster_selection_method="eom",
    cluster_selection_epsilon=0.15,
    prediction_data=True,
)


def main():
    t0 = time.time()

    # --- Load -------------------------------------------------------------
    print(f"[{time.strftime('%H:%M:%S')}] Loading inputs...")
    embeddings = np.load(EMB_PATH)
    with open(META_PATH, encoding="utf-8") as f:
        meta = json.load(f)
    record_ids = meta["record_ids"]
    df = pd.read_parquet(CORPUS_PATH)

    assert embeddings.shape == (9413, 768), \
        f"Expected (9413, 768), got {embeddings.shape}"
    assert len(record_ids) == 9413
    assert len(df) == 9413
    # Verify alignment (defensive)
    assert df["record_id"].tolist() == record_ids or \
        set(df["record_id"]) == set(record_ids), \
        "record_id order mismatch between corpus and embedding meta"
    print(f"  Embeddings: {embeddings.shape} {embeddings.dtype}")
    print(f"  Norm: mean={np.linalg.norm(embeddings, axis=1).mean():.3f}")

    # --- UMAP 5-dim for HDBSCAN ------------------------------------------
    t1 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] UMAP → 5-dim for HDBSCAN "
          f"(metric=cosine, min_dist=0.0)...")
    reducer_5d = umap.UMAP(**UMAP_HDBSCAN_PARAMS, verbose=False)
    umap_5d = reducer_5d.fit_transform(embeddings).astype(np.float32)
    np.save(OUT_5D, umap_5d)
    print(f"  Done in {time.time()-t1:.1f}s → {OUT_5D.name} {umap_5d.shape}")

    # --- UMAP 2-dim for visualization ------------------------------------
    t2 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] UMAP → 2-dim for viz "
          f"(metric=cosine, min_dist=0.1)...")
    reducer_2d = umap.UMAP(**UMAP_VIZ_PARAMS, verbose=False)
    umap_2d = reducer_2d.fit_transform(embeddings).astype(np.float32)
    np.save(OUT_2D, umap_2d)
    print(f"  Done in {time.time()-t2:.1f}s → {OUT_2D.name} {umap_2d.shape}")

    # --- HDBSCAN ----------------------------------------------------------
    t3 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] HDBSCAN "
          f"(min_cluster_size={HDBSCAN_PARAMS['min_cluster_size']}, "
          f"min_samples={HDBSCAN_PARAMS['min_samples']})...")
    clusterer = hdbscan.HDBSCAN(**HDBSCAN_PARAMS)
    labels = clusterer.fit_predict(umap_5d)
    probs = clusterer.probabilities_
    outlier_scores = clusterer.outlier_scores_
    print(f"  Done in {time.time()-t3:.1f}s")

    # --- Stats ------------------------------------------------------------
    unique, counts = np.unique(labels, return_counts=True)
    n_clusters = int((unique >= 0).sum())
    n_noise = int((labels == -1).sum())
    valid_mask = unique >= 0
    sizes = counts[valid_mask]
    print(f"\n  Clusters: {n_clusters}")
    print(f"  Noise:    {n_noise} ({n_noise/len(labels)*100:.1f}%)")
    if n_clusters > 0:
        print(f"  Cluster sizes: min={sizes.min()}, median={int(np.median(sizes))}, "
              f"max={sizes.max()}, mean={sizes.mean():.1f}")

    # --- Save assignments -------------------------------------------------
    assignments = pd.DataFrame({
        "record_id": record_ids,
        "cluster_id": labels.astype(int),
        "probability": probs.astype(np.float32),
        "outlier_score": outlier_scores.astype(np.float32),
    })
    assignments.to_parquet(OUT_CLUSTERS, index=False)
    print(f"  → {OUT_CLUSTERS.name}")

    # --- Cluster stats CSV ------------------------------------------------
    stats = []
    for cid, n in zip(unique, counts):
        mask = labels == cid
        stats.append({
            "cluster_id": int(cid),
            "n_docs": int(n),
            "pct_corpus": round(n / len(labels) * 100, 2),
            "mean_probability": round(float(probs[mask].mean()), 3),
            "mean_outlier_score": round(float(outlier_scores[mask].mean()), 3),
        })
    stats_df = pd.DataFrame(stats).sort_values(
        "cluster_id", key=lambda s: s.map(lambda x: (x == -1, -x if x < 0 else x))
    )
    stats_df.to_csv(OUT_STATS, index=False)
    print(f"  → {OUT_STATS.name}")

    # Display
    print(f"\nCluster distribution (top 15 + noise):")
    show = stats_df.sort_values("n_docs", ascending=False).head(16)
    print(show.to_string(index=False))

    print(f"\n[{time.strftime('%H:%M:%S')}] Block 2 complete. "
          f"Total elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
