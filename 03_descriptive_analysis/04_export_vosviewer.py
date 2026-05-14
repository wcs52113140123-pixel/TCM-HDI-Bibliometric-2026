"""
Block 2C: Export VOSviewer-compatible files for country collaboration network.

VOSviewer accepts two-file format:
- map.txt:     node attributes (id, label, weight, cluster)
- network.txt: edges (id1, id2, strength)

Strategy:
- Include countries with >= 10 publications (avoids long tail noise)
- Include collaboration edges with >= 3 co-publications (avoids weak edges)
- Pre-assign cluster IDs based on region (will be overridden by VOSviewer's
  modularity clustering, but provides initial layout hint)

Run:
    python 03_descriptive_analysis/04_export_vosviewer.py
"""

from pathlib import Path
import pandas as pd

# Region -> cluster id (for initial coloring; VOSviewer will recompute)
REGION_TO_CLUSTER = {
    "China (mainland & regions)": 1,
    "Asia (other)": 2,
    "North America": 3,
    "Europe": 4,
    "Oceania": 5,
    "Middle East": 6,
    "Africa": 7,
    "Latin America": 8,
    "Other": 9,
}


def main():
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "results" / "vosviewer"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Block 2C: Export VOSviewer files for country collaboration network")
    print("=" * 70)
    
    # Load country ranking + collaboration pairs
    print("\n[1] Loading data...")
    rank_df = pd.read_csv(repo_root / "results/tables/table_02_country_ranking.csv")
    pair_df = pd.read_parquet(repo_root / "data/processed/country_collaboration_pairs.parquet")
    
    print(f"    Countries:               {len(rank_df):,}")
    print(f"    Collaboration pairs:     {len(pair_df):,}")
    
    # Filter: nodes with >= 10 publications, edges with >= 3 co-publications
    MIN_PUBS = 10
    MIN_COLLAB = 3
    
    nodes_df = rank_df[rank_df["n_publications"] >= MIN_PUBS].copy()
    edges_df = pair_df[pair_df["co_publications"] >= MIN_COLLAB].copy()
    
    # Restrict edges to only include nodes in the filtered set
    node_set = set(nodes_df["country_code"])
    edges_df = edges_df[
        edges_df["country_a"].isin(node_set) & edges_df["country_b"].isin(node_set)
    ].copy()
    
    print(f"\n[2] After filtering (nodes>={MIN_PUBS} pubs, edges>={MIN_COLLAB} co-pubs):")
    print(f"    Nodes kept: {len(nodes_df):,}")
    print(f"    Edges kept: {len(edges_df):,}")
    
    # Assign integer IDs (1-indexed for VOSviewer)
    nodes_df = nodes_df.reset_index(drop=True)
    nodes_df["vos_id"] = nodes_df.index + 1
    cc_to_id = dict(zip(nodes_df["country_code"], nodes_df["vos_id"]))
    
    nodes_df["cluster"] = nodes_df["region"].map(REGION_TO_CLUSTER).fillna(9).astype(int)
    
    # ============ Write map file ============
    # VOSviewer map.txt format (tab-separated):
    # idlabelweight<Documents>cluster
    print("\n[3] Writing VOSviewer map.txt...")
    map_path = out_dir / "country_collab_map.txt"
    with open(map_path, "w", encoding="utf-8") as fp:
        # Header
        fp.write("id\tlabel\tweight<Documents>\tweight<Citations>\tcluster\n")
        # Rows
        for _, row in nodes_df.iterrows():
            fp.write(
                f"{int(row['vos_id'])}\t"
                f"{row['country_name']}\t"
                f"{int(row['n_publications'])}\t"
                f"{int(row['n_total_citations'])}\t"
                f"{int(row['cluster'])}\n"
            )
    print(f"    {map_path}  ({len(nodes_df):,} nodes)")
    
    # ============ Write network file ============
    # VOSviewer network.txt format (tab-separated, no header):
    # id1id2strength
    print("\n[4] Writing VOSviewer network.txt...")
    net_path = out_dir / "country_collab_network.txt"
    edges_df["id_a"] = edges_df["country_a"].map(cc_to_id)
    edges_df["id_b"] = edges_df["country_b"].map(cc_to_id)
    with open(net_path, "w", encoding="utf-8") as fp:
        for _, row in edges_df.iterrows():
            fp.write(f"{int(row['id_a'])}\t{int(row['id_b'])}\t{int(row['co_publications'])}\n")
    print(f"    {net_path}  ({len(edges_df):,} edges)")
    
    # ============ Preview ============
    print(f"\n[5] Node preview (top 10 by publications):")
    print(f"    {'ID':>3} {'Country':<25s} {'N_Pub':>6s} {'Citations':>10s} {'Cluster':>8s}")
    for _, row in nodes_df.head(10).iterrows():
        print(f"    {int(row['vos_id']):>3} {row['country_name']:<25s} "
              f"{int(row['n_publications']):>6,} {int(row['n_total_citations']):>10,} "
              f"{int(row['cluster']):>8}")
    
    print(f"\n[6] Edge preview (top 10 by strength):")
    edges_sorted = edges_df.sort_values("co_publications", ascending=False).head(10)
    id_to_name = dict(zip(nodes_df["vos_id"], nodes_df["country_name"]))
    for _, row in edges_sorted.iterrows():
        n_a = id_to_name[row["id_a"]]
        n_b = id_to_name[row["id_b"]]
        print(f"    {n_a:>25s} <-> {n_b:<25s}  {int(row['co_publications']):>5,}")
    
    print("\n" + "=" * 70)
    print("VOSviewer files ready!")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"  1. Open VOSviewer")
    print(f"  2. File -> Create -> Read data from VOSviewer files")
    print(f"  3. Map file:     {map_path}")
    print(f"  4. Network file: {net_path}")
    print(f"  5. (follow detailed instructions for layout/clustering settings)")


if __name__ == "__main__":
    main()
