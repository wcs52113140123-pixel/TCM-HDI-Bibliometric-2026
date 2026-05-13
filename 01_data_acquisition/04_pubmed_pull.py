"""
Pull TCM herb-drug interaction publications from PubMed via NCBI E-utilities.

Uses Biopython Entrez with NCBI_EMAIL and NCBI_API_KEY from .env.

PubMed 2026 syntax notes:
- Field tags: [TIAB], [MH], [MeSH], [PT], [LA], [PDAT] (case-insensitive)
- Boolean operators (AND, OR, NOT) must be UPPERCASE
- MeSH headings (post-2004): "Herb-Drug Interactions" exists as MeSH

Strategy:
- ESearch with TCM-HDI query (TIAB + MeSH hybrid)
- EFetch in batches of 200 (PubMed-recommended)
- Parse MEDLINE XML; extract MeSH terms (PubMed's unique strength)
- Save as JSONL

Output:
- data/raw/pubmed/pubmed_records.jsonl
- data/raw/pubmed/pubmed_pull_log.json

Usage:
    conda activate tcm-hdi
    python 01_data_acquisition/04_pubmed_pull.py
    python 01_data_acquisition/04_pubmed_pull.py --partial-2026
    python 01_data_acquisition/04_pubmed_pull.py --count-only   # just get N
"""

import json
import sys
import time
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
repo_root = Path(__file__).resolve().parent.parent
load_dotenv(repo_root / ".env")

from Bio import Entrez

NCBI_EMAIL = os.getenv("NCBI_EMAIL", "").strip()
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "").strip() or None

if not NCBI_EMAIL or "example.com" in NCBI_EMAIL:
    print("ERROR: Set NCBI_EMAIL in .env to a real email address")
    sys.exit(1)

Entrez.email = NCBI_EMAIL
if NCBI_API_KEY:
    Entrez.api_key = NCBI_API_KEY
    rate_limit = 10
    print(f"NCBI E-utilities: email + API key (rate limit 10/sec)")
else:
    rate_limit = 3
    print(f"NCBI E-utilities: email only (rate limit 3/sec)")


# ============ Mode ============
PARTIAL_2026 = "--partial-2026" in sys.argv
COUNT_ONLY = "--count-only" in sys.argv

if PARTIAL_2026:
    YEAR_TERM = "2026/01/01:2026/12/31[PDAT]"
    OUT_DIR = repo_root / "data" / "raw" / "pubmed_partial2026"
    OUT_JSONL = OUT_DIR / "pubmed_partial2026_records.jsonl"
    OUT_LOG = OUT_DIR / "pubmed_partial2026_pull_log.json"
    LABEL = "PARTIAL 2026"
else:
    YEAR_TERM = "2005/01/01:2025/12/31[PDAT]"
    OUT_DIR = repo_root / "data" / "raw" / "pubmed"
    OUT_JSONL = OUT_DIR / "pubmed_records.jsonl"
    OUT_LOG = OUT_DIR / "pubmed_pull_log.json"
    LABEL = "MAIN 2005-2025"

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ============ PubMed Query (verified 2026 syntax) ============
# Combines TIAB keywords + MeSH headings for maximum recall
# All MeSH headings verified to exist in PubMed MeSH tree

