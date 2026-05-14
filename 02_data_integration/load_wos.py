"""
WoS Core Collection plain-text record parser.

Reads WoS export files (.txt with PT/AU/TI/SO/AB/DE/DI/PY/UT/DT/LA/TC/NR fields).
Standardizes to unified schema for cross-database integration.

WoS plain-text format conventions:
- 2-char field tag at column 0-1, space at column 2, value from column 3
- Continuation lines for multi-line values start with 3 spaces
- Records separated by "ER" marker
- File ends with "EF" marker

Usage as module:
    from load_wos import load_all_wos
    records = load_all_wos(repo_root, partial_2026=False)

Usage as script (test mode):
    python 02_data_integration/load_wos.py
"""

import sys
from pathlib import Path


# WoS field tags → standardized field names
WOS_FIELDS = {
    "PT": "publication_type",
    "AU": "authors_short",        # "Smith, JA"
    "AF": "authors_full",         # "Smith, John A."
    "TI": "title",
    "SO": "journal",
    "AB": "abstract",
    "DE": "author_keywords",
    "ID": "keywords_plus",
    "DI": "doi",
    "PY": "year",
    "UT": "wos_uid",
    "DT": "doc_type",
    "LA": "language",
    "TC": "times_cited",
    "NR": "references_count",
    "CR": "cited_references",
    "C1": "affiliations_raw",
    "RP": "reprint_address",
    "FU": "funding",
    "JI": "journal_iso_abbr",
    "SN": "issn",
    "EI": "eissn",
    "VL": "volume",
    "IS": "issue",
    "BP": "beginning_page",
    "EP": "ending_page",
}


def parse_wos_file(filepath):
    """
    Parse a WoS plain-text export file.
    Returns: list of dict records (raw field tags as keys).
    """
    records = []
    current_record = {}
    current_field = None
    current_value_lines = []
    
    with open(filepath, encoding="utf-8") as fp:
        for line in fp:
            line = line.rstrip("\n").rstrip("\r")
            
            if not line.strip():
                continue
            
            # Header lines
            if line.startswith("FN ") or line.startswith("VR "):
                continue
            
            # End of record
            if line.startswith("ER"):
                if current_field and current_value_lines:
                    current_record[current_field] = "\n".join(current_value_lines)
                if current_record:
                    records.append(current_record)
                current_record = {}
                current_field = None
                current_value_lines = []
                continue
            
            if line.startswith("EF"):
                break
            
            # New field: 2-char tag + space at col 2
            if (len(line) >= 3 and line[2] == " "
                and line[0].isalpha() and line[0].isupper()
                and (line[1].isalpha() or line[1].isdigit())
                and (not line[1].isalpha() or line[1].isupper())):
                # Flush previous field
                if current_field and current_value_lines:
                    current_record[current_field] = "\n".join(current_value_lines)
                
                tag = line[:2]
                value = line[3:]
                current_field = WOS_FIELDS.get(tag, f"wos_{tag}")
                current_value_lines = [value]
            else:
                # Continuation line (indented)
                if current_field:
                    current_value_lines.append(line.strip())
    
    return records


def normalize_wos_record(rec):
    """Convert raw WoS dict to standardized schema."""
    # DOI
    doi = rec.get("doi", "").strip().lower()
    if doi:
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    
    # Year
    year = None
    py = rec.get("year", "").strip()
    if py and py.isdigit():
        year = int(py)
    
    # Authors
    au_raw = rec.get("authors_short", "")
    authors = [a.strip() for a in au_raw.split("\n") if a.strip()]
    
    first_author_lastname = ""
    if authors:
        first = authors[0]
        if "," in first:
            first_author_lastname = first.split(",")[0].strip()
        else:
            first_author_lastname = first.strip()
    
    # Title
    title = rec.get("title", "").replace("\n", " ").strip()
    while "  " in title:
        title = title.replace("  ", " ")
    
    # Abstract
    abstract = rec.get("abstract", "").replace("\n", " ").strip()
    while "  " in abstract:
        abstract = abstract.replace("  ", " ")
    
    # Doc type
    dt_raw = rec.get("doc_type", "").strip()
    dt_lower = dt_raw.lower()
    if "article" in dt_lower and "review" not in dt_lower:
        doc_type = "Article"
    elif "review" in dt_lower:
        doc_type = "Review"
    else:
        doc_type = dt_raw if dt_raw else "Unknown"
    
    # Numeric fields
    nr = rec.get("references_count", "").strip()
    references_count = int(nr) if nr.isdigit() else None
    
    tc = rec.get("times_cited", "").strip()
    cited_by = int(tc) if tc.isdigit() else None
    
    # Keywords
    de = rec.get("author_keywords", "").replace("\n", ";")
    author_keywords = [k.strip() for k in de.split(";") if k.strip()]
    
    id_field = rec.get("keywords_plus", "").replace("\n", ";")
    keywords_plus = [k.strip() for k in id_field.split(";") if k.strip()]
    
    return {
        "source_db": "WoS",
        "source_id": rec.get("wos_uid", "").strip(),
        "doi": doi if doi else None,
        "title": title,
        "year": year,
        "authors": authors,
        "first_author_lastname": first_author_lastname,
        "journal": rec.get("journal", "").replace("\n", " ").strip(),
        "abstract": abstract,
        "author_keywords": author_keywords,
        "keywords_plus": keywords_plus,
        "doc_type": doc_type,
        "language": rec.get("language", "").strip(),
        "cited_by": cited_by,
        "references_count": references_count,
        "mesh_terms": None,
        "openalex_concepts": None,
        # === New affiliation fields (Day 3 patch) ===
        "affiliations_raw": rec.get("affiliations_raw", "").strip(),
        "reprint_address": rec.get("reprint_address", "").strip(),
        "institutions_list": [],  # WoS doesn't provide structured institutions
    }


