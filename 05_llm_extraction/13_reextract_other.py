"""
Day 8 Step 2: Re-extract records where mechanism='other' was assigned.

Uses extended Schema v3 (adds signaling_pathway_modulation +
organ_toxicity_modulation) and updated Prompt v2 (transporter_modulation
includes MRP/BSEP/BCRP/OATP/OCT; new few-shot example for organ toxicity).

Workflow:
  1. Identify record_ids with ≥1 mechanism='other' interaction from
     primary_<model>.interactions.parquet
  2. Pull those abstracts from integrated_corpus.parquet
  3. Re-extract using NEW schema + NEW prompt
  4. Output to primary_<model>.results.v2.jsonl  (only re-extracted records)
  5. AUTO-MERGE: backup v1 → overwrite primary_<model>.results.jsonl
                 with (v1 minus re-extracted) + v2

After completion, run 10_parse_results.py to regenerate parquet with
new mechanism distribution.

CLI:
    python 05_llm_extraction/13_reextract_other.py
        [--model openai/gpt-4o-mini]
        [--prefix primary]
        [--max-workers 5]
        [--batch-size 50]
        [--dry-run]               # only count records, don't extract
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import shutil
import sys
import threading
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
LLM_DIR = DATA / "llm_extraction"
CORPUS_PATH = DATA / "integrated_corpus.parquet"


def _import_local(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def model_safe_name(model: str) -> str:
    return model.replace("/", "__").replace(".", "_")


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/gpt-4o-mini")
    ap.add_argument("--prefix", default="primary")
    ap.add_argument("--max-workers", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--dry-run", action="store_true",
                    help="Only show which records would be re-extracted")
    args = ap.parse_args()

    safe = model_safe_name(args.model)
    interactions_path = LLM_DIR / f"{args.prefix}_{safe}.interactions.parquet"
    main_jsonl = LLM_DIR / f"{args.prefix}_{safe}.results.jsonl"
    v2_jsonl = LLM_DIR / f"{args.prefix}_{safe}.results.v2.jsonl"
    backup_jsonl = LLM_DIR / f"{args.prefix}_{safe}.results.v1_backup.jsonl"
    v2_failed_jsonl = LLM_DIR / f"{args.prefix}_{safe}.results.v2_failed.jsonl"
    v2_checkpoint = LLM_DIR / f"{args.prefix}_{safe}.v2_checkpoint.json"

    print(f"{'='*72}\n  Day 8 — Re-extract 'other' mechanism records\n{'='*72}")
    print(f"  Model:    {args.model}")
    print(f"  Prefix:   {args.prefix}")

    # ------------------------------------------------------------------
    # 1. Find record_ids with mechanism='other'
    # ------------------------------------------------------------------
    if not interactions_path.exists():
        print(f"FATAL: {interactions_path.relative_to(REPO)} not found.")
        print("Run 10_parse_results.py first.")
        sys.exit(1)
    df_int = pd.read_parquet(interactions_path)
    other_ids = set(df_int.loc[df_int["mechanism"] == "other", "record_id"].unique())
    n_other_records = len(other_ids)
    n_other_int = int((df_int["mechanism"] == "other").sum())
    print(f"\n  'other' interactions:      {n_other_int:,}")
    print(f"  Unique record_ids to redo: {n_other_records:,}")

    if n_other_records == 0:
        print("  Nothing to re-extract. Exiting.")
        sys.exit(0)

    # ------------------------------------------------------------------
    # 2. Pull abstracts from corpus
    # ------------------------------------------------------------------
    df_corpus = pd.read_parquet(CORPUS_PATH)
    cluster_path = DATA / "cluster_assignments.parquet"
    if cluster_path.exists():
        df_cl = pd.read_parquet(cluster_path)
        df_corpus = df_corpus.merge(df_cl, on="record_id", how="left")

    df_target = df_corpus[df_corpus["record_id"].isin(other_ids)].copy()
    print(f"  Found in corpus:           {len(df_target):,}")
    if len(df_target) < n_other_records:
        missing = other_ids - set(df_corpus["record_id"])
        print(f"  ⚠️  Missing from corpus:  {len(missing)} record_ids")

    if args.dry_run:
        print("\n  DRY-RUN: not extracting. Top 5 sample:")
        for _, r in df_target.head(5).iterrows():
            print(f"    {r['record_id']}: {(r.get('title') or '')[:60]}...")
        sys.exit(0)

    # ------------------------------------------------------------------
    # 3. Checkpoint: skip already re-extracted records
    # ------------------------------------------------------------------
    done_ids: set[str] = set()
    if v2_checkpoint.exists():
        try:
            done_ids = set(json.loads(v2_checkpoint.read_text(encoding="utf-8")).get("done", []))
        except Exception:
            pass
    for p in [v2_jsonl, v2_failed_jsonl]:
        if p.exists():
            with open(p, encoding="utf-8") as f:
                for line in f:
                    try:
                        done_ids.add(json.loads(line)["record_id"])
                    except Exception:
                        pass
    if done_ids:
        print(f"  Already re-extracted:      {len(done_ids):,}")
    pending = df_target[~df_target["record_id"].isin(done_ids)].copy()
    print(f"  Pending:                   {len(pending):,}")

    # ------------------------------------------------------------------
    # 4. Run extraction (concurrent, same pattern as 09)
    # ------------------------------------------------------------------
    if len(pending) > 0:
        here = Path(__file__).parent
        prompt_mod = _import_local(here / "02_prompt.py", "prompt_mod")
        client_mod = _import_local(here / "03_llm_client.py", "client_mod")

        client = client_mod.LLMClient(model=args.model, log_dir=LLM_DIR)
        file_lock = threading.Lock()
        stats = {"processed": 0, "success": 0, "failed": 0}

        def process_one(row: dict) -> None:
            user_prompt = prompt_mod.build_user_prompt(
                record_id=row["record_id"],
                title=row.get("title") or "",
                abstract=row.get("abstract") or "",
            )
            extraction, meta = client.extract(
                prompt_mod.SYSTEM_PROMPT, user_prompt
            )
            ok = extraction is not None
            out = {
                "record_id": row["record_id"],
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
            with file_lock:
                target = v2_jsonl if ok else v2_failed_jsonl
                with open(target, "a", encoding="utf-8") as f:
                    f.write(json.dumps(out, ensure_ascii=False, default=str) + "\n")
                stats["processed"] += 1
                if ok:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1

        rows = pending.to_dict("records")
        n_total = len(rows)
        t0 = time.time()

        def chunks(seq, size):
            for i in range(0, len(seq), size):
                yield seq[i:i + size]

        print(f"\n  Starting re-extraction with Schema v3 + Prompt v2...\n  {'='*70}")
        for batch_idx, batch in enumerate(chunks(rows, args.batch_size)):
            with cf.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
                futures = [pool.submit(process_one, row) for row in batch]
                for fut in cf.as_completed(futures):
                    try:
                        fut.result()
                    except Exception as e:
                        print(f"  ✗ {type(e).__name__}: {str(e)[:100]}")

            # Update checkpoint
            new_done = set(done_ids)
            for p in [v2_jsonl, v2_failed_jsonl]:
                if p.exists():
                    with open(p, encoding="utf-8") as f:
                        for line in f:
                            try:
                                new_done.add(json.loads(line)["record_id"])
                            except Exception:
                                pass
            done_ids = new_done
            tmp = v2_checkpoint.with_suffix(v2_checkpoint.suffix + ".tmp")
            tmp.write_text(
                json.dumps({"done": sorted(done_ids), "n_done": len(done_ids)},
                           ensure_ascii=False), encoding="utf-8"
            )
            tmp.replace(v2_checkpoint)

            elapsed = time.time() - t0
            rate = stats["processed"] / elapsed if elapsed > 0 else 0
            eta_min = (n_total - stats["processed"]) / rate / 60 if rate > 0 else float("inf")
            cost = client.estimate_cost_usd()
            print(f"  [batch {batch_idx+1:>3d}] {stats['processed']:>4d}/{n_total} "
                  f"(✓{stats['success']} ✗{stats['failed']}) "
                  f"| {rate:.2f}/s ETA {eta_min:.1f}min "
                  f"| tokens {client.total_input_tokens:>7,}/{client.total_output_tokens:>5,} "
                  f"| ~${cost:.3f}")

        elapsed_total = time.time() - t0
        print(f"\n  Re-extraction done. {stats['processed']:,} records in {elapsed_total/60:.1f} min")
        print(f"  💰 Re-extraction cost: ${client.estimate_cost_usd():.3f}")

    # ------------------------------------------------------------------
    # 5. AUTO-MERGE: replace v1 records with v2 where re-extracted
    # ------------------------------------------------------------------
    print(f"\n  Auto-merging v2 into main JSONL...")

    if not backup_jsonl.exists():
        shutil.copy(main_jsonl, backup_jsonl)
        print(f"  → V1 backup created: {backup_jsonl.relative_to(REPO)}")
    else:
        print(f"  → V1 backup already exists (not overwritten): "
              f"{backup_jsonl.relative_to(REPO)}")

    # Load v2 records into dict
    v2_dict: dict[str, str] = {}
    if v2_jsonl.exists():
        with open(v2_jsonl, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    v2_dict[d["record_id"]] = line
                except Exception:
                    pass
    print(f"  V2 records loaded:  {len(v2_dict):,}")

    n_replaced = 0
    n_kept = 0
    out_lines: list[str] = []
    with open(backup_jsonl, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                if d["record_id"] in v2_dict:
                    out_lines.append(v2_dict[d["record_id"]])
                    n_replaced += 1
                else:
                    out_lines.append(line)
                    n_kept += 1
            except Exception:
                out_lines.append(line)

    with open(main_jsonl, "w", encoding="utf-8") as f:
        for ln in out_lines:
            f.write(ln + "\n")

    print(f"  Replaced: {n_replaced:,} record extractions (now using Schema v3)")
    print(f"  Kept:     {n_kept:,} record extractions (unchanged from v1)")
    print(f"  → {main_jsonl.relative_to(REPO)} (now MERGED v1+v2)")

    print(f"\n  {'='*70}")
    print(f"  NEXT: regenerate parquet + see new mechanism distribution:")
    print(f"     python 05_llm_extraction/10_parse_results.py --model {args.model}")
    print(f"\n  To roll back to v1 (just in case):")
    print(f"     cp {backup_jsonl.name} {main_jsonl.name}")


if __name__ == "__main__":
    main()