QUERY = """(
    "herb-drug interaction"[TIAB]
    OR "herb-drug interactions"[TIAB]
    OR "herb drug interaction"[TIAB]
    OR "herb drug interactions"[TIAB]
    OR "herbal drug interaction"[TIAB]
    OR "herbal drug interactions"[TIAB]
    OR "Herb-Drug Interactions"[MH]
    OR (
        (
            "traditional Chinese medicine"[TIAB]
            OR "Chinese herbal medicine"[TIAB]
            OR "Chinese herbal"[TIAB]
            OR "TCM"[TIAB]
            OR "Medicine, Chinese Traditional"[MH]
            OR "Drugs, Chinese Herbal"[MH]
        )
        AND (
            "drug interaction"[TIAB]
            OR "drug interactions"[TIAB]
            OR "pharmacokinetic interaction"[TIAB]
            OR "pharmacodynamic interaction"[TIAB]
            OR "Drug Interactions"[MH]
        )
    )
    OR (
        (
            "traditional Chinese medicine"[TIAB]
            OR "Chinese herbal medicine"[TIAB]
            OR "Medicine, Chinese Traditional"[MH]
            OR "Drugs, Chinese Herbal"[MH]
        )
        AND (
            "CYP3A4"[TIAB]
            OR "CYP2D6"[TIAB]
            OR "CYP1A2"[TIAB]
            OR "CYP2C9"[TIAB]
            OR "CYP2C19"[TIAB]
            OR "cytochrome P450"[TIAB]
            OR "P-glycoprotein"[TIAB]
            OR "P-gp"[TIAB]
            OR "Cytochrome P-450 Enzyme System"[MH]
            OR "drug metabolism"[TIAB]
            OR "drug transporter"[TIAB]
            OR "drug transporters"[TIAB]
        )
    )
)
AND """ + YEAR_TERM + """
AND english[LA]
AND ("journal article"[PT] OR "review"[PT])
NOT ("comment"[PT] OR "editorial"[PT] OR "letter"[PT])"""

QUERY_FLAT = " ".join(QUERY.split())

print(f"\n{'='*70}")
print(f"PubMed pull: {LABEL}")
print(f"Year filter: {YEAR_TERM}")
print(f"{'='*70}\n")

# ============ Step 1: ESearch — get count + PMIDs ============
print("Step 1: ESearch — getting matching count + PMIDs...")
start_time = time.time()

try:
    handle = Entrez.esearch(db="pubmed", term=QUERY_FLAT, retmax=0)
    res = Entrez.read(handle)
    handle.close()
    total_count = int(res["Count"])
    print(f"  PubMed reports {total_count:,} matching records")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

if COUNT_ONLY:
    print(f"\n--count-only specified. Exiting.")
    sys.exit(0)

if total_count == 0:
    print("ERROR: PubMed returned 0 records. Check query syntax.")
    sys.exit(1)

# Now fetch all PMIDs (paginate if > 9999)
print(f"  Fetching all {total_count:,} PMIDs...")
all_pmids = []
retstart = 0
batch_pmid = 9999  # PubMed esearch max per request

while retstart < total_count:
    try:
        handle = Entrez.esearch(
            db="pubmed",
            term=QUERY_FLAT,
            retmax=batch_pmid,
            retstart=retstart,
        )
        res = Entrez.read(handle)
        handle.close()
        all_pmids.extend(res["IdList"])
        retstart += batch_pmid
        time.sleep(1.0 / rate_limit)
    except Exception as e:
        print(f"  ERROR retrieving PMIDs at retstart={retstart}: {e}")
        break

print(f"  Retrieved {len(all_pmids):,} PMIDs (expected {total_count:,})")

# ============ Step 2: EFetch in batches; parse MEDLINE XML ============
print(f"\nStep 2: EFetch — downloading full MEDLINE XML...")

records = []
batch_size = 200
n_errors = 0

