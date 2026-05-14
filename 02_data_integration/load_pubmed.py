"""
PubMed JSONL loader.
Reads our pre-normalized PubMed JSONL (from Day 1 Step 5).
"""

import json
from pathlib import Path


def normalize_pubmed_record(rec):
    """Adapt our PubMed record to standardized schema."""
    # DOI
    doi = (rec.get("doi") or "").lower().strip()
    doi = doi if doi else None
    
    # First author
    authors = rec.get("authors", []) or []
    first_author_lastname = ""
    if authors:
        # Our format: "Smith J" or "Smith JA"
        parts = authors[0].split()
        if parts:
            first_author_lastname = parts[0]
    
    # Doc type from publication_types list
    pubtypes = rec.get("publication_types", []) or []
    doc_type = "Unknown"
    pt_lower = [p.lower() for p in pubtypes]
    if any("review" in p for p in pt_lower):
        doc_type = "Review"
    elif any("journal article" in p for p in pt_lower):
        doc_type = "Article"
    elif pubtypes:
        doc_type = pubtypes[0]
    
    # Language (list -> first)
    langs = rec.get("language", []) or []
    language = langs[0] if langs else ""
    
    return {
        "source_db": "PubMed",
        "source_id": rec.get("pmid", ""),
        "doi": doi,
        "title": (rec.get("title") or "").strip(),
        "year": rec.get("year"),
        "authors": authors,
        "first_author_lastname": first_author_lastname,
        "journal": (rec.get("journal") or "").strip(),
        "abstract": (rec.get("abstract") or "").strip(),
        "author_keywords": [],
        "keywords_plus": [],
        "doc_type": doc_type,
        "language": language,
        "cited_by": None,
        "references_count": None,
        "mesh_terms": rec.get("mesh_terms", []) or [],
        "openalex_concepts": None,
    }


def load_all_pubmed(repo_root, partial_2026=False):
    """Load all PubMed JSONL."""
    if partial_2026:
        path = repo_root / "data" / "raw" / "pubmed_partial2026" / "pubmed_partial2026_records.jsonl"
    else:
        path = repo_root / "data" / "raw" / "pubmed" / "pubmed_records.jsonl"
    
    if not path.exists():
        print(f"  WARNING: {path} not found")
        return []
    
    records = []
    with open(path, encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(normalize_pubmed_record(rec))
            except Exception as e:
                print(f"  WARN parse error: {e}")
    
    print(f"  Loaded {len(records):,} from {path.name}")
    return records


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent
    
    print("=" * 60)
    print("PubMed Loader - Standalone Test")
    print("=" * 60)
    
    print("\n[1] Main:")
    main = load_all_pubmed(repo, partial_2026=False)
    print(f"  Total: {len(main):,} (expected 3,867)")
    
    print("\n[2] Partial 2026:")
    partial = load_all_pubmed(repo, partial_2026=True)
    print(f"  Total: {len(partial):,} (expected 106)")
    
    print("\n[3] Field coverage (main):")
    n = len(main)
    print(f"  DOI:      {sum(1 for r in main if r['doi']):>5,}/{n:,} ({100*sum(1 for r in main if r['doi'])/n:.1f}%)")
    print(f"  Year:     {sum(1 for r in main if r['year']):>5,}/{n:,}")
    print(f"  Abstract: {sum(1 for r in main if r['abstract']):>5,}/{n:,}")
    print(f"  Author:   {sum(1 for r in main if r['first_author_lastname']):>5,}/{n:,}")
    print(f"  MeSH:     {sum(1 for r in main if r['mesh_terms']):>5,}/{n:,}")
    
    print("\n[4] Doc type distribution:")
    from collections import Counter
    for dt, c in Counter(r["doc_type"] for r in main).most_common():
        print(f"  {dt:20s} {c:>5,}")
    
    print("\n[5] Sample:")
    import random
    random.seed(42)
    for i, rec in enumerate(random.sample(main, 2), 1):
        print(f"\n  --- Sample {i} ---")
        print(f"  PMID:   {rec['source_id']}  Year: {rec['year']}")
        print(f"  Title:  {rec['title'][:90]}")
        print(f"  DOI:    {rec['doi']}")
        print(f"  Author: {rec['first_author_lastname']} ({len(rec['authors'])} total)")
        print(f"  Type:   {rec['doc_type']}")
        print(f"  MeSH:   {rec['mesh_terms'][:5]}")
    
    print("\n[6] DONE.")
