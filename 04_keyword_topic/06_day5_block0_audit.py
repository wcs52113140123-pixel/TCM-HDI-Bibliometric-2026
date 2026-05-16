"""
Day 5 Block 0: Audit input data + environment for topic modeling.

Outputs:
  - Console summary
  - results/audits/day5_block0_audit.md (markdown report for review)

Run from repo root:
  conda activate tcm-hdi
  python 04_keyword_topic/06_day5_block0_audit.py
"""

from __future__ import annotations

import importlib
import importlib.metadata as ilmd
import sys
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "processed"
OUT_DIR = REPO_ROOT / "results" / "audits"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = OUT_DIR / "day5_block0_audit.md"

MAIN_CORPUS = DATA_DIR / "integrated_corpus.parquet"
PARTIAL_CORPUS = DATA_DIR / "integrated_corpus_partial2026.parquet"

# Packages needed for Day 5 Blocks 1-6
REQUIRED_PKGS = {
    # Block 1: embedding
    "torch": "PyTorch (CPU build is fine)",
    "transformers": "HuggingFace transformers (loads SPECTER2)",
    "sentence_transformers": "sentence-transformers (optional alt encoder)",
    "adapters": "adapter-transformers (for SPECTER2 task-specific adapter)",
    # Block 2: cluster + reduce
    "umap": "umap-learn (UMAP dimensionality reduction)",
    "hdbscan": "HDBSCAN clustering",
    "sklearn": "scikit-learn (TF-IDF for topic labels)",
    # Block 3-4: orchestration + viz
    "bertopic": "BERTopic (optional all-in-one wrapper)",
    "plotly": "plotly (topic viz)",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
}

