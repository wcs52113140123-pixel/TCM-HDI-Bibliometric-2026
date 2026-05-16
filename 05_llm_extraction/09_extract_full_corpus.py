"""
Day 7 full-corpus LLM extraction.

Runs the primary mechanism extraction on the full 9,413-abstract main corpus
using a single LLM model (default: openai/gpt-4o-mini via OpenRouter).

Critical features for long-running production extraction:
  1. CHECKPOINT RESUME    — incrementally appends successful results to JSONL;
                            on restart, skips records already processed
  2. CONCURRENT REQUESTS  — ThreadPoolExecutor with N workers (default 5),
                            ~5× speedup vs sequential (~3h vs ~16h)
  3. FAILED-RECORD LOG    — records that exhaust all retry tiers go to a
                            separate JSONL for later inspection / re-extraction
  4. GRACEFUL CTRL+C      — SIGINT flushes the current in-memory buffer
                            before exiting so no data is lost

CLI usage:
    python 05_llm_extraction/09_extract_full_corpus.py
        [--model openai/gpt-4o-mini]
        [--input data/processed/integrated_corpus.parquet]
        [--max-records N]
        [--max-workers 5]
        [--batch-size 100]

Output files (under data/processed/llm_extraction/):
    primary_<model>.results.jsonl      # one extraction per line
    primary_<model>.failed.jsonl       # one failed record per line
    primary_<model>.checkpoint.json    # set of completed record_ids
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import signal
import sys
import threading
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
OUT_DIR = DATA / "llm_extraction"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
def _import_local(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------
def model_safe_name(model: str) -> str:
    return model.replace("/", "__").replace(".", "_")


def load_checkpoint(checkpoint_path: Path) -> set[str]:
    """Return set of record_ids already processed (success or hard failure)."""
    if not checkpoint_path.exists():
        return set()
    try:
        return set(json.loads(checkpoint_path.read_text(encoding="utf-8")).get("done", []))
    except Exception:
        return set()


def write_checkpoint(checkpoint_path: Path, done_ids: set[str]) -> None:
    tmp = checkpoint_path.with_suffix(checkpoint_path.suffix + ".tmp")
    tmp.write_text(
        json.dumps({"done": sorted(done_ids), "n_done": len(done_ids)},
                   ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(checkpoint_path)


# ----------------------------------------------------------------------
class ExtractionWorker:
    """Holds shared state across threads: LLM client, file locks, counters."""

    def __init__(self, model: str, build_user_prompt, system_prompt: str,
                 results_path: Path, failed_path: Path):
        client_mod = _import_local(
            Path(__file__).parent / "03_llm_client.py", "client_mod"
        )
        self.client = client_mod.LLMClient(model=model, log_dir=OUT_DIR)
        self.build_user_prompt = build_user_prompt
        self.system_prompt = system_prompt
        self.results_path = results_path
        self.failed_path = failed_path

        # Thread-safe append lock
        self._file_lock = threading.Lock()
        # Counters (GIL-protected int += is atomic, no lock needed)
        self.n_processed = 0
        self.n_success = 0
        self.n_failed = 0

    def process_one(self, row: dict) -> dict:
        """Process a single abstract. Thread-safe."""
        record_id = row["record_id"]
        user_prompt = self.build_user_prompt(
            record_id=record_id,
            title=row.get("title") or "",
            abstract=row.get("abstract") or "",
        )
        extraction, meta = self.client.extract(self.system_prompt, user_prompt)
        ok = extraction is not None

        out = {
            "record_id": record_id,
            "cluster_id": int(row.get("cluster_id", -1))
                if pd.notna(row.get("cluster_id")) else None,
            "year": int(row["year"]) if pd.notna(row.get("year")) else None,
            "ok": ok,
            "extraction": extraction.model_dump() if extraction else None,
            "tier_used": meta.get("tier_used"),
            "n_attempts": meta.get("n_attempts"),
            "validation_failures": meta.get("validation_failures"),
            "input_tokens": meta.get("input_tokens"),
            "output_tokens": meta.get("output_tokens"),
            "elapsed_s": meta.get("elapsed_s"),
            "error": meta.get("error"),
        }

        # Thread-safe append to JSONL
        with self._file_lock:
            target = self.results_path if ok else self.failed_path
            with open(target, "a", encoding="utf-8") as f:
                f.write(json.dumps(out, ensure_ascii=False, default=str) + "\n")
            self.n_processed += 1
            if ok:
                self.n_success += 1
            else:
                self.n_failed += 1
        return out


# ----------------------------------------------------------------------
class GracefulExit:
    """SIGINT handler: set flag so worker pool can finish in-flight tasks."""
    def __init__(self):
        self.flag = False
        signal.signal(signal.SIGINT, self._handler)

    def _handler(self, signum, frame):
        print("\n\n⚠️  Ctrl+C received. Finishing in-flight tasks then exiting...\n"
              "    Run the same command again to resume from checkpoint.\n")
        self.flag = True


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini",
                    help="Model id (auto-routed by 03_llm_client.py)")
    ap.add_argument("--input", default=str(DATA / "integrated_corpus.parquet"),
                    help="Path to corpus parquet")
    ap.add_argument("--max-records", type=int, default=None,
                    help="Limit to N records (for testing). Default: all eligible.")
    ap.add_argument("--max-workers", type=int, default=5,
                    help="Concurrent LLM requests (default 5)")
    ap.add_argument("--batch-size", type=int, default=100,
                    help="Records per checkpoint flush (default 100)")
    ap.add_argument("--exclude-noise", action="store_true", default=True,
                    help="Exclude HDBSCAN noise cluster (default True)")
    ap.add_argument("--include-reviews", action="store_true",
                    help="Include review papers (default: exclude)")
    args = ap.parse_args()

    safe = model_safe_name(args.model)
    results_path = OUT_DIR / f"primary_{safe}.results.jsonl"
    failed_path = OUT_DIR / f"primary_{safe}.failed.jsonl"
    checkpoint_path = OUT_DIR / f"primary_{safe}.checkpoint.json"

    print(f"{'='*72}\n  Day 7 full-corpus extraction\n{'='*72}")
    print(f"  Model:        {args.model}")
    print(f"  Input:        {args.input}")
    print(f"  Results:      {results_path.relative_to(REPO)}")
    print(f"  Failed:       {failed_path.relative_to(REPO)}")
    print(f"  Checkpoint:   {checkpoint_path.relative_to(REPO)}")
    print(f"  Concurrency:  {args.max_workers} workers")

    # --- Load corpus + cluster + filter ---
    df = pd.read_parquet(args.input)
    print(f"\n  Corpus loaded: {len(df):,} records")

    # Optional: merge cluster assignments
    cluster_path = DATA / "cluster_assignments.parquet"
    if cluster_path.exists():
        df_cl = pd.read_parquet(cluster_path)
        df = df.merge(df_cl, on="record_id", how="left")
        if args.exclude_noise and "cluster_id" in df.columns:
            n_before = len(df)
            df = df[df["cluster_id"] >= 0].copy()
            print(f"  After excluding HDBSCAN noise: {len(df):,} "
                  f"(-{n_before-len(df):,})")

    # Filter: must have abstract with ≥100 chars
    mask_abs = df["abstract"].apply(
        lambda x: isinstance(x, str) and len(x.strip()) >= 100
    )
    n_short = (~mask_abs).sum()
    df = df[mask_abs].copy()
    if n_short:
        print(f"  Excluded short abstracts (<100 chars): {n_short:,}")

    # Optionally exclude review papers
    if not args.include_reviews and "doc_type" in df.columns:
        is_review = df["doc_type"].apply(
            lambda x: isinstance(x, str) and any(
                kw in x.lower() for kw in
                ["review", "systematic", "meta-analysis", "metaanalysis"]
            )
        )
        n_rev = is_review.sum()
        df = df[~is_review].copy()
        if n_rev:
            print(f"  Excluded review papers: {n_rev:,}")

    if args.max_records is not None:
        df = df.head(args.max_records)
        print(f"  Limited to first {len(df):,} records (--max-records)")

    print(f"\n  Eligible: {len(df):,}")

    # --- Checkpoint resume ---
    done_ids = load_checkpoint(checkpoint_path)
    if done_ids:
        # Also rebuild from results JSONL in case checkpoint is stale
        for p in [results_path, failed_path]:
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        try:
                            done_ids.add(json.loads(line)["record_id"])
                        except Exception:
                            pass
        print(f"  Checkpoint loaded: {len(done_ids):,} records already processed")
    pending = df[~df["record_id"].isin(done_ids)].copy()
    print(f"  Pending: {len(pending):,}")

    if len(pending) == 0:
        print("\n  ✓ Nothing to do — all records already processed.")
        sys.exit(0)

    # --- Load prompt + worker ---
    here = Path(__file__).parent
    prompt_mod = _import_local(here / "02_prompt.py", "prompt_mod")
    worker = ExtractionWorker(
        model=args.model,
        build_user_prompt=prompt_mod.build_user_prompt,
        system_prompt=prompt_mod.SYSTEM_PROMPT,
        results_path=results_path,
        failed_path=failed_path,
    )

    # --- Concurrent extraction ---
    graceful = GracefulExit()
    rows = pending.to_dict("records")
    n_total = len(rows)
    t_start = time.time()
    last_print = 0
    last_done = len(done_ids)

    def chunks(seq, size):
        for i in range(0, len(seq), size):
            yield seq[i:i + size]

    print(f"\n  Starting extraction...\n  {'='*70}")

    for batch_idx, batch in enumerate(chunks(rows, args.batch_size)):
        if graceful.flag:
            break

        with cf.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
            futures = [pool.submit(worker.process_one, row) for row in batch]
            for fut in cf.as_completed(futures):
                try:
                    fut.result()
                except Exception as e:
                    print(f"  ✗ Worker exception: {type(e).__name__}: {e}")
                if graceful.flag:
                    # Cancel pending; in-flight will complete naturally
                    for f in futures:
                        f.cancel()
                    break

        # Update checkpoint after each batch
        # (re-derive done_ids from JSONL files to be authoritative)
        new_done = set(done_ids)
        for p in [results_path, failed_path]:
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        try:
                            new_done.add(json.loads(line)["record_id"])
                        except Exception:
                            pass
        done_ids = new_done
        write_checkpoint(checkpoint_path, done_ids)

        # Progress
        elapsed = time.time() - t_start
        n_done_now = len(done_ids) - last_done
        rate = n_done_now / elapsed if elapsed > 0 else 0
        eta_min = (n_total - worker.n_processed) / rate / 60 if rate > 0 else float("inf")
        cost = worker.client.estimate_cost_usd()
        print(f"  [batch {batch_idx+1:>4d}] processed {worker.n_processed:>5d}/{n_total} "
              f"(✓{worker.n_success} ✗{worker.n_failed}) "
              f"| {rate:.1f}/s ETA {eta_min:.0f}min "
              f"| tokens {worker.client.total_input_tokens:>9,} in / "
              f"{worker.client.total_output_tokens:>7,} out "
              f"| ~${cost:.2f}")

    elapsed_total = time.time() - t_start
    print(f"\n  {'='*70}")
    print(f"  Done. Processed {worker.n_processed:,} records in {elapsed_total/60:.1f} min")
    print(f"  ✓ Success: {worker.n_success:,}")
    print(f"  ✗ Failed:  {worker.n_failed:,}")
    print(f"  💰 Total estimated cost: ${worker.client.estimate_cost_usd():.2f}")
    print(f"  📁 Results:    {results_path.relative_to(REPO)}")
    print(f"  📁 Failed:     {failed_path.relative_to(REPO)}")
    print(f"  📁 Checkpoint: {checkpoint_path.relative_to(REPO)}")
    print(f"\n  Next: python 05_llm_extraction/10_parse_results.py "
          f"--model {args.model}")


if __name__ == "__main__":
    main()
