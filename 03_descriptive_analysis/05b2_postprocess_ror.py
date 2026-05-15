"""
Block 3A.2b: Post-process ROR results to fix systematic errors.

Three known issues:
1. TCM affiliations routed to non-TCM ROR names (~38% of TCM records)
2. "Shanghai University" catch-all bucket (174 TCM + 73 non-TCM misclassifications)
3. "Israel Cancer Association USA" catch-all bucket (128 US-only records)

Strategy:
- Detect raw_strings by keyword patterns and reassign to correct institution
- Build a rule-based corrector with manual mapping for the most-common variants
- Output audit log of all changes for manual review

Input:
- data/processed/ror_results.parquet (original ROR results)

Output:
- data/processed/ror_results_fixed.parquet (post-processed)
- data/processed/ror_postprocess_audit.csv (changes log)
"""

import re
from pathlib import Path

import pandas as pd


# ============================================================
# Manual mapping rules
# Each rule: (regex pattern in raw_string, correct ROR name, correct ROR ID)
# ROR IDs are real and verified from ror.org
# ============================================================
RULES = [
    # === TCM university name normalization (case-insensitive) ===
    (
        r"shanghai\s+univ(?:ersity)?\s+(?:of\s+)?tradit(?:ional)?\s+chinese\s+med(?:icine)?|"
        r"shanghai\s+univ\s+tradit\s+chinese\s+med",
        "Shanghai University of Traditional Chinese Medicine",
        "https://ror.org/02hxr5x73",
    ),
    (
        r"beijing\s+univ(?:ersity)?\s+(?:of\s+)?chinese\s+med(?:icine)?|"
        r"beijing\s+univ\s+chinese\s+med",
        "Beijing University of Chinese Medicine",
        "https://ror.org/04w6cq356",
    ),
    (
        r"nanjing\s+univ(?:ersity)?\s+(?:of\s+)?chinese\s+med(?:icine)?",
        "Nanjing University of Chinese Medicine",
        "https://ror.org/03tk24v98",
    ),
    (
        r"chengdu\s+univ(?:ersity)?\s+(?:of\s+)?tradit(?:ional)?\s+chinese\s+med(?:icine)?",
        "Chengdu University of Traditional Chinese Medicine",
        "https://ror.org/00r36hp79",
    ),
    (
        r"tianjin\s+univ(?:ersity)?\s+(?:of\s+)?tradit(?:ional)?\s+chinese\s+med(?:icine)?",
        "Tianjin University of Traditional Chinese Medicine",
        "https://ror.org/0099qb215",
    ),
    (
        r"guangzhou\s+univ(?:ersity)?\s+(?:of\s+)?chinese\s+med(?:icine)?",
        "Guangzhou University of Chinese Medicine",
        "https://ror.org/04vd1zw47",
    ),
    (
        r"shandong\s+univ(?:ersity)?\s+(?:of\s+)?tradit(?:ional)?\s+chinese\s+med(?:icine)?",
        "Shandong University of Traditional Chinese Medicine",
        "https://ror.org/0079y2k27",
    ),
    (
        r"heilongjiang\s+univ(?:ersity)?\s+(?:of\s+)?chinese\s+med(?:icine)?",
        "Heilongjiang University of Chinese Medicine",
        "https://ror.org/03e1wbn82",
    ),
    (
        r"hebei\s+univ(?:ersity)?\s+(?:of\s+)?chinese\s+med(?:icine)?",
        "Hebei University of Chinese Medicine",
        "https://ror.org/03vdkx813",
    ),
    (
        r"changchun\s+univ(?:ersity)?\s+(?:of\s+)?chinese\s+med(?:icine)?",
        "Changchun University of Chinese Medicine",
        "https://ror.org/02x55hd44",
    ),
    (
        r"fujian\s+univ(?:ersity)?\s+(?:of\s+)?tradit(?:ional)?\s+chinese\s+med(?:icine)?",
        "Fujian University of Traditional Chinese Medicine",
        "https://ror.org/00pjnws39",
    ),
    (
        r"jiangxi\s+univ(?:ersity)?\s+(?:of\s+)?tradit(?:ional)?\s+chinese\s+med(?:icine)?",
        "Jiangxi University of Traditional Chinese Medicine",
        "https://ror.org/02k1n9p59",
    ),
    (
        r"liaoning\s+univ(?:ersity)?\s+(?:of\s+)?tradit(?:ional)?\s+chinese\s+med(?:icine)?",
        "Liaoning University of Traditional Chinese Medicine",
        "https://ror.org/02d245m08",
    ),
    (
        r"zhejiang\s+chinese\s+med(?:ical)?\s+univ(?:ersity)?",
        "Zhejiang Chinese Medical University",
        "https://ror.org/0269aze07",
    ),
    (
        r"hubei\s+univ(?:ersity)?\s+(?:of\s+)?chinese\s+med(?:icine)?",
        "Hubei University of Chinese Medicine",
        "https://ror.org/04qzas036",
    ),
    (
        r"hunan\s+univ(?:ersity)?\s+(?:of\s+)?chinese\s+med(?:icine)?",
        "Hunan University of Chinese Medicine",
        "https://ror.org/01hbqkz36",
    ),
    
    # === Non-TCM Shanghai institutions wrongly bucketed ===
    (
        r"second\s+mil(?:itary)?\s+med(?:ical)?\s+univ(?:ersity)?|"
        r"naval\s+med(?:ical)?\s+univ(?:ersity)?",
        "Naval Medical University",
        "https://ror.org/05tezxk26",
    ),
    (
        r"shanghai\s+inst(?:itute)?\s+(?:of\s+)?mat(?:eria)?\s+med(?:ica)?|"
        r"chinese\s+acad\s+sci.*shanghai\s+inst\s+mat\s+med|"
        r"shanghai\s+institute\s+of\s+materia\s+medica",
        "Shanghai Institute of Materia Medica",
        "https://ror.org/03vbzg524",
    ),
    (
        r"univ\s+chinese\s+acad\s+sci|"
        r"university\s+of\s+chinese\s+academy\s+of\s+sciences",
        "University of Chinese Academy of Sciences",
        "https://ror.org/05qbk4x57",
    ),
]


