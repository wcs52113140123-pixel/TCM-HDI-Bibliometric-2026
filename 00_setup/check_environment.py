"""
Day 0 environment sanity check (fault-tolerant version).

This script tests every dependency and prints a final summary.
It does NOT exit early on errors — it records and continues.

Each check is classified as:
  - BLOCKER:  must fix before Day 1 (data acquisition impossible without it)
  - WARNING:  fix before the day this is needed (script will tell you)
  - INFO:     informational only

Usage:
    conda activate tcm-hdi
    python 00_setup/check_environment.py
"""

import os
import sys
import traceback
from pathlib import Path

# Soft import: dotenv is itself one of the things we check
try:
    from dotenv import load_dotenv
    repo_root = Path(__file__).resolve().parent.parent
    load_dotenv(repo_root / ".env")
except ImportError:
    repo_root = Path(__file__).resolve().parent.parent

# ============================================================
# Result tracking
# ============================================================

results = []  # list of (status, severity, name, detail)
# status:   "OK" | "FAIL" | "SKIP"
# severity: "blocker" | "warning" | "info"


def check(name, severity, fn):
    """Run a check function; record OK/FAIL without raising."""
    print(f"\n[{name}] ...")
    try:
        detail = fn()
        results.append(("OK", severity, name, detail or ""))
        print(f"      OK  {detail or ''}")
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        results.append(("FAIL", severity, name, msg))
        print(f"      FAIL ({severity}): {msg}")
        # Print short traceback for blockers/warnings (helps debugging)
        if severity in ("blocker", "warning"):
            tb = traceback.format_exc().splitlines()
            # Print only the last 3 lines of traceback (concise)
            for line in tb[-4:]:
                print(f"           {line}")


# ============================================================
# Individual checks
# ============================================================

def check_python_version():
    v = sys.version_info
    if v < (3, 10):
        raise RuntimeError(f"Python 3.10+ required, found {v.major}.{v.minor}")
    return f"Python {v.major}.{v.minor}.{v.micro}"


def check_core_packages():
    import pandas, numpy, anthropic, openai, pyalex, networkx, matplotlib, sklearn
    return (f"pandas {pandas.__version__}, numpy {numpy.__version__}, "
            f"anthropic {anthropic.__version__}, openai {openai.__version__}, "
            f"networkx {networkx.__version__}, sklearn {sklearn.__version__}")


def check_data_io_packages():
    import requests
    import bs4
    import lxml
    from fuzzywuzzy import fuzz
    from Bio import Entrez   # biopython
    return f"requests, bs4, lxml, fuzzywuzzy, biopython all imported"


def check_visualization_packages():
    import matplotlib, seaborn, plotly
    import matplotlib_venn
    return (f"matplotlib {matplotlib.__version__}, "
            f"seaborn {seaborn.__version__}, plotly {plotly.__version__}, "
            f"matplotlib_venn imported")


def check_topic_modeling_stack():
    # This is the one that failed for you — keep as WARNING, not BLOCKER
    import sentence_transformers
    import umap
    import hdbscan
    return (f"sentence-transformers {sentence_transformers.__version__}, "
            f"umap {umap.__version__}, hdbscan {hdbscan.__version__}")


def check_gseapy():
    # gseapy is a heavy bioconda-adjacent package, sometimes flaky on Windows
    import gseapy
    return f"gseapy {gseapy.__version__}"


def check_dotenv():
    from dotenv import load_dotenv
    return "python-dotenv imported"


def check_directories():
    expected_dirs = [
        "00_setup", "01_data_acquisition", "02_data_integration",
        "03_basic_bibliometrics", "04_topic_modeling", "05_llm_extraction",
        "06_pharmacology_network", "07_subgroup_analysis", "08_citation_burst",
        "09_figures", "10_tables", "11_supplementary", "12_manuscript",
        "data/raw", "data/processed", "data/llm_output", "data/pharmacology",
        "docs"
    ]
    missing = [d for d in expected_dirs if not (repo_root / d).exists()]
    if missing:
        raise RuntimeError(f"Missing dirs: {missing}")
    return f"All {len(expected_dirs)} directories present"


def check_gitignore_protects_secrets():
    """Critical: confirm .env is NOT tracked by git."""
    gitignore_path = repo_root / ".gitignore"
    if not gitignore_path.exists():
        raise RuntimeError(".gitignore missing!")
    content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
    if ".env" not in content:
        raise RuntimeError(".env not protected by .gitignore — your API keys could leak!")
    return ".env is protected by .gitignore"