# Heuristic candidate column names across DBs
ABSTRACT_CANDIDATES = ["abstract", "AB", "Abstract", "abstract_text", "abs"]
TITLE_CANDIDATES = ["title", "TI", "Title", "article_title"]
YEAR_CANDIDATES = ["year", "PY", "Year", "publication_year", "pub_year"]


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def detect_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first matching column name, case-insensitive fallback."""
    for c in candidates:
        if c in df.columns:
            return c
    lowered = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lowered:
            return lowered[c.lower()]
    return None


def check_pkg(name: str) -> tuple[bool, str]:
    """Return (installed, version_or_error)."""
    try:
        importlib.import_module(name)
        try:
            ver = ilmd.version(name.replace("_", "-"))
        except ilmd.PackageNotFoundError:
            try:
                ver = ilmd.version(name)
            except ilmd.PackageNotFoundError:
                ver = "imported, version unknown"
        return True, ver
    except ImportError as e:
        return False, str(e)


def n_tokens_estimate(text: str, tokenizer=None) -> int:
    """Token count: SPECTER2 tokenizer if available, else word-count heuristic."""
    if not isinstance(text, str) or not text.strip():
        return 0
    if tokenizer is not None:
        return len(tokenizer.encode(text, add_special_tokens=False))
    # Fallback: words * 1.3 (rough BERT subword inflation for English)
    return int(len(text.split()) * 1.3)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    lines: list[str] = []

    def log(msg: str):
        print(msg)
        lines.append(msg)

    log("# Day 5 Block 0 — Audit Report\n")
    log(f"- Repo root: `{REPO_ROOT}`")
    log(f"- Python: `{sys.version.split()[0]}` @ `{sys.executable}`")
    log("")

    # ---------------- Part A: Environment ----------------
    log("## A. Environment Check\n")
    log("| Package | Installed | Version | Purpose |")
    log("|---|---|---|---|")
    missing = []
    for pkg, purpose in REQUIRED_PKGS.items():
        ok, info = check_pkg(pkg)
        mark = "✅" if ok else "❌"
        ver = info if ok else "MISSING"
        log(f"| `{pkg}` | {mark} | `{ver}` | {purpose} |")
        if not ok:
            missing.append(pkg)
    log("")
    if missing:
        log(f"**Missing packages**: `{', '.join(missing)}`")
        log("Install hint (CPU-only):")
        log("```")
        log(f"pip install {' '.join(p.replace('_', '-') for p in missing)}")
        log("```")
    else:
        log("All required packages installed.")
    log("")

    # Try loading SPECTER2 tokenizer (small download, validates HF reachability)
    tokenizer = None
    log("### SPECTER2 tokenizer reachability\n")
    try:
        from transformers import AutoTokenizer  # noqa: WPS433
        tokenizer = AutoTokenizer.from_pretrained("allenai/specter2_base")
        log("✅ SPECTER2 tokenizer loaded successfully (HuggingFace reachable).")
    except Exception as e:
        log(f"⚠️  SPECTER2 tokenizer load failed: `{type(e).__name__}: {e}`")
        log("Token counts below will fall back to word*1.3 heuristic.")
        log("If HF is blocked, configure HF_ENDPOINT=https://hf-mirror.com")
    log("")

    # ---------------- Part B: Data files ----------------
    log("## B. Data Files\n")
    for f in [MAIN_CORPUS, PARTIAL_CORPUS]:
        if f.exists():
            size_mb = f.stat().st_size / 1024 / 1024
            log(f"- ✅ `{f.relative_to(REPO_ROOT)}` ({size_mb:.1f} MB)")
        else:
            log(f"- ❌ MISSING: `{f.relative_to(REPO_ROOT)}`")
    log("")

    if not MAIN_CORPUS.exists():
        log("**FATAL**: main corpus missing — cannot proceed.")
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        return

    # ---------------- Part C: Schema ----------------
    df = pd.read_parquet(MAIN_CORPUS)
    log("## C. Main Corpus Schema (9,438 expected)\n")
    log(f"- Shape: **{df.shape[0]:,} rows × {df.shape[1]} cols**")
    log(f"- Columns: `{list(df.columns)}`")
    log("")

    abs_col = detect_col(df, ABSTRACT_CANDIDATES)
    title_col = detect_col(df, TITLE_CANDIDATES)
    year_col = detect_col(df, YEAR_CANDIDATES)
    log(f"- Detected abstract column: `{abs_col}`")
    log(f"- Detected title column:    `{title_col}`")
    log(f"- Detected year column:     `{year_col}`")
    log("")

    if abs_col is None or title_col is None or year_col is None:
        log("**WARN**: missing essential column(s). Full column list above — "
            "please tell me which column holds which field if heuristic failed.")

    # ---------------- Part D: Coverage ----------------
    log("## D. Coverage (title / abstract)\n")
    n = len(df)
    if title_col:
        n_title = df[title_col].notna().sum()
        log(f"- Title:    {n_title:,} / {n:,} = **{n_title/n*100:.1f}%**")
    if abs_col:
        has_abs = df[abs_col].apply(
            lambda x: isinstance(x, str) and bool(x.strip())
        )
        non_empty_abs = int(has_abs.sum())
        log(f"- Abstract: {non_empty_abs:,} / {n:,} = **{non_empty_abs/n*100:.1f}%**")
        if title_col:
            has_title = df[title_col].apply(
                lambda x: isinstance(x, str) and bool(x.strip())
            )
            n_both = int((has_abs & has_title).sum())
            log(f"- Both title+abstract: {n_both:,} / {n:,} = **{n_both/n*100:.1f}%**")
    log("")

    # ---------------- Part E: Token length distribution ----------------
    log("## E. Abstract Token Length (SPECTER2 max=512)\n")
    if abs_col:
        sample = df[df[abs_col].apply(
            lambda x: isinstance(x, str) and len(x.strip()) > 0
        )]
        # For speed: tokenize ALL if <1000 rows, else random 1000-sample
        if len(sample) > 1000:
            sample = sample.sample(n=1000, random_state=42)
            log(f"_(sampled 1,000 of {non_empty_abs:,} non-empty abstracts)_")
        text_lengths = sample[abs_col].apply(lambda t: n_tokens_estimate(t, tokenizer))
        log(f"- mean:   {text_lengths.mean():.0f}")
        log(f"- median: {text_lengths.median():.0f}")
        log(f"- p95:    {text_lengths.quantile(0.95):.0f}")
        log(f"- p99:    {text_lengths.quantile(0.99):.0f}")
        log(f"- max:    {text_lengths.max():.0f}")
        over_512 = (text_lengths > 512).sum()
        log(f"- **>512 tokens (will need truncation): "
            f"{over_512}/{len(sample)} = {over_512/len(sample)*100:.1f}%**")
    log("")

    # ---------------- Part F: Year coverage ----------------
    log("## F. Abstract Coverage by Year\n")
    if year_col and abs_col:
        df["_has_abs"] = df[abs_col].apply(
            lambda x: isinstance(x, str) and len(x.strip()) > 0
        )
        yr_cov = df.groupby(year_col)["_has_abs"].agg(["sum", "count"])
        yr_cov["pct"] = yr_cov["sum"] / yr_cov["count"] * 100
        log("| Year | n records | with abstract | coverage |")
        log("|---|---|---|---|")
        for yr, row in yr_cov.iterrows():
            log(f"| {int(yr)} | {int(row['count']):,} | {int(row['sum']):,} "
                f"| {row['pct']:.1f}% |")
        df.drop(columns="_has_abs", inplace=True)
    log("")

    # ---------------- Part G: Partial 2026 ----------------
    log("## G. Partial 2026 Status\n")
    if PARTIAL_CORPUS.exists():
        df2 = pd.read_parquet(PARTIAL_CORPUS)
        log(f"- Shape: {df2.shape[0]:,} rows")
        if abs_col and abs_col in df2.columns:
            p_abs = df2[abs_col].apply(
                lambda x: isinstance(x, str) and len(x.strip()) > 0
            ).sum()
            log(f"- Abstract coverage: {p_abs}/{len(df2)} "
                f"= {p_abs/len(df2)*100:.1f}%")
        log("- **Decision**: excluded from primary topic modeling "
            "(per Donthu 2021 / Yao 2025 complete-year cutoff convention)")
    log("")

    # ---------------- Part H: Recommendations ----------------
    log("## H. Recommendations for Block 1\n")
    recs = []
    if abs_col and (non_empty_abs / n) >= 0.85:
        recs.append(
            f"- Abstract coverage **{non_empty_abs/n*100:.1f}%** is acceptable. "
            "Proceed with `title [SEP] abstract` for records with both; "
            "use title-only fallback for the rest."
        )
    elif abs_col:
        recs.append(
            f"- Abstract coverage is **{non_empty_abs/n*100:.1f}%** — flag "
            "in Methods. Consider title-only embedding as primary if <70%."
        )
    if abs_col:
        recs.append(
            "- For records with token>512, use **head+tail truncation** "
            "(first 384 + last 128 tokens) — preserves intro context + "
            "conclusions, standard for long scientific abstracts."
        )
    recs.append(
        "- Embedding output target: "
        "`data/processed/specter2_embeddings.npy` (float32, "
        f"~{n*768*4/1024/1024:.0f} MB for {n:,} docs × 768 dims)."
    )
    for r in recs:
        log(r)
    log("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📝 Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
