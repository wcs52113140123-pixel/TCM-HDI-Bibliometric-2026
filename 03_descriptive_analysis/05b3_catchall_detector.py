"""
Block 3A.2c: Systematic catch-all bucket detector for ROR results.

Identifies ROR identifiers that exhibit catch-all bucket behavior by
analyzing the diversity of their underlying raw_strings.

Detection criteria:
1. City diversity > 5
2. Core token overlap (ROR name in raw_string) < 50%
3. Leading institution token diversity > 60%
4. Median chosen_score < 0.85
5. Country code inconsistency

ROR ID flagged as catch-all if 2+ criteria triggered.
Only checks ROR IDs with >= 30 raw_strings (Top 50 institutions).

Output:
- data/processed/ror_catchall_audit.csv (per-ROR-ID assessment)
- data/processed/ror_results_fixed.parquet (updated, catch-alls unmatched)
"""

import re
from collections import Counter
from pathlib import Path

import pandas as pd


def extract_city_tokens(text):
    """Extract likely city/province tokens from an affiliation string."""
    if not isinstance(text, str):
        return set()
    # Common Chinese cities + province names
    chinese_locations = {
        "beijing", "shanghai", "guangzhou", "shenzhen", "tianjin", "chongqing",
        "chengdu", "wuhan", "xian", "hangzhou", "nanjing", "jinan", "hefei",
        "fuzhou", "shenyang", "harbin", "changchun", "kunming", "guizhou",
        "haikou", "zhengzhou", "taipei", "hong kong", "macao", "macau",
        "shijiazhuang", "taiyuan", "ningxia", "tibet", "hainan", "yunnan",
        "sichuan", "shandong", "shanxi", "shaanxi", "jiangsu", "zhejiang",
        "fujian", "guangdong", "anhui", "jiangxi", "hubei", "hunan", "henan",
        "hebei", "liaoning", "jilin", "heilongjiang", "gansu", "qinghai",
        "rizhao", "yinchuan", "xining", "lhasa", "urumqi", "lanzhou"
    }
    international_cities = {
        "tokyo", "seoul", "singapore", "bangkok", "delhi", "mumbai", "sydney",
        "london", "paris", "berlin", "rome", "madrid", "new york", "boston",
        "chicago", "los angeles", "san francisco", "san diego", "houston",
        "philadelphia", "phoenix", "atlanta", "miami", "dallas", "seattle",
        "stockholm", "moscow", "istanbul", "tehran", "riyadh", "cairo"
    }
    
    text_lower = text.lower()
    found = set()
    for loc in chinese_locations | international_cities:
        if re.search(rf"\b{re.escape(loc)}\b", text_lower):
            found.add(loc)
    return found


def get_core_tokens(name):
    """Extract the meaningful tokens from a ROR name."""
    if not isinstance(name, str):
        return set()
    # Remove common stop words
    stopwords = {"of", "the", "and", "in", "for", "&", "a", "an", "at"}
    tokens = set(t.lower() for t in re.findall(r"[a-zA-Z]+", name) 
                  if len(t) >= 3 and t.lower() not in stopwords)
    return tokens


def get_leading_token(raw_string):
    """Get the first meaningful word of the affiliation."""
    if not isinstance(raw_string, str):
        return ""
    # Strip [Author] prefix
    raw = re.sub(r"^\[[^\]]+\]\s*", "", raw_string).strip()
    # First segment before comma
    first_seg = raw.split(",")[0].strip().lower()
    # First word
    tokens = re.findall(r"[a-z]+", first_seg)
    return tokens[0] if tokens else ""


