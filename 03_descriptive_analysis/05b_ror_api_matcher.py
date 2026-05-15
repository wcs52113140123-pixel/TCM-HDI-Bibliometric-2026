"""
Block 3A.2: ROR API matching for affiliation standardization.

Sends each unique affiliation string to ROR API v2 and stores the best match.

Usage:
    python 03_descriptive_analysis/05b_ror_api_matcher.py
    
    # Resume after Ctrl+C:
    python 03_descriptive_analysis/05b_ror_api_matcher.py  # auto-resumes

Strategy:
- Rate limit: 1 req/sec (friendly, avoids 429 throttling)
- Checkpoint: save every 100 calls to data/processed/ror_results_checkpoint.parquet
- Retry: 3 attempts with exponential backoff on network errors
- Safe interrupt: Ctrl+C saves state and exits

Input:
    data/processed/unique_affiliations.parquet (21,367 unique strings)

Output:
    data/processed/ror_results.parquet
        Columns: affil_id, raw_string, ror_id, ror_name, ror_country, 
                 chosen_score, matched, error
"""

import json
import signal
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import requests
from tqdm import tqdm

# ============================================================
# CONFIG
# ============================================================
ROR_API_URL = "https://api.ror.org/v2/organizations"
RATE_LIMIT_SEC = 1.0       # 1 sec between requests
CHECKPOINT_EVERY = 100     # save every N calls
MAX_RETRIES = 3
TIMEOUT = 15               # seconds per request
USER_AGENT = "TCM-HDI-Bibliometric/1.0 (research)"


# Global flag for graceful shutdown
SHUTDOWN_REQUESTED = False

def handle_sigint(sig, frame):
    """Catch Ctrl+C, set flag for graceful exit."""
    global SHUTDOWN_REQUESTED
    print("\n\n[CTRL+C caught] Saving current progress... DO NOT close terminal yet.")
    SHUTDOWN_REQUESTED = True

signal.signal(signal.SIGINT, handle_sigint)


def query_ror(affiliation: str, retries: int = MAX_RETRIES) -> dict:
    """
    Query ROR API affiliation matching endpoint.
    
    Returns dict with:
        - matched: bool (whether a chosen match found)
        - ror_id: str | None
        - ror_name: str | None
        - ror_country: str | None
        - chosen_score: float | None
        - error: str | None (if request failed)
    """
    params = {"affiliation": affiliation}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    
    last_error = None
    for attempt in range(retries):
        try:
            r = requests.get(ROR_API_URL, params=params, headers=headers, timeout=TIMEOUT)
            
            if r.status_code == 429:
                # Rate limited — wait longer
                wait = 5 * (2 ** attempt)
                time.sleep(wait)
                last_error = f"HTTP 429 (rate limited), retried after {wait}s"
                continue
            
            r.raise_for_status()
            data = r.json()
            
            items = data.get("items", [])
            # Find chosen match
            chosen = next((it for it in items if it.get("chosen")), None)
            if chosen is None and items:
                # No "chosen" flag — pick highest score (defensive)
                chosen = max(items, key=lambda x: x.get("score", 0))
            
            if chosen:
                org = chosen.get("organization", {})
                return {
                    "matched": True,
                    "ror_id": org.get("id"),
                    "ror_name": next((n["value"] for n in org.get("names", []) 
                                       if "ror_display" in n.get("types", [])), 
                                     org.get("id", "").split("/")[-1] if org.get("id") else None),
                    "ror_country": next((loc["geonames_details"].get("country_code") 
                                          for loc in org.get("locations", []) 
                                          if loc.get("geonames_details")), None),
                    "chosen_score": chosen.get("score"),
                    "error": None,
                }
            else:
                return {
                    "matched": False,
                    "ror_id": None,
                    "ror_name": None,
                    "ror_country": None,
                    "chosen_score": None,
                    "error": None,
                }
        
        except requests.exceptions.Timeout:
            last_error = "Timeout"
            time.sleep(2 ** attempt)
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection: {str(e)[:80]}"
            time.sleep(2 ** attempt)
        except Exception as e:
            last_error = f"{type(e).__name__}: {str(e)[:80]}"
            time.sleep(2 ** attempt)
    
    # All retries failed
    return {
        "matched": False,
        "ror_id": None,
        "ror_name": None,
        "ror_country": None,
        "chosen_score": None,
        "error": last_error,
    }


def save_checkpoint(results_dict: dict, checkpoint_path: Path):
    """Save current results to disk."""
    if not results_dict:
        return
    df = pd.DataFrame(results_dict.values())
    df.to_parquet(checkpoint_path, index=False, engine="pyarrow")


