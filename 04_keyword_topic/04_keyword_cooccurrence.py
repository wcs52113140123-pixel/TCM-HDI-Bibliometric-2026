"""
Day 4 Block 4: Keyword co-occurrence network for VOSviewer.

Builds co-occurrence matrix for Top 100 keywords and exports VOSviewer-compatible
input files (network + map).

Co-occurrence definition:
- Two keywords co-occur if they appear in the same record.
- Edge weight = number of records where both appear.

Output:
- results/vosviewer/keyword_cooccur_map.txt
- results/vosviewer/keyword_cooccur_network.txt
- data/processed/keyword_cooccurrence_pairs.parquet (for diagnostics)
- results/tables/table_06b_top_keyword_cooccur_pairs.csv
"""

from pathlib import Path
from collections import Counter
from itertools import combinations

import pandas as pd


# Number of top keywords to include in co-occurrence (typical: 50-150)
N_TOP = 100

# Minimum co-occurrence count to include edge (VOSviewer recommendation)
MIN_COOC = 5


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 4: Keyword co-occurrence network")
    print("=" * 70)
    
    # Load
    print("\n[1] Loading data...")
    km = pd.read_parquet(repo_root / "data/processed/keyword_record_map.parquet")
    lookup = pd.read_parquet(repo_root / "data/processed/keyword_lookup.parquet")
    print(f"    Records with keywords: {km['record_id'].nunique():,}")
    print(f"    Total (record, kw) pairs: {len(km):,}")
    
    # Filter to Top N keywords
    print(f"\n[2] Filtering to Top {N_TOP} keywords...")
    top_kws = set(lookup.head(N_TOP)["keyword"].tolist())
    km_top = km[km["keyword"].isin(top_kws)].copy()
    print(f"    Filtered pairs: {len(km_top):,}")
    print(f"    Records with at least 2 top-kws: ", end="")
    
    # Group by record_id to get keyword sets
    record_kws = km_top.groupby("record_id")["keyword"].apply(set)
    record_kws_multi = record_kws[record_kws.apply(len) >= 2]
    print(f"{len(record_kws_multi):,}")
    
    # ============ Build co-occurrence pairs ============
    print(f"\n[3] Computing co-occurrence pairs...")
    cooc_counter = Counter()
    
    for kws in record_kws_multi:
        kw_list = sorted(kws)
        for kw1, kw2 in combinations(kw_list, 2):
            cooc_counter[(kw1, kw2)] += 1
    
    print(f"    Raw co-occurrence pairs: {len(cooc_counter):,}")
    
    # Filter weak edges (min count)
    cooc_filtered = {pair: w for pair, w in cooc_counter.items() if w >= MIN_COOC}
    print(f"    After filter (min={MIN_COOC}): {len(cooc_filtered):,}")
    
    # Save as DataFrame
    cooc_rows = [
        {"keyword1": pair[0], "keyword2": pair[1], "n_cooccur": w}
        for pair, w in cooc_filtered.items()
    ]
    cooc_df = pd.DataFrame(cooc_rows).sort_values("n_cooccur", ascending=False).reset_index(drop=True)
    
    cooc_path = repo_root / "data/processed/keyword_cooccurrence_pairs.parquet"
    cooc_df.to_parquet(cooc_path, index=False, engine="pyarrow")
    print(f"    Saved: {cooc_path}")
    
    # Top 20 pairs table
    print(f"\n[4] Top 20 co-occurring keyword pairs:")
    print(f"    {'Rank':<5} {'N':>5}  Keyword 1                                  + Keyword 2")
    for i, row in cooc_df.head(20).iterrows():
        n = int(row["n_cooccur"])
        k1 = row["keyword1"][:40]
        k2 = row["keyword2"][:40]
        print(f"    {i+1:<5} {n:>5}  {k1:<42s}  + {k2}")
    
    # Save table
    out_tables = repo_root / "results" / "tables"
    cooc_df.head(50).to_csv(
        out_tables / "table_06b_top_keyword_cooccur_pairs.csv",
        index=False, encoding="utf-8"
    )
    print(f"\n[5] Saved: {out_tables / 'table_06b_top_keyword_cooccur_pairs.csv'}")
    
    # ============ Build VOSviewer files ============
    print(f"\n[6] Generating VOSviewer input files...")
    
    out_vos = repo_root / "results" / "vosviewer"
    out_vos.mkdir(parents=True, exist_ok=True)
    
    # Get all keywords appearing in edges (after filter)
    nodes_in_network = set()
    for kw1, kw2 in cooc_filtered.keys():
        nodes_in_network.add(kw1)
        nodes_in_network.add(kw2)
    
    # Map: keyword -> node id (1-indexed)
    sorted_kws = sorted(nodes_in_network)
    kw_to_id = {kw: i+1 for i, kw in enumerate(sorted_kws)}
    
    # Lookup for node weight (n_records)
    weight_lookup = dict(zip(lookup["keyword"], lookup["n_records"]))
    
    # Map file: id, label, weight
    map_lines = ["id\tlabel\tweight<Documents>"]
    for kw, nid in kw_to_id.items():
        weight = weight_lookup.get(kw, 0)
        map_lines.append(f"{nid}\t{kw}\t{int(weight)}")
    
    map_path = out_vos / "keyword_cooccur_map.txt"
    map_path.write_text("\n".join(map_lines), encoding="utf-8")
    print(f"    Map file: {map_path}  ({len(kw_to_id)} nodes)")
    
    # Network file: id1, id2, strength
    net_lines = []
    for (kw1, kw2), w in sorted(cooc_filtered.items(), key=lambda x: -x[1]):
        id1 = kw_to_id[kw1]
        id2 = kw_to_id[kw2]
        net_lines.append(f"{id1}\t{id2}\t{w}")
    
    net_path = out_vos / "keyword_cooccur_network.txt"
    net_path.write_text("\n".join(net_lines), encoding="utf-8")
    print(f"    Network file: {net_path}  ({len(net_lines)} edges)")
    
    # ============ Summary ============
    print(f"\n[7] Network statistics:")
    print(f"    Nodes:      {len(kw_to_id):,}")
    print(f"    Edges:      {len(cooc_filtered):,}")
    print(f"    Density:    {2*len(cooc_filtered)/(len(kw_to_id)*(len(kw_to_id)-1)):.3f}")
    print(f"    Max weight: {max(cooc_filtered.values()):,}")
    print(f"    Min weight: {min(cooc_filtered.values()):,}")
    
    print("\n" + "=" * 70)
    print("VOSVIEWER WORKFLOW:")
    print("1. Open VOSviewer 1.6.20")
    print("2. File -> Create map -> Create map based on network data")
    print(f"3. Choose 'Read data from VOSviewer files'")
    print(f"4. Map file: {map_path}")
    print(f"5. Network file: {net_path}")
    print("6. Choose layout/clustering parameters:")
    print("   - Normalization: Association strength")
    print("   - Layout: attraction=2, repulsion=0")
    print("   - Clustering: resolution=0.80 (yields 5-7 clusters)")
    print("   - Min cluster size: 5")
    print("=" * 70)


if __name__ == "__main__":
    main()