def apply_fix(raw_string):
    """Apply rules in order; return (new_name, new_id) if matched, else (None, None)."""
    if not isinstance(raw_string, str):
        return (None, None)
    for pattern, name, ror_id in RULES:
        if re.search(pattern, raw_string, re.IGNORECASE):
            return (name, ror_id)
    return (None, None)


def is_known_catch_all(ror_name):
    """ROR names that are known catch-all buckets — always re-attempt fix."""
    return ror_name in {
        "Shanghai University",  # Confirmed catch-all
        "Israel Cancer Association USA",  # Confirmed catch-all
    }


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3A.2b: Post-process ROR results to fix systematic errors")
    print("=" * 70)
    
    # Load
    print("\n[1] Loading ROR results...")
    ror = pd.read_parquet(repo_root / "data/processed/ror_results.parquet")
    print(f"    Total records: {len(ror):,}")
    print(f"    Currently matched: {ror['matched'].sum():,}")
    
    # Pre-fix counts for tracking
    pre_counts = ror['ror_name'].value_counts().head(20).to_dict()
    
    # Apply fixes
    print("\n[2] Applying post-processing rules...")
    
    audit_log = []
    fixes_applied = 0
    
    for idx, row in ror.iterrows():
        raw = row['raw_string']
        cur_name = row['ror_name']
        cur_id = row['ror_id']
        
        # Try rule-based fix
        new_name, new_id = apply_fix(raw)
        
        should_apply = False
        reason = ""
        
        if new_name is not None:
            if new_name != cur_name:
                # Rule matched and disagrees with current
                should_apply = True
                reason = f"rule_match_disagree"
            # If rule agrees with current, leave alone (no change needed)
        elif is_known_catch_all(cur_name):
            # In catch-all, no rule matched -> mark as unmatched
            new_name = None
            new_id = None
            should_apply = True
            reason = "catch_all_no_rule"
        
        if should_apply:
            audit_log.append({
                "raw_string": raw[:200],
                "old_ror_name": cur_name,
                "new_ror_name": new_name if new_name else "(unmatched)",
                "reason": reason,
                "chosen_score": row.get("chosen_score"),
            })
            ror.at[idx, 'ror_name'] = new_name
            ror.at[idx, 'ror_id'] = new_id
            if new_name is None:
                ror.at[idx, 'matched'] = False
            fixes_applied += 1
    
    print(f"    Total fixes applied: {fixes_applied:,}")
    
    # Stats by reason
    audit_df = pd.DataFrame(audit_log)
    if len(audit_df) > 0:
        print(f"\n[3] Fix breakdown:")
        for reason, n in audit_df['reason'].value_counts().items():
            print(f"    {reason}: {n:,}")
    
    # Save audit log
    audit_path = repo_root / "data/processed/ror_postprocess_audit.csv"
    audit_df.to_csv(audit_path, index=False, encoding="utf-8")
    print(f"\n[4] Audit log saved: {audit_path}")
    
    # Save fixed ROR results
    fixed_path = repo_root / "data/processed/ror_results_fixed.parquet"
    ror.to_parquet(fixed_path, index=False, engine="pyarrow")
    print(f"    Fixed ROR results: {fixed_path}")
    
    # Final coverage
    matched_after = ror['matched'].sum()
    print(f"\n[5] After post-processing:")
    print(f"    Matched: {matched_after:,} / {len(ror):,} ({100*matched_after/len(ror):.1f}%)")
    
    # Top 20 changes
    print(f"\n[6] Top 20 ROR names AFTER post-processing:")
    post_counts = ror[ror['matched']==True]['ror_name'].value_counts().head(20)
    for name, n in post_counts.items():
        pre_n = pre_counts.get(name, 0)
        delta = n - pre_n
        delta_str = f"(+{delta:>4})" if delta > 0 else f"({delta:>4})" if delta < 0 else "      "
        print(f"    {n:>5,} {delta_str}  {name[:65]}")
    
    print("\n" + "=" * 70)
    print("DONE: Run 05c_standardize_institutions.py + 05d_institution_ranking.py")
    print("with new ror_results_fixed.parquet")
    print("=" * 70)


if __name__ == "__main__":
    main()
