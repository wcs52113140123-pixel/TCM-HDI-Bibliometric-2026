"""
Scopus CSV loader.
Reads Scopus "Download CSV" export and normalizes to unified schema.

Usage as module:
    from load_scopus import load_all_scopus
    records = load_all_scopus(repo_root, partial_2026=False)

Usage as script (test mode):
    python 02_data_integration/load_scopus.py
"""

import pandas as pd
from pathlib import Path


def normalize_scopus_record(row):
    """Convert one Scopus CSV row to standardized schema."""
    # DOI
    doi = str(row.get("DOI", "") or "").strip().lower()
    if doi and doi != "nan":
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    else:
        doi = None
    
    # Year
    year_raw = row.get("Year", None)
    year = None
    if pd.notna(year_raw):
        try:
            year = int(year_raw)
        except (ValueError, TypeError):
            pass
    
    # Authors — Scopus Download CSV uses "; " (semicolon+space) as separator.
    # Format example: "Liu K.; Xu Z.; Zhang J." (each name is "LastName Initials").
    # Older Scopus "Export by page" CSV may use ", " — fall back to comma if no semicolon.
    au_raw = str(row.get("Authors", "") or "").strip()
    if not au_raw or au_raw == "nan":
        authors = []
    elif ";" in au_raw:
        authors = [a.strip() for a in au_raw.split(";") if a.strip()]
    else:
        # Fallback: comma-separated (legacy format)
        authors = [a.strip() for a in au_raw.split(",") if a.strip()]
    
    first_author_lastname = ""
    if authors:
        first = authors[0]
        parts = first.split()
        if parts:
            first_author_lastname = parts[0]
    
    # Title / Abstract / Journal — clean nan strings
    def clean_str(val):
        s = str(val or "").strip()
        return "" if s == "nan" else s
    
    title = clean_str(row.get("Title", ""))
    abstract = clean_str(row.get("Abstract", ""))
    if abstract == "[No abstract available]":
        abstract = ""
    journal = clean_str(row.get("Source title", ""))
    lang = clean_str(row.get("Language of Original Document", ""))
    source_id = clean_str(row.get("EID", ""))
    
    # Doc type
    dt_raw = clean_str(row.get("Document Type", ""))
    if "Article" in dt_raw:
        doc_type = "Article"
    elif "Review" in dt_raw:
        doc_type = "Review"
    else:
        doc_type = dt_raw if dt_raw else "Unknown"
    
    # Cited by
    cb_raw = row.get("Cited by", None)
    cited_by = None
    if pd.notna(cb_raw):
        try:
            cited_by = int(cb_raw)
        except (ValueError, TypeError):
            pass
    
    # References count (Scopus separator: semicolon)
    refs_raw = clean_str(row.get("References", ""))
    references_count = (refs_raw.count(";") + 1) if refs_raw else None
    
    # Keywords
    ak = clean_str(row.get("Author Keywords", ""))
    author_keywords = [k.strip() for k in ak.split(";") if k.strip()] if ak else []
    
    ik = clean_str(row.get("Index Keywords", ""))
    keywords_plus = [k.strip() for k in ik.split(";") if k.strip()] if ik else []
    
    return {
        "source_db": "Scopus",
        "source_id": source_id,
        "doi": doi,
        "title": title,
        "year": year,
        "authors": authors,
        "first_author_lastname": first_author_lastname,
        "journal": journal,
        "abstract": abstract,
        "author_keywords": author_keywords,
        "keywords_plus": keywords_plus,
        "doc_type": doc_type,
        "language": lang,
        "cited_by": cited_by,
        "references_count": references_count,
        "mesh_terms": None,
        "openalex_concepts": None,
        # === New affiliation fields (Day 3 patch) ===
        "affiliations_raw": clean_str(row.get("Affiliations", "")),
        "reprint_address": clean_str(row.get("Correspondence Address", "")),
        "institutions_list": [],
    }


def load_all_scopus(repo_root, partial_2026=False):
    """Load all Scopus CSV file(s)."""
    if partial_2026:
        path = repo_root / "data" / "raw" / "scopus_partial2026" / "scopus_partial2026_all.csv"
    else:
        path = repo_root / "data" / "raw" / "scopus" / "scopus_all_7181.csv"
    
    if not path.exists():
        print(f"  WARNING: {path} not found")
        return []
    
    df = pd.read_csv(path, low_memory=False)
    records = [normalize_scopus_record(row) for _, row in df.iterrows()]
    print(f"  Loaded {len(records):,} from {path.name}")
    return records


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent
    
    print("=" * 60)
    print("Scopus Loader - Standalone Test")
    print("=" * 60)
    
    print("\n[1] Loading main analysis...")
    main = load_all_scopus(repo, partial_2026=False)
    print(f"  Total: {len(main):,} (expected 7,181)")
    
    print("\n[2] Loading partial 2026...")
    partial = load_all_scopus(repo, partial_2026=True)
    print(f"  Total: {len(partial):,} (expected 230)")
    
    # Field coverage
    print("\n[3] Field coverage (main):")
    n = len(main)
    print(f"  DOI:      {sum(1 for r in main if r['doi']):>5,}/{n:,} ({100*sum(1 for r in main if r['doi'])/n:.1f}%)")
    print(f"  Year:     {sum(1 for r in main if r['year']):>5,}/{n:,}")
    print(f"  Abstract: {sum(1 for r in main if r['abstract']):>5,}/{n:,}")
    print(f"  Author:   {sum(1 for r in main if r['first_author_lastname']):>5,}/{n:,}")
    print(f"  Cited:    {sum(1 for r in main if r['cited_by'] is not None):>5,}/{n:,}")
    print(f"  Refs#:    {sum(1 for r in main if r['references_count']):>5,}/{n:,}")
    
    # Doc type
    print("\n[4] Document type distribution:")
    from collections import Counter
    for dt, c in Counter(r["doc_type"] for r in main).most_common():
        print(f"  {dt:20s} {c:>5,}")
    
    # Sample
    print("\n[5] Random sample:")
    import random
    random.seed(42)
    for i, rec in enumerate(random.sample(main, 2), 1):
        print(f"\n  --- Sample {i} ---")
        print(f"  Title:  {rec['title'][:90]}")
        print(f"  Year:   {rec['year']}  DOI: {rec['doi']}")
        print(f"  Author: {rec['first_author_lastname']} ({len(rec['authors'])} total)")
        print(f"  Type:   {rec['doc_type']}  Cited: {rec['cited_by']}  Refs: {rec['references_count']}")
    
    print("\n[6] DONE.")

