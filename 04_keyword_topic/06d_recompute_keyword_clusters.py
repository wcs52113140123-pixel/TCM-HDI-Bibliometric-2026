"""
Day 5 Block 5 prep: Re-derive Day-4 keyword clusters from co-occurrence graph
using Louvain community detection.

Why this exists:
  Day 4's VOSviewer .map file was exported WITHOUT cluster information
  (a common VOSviewer UX pitfall — "Save with cluster information" checkbox
  was not selected). Day-4 script printed VOSviewer GUI clustering instructions
  (resolution=0.80, min_cluster_size=5) but did NOT persist the cluster column
  to disk. Block 5 cross-validation requires a keyword → cluster mapping; we
  re-derive it from the same co-occurrence graph that VOSviewer used, applying
  the same parameters.

  NetworkX Louvain (Blondel et al. 2008) and VOSviewer Smart Local Moving
  (Waltman & van Eck 2013) are closely related modularity-maximizing algorithms.
  Empirical cluster membership agreement is typically > 85% on the same graph
  with matched resolution.

Citations:
  - Blondel et al. 2008. Fast unfolding of communities in large networks. JSM.
  - Waltman & van Eck 2013. A smart local moving algorithm for large-scale
    modularity-based community detection. Eur Phys J B.

Inputs:
  data/processed/keyword_cooccurrence_pairs.parquet

Outputs:
  data/processed/keyword_cluster_day4_louvain.csv  # keyword, day4_cluster
  results/audits/keyword_cluster_day4_louvain_audit.md  # human verification

Prerequisite:
  pip install python-louvain

Run:
  python 04_keyword_topic/06d_recompute_keyword_clusters.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import networkx as nx
import pandas as pd

try:
    import community as community_louvain  # python-louvain package
except ImportError:
    print("FATAL: python-louvain not installed.")
    print("Install: pip install python-louvain")
    sys.exit(1)

REPO = Path(__file__).resolve().parents[1]
COOC_PATH = REPO / "data" / "processed" / "keyword_cooccurrence_pairs.parquet"
MAP_PATH = REPO / "results" / "vosviewer" / "keyword_cooccur_map.txt"

OUT_CSV = REPO / "data" / "processed" / "keyword_cluster_day4_louvain.csv"
OUT_AUDIT = REPO / "results" / "audits" / "keyword_cluster_day4_louvain_audit.md"

# Day 4 parameters (locked in master_progress)
RESOLUTION = 0.80
MIN_CLUSTER_SIZE = 5
RANDOM_STATE = 42


def detect_pair_columns(df: pd.DataFrame) -> tuple[str, str, str]:
    """Auto-detect (source, target, weight) columns in cooccurrence pairs df.
    Uses substring matching for weight to handle names like 'n_cooccur', 'cooccur_n'."""
    cols = list(df.columns)
    cols_lower = {c.lower(): c for c in cols}

    # Exact-match candidates for source / target (these names are usually clean)
    src_candidates = ["kw1", "keyword1", "source", "from", "src", "node1", "term1"]
    tgt_candidates = ["kw2", "keyword2", "target", "to", "dst", "node2", "term2"]
    src_col = next((cols_lower[c] for c in src_candidates if c in cols_lower), None)
    tgt_col = next((cols_lower[c] for c in tgt_candidates if c in cols_lower), None)

    # Substring-match for weight (handles 'n_cooccur', 'cooccur_count', 'weight_n', etc.)
    w_substrings = ["weight", "cooccur", "occur", "count", "freq", "strength"]
    w_col = None
    for c in cols:
        cl = c.lower()
        if any(sub in cl for sub in w_substrings):
            w_col = c
            break

    return src_col, tgt_col, w_col


def main():
    # --- Load co-occurrence pairs ---
    print(f"Loading {COOC_PATH.name}...")
    df = pd.read_parquet(COOC_PATH)
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Dtypes: {df.dtypes.to_dict()}")

    src_col, tgt_col, w_col = detect_pair_columns(df)
    print(f"  Detected: source='{src_col}', target='{tgt_col}', weight='{w_col}'")

    if src_col is None or tgt_col is None:
        print("\nFATAL: Could not auto-detect source/target columns.")
        print("Please tell me the actual column names; I'll patch the detector.")
        print(f"  First 3 rows:\n{df.head(3)}")
        sys.exit(1)

    if w_col is None:
        print("  WARNING: No weight column found; using uniform weight=1.")

    # --- If sources are integers (VOSviewer IDs), convert to labels ---
    sample_src = df[src_col].iloc[0]
    if isinstance(sample_src, (int, float)) or (
        isinstance(sample_src, str) and sample_src.isdigit()
    ):
        print(f"  Source values look like IDs; loading id→label map...")
        if not MAP_PATH.exists():
            print(f"FATAL: ID-keyed pairs require {MAP_PATH.name}; not found.")
            sys.exit(1)
        map_df = pd.read_csv(MAP_PATH, sep="\t")
        id_to_label = dict(zip(map_df["id"].astype(int), map_df["label"]))
        df[src_col] = df[src_col].astype(int).map(id_to_label)
        df[tgt_col] = df[tgt_col].astype(int).map(id_to_label)
        # Drop pairs where mapping failed (shouldn't happen if data is consistent)
        before = len(df)
        df = df.dropna(subset=[src_col, tgt_col])
        if len(df) < before:
            print(f"  Dropped {before - len(df)} pairs with unmapped IDs")

    # --- Build weighted graph ---
    print(f"\nBuilding co-occurrence graph...")
    G = nx.Graph()
    for _, r in df.iterrows():
        u = str(r[src_col]).strip().lower()
        v = str(r[tgt_col]).strip().lower()
        if u == v or not u or not v:
            continue
        w = float(r[w_col]) if w_col else 1.0
        if G.has_edge(u, v):
            G[u][v]["weight"] += w
        else:
            G.add_edge(u, v, weight=w)
    print(f"  Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print(f"  Total edge weight: {sum(d['weight'] for _,_,d in G.edges(data=True)):,.0f}")

    # --- Louvain community detection ---
    print(f"\nRunning Louvain (resolution={RESOLUTION}, seed={RANDOM_STATE})...")
    partition = community_louvain.best_partition(
        G, weight="weight", resolution=RESOLUTION, random_state=RANDOM_STATE
    )
    modularity = community_louvain.modularity(partition, G, weight="weight")
    print(f"  Modularity: {modularity:.4f}")
    raw_sizes = Counter(partition.values())
    print(f"  Raw clusters: {len(raw_sizes)} "
          f"(sizes: {sorted(raw_sizes.values(), reverse=True)})")

    # --- Filter by min_cluster_size, renumber 0..K-1 by size desc ---
    valid_clusters = {c for c, n in raw_sizes.items() if n >= MIN_CLUSTER_SIZE}
    sorted_valid = sorted(valid_clusters, key=lambda c: -raw_sizes[c])
    renumber = {old: new for new, old in enumerate(sorted_valid)}

    rows = []
    for kw, c in partition.items():
        if c in valid_clusters:
            rows.append({"keyword": kw, "day4_cluster": renumber[c]})
    out_df = pd.DataFrame(rows).sort_values(["day4_cluster", "keyword"])
    out_df.to_csv(OUT_CSV, index=False)
    print(f"\n→ {OUT_CSV.relative_to(REPO)}")
    print(f"  Final clusters (≥{MIN_CLUSTER_SIZE} keywords): "
          f"{out_df['day4_cluster'].nunique()}")
    print(f"  Total keywords clustered: {len(out_df)}")
    print(f"  Keywords dropped (cluster < {MIN_CLUSTER_SIZE}): "
          f"{sum(n for c,n in raw_sizes.items() if c not in valid_clusters)}")

    # --- Human-verification audit ---
    OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# Day-4 Keyword Cluster Re-derivation (Louvain)\n")
    lines.append(f"- Algorithm: NetworkX + python-louvain (Blondel et al. 2008)")
    lines.append(f"- Parameters: resolution={RESOLUTION}, "
                 f"min_cluster_size={MIN_CLUSTER_SIZE}, seed={RANDOM_STATE}")
    lines.append(f"- Graph: {G.number_of_nodes():,} nodes, "
                 f"{G.number_of_edges():,} edges")
    lines.append(f"- Modularity: {modularity:.4f}")
    lines.append(f"- Final clusters: {out_df['day4_cluster'].nunique()}\n")

    lines.append("## Verification: top keywords per cluster\n")
    lines.append("**Action required**: compare these against Day-4 published "
                 "5-cluster labels (ADME core / TCM oncology / CAM clinical "
                 "safety / in silico mechanisms / classic herb-drug pairs).\n")

    # For each cluster, top keywords by weighted degree (within-cluster strength)
    for cid in sorted(out_df["day4_cluster"].unique()):
        kws = out_df.loc[out_df["day4_cluster"] == cid, "keyword"].tolist()
        # Compute weighted degree within this cluster
        sub = G.subgraph(kws)
        strengths = {
            k: sum(d["weight"] for _, _, d in sub.edges(k, data=True))
            for k in sub.nodes()
        }
        top = sorted(strengths.items(), key=lambda x: -x[1])[:15]
        lines.append(f"### Cluster {cid} (n={len(kws)} keywords)\n")
        lines.append("Top 15 by within-cluster weighted degree:")
        for k, s in top:
            lines.append(f"- `{k}` (strength={s:.0f})")
        lines.append("")

    OUT_AUDIT.write_text("\n".join(lines), encoding="utf-8")
    print(f"→ {OUT_AUDIT.relative_to(REPO)}")
    print(f"\n👉 Open the audit file and compare top keywords per cluster")
    print(f"   with Day-4 published cluster labels for sanity check.")


if __name__ == "__main__":
    main()