def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    print("=" * 70)
    print("Block 3A.2: ROR API affiliation matching")
    print("=" * 70)
    
    # Load input
    print("\n[1] Loading unique affiliations...")
    in_path = repo_root / "data/processed/unique_affiliations.parquet"
    df_in = pd.read_parquet(in_path)
    print(f"    Total: {len(df_in):,} unique affiliations")
    
    # Load checkpoint if exists
    checkpoint_path = repo_root / "data/processed/ror_results_checkpoint.parquet"
    final_path = repo_root / "data/processed/ror_results.parquet"
    
    results = {}  # affil_id -> result dict
    if checkpoint_path.exists():
        print(f"\n[2] Resuming from checkpoint: {checkpoint_path.name}")
        df_ckpt = pd.read_parquet(checkpoint_path)
        results = {row["affil_id"]: row.to_dict() for _, row in df_ckpt.iterrows()}
        print(f"    Already completed: {len(results):,}/{len(df_in):,} "
              f"({100*len(results)/len(df_in):.1f}%)")
    else:
        print("\n[2] No checkpoint found — starting fresh")
    
    # Filter to remaining
    completed_ids = set(results.keys())
    remaining = df_in[~df_in["affil_id"].isin(completed_ids)].reset_index(drop=True)
    n_remaining = len(remaining)
    
    if n_remaining == 0:
        print("\n[3] All affiliations already processed!")
        print(f"    Final output: {final_path}")
        df_final = pd.DataFrame(results.values())
        df_final.to_parquet(final_path, index=False, engine="pyarrow")
        return
    
    # ETA calculation
    eta_sec = n_remaining * (RATE_LIMIT_SEC + 0.5)  # +0.5 for API response time
    eta_str = str(timedelta(seconds=int(eta_sec)))
    print(f"\n[3] Remaining: {n_remaining:,} affiliations")
    print(f"    ETA: ~{eta_str} (at ~1.5 sec/request)")
    print(f"    Checkpoint every {CHECKPOINT_EVERY} calls -> {checkpoint_path.name}")
    print(f"    Press Ctrl+C anytime to safely interrupt")
    print()
    
    # Process
    start_time = time.time()
    last_save = 0
    n_matched = 0
    n_failed = 0
    
    progress = tqdm(remaining.itertuples(index=False), total=n_remaining, 
                     desc="ROR matching", unit="req", smoothing=0.05)
    
    for i, row in enumerate(progress):
        if SHUTDOWN_REQUESTED:
            print(f"\n[INTERRUPT] Saving checkpoint with {len(results):,} results...")
            save_checkpoint(results, checkpoint_path)
            print(f"[INTERRUPT] Saved to {checkpoint_path}")
            print(f"[INTERRUPT] Rerun the script to resume from this point")
            sys.exit(0)
        
        affil_id = row.affil_id
        affiliation = row.raw_string
        
        # Query ROR
        result = query_ror(affiliation)
        result["affil_id"] = affil_id
        result["raw_string"] = affiliation
        results[affil_id] = result
        
        if result["matched"]:
            n_matched += 1
        elif result["error"]:
            n_failed += 1
        
        # Update progress bar postfix
        progress.set_postfix({
            "matched": f"{n_matched:,}",
            "failed": f"{n_failed:,}",
            "pct_match": f"{100*n_matched/(i+1):.1f}%"
        })
        
        # Rate limit
        time.sleep(RATE_LIMIT_SEC)
        
        # Checkpoint
        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(results, checkpoint_path)
            last_save = i + 1
    
    progress.close()
    
    # Final save
    print(f"\n[4] Processing complete!")
    print(f"    Total matched:    {n_matched:,}/{n_remaining:,} ({100*n_matched/n_remaining:.1f}%)")
    print(f"    Total failed:     {n_failed:,}")
    print(f"    Total skipped:    {n_remaining - n_matched - n_failed:,}")
    
    # Save final
    df_final = pd.DataFrame(results.values())
    df_final.to_parquet(final_path, index=False, engine="pyarrow")
    print(f"\n    Final output: {final_path}")
    print(f"    Total records: {len(df_final):,}")
    
    # Cleanup checkpoint
    if checkpoint_path.exists():
        checkpoint_path.unlink()
        print(f"    Cleaned up: {checkpoint_path.name}")
    
    # ROR coverage summary
    matched = df_final[df_final["matched"] == True]
    print(f"\n[5] ROR matching summary:")
    print(f"    Successfully matched: {len(matched):,}/{len(df_final):,} "
          f"({100*len(matched)/len(df_final):.1f}%)")
    
    if len(matched) > 0:
        print(f"\n    Top 10 ROR-matched institutions:")
        top = matched.groupby("ror_name").size().sort_values(ascending=False).head(10)
        for inst, n in top.items():
            print(f"    {n:>4,}x  {inst}")
    
    print("\n" + "=" * 70)
    print("DONE: ROR matching complete. Next: 05c_standardize_institutions.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
