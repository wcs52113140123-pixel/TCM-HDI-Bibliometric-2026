"""
Block 3B.1: Author name standardization via FINI (First Initial + Surname).

Normalizes various author name formats from 4 databases into a common FINI ID:
- WoS:      'Wang, YH'       -> wang_y
- Scopus:   'Wang Y.H.'      -> wang_y  
- Scopus:   'Li Y.-L.'       -> li_y
- OpenAlex: 'Yong Wang'      -> wang_y      (display name -> normalize)
- PubMed:   'Wang YH'        -> wang_y

Strategy:
1. Extract surname and first_initial from each author string
2. Generate FINI ID: lowercase(surname)_lowercase(first_initial)
3. Build author_lookup: FINI -> {name_variants, n_records, first_author_count}

Output:
- data/processed/author_lookup.parquet
    columns: fini_id, canonical_name, n_records, first_author_count, 
             name_variants, sample_record_ids
- data/processed/author_record_map.parquet
    columns: record_id, fini_id, position_in_authors (1=first author)

Run:
    python 03_descriptive_analysis/06a_author_normalize.py
"""

import re
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd


# Common prefixes to strip from surnames
SURNAME_PREFIXES = {"van", "von", "de", "del", "della", "di", "da", "le", "la", "el", "al"}


def extract_surname_initial(name: str) -> tuple:
    """
    Parse author name and return (surname, first_initial) tuple.
    Returns (None, None) if can't parse.
    
    Handles formats:
    - "Wang, YH"     -> ("Wang", "Y")
    - "Wang Y.H."    -> ("Wang", "Y")
    - "Wang Y.-H."   -> ("Wang", "Y")
    - "Wang YH"      -> ("Wang", "Y")
    - "Yong Wang"    -> ("Wang", "Y")  [single space, no comma]
    - "Li, Y.-L."    -> ("Li", "Y")
    - "Van der Berg, P." -> ("Van der Berg", "P")
    """
    if not name or not isinstance(name, str):
        return (None, None)
    
    name = name.strip()
    if not name:
        return (None, None)
    
    # Strip trailing period
    name = name.rstrip(".").strip()
    
    # CASE 1: "Surname, FirstInitial(s)" or "Surname, FirstName"
    if "," in name:
        parts = [p.strip() for p in name.split(",", 1)]
        if len(parts) == 2:
            surname, given = parts
            if surname and given:
                # Get first letter of given name (skip hyphens/dots/spaces)
                given_clean = re.sub(r"[.\-\s]+", "", given)
                if given_clean:
                    return (surname, given_clean[0].upper())
    
    # CASE 2: "Surname FI" or "Surname F.I." (Scopus style, no comma)
    # Try to detect: last token looks like initials (1-3 chars, mostly uppercase)
    tokens = name.split()
    if len(tokens) >= 2:
        last_token = tokens[-1].rstrip(".")
        # Check if last token looks like initials: short, possibly with periods/hyphens
        cleaned = re.sub(r"[.\-]", "", last_token)
        if len(cleaned) <= 3 and cleaned.isalpha() and (cleaned.isupper() or len(cleaned) == 1):
            # Treat as initials — surname is everything before
            surname = " ".join(tokens[:-1])
            return (surname, cleaned[0].upper())
        
        # CASE 3: "Yong Wang" — first token is given name, last is surname (OpenAlex style)
        # Heuristic: if first token is >1 char and not all uppercase, treat as full given name
        first_token = tokens[0]
        if len(first_token) > 1 and not first_token.isupper():
            surname = tokens[-1]
            first_initial = first_token[0].upper()
            return (surname, first_initial)
    
    # CASE 4: Single-token name (no first name) — can't generate FINI
    return (None, None)


