"""
Day 7 LLM client v2 — OpenRouter Structured Outputs with multi-tier fallback.

DESIGN (informed by OpenRouter official docs):
  Tier 1 (preferred): response_format=json_schema + strict=true + require_parameters
                      Server-side enforcement. Expected ~99% first-attempt success
                      on Anthropic Sonnet 4.5+/Opus 4.1+ and OpenAI GPT-4o+/O3+.
  Tier 2 (fallback):  response_format={"type":"json_object"} (loose JSON mode).
                      Some models support this even without strict schema.
  Tier 3 (last):      pure prompt-driven JSON (no response_format) + retry.

Pydantic post-validation runs after every attempt — catches range/length checks
that strict JSON schema cannot express.

Key features:
  - Auto-pre-compute strict JSON schema once per process (cached)
  - Per-call JSONL audit log (which tier succeeded, validation_failures, tokens)
  - Cost tracking with model-specific pricing
  - Pre-flight model availability check via /v1/models endpoint
  - require_parameters=true ensures OpenRouter only routes to providers that
    accept the requested response_format (prevents silent fallback)
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

# --- import schema module from same directory ---------------------------
_HERE = Path(__file__).parent
_SCHEMA_SPEC = importlib.util.spec_from_file_location(
    "schema_mod", _HERE / "01_schema.py"
)
_SCHEMA = importlib.util.module_from_spec(_SCHEMA_SPEC)
_SCHEMA_SPEC.loader.exec_module(_SCHEMA)
AbstractExtraction = _SCHEMA.AbstractExtraction
build_strict_json_schema = _SCHEMA.build_strict_json_schema

# --- env / constants ----------------------------------------------------
load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("FATAL: OPENROUTER_API_KEY not set in .env", file=sys.stderr)
    sys.exit(1)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# OpenRouter pricing (USD per 1M tokens). Verify at https://openrouter.ai/models
MODEL_PRICING_USD_PER_1M: dict[str, tuple[float, float]] = {
    "anthropic/claude-sonnet-4.6": (3.0, 15.0),
    "anthropic/claude-opus-4.6": (15.0, 75.0),
    "anthropic/claude-3.5-sonnet": (3.0, 15.0),
    "anthropic/claude-3.7-sonnet": (3.0, 15.0),
    "openai/gpt-4o-mini": (0.15, 0.60),
    "openai/gpt-4o": (2.5, 10.0),
    "openai/o3-mini": (1.10, 4.40),
}


# ----------------------------------------------------------------------
def list_available_models() -> set[str]:
    """Fetch list of model IDs currently exposed by OpenRouter."""
    r = requests.get(
        f"{OPENROUTER_BASE_URL}/models",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        timeout=15,
    )
    r.raise_for_status()
    return {m["id"] for m in r.json()["data"]}


def check_models_available(model_ids: list[str]) -> list[str]:
    """Verify each requested model id exists on OpenRouter; print suggestions."""
    try:
        available = list_available_models()
    except Exception as e:
        print(f"⚠️  Could not fetch OpenRouter model list: {e}")
        return []
    missing = [m for m in model_ids if m not in available]
    if missing:
        print(f"\n⚠️  Missing model IDs on OpenRouter: {missing}")
        print("Available models containing 'sonnet'/'opus'/'gpt-4o'/'o3':")
        for m in sorted(available):
            if any(k in m.lower() for k in ["sonnet", "opus", "gpt-4o", "o3"]):
                print(f"  - {m}")
    return missing


# ----------------------------------------------------------------------
class LLMClient:
    """OpenRouter-routed LLM client with 3-tier fallback for structured output."""

    # Pre-compute strict JSON schema once (shared across instances)
    _STRICT_SCHEMA: dict = build_strict_json_schema(
        AbstractExtraction, "abstract_extraction"
    )

    def __init__(
        self, model: str, log_dir: Path,
        referer: str = "https://github.com/anonymous/tcm-hdi-bibliometric",
        app_title: str = "TCM-HDI-Bibliometric-2026",
        enable_response_healing: bool = False,
    ):
        self.model = model
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / f"{model.replace('/', '__')}.jsonl"
        self.enable_response_healing = enable_response_healing

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": referer,
                "X-OpenRouter-Title": app_title,
            },
        )

        # Stats
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.n_calls = 0
        self.n_tier1_success = 0
        self.n_tier2_success = 0
        self.n_tier3_success = 0
        self.n_total_failure = 0
        self.n_validation_fails = 0

    # ==================================================================
    # Public API
    # ==================================================================
    def extract(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 2,
        temperature: float = 0.0,
        max_output_tokens: int = 4096,
    ) -> tuple[Optional[AbstractExtraction], dict[str, Any]]:
        """Extract structured AbstractExtraction with multi-tier fallback.

        Returns (extraction or None, metadata dict).
        """
        meta: dict[str, Any] = {
            "model": self.model,
            "tier_used": None,           # 1=strict, 2=loose_json, 3=prompt_only
            "n_attempts": 0,
            "validation_failures": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "elapsed_s": 0.0,
            "tier1_error": None,
            "tier2_error": None,
            "tier3_error": None,
            "error": None,
        }
        t0 = time.time()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # ---- Tier 1: structured outputs (strict JSON schema) ----
        extraction, t1_meta = self._try_call(
            messages,
            response_format={
                "type": "json_schema",
                "json_schema": self._STRICT_SCHEMA,
            },
            extra_body=self._build_extra_body(require_parameters=True),
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            tier=1,
        )
        self._merge_meta(meta, t1_meta)
        if extraction is not None:
            meta["tier_used"] = 1
            meta["elapsed_s"] = round(time.time() - t0, 2)
            self.n_tier1_success += 1
            self.n_calls += 1
            self._log(meta, success=True)
            return extraction, meta
        meta["tier1_error"] = t1_meta.get("error")

        # ---- Tier 2: loose JSON mode ----
        extraction, t2_meta = self._try_call(
            messages,
            response_format={"type": "json_object"},
            extra_body=None,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            tier=2,
        )
        self._merge_meta(meta, t2_meta)
        if extraction is not None:
            meta["tier_used"] = 2
            meta["elapsed_s"] = round(time.time() - t0, 2)
            self.n_tier2_success += 1
            self.n_calls += 1
            self._log(meta, success=True)
            return extraction, meta
        meta["tier2_error"] = t2_meta.get("error")

        # ---- Tier 3: prompt-only with explicit retry loop ----
        extraction, t3_meta = self._extract_prompt_only(
            messages, max_retries=max_retries,
            temperature=temperature, max_output_tokens=max_output_tokens,
        )
        self._merge_meta(meta, t3_meta)
        if extraction is not None:
            meta["tier_used"] = 3
            meta["elapsed_s"] = round(time.time() - t0, 2)
            self.n_tier3_success += 1
            self.n_calls += 1
            self._log(meta, success=True)
            return extraction, meta
        meta["tier3_error"] = t3_meta.get("error")

        # All tiers failed
        meta["error"] = (f"All tiers failed. Last error: {meta['tier3_error']}")
        meta["elapsed_s"] = round(time.time() - t0, 2)
        self.n_total_failure += 1
        self._log(meta, success=False)
        return None, meta

    # ==================================================================
    # Internal helpers
    # ==================================================================
    def _build_extra_body(self, require_parameters: bool = True) -> dict:
        body: dict[str, Any] = {}
        if require_parameters:
            body["provider"] = {"require_parameters": True}
        if self.enable_response_healing:
            # Response Healing plugin (non-streaming, json_schema requests)
            body["plugins"] = [{"id": "response-healing"}]
        return body

    def _try_call(
        self,
        messages: list[dict],
        response_format: Optional[dict],
        extra_body: Optional[dict],
        temperature: float,
        max_output_tokens: int,
        tier: int,
    ) -> tuple[Optional[AbstractExtraction], dict]:
        """Single-attempt call (no retry). For use in Tiers 1 and 2."""
        m: dict[str, Any] = {
            "n_attempts": 1,
            "validation_failures": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "error": None,
        }
        try:
            kwargs = dict(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
            if response_format is not None:
                kwargs["response_format"] = response_format
            if extra_body:
                kwargs["extra_body"] = extra_body

            resp = self.client.chat.completions.create(**kwargs)
            content = resp.choices[0].message.content or ""

            if resp.usage:
                m["input_tokens"] = resp.usage.prompt_tokens or 0
                m["output_tokens"] = resp.usage.completion_tokens or 0
                self.total_input_tokens += m["input_tokens"]
                self.total_output_tokens += m["output_tokens"]

            cleaned = self._strip_fence(content)
            data = json.loads(cleaned)
            extraction = AbstractExtraction.model_validate(data)
            return extraction, m

        except (json.JSONDecodeError, ValidationError) as e:
            m["validation_failures"] = 1
            m["error"] = f"ValidationError (tier {tier}): {str(e)[:300]}"
            self.n_validation_fails += 1
            return None, m
        except Exception as e:
            m["error"] = f"{type(e).__name__} (tier {tier}): {str(e)[:300]}"
            return None, m

    def _extract_prompt_only(
        self,
        base_messages: list[dict],
        max_retries: int,
        temperature: float,
        max_output_tokens: int,
    ) -> tuple[Optional[AbstractExtraction], dict]:
        """Tier 3: no response_format, retry on validation failure with
        corrective message appended to the conversation."""
        messages = list(base_messages)
        m: dict[str, Any] = {
            "n_attempts": 0,
            "validation_failures": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "error": None,
        }
        last_err = None
        for attempt in range(max_retries + 1):
            m["n_attempts"] += 1
            content: Optional[str] = None
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_output_tokens,
                )
                content = resp.choices[0].message.content or ""
                if resp.usage:
                    m["input_tokens"] += resp.usage.prompt_tokens or 0
                    m["output_tokens"] += resp.usage.completion_tokens or 0
                    self.total_input_tokens += resp.usage.prompt_tokens or 0
                    self.total_output_tokens += resp.usage.completion_tokens or 0

                cleaned = self._strip_fence(content)
                data = json.loads(cleaned)
                extraction = AbstractExtraction.model_validate(data)
                return extraction, m

            except (json.JSONDecodeError, ValidationError) as e:
                last_err = str(e)[:500]
                m["validation_failures"] += 1
                self.n_validation_fails += 1
                if content is not None:
                    messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": (
                        f"Your previous response failed JSON/schema "
                        f"validation. Error:\n{last_err}\n\n"
                        f"Output ONLY a valid JSON object matching the "
                        f"AbstractExtraction schema. No prose, no code fences."
                    ),
                })
            except Exception as e:
                m["error"] = f"{type(e).__name__}: {str(e)[:300]}"
                return None, m

        m["error"] = f"Validation failed after {max_retries+1} attempts: {last_err}"
        return None, m

    # ==================================================================
    # Utilities
    # ==================================================================
    @staticmethod
    def _strip_fence(s: str) -> str:
        """Strip ```json ... ``` markdown fences if present."""
        s = (s or "").strip()
        if s.startswith("```"):
            lines = s.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            s = "\n".join(lines).strip()
        return s

    @staticmethod
    def _merge_meta(parent: dict, child: dict) -> None:
        parent["n_attempts"] += child.get("n_attempts", 0)
        parent["validation_failures"] += child.get("validation_failures", 0)
        parent["input_tokens"] += child.get("input_tokens", 0)
        parent["output_tokens"] += child.get("output_tokens", 0)

    def estimate_cost_usd(self) -> float:
        if self.model not in MODEL_PRICING_USD_PER_1M:
            return -1.0
        in_p, out_p = MODEL_PRICING_USD_PER_1M[self.model]
        return round(
            self.total_input_tokens / 1e6 * in_p
            + self.total_output_tokens / 1e6 * out_p, 4
        )

    def stats(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "n_calls": self.n_calls,
            "tier1_success": self.n_tier1_success,
            "tier2_success": self.n_tier2_success,
            "tier3_success": self.n_tier3_success,
            "total_failure": self.n_total_failure,
            "validation_fails": self.n_validation_fails,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "estimated_cost_usd": self.estimate_cost_usd(),
        }

    def _log(self, meta: dict, success: bool):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(
                {**meta, "success": success}, ensure_ascii=False, default=str
            ) + "\n")
