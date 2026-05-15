"""
Block 3B-upgrade: D2 FINI + Institution disambiguation.

Augments each FINI with the author's institution at each publication,
splitting conflated identities (e.g., wang_y@bucm vs wang_y@sutcm).

Strategy:
- For each author-record pair, look up the record's institutions from
  institution_lookup.parquet (ROR + catch-all corrected)
- Position-aware assignment: author at position N gets institution N if
  position <= number of institutions; else fallback to first institution
- For records with single institution: easy match
- For records with no institution data: unknown bucket

Output:
- data/processed/author_lookup_d2.parquet — final, with D2 FINI+inst IDs
- data/processed/author_record_map_d2.parquet — record-author-D2 mapping

Run:
    python 03_descriptive_analysis/06c_author_d2_upgrade.py
"""

import re
from pathlib import Path

import pandas as pd


def make_inst_slug(institution):
    """Simplify institution name into a slug for D2 ID."""
    if not institution or institution == "(unknown)":
        return "unknown"
    s = institution.lower()
    # Take first 5 alphabetic tokens (usually enough)
    tokens = re.findall(r"[a-z]+", s)
    tokens = [t for t in tokens if len(t) >= 2 and t not in {"of", "the", "and", "in"}][:5]
    slug = "_".join(tokens)
    return slug[:60] if slug else "unknown"


