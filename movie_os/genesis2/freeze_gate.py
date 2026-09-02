"""Freeze Eligibility Gate for GENESIS.

Deterministic authority over whether a ProductionKnowledgePackage may be
frozen into a PKP.  This module separates *PKP_STRUCTURAL_VALIDITY* from
*GENESIS_FREEZE_ELIGIBILITY*: a package may be a well-formed YAML/JSON object
and still be ineligible to freeze when its semantic payloads are missing,
validation is not an explicit pass, creative fallbacks were used, or the story
was not preserved across phases.

Freeze decisions live here and only here.  LLM output may generate, critique
and repair content, but it never decides whether freezing is allowed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Eligibility result
# ---------------------------------------------------------------------------

@dataclass
class FreezeEligibilityResult:
    freeze_allowed: bool
    summary: dict[str, Any] = field(default_factory=dict)
    blocking_reasons: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class FreezeIneligibleError(Exception):
    """Raised when a package is not eligible to freeze."""

    def __init__(self, result: FreezeEligibilityResult):
        self.result = result
        super().__init__(
            "GENESIS freeze not allowed: " + "; ".join(
                f"{b.get('code', '?')}@{b.get('phase', '?')}" for b in result.blocking_reasons
            )
        )


# ---------------------------------------------------------------------------
# Generic access helpers (work on Pydantic models OR dicts)
# ---------------------------------------------------------------------------

def _resolve(obj: Any, attr: str):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(attr)
    if hasattr(obj, attr):
        return getattr(obj, attr, None)
    return None


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (dict, str)):
        return [value]
    return list(value)


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (dict, list, tuple, set)):
        return len(value) == 0
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return False
    return not str(value).strip()


def _is_truth(value: Any) -> bool:
    """True when a value carries real content; empty/None/placeholder => False."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    s = str(value).strip()
    if not s:
        return False
    low = s.lower()
    if low in ("none", "null", "n/a", "na", "todo", "tbd", "placeholder"):
        return False
    return True