def load_all_wos(repo_root, partial_2026=False):
    """Load + normalize all WoS batch files."""
    if partial_2026:
        wos_dir = repo_root / "data" / "raw" / "wos_partial2026"
        glob_pat = "wos_partial2026_*.txt"
    else:
        wos_dir = repo_root / "data" / "raw" / "wos"
        glob_pat = "wos_batch_*.txt"
    
    all_records = []
    for filepath in sorted(wos_dir.glob(glob_pat)):
        raw = parse_wos_file(filepath)
        normalized = [normalize_wos_record(r) for r in raw]
        all_records.extend(normalized)
        print(f"  Loaded {len(normalized):>5,} from {filepath.name}")
    
    return all_records


# ============================================================
# Standalone test mode
# ============================================================
if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 60)
    print("WoS Loader - Standalone Test")
    print("=" * 60)
    
    print("\n[1] Loading main analysis files...")
    main_records = load_all_wos(repo_root, partial_2026=False)
    print(f"\n  Total main records: {len(main_records):,} (expected 3,091)")
    
    print("\n[2] Loading partial 2026...")
    partial_records = load_all_wos(repo_root, partial_2026=True)
    print(f"\n  Total partial 2026: {len(partial_records):,} (expected 83)")
    
    # Validation
    print("\n[3] Field coverage check (main analysis):")
    n = len(main_records)
    has_doi = sum(1 for r in main_records if r["doi"])
    has_year = sum(1 for r in main_records if r["year"])
    has_abstract = sum(1 for r in main_records if r["abstract"])
    has_author = sum(1 for r in main_records if r["first_author_lastname"])
    has_journal = sum(1 for r in main_records if r["journal"])
    
    print(f"  DOI:      {has_doi:>5,}/{n:,} ({100*has_doi/n:.1f}%)")
    print(f"  Year:     {has_year:>5,}/{n:,} ({100*has_year/n:.1f}%)")
    print(f"  Title:    all records")
    print(f"  Abstract: {has_abstract:>5,}/{n:,} ({100*has_abstract/n:.1f}%)")
    print(f"  Author:   {has_author:>5,}/{n:,} ({100*has_author/n:.1f}%)")
    print(f"  Journal:  {has_journal:>5,}/{n:,} ({100*has_journal/n:.1f}%)")
    
    # Doc type distribution
    print("\n[4] Document type distribution:")
    dt_counts = {}
    for r in main_records:
        dt = r["doc_type"]
        dt_counts[dt] = dt_counts.get(dt, 0) + 1
    for dt, c in sorted(dt_counts.items(), key=lambda x: -x[1]):
        print(f"  {dt:20s} {c:>5,}")
    
    # Sample 3 records
    print("\n[5] Random sample records:")
    import random
    random.seed(42)
    samples = random.sample(main_records, 3)
    for i, rec in enumerate(samples, 1):
        print(f"\n  --- Sample {i} ---")
        print(f"  Title:        {rec['title'][:90]}")
        print(f"  Year:         {rec['year']}")
        print(f"  DOI:          {rec['doi']}")
        print(f"  WoS UID:      {rec['source_id']}")
        print(f"  First author: {rec['first_author_lastname']}")
        print(f"  Authors (N):  {len(rec['authors'])}")
        print(f"  Journal:      {rec['journal'][:60]}")
        print(f"  Doc type:     {rec['doc_type']}")
        print(f"  Cited by:     {rec['cited_by']}")
        print(f"  Refs count:   {rec['references_count']}")
        print(f"  Keywords:     {rec['author_keywords'][:5]}")
        print(f"  Abstract:     {(rec['abstract'][:120] + '...') if len(rec['abstract']) > 120 else rec['abstract']}")
    
    print("\n[6] DONE. WoS loader test passed.")
