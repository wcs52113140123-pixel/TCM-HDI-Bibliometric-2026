"""
Block 2A: Country extraction from affiliations.

Extracts country codes (ISO 2-letter) from each record's affiliation data,
using a priority chain: OpenAlex institutions_list -> WoS/Scopus affiliations_raw
-> WoS reprint_address fallback.

Strategy:
1. OpenAlex records have structured institutions_list with country_code (best)
2. WoS/Scopus have free-text affiliations_raw — extract via regex + alias dict
3. HK/TW/MO are treated as distinct from mainland CN (Frontiers/Scopus convention)
4. For records without ANY affiliation (mainly PubMed), use DOI-based cross-DB
   join to borrow affiliations from sibling records.

Output:
- data/processed/country_lookup.parquet      (record_id -> list of country codes)
- data/processed/country_extraction_audit.csv (audit log for quality checks)
- results/tables/table_02_country_coverage.csv (coverage statistics)

Run:
    python 03_descriptive_analysis/02_country_extraction.py
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

import pandas as pd


# ============================================================
# Country alias dictionary (lowercase keys -> ISO 2-letter code)
# Order in COUNTRY_ALIASES doesn't matter, but HK/TW/MO are 
# checked SEPARATELY first to prevent fall-through to CN.
# ============================================================
COUNTRY_ALIASES = {
    # ===== Asia =====
    "peoples r china": "CN", "p r china": "CN", "p.r. china": "CN", "p.r.china": "CN",
    "prc": "CN", "mainland china": "CN",
    "china": "CN",  # Note: HK/TW/MO checked first; this only matches if those don't
    "japan": "JP",
    "south korea": "KR", "republic of korea": "KR", "korea, south": "KR", 
    "korea": "KR", "korea rep": "KR",
    "north korea": "KP", "korea dem peoples rep": "KP",
    "india": "IN",
    "singapore": "SG",
    "malaysia": "MY",
    "thailand": "TH",
    "vietnam": "VN", "viet nam": "VN",
    "indonesia": "ID",
    "philippines": "PH",
    "pakistan": "PK",
    "bangladesh": "BD",
    "sri lanka": "LK",
    "nepal": "NP",
    "myanmar": "MM", "burma": "MM",
    "cambodia": "KH",
    "laos": "LA",
    "mongolia": "MN",
    "kazakhstan": "KZ",
    "uzbekistan": "UZ",
    
    # ===== Middle East =====
    "saudi arabia": "SA",
    "u arab emirates": "AE", "united arab emirates": "AE", "uae": "AE",
    "iran": "IR",
    "iraq": "IQ",
    "israel": "IL",
    "turkey": "TR",
    "jordan": "JO",
    "lebanon": "LB",
    "syria": "SY",
    "qatar": "QA",
    "kuwait": "KW",
    "oman": "OM",
    "bahrain": "BH",
    "yemen": "YE",
    "palestine": "PS",
    
    # ===== Europe =====
    "united kingdom": "GB", "uk": "GB", "u.k.": "GB",
    "england": "GB", "scotland": "GB", "wales": "GB", "northern ireland": "GB",
    "germany": "DE", "deutschland": "DE",
    "france": "FR",
    "italy": "IT",
    "spain": "ES",
    "portugal": "PT",
    "netherlands": "NL", "the netherlands": "NL", "holland": "NL",
    "belgium": "BE",
    "switzerland": "CH",
    "austria": "AT",
    "sweden": "SE",
    "norway": "NO",
    "finland": "FI",
    "denmark": "DK",
    "iceland": "IS",
    "ireland": "IE",
    "poland": "PL",
    "czech republic": "CZ", "czechia": "CZ",
    "slovakia": "SK", "slovak republic": "SK",
    "hungary": "HU",
    "romania": "RO",
    "bulgaria": "BG",
    "greece": "GR",
    "ukraine": "UA",
    "russia": "RU", "russian federation": "RU",
    "belarus": "BY",
    "serbia": "RS",
    "croatia": "HR",
    "slovenia": "SI",
    "bosnia and herzegovina": "BA",
    "albania": "AL",
    "macedonia": "MK", "north macedonia": "MK",
    "estonia": "EE",
    "latvia": "LV",
    "lithuania": "LT",
    "luxembourg": "LU",
    "cyprus": "CY",
    "malta": "MT",
    "moldova": "MD",
    "georgia": "GE",
    "armenia": "AM",
    "azerbaijan": "AZ",
    
    # ===== Americas =====
    "usa": "US", "united states": "US", "u.s.a.": "US", "u.s.": "US",
    "united states of america": "US",
    "canada": "CA",
    "mexico": "MX",
    "brazil": "BR", "brasil": "BR",
    "argentina": "AR",
    "chile": "CL",
    "colombia": "CO",
    "peru": "PE",
    "venezuela": "VE",
    "ecuador": "EC",
    "bolivia": "BO",
    "uruguay": "UY",
    "paraguay": "PY",
    "cuba": "CU",
    "puerto rico": "PR",
    "panama": "PA",
    "costa rica": "CR",
    "dominican republic": "DO",
    "guatemala": "GT",
    "honduras": "HN",
    "nicaragua": "NI",
    "el salvador": "SV",
    
    # ===== Oceania =====
    "australia": "AU",
    "new zealand": "NZ",
    "fiji": "FJ",
    
    # ===== Africa =====
    "south africa": "ZA",
    "egypt": "EG",
    "nigeria": "NG",
    "kenya": "KE",
    "ethiopia": "ET",
    "morocco": "MA",
    "tunisia": "TN",
    "algeria": "DZ",
    "ghana": "GH",
    "tanzania": "TZ",
    "uganda": "UG",
    "sudan": "SD",
    "libya": "LY",
    "zimbabwe": "ZW",
    "zambia": "ZM",
    "mozambique": "MZ",
    "cameroon": "CM",
    "senegal": "SN",
    "ivory coast": "CI", "cote divoire": "CI",
    "democratic republic of the congo": "CD",
    "republic of the congo": "CG",
    "angola": "AO",
    "rwanda": "RW",
    "burkina faso": "BF",
    "mali": "ML",
    "niger": "NE",
    "mauritius": "MU",
    "madagascar": "MG",
    "namibia": "NA",
    "botswana": "BW",
}

# Precompile regex patterns for each alias (word-boundary safe)
ALIAS_PATTERNS = {
    alias: re.compile(r'\b' + re.escape(alias) + r'\b', re.IGNORECASE)
    for alias in COUNTRY_ALIASES.keys()
}


def extract_special_china_regions(text_lower):
    """
    Check HK/TW/MO BEFORE generic China matching.
    Returns set of {'HK', 'TW', 'MO'} subset present in text.
    """
    found = set()
    if re.search(r'\bhong\s*kong\b', text_lower):
        found.add("HK")
    if re.search(r'\btaiwan\b|\btaipei\b|\bchinese\s*taipei\b', text_lower):
        found.add("TW")
    if re.search(r'\bmacao\b|\bmacau\b', text_lower):
        found.add("MO")
    return found


def extract_countries_from_text(text):
    """
    Extract ISO country codes from a free-text affiliation string.
    Returns a set of 2-letter codes.
    """
    if not text or not isinstance(text, str):
        return set()
    
    text_lower = text.lower()
    found = set()
    
    # Step 1: HK/TW/MO first (they often co-occur with "China" in the same address)
    china_special = extract_special_china_regions(text_lower)
    found.update(china_special)
    
    # Step 2: Other countries via alias dictionary
    for alias, pattern in ALIAS_PATTERNS.items():
        if pattern.search(text_lower):
            code = COUNTRY_ALIASES[alias]
            # SPECIAL: skip CN if HK/TW/MO already added (likely co-mentioned)
            # Only suppress when HK/TW/MO IS in this specific text
            if code == "CN" and china_special:
                # Check if there is non-HK/TW/MO Chinese mainland context
                # Heuristic: if "China" appears WITHOUT being prefixed by Hong Kong / Taiwan / Macao
                # e.g., "Hong Kong, China" - skip CN
                # But "Beijing, China; Hong Kong" - keep CN
                # Simplest: check if 'china' appears in a non-HK/TW/MO-adjacent context
                china_matches = list(re.finditer(r'\bchina\b', text_lower))
                for m in china_matches:
                    # Check 30 chars before this "china" — does it contain HK/TW/MO?
                    context_before = text_lower[max(0, m.start()-30):m.start()]
                    if not any(t in context_before for t in ["hong kong", "taiwan", "taipei", "macao", "macau"]):
                        found.add("CN")
                        break
                continue
            found.add(code)
    
    return found


def extract_countries(row):
    """
    Extract country codes from a single record using priority chain.
    Returns: (countries: list, source: str)
    """
    countries = set()
    sources_used = []
    
    # Priority 1: OpenAlex institutions_list (structured, cleanest)
    inst_list = row.get("institutions_list")
    if inst_list is not None:
        try:
            for inst in inst_list:
                cc = inst.get("country_code", "").strip().upper() if isinstance(inst, dict) else ""
                if cc and len(cc) == 2 and cc.isalpha():
                    countries.add(cc)
        except (TypeError, AttributeError):
            pass
        if countries:
            sources_used.append("openalex_institutions")
    
    # Priority 2: affiliations_raw (WoS C1 / Scopus Affiliations)
    aff_text = row.get("affiliations_raw") or ""
    if aff_text:
        extracted = extract_countries_from_text(aff_text)
        if extracted:
            countries.update(extracted)
            sources_used.append("affiliations_raw")
    
    # Priority 3: reprint_address (WoS RP) — fallback
    if not countries:
        rp = row.get("reprint_address") or ""
        if rp:
            extracted = extract_countries_from_text(rp)
            if extracted:
                countries.update(extracted)
                sources_used.append("reprint_address")
    
    return sorted(countries), "+".join(sources_used) if sources_used else "none"


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 2A: Country Extraction")
    print("=" * 70)
    
    # Load integrated_corpus
    print("\n[1] Loading integrated_corpus.parquet...")
    df = pd.read_parquet(repo_root / "data/processed/integrated_corpus.parquet")
    print(f"    -> {len(df):,} records loaded")
    
    # Extract countries
    print("\n[2] Extracting countries (priority: OpenAlex > affiliations_raw > reprint_address)...")
    results = df.apply(extract_countries, axis=1)
    df["country_codes"] = [r[0] for r in results]
    df["country_extraction_source"] = [r[1] for r in results]
    df["country_count"] = df["country_codes"].apply(len)
    
    # Coverage stats
    print("\n[3] Direct extraction coverage:")
    n_total = len(df)
    n_with_country = (df["country_count"] > 0).sum()
    print(f"    Records with at least one country: {n_with_country:,}/{n_total:,} "
          f"({100*n_with_country/n_total:.1f}%)")
    
    print("\n    By source_db:")
    for db in ["WoS", "Scopus", "OpenAlex", "PubMed"]:
        sub = df[df["source_db"] == db]
        if len(sub) == 0: continue
        n_db_with = (sub["country_count"] > 0).sum()
        print(f"    {db:10s}: {n_db_with:,}/{len(sub):,} "
              f"({100*n_db_with/len(sub):.1f}%)")
    
    # Source breakdown
    print("\n[4] Extraction source breakdown:")
    src_counts = df["country_extraction_source"].value_counts()
    for src, n in src_counts.items():
        print(f"    {src:50s} {n:>5,}")
    
    # Cross-DB join for records without countries (mostly PubMed)
    print("\n[5] DOI-based cross-DB join for records without countries...")
    no_country_mask = df["country_count"] == 0
    n_missing_before = no_country_mask.sum()
    print(f"    Before join: {n_missing_before:,} records lack country info")
    
    # Build DOI -> countries map from records that HAVE countries
    has_country = df[df["country_count"] > 0].copy()
    has_doi_mask = has_country["doi"].notna() & (has_country["doi"].str.len() > 0)
    doi_to_countries = (
        has_country[has_doi_mask]
        .groupby("doi")["country_codes"]
        .apply(lambda lists: sorted(set(c for sub in lists for c in sub)))
        .to_dict()
    )
    print(f"    Built DOI -> countries map: {len(doi_to_countries):,} unique DOIs")
    
    # Apply join
    n_recovered = 0
    for idx in df[no_country_mask].index:
        doi = df.at[idx, "doi"]
        if doi and doi in doi_to_countries:
            df.at[idx, "country_codes"] = doi_to_countries[doi]
            df.at[idx, "country_extraction_source"] = "doi_cross_db_join"
            df.at[idx, "country_count"] = len(doi_to_countries[doi])
            n_recovered += 1
    
    print(f"    Recovered via DOI join: {n_recovered:,}")
    print(f"    Final missing: {n_missing_before - n_recovered:,} "
          f"({100*(n_missing_before-n_recovered)/n_total:.1f}% of total)")
    
    # Final coverage
    final_with_country = (df["country_count"] > 0).sum()
    print(f"\n[6] FINAL country coverage: {final_with_country:,}/{n_total:,} "
          f"({100*final_with_country/n_total:.1f}%)")
    
    # Top countries (preview)
    print("\n[7] Top 15 countries by record count (preview):")
    country_counter = Counter()
    for clist in df["country_codes"]:
        for c in clist:
            country_counter[c] += 1
    for c, n in country_counter.most_common(15):
        bar = "#" * int(n / max(country_counter.most_common(1)[0][1] / 30, 1))
        print(f"    {c}: {n:>5,}  {bar}")
    
    # Save outputs
    out_dir = repo_root / "data" / "processed"
    out_tables = repo_root / "results" / "tables"
    out_tables.mkdir(parents=True, exist_ok=True)
    
    # 1. Country lookup parquet
    lookup_df = df[["record_id", "doi", "year", "source_db", "country_codes",
                    "country_count", "country_extraction_source"]].copy()
    lookup_path = out_dir / "country_lookup.parquet"
    lookup_df.to_parquet(lookup_path, index=False, engine="pyarrow")
    print(f"\n[8] Outputs saved:")
    print(f"    {lookup_path}  ({lookup_path.stat().st_size/1024:.1f} KB)")
    
    # 2. Audit CSV (records without countries — for manual review)
    audit_path = out_dir / "country_extraction_audit.csv"
    missing = df[df["country_count"] == 0][
        ["record_id", "doi", "source_db", "title", "affiliations_raw", "reprint_address"]
    ].head(100)
    missing.to_csv(audit_path, index=False, encoding="utf-8")
    print(f"    {audit_path}  ({audit_path.stat().st_size/1024:.1f} KB)")
    
    # 3. Coverage summary table
    coverage_data = []
    for db in ["WoS", "Scopus", "OpenAlex", "PubMed"]:
        sub = df[df["source_db"] == db]
        if len(sub) == 0: continue
        coverage_data.append({
            "source_db": db,
            "n_records": int(len(sub)),
            "n_with_country": int((sub["country_count"] > 0).sum()),
            "coverage_pct": round(100 * (sub["country_count"] > 0).sum() / len(sub), 1),
        })
    pd.DataFrame(coverage_data).to_csv(
        out_tables / "table_02_country_coverage.csv", index=False, encoding="utf-8"
    )
    print(f"    {out_tables / 'table_02_country_coverage.csv'}")
    
    print("\n" + "=" * 70)
    print(f"DONE: country_codes field populated for {final_with_country:,} records")
    print("=" * 70)


if __name__ == "__main__":
    main()
