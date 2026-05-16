"""
Day 7 LLM extraction schema (Schema D, v2 — OpenAI strict-mode compatible).

CHANGES vs v1:
  - All `Field(None, ...)` → `Field(..., ...)` (required-but-nullable for strict mode)
  - All `Field(default_factory=list, ...)` → `Field(..., ...)` (LLM must explicitly return [])
  - `ge`, `le`, `min_length` removed from Field (moved to @field_validator)
    — OpenAI strict mode forbids these JSON Schema keywords
  - Helper `build_strict_json_schema()` for OpenRouter response_format=json_schema mode

Design rationale unchanged: A+B+C (core / TCM formula / clinical PK).
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ----------------------------------------------------------------------
# Enumerations (used as Literal types — LLM must match exactly)
# ----------------------------------------------------------------------
INTERACTION_TYPE = Literal[
    "pharmacokinetic", "pharmacodynamic", "both", "unspecified"
]

MECHANISM = Literal[
    "CYP_inhibition", "CYP_induction",
    "P-gp_inhibition", "P-gp_induction",
    "UGT_inhibition", "UGT_induction",
    "transporter_modulation",
    "absorption_alteration",
    "protein_binding_displacement",
    "receptor_synergism", "receptor_antagonism",
    "additive_toxicity",
    "synergistic_efficacy", "antagonistic_efficacy",
    "signaling_pathway_modulation",   # NEW v3: transcription factor / kinase pathway
    "organ_toxicity_modulation",       # NEW v3: drug-induced organ toxicity protection/potentiation
    "other", "unspecified"
]

DIRECTION = Literal[
    "exposure_increase", "exposure_decrease",
    "effect_increase", "effect_decrease",
    "no_change", "context_dependent"
]

EVIDENCE_TYPE = Literal[
    "in_vitro", "in_vivo_animal", "human_PK_study",
    "clinical_trial", "case_report", "review", "in_silico"
]

CLINICAL_SIGNIFICANCE = Literal[
    "high", "moderate", "low", "none", "not_assessed"
]


# ----------------------------------------------------------------------
# Main model: single interaction
# ----------------------------------------------------------------------
class HerbDrugInteraction(BaseModel):
    """One herb-drug interaction extracted from an abstract.

    All Optional fields are required-but-nullable for OpenAI strict-mode
    compatibility — LLM must explicitly return null if absent.
    """
    model_config = ConfigDict(extra="forbid")

    # === A: Core interaction tuple ===
    herb_name_latin: Optional[str] = Field(
        ..., description="Latin binomial of the herb if explicitly stated, "
                         "e.g. 'Hypericum perforatum'. Return null if not specified."
    )
    herb_common_name: Optional[str] = Field(
        ..., description="Common English name, e.g. 'St. John's Wort', 'ginseng'. "
                         "Return null if not specified."
    )
    herb_active_compound: Optional[str] = Field(
        ..., description="Active compound if mentioned, "
                         "e.g. 'hyperforin', 'puerarin'. Return null if not mentioned."
    )
    drug_name: Optional[str] = Field(
        ..., description="Conventional drug name, e.g. 'cyclosporine', 'warfarin'. "
                         "Return null if not specified."
    )
    drug_class: Optional[str] = Field(
        ..., description="Drug class, e.g. 'immunosuppressant'. Return null if absent."
    )
    interaction_type: INTERACTION_TYPE = Field(
        ..., description="Pharmacokinetic (ADME), pharmacodynamic (effect), "
                         "both, or unspecified."
    )
    mechanism: MECHANISM = Field(
        ..., description="Most specific mechanism category. Use 'unspecified' if "
                         "interaction reported but mechanism not detailed."
    )
    specific_target: Optional[str] = Field(
        ..., description="Specific molecular target if mentioned, "
                         "e.g. 'CYP3A4', 'OATP1B1', 'PXR', 'P-gp'. Null if not stated."
    )
    direction: DIRECTION = Field(
        ..., description="Direction of effect on the partner. exposure_increase = "
                         "drug plasma level goes up; effect_increase = therapeutic/"
                         "toxic effect intensifies; no_change for null result."
    )

    # === B: TCM formula extension ===
    tcm_formula_name: Optional[str] = Field(
        ..., description="TCM compound formula name if any, e.g. 'Wuzhi capsule', "
                         "'Banxia Xiexin decoction'. Null if single-herb study."
    )
    co_herbs: list[str] = Field(
        ..., description="Other herbs in the same formula. Return [] (empty list) "
                         "if single-herb. Never null — always a list."
    )
    tcm_pattern: Optional[str] = Field(
        ..., description="TCM syndrome/pattern if mentioned, e.g. 'spleen deficiency'. "
                         "Null if not in TCM theoretical framework."
    )

    # === C: Clinical quantitative fields ===
    auc_change_pct: Optional[float] = Field(
        ..., description="AUC change as percentage (positive=increase, negative=decrease). "
                         "E.g. -52.0 for 52% AUC drop. Null if not reported."
    )
    cmax_change_pct: Optional[float] = Field(
        ..., description="Cmax change in %. Null if not reported."
    )
    half_life_change_pct: Optional[float] = Field(
        ..., description="Half-life change in %. Null if not reported."
    )
    cl_change_pct: Optional[float] = Field(
        ..., description="Clearance change in %. Null if not reported."
    )
    sample_size: Optional[int] = Field(
        ..., description="Number of subjects/animals/replicates. Null if not stated."
    )

    # === Metadata ===
    evidence_type: EVIDENCE_TYPE = Field(
        ..., description="Type of evidence reported in this study."
    )
    clinical_significance: CLINICAL_SIGNIFICANCE = Field(
        ..., description="Clinical relevance: 'high' for clinically actionable "
                         "(>50% PK change or major efficacy/toxicity); 'low' for "
                         "in vitro with unclear clinical implication; "
                         "'not_assessed' if abstract does not allow judgment."
    )
    confidence: float = Field(
        ..., description="Your confidence 0.0-1.0 (0=guess, 1=explicit and unambiguous)."
    )
    evidence_quote: str = Field(
        ..., description="VERBATIM sentence(s) from the abstract supporting this "
                         "extraction. Must be ≥10 characters and copied exactly."
    )

    # --- Post-parse validators (constraints OpenAI strict mode can't enforce) ---
    @field_validator("confidence")
    @classmethod
    def _check_confidence_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"confidence must be 0-1, got {v}")
        return v

    @field_validator("evidence_quote")
    @classmethod
    def _check_quote_length(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError(f"evidence_quote must be ≥10 chars, got len={len(v)}")
        return v


# ----------------------------------------------------------------------
# Top-level: full extraction result for one abstract
# ----------------------------------------------------------------------
class AbstractExtraction(BaseModel):
    """Full extraction result for one abstract."""
    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(..., description="Identifier copied from input.")
    contains_hdi: bool = Field(
        ..., description="True if abstract describes ≥1 herb-drug or herb-herb "
                         "interaction; False if pure methodology, non-HDI review, "
                         "or unrelated."
    )
    interactions: list[HerbDrugInteraction] = Field(
        ..., description="All interactions extracted. Return [] if contains_hdi=False."
    )
    extraction_notes: Optional[str] = Field(
        ..., description="Optional notes: ambiguities, partial extractions, or "
                         "reason for contains_hdi=False. Null if none needed."
    )


# Resolve forward references (Pydantic v2 needs this when list[HerbDrugInteraction]
# is referenced before HerbDrugInteraction is fully imported by the namespace).
AbstractExtraction.model_rebuild()


# ======================================================================
# JSON Schema builder for OpenRouter response_format=json_schema (strict mode)
# ======================================================================
_UNSUPPORTED_STRICT_KEYS = {
    "default", "minimum", "maximum",
    "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minLength", "maxLength", "pattern", "format",
    "minItems", "maxItems", "uniqueItems",
    "minProperties", "maxProperties",
    "examples", "example",
}


def _strip_unsupported_inplace(obj: Any) -> None:
    """Recursively strip OpenAI-strict-mode-incompatible JSON schema keywords
    AND enforce additionalProperties=False + required=all-properties on every
    object node."""
    if isinstance(obj, dict):
        for k in list(obj.keys()):
            if k in _UNSUPPORTED_STRICT_KEYS:
                obj.pop(k)
        if obj.get("type") == "object" and "properties" in obj:
            obj["additionalProperties"] = False
            obj["required"] = list(obj["properties"].keys())
        for v in obj.values():
            _strip_unsupported_inplace(v)
    elif isinstance(obj, list):
        for item in obj:
            _strip_unsupported_inplace(item)


def build_strict_json_schema(
    model_cls: type[BaseModel], schema_name: str = "extraction"
) -> dict:
    """Convert a Pydantic v2 model into OpenAI-strict-mode JSON Schema dict
    suitable for OpenRouter `response_format={"type":"json_schema",
    "json_schema":<this dict>}`.
    """
    schema = model_cls.model_json_schema()
    _strip_unsupported_inplace(schema)
    if "$defs" in schema:
        for def_obj in schema["$defs"].values():
            _strip_unsupported_inplace(def_obj)
    return {"name": schema_name, "strict": True, "schema": schema}


# ======================================================================
# CLI: print the generated schema for visual inspection / debugging
# ======================================================================
if __name__ == "__main__":
    import json
    s = build_strict_json_schema(AbstractExtraction, "abstract_extraction")
    print(json.dumps(s, indent=2, ensure_ascii=False))
