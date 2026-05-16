"""
Day 5 Block 1: SPECTER2 embedding of 9,413 main corpus abstracts.

Model: allenai/specter2_base (Cohan et al. 2020) + proximity adapter
       (Singh et al. 2023 SciRepEval). Proximity is the task-specific adapter
       designed for clustering / similarity / nearest-neighbor retrieval —
       directly aligned with our downstream HDBSCAN clustering.

Input format: `title [SEP] abstract` (SPECTER2 standard).
Truncation:   head+tail when title+abstract > 512 tokens (Sun et al. 2019),
              with 75/25 split of available budget after preserving title.
Fallback:     title-only for the ~3% of records without abstract.

Outputs:
  data/processed/specter2_embeddings.npy        # (9413, 768) float32, ~28 MB
  data/processed/specter2_embeddings_meta.json  # record_id order + config

Run from repo root (CPU inference, ~30-45 min for 9,413 docs):
  python 04_keyword_topic/07_block1_specter2_embedding.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoTokenizer
from adapters import AutoAdapterModel

# ----------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[1]
CORPUS_PATH = REPO / "data" / "processed" / "integrated_corpus.parquet"
OUT_DIR = REPO / "data" / "processed"
OUT_EMB = OUT_DIR / "specter2_embeddings.npy"
OUT_META = OUT_DIR / "specter2_embeddings_meta.json"

MODEL_NAME = "allenai/specter2_base"
ADAPTER_NAME = "allenai/specter2"  # proximity adapter
MAX_LENGTH = 512
HEAD_RATIO = 0.75  # for head+tail truncation of abstract
BATCH_SIZE = 8     # CPU-conservative
EMBED_DIM = 768

DEVICE = torch.device("cpu")


# ----------------------------------------------------------------------
def smart_truncate(
    title: str,
    abstract: str | None,
    tokenizer,
    max_length: int = MAX_LENGTH,
) -> tuple[str, int]:
    """
    Build SPECTER2 input `title [SEP] abstract` with head+tail truncation
    when total exceeds max_length tokens. Title is always preserved in full.

    Returns: (joined_text, original_token_count)
    """
    sep = tokenizer.sep_token

    title = (title or "").strip()
    abstract = (abstract or "").strip() if isinstance(abstract, str) else ""

    if not abstract:
        # title-only fallback
        full = title
        full_ids = tokenizer.encode(full, add_special_tokens=False)
        return full, len(full_ids)

    # Pre-tokenize parts (no special tokens)
    title_ids = tokenizer.encode(title, add_special_tokens=False)
    abs_ids = tokenizer.encode(abstract, add_special_tokens=False)
    sep_ids = tokenizer.encode(sep, add_special_tokens=False)

    # 2 reserved for [CLS] and final [SEP] added by tokenizer
    budget_total = max_length - 2
    n_total = len(title_ids) + len(sep_ids) + len(abs_ids)

    if n_total <= budget_total:
        return f"{title}{sep}{abstract}", n_total

    # Truncate abstract head+tail; keep title intact
    budget_abs = max(0, budget_total - len(title_ids) - len(sep_ids))
    if budget_abs <= 0:
        # Pathological: title alone fills budget (extremely rare)
        return title, len(title_ids)

    head_n = int(budget_abs * HEAD_RATIO)
    tail_n = budget_abs - head_n
    if tail_n > 0:
        trunc_abs_ids = abs_ids[:head_n] + abs_ids[-tail_n:]
    else:
        trunc_abs_ids = abs_ids[:head_n]
    trunc_abs = tokenizer.decode(trunc_abs_ids, skip_special_tokens=True)
    return f"{title}{sep}{trunc_abs}", n_total


def batch_iter(seq, n):
    for i in range(0, len(seq), n):
        yield i, seq[i : i + n]


# ----------------------------------------------------------------------
def main():
    t0 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] Loading corpus...")
    df = pd.read_parquet(CORPUS_PATH)
    assert len(df) == 9413, f"Expected 9413 rows, got {len(df)}"
    assert 2026 not in df["year"].values, "year=2026 still in main (re-run 06c)"
    print(f"  Corpus: {len(df):,} rows, years {df['year'].min()}-{df['year'].max()}")

    print(f"[{time.strftime('%H:%M:%S')}] Loading SPECTER2 + proximity adapter...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoAdapterModel.from_pretrained(MODEL_NAME)
    model.load_adapter(
        ADAPTER_NAME,
        source="hf",
        load_as="proximity",
        set_active=True,
    )
    # adapters 1.x quirk: set_active=True at load doesn't propagate to forward.
    # Must call set_active_adapters() explicitly, then re-enter eval mode.
    model.set_active_adapters("proximity")
    assert model.active_adapters is not None, \
        "FATAL: proximity adapter loaded but not active for forward pass"
    model.to(DEVICE)
    model.eval()
    n_params = sum(p.numel() for p in model.parameters()) / 1e6
    print(f"  Model loaded: {n_params:.1f}M params on {DEVICE}")
    print(f"  Active adapter: {model.active_adapters}")

    # Construct input texts in record_id order (preserved for downstream join)
    print(f"[{time.strftime('%H:%M:%S')}] Building input texts...")
    df = df.reset_index(drop=True)
    record_ids = df["record_id"].tolist()
    titles = df["title"].fillna("").tolist()
    abstracts = df["abstract"].tolist()

    texts: list[str] = []
    tok_lengths: list[int] = []
    n_title_only = 0
    n_truncated = 0
    for ti, ab in zip(titles, abstracts):
        text, n_tok = smart_truncate(ti, ab, tokenizer)
        texts.append(text)
        tok_lengths.append(n_tok)
        if not (isinstance(ab, str) and ab.strip()):
            n_title_only += 1
        if n_tok > MAX_LENGTH - 2:
            n_truncated += 1
    print(f"  Title-only fallback: {n_title_only} ({n_title_only/len(df)*100:.1f}%)")
    print(f"  Head+tail truncated: {n_truncated} ({n_truncated/len(df)*100:.1f}%)")
    print(f"  Token length stats (original): mean={np.mean(tok_lengths):.0f}, "
          f"p95={np.percentile(tok_lengths, 95):.0f}, "
          f"max={max(tok_lengths)}")

    # Pre-allocate output
    embeddings = np.zeros((len(df), EMBED_DIM), dtype=np.float32)

    print(f"[{time.strftime('%H:%M:%S')}] Encoding with batch_size={BATCH_SIZE}...")
    n_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
    pbar = tqdm(total=len(texts), unit="doc", smoothing=0.1)

    try:
        with torch.inference_mode():
            for start, batch_texts in batch_iter(texts, BATCH_SIZE):
                enc = tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=MAX_LENGTH,
                    return_tensors="pt",
                    return_token_type_ids=False,
                )
                enc = {k: v.to(DEVICE) for k, v in enc.items()}
                out = model(**enc)
                # SPECTER/SPECTER2 convention: [CLS] token
                cls_emb = out.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings[start : start + len(batch_texts)] = cls_emb.astype(np.float32)
                pbar.update(len(batch_texts))

                # Periodic checkpoint every 50 batches (~400 docs)
                if (start // BATCH_SIZE) % 50 == 49:
                    np.save(OUT_EMB, embeddings)
    except KeyboardInterrupt:
        pbar.close()
        np.save(OUT_EMB, embeddings)
        print(f"\n[INTERRUPT] Partial embeddings saved to {OUT_EMB}")
        print(f"  Completed: {pbar.n}/{len(texts)} ({pbar.n/len(texts)*100:.1f}%)")
        raise
    pbar.close()

    # Final save
    np.save(OUT_EMB, embeddings)
    elapsed = time.time() - t0

    # Sanity checks
    norms = np.linalg.norm(embeddings, axis=1)
    n_zero = int((norms == 0).sum())
    print(f"\n[{time.strftime('%H:%M:%S')}] Encoding complete.")
    print(f"  Elapsed: {elapsed/60:.1f} min")
    print(f"  Output:  {OUT_EMB} ({embeddings.nbytes/1024/1024:.1f} MB)")
    print(f"  Shape:   {embeddings.shape}, dtype={embeddings.dtype}")
    print(f"  Norm:    mean={norms.mean():.3f}, "
          f"min={norms.min():.3f}, max={norms.max():.3f}")
    print(f"  Zero-norm vectors (bug check): {n_zero}")
    assert n_zero == 0, "FATAL: some embeddings are zero — check inference loop"

    # Metadata sidecar
    meta = {
        "model": MODEL_NAME,
        "adapter": ADAPTER_NAME,
        "adapter_role": "proximity (clustering/similarity)",
        "max_length": MAX_LENGTH,
        "truncation": f"head+tail {HEAD_RATIO}/{1-HEAD_RATIO}",
        "batch_size": BATCH_SIZE,
        "n_records": len(df),
        "embed_dim": EMBED_DIM,
        "n_title_only_fallback": n_title_only,
        "n_truncated": n_truncated,
        "device": str(DEVICE),
        "elapsed_min": round(elapsed / 60, 2),
        "record_ids": record_ids,  # row-aligned with embeddings.npy
        "citations": [
            "Cohan et al. 2020. SPECTER: Document-level Representation Learning "
            "using Citation-informed Transformers. ACL.",
            "Singh et al. 2023. SciRepEval: A Multi-Format Benchmark for "
            "Scientific Document Representations. EMNLP.",
            "Sun et al. 2019. How to Fine-Tune BERT for Text Classification? CCL.",
        ],
    }
    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  Meta:    {OUT_META}")


if __name__ == "__main__":
    main()
