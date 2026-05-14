"""
OpenAlex JSONL loader.
Reads OpenAlex Works JSONL, reconstructs abstract from inverted index.
"""

import json
from pathlib import Path


def reconstruct_abstract(inverted_index):
    """Reconstruct abstract text from OpenAlex inverted index."""
    if not inverted_index:
        return ""
    word_pos = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_pos.append((pos, word))
    word_pos.sort()
    return " ".join(w for _, w in word_pos)


def normalize_openalex_record(work):
    """Convert one OpenAlex Work to standardized schema."""
    # source_id
    source_id = (work.get("id") or "").replace("https://openalex.org/", "")
    
    # DOI
    doi = work.get("doi") or ""
    if doi:
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").lower().strip()
    doi = doi if doi else None
    
    # Title
    title = (work.get("title") or work.get("display_name") or "").strip()
    
    # Year
    year = work.get("publication_year")
    
    # Authors
    authorships = work.get("authorships", []) or []
    authors = []
    for au in authorships:
        author_obj = au.get("author") or {}
        display = author_obj.get("display_name", "")
        if display:
            authors.append(display)
    
    first_author_lastname = ""
    if authors:
        # OpenAlex display format: "First Middle Last"
        parts = authors[0].split()
        if parts:
            first_author_lastname = parts[-1]
    
    # Abstract (reconstruct)
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    
    # Journal
    primary = work.get("primary_location") or {}
    source_obj = primary.get("source") or {}
    journal = (source_obj.get("display_name") or "").strip()
    
    # Doc type
    type_raw = (work.get("type") or "").strip()
    if "article" in type_raw.lower() and "review" not in type_raw.lower():
        doc_type = "Article"
    elif "review" in type_raw.lower():
        doc_type = "Review"
    else:
        doc_type = type_raw.title() if type_raw else "Unknown"
    
    # Cited / refs
    cited_by = work.get("cited_by_count")
    refs = work.get("referenced_works") or []
    references_count = len(refs) if refs else None
    
    # OpenAlex concepts (unique field)
    concepts_raw = work.get("concepts") or []
    openalex_concepts = [c.get("display_name", "") for c in concepts_raw if c.get("display_name")]
    
    return {
        "source_db": "OpenAlex",
        "source_id": source_id,
        "doi": doi,
        "title": title,
        "year": year,
        "authors": authors,
        "first_author_lastname": first_author_lastname,
        "journal": journal,
        "abstract": abstract,
        "author_keywords": [],
        "keywords_plus": [],
        "doc_type": doc_type,
        "language": work.get("language") or "",
        "cited_by": cited_by,
        "references_count": references_count,
        "mesh_terms": None,
        "openalex_concepts": openalex_concepts,
    }


def load_all_openalex(repo_root, partial_2026=False):
    """Load all OpenAlex JSONL."""
    if partial_2026:
        path = repo_root / "data" / "raw" / "openalex_partial2026" / "openalex_partial2026_candidates.jsonl"
    else:
        path = repo_root / "data" / "raw" / "openalex" / "openalex_candidates.jsonl"
    
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
                work = json.loads(line)
                records.append(normalize_openalex_record(work))
            except Exception as e:
                print(f"  WARN parse error: {e}")
    
    print(f"  Loaded {len(records):,} from {path.name}")
    return records


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent
    
    print("=" * 60)
    print("OpenAlex Loader - Standalone Test")
    print("=" * 60)
    
    print("\n[1] Main:")
    main = load_all_openalex(repo, partial_2026=False)
    print(f"  Total: {len(main):,} (expected 2,513)")
    
    print("\n[2] Partial 2026:")
    partial = load_all_openalex(repo, partial_2026=True)
    print(f"  Total: {len(partial):,} (expected 95)")
    
    print("\n[3] Field coverage (main):")
    n = len(main)
    print(f"  DOI:      {sum(1 for r in main if r['doi']):>5,}/{n:,} ({100*sum(1 for r in main if r['doi'])/n:.1f}%)")
    print(f"  Year:     {sum(1 for r in main if r['year']):>5,}/{n:,}")
    print(f"  Abstract: {sum(1 for r in main if r['abstract']):>5,}/{n:,}")
    print(f"  Author:   {sum(1 for r in main if r['first_author_lastname']):>5,}/{n:,}")
    print(f"  Concepts: {sum(1 for r in main if r['openalex_concepts']):>5,}/{n:,}")
    print(f"  Refs#:    {sum(1 for r in main if r['references_count']):>5,}/{n:,}")
    
    print("\n[4] Doc type distribution:")
    from collections import Counter
    for dt, c in Counter(r["doc_type"] for r in main).most_common():
        print(f"  {dt:20s} {c:>5,}")
    
    print("\n[5] Sample:")
    import random
    random.seed(42)
    for i, rec in enumerate(random.sample(main, 2), 1):
        print(f"\n  --- Sample {i} ---")
        print(f"  Title:    {rec['title'][:90]}")
        print(f"  Year:     {rec['year']}  DOI: {rec['doi']}")
        print(f"  Author:   {rec['first_author_lastname']} ({len(rec['authors'])} total)")
        print(f"  Type:     {rec['doc_type']}")
        print(f"  Concepts: {rec['openalex_concepts'][:3]}")
    
    print("\n[6] DONE.")
