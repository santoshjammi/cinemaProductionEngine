"""P0-04: Performance enrichment — fill only genuinely missing mandatory fields.

Semantic enrichment (authorized LLM: DeepSeek V4 Flash / local Ollama per
policy) supplies concise subtext, acting intention, and performance metadata for
lines that LACK them.  It never rewrites valid dialogue text, never overwrites
existing authored performance, and never inserts generic neutral defaults.  The
enrichment is a repair loop: after enrichment the deterministic coverage gate
re-evaluates; any remaining missing mandatory field is a blocker.

Only the missing fields are targeted.  Complete lines pass through untouched.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

from .llm_client import _extract_json

from .performance_eval import (
    MANDATORY_PERF_FIELDS,
    normalize_performance_fields,
    _line_missing_fields,
)

logger = logging.getLogger("movie_os.genesis2.performance.enrich")


class PerformanceEnrichmentLine(BaseModel):
    line_id: str
    emotional_state_primary: str = Field(default="")
    delivery_intent: str = Field(default="")
    subtext: str = Field(default="")


class PerformanceEnrichmentBatch(BaseModel):
    scene_id: str
    lines: list[PerformanceEnrichmentLine]


def build_enrichment_context(
    episode_mechanism: str = "",
    character_canon: Optional[dict] = None,
    scene: Optional[dict] = None,
    prev_lines: Optional[list] = None,
    next_lines: Optional[list] = None,
) -> dict[str, Any]:
    """Assemble the authoritative context passed to the semantic enricher."""
    return {
        "episode_mechanism": episode_mechanism,
        "character_canon": character_canon or {},
        "scene": scene or {},
        "previous_dialogue_lines": prev_lines or [],
        "following_dialogue_lines": next_lines or [],
    }


def _required_line_ids(lines: list[dict[str, Any]]) -> list[str]:
    return [str(line.get("line_id") or "") for line in lines if _line_missing_fields(line)]


def _line_payloads(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payloads = []
    for line in lines:
        if not _line_missing_fields(line):
            continue
        payloads.append({
            "line_id": str(line.get("line_id") or ""),
            "speaker_id": str(line.get("speaker_id") or line.get("speaker") or ""),
            "exact_dialogue_text": str(line.get("text") or line.get("exact_dialogue_text") or ""),
            "missing_fields": _line_missing_fields(line),
        })
    return payloads


def enrichment_prompt_for_batch(batch: dict[str, Any], context: dict[str, Any]) -> str:
    """Build a scene-batch enrichment prompt for all incomplete authoritative lines."""
    required_line_ids = _required_line_ids(list(batch.get("lines", [])))
    lines = _line_payloads(list(batch.get("lines", [])))
    return (
        "# Performance Enrichment (P0-04)\n"
        "The dialogue text below is AUTHORITATIVE and must NOT be rewritten.\n"
        "Return structured performance metadata only for the requested lines.\n\n"
        f"## Scene\n{json.dumps(batch, indent=2, default=str)}\n\n"
        f"## Required line ids\n{json.dumps(required_line_ids, indent=2)}\n\n"
        f"## Dialogue lines\n{json.dumps(lines, indent=2, default=str)}\n\n"
        f"## Authoritative context\n{json.dumps(context, indent=2, default=str)}\n\n"
        "Each returned line must keep the same line_id and provide only the missing semantic metadata. "
        "Do not return dialogue text. Do not invent new line ids. Do not add markdown."
    )


def _parse_batch_response(response: Any) -> dict[str, dict[str, Any]]:
    if isinstance(response, str):
        response = _extract_json(response)
    if isinstance(response, list):
        raise ValueError("PERFORMANCE_ENRICHMENT_LINE_RECONCILIATION_FAILED: list instead of object")
    if not isinstance(response, dict):
        raise ValueError("PERFORMANCE_ENRICHMENT_LINE_RECONCILIATION_FAILED: non-object response")
    if "scene_id" in response and "lines" in response:
        parsed = PerformanceEnrichmentBatch.model_validate(response)
        return {line.line_id: line.model_dump() for line in parsed.lines}
    line_map: dict[str, dict[str, Any]] = {}
    for line_id, payload in response.items():
        if not isinstance(payload, dict):
            raise ValueError("PERFORMANCE_ENRICHMENT_LINE_RECONCILIATION_FAILED: non-object line payload")
        line_map[str(line_id)] = payload
    return line_map


def _validate_semantics(line: dict[str, Any], enriched: dict[str, Any]) -> None:
    if not enriched.get("emotional_state_primary", "").strip():
        raise ValueError("PERFORMANCE_ENRICHMENT_SEMANTIC_FAILURE: blank emotional_state_primary")
    if enriched.get("emotional_state_primary", "").strip().lower() in {"neutral", "generic", "normal"}:
        raise ValueError("PERFORMANCE_ENRICHMENT_SEMANTIC_FAILURE: generic emotional_state_primary")
    if not enriched.get("delivery_intent", "").strip():
        raise ValueError("PERFORMANCE_ENRICHMENT_SEMANTIC_FAILURE: blank delivery_intent")
    if not enriched.get("subtext", "").strip():
        raise ValueError("PERFORMANCE_ENRICHMENT_SEMANTIC_FAILURE: blank subtext")


def merge_enriched_fields(line: dict, enriched: dict) -> dict:
    """Merge enriched fields into the line, preserving existing authored values.

    Enriched fields fill only what was missing; they never overwrite existing
    valid authored performance.  Voice identity (character_voice_id,
    presentation_mode) is GENESIS-owned/deterministic and is NEVER taken from
    the enrichment LLM — it is re-resolved from the speaker.
    """
    out = dict(line)
    for k, v in (enriched or {}).items():
        if k in ("character_voice_id", "presentation_mode", "speaker", "text", "line_id"):
            continue  # never LLM-authored
        if not out.get(k) and k in MANDATORY_PERF_FIELDS:
            out[k] = str(v).strip() if v is not None else ""
    # Deterministic voice identity resolution (GENESIS-owned).
    from .performance_model import resolve_voice_binding
    vbind = resolve_voice_binding(out.get("speaker", ""))
    out["character_voice_id"] = vbind["character_voice_id"]
    out["presentation_mode"] = vbind["presentation_mode"]
    return out


def enrich_line(
    line: dict,
    context: dict,
    llm,
    *,
    batch_prompt: str | None = None,
    batch_response: dict[str, Any] | None = None,
) -> dict:
    """Enrich a line's missing mandatory fields using scene-batch output when available."""
    missing = _line_missing_fields(line)
    if not missing:
        return line
    line_id = str(line.get("line_id") or "")
    if batch_response and line_id in batch_response:
        enriched = merge_enriched_fields(line, batch_response[line_id])
        _validate_semantics(line, enriched)
        return enriched
    last_exc = None
    for attempt in range(2):
        try:
            prompt = batch_prompt or enrichment_prompt_for_batch({"lines": [line]}, context)
            response = llm.generate(
                prompt,
                phase_name="PerformanceEnrichment",
                task_key=f"PerformanceEnrichment:{line.get('line_id','line')}",
                response_format=PerformanceEnrichmentBatch.model_json_schema(),
            )
            enriched_map = _parse_batch_response(response)
            if line_id in enriched_map:
                enriched = merge_enriched_fields(line, enriched_map[line_id])
                _validate_semantics(line, enriched)
                return enriched
            raise ValueError("PERFORMANCE_ENRICHMENT_LINE_RECONCILIATION_FAILED: missing line_id")
        except Exception as exc:
            last_exc = exc
            logger.warning("performance enrichment attempt %d failed: %s", attempt + 1, exc)
    logger.warning("performance enrichment failed after retries: %s", last_exc)
    return line


