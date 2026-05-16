"""
Day 10 T2: Build Herb × Target bipartite network.

Aggregates target_known interactions (1,734 records) into a bipartite network:
  - Herb nodes (herb_canonical_latin)
  - Target nodes (target_canonical — HGNC symbol or descriptor)
  - Edges weighted by record count, attributed with top mechanism / direction /
    mean confidence / drug class context

Outputs:
  - data/processed/network/herb_target_edges.parquet
  - data/processed/network/herb_target_nodes.parquet
  - data/processed/network/herb_target.graphml
  - data/processed/network/herb_family_x_target_family.parquet  ⭐ Figure 2 heatmap source
  - data/processed/network/target_family_x_mechanism.parquet    ⭐ Figure 2b heatmap source

Console: network metrics + Top hubs + Top edges + Family-level cross-tabs.

Usage:
    python 06_network_analysis/20_build_herb_target_network.py
        [--model openai/gpt-4o-mini]
        [--min-edge-weight 1]
        [--exclude-fragmentary]
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
    """For one (herb, target) group, produce aggregated edge attributes."""
    n = len(group)

    # Top mechanism (prefer specific over other/unspecified)
    mechs = group["mechanism"].dropna().tolist()
    specific = [m for m in mechs if m not in ("unspecified", "other")]
    top_mech = Counter(specific).most_common(1)[0][0] if specific else (
        Counter(mechs).most_common(1)[0][0] if mechs else None
    )
    mech_set = sorted(set(mechs))

    # Direction
    dirs = group["direction"].dropna().tolist()
    top_dir = Counter(dirs).most_common(1)[0][0] if dirs else None

    # Confidence
    conf = group["confidence"].dropna()
    mean_conf = float(conf.mean()) if len(conf) else None

    # Years
    years = sorted(group["year"].dropna().astype(int).unique())
    year_min = int(min(years)) if years else None
    year_max = int(max(years)) if years else None

    # Drugs touched (context — which drugs are involved when herb hits this target)
    drugs = group["drug_canonical"].dropna().tolist()
    drug_set = sorted(set(drugs))
    top_drug = Counter(drugs).most_common(1)[0][0] if drugs else None

    # Drug class distribution
    drug_classes = group["drug_class"].dropna().tolist()
    top_drug_class = (
        Counter([c for c in drug_classes if c != "other"]).most_common(1)[0][0]
        if any(c != "other" for c in drug_classes)
        else (Counter(drug_classes).most_common(1)[0][0] if drug_classes else None)
    )

    # Evidence type
    evidences = group["evidence_type"].dropna().tolist()
    top_evidence = Counter(evidences).most_common(1)[0][0] if evidences else None

    # Clinical significance
    sig_order = {"high": 3, "moderate": 2, "low": 1, "none": 0, "not_assessed": 0}
    sigs = group["clinical_significance"].dropna().tolist()
    max_sig = max(sigs, key=lambda s: sig_order.get(s, 0)) if sigs else None

    return {
        "n_records": n,
        "top_mechanism": top_mech,
        "mechanism_set": "|".join(mech_set) if mech_set else None,
        "n_distinct_mechanisms": len(mech_set),
        "top_direction": top_dir,
        "mean_confidence": mean_conf,
        "top_drug": top_drug,
        "top_drug_class": top_drug_class,
        "n_distinct_drugs": len(drug_set),
        "top_evidence_type": top_evidence,
        "max_clinical_significance": max_sig,
        "year_min": year_min,
        "year_max": year_max,
        "record_ids": "|".join(group["record_id"].astype(str).tolist()),
    }


def build_node_table(edge_df: pd.DataFrame, df_orig: pd.DataFrame) -> pd.DataFrame:
    """Build node metadata for herbs and targets."""
    nodes = []

    # Herb nodes
    herbs = edge_df["herb"].unique()
    herb_meta = (
        df_orig[df_orig["herb_canonical_latin"].isin(herbs)]
        .drop_duplicates(subset="herb_canonical_latin")
        .set_index("herb_canonical_latin")
    )
    for h in herbs:
        if h in herb_meta.index:
            m = herb_meta.loc[h]
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

    # Target nodes
    targets = edge_df["target"].unique()
    target_meta = (
        df_orig[df_orig["target_canonical"].isin(targets)]
        .drop_duplicates(subset="target_canonical")
        .set_index("target_canonical")
    )
    for t in targets:
        if t in target_meta.index:
            m = target_meta.loc[t]
            fam = m.get("target_family") or "unmapped"
            nodes.append({
                "node_id": t,
                "node_type": "target",
                "display_name": t,
                "family_or_class": fam,
                "in_map": fam not in ("unmapped", None),
                "secondary_label": "",
            })
        else:
            nodes.append({
                "node_id": t, "node_type": "target",
                "display_name": t, "family_or_class": "unmapped",
                "in_map": False, "secondary_label": "",
            })

    return pd.DataFrame(nodes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary")
    ap.add_argument("--min-edge-weight", type=int, default=1)
    ap.add_argument("--exclude-fragmentary", action="store_true")
    args = ap.parse_args()

    safe = args.model.replace("/", "__").replace(".", "_")
    in_path = LLM_DIR / f"{args.prefix}_{safe}.interactions_normalized.parquet"
    if not in_path.exists():
        print(f"FATAL: {in_path.relative_to(REPO)} not found")
        return

    print(f"{'='*72}\n  Day 10 T2: Herb × Target Bipartite Network\n{'='*72}")
    df = pd.read_parquet(in_path)
    print(f"  Loaded {len(df):,} interactions")

    # Filter: must have both canonical herb and canonical target
    df = df[df["herb_canonical_latin"].notna() & df["target_canonical"].notna()].copy()
    print(f"  After requiring herb_canonical + target_canonical: {len(df):,}")

    if args.exclude_fragmentary:
        df = df[df["interaction_class"] != "fragmentary"].copy()
        print(f"  After excluding fragmentary: {len(df):,}")

    if len(df) == 0:
        print("  No data after filtering. Exiting.")
        return

    # --- Aggregate edges ---
    df_orig = df.copy()
    df_e = df.rename(columns={
        "herb_canonical_latin": "herb",
        "target_canonical": "target",
    })
    edge_agg = (
        df_e.groupby(["herb", "target"], group_keys=False)
        .apply(aggregate_edge, include_groups=False)
        .reset_index()
    )
    edge_df = pd.concat(
        [edge_agg[["herb", "target"]],
         pd.DataFrame(edge_agg[0].tolist())], axis=1
    )

    n_edges_raw = len(edge_df)
    if args.min_edge_weight > 1:
        edge_df = edge_df[edge_df["n_records"] >= args.min_edge_weight].copy()
        print(f"  Edges before min-weight filter: {n_edges_raw:,}")
        print(f"  Edges after  min-weight ≥ {args.min_edge_weight}: {len(edge_df):,}")
    else:
        print(f"  Total edges (unique herb-target pairs): {len(edge_df):,}")

    # --- Build node table ---
    node_df = build_node_table(edge_df, df_orig)
    n_herbs = (node_df["node_type"] == "herb").sum()
    n_targets = (node_df["node_type"] == "target").sum()
    print(f"  Total nodes: {len(node_df):,} ({n_herbs} herbs + {n_targets} targets)")

    # --- Save tables ---
    edge_path = NET_DIR / "herb_target_edges.parquet"
    node_path = NET_DIR / "herb_target_nodes.parquet"
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
            display_name=str(n["display_name"]),
            family_or_class=str(n["family_or_class"]),
            in_map=str(n["in_map"]),
            secondary_label=str(n["secondary_label"]),
        )
    for _, e in edge_df.iterrows():
        G.add_edge(
            e["herb"], e["target"],
            weight=int(e["n_records"]),
            top_mechanism=str(e["top_mechanism"]) if pd.notna(e["top_mechanism"]) else "",
            top_direction=str(e["top_direction"]) if pd.notna(e["top_direction"]) else "",
            mean_confidence=float(e["mean_confidence"])
                if pd.notna(e["mean_confidence"]) else 0.0,
            top_drug=str(e["top_drug"]) if pd.notna(e["top_drug"]) else "",
            top_drug_class=str(e["top_drug_class"]) if pd.notna(e["top_drug_class"]) else "",
            max_clinical_significance=str(e["max_clinical_significance"])
                if pd.notna(e["max_clinical_significance"]) else "",
            year_min=int(e["year_min"]) if pd.notna(e["year_min"]) else 0,
            year_max=int(e["year_max"]) if pd.notna(e["year_max"]) else 0,
        )
    graphml_path = NET_DIR / "herb_target.graphml"
    nx.write_graphml(G, graphml_path)
    print(f"  → {graphml_path.relative_to(REPO)} (Cytoscape compatible)")

    # ================================================================
    # NETWORK METRICS
    # ================================================================
    print(f"\n{'='*72}\n  NETWORK METRICS\n{'='*72}")
    print(f"  Nodes:               {G.number_of_nodes():>5,} "
          f"({n_herbs} herbs + {n_targets} targets)")
    print(f"  Edges:               {G.number_of_edges():>5,}")
    bipartite_density = G.number_of_edges() / (n_herbs * n_targets) \
        if (n_herbs and n_targets) else 0
    print(f"  Bipartite density:   {bipartite_density:>5.4f} "
          f"(fraction of possible herb×target pairs realized)")

    components = list(nx.connected_components(G))
    sizes = sorted([len(c) for c in components], reverse=True)
    print(f"  Connected components: {len(components)}")
    print(f"    Largest:           {sizes[0]:>4,} nodes "
          f"({sizes[0]/G.number_of_nodes()*100:.1f}% of all)")

    herb_degrees = sorted(
        [(n, G.degree(n)) for n in G.nodes()
         if G.nodes[n]["node_type"] == "herb"],
        key=lambda x: x[1], reverse=True
    )
    target_degrees = sorted(
        [(n, G.degree(n)) for n in G.nodes()
         if G.nodes[n]["node_type"] == "target"],
        key=lambda x: x[1], reverse=True
    )
    print(f"\n  Herb degree:    mean {sum(d for _, d in herb_degrees)/max(len(herb_degrees),1):.2f}, "
          f"max {herb_degrees[0][1] if herb_degrees else 0}")
    print(f"  Target degree:  mean {sum(d for _, d in target_degrees)/max(len(target_degrees),1):.2f}, "
          f"max {target_degrees[0][1] if target_degrees else 0}")

    # ================================================================
    # TOP HUBS
    # ================================================================
    print(f"\n  --- Top 20 HUB HERBS (most distinct targets) ---")
    print(f"  {'Herb (canonical)':40s} {'deg':>5} {'family':25s}")
    print(f"  {'-'*40} {'-'*5} {'-'*25}")
    for h, deg in herb_degrees[:20]:
        fam = G.nodes[h]["family_or_class"]
        print(f"  {h[:39]:40s} {deg:>5d} {fam[:24]:25s}")

    print(f"\n  --- Top 20 HUB TARGETS (most distinct herbs) ---")
    print(f"  {'Target':30s} {'deg':>5} {'family':30s}")
    print(f"  {'-'*30} {'-'*5} {'-'*30}")
    for t, deg in target_degrees[:20]:
        fam = G.nodes[t]["family_or_class"]
        print(f"  {t[:29]:30s} {deg:>5d} {fam[:29]:30s}")

    # ================================================================
    # TOP EDGES
    # ================================================================
    print(f"\n  --- Top 25 STRONGEST EDGES (most supporting records) ---")
    print(f"  {'Herb':28s} × {'Target':18s} {'n':>3} {'mech':>30s} {'top_drug':20s}")
    print(f"  {'-'*28}   {'-'*18} {'-'*3} {'-'*30} {'-'*20}")
    edges_by_weight = sorted(
        G.edges(data=True), key=lambda e: e[2].get("weight", 0), reverse=True
    )
    for u, v, attrs in edges_by_weight[:25]:
        # u/v ordering: ensure herb first
        utype = G.nodes[u]["node_type"]
        h, t = (u, v) if utype == "herb" else (v, u)
        w = attrs.get("weight", 0)
        m = attrs.get("top_mechanism", "")
        d = attrs.get("top_drug", "")
        print(f"  {h[:27]:28s} × {t[:17]:18s} {w:>3d} {m[:29]:>30s} {d[:19]:20s}")

    # ================================================================
    # MECHANISM SUMMARY ON EDGES
    # ================================================================
    print(f"\n  --- Top mechanisms on edges ---")
    for mech, cnt in edge_df["top_mechanism"].value_counts(dropna=False).head(15).items():
        print(f"    {(mech or '(null)'):35s} {cnt:>5,} edges")

    # ================================================================
    # FAMILY-LEVEL CROSS-TABS (Figure 2 heatmap sources)
    # ================================================================
    # Need to merge family info onto the original df
    df_with_fams = df_orig[[
        "herb_canonical_latin", "target_canonical",
        "herb_family", "target_family", "mechanism", "direction"
    ]].copy()

    # Filter to records with both families (mapped herbs and mapped targets only)
    df_fam = df_with_fams[
        df_with_fams["herb_family"].notna()
        & df_with_fams["target_family"].notna()
    ].copy()
    print(f"\n{'='*72}\n  FAMILY-LEVEL CROSS-TABS (mapped only, "
          f"{len(df_fam):,} records)\n{'='*72}")

    # 1. herb_family × target_family matrix
    matrix_hf_tf = (
        df_fam.groupby(["herb_family", "target_family"])
        .size().reset_index(name="n_records")
    )
    matrix_hf_tf = matrix_hf_tf.sort_values("n_records", ascending=False)
    mat_path = NET_DIR / "herb_family_x_target_family.parquet"
    matrix_hf_tf.to_parquet(mat_path, index=False)
    print(f"  → {mat_path.relative_to(REPO)} "
          f"({len(matrix_hf_tf):,} (herb_family, target_family) pairs)")

    print(f"\n  Top 20 (herb_family → target_family) pairs:")
    for _, r in matrix_hf_tf.head(20).iterrows():
        print(f"    {r['herb_family']:30s} → {r['target_family']:25s} "
              f"{int(r['n_records']):>5,}")

    # 2. target_family × mechanism cross-tab
    matrix_tf_m = (
        df_fam.groupby(["target_family", "mechanism"])
        .size().reset_index(name="n_records")
    )
    matrix_tf_m = matrix_tf_m.sort_values("n_records", ascending=False)
    mat2_path = NET_DIR / "target_family_x_mechanism.parquet"
    matrix_tf_m.to_parquet(mat2_path, index=False)
    print(f"\n  → {mat2_path.relative_to(REPO)} "
          f"({len(matrix_tf_m):,} (target_family, mechanism) pairs)")

    print(f"\n  Top 15 (target_family → mechanism) pairs:")
    for _, r in matrix_tf_m.head(15).iterrows():
        print(f"    {r['target_family']:25s} → {r['mechanism']:30s} "
              f"{int(r['n_records']):>5,}")

    # 3. herb_family-level summary
    print(f"\n  Herb family rank by target diversity (n distinct target families):")
    hf_summary = (
        df_fam.groupby("herb_family")
        .agg(n_records=("target_canonical", "size"),
             n_distinct_targets=("target_canonical", "nunique"),
             n_distinct_target_families=("target_family", "nunique"))
        .sort_values("n_records", ascending=False)
        .head(15)
    )
    for hf, row in hf_summary.iterrows():
        print(f"    {hf:30s} records {int(row['n_records']):>4,}  "
              f"unique targets {int(row['n_distinct_targets']):>3}  "
              f"target families {int(row['n_distinct_target_families']):>2}")

    print(f"\n  ✓ Day 10 T2 done.")
    print(f"  Next: 21_build_knowledge_graph.py (T3 — 3-axis KG from "
          f"complete triples for Figure 3)")


if __name__ == "__main__":
    main()
