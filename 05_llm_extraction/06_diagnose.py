"""
Day 7 OpenRouter diagnostic script.

Run this to determine why benchmark calls are failing immediately.
Usage:
    python 05_llm_extraction/06_diagnose.py
"""
from __future__ import annotations

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ.get("OPENROUTER_API_KEY")
if not KEY:
    print("FATAL: OPENROUTER_API_KEY not in .env"); sys.exit(1)

print(f"Key prefix: {KEY[:12]}...{KEY[-4:]} (length={len(KEY)})\n")

BASE = "https://openrouter.ai/api/v1"
HEADERS = {
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/anonymous/tcm-hdi",
    "X-OpenRouter-Title": "TCM-HDI-Bibliometric-2026",
}


def section(n: int, title: str) -> None:
    print(f"\n{'='*72}\n  [{n}] {title}\n{'='*72}")


# ----------------------------------------------------------------------
# 1. Credits / account
# ----------------------------------------------------------------------
section(1, "Account credits / balance")
try:
    r = requests.get(f"{BASE}/credits", headers=HEADERS, timeout=15)
    print(f"   HTTP {r.status_code}")
    print(f"   Body: {r.text[:600]}")
except Exception as e:
    print(f"   EXCEPTION: {e}")

# ----------------------------------------------------------------------
# 2. List models (sanity)
# ----------------------------------------------------------------------
section(2, "List models")
try:
    r = requests.get(f"{BASE}/models", headers=HEADERS, timeout=15)
    data = r.json().get("data", [])
    print(f"   HTTP {r.status_code}, n_models={len(data)}")
    matching = [m["id"] for m in data
                if "claude-sonnet-4.6" in m["id"] or "claude-opus-4.6" in m["id"]
                or "o3-mini" in m["id"] or "gpt-4o-mini" in m["id"]]
    print(f"   Target models present: {matching}")
except Exception as e:
    print(f"   EXCEPTION: {e}")

# ----------------------------------------------------------------------
# 3. Minimal chat call (no structured output) — bare minimum to verify
#    that an API call to a paid model works
# ----------------------------------------------------------------------
section(3, "Minimal chat call (no structured output, 50 tokens)")
try:
    r = requests.post(f"{BASE}/chat/completions", headers=HEADERS, timeout=30, json={
        "model": "anthropic/claude-sonnet-4.6",
        "messages": [{"role": "user", "content": "Reply with just the word 'pong'."}],
        "max_tokens": 50,
    })
    print(f"   HTTP {r.status_code}")
    print(f"   Body: {r.text[:1500]}")
except Exception as e:
    print(f"   EXCEPTION: {e}")

# ----------------------------------------------------------------------
# 4. Same call but with json_schema strict response_format (Tier 1)
# ----------------------------------------------------------------------
section(4, "Chat with json_schema (Tier 1 path)")
try:
    r = requests.post(f"{BASE}/chat/completions", headers=HEADERS, timeout=30, json={
        "model": "anthropic/claude-sonnet-4.6",
        "messages": [{"role": "user", "content": "Return JSON: {\"answer\":\"yes\"}."}],
        "max_tokens": 100,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "answer",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["answer"],
                    "properties": {"answer": {"type": "string"}}
                }
            }
        },
        "provider": {"require_parameters": True}
    })
    print(f"   HTTP {r.status_code}")
    print(f"   Body: {r.text[:1500]}")
except Exception as e:
    print(f"   EXCEPTION: {e}")

# ----------------------------------------------------------------------
# 5. Same with json_object (Tier 2 path)
# ----------------------------------------------------------------------
section(5, "Chat with json_object (Tier 2 path)")
try:
    r = requests.post(f"{BASE}/chat/completions", headers=HEADERS, timeout=30, json={
        "model": "anthropic/claude-sonnet-4.6",
        "messages": [
            {"role": "system", "content": "Reply with JSON only."},
            {"role": "user", "content": "Return JSON: {\"answer\":\"yes\"}."}
        ],
        "max_tokens": 100,
        "response_format": {"type": "json_object"},
    })
    print(f"   HTTP {r.status_code}")
    print(f"   Body: {r.text[:1500]}")
except Exception as e:
    print(f"   EXCEPTION: {e}")

print(f"\n{'='*72}\nDIAGNOSTIC COMPLETE\n{'='*72}")
