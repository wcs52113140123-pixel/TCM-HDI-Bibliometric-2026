"""
Quick API connectivity test for OpenAlex.
Pulls 1 sample paper to verify pyalex + email config work.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
load_dotenv(repo_root / ".env")

import pyalex
from pyalex import Works

email = os.getenv("OPENALEX_EMAIL", "").strip()
if email and "example.com" not in email:
    pyalex.config.email = email
    print(f"Using polite pool: {email}")
else:
    print("Anonymous pool (slower; consider setting OPENALEX_EMAIL in .env)")

print("\nQuerying OpenAlex for 1 sample 'herb-drug interaction' paper from 2025...")

result = (
    Works()
    .search_filter(title_and_abstract="herb-drug interaction")
    .filter(publication_year=2025)
    .get(per_page=1)
)

print(f"\nTest query returned {len(result)} work(s)")

if result:
    work = result[0]
    title = work.get("title", "")
    title_preview = title[:80] if title else "<no title>"
    print(f"  Title:    {title_preview}...")
    print(f"  Year:     {work.get('publication_year', '?')}")
    print(f"  DOI:      {work.get('doi', 'N/A')}")
    print(f"  Cited by: {work.get('cited_by_count', '?')}")
    print(f"  Type:     {work.get('type', '?')}")
    print(f"  Language: {work.get('language', '?')}")
    print("\nAPI connectivity OK.")
else:
    print("\nWARNING: query returned no results — investigate before running full pull")