def make_fini(surname: str, first_initial: str) -> str:
    """Build FINI ID: lowercase, underscore-separated."""
    if not surname or not first_initial:
        return None
    s = surname.lower().strip()
    # Collapse internal whitespace + remove non-alphanumeric (except space/hyphen)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z\-\s]", "", s)
    s = s.strip().replace(" ", "_").replace("-", "_")
    if not s:
        return None
    return f"{s}_{first_initial.lower()}"


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3B.1: Author normalization (FINI)")
    print("=" * 70)
    
    # Load main + partial
    print("\n[1] Loading corpus...")
    df_main = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    df_partial = pd.read_parquet(repo_root / "data/processed/integrated_corpus_partial2026.parquet")
    df = pd.concat([df_main, df_partial], ignore_index=True)
    print(f"    Combined: {len(df):,} records")
    
    # Process all authors
    print("\n[2] Parsing author names...")
    
    author_records = []  # list of (record_id, fini_id, position, original_name)
    parse_failures = []  # names we couldn't parse
    
    for _, row in df.iterrows():
        rid = row["record_id"]
        authors = row.get("authors")
        if authors is None:
            continue
        try:
            au_list = list(authors)
        except (TypeError, ValueError):
            continue
        
        for pos, au in enumerate(au_list, start=1):
            if not au or not isinstance(au, str):
                continue
            surname, init = extract_surname_initial(au)
            fini = make_fini(surname, init) if surname and init else None
            
            if fini:
                author_records.append({
                    "record_id": rid,
                    "fini_id": fini,
                    "position": pos,
                    "original_name": au,
                    "surname": surname,
                })
            else:
                parse_failures.append(au)
    
    print(f"    Total author-paper pairs:  {len(author_records):,}")
    print(f"    Parse failures:            {len(parse_failures):,}")
    if parse_failures:
        sample = list(set(parse_failures))[:5]
        print(f"    Sample failures: {sample}")
    
    # Build maps
    print("\n[3] Building lookup tables...")
    
    ar_df = pd.DataFrame(author_records)
    
    # Map: fini -> stats
    fini_stats = {}
    for fini, group in ar_df.groupby("fini_id"):
        name_variants = group["original_name"].value_counts().to_dict()
        canonical = max(name_variants, key=name_variants.get)  # most common variant
        record_ids = group["record_id"].unique().tolist()
        first_authors = (group["position"] == 1).sum()
        
        fini_stats[fini] = {
            "fini_id": fini,
            "canonical_name": canonical,
            "n_records": len(record_ids),
            "first_author_count": int(first_authors),
            "n_name_variants": len(name_variants),
            "name_variants_top3": "; ".join([f"{n}({c})" for n, c in 
                                              sorted(name_variants.items(), key=lambda x: -x[1])[:3]]),
            "sample_record_ids": "|".join(record_ids[:5]),
        }
    
    author_df = pd.DataFrame(fini_stats.values()).sort_values("n_records", ascending=False).reset_index(drop=True)
    
    # Stats
    print(f"\n[4] Author normalization results:")
    print(f"    Total unique FINIs:           {len(author_df):,}")
    print(f"    Authors with >=2 papers:      {(author_df['n_records'] >= 2).sum():,}")
    print(f"    Authors with >=5 papers:      {(author_df['n_records'] >= 5).sum():,}")
    print(f"    Authors with >=10 papers:     {(author_df['n_records'] >= 10).sum():,}")
    print(f"    Authors with >=20 papers:     {(author_df['n_records'] >= 20).sum():,}")
    
    # Top 30 preview
    print(f"\n[5] Top 30 most prolific authors (by total paper count):")
    print(f"    {'Rank':<5s} {'FINI':<25s} {'Name':<30s} {'NPub':>5s} {'1st':>5s} {'Variants':>9s}")
    for i, row in author_df.head(30).iterrows():
        print(f"    {i+1:<5} {row['fini_id'][:24]:<25s} {row['canonical_name'][:29]:<30s} "
              f"{int(row['n_records']):>5,} {int(row['first_author_count']):>5,} "
              f"{int(row['n_name_variants']):>9}")
    
    # Save outputs
    out_dir = repo_root / "data" / "processed"
    
    author_path = out_dir / "author_lookup.parquet"
    author_df.to_parquet(author_path, index=False, engine="pyarrow")
    
    map_path = out_dir / "author_record_map.parquet"
    ar_df[["record_id", "fini_id", "position"]].to_parquet(map_path, index=False, engine="pyarrow")
    
    print(f"\n[6] Outputs saved:")
    print(f"    {author_path}  ({len(author_df):,} unique FINIs)")
    print(f"    {map_path}     ({len(ar_df):,} author-record links)")
    
    # FINI ambiguity warning (Chinese surname issue)
    print(f"\n[7] FINI ambiguity warning:")
    common_cn_surnames = ["wang", "li", "zhang", "liu", "chen", "yang", "wu", "huang", "zhou", "lin"]
    for sn in common_cn_surnames:
        match = author_df[author_df["fini_id"].str.startswith(sn + "_")]
        if len(match) > 0:
            top_fini = match.iloc[0]
            print(f"    {sn}: {len(match)} unique FINIs, top: {top_fini['fini_id']} (n={int(top_fini['n_records'])} papers, {int(top_fini['n_name_variants'])} name variants)")
    
    print("\n" + "=" * 70)
    print("DONE: author_lookup.parquet ready for Block 3B.2 ranking")
    print("=" * 70)


if __name__ == "__main__":
    main()