def make_d2_id(fini, institution):
    """Build D2 author identifier: fini@inst_slug."""
    if not fini:
        return None
    return f"{fini}@{make_inst_slug(institution)}"


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3B-upgrade: D2 FINI + Institution disambiguation")
    print("=" * 70)
    
    # Load inputs
    print("\n[1] Loading data...")
    author_map = pd.read_parquet(repo_root / "data/processed/author_record_map.parquet")
    inst_lookup = pd.read_parquet(repo_root / "data/processed/institution_lookup.parquet")
    print(f"    Author-record pairs (D1):      {len(author_map):,}")
    print(f"    Records with institutions:     {len(inst_lookup):,}")
    
    # Build record_id -> institutions list mapping
    rid_to_insts = dict(zip(inst_lookup["record_id"], inst_lookup["institutions"]))
    
    # Assign institutions to authors
    print("\n[2] Assigning institutions to authors (position-aware)...")
    
    rows = []
    n_with_inst = 0
    n_without_inst = 0
    
    for _, row in author_map.iterrows():
        rid = row["record_id"]
        fini = row["fini_id"]
        position = row["position"]
        
        insts = rid_to_insts.get(rid)
        if insts is None or len(insts) == 0:
            inst = "(unknown)"
            n_without_inst += 1
        else:
            insts_list = list(insts)
            # Position-aware: author at pos N gets inst at pos N if available
            if position <= len(insts_list):
                inst = insts_list[position - 1]
            else:
                # Fallback to first institution
                inst = insts_list[0]
            n_with_inst += 1
        
        d2_id = make_d2_id(fini, inst)
        rows.append({
            "record_id": rid,
            "fini_id": fini,
            "position": position,
            "d2_id": d2_id,
            "institution": inst,
        })
    
    ar_d2 = pd.DataFrame(rows)
    print(f"    With institution:    {n_with_inst:,}")
    print(f"    Without institution: {n_without_inst:,} (fallback to @unknown)")
    
    # Build D2 author lookup
    print("\n[3] Building D2 author lookup...")
    
    d2_stats = []
    for d2_id, group in ar_d2.groupby("d2_id"):
        if d2_id is None:
            continue
        record_ids = group["record_id"].unique().tolist()
        # Most common institution for this D2 (in case of fallback)
        inst_mode = group["institution"].mode().iloc[0] if len(group) > 0 else "(unknown)"
        first_author_count = int((group["position"] == 1).sum())
        
        d2_stats.append({
            "d2_id": d2_id,
            "fini_id": group["fini_id"].iloc[0],
            "institution": inst_mode,
            "is_unknown_inst": (inst_mode == "(unknown)"),
            "n_records": len(record_ids),
            "first_author_count": first_author_count,
            "sample_record_ids": "|".join(record_ids[:5]),
        })
    
    d2_df = pd.DataFrame(d2_stats).sort_values("n_records", ascending=False).reset_index(drop=True)
    
    # Stats
    print(f"\n[4] D2 disambiguation results:")
    print(f"    D1 FINI count:                 16,094")
    print(f"    D2 FINI+Inst count:            {len(d2_df):,}")
    print(f"    Reduction factor (split):      {len(d2_df)/16094:.2f}x")
    print()
    print(f"    D2 authors with >=2 papers:    {(d2_df['n_records'] >= 2).sum():,}")
    print(f"    D2 authors with >=5 papers:    {(d2_df['n_records'] >= 5).sum():,}")
    print(f"    D2 authors with >=10 papers:   {(d2_df['n_records'] >= 10).sum():,}")
    print(f"    D2 authors with >=20 papers:   {(d2_df['n_records'] >= 20).sum():,}")
    print()
    print(f"    Authors with known institution: {(~d2_df['is_unknown_inst']).sum():,} "
          f"({100*(~d2_df['is_unknown_inst']).sum()/len(d2_df):.1f}%)")
    
    # Top 30 (exclude unknown)
    print(f"\n[5] Top 30 D2 authors (excluding @unknown):")
    print(f"    {'Rank':<5} {'FINI':<14s} {'Institution':<48s} {'NPub':>5s} {'1st':>5s}")
    print(f"    {'-'*4:<5} {'-'*14:<14s} {'-'*48:<48s} {'-'*5:>5s} {'-'*5:>5s}")
    top30_d2 = d2_df[~d2_df['is_unknown_inst']].head(30)
    for i, row in top30_d2.iterrows():
        inst_short = row["institution"][:47]
        print(f"    {i+1:<5} {row['fini_id'][:13]:<14s} {inst_short:<48s} "
              f"{int(row['n_records']):>5,} {int(row['first_author_count']):>5,}")
    
    # Compare with D1 ambiguous FINIs
    print(f"\n[6] D1 -> D2 disambiguation for top Chinese surname FINIs:")
    for dom_fini in ["wang_y", "zhang_y", "li_y", "wang_x", "li_x", "liu_y", "chen_y"]:
        d1_n_pairs = (ar_d2["fini_id"] == dom_fini).sum()
        d2_unique = ar_d2[ar_d2["fini_id"] == dom_fini]["d2_id"].nunique()
        # Top 3 D2 for this FINI
        top_d2 = (d2_df[(d2_df["fini_id"] == dom_fini) & (~d2_df["is_unknown_inst"])]
                   .sort_values("n_records", ascending=False).head(3))
        print(f"\n    {dom_fini}: D1={d1_n_pairs} author-records -> D2={d2_unique} distinct identifiers")
        for _, r in top_d2.iterrows():
            inst = r["institution"][:50]
            print(f"      Top: n={int(r['n_records'])} @ {inst}")
    
    # Save outputs
    out_dir = repo_root / "data" / "processed"
    d2_df.to_parquet(out_dir / "author_lookup_d2.parquet", index=False, engine="pyarrow")
    ar_d2.to_parquet(out_dir / "author_record_map_d2.parquet", index=False, engine="pyarrow")
    print(f"\n[7] Outputs saved:")
    print(f"    {out_dir / 'author_lookup_d2.parquet'}  ({len(d2_df):,} D2 authors)")
    print(f"    {out_dir / 'author_record_map_d2.parquet'}  ({len(ar_d2):,} D2 author-records)")
    
    print("\n" + "=" * 70)
    print("DONE: Ready to re-run Top 30 authors + Lotka with D2 method")
    print("=" * 70)


if __name__ == "__main__":
    main()
