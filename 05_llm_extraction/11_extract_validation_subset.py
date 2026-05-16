"""
Day 7 cross-validation extraction.

Re-extracts the 500-abstract stratified validation subset using a second
LLM (default: Claude Sonnet 4.6) for inter-model concordance assessment.

Output files use the `secondary_` prefix to distinguish from the primary
9,413 extraction:
    secondary_<model>.results.jsonl
    secondary_<model>.failed.jsonl
    secondary_<model>.checkpoint.json

After this finishes, run 10_parse_results.py with --prefix secondary
to get the matched records / interactions parquets, then run a separate
agreement-analysis script to compute Jaccard / κ on (herb, drug) pairs.

CLI usage:
    python 05_llm_extraction/11_extract_validation_subset.py
        [--model anthropic/claude-sonnet-4.6]
        [--max-workers 5]
        [--batch-size 50]
        [--max-records N]   # for cheap dry-run
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

VALIDATION_INPUT = DATA / "llm_validation_500.parquet"


# ----------------------------------------------------------------------
def _import_local(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def model_safe_name(model: str) -> str:
    return model.replace("/", "__").replace(".", "_")


def load_checkpoint(checkpoint_path: Path) -> set[str]:
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
                   ensure_ascii=False), encoding="utf-8")
    tmp.replace(checkpoint_path)


# ----------------------------------------------------------------------
class ExtractionWorker:
    """Same design as 09_extract_full_corpus.py; output prefix='secondary'."""

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
        self._file_lock = threading.Lock()
        self.n_processed = 0
        self.n_success = 0
        self.n_failed = 0

    def process_one(self, row: dict) -> dict:
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


class GracefulExit:
    def __init__(self):
        self.flag = False
        signal.signal(signal.SIGINT, self._h)

    def _h(self, *_):
        print("\n\n⚠️  Ctrl+C received. Finishing in-flight, then exiting...\n"
              "    Resume with the same command.\n")
        self.flag = True


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="anthropic/claude-sonnet-4.6")
    ap.add_argument("--max-records", type=int, default=None)
    ap.add_argument("--max-workers", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=50)
    args = ap.parse_args()

    if not VALIDATION_INPUT.exists():
        print(f"FATAL: {VALIDATION_INPUT.relative_to(REPO)} not found.")
        print("Run: python 05_llm_extraction/04_stratified_sample.py first.")
        sys.exit(1)

    safe = model_safe_name(args.model)
    results_path = OUT_DIR / f"secondary_{safe}.results.jsonl"
    failed_path = OUT_DIR / f"secondary_{safe}.failed.jsonl"
    checkpoint_path = OUT_DIR / f"secondary_{safe}.checkpoint.json"

    print(f"{'='*72}\n  Day 7 cross-validation extraction (500-subset)\n{'='*72}")
    print(f"  Model:        {args.model}")
    print(f"  Input:        {VALIDATION_INPUT.relative_to(REPO)} (500 stratified)")
    print(f"  Results:      {results_path.relative_to(REPO)}")
    print(f"  Failed:       {failed_path.relative_to(REPO)}")
    print(f"  Concurrency:  {args.max_workers} workers")

    df = pd.read_parquet(VALIDATION_INPUT)
    print(f"\n  Loaded validation subset: {len(df):,} records")
    if args.max_records:
        df = df.head(args.max_records)
        print(f"  Limited to first {len(df):,} (--max-records)")

    done_ids = load_checkpoint(checkpoint_path)
    if done_ids:
        for p in [results_path, failed_path]:
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        try:
                            done_ids.add(json.loads(line)["record_id"])
                        except Exception:
                            pass
        print(f"  Checkpoint: {len(done_ids):,} already done")
    pending = df[~df["record_id"].isin(done_ids)].copy()
    print(f"  Pending:    {len(pending):,}")

    if len(pending) == 0:
        print("\n  ✓ Nothing to do — all validation records already extracted.")
        sys.exit(0)

    here = Path(__file__).parent
    prompt_mod = _import_local(here / "02_prompt.py", "prompt_mod")
    worker = ExtractionWorker(
        model=args.model,
        build_user_prompt=prompt_mod.build_user_prompt,
        system_prompt=prompt_mod.SYSTEM_PROMPT,
        results_path=results_path,
        failed_path=failed_path,
    )

    graceful = GracefulExit()
    rows = pending.to_dict("records")
    n_total = len(rows)
    t0 = time.time()

    def chunks(seq, size):
        for i in range(0, len(seq), size):
            yield seq[i:i + size]

    print(f"\n  Starting cross-validation extraction...\n  {'='*70}")
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
                    for f in futures:
                        f.cancel()
                    break

        # Update checkpoint from JSONL (authoritative)
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

        elapsed = time.time() - t0
        rate = worker.n_processed / elapsed if elapsed > 0 else 0
        eta_min = (n_total - worker.n_processed) / rate / 60 if rate > 0 else float("inf")
        cost = worker.client.estimate_cost_usd()
        print(f"  [batch {batch_idx+1:>3d}] {worker.n_processed:>4d}/{n_total} "
              f"(✓{worker.n_success} ✗{worker.n_failed}) "
              f"| {rate:.2f}/s ETA {eta_min:.1f}min "
              f"| tokens {worker.client.total_input_tokens:>8,} in / "
              f"{worker.client.total_output_tokens:>6,} out "
              f"| ~${cost:.2f}")

    elapsed_total = time.time() - t0
    print(f"\n  {'='*70}")
    print(f"  Done. {worker.n_processed:,} records in {elapsed_total/60:.1f} min")
    print(f"  ✓ Success: {worker.n_success:,}")
    print(f"  ✗ Failed:  {worker.n_failed:,}")
    print(f"  💰 Cost:   ${worker.client.estimate_cost_usd():.2f}")
    print(f"\n  Next steps:")
    print(f"    1. python 05_llm_extraction/10_parse_results.py "
          f"--model {args.model} --prefix secondary")
    print(f"    2. Compute Jaccard / κ agreement vs primary "
          f"(separate analysis script).")


if __name__ == "__main__":
    main()
