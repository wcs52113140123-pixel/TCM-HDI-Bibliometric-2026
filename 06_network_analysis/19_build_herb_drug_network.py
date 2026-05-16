"""
Day 10 T1: Build Herb × Drug bipartite network.

Aggregates the 2,167 drug_known interactions into a clean bipartite network:
  - Herb nodes (herb_canonical_latin)
  - Drug nodes (drug_canonical)
  - Edges: weighted by record count, attributed with top mechanism / direction /
    mean confidence / evidence record_ids

Outputs:
  - data/processed/network/herb_drug_edges.parquet
  - data/processed/network/herb_drug_nodes.parquet
  - data/processed/network/herb_drug.graphml   (for Cytoscape / Gephi)
  - Console: network-level metrics + Top 20 hub herbs/drugs + Top 20 strongest edges

This is Figure 1 source for the paper.

Usage:
    python 06_network_analysis/19_build_herb_drug_network.py
        [--model openai/gpt-4o-mini]
        [--min-edge-weight 1]    # filter edges with fewer records
        [--exclude-fragmentary]  # also exclude fragmentary class
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import networkx as nx
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LLM_DIR = REPO / "data" / "processed" / "llm_extraction"
NET_DIR = REPO / "data" / "processed" / "network"
NET_DIR.mkdir(parents=True, exist_ok=True)


def aggregate_edge(group: pd.DataFrame) -> dict:
    """For one (herb, drug) group, produce aggregated edge attributes."""
    n = len(group)

    # Most-common mechanism (excluding 'unspecified'/'other' if alternatives exist)
    mechs = group["mechanism"].dropna().tolist()
    specific_mechs = [m for m in mechs if m not in ("unspecified", "other")]
    if specific_mechs:
        top_mech = Counter(specific_mechs).most_common(1)[0][0]
    elif mechs:
        top_mech = Counter(mechs).most_common(1)[0][0]
    else:
        top_mech = None
    mech_set = sorted(set(mechs))

    # Direction
    dirs = group["direction"].dropna().tolist()
    top_dir = Counter(dirs).most_common(1)[0][0] if dirs else None
    dir_set = sorted(set(dirs))

    # Specific target (most common, if any)
    targets = group["target_canonical"].dropna().tolist()
    top_target = Counter(targets).most_common(1)[0][0] if targets else None

    # Evidence type (most common)
    evidences = group["evidence_type"].dropna().tolist()
    top_evidence = Counter(evidences).most_common(1)[0][0] if evidences else None

    # Confidence stats
    conf = group["confidence"].dropna()
    mean_conf = float(conf.mean()) if len(conf) else None

    # Years range
    years = sorted(group["year"].dropna().astype(int).unique())
    year_min = int(min(years)) if years else None
    year_max = int(max(years)) if years else None
    year_span = year_max - year_min + 1 if years else None

    # Clinical significance (max severity)
    sig_order = {"high": 3, "moderate": 2, "low": 1, "none": 0, "not_assessed": 0}
    sigs = group["clinical_significance"].dropna().tolist()
    if sigs:
        max_sig = max(sigs, key=lambda s: sig_order.get(s, 0))
    else:
        max_sig = None

    return {
        "n_records": n,
        "top_mechanism": top_mech,
        "mechanism_set": "|".join(mech_set) if mech_set else None,
        "n_distinct_mechanisms": len(mech_set),
        "top_direction": top_dir,
        "direction_set": "|".join(dir_set) if dir_set else None,
        "top_target": top_target,
        "top_evidence_type": top_evidence,
        "mean_confidence": mean_conf,
        "max_clinical_significance": max_sig,
        "year_min": year_min,
        "year_max": year_max,
        "year_span": year_span,
        "record_ids": "|".join(group["record_id"].astype(str).tolist()),
    }


def build_node_table(df_edges: pd.DataFrame, df_int: pd.DataFrame) -> pd.DataFrame:
    """Build node metadata table from edges + original interactions."""
    nodes = []

    # Herb nodes
    herbs = df_edges["herb"].unique()
    herb_meta_df = df_int[df_int["herb_canonical_latin"].isin(herbs)].drop_duplicates(
        subset="herb_canonical_latin"
    )
    herb_meta = {
        r["herb_canonical_latin"]: r for _, r in herb_meta_df.iterrows()
    }
    for h in herbs:
        m = herb_meta.get(h)
        if m is not None:
            nodes.append({
                "node_id": h,
                "node_type": "herb",
                "display_name": m.get("herb_canonical_english") or h,
                "family_or_class": m.get("herb_family") or "unmapped",
                "in_map": bool(m.get("herb_in_map", False)),
                "secondary_label": m.get("herb_canonical_pinyin") or "",
            })
        else:
            nodes.append({
                "node_id": h, "node_type": "herb",
                "display_name": h, "family_or_class": "unmapped",
                "in_map": False, "secondary_label": "",
            })

    # Drug nodes
    drugs = df_edges["drug"].unique()
    drug_meta_df = df_int[df_int["drug_canonical"].isin(drugs)].drop_duplicates(
        subset="drug_canonical"
    )
    drug_meta = {
        r["drug_canonical"]: r for _, r in drug_meta_df.iterrows()
    }
    for d in drugs:
        m = drug_meta.get(d)
        if m is not None:
            nodes.append({
                "node_id": d,
                "node_type": "drug",
                "display_name": d,
                "family_or_class": m.get("drug_class") or "other",
                "in_map": (m.get("drug_class") or "other") != "other",
                "secondary_label": "",
            })
        else:
            nodes.append({
                "node_id": d, "node_type": "drug",
                "display_name": d, "family_or_class": "other",
                "in_map": False, "secondary_label": "",
            })

    return pd.DataFrame(nodes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary")
    ap.add_argument("--min-edge-weight", type=int, default=1,
                    help="Drop edges with fewer than N records (default 1 = no filter)")
    ap.add_argument("--exclude-fragmentary", action="store_true",
                    help="Drop interactions classified as fragmentary")
    args = ap.parse_args()

    safe = args.model.replace("/", "__").replace(".", "_")
    in_path = LLM_DIR / f"{args.prefix}_{safe}.interactions_normalized.parquet"
    if not in_path.exists():
        print(f"FATAL: {in_path.relative_to(REPO)} not found")
        return

    print(f"{'='*72}\n  Day 10 T1: Herb × Drug Bipartite Network\n{'='*72}")
    df = pd.read_parquet(in_path)
    print(f"  Loaded {len(df):,} interactions from {in_path.name}")

    # --- Filter: must have both herb canonical and drug canonical ---
    df = df[df["herb_canonical_latin"].notna() & df["drug_canonical"].notna()].copy()
    print(f"  After requiring herb_canonical + drug_canonical: {len(df):,}")

    if args.exclude_fragmentary:
        df = df[df["interaction_class"] != "fragmentary"].copy()
        print(f"  After excluding fragmentary: {len(df):,}")

    if len(df) == 0:
        print("  No data after filtering. Exiting.")
        return

    # --- Aggregate edges ---
    # Keep an unrenamed copy for node metadata lookup (it uses original column names)
    df_orig = df.copy()
    df = df.rename(columns={
        "herb_canonical_latin": "herb",
        "drug_canonical": "drug",
    })
    edge_agg = df.groupby(["herb", "drug"]).apply(aggregate_edge).reset_index()
    edge_df = pd.concat(
        [edge_agg[["herb", "drug"]],
         pd.DataFrame(edge_agg[0].tolist())], axis=1
    )

    n_edges_raw = len(edge_df)
    if args.min_edge_weight > 1:
        edge_df = edge_df[edge_df["n_records"] >= args.min_edge_weight].copy()
        print(f"  Edges before min-weight filter: {n_edges_raw:,}")
        print(f"  Edges after  min-weight ≥ {args.min_edge_weight}: {len(edge_df):,}")
    else:
        print(f"  Total edges (unique herb-drug pairs): {len(edge_df):,}")

    # --- Build node table (uses original column names from df_orig) ---
    node_df = build_node_table(edge_df, df_orig)
    print(f"  Total nodes: {len(node_df):,} "
          f"({(node_df['node_type']=='herb').sum()} herbs, "
          f"{(node_df['node_type']=='drug').sum()} drugs)")

    # --- Save tables ---
    edge_path = NET_DIR / "herb_drug_edges.parquet"
    node_path = NET_DIR / "herb_drug_nodes.parquet"
    edge_df.to_parquet(edge_path, index=False)
    node_df.to_parquet(node_path, index=False)
    print(f"  → {edge_path.relative_to(REPO)} ({len(edge_df):,} rows)")
    print(f"  → {node_path.relative_to(REPO)} ({len(node_df):,} rows)")

    # --- Build NetworkX graph ---
    G = nx.Graph()
    for _, n in node_df.iterrows():
        G.add_node(
            n["node_id"],
            node_type=n["node_type"],
            display_name=n["display_name"],
            family_or_class=n["family_or_class"],
            in_map=str(n["in_map"]),
            secondary_label=n["secondary_label"],
        )
    for _, e in edge_df.iterrows():
        G.add_edge(
            e["herb"], e["drug"],
            weight=int(e["n_records"]),
            top_mechanism=str(e["top_mechanism"]) if pd.notna(e["top_mechanism"]) else "",
            top_direction=str(e["top_direction"]) if pd.notna(e["top_direction"]) else "",
            mean_confidence=float(e["mean_confidence"])
                if pd.notna(e["mean_confidence"]) else 0.0,
            top_target=str(e["top_target"]) if pd.notna(e["top_target"]) else "",
            max_clinical_significance=str(e["max_clinical_significance"])
                if pd.notna(e["max_clinical_significance"]) else "",
            year_min=int(e["year_min"]) if pd.notna(e["year_min"]) else 0,
            year_max=int(e["year_max"]) if pd.notna(e["year_max"]) else 0,
        )

    graphml_path = NET_DIR / "herb_drug.graphml"
    nx.write_graphml(G, graphml_path)
    print(f"  → {graphml_path.relative_to(REPO)} (Cytoscape/Gephi compatible)")

    # ================================================================
    # NETWORK METRICS
    # ================================================================
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    n_herbs = (node_df["node_type"] == "herb").sum()
    n_drugs = (node_df["node_type"] == "drug").sum()
    print(f"\n{'='*72}\n  NETWORK METRICS\n{'='*72}")
    print(f"  Nodes:               {n_nodes:>6,} ({n_herbs} herbs + {n_drugs} drugs)")
    print(f"  Edges:               {n_edges:>6,}")
    density = 2 * n_edges / (n_nodes * (n_nodes - 1)) if n_nodes >= 2 else 0
    print(f"  Overall density:     {density:>6.5f}")
    bipartite_density = n_edges / (n_herbs * n_drugs) if (n_herbs and n_drugs) else 0
    print(f"  Bipartite density:   {bipartite_density:>6.5f} "
          f"(fraction of possible herb×drug pairs)")

    # Connected components
    components = list(nx.connected_components(G))
    sizes = sorted([len(c) for c in components], reverse=True)
    print(f"  Connected components: {len(components)}")
    print(f"    Largest:           {sizes[0]:>5,} nodes "
          f"({sizes[0]/n_nodes*100:.1f}% of all)")
    if len(sizes) >= 2:
        print(f"    2nd, 3rd, 4th:     {sizes[1]}, "
              f"{sizes[2] if len(sizes)>2 else 0}, "
              f"{sizes[3] if len(sizes)>3 else 0}")
        n_singleton = sum(1 for s in sizes if s == 2)
        print(f"    'Isolated pairs' (size=2): {n_singleton}")

    # Degree distributions
    herb_degrees = sorted(
        [(n, G.degree(n)) for n in G.nodes() if G.nodes[n]["node_type"] == "herb"],
        key=lambda x: x[1], reverse=True
    )
    drug_degrees = sorted(
        [(n, G.degree(n)) for n in G.nodes() if G.nodes[n]["node_type"] == "drug"],
        key=lambda x: x[1], reverse=True
    )
    print(f"\n  Herb degree:  mean {sum(d for _, d in herb_degrees)/max(len(herb_degrees),1):.2f}, "
          f"max {herb_degrees[0][1] if herb_degrees else 0}")
    print(f"  Drug degree:  mean {sum(d for _, d in drug_degrees)/max(len(drug_degrees),1):.2f}, "
          f"max {drug_degrees[0][1] if drug_degrees else 0}")

    # ================================================================
    # TOP HUBS
    # ================================================================
    print(f"\n  --- Top 20 HUB HERBS (most drug partners) ---")
    print(f"  {'Herb (canonical)':40s} {'deg':>5} {'family':25s} {'in_map':>7}")
    print(f"  {'-'*40} {'-'*5} {'-'*25} {'-'*7}")
    for h, deg in herb_degrees[:20]:
        fam = G.nodes[h]["family_or_class"]
        inmap = G.nodes[h]["in_map"]
        print(f"  {h[:39]:40s} {deg:>5d} {fam[:24]:25s} {inmap:>7}")

    print(f"\n  --- Top 20 HUB DRUGS (most herb partners) ---")
    print(f"  {'Drug':40s} {'deg':>5} {'class':25s}")
    print(f"  {'-'*40} {'-'*5} {'-'*25}")
    for d, deg in drug_degrees[:20]:
        cls = G.nodes[d]["family_or_class"]
        print(f"  {d[:39]:40s} {deg:>5d} {cls[:24]:25s}")

    # ================================================================
    # TOP EDGES
    # ================================================================
    edges_by_weight = sorted(
        G.edges(data=True), key=lambda e: e[2].get("weight", 0), reverse=True
    )
    print(f"\n  --- Top 25 STRONGEST EDGES (most supporting records) ---")
    print(f"  {'Herb':28s} × {'Drug':28s} {'n':>4} {'mech':>30s} "
          f"{'dir':>15}")
    print(f"  {'-'*28}   {'-'*28} {'-'*4} {'-'*30} {'-'*15}")
    for u, v, attrs in edges_by_weight[:25]:
        # u is herb (alphabetically), but we encoded both — fix order
        utype = G.nodes[u]["node_type"]
        h, d = (u, v) if utype == "herb" else (v, u)
        w = attrs.get("weight", 0)
        m = attrs.get("top_mechanism", "")
        dir_ = attrs.get("top_direction", "")
        print(f"  {h[:27]:28s} × {d[:27]:28s} {w:>4d} {m[:29]:>30s} "
              f"{dir_[:14]:>15}")

    # ================================================================
    # MECHANISM SUMMARY
    # ================================================================
    print(f"\n  --- Top mechanisms on edges (counts unique edges per top_mechanism) ---")
    mech_counts = edge_df["top_mechanism"].value_counts(dropna=False).head(15)
    for mech, cnt in mech_counts.items():
        print(f"    {(mech or '(null)'):35s} {cnt:>5,} edges")

    print(f"\n  --- Most multi-mechanism edges (n_distinct_mechanisms ≥ 3) ---")
    multi_mech = edge_df[edge_df["n_distinct_mechanisms"] >= 3].sort_values(
        "n_distinct_mechanisms", ascending=False
    )
    for _, e in multi_mech.head(10).iterrows():
        print(f"    {e['herb'][:25]:25s} × {e['drug'][:20]:20s} "
              f"({e['n_distinct_mechanisms']} mechs, {e['n_records']} records): "
              f"{e['mechanism_set']}")

    print(f"\n  ✓ Day 10 T1 done.")
    print(f"  Next: 20_build_herb_target_network.py (T2 — Figure 2 source)")


if __name__ == "__main__":
    main()