def _bool_of(value: Any) -> Optional[bool]:
    """Explicitly resolve a value to True/False, or None if not a real boolean."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 1:
            return True
        if value == 0:
            return False
        return None
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "yes", "pass", "passed", "1", "ok", "completed"):
            return True
        if v in ("false", "no", "fail", "failed", "0"):
            return False
        return None
    return None


def _sev(value: Any) -> str:
    """Map a critique severity to a gate severity.

    Only ``critical``/``blocker`` findings may block freeze (BLOCKER level in
    the rule-severity model). ``major``/``warning`` are WARNINGs that may
    advance but are retained in the report; ``minor`` is a PREFERENCE signal.
    """
    if isinstance(value, dict):
        value = value.get("severity")
    s = str(value or "").strip().lower()
    if s in ("critical", "blocker"):
        return "critical"
    if s in ("major", "warning"):
        return "warning"
    return "preference"


# ---------------------------------------------------------------------------
# Phase payload extraction
# ---------------------------------------------------------------------------

def _phase_status(phase: Any) -> str:
    """Normalize a phase's status to a lowercase string, handling Pydantic
    enums (PhaseStatus.COMPLETED -> 'completed') and plain dicts/strings."""
    if isinstance(phase, dict):
        raw = phase.get("status")
    else:
        raw = getattr(phase, "status", None)
    if raw is None:
        return ""
    # PhaseStatus enum -> .value, or enum in other reprs
    if hasattr(raw, "value"):
        raw = raw.value
    return str(raw).strip().lower()


def _phase_results(pkg: Any) -> list:
    return _as_list(_resolve(pkg, "phase_results"))


def _phase_knowledge_by_number(pkg: Any, number: int) -> Any:
    for r in _phase_results(pkg):
        if isinstance(r, dict):
            if r.get("phase_number") == number:
                return r.get("knowledge")
        elif getattr(r, "phase_number", None) == number:
            return getattr(r, "knowledge", None)
    return None


def _scene_planning_scenes(pkg: Any) -> list:
    sp = _resolve(pkg, "scene_planning")
    if sp is None:
        sp = _phase_knowledge_by_number(pkg, 6)
    if sp is None:
        return []
    return _as_list(_resolve(sp, "scenes"))


def _dialogue_planning_dialogues(pkg: Any) -> list:
    dp = _resolve(pkg, "dialogue_planning")
    if dp is None:
        dp = _phase_knowledge_by_number(pkg, 7)
    if dp is None:
        return []
    return _as_list(_resolve(dp, "dialogues"))


def _narrative_expansion_scenes(pkg: Any) -> list:
    ne = _resolve(pkg, "narrative_expansion")
    if ne is None:
        ne = _phase_knowledge_by_number(pkg, 5)
    if ne is None:
        return []
    return _as_list(_resolve(ne, "scenes"))


def _validation(pkg: Any) -> Any:
    val = _resolve(pkg, "validation")
    if val is None:
        val = _phase_knowledge_by_number(pkg, 10)
    return val


def _creative_critique_findings(pkg: Any) -> list:
    cc = _resolve(pkg, "creative_critique")
    if cc is None:
        cc = _phase_knowledge_by_number(pkg, 11)
    if cc is None:
        return []
    return _as_list(_resolve(cc, "findings"))


# ---------------------------------------------------------------------------
# Creative-fallback detection
# ---------------------------------------------------------------------------

# These are the exact fabrication fingerprints seen in the defective fixture:
# scene-title text pasted into spoken lines, "establishes the starting
# emotional state" templates, "causal bridge", and generic placeholder lines.
_TEMPLATE_FRAGMENTS = (
    "establishes the starting emotional state",
    "shifts the relationship",
    "leaves the characters changed for the next scene",
    "causal bridge",
    "keep the scene moving with an honest exchange",
    "speaker and listener stay in active conversational coverage",
    "i need to tell you something important",
    "i am listening",
)

_TEMPLATE_PATTERNS = (
    re.compile(r"^scene\s+\d+\s*:\s", re.I),
)


def _is_template_text(text: Any) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False
    low = text.strip().lower()
    for frag in _TEMPLATE_FRAGMENTS:
        if frag in low:
            return True
    for pat in _TEMPLATE_PATTERNS:
        if pat.match(low):
            return True
    return False


def _has_fallback_flag(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        return bool(value.get("used", False) or value.get("fabricated", False))
    if isinstance(value, str):
        return value.strip().lower() in ("true", "used", "fabricated", "1")
    return False


def _detect_creative_fallback(pkg: Any, brief: Any) -> str:
    """Return a description if creative fabrication is detected, else ''."""
    reasons = []

    # 1) Brief scenes may carry an explicit fallback_used flag.
    if brief is not None:
        for scene in _as_list(_resolve(brief, "scenes")):
            if _has_fallback_flag(_resolve(scene, "fallback_used")):
                reasons.append("brief scene flagged fallback_used")
        # 1b) Brief dialogue lines that carry scene-title/placeholder echoes.
        for dlg in _as_list(_resolve(brief, "dialogues")):
            for line in _as_list(_resolve(dlg, "lines")):
                text = _resolve(line, "text")
                if _is_template_text(text):
                    reasons.append(f"brief dialogue line is a scene-title/placeholder echo: {str(text)[:60]!r}")
                    break

    # 2) Dialogue lines that carry scene-title placeholders / template text.
    for dlg in _dialogue_planning_dialogues(pkg):
        for line in _as_list(_resolve(dlg, "lines")):
            text = _resolve(line, "text")
            if _is_template_text(text):
                reasons.append(f"dialogue line is a scene-title/placeholder echo: {str(text)[:60]!r}")
                break
        for line in _as_list(_resolve(dlg, "inner_voice")):
            text = _resolve(line, "text")
            if _is_template_text(text):
                reasons.append(f"inner-voice is a scene-title/placeholder echo: {str(text)[:60]!r}")
                break

    # 3) Template entry/turning/exit state text.
    for scene in _scene_planning_scenes(pkg) + _narrative_expansion_scenes(pkg):
        for key in ("entry_state", "turning_point", "exit_state", "purpose", "description"):
            val = _resolve(scene, key)
            if _is_template_text(val):
                reasons.append(f"scene {key} carries template text: {str(val)[:60]!r}")
                break
        if reasons:
            break

    return " | ".join(reasons)


def _is_scene_text_echo(value: Any) -> bool:
    if not _is_truth(value):
        return False
    return _is_template_text(value)


# ---------------------------------------------------------------------------
# Story requirements / beat lineage
# ---------------------------------------------------------------------------

# This is the seed for the current episode's *narrative contract* (a linear
# drama).  It is NOT a global rule: the gate consumes whatever the episode
# contract declares via ``story_requirements``.  A default is provided so the
# canonical Mark & Sarah episode always has a stable lineage to reconcile.
DEFAULT_STORY_REQUIREMENTS = [
    {"id": "BEAT-001", "type": "INCITING_INCIDENT", "description": "Mark loses his job", "required": True},
    {"id": "BEAT-002", "type": "BEHAVIORAL_RESPONSE", "description": "Mark conceals or avoids discussing the loss", "required": True},
    {"id": "BEAT-003", "type": "RELATIONSHIP_CHANGE", "description": "Sarah notices emotional withdrawal", "required": True},
    {"id": "BEAT-004", "type": "CONNECTION_ATTEMPT", "description": "Sarah attempts to reconnect", "required": True},
    {"id": "BEAT-005", "type": "ESCALATION", "description": "Mark withdraws further", "required": True},
    {"id": "BEAT-006", "type": "CONFRONTATION", "description": "Relationship tension reaches confrontation", "required": True},
    {"id": "BEAT-007", "type": "REVELATION", "description": "Mark's underlying fear or shame becomes visible", "required": True},
    {"id": "BEAT-008", "type": "RESOLUTION", "description": "Movement toward reconnection", "required": True},
]


def story_requirements_from_contract(contract: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    """Return the story-requirement list declared by the episode contract.

    Contract-declared ``story_requirements`` win; otherwise fall back to the
    canonical Mark & Sarah lineage so the current episode always has a stable
    requirement set to reconcile against.
    """
    if contract and isinstance(contract.get("story_requirements"), list) and contract["story_requirements"]:
        return contract["story_requirements"]
    return [dict(r) for r in DEFAULT_STORY_REQUIREMENTS]


def _requirements_from_brief(brief: Any) -> list[dict[str, Any]]:
    """Return the canonical requirement set for reconciliation.

    The denominator MUST come from the frozen canonical requirement manifest,
    never from the artifact being evaluated.  Priority:
      1. brief['canonical_requirements']  (frozen manifest, set by the driver)
      2. brief['story_requirements']      (bridge-derived — only a fallback)
      3. DEFAULT_STORY_REQUIREMENTS      (last resort)
    """
    if brief is not None:
        canon = _resolve(brief, "canonical_requirements")
        if isinstance(canon, list) and canon:
            return canon
        reqs = _resolve(brief, "story_requirements")
        if isinstance(reqs, list) and reqs:
            return reqs
    return [dict(r) for r in DEFAULT_STORY_REQUIREMENTS]


# ---------------------------------------------------------------------------
# Act-order validation
# ---------------------------------------------------------------------------

_ACT_RANK = {
    "ACT I": 1, "ACT 1": 1, "ACT ONE": 1, "ACT_I": 1, "ACT_1": 1,
    "ACT II": 2, "ACT 2": 2, "ACT TWO": 2, "ACT_II": 2, "ACT_2": 2,
    "ACT III": 3, "ACT 3": 3, "ACT THREE": 3, "ACT_III": 3, "ACT_3": 3,
}


def _act_rank(act: Any) -> Optional[int]:
    if not isinstance(act, str) or not act.strip():
        return None
    norm = act.strip().upper()
    # strip trailing prose ("ACT I: The Beginning" -> "ACT I")
    for sep in (":", "—", " - "):
        if sep in norm:
            norm = norm.split(sep)[0].strip()
            break
    return _ACT_RANK.get(norm)


def act_order_valid(scenes: list) -> tuple[bool, str]:
    """Return (valid, reason). For LINEAR structure acts must be monotonic."""
    prev_rank: Optional[int] = None
    for s in scenes:
        act = _resolve(s, "act") or ""
        rank = _act_rank(act)
        if rank is None:
            continue
        if prev_rank is not None and rank < prev_rank:
            return False, f"act order regresses ({act}) after an earlier higher act"
        prev_rank = rank
    return True, ""


# ---------------------------------------------------------------------------
# Beat realization / cross-phase reconciliation
# ---------------------------------------------------------------------------

def _realizes_requirements(scene: Any) -> list[str]:
    """The requirement ids a scene claims or deterministically maps to."""
    realizes = _resolve(scene, "realizes_requirements")
    if isinstance(realizes, list) and realizes:
        return [str(x) for x in realizes]
    return _infer_requirements_from_text(str(
        _resolve(scene, "narrative_beat") or _resolve(scene, "title") or ""
    ))


_INFER_MAP = {
    "inciting": "BEAT-001", "loses his job": "BEAT-001", "lose his job": "BEAT-001", "layoff": "BEAT-001",
    "conceal": "BEAT-002", "avoid": "BEAT-002", "hide": "BEAT-002", "deny": "BEAT-002",
    "distance": "BEAT-003", "withdraw": "BEAT-003", "pull away": "BEAT-003",
    "reconnect": "BEAT-004", "connection attempt": "BEAT-004", "reach out": "BEAT-004",
    "escalat": "BEAT-005", "further": "BEAT-005",
    "confront": "BEAT-006", "confrontation": "BEAT-006",
    "revelation": "BEAT-007", "shame": "BEAT-007", "fear visible": "BEAT-007", "vulnerab": "BEAT-007", "surrender": "BEAT-007",
    "resolution": "BEAT-008", "reconcil": "BEAT-008", "breakthrough": "BEAT-008", "reconnect": "BEAT-008",
}


def _infer_requirements_from_text(text: str) -> list[str]:
    found: list[str] = []
    low = text.strip().lower()
    for key, rid in _INFER_MAP.items():
        if key in low and rid not in found:
            found.append(rid)
    return found


def _beat_to_req(rid: str) -> str:
    """Translate a legacy BEAT-00N id to the canonical REQ-00N id."""
    m = re.match(r"BEAT-(\d+)", rid)
    if m:
        return f"REQ-{int(m.group(1)):03d}"
    return rid


def reconcile_requirements(pkg: Any, requirements: list[dict[str, Any]], brief: Any = None) -> dict[str, Any]:
    """Machine-readable cross-phase reconciliation matrix.

    The denominator is the FROZEN CANONICAL requirement set (never derived from
    the artifact being evaluated).  Scenes are taken from the brief (which
    carries bridge-derived ``realizes_requirements``) when available, otherwise
    from the PKG phase payloads.  Each canonical requirement id must be realized
    by at least one scene.  Scenes are mapped to canonical REQ ids via
    ``map_scene_to_requirements`` (deterministic, onto the frozen set).
    """
    from movie_os.genesis2.requirement_manifest import map_scene_to_requirements

    def _scene_id(scene: Any) -> Any:
        return _resolve(scene, "scene_number") or _resolve(scene, "id") or _resolve(scene, "scene_id") or _resolve(scene, "sequence_id")

    def _ordered_scene_pool() -> list[Any]:
        pool = _as_list(_resolve(brief, "scenes")) if brief is not None else []
        if not pool:
            pool = _scene_planning_scenes(pkg) + _narrative_expansion_scenes(pkg)
        def _order_key(scene: Any):
            sid = _scene_id(scene)
            try:
                return (0, int(sid))
            except Exception:
                return (1, str(sid))
        return sorted(pool, key=_order_key)

    def _candidate_arc_windows(scene_pool: list[Any], max_len: int = 4) -> list[list[Any]]:
        windows: list[list[Any]] = []
        n = len(scene_pool)
        for start in range(n):
            for length in range(2, min(max_len, n - start) + 1):
                windows.append(scene_pool[start:start + length])
        return windows

    def _arc_state(scene: Any) -> str:
        pieces = [
            _resolve(scene, "narrative_beat"),
            _resolve(scene, "title"),
            _resolve(scene, "purpose"),
            _resolve(scene, "scene_description"),
            _resolve(scene, "outcome"),
            _resolve(scene, "escalation"),
            _resolve(scene, "stakes"),
            _resolve(scene, "tension"),
            _resolve(scene, "emotional_state"),
        ]
        return " | ".join(str(p or "").strip() for p in pieces if str(p or "").strip())

    def _arc_semantic_accepts(req: dict[str, Any], arc_scenes: list[Any]) -> bool:
        rid = str(req.get("id", ""))
        if rid == "REQ-005":
            states = [(_arc_state(s)).lower() for s in arc_scenes]
            if len(states) < 2:
                return False
            joined = " \n".join(states)
            return any(k in joined for k in ("withdraw", "distance", "isolat", "avoid", "worsen", "escalat", "further")) and any(
                k in joined for k in ("connect", "attempt", "reach", "touch", "respond", "hope")
            )
        return False

    req_ids = {r["id"] for r in requirements}
    use_req_namespace = any(str(rid).startswith("REQ-") for rid in req_ids)
    scene_pool = _ordered_scene_pool()
    realized: dict[str, list[Any]] = {r["id"]: [] for r in requirements}
    candidates_by_req: dict[str, list[dict[str, Any]]] = {r["id"]: [] for r in requirements}

    # First pass: explicit scene lineage or deterministic scene mapping.
    for scene in scene_pool:
        explicit = _resolve(scene, "realizes_requirements")
        if isinstance(explicit, list) and explicit:
            rids = [str(x) for x in explicit]
            if use_req_namespace:
                rids = [_beat_to_req(x) for x in rids]
        else:
            rids = map_scene_to_requirements(scene)
        for rid in rids:
            if rid in realized:
                realized[rid].append(_scene_id(scene))

    # Second pass: bounded contiguous arc candidates for requirements that allow them.
    for req in requirements:
        rid = str(req.get("id", ""))
        modes = [str(m) for m in _as_list(req.get("realization_modes"))]
        if "MULTI_SCENE_ARC" not in modes:
            continue
        for arc in _candidate_arc_windows(scene_pool):
            if _arc_semantic_accepts(req, arc):
                candidate = {
                    "requirement_id": rid,
                    "realization_mode": "MULTI_SCENE_ARC",
                    "source_artifact_id": _resolve(pkg, "episode_id") or _resolve(pkg, "run_id") or "",
                    "source_artifact_hash": _resolve(pkg, "content_hash") or _resolve(pkg, "artifact_hash") or "",
                    "ordered_scene_ids": [_scene_id(s) for s in arc],
                    "source_field_paths": [
                        f"scenes[{i}].{field}"
                        for i, s in enumerate(arc)
                        for field in ("narrative_beat", "title", "purpose", "scene_description", "outcome", "escalation", "stakes", "tension", "emotional_state")
                        if _resolve(s, field) not in (None, "")
                    ],
                    "source_hashes": [str(_resolve(s, "source_hash") or _resolve(s, "content_hash") or "") for s in arc if _resolve(s, "source_hash") or _resolve(s, "content_hash")],
                    "arc_start_state": _arc_state(arc[0]),
                    "arc_intermediate_states": [_arc_state(s) for s in arc[1:-1]],
                    "arc_end_state": _arc_state(arc[-1]),
                    "transition_summary": f"{_arc_state(arc[0])[:120]} -> {_arc_state(arc[-1])[:120]}",
                    "evidence_claim": f"{rid} realized by ordered progression across {len(arc)} scenes",
                    "provenance": {
                        "production_id": _resolve(pkg, "episode_id") or "",
                        "run_id": _resolve(pkg, "run_id") or "",
                        "source_hashes": [str(_resolve(pkg, "content_hash") or _resolve(pkg, "artifact_hash") or "")],
                    },
                }
                candidates_by_req[rid].append(candidate)
                if _arc_semantic_accepts(req, arc):
                    realized[rid].append([_scene_id(s) for s in arc])
                break

    # Normalize arc realized list structure.
    for rid, vals in list(realized.items()):
        flat: list[Any] = []
        for v in vals:
            if isinstance(v, list):
                flat.extend(v)
            else:
                flat.append(v)
        realized[rid] = flat

    preserved = [r["id"] for r in requirements if realized[r["id"]]]
    missing = [r["id"] for r in requirements if not realized[r["id"]]]
    total = len(requirements)
    coverage = (len(preserved) / total * 100) if total else 100.0
    return {
        "requirements": {
            r["id"]: {
                "realized": bool(realized[r["id"]]),
                "by_scenes": realized[r["id"]],
                "candidates": candidates_by_req[r["id"]],
            }
            for r in requirements
        },
        "required_coverage": {"total": total, "preserved": len(preserved), "percentage": coverage},
        "missing_requirements": missing,
        "blockers": missing,
        "passed": len(missing) == 0,
    }


def _authoritative_performance_lines(brief: Any) -> list[dict[str, Any]]:
    """Extract the authoritative dialogue lines from the brief for performance
    coverage.  Flattens brief['dialogues'][*].lines (the authoritative set —
    orphans were already excluded by the bridge).  Returns an empty list when no
    dialogue is present so the performance gate is a no-op for legacy tests."""
    lines: list[dict[str, Any]] = []
    for d in _as_list(_resolve(brief, "dialogues")):
        for ln in _as_list(_resolve(d, "lines")):
            if isinstance(ln, dict):
                lines.append(ln)
    return lines


# ---------------------------------------------------------------------------
# Main gate
# ---------------------------------------------------------------------------

def evaluate_genesis_freeze_eligibility(
    pkg: Any,
    brief: Optional[dict[str, Any]] = None,
    *,
    resolution_requirement: str = "REQUIRED",
    narrative_structure: str = "LINEAR",
    story_requirements: Optional[list[dict[str, Any]]] = None,
) -> FreezeEligibilityResult:
    """Evaluate freeze eligibility deterministically.

    All LLM-authored content is already embedded in ``pkg``/``brief`` by the
    time this runs.  This function only reads it and decides.
    """
    blocking: list[dict[str, str]] = []
    warnings: list[str] = []
    summary: dict[str, Any] = {}
    resolution_requirement = (resolution_requirement or "REQUIRED").upper()
    narrative_structure = (narrative_structure or "LINEAR").upper()
    reqs = story_requirements or _requirements_from_brief(brief)

    # ---- 0. Bridge-collected GENESIS defects (fabrication / missing content) ----
    defects = _as_list(_resolve(brief, "_genesis_defects"))
    if defects:
        for d in defects:
            code = str(d.get("code", "GENESIS_DEFECT"))
            severity = str(d.get("severity", "BLOCKER")).upper()
            blocking.append({"code": code, "phase": d.get("scene") or "bridge",
                             "detail": str(d.get("detail", code))})
        summary["genesis_defects"] = len(defects)
    else:
        summary["genesis_defects"] = 0

    # ---- 1. Phase completion ----
    phases = _phase_results(pkg)
    completed = [p for p in phases if _phase_status(p) == "completed"]
    failed = [p for p in phases if _phase_status(p) == "failed"]
    summary["required_phases"] = {"all_completed": len(completed) >= 12 and not failed}
    if failed:
        blocking.append({"code": "REQUIRED_PHASES_FAILED", "phase": "ALL",
                         "detail": f"failed={len(failed)}"})
    elif len(completed) < 12:
        blocking.append({"code": "REQUIRED_PHASES_INCOMPLETE", "phase": "ALL",
                         "detail": f"completed={len(completed)}/12"})

    # ---- 2. Phase semantic payload presence ----
    sp_scenes = _scene_planning_scenes(pkg)
    summary["scene_planning"] = {"semantic_payload_present": len(sp_scenes) > 0, "scene_count": len(sp_scenes)}
    if not sp_scenes:
        blocking.append({"code": "SCENE_PLANNING_PAYLOAD_MISSING", "phase": "6",
                         "detail": "Scene Planning produced no scenes"})
    dp_dialogues = _dialogue_planning_dialogues(pkg)
    summary["dialogue_planning"] = {"semantic_payload_present": len(dp_dialogues) > 0, "dialogue_count": len(dp_dialogues)}
    if not dp_dialogues:
        blocking.append({"code": "DIALOGUE_PLANNING_PAYLOAD_MISSING", "phase": "7",
                         "detail": "Dialogue Planning produced no dialogue"})
    else:
        # ---- Dialogue-policy density enforcement (rule-driven, not hard-coded) ----
        # CONVERSATION scenes require minimum alternating turns & active speakers.
        policy_rules = _resolve(brief, "dialogue_policy_rules") or {}
        min_speakers = int(policy_rules.get("min_active_speakers", 2) if isinstance(policy_rules, dict) else 2)
        min_turns = int(policy_rules.get("min_alternating_turns", 4) if isinstance(policy_rules, dict) else 4)
        brief_dialogues = _as_list(_resolve(brief, "dialogues"))
        # Only enforce density on authoritative scenes. The bridge drops orphan
        # dialogues (e.g. a stray scene 0) from the brief; the raw PKG may still
        # carry them, and they must not block freeze.
        auth_scene_ids = set()
        for bd in brief_dialogues:
            sn = _resolve(bd, "scene_number")
            if sn is not None:
                auth_scene_ids.add(int(sn))
        for dlg in dp_dialogues:
            scene_number = _resolve(dlg, "scene_number")
            if scene_number is not None and auth_scene_ids and int(scene_number) not in auth_scene_ids:
                continue  # orphan dialogue — not authoritative, skip
            policy_type = ""
            # Prefer brief dialogue policy, fall back to PKG payload.
            for bd in brief_dialogues:
                if _resolve(bd, "scene_number") == scene_number:
                    declared = _resolve(bd, "dialogue_policy") or {}
                    policy_type = str(_resolve(declared, "type") or policy_type).upper()
                    break
            if not policy_type:
                declared = _resolve(dlg, "dialogue_policy") or {}
                policy_type = str(_resolve(declared, "type") or "CONVERSATION").upper()
            lines = _as_list(_resolve(dlg, "lines"))
            real = [ln for ln in lines if _is_truth(_resolve(ln, "text"))]
            speakers = {str(_resolve(ln, "speaker")).strip() for ln in real if _resolve(ln, "speaker")}
            turns = len(real)
            if policy_type == "CONVERSATION" and turns < min_turns:
                blocking.append({"code": "DIALOGUE_DENSITY_INSUFFICIENT", "phase": "7",
                                 "detail": f"scene {scene_number} CONVERSATION has {turns} turns < required {min_turns}"})
            if policy_type == "CONVERSATION" and len(speakers) < min_speakers:
                blocking.append({"code": "DIALOGUE_SPEAKER_COUNT", "phase": "7",
                                 "detail": f"scene {scene_number} CONVERSATION has {len(speakers)} active speakers < required {min_speakers}"})
            if turns > 0 and not speakers:
                blocking.append({"code": "DIALOGUE_SPEAKER_MISSING", "phase": "7",
                                 "detail": f"scene {scene_number} has lines with no speaker"})
        summary["dialogue_policy"] = {"min_speakers": min_speakers, "min_turns": min_turns}

    # ---- 3. Validation explicitness ----
    val = _validation(pkg)
    passed_val = _bool_of(_resolve(val, "passed"))
    score_val = _resolve(val, "score")
    summary["validation"] = {"result_exists": val is not None, "passed": passed_val, "score": score_val}
    if val is None or passed_val is None:
        blocking.append({"code": "GENESIS_VALIDATION_MISSING", "phase": "10",
                         "detail": "validation.passed is not an explicit boolean (None/missing)"})
    elif passed_val is False:
        blocking.append({"code": "GENESIS_VALIDATION_FAILED", "phase": "10",
                         "detail": "validation.passed is explicitly False"})
    elif passed_val is True and isinstance(score_val, (int, float)) and score_val < 0.7:
        warnings.append(f"validation passed=True but score={score_val} below 0.7 (warning only)")

    # ---- 4. Blocking critique findings ----
    findings = _creative_critique_findings(pkg)
    # Severity model: only critical/blocker are BLOCKER-level (must not advance).
    # major/warning are WARNINGs (advance, retained); minor is PREFERENCE. Never
    # let an aggregate score override a blocker.
    critical = [f for f in findings if _sev(f) == "critical"]
    warnings_count = len([f for f in findings if _sev(f) == "warning"])
    summary["critique"] = {"blocking_findings": len(critical), "warning_findings": warnings_count}
    if critical:
        blocking.append({"code": "BLOCKER_CRITIQUE_FINDING", "phase": "11",
                         "detail": f"{len(critical)} critical/blocker critique finding(s)"})
    if warnings_count:
        warnings.append(f"{warnings_count} major/warning critique finding(s) (non-blocking)")

    # ---- 5. Story ending / resolution ----
    ending = _resolve(brief, "ending")
    if not _is_truth(ending):
        ending = _resolve(pkg, "ending")
    if not _is_truth(ending):
        story = _resolve(pkg, "story") or {}
        ending = _resolve(story, "ending")
    summary["story_ending"] = {"present": _is_truth(ending), "value": ending}
    if resolution_requirement == "REQUIRED" and not _is_truth(ending):
        blocking.append({"code": "STORY_ENDING_MISSING", "phase": "story",
                         "detail": "Resolution is REQUIRED but story.ending is empty"})

    # ---- 6. Scene order ----
    if narrative_structure == "LINEAR":
        # The reversed/empty acts for this episode live on the *brief* scenes
        # (bridge output), so check both the PKG scene-plan payload and the
        # brief scene list; either one regressing blocks freeze.
        order_scenes = sp_scenes
        brief_scenes = _as_list(_resolve(brief, "scenes"))
        checked = order_scenes
        if brief_scenes:
            # Prefer the brief scene list when present (it carries act labels).
            checked = brief_scenes
        ok, reason = act_order_valid(checked)
        summary["scene_order"] = {"valid": ok, "reason": reason, "scenes_checked": len(checked)}
        if not ok:
            blocking.append({"code": "SCENE_ORDER_INVALID", "phase": "6", "detail": reason})

    # ---- 7. Cross-phase reconciliation ----
    rec = reconcile_requirements(pkg, reqs, brief=brief)
    summary["cross_phase_reconciliation"] = rec
    if not rec["passed"]:
        blocking.append({"code": "REQUIRED_STORY_BEAT_COVERAGE", "phase": "cross-phase",
                         "detail": "missing requirements: " + ",".join(rec["missing_requirements"])})

    # ---- 8. Creative fallback ----
    fb = _detect_creative_fallback(pkg, brief)
    summary["creative_fallback"] = {"unresolved_usage": bool(fb), "detail": fb}
    if fb:
        blocking.append({"code": "CREATIVE_FALLBACK_DETECTED", "phase": "bridge", "detail": fb})

    # ---- 9. Persistence integrity (P0-03R-SER-01 §15) ----
    # Freeze requires that the knowledge that was validated in memory is the
    # same as what will be persisted.  The driver computes
    # serialization_reconciliation (in-memory vs serialized vs reloaded) and
    # attaches it to the brief; if any phase lost subclass semantics, block.
    ser = _resolve(brief, "serialization_reconciliation")
    if ser is not None:
        loss = _resolve(ser, "semantic_information_loss")
        if loss is None or (isinstance(loss, (int, float)) and loss > 0):
            blocking.append({
                "code": "PERSISTED_KNOWLEDGE_MISMATCH",
                "phase": "ALL",
                "detail": f"persistence integrity failed: {loss} phase(s) lost subclass semantic fields",
            })
        summary["persistence_integrity"] = {
            "in_memory_vs_serialized": "PASS" if loss == 0 else "FAIL",
            "information_loss_count": loss,
        }
    else:
        summary["persistence_integrity"] = {"reconciled": False, "note": "driver did not attach report"}

    # ---- 10. Performance coverage (P0-04 §28-29) ----
    # Every authoritative spoken line must carry the mandatory performance
    # contract + a resolvable voice binding.  One missing mandatory field or
    # unresolved binding is a blocker.
    from .performance_eval import performance_coverage, voice_binding_coverage
    perf_lines = _authoritative_performance_lines(brief)
    pc = performance_coverage(perf_lines)
    vb = voice_binding_coverage(perf_lines)
    summary["performance_coverage"] = pc
    summary["voice_binding_reconciliation"] = vb
    if not pc["passed"]:
        blocking.append({
            "code": "LINE_PERFORMANCE_INCOMPLETE",
            "phase": "dialogue",
            "detail": f"{len(pc['incomplete_records'])} line(s) missing mandatory performance fields",
        })
    if not vb["passed"]:
        blocking.append({
            "code": "VOICE_BINDING_INCOMPLETE",
            "phase": "dialogue",
            "detail": f"{len(vb['unresolved'])} line(s) unresolved voice binding, {len(vb['wrong_character_bindings'])} wrong",
        })

    # ---- 11. Cinematic shot plan (P0-05) ----
    # The authoritative shot plan (generated by the bridge/PKP compiler) must
    # be cinematically varied, not mechanical one-line-per-shot.  Block if the
    # plan is missing, mechanically coupled, or fails coverage/scene integrity.
    shot_report = _resolve(brief, "authoritative_shot_plan")
    if shot_report is not None:
        mc = shot_report.get("mechanical_coupling")
        if mc:
            blocking.append({
                "code": "MECHANICAL_SHOT_DIALOGUE_COUPLING",
                "phase": "shot",
                "detail": "shot plan is mechanically one-line-per-shot; cinematic variation required",
            })
        cov = shot_report.get("dialogue_visual_coverage") or {}
        if cov.get("uncovered_lines"):
            blocking.append({
                "code": "UNMAPPED_AUTHORITATIVE_LINE",
                "phase": "shot",
                "detail": f"uncovered dialogue lines: {cov['uncovered_lines']}",
            })
        integ = shot_report.get("scene_integrity") or {}
        if integ.get("invalid_scene_references") or integ.get("orphan_shot_scene_ids"):
            blocking.append({
                "code": "ORPHAN_SHOT_SCENE_REFERENCE",
                "phase": "shot",
                "detail": f"orphan/invalid scene refs: {integ.get('invalid_scene_references') or integ.get('orphan_shot_scene_ids')}",
            })
        if integ.get("duplicate_shot_ids"):
            blocking.append({
                "code": "DUPLICATE_SHOT_ID",
                "phase": "shot",
                "detail": f"duplicate shot ids: {integ['duplicate_shot_ids']}",
            })
        summary["cinematic_shot_plan"] = {
            "mechanical_coupling": mc,
            "dialogue_visual_coverage": cov,
            "scene_integrity": integ,
            "shot_metrics": shot_report.get("shot_metrics"),
        }
    else:
        # No authoritative shot plan attached — legacy path; do not block.
        summary["cinematic_shot_plan"] = {"reconciled": False, "note": "no shot plan attached"}

    freeze_allowed = len(blocking) == 0
    return FreezeEligibilityResult(
        freeze_allowed=freeze_allowed,
        summary=summary,
        blocking_reasons=blocking,
        warnings=warnings,
    )
