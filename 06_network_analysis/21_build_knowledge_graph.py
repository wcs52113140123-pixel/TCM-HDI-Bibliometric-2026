"""
Day 10 T3: Build 3-axis Knowledge Graph from complete (herb, drug, target, mechanism) triples.

The "gold-standard" subset: interactions with ALL three axes specified
(drug_known + target_known + mech_specific). These are the most rigorously
characterized claims in the corpus — what HDI researchers actually want
to act on.

Outputs:
  - data/processed/network/kg_triples.parquet          ← long-format triples (Supp Table)
  - data/processed/network/kg_multigraph.graphml        ← heterogeneous multigraph
  - data/processed/network/drug_target_edges.parquet    ← bipartite (T1+T2 trio completion)
  - data/processed/network/drug_class_x_mechanism.parquet   ⭐ Figure 3a heatmap source
  - data/processed/network/target_family_x_drug_class.parquet ⭐ Figure 3b heatmap source
  - data/processed/network/kg_chain_summary.parquet     ← herb_family → mech → drug_class flows

Console: gold-standard hub analysis, top mechanistic chains, sample evidence.

Usage:
    python 06_network_analysis/21_build_knowledge_graph.py
        [--model openai/gpt-4o-mini]
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


def aggregate_drug_target_edge(group: pd.DataFrame) -> dict:
    """For one (drug, target) group, produce aggregated edge attributes."""
    n = len(group)
    mechs = group["mechanism"].dropna().tolist()
    specific = [m for m in mechs if m not in ("unspecified", "other")]
    top_mech = Counter(specific).most_common(1)[0][0] if specific else (
        Counter(mechs).most_common(1)[0][0] if mechs else None
    )
    dirs = group["direction"].dropna().tolist()
    top_dir = Counter(dirs).most_common(1)[0][0] if dirs else None
    conf = group["confidence"].dropna()
    herbs = group["herb_canonical_latin"].dropna().tolist()
    top_herb = Counter(herbs).most_common(1)[0][0] if herbs else None

    return {
        "n_records": n,
        "top_mechanism": top_mech,
        "mechanism_set": "|".join(sorted(set(mechs))) if mechs else None,
        "n_distinct_mechanisms": len(set(mechs)),
        "top_direction": top_dir,
        "mean_confidence": float(conf.mean()) if len(conf) else None,
        "top_herb": top_herb,
        "n_distinct_herbs": len(set(herbs)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary")
    args = ap.parse_args()

    safe = args.model.replace("/", "__").replace(".", "_")
    in_path = LLM_DIR / f"{args.prefix}_{safe}.interactions_normalized.parquet"
    if not in_path.exists():
        print(f"FATAL: {in_path.relative_to(REPO)} not found")
        return

    print(f"{'='*72}\n  Day 10 T3: 3-axis Knowledge Graph from complete triples\n{'='*72}")
    df = pd.read_parquet(in_path)
    print(f"  Loaded {len(df):,} interactions")

    # ================================================================
    # STAGE 1: Extract gold-standard triples (3-axis complete)
    # ================================================================
    triples = df[
        (df["interaction_class"] == "complete")
        & (df["mech_specific"] == True)
        & df["herb_canonical_latin"].notna()
        & df["drug_canonical"].notna()
        & df["target_canonical"].notna()
        & df["mechanism"].notna()
    ].copy()
    print(f"  Gold-standard 3-axis triples (complete + specific mech + all three "
          f"canonical fields populated): {len(triples):,}")

    if len(triples) == 0:
        print("  No triples found. Exiting.")
        return

    # Save triple table
    triple_cols = [
        "record_id", "year",
        "herb_canonical_latin", "herb_canonical_english",
        "herb_family", "herb_type", "herb_in_map",
        "drug_canonical", "drug_class",
        "target_canonical", "target_family",
        "mechanism", "direction", "confidence",
        "evidence_type", "clinical_significance",
        "evidence_quote",
    ]
    triple_cols = [c for c in triple_cols if c in triples.columns]
    triples_out = triples[triple_cols].copy()
    triples_path = NET_DIR / "kg_triples.parquet"
    triples_out.to_parquet(triples_path, index=False)
    print(f"  → {triples_path.relative_to(REPO)} ({len(triples_out):,} rows)")

    # ================================================================
    # STAGE 2: Heterogeneous multigraph
    # ================================================================
    G = nx.MultiGraph()  # multi because (herb, drug) can have multiple mech-labeled edges

    # Add herb nodes
    for h, sub in triples.groupby("herb_canonical_latin"):
        first = sub.iloc[0]
        G.add_node(
            f"herb::{h}",
            node_type="herb",
            display_name=str(first.get("herb_canonical_english") or h),
            family_or_class=str(first.get("herb_family") or "unmapped"),
            in_map=str(bool(first.get("herb_in_map", False))),
            n_triples=len(sub),
        )

    # Add drug nodes
    for d, sub in triples.groupby("drug_canonical"):
        first = sub.iloc[0]
        G.add_node(
            f"drug::{d}",
            node_type="drug",
            display_name=str(d),
            family_or_class=str(first.get("drug_class") or "other"),
            n_triples=len(sub),
        )

    # Add target nodes
    for t, sub in triples.groupby("target_canonical"):
        first = sub.iloc[0]
        G.add_node(
            f"target::{t}",
            node_type="target",
            display_name=str(t),
            family_or_class=str(first.get("target_family") or "unmapped"),
            n_triples=len(sub),
        )

    # Add edges: each triple produces 3 edges (herb-drug, herb-target, drug-target)
    # labeled by mechanism. We'll aggregate by (node1, node2, mechanism) to dedupe.
    edge_records = {}  # (n1, n2, mech) → list of (record_id, direction, confidence)

    for _, row in triples.iterrows():
        h = f"herb::{row['herb_canonical_latin']}"
        d = f"drug::{row['drug_canonical']}"
        t = f"target::{row['target_canonical']}"
        mech = row["mechanism"]
        rec_id = str(row["record_id"])
        direction = row["direction"]
        conf = row["confidence"]
        year = row.get("year")

        for (u, v) in [(h, d), (h, t), (d, t)]:
            key = (u, v, mech)
            if key not in edge_records:
                edge_records[key] = {
                    "record_ids": [], "directions": [],
                    "confidences": [], "years": []
                }
            edge_records[key]["record_ids"].append(rec_id)
            if pd.notna(direction):
                edge_records[key]["directions"].append(direction)
            if pd.notna(conf):
                edge_records[key]["confidences"].append(float(conf))
            if pd.notna(year):
                edge_records[key]["years"].append(int(year))

    for (u, v, mech), info in edge_records.items():
        G.add_edge(
            u, v,
            mechanism=str(mech),
            n_records=len(info["record_ids"]),
            top_direction=Counter(info["directions"]).most_common(1)[0][0]
                if info["directions"] else "",
            mean_confidence=sum(info["confidences"])/len(info["confidences"])
                if info["confidences"] else 0.0,
            year_min=min(info["years"]) if info["years"] else 0,
            year_max=max(info["years"]) if info["years"] else 0,
        )

    kg_path = NET_DIR / "kg_multigraph.graphml"
    nx.write_graphml(G, kg_path)
    print(f"  → {kg_path.relative_to(REPO)} "
          f"({G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges)")

    # ================================================================
    # STAGE 3: Drug × Target bipartite (completes the trio with T1+T2)
    # ================================================================
    # Drug-Target edges: each drug + target pair (across triples)
    dt = triples[["herb_canonical_latin", "drug_canonical", "target_canonical",
                  "mechanism", "direction", "confidence"]].copy()
    dt_agg = (
        dt.groupby(["drug_canonical", "target_canonical"], group_keys=False)
        .apply(aggregate_drug_target_edge, include_groups=False)
        .reset_index()
    )
    dt_edges = pd.concat(
        [dt_agg[["drug_canonical", "target_canonical"]],
         pd.DataFrame(dt_agg[0].tolist())], axis=1
    )
    dt_path = NET_DIR / "drug_target_edges.parquet"
    dt_edges.to_parquet(dt_path, index=False)
    print(f"  → {dt_path.relative_to(REPO)} "
          f"({len(dt_edges):,} unique drug-target pairs)")

    # ================================================================
    # STAGE 4: Cross-tab matrices (Figure 3 heatmap sources)
    # ================================================================
    # 4a: drug_class × mechanism
    mat_dc_m = (
        triples.groupby(["drug_class", "mechanism"])
        .size().reset_index(name="n_records")
        .sort_values("n_records", ascending=False)
    )
    mat_dc_m_path = NET_DIR / "drug_class_x_mechanism.parquet"
    mat_dc_m.to_parquet(mat_dc_m_path, index=False)
    print(f"  → {mat_dc_m_path.relative_to(REPO)} "
          f"({len(mat_dc_m):,} (drug_class, mechanism) pairs)")

    # 4b: target_family × drug_class
    mat_tf_dc = (
        triples.groupby(["target_family", "drug_class"])
        .size().reset_index(name="n_records")
        .sort_values("n_records", ascending=False)
    )
    mat_tf_dc_path = NET_DIR / "target_family_x_drug_class.parquet"
    mat_tf_dc.to_parquet(mat_tf_dc_path, index=False)
    print(f"  → {mat_tf_dc_path.relative_to(REPO)} "
          f"({len(mat_tf_dc):,} (target_family, drug_class) pairs)")

    # 4c: herb_family → mechanism → drug_class chains (for Sankey)
    chains = (
        triples[triples["herb_family"].notna() & triples["drug_class"].notna()]
        .groupby(["herb_family", "mechanism", "drug_class"])
        .size().reset_index(name="n_records")
        .sort_values("n_records", ascending=False)
    )
    chain_path = NET_DIR / "kg_chain_summary.parquet"
    chains.to_parquet(chain_path, index=False)
    print(f"  → {chain_path.relative_to(REPO)} "
          f"({len(chains):,} herb_family → mech → drug_class chains)")

    # ================================================================
    # STAGE 5: Knowledge Graph analytics
    # ================================================================
    print(f"\n{'='*72}\n  KNOWLEDGE GRAPH ANALYTICS (gold-standard subset)\n{'='*72}")
    print(f"  Nodes:    {G.number_of_nodes():>4,} ", end="")
    type_counts = Counter(G.nodes[n]["node_type"] for n in G.nodes())
    print(f"({type_counts.get('herb',0)} herbs + {type_counts.get('drug',0)} drugs "
          f"+ {type_counts.get('target',0)} targets)")
    print(f"  Edges:    {G.number_of_edges():>4,} (3 edges per triple × {len(triples):,} triples, "
          f"deduplicated by mechanism)")

    # Most common (herb, drug, target, mech) signatures
    print(f"\n  --- Top 20 GOLD-STANDARD TRIPLES (most-replicated 4-tuples) ---")
    quad_counts = (
        triples.groupby(["herb_canonical_latin", "drug_canonical",
                         "target_canonical", "mechanism"])
        .size().reset_index(name="n").sort_values("n", ascending=False)
    )
    print(f"  {'Herb':24s} × {'Drug':18s} → {'Target':12s} via {'mechanism':22s} {'n':>3}")
    print(f"  {'-'*24}   {'-'*18}   {'-'*12}     {'-'*22} {'-'*3}")
    for _, r in quad_counts.head(20).iterrows():
        print(f"  {str(r['herb_canonical_latin'])[:23]:24s} × "
              f"{str(r['drug_canonical'])[:17]:18s} → "
              f"{str(r['target_canonical'])[:11]:12s} via "
              f"{str(r['mechanism'])[:21]:22s} {int(r['n']):>3}")

    # Top mechanistic flows
    print(f"\n  --- Top 20 HERB FAMILY → MECHANISM → DRUG CLASS chains ---")
    print(f"  {'Herb family':25s} → {'mechanism':28s} → {'drug class':28s} {'n':>3}")
    print(f"  {'-'*25}   {'-'*28}   {'-'*28} {'-'*3}")
    for _, r in chains.head(20).iterrows():
        print(f"  {str(r['herb_family'])[:24]:25s} → "
              f"{str(r['mechanism'])[:27]:28s} → "
              f"{str(r['drug_class'])[:27]:28s} {int(r['n_records']):>3}")

    # Drug class × mechanism flows
    print(f"\n  --- Top 15 DRUG CLASS × MECHANISM pairs ---")
    print(f"  {'Drug class':30s} ↔ {'mechanism':30s} {'n':>4}")
    print(f"  {'-'*30}   {'-'*30} {'-'*4}")
    for _, r in mat_dc_m.head(15).iterrows():
        print(f"  {str(r['drug_class'])[:29]:30s} ↔ "
              f"{str(r['mechanism'])[:29]:30s} {int(r['n_records']):>4}")

    # Drug × Target hub
    print(f"\n  --- Top 15 DRUG × TARGET hubs (most herb evidence) ---")
    dt_sorted = dt_edges.sort_values("n_records", ascending=False).head(15)
    print(f"  {'Drug':25s} × {'Target':18s} {'n':>3} {'top_herb':25s}  {'top_mech':25s}")
    print(f"  {'-'*25}   {'-'*18} {'-'*3} {'-'*25}  {'-'*25}")
    for _, r in dt_sorted.iterrows():
        print(f"  {str(r['drug_canonical'])[:24]:25s} × "
              f"{str(r['target_canonical'])[:17]:18s} "
              f"{int(r['n_records']):>3} "
              f"{str(r.get('top_herb',''))[:24]:25s}  "
              f"{str(r.get('top_mechanism',''))[:24]:25s}")

    # Direction summary
    print(f"\n  --- Direction distribution in gold-standard triples ---")
    for d, cnt in triples["direction"].value_counts(dropna=False).head(10).items():
        print(f"    {(d or '(null)'):30s} {cnt:>4,}  ({cnt/len(triples)*100:.1f}%)")

    # Confidence summary
    print(f"\n  --- Confidence distribution in gold-standard triples ---")
    conf_series = triples["confidence"].dropna()
    if len(conf_series):
        print(f"    Mean: {conf_series.mean():.3f}   Median: {conf_series.median():.3f}   "
              f"Min: {conf_series.min():.2f}   Max: {conf_series.max():.2f}")
        for lo, hi, label in [(0.0, 0.3, "low (<0.3)"),
                              (0.3, 0.6, "moderate (0.3-0.6)"),
                              (0.6, 0.8, "high (0.6-0.8)"),
                              (0.8, 1.01, "very high (≥0.8)")]:
            cnt = ((conf_series >= lo) & (conf_series < hi)).sum()
            print(f"    {label:25s} {cnt:>4,}  ({cnt/len(triples)*100:.1f}%)")

    # Year span
    if "year" in triples.columns and triples["year"].notna().any():
        years = triples["year"].dropna().astype(int)
        print(f"\n  --- Temporal coverage ---")
        print(f"    Year range:     {years.min()} - {years.max()}")
        print(f"    Most active:    {years.value_counts().head(5).to_dict()}")

    print(f"\n  ✓ Day 10 T3 done. Day 10 trilogy COMPLETE.")
    print(f"  Next: Day 10 commit (scripts 19/20/21 + 8 network parquets + 3 graphml + master_progress)")


if __name__ == "__main__":
    main()