for batch_start in range(0, len(all_pmids), batch_size):
    batch_pmids = all_pmids[batch_start:batch_start + batch_size]
    
    try:
        handle = Entrez.efetch(
            db="pubmed",
            id=",".join(batch_pmids),
            rettype="medline",
            retmode="xml",
        )
        data = Entrez.read(handle)
        handle.close()
        
        for article in data.get("PubmedArticle", []):
            try:
                mc = article["MedlineCitation"]
                ad = mc["Article"]
                
                rec = {
                    "pmid": str(mc.get("PMID", "")),
                    "title": str(ad.get("ArticleTitle", "")),
                    "year": None,
                    "journal": str(ad["Journal"]["Title"]) if "Journal" in ad else "",
                    "abstract": "",
                    "authors": [],
                    "mesh_terms": [],
                    "doi": None,
                    "language": [],
                    "publication_types": [],
                }
                
                # Year
                pub_date = ad.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                if "Year" in pub_date:
                    try: rec["year"] = int(str(pub_date["Year"]))
                    except (ValueError, TypeError): pass
                elif "MedlineDate" in pub_date:
                    md = str(pub_date["MedlineDate"])
                    if md and md[:4].isdigit():
                        rec["year"] = int(md[:4])
                
                # Abstract
                abs_block = ad.get("Abstract", {})
                if "AbstractText" in abs_block:
                    parts = abs_block["AbstractText"]
                    if isinstance(parts, list):
                        rec["abstract"] = " ".join(str(a) for a in parts)
                    else:
                        rec["abstract"] = str(parts)
                
                # Authors
                for au in ad.get("AuthorList", []):
                    last = au.get("LastName", "")
                    initials = au.get("Initials", "")
                    if last:
                        rec["authors"].append(f"{last} {initials}".strip())
                
                # MeSH (PubMed's superpower)
                for mh in mc.get("MeshHeadingList", []):
                    descriptor = mh.get("DescriptorName", "")
                    if descriptor:
                        rec["mesh_terms"].append(str(descriptor))
                
                # DOI
                for eloc in ad.get("ELocationID", []):
                    if eloc.attributes.get("EIdType") == "doi":
                        rec["doi"] = str(eloc)
                        break
                
                # Language
                for lang in ad.get("Language", []):
                    rec["language"].append(str(lang))
                
                # Pub types
                for pt in ad.get("PublicationTypeList", []):
                    rec["publication_types"].append(str(pt))
                
                records.append(rec)
            except Exception as e:
                n_errors += 1
                continue
        
        elapsed = time.time() - start_time
        n_done = batch_start + len(batch_pmids)
        rate = n_done / max(elapsed, 1)
        eta_sec = (len(all_pmids) - n_done) / max(rate, 1)
        print(f"  batch {batch_start//batch_size + 1:>3d}: "
              f"{n_done:>5,}/{len(all_pmids):,} ({100*n_done/len(all_pmids):.0f}%) "
              f"rate={rate:.1f}/s ETA={eta_sec/60:.1f}min")
        
        time.sleep(1.0 / rate_limit)
        
    except Exception as e:
        n_errors += 1
        print(f"  ERROR in batch starting {batch_start}: {e}")
        time.sleep(2)
        continue

# ============ Save JSONL ============
print(f"\nWriting {len(records):,} records to: {OUT_JSONL.name}")
with open(OUT_JSONL, "w", encoding="utf-8") as fp:
    for rec in records:
        json.dump(rec, fp, ensure_ascii=False)
        fp.write("\n")

elapsed_total = time.time() - start_time
file_size_mb = OUT_JSONL.stat().st_size / 1024 / 1024

log = {
    "label": LABEL,
    "search_date": datetime.now().isoformat(),
    "year_filter": YEAR_TERM,
    "query": QUERY_FLAT,
    "api_reported_total": total_count,
    "pmids_retrieved": len(all_pmids),
    "records_saved": len(records),
    "errors": n_errors,
    "elapsed_sec": round(elapsed_total, 1),
    "output_file": str(OUT_JSONL.relative_to(repo_root)).replace(os.sep, "/"),
    "file_size_mb": round(file_size_mb, 2),
    "rate_limit_used": f"{rate_limit}/sec",
}
with open(OUT_LOG, "w", encoding="utf-8") as fp:
    json.dump(log, fp, indent=2, ensure_ascii=False)

# Summary
print(f"\n{'='*70}\nDONE\n{'='*70}")
print(f"  PubMed reports:  {total_count:,}")
print(f"  PMIDs retrieved: {len(all_pmids):,}")
print(f"  Records saved:   {len(records):,}")
print(f"  Errors:          {n_errors}")
print(f"  Elapsed:         {elapsed_total/60:.1f} min")
print(f"  File size:       {file_size_mb:.1f} MB")
print(f"  Output:          {OUT_JSONL.relative_to(repo_root)}")