def enrich_dialogue(
    lines: list[dict],
    context: dict,
    llm,
) -> tuple[list[dict], int]:
    """Enrich a list of authoritative lines with one bounded scene-batch call."""
    enriched_out = []
    repaired = 0
    prompt = enrichment_prompt_for_batch({"lines": lines}, context)
    last_exc = None
    batch_response: dict[str, Any] | None = None
    for attempt in range(2):
        try:
            response = llm.generate(
                prompt,
                phase_name="PerformanceEnrichment",
                task_key="PerformanceEnrichment:scene_batch",
                response_format=PerformanceEnrichmentBatch.model_json_schema(),
            )
            batch_response = _parse_batch_response(response)
            break
        except Exception as exc:
            last_exc = exc
            logger.warning("performance enrichment scene batch attempt %d failed: %s", attempt + 1, exc)
    for line in lines:
        before_missing = _line_missing_fields(line)
        line_id = str(line.get("line_id") or "")
        if batch_response and line_id in batch_response:
            enriched = merge_enriched_fields(line, batch_response[line_id])
            try:
                _validate_semantics(line, enriched)
            except ValueError:
                # P0: a generic/blank emotional_state_primary from the enrichment
                # LLM is not a pipeline crash.  Skip applying that enrichment and
                # keep the original authored line rather than failing the run.
                enriched = line
        else:
            enriched = line
        after_missing = _line_missing_fields(enriched)
        if before_missing and len(after_missing) < len(before_missing):
            repaired += 1
        enriched_out.append(enriched)
    if last_exc is not None and repaired == 0:
        logger.warning("performance enrichment failed after retries: %s", last_exc)
    return enriched_out, repaired


def enrich_dialogue_batches(
    dialogue_batches: list[dict[str, Any]],
    build_context,
    llm,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Enrich scene batches and fail fast on the first incomplete final batch.

    Each batch is handled independently. Complete records skip LLM calls via
    :func:`enrich_line`. If a batch still contains incomplete authoritative
    lines after retry, processing stops immediately and a blocker is returned.
    """
    updated_batches: list[dict[str, Any]] = []
    total_repaired = 0
    processed_batches = 0
    for batch in dialogue_batches:
        processed_batches += 1
        context = build_context(batch)
        updated_batch = dict(batch)
        any_incomplete_before = False
        any_incomplete_after = False
        repaired_in_batch = 0
        for key in ("lines",):
            lines = list(batch.get(key, []))
            if not lines:
                updated_batch[key] = []
                continue
            before_complete = sum(1 for ln in lines if not _line_missing_fields(ln))
            before_incomplete = len(lines) - before_complete
            if before_incomplete:
                any_incomplete_before = True
            enriched_lines, repaired = enrich_dialogue(lines, context, llm)
            repaired_in_batch += repaired
            updated_batch[key] = enriched_lines
            after_incomplete = sum(1 for ln in enriched_lines if _line_missing_fields(ln))
            if after_incomplete:
                any_incomplete_after = True
        updated_batch["inner_voice"] = list(batch.get("inner_voice", []))
        total_repaired += repaired_in_batch
        updated_batches.append(updated_batch)
        if any_incomplete_before and any_incomplete_after:
            return updated_batches, {
                "passed": False,
                "processed_batches": processed_batches,
                "repaired_lines": total_repaired,
                "blocker": {
                    "code": "PERFORMANCE_ENRICHMENT_INCOMPLETE",
                    "detail": f"batch {processed_batches} still has incomplete authoritative dialogue after bounded retry",
                },
                "aborted_remaining_batches": True,
            }
    return updated_batches, {
        "passed": True,
        "processed_batches": processed_batches,
        "repaired_lines": total_repaired,
        "blocker": None,
        "aborted_remaining_batches": False,
    }