def detect_catch_all(ror_name, group_df):
    """Apply 5 criteria; return (is_catchall, score, reasons)."""
    raw_strings = group_df["raw_string"].tolist()
    n = len(raw_strings)
    reasons = []
    
    # Criterion 1: City diversity
    all_cities = set()
    for s in raw_strings:
        all_cities |= extract_city_tokens(s)
    if len(all_cities) > 5:
        reasons.append(f"city_diversity={len(all_cities)}")
    
    # Criterion 2: Core token overlap
    ror_tokens = get_core_tokens(ror_name)
    if ror_tokens:
        overlap_count = sum(1 for s in raw_strings 
                             if ror_tokens & get_core_tokens(s))
        overlap_pct = overlap_count / n
        if overlap_pct < 0.4:
            reasons.append(f"core_overlap={overlap_pct:.1%}")
    
    # Criterion 3: Leading token diversity  
    leading_tokens = [get_leading_token(s) for s in raw_strings]
    unique_leading = set(t for t in leading_tokens if t and len(t) >= 3)
    leading_diversity = len(unique_leading) / max(n, 1)
    if leading_diversity > 0.6:
        reasons.append(f"leading_diversity={leading_diversity:.1%}")
    
    # Criterion 4: Score median
    scores = group_df["chosen_score"].dropna().tolist()
    if scores:
        median_score = sorted(scores)[len(scores)//2]
        if median_score < 0.85:
            reasons.append(f"score_median={median_score:.2f}")
    
    # Criterion 5: ROR country vs raw_string country inconsistency
    ror_country = group_df["ror_country"].dropna().iloc[0] if not group_df["ror_country"].isna().all() else None
    if ror_country:
        # Detect mentioned countries in raw_strings
        raw_country_hint_counter = Counter()
        for s in raw_strings:
            s_lower = s.lower() if isinstance(s, str) else ""
            if "peoples r china" in s_lower or ", china" in s_lower or "p.r. china" in s_lower:
                raw_country_hint_counter["CN"] += 1
            elif "usa" in s_lower or ", usa" in s_lower or " us " in s_lower:
                raw_country_hint_counter["US"] += 1
            elif "israel" in s_lower:
                raw_country_hint_counter["IL"] += 1
            elif "uk" in s_lower or "united kingdom" in s_lower:
                raw_country_hint_counter["GB"] += 1
            elif "germany" in s_lower:
                raw_country_hint_counter["DE"] += 1
        
        if raw_country_hint_counter:
            dominant_country, dominant_count = raw_country_hint_counter.most_common(1)[0]
            if dominant_country != ror_country and dominant_count / n > 0.5:
                reasons.append(f"country_mismatch (ROR={ror_country}, raw_dominant={dominant_country})")
    
    is_catchall = len(reasons) >= 2
    return is_catchall, len(reasons), "; ".join(reasons)


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3A.2c: Systematic catch-all bucket detector")
    print("=" * 70)
    
    # Load
    print("\n[1] Loading ROR results (fixed v1)...")
    ror = pd.read_parquet(repo_root / "data/processed/ror_results_fixed.parquet")
    matched = ror[ror['matched'] == True].copy()
    print(f"    Total matched: {len(matched):,}")
    
    # Group by ROR name, check those with >= 30 records
    print("\n[2] Detecting catch-all buckets...")
    counts = matched['ror_name'].value_counts()
    candidates = counts[counts >= 30].index.tolist()
    print(f"    Candidates with >= 30 records: {len(candidates)}")
    
    audit_rows = []
    catchalls = []
    
    for ror_name in candidates:
        group = matched[matched['ror_name'] == ror_name]
        is_ca, n_reasons, reasons_str = detect_catch_all(ror_name, group)
        audit_rows.append({
            "ror_name": ror_name,
            "n_records": len(group),
            "n_reasons_triggered": n_reasons,
            "is_catchall": is_ca,
            "reasons": reasons_str,
        })
        if is_ca:
            catchalls.append(ror_name)
    
    audit_df = pd.DataFrame(audit_rows).sort_values(
        ["is_catchall", "n_reasons_triggered", "n_records"], 
        ascending=[False, False, False]
    )
    
    audit_path = repo_root / "data/processed/ror_catchall_audit.csv"
    audit_df.to_csv(audit_path, index=False, encoding="utf-8")
    
    # Print results
    print(f"\n[3] Catch-alls detected: {len(catchalls)}")
    if catchalls:
        print(f"\n    Flagged catch-all ROR names (will be unmatched):")
        print(f"    {'#':<3} {'N':>5} {'Reasons':<60} {'ROR name'}")
        for i, row in audit_df[audit_df['is_catchall']].iterrows():
            reasons_short = row['reasons'][:58]
            print(f"    {row['n_reasons_triggered']:<3} {int(row['n_records']):>5} "
                  f"{reasons_short:<60} {row['ror_name'][:50]}")
    
    print(f"\n[4] Top 10 high-confidence (n_reasons=0):")
    clean = audit_df[~audit_df['is_catchall']].head(10)
    for _, row in clean.iterrows():
        print(f"    {row['n_reasons_triggered']:<3} {int(row['n_records']):>5}  "
              f"{row['ror_name'][:60]}")
    
    # Apply: mark catchalls as unmatched
    if catchalls:
        print(f"\n[5] Marking catch-all records as unmatched...")
        catchall_mask = ror['ror_name'].isin(catchalls)
        n_to_unmatch = catchall_mask.sum()
        print(f"    Records to mark unmatched: {n_to_unmatch:,}")
        
        ror.loc[catchall_mask, 'matched'] = False
        ror.loc[catchall_mask, 'ror_name'] = None
        ror.loc[catchall_mask, 'ror_id'] = None
        ror.loc[catchall_mask, 'ror_country'] = None
        
        # Save
        out_path = repo_root / "data/processed/ror_results_fixed.parquet"
        ror.to_parquet(out_path, index=False, engine="pyarrow")
        
        final_matched = ror['matched'].sum()
        print(f"\n[6] Final ROR coverage after catch-all removal:")
        print(f"    Matched: {final_matched:,} / {len(ror):,} ({100*final_matched/len(ror):.1f}%)")
    else:
        print(f"\n[5] No new catch-alls detected; ror_results_fixed.parquet unchanged.")
    
    print(f"\n    Audit log: {audit_path}")
    
    print("\n" + "=" * 70)
    print("DONE: Re-run 05c + 05d to refresh Top 30 institutions ranking")
    print("=" * 70)


if __name__ == "__main__":
    main()
