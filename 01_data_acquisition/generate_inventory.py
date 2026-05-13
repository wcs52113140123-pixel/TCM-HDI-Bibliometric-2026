"""
Generate a unified inventory CSV of all raw data files acquired during Day 1+.

Scans data/raw/wos/, data/raw/wos_partial2026/, data/raw/scopus/, 
data/raw/scopus_partial2026/ (and later OpenAlex / PubMed dirs) and 
produces 01_data_acquisition/data_acquisition_inventory.csv.

Usage:
    python 01_data_acquisition/generate_inventory.py
"""

import pandas as pd
import os
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
records = []


def count_pt_lines(filepath):
    """Count 'PT ' field markers (one per WoS record)."""
    with open(filepath, encoding='utf-8', errors='ignore') as fp:
        return sum(1 for line in fp if line.startswith('PT '))


def count_csv_rows(filepath):
    """Count rows in a CSV (excluding header)."""
    df = pd.read_csv(filepath, low_memory=False)
    return len(df)


# ============ WoS main (batched .txt) ============
wos_dir = repo_root / 'data' / 'raw' / 'wos'
for f in sorted(wos_dir.glob('wos_batch_*.txt')):
    name = f.name
    parts = name.replace('.txt', '').split('_')
    batch_num = int(parts[2])
    rng = parts[3].split('-')
    range_start = int(rng[0])
    range_end = int(rng[1])
    count = count_pt_lines(f)
    records.append({
        'database': 'WoS',
        'purpose': 'main',
        'batch': batch_num,
        'file_path': str(f.relative_to(repo_root)).replace(os.sep, '/'),
        'record_range_start': range_start,
        'record_range_end': range_end,
        'record_count': count,
        'file_size_mb': round(f.stat().st_size / 1024 / 1024, 2),
        'format': 'plain_text',
    })

# ============ WoS partial 2026 ============
wos_p_dir = repo_root / 'data' / 'raw' / 'wos_partial2026'
for f in sorted(wos_p_dir.glob('wos_partial2026_*.txt')):
    name = f.name
    rng = name.replace('.txt', '').replace('wos_partial2026_', '').split('-')
    range_start = int(rng[0])
    range_end = int(rng[1])
    count = count_pt_lines(f)
    records.append({
        'database': 'WoS',
        'purpose': 'partial_2026',
        'batch': 1,
        'file_path': str(f.relative_to(repo_root)).replace(os.sep, '/'),
        'record_range_start': range_start,
        'record_range_end': range_end,
        'record_count': count,
        'file_size_mb': round(f.stat().st_size / 1024 / 1024, 2),
        'format': 'plain_text',
    })

# ============ Scopus main (single CSV) ============
scopus_main = repo_root / 'data' / 'raw' / 'scopus' / 'scopus_all_7181.csv'
if scopus_main.exists():
    count = count_csv_rows(scopus_main)
    records.append({
        'database': 'Scopus',
        'purpose': 'main',
        'batch': 1,
        'file_path': str(scopus_main.relative_to(repo_root)).replace(os.sep, '/'),
        'record_range_start': 1,
        'record_range_end': count,
        'record_count': count,
        'file_size_mb': round(scopus_main.stat().st_size / 1024 / 1024, 2),
        'format': 'csv',
    })

# ============ Scopus partial 2026 ============
scopus_p = repo_root / 'data' / 'raw' / 'scopus_partial2026' / 'scopus_partial2026_all.csv'
if scopus_p.exists():
    count = count_csv_rows(scopus_p)
    records.append({
        'database': 'Scopus',
        'purpose': 'partial_2026',
        'batch': 1,
        'file_path': str(scopus_p.relative_to(repo_root)).replace(os.sep, '/'),
        'record_range_start': 1,
        'record_range_end': count,
        'record_count': count,
        'file_size_mb': round(scopus_p.stat().st_size / 1024 / 1024, 2),
        'format': 'csv',
    })

# ============ Save + summary ============
inv_df = pd.DataFrame(records)
out_path = repo_root / '01_data_acquisition' / 'data_acquisition_inventory.csv'
inv_df.to_csv(out_path, index=False, encoding='utf-8')

print(inv_df.to_string(index=False))
print()
print(f'Total files: {len(inv_df)}')
print(f'Main records:    {inv_df[inv_df.purpose == "main"].record_count.sum()}')
print(f'Partial records: {inv_df[inv_df.purpose == "partial_2026"].record_count.sum()}')
print(f'Grand total:     {inv_df.record_count.sum()}')
print()
print(f'Saved to: {out_path}')
