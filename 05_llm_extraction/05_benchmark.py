"""
Day 6 benchmark: compare 4 LLM models on 50 stratified abstracts.

Metrics computed (gold-standard-free):
  - Validation rate: % responses passing Pydantic schema
  - HDI detection rate: % abstracts flagged contains_hdi=True
  - Avg interactions per abstract (recall proxy)
  - Avg confidence
  - Cost per abstract (USD)
  - Time per abstract (sec)
  - Inter-model agreement: Jaccard on extracted (herb, drug) pairs

Outputs:
  results/llm_benchmark/<model>.jsonl        # per-call audit log
  results/llm_benchmark/results_<model>.json # per-model extraction results
  results/llm_benchmark/benchmark_summary.csv
  results/llm_benchmark/benchmark_review.md  # 10 sample cases × 4 models, hand-review

Pre-flight checks:
  - OPENROUTER_API_KEY set
  - Requested model IDs available on OpenRouter
  - Benchmark sample file exists
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
OUT_DIR = REPO / "results" / "llm_benchmark"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BENCHMARK_INPUT = DATA / "llm_benchmark_50.parquet"

# Models to benchmark — verify IDs at https://openrouter.ai/models
# Opus 4.6 commented to save cost in first pass; uncomment if Sonnet insufficient
MODELS = [
    "openai/gpt-5-mini",
    "anthropic/claude-haiku-4.5",
    "openai/gpt-5.5",
    # "anthropic/claude-opus-4.6",
]


# ----------------------------------------------------------------------
def _import_local(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    here = Path(__file__).parent
    schema_mod = _import_local(here / "01_schema.py", "schema_mod")
    prompt_mod = _import_local(here / "02_prompt.py", "prompt_mod")
    client_mod = _import_local(here / "03_llm_client.py", "client_mod")

    SYSTEM_PROMPT = prompt_mod.SYSTEM_PROMPT
    build_user_prompt = prompt_mod.build_user_prompt
    LLMClient = client_mod.LLMClient
    check_models_available = client_mod.check_models_available

    # --- Pre-flight: input file ---
    if not BENCHMARK_INPUT.exists():
        print(f"FATAL: {BENCHMARK_INPUT.relative_to(REPO)} not found.")
        print("Run: python 05_llm_extraction/04_stratified_sample.py")
        sys.exit(1)
    df = pd.read_parquet(BENCHMARK_INPUT)
    print(f"Loaded {len(df)} benchmark abstracts "
          f"from {BENCHMARK_INPUT.relative_to(REPO)}")

    # --- Pre-flight: model availability ---
    print("\nChecking OpenRouter model availability...")
    missing = check_models_available(MODELS)
    if missing:
        print(f"\nFATAL: {len(missing)} model IDs not found. Fix MODELS list, exit.")
        sys.exit(1)
    print("  ✓ All models available")

    # --- Run benchmark ---
    summary_rows: list[dict] = []
    all_results: dict[str, list[dict]] = {}

    for model_id in MODELS:
        print(f"\n{'='*72}\n{model_id}\n{'='*72}")
        client = LLMClient(model=model_id, log_dir=OUT_DIR)
        t_start = time.time()
        results: list[dict] = []

        for i, row in df.reset_index(drop=True).iterrows():
            user_prompt = build_user_prompt(
                record_id=row["record_id"],
                title=row["title"],
                abstract=row["abstract"],
            )
            extraction, meta = client.extract(SYSTEM_PROMPT, user_prompt)

            n_int = len(extraction.interactions) if extraction else 0
            contains = extraction.contains_hdi if extraction else None

            results.append({
                "record_id": row["record_id"],
                "cluster_id": int(row["cluster_id"]),
                "year": int(row["year"]) if pd.notna(row["year"]) else None,
                "title": row["title"][:120] if isinstance(row["title"], str) else "",
                "contains_hdi": contains,
                "n_interactions": n_int,
                "extraction": extraction.model_dump() if extraction else None,
                "validation_attempts": meta["n_attempts"],
                "validation_failures": meta["validation_failures"],
                "elapsed_s": meta["elapsed_s"],
                "input_tokens": meta["input_tokens"],
                "output_tokens": meta["output_tokens"],
                "success": extraction is not None,
                "error": meta["error"],
            })
            status = "✓" if extraction else "✗"
            print(f"  [{i+1:2d}/{len(df)}] {status} "
                  f"{row['record_id'][:35]:35s} "
                  f"hdi={str(contains)[:5]:5s} n={n_int} "
                  f"att={meta['n_attempts']} t={meta['elapsed_s']:.1f}s")

        elapsed_total = time.time() - t_start
        all_results[model_id] = results

        # Per-model summary
        n_success = sum(r["success"] for r in results)
        n_with_hdi = sum(1 for r in results if r["contains_hdi"] is True)
        total_int = sum(r["n_interactions"] for r in results)
        cost = client.estimate_cost_usd()

        # Avg confidence on successful interactions
        confidences = [
            iv["confidence"]
            for r in results if r["extraction"]
            for iv in r["extraction"]["interactions"]
        ]
        avg_conf = round(sum(confidences) / len(confidences), 3) if confidences else None

        summary_rows.append({
            "model": model_id,
            "n_total": len(df),
            "n_validated": n_success,
            "validation_rate": round(n_success / len(df), 3),
            "n_with_hdi": n_with_hdi,
            "hdi_detection_rate": round(n_with_hdi / len(df), 3),
            "total_interactions": total_int,
            "avg_int_per_abstract": round(total_int / len(df), 2),
            "avg_confidence": avg_conf,
            "total_input_tokens": client.total_input_tokens,
            "total_output_tokens": client.total_output_tokens,
            "estimated_cost_usd": cost,
            "cost_per_abstract_usd": round(cost / len(df), 4) if cost > 0 else None,
            "elapsed_min": round(elapsed_total / 60, 2),
            "avg_validation_attempts": round(
                sum(r["validation_attempts"] for r in results) / len(df), 2
            ),
        })

        results_path = OUT_DIR / f"results_{model_id.replace('/', '__')}.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n  Cost: ${cost:.4f}  Time: {elapsed_total/60:.1f}min  "
              f"Success: {n_success}/{len(df)}  HDI: {n_with_hdi}/{len(df)}")

    # --- Comparison summary ---
    summary_df = pd.DataFrame(summary_rows)
    summary_path = OUT_DIR / "benchmark_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    print(f"\n\n{'='*72}\nBENCHMARK SUMMARY\n{'='*72}")
    print(summary_df.to_string(index=False))
    print(f"\n→ {summary_path.relative_to(REPO)}")

    # --- Inter-model Jaccard agreement on (herb, drug) pairs ---
    print(f"\n{'='*72}\nINTER-MODEL AGREEMENT (Jaccard on herb-drug pairs)\n{'='*72}")
    pairs_by_model: dict[str, set[tuple[str, str]]] = {}
    for m in MODELS:
        pairs: set[tuple[str, str]] = set()
        for r in all_results[m]:
            if not r["extraction"]:
                continue
            for iv in r["extraction"]["interactions"]:
                herb = (iv.get("herb_name_latin") or iv.get("herb_common_name")
                        or iv.get("herb_active_compound") or "").strip().lower()
                drug = (iv.get("drug_name") or "").strip().lower()
                if herb and drug:
                    pairs.add((herb, drug))
        pairs_by_model[m] = pairs

    print(f"{'Model':40s} {'unique (herb,drug)':>22s}")
    for m, pairs in pairs_by_model.items():
        print(f"{m:40s} {len(pairs):>22d}")
    print(f"\nPairwise Jaccard:")
    print(f"{'Model A':40s} {'Model B':40s} {'Jaccard':>8s} {'|A∩B|':>6s}")
    for i, m1 in enumerate(MODELS):
        for m2 in MODELS[i+1:]:
            a, b = pairs_by_model[m1], pairs_by_model[m2]
            union = a | b
            jac = len(a & b) / len(union) if union else 0.0
            print(f"{m1:40s} {m2:40s} {jac:>8.3f} {len(a & b):>6d}")

    # --- Hand-review markdown: 10 random sample cases × all models ---
    review_path = OUT_DIR / "benchmark_review.md"
    review_indices = list(range(min(10, len(df))))
    lines = ["# Day 6 Benchmark Hand-Review\n",
             f"Compare 4 models on 10 sample abstracts (out of {len(df)}). "
             "Use this to qualitatively judge extraction accuracy.\n"]
    for idx in review_indices:
        rec_id = df.iloc[idx]["record_id"]
        title = df.iloc[idx]["title"]
        abstract = df.iloc[idx]["abstract"]
        lines.append(f"\n---\n\n## Case {idx+1}: `{rec_id}` (cluster {df.iloc[idx]['cluster_id']})\n")
        lines.append(f"**Title**: {title}\n")
        lines.append(f"**Abstract** (first 600 chars):\n> {abstract[:600]}{'...' if len(abstract) > 600 else ''}\n")
        for m in MODELS:
            r = next(x for x in all_results[m] if x["record_id"] == rec_id)
            lines.append(f"\n### Model: `{m}`")
            if not r["extraction"]:
                lines.append(f"❌ **Failed**: {r['error']}")
                continue
            lines.append(f"- contains_hdi: **{r['extraction']['contains_hdi']}**, "
                         f"n={r['n_interactions']}, "
                         f"validation_attempts={r['validation_attempts']}")
            for j, iv in enumerate(r["extraction"]["interactions"][:3]):
                lines.append(f"  - **Interaction {j+1}**: "
                             f"`{iv.get('herb_common_name') or iv.get('herb_name_latin')}` "
                             f"× `{iv.get('drug_name')}` "
                             f"| {iv.get('mechanism')} | "
                             f"{iv.get('direction')} | conf={iv.get('confidence')}")
                lines.append(f"    > {iv.get('evidence_quote', '')[:200]}")
    review_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n→ {review_path.relative_to(REPO)} (hand-review 10 cases)")

    print(f"\n{'='*72}\nDONE. Review the summary CSV + markdown to pick the main model.\n{'='*72}")


if __name__ == "__main__":
    main()