def check_required_env_keys():
    # Required for Day 1-2 (data acquisition): emails
    # Required for Day 8+ (LLM): ANTHROPIC_API_KEY — placeholder OK for now
    must_have_now    = ["NCBI_EMAIL", "OPENALEX_EMAIL"]
    placeholder_ok   = ["ANTHROPIC_API_KEY"]

    missing = []
    for key in must_have_now:
        val = os.getenv(key, "").strip()
        if not val or "@" not in val or "example.com" in val:
            missing.append(f"{key} (must be a real email)")
    for key in placeholder_ok:
        val = os.getenv(key, "").strip()
        if not val:
            missing.append(f"{key} (empty — set at least a placeholder)")

    if missing:
        raise RuntimeError(f"Missing or invalid: {missing}")
    return (f"Emails set, ANTHROPIC_API_KEY present "
            f"(placeholder OK before Day 8)")


def check_optional_env_keys():
    optional = ["OPENAI_API_KEY", "NCBI_API_KEY", "ANTHROPIC_BASE_URL"]
    present = []
    for key in optional:
        val = os.getenv(key, "").strip()
        if val:
            present.append(key)
    return f"Optional keys present: {present if present else 'none (OK to skip)'}"


def check_anthropic_api_connectivity():
    import anthropic
    base_url = os.getenv("ANTHROPIC_BASE_URL", "").strip() or None
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in .env")
    # Allow placeholder keys to skip connectivity check (will fail before Day 8 anyway)
    if "PLACEHOLDER" in api_key.upper() or len(api_key) < 30:
        return "skipped (placeholder key — fill real key before Day 8)"
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = anthropic.Anthropic(**kwargs)
    # Try a list of candidate model names — first one that works wins
    candidates = [
        "claude-sonnet-4-5",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-latest",
    ]
    last_err = None
    for model in candidates:
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            )
            text = resp.content[0].text.strip() if resp.content else "<no content>"
            return f"model={model} -> {text!r}"
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"All candidate models failed; last error: {last_err}")


def check_git_status():
    """Just confirm git is available; don't enforce clean state."""
    import subprocess
    r = subprocess.run(["git", "--version"], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git not in PATH")
    return r.stdout.strip()


# ============================================================
# Run all checks
# ============================================================

print("=" * 70)
print("Day 0 Environment Check for TCM-HDI Bibliometric 2026 (fault-tolerant)")
print("=" * 70)

checks_to_run = [
    ("Python version",                 "blocker", check_python_version),
    ("Core packages",                  "blocker", check_core_packages),
    ("Data I/O packages",              "blocker", check_data_io_packages),
    ("Visualization packages",         "blocker", check_visualization_packages),
    ("Topic modeling stack (PyTorch)", "warning", check_topic_modeling_stack),
    ("gseapy (KEGG enrichment)",       "warning", check_gseapy),
    ("python-dotenv",                  "blocker", check_dotenv),
    ("Directory structure",            "blocker", check_directories),
    (".gitignore protects .env",       "blocker", check_gitignore_protects_secrets),
    ("Required .env keys",             "blocker", check_required_env_keys),
    ("Optional .env keys",             "info",    check_optional_env_keys),
    ("Anthropic API connectivity",     "blocker", check_anthropic_api_connectivity),
    ("Git availability",               "blocker", check_git_status),
]

for name, severity, fn in checks_to_run:
    check(name, severity, fn)


# ============================================================
# Summary
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

ok      = [r for r in results if r[0] == "OK"]
fails   = [r for r in results if r[0] == "FAIL"]
blocker_fails = [r for r in fails if r[1] == "blocker"]
warning_fails = [r for r in fails if r[1] == "warning"]

print(f"\nPassed: {len(ok)}/{len(results)}")

if blocker_fails:
    print(f"\n❌ BLOCKERS ({len(blocker_fails)}) — must fix before Day 1:")
    for _, _, name, detail in blocker_fails:
        print(f"   - {name}")
        print(f"     ({detail[:100]}{'...' if len(detail) > 100 else ''})")

if warning_fails:
    print(f"\n⚠️  WARNINGS ({len(warning_fails)}) — fix before the relevant day:")
    for _, _, name, detail in warning_fails:
        when = {
            "Topic modeling stack (PyTorch)": "Day 7 (topic modeling)",
            "gseapy (KEGG enrichment)":       "Day 13 (KEGG enrichment)",
        }.get(name, "before use")
        print(f"   - {name}  [needed by: {when}]")
        print(f"     ({detail[:100]}{'...' if len(detail) > 100 else ''})")

if not blocker_fails and not warning_fails:
    print("\n✅ All checks passed. Day 0 environment is fully ready.")
elif not blocker_fails:
    print("\n✅ No blockers. You can start Day 1 immediately.")
    print("   Warnings above are non-blocking — schedule a fix before they bite.")
else:
    print("\n❌ Blockers present. Fix them before Day 1.")

print()
sys.exit(0 if not blocker_fails else 1)


