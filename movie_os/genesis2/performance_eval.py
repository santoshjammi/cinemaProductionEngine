"""P0-04: Deterministic performance coverage, voice-binding, and semantic evaluation.

Mandatory per-line performance fields are checked deterministically (no LLM).
Semantic checks (continuity, professional register, subtext vs motivation) are
evaluated by the semantic evaluator and returned as warnings/blockers — the
freeze gate enforces the verdicts.
"""
from __future__ import annotations

import logging
from typing import Any

from .performance_model import resolve_voice_binding, VOICE_PROFILES, _speaker_base

logger = logging.getLogger("movie_os.genesis2.performance")

# Mandatory per-line performance fields (P0-04 §9).
# A line is incomplete if any of these is empty.
MANDATORY_PERF_FIELDS = [
    "line_id",
    "speaker",
    "text",
    "emotional_state_primary",
    "delivery_intent",
    "subtext",
    "character_voice_id",
    "presentation_mode",
]


def _first_truth(*vals):
    for v in vals:
        if v and str(v).strip():
            return str(v).strip()
    return ""


def normalize_performance_fields(line: dict[str, Any]) -> dict[str, Any]:
    """Normalize a source line into the canonical performance contract.

    Preserves existing authored knowledge (emotion, delivery_intent, subtext);
    never replaces a valid field with a generic default.  Missing mandatory
    fields are left empty so the coverage gate can flag them.

    Voice identity binding is GENESIS-owned and DETERMINISTIC: character_voice_id
    and presentation_mode are always resolved from the speaker, never invented
    by the enrichment LLM.
    """
    out = dict(line)
    # emotional_state_primary from explicit field or legacy emotion
    if not out.get("emotional_state_primary"):
        out["emotional_state_primary"] = _first_truth(line.get("emotion"), line.get("emotional_state"))
    if not out.get("delivery_intent"):
        out["delivery_intent"] = _first_truth(line.get("delivery_intent"), line.get("emotion"))
    # subtext preserved if present
    # Voice binding resolved deterministically — OVERRIDES any LLM-invented value.
    vbind = resolve_voice_binding(line.get("speaker", ""))
    out["character_voice_id"] = vbind["character_voice_id"]
    out["presentation_mode"] = vbind["presentation_mode"]
    return out


def _line_missing_fields(line: dict[str, Any]) -> list[str]:
    return [f for f in MANDATORY_PERF_FIELDS if not str(line.get(f, "") or "").strip()]


def line_mandatory_coverage(line: dict[str, Any]) -> dict[str, Any]:
    """Check a single line for mandatory performance completeness."""
    missing = _line_missing_fields(line)
    return {"complete": len(missing) == 0, "missing_fields": missing}


def performance_coverage(lines: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate mandatory performance coverage over authoritative lines (§28)."""
    complete = 0
    incomplete: list[dict[str, Any]] = []
    for ln in lines:
        cov = line_mandatory_coverage(ln)
        if cov["complete"]:
            complete += 1
        else:
            incomplete.append({"line_id": ln.get("line_id"), "missing": cov["missing_fields"]})
    total = len(lines)
    pct = (complete / total * 100) if total else 100.0
    return {
        "denominator": "AUTHORITATIVE_DIALOGUE_LINES",
        "expected": total,
        "complete_records": complete,
        "incomplete_records": incomplete,
        "percentage": pct,
        "passed": complete == total,
    }


def voice_binding_coverage(lines: list[dict[str, Any]]) -> dict[str, Any]:
    """line_id -> speaker -> character_voice_id resolution (§29)."""
    resolved = 0
    unresolved: list[dict[str, Any]] = []
    wrong: list[dict[str, Any]] = []
    for ln in lines:
        cvid = str(ln.get("character_voice_id", "") or "").strip()
        base = _speaker_base(ln.get("speaker", ""))
        expected = VOICE_PROFILES.get(base, {}).get("character_voice_id")
        if cvid:
            resolved += 1
            if expected and cvid != expected:
                wrong.append({"line_id": ln.get("line_id"), "speaker": ln.get("speaker"),
                              "got": cvid, "expected": expected})
        else:
            unresolved.append({"line_id": ln.get("line_id"), "speaker": ln.get("speaker")})
    total = len(lines)
    return {
        "authoritative_lines": total,
        "resolved": resolved,
        "unresolved": unresolved,
        "wrong_character_bindings": wrong,
        "coverage": (resolved / total * 100) if total else 100.0,
        "passed": resolved == total and not wrong,
    }
