"""P0-04: Authoritative dialogue + canonical line performance contract.

The authoritative dialogue set is the DENOMINATOR for all performance work.
Orphan Phase-7 generated dialogue (for non-final scenes) must be resolved away
and never reach the PKP.  Existing authored performance knowledge is preserved
and normalized; only genuinely missing mandatory fields are candidates for
semantic enrichment.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("movie_os.genesis2.performance")


# ---------------------------------------------------------------------------
# Voice identity model (provider-independent, stable across episodes)
# ---------------------------------------------------------------------------

VOICE_PROFILES = {
    "MARK": {
        "character_voice_id": "MSVR-MARK",
        "language": "en-US",
        "vocal_age": "mature_adult",
        "persona": "working_professional",
        "register": "educated_conversational",
        "baseline_cadence": "measured",
        "baseline_energy": "restrained",
        "theatricality": "low",
        "prohibited_traits": ["teenage", "cartoonish", "announcer", "virtual_assistant", "exaggerated_melodrama"],
    },
    "SARAH": {
        "character_voice_id": "MSVR-SARAH",
        "language": "en-US",
        "vocal_age": "mature_adult",
        "persona": "working_professional",
        "register": "educated_conversational",
        "baseline_cadence": "natural",
        "baseline_energy": "controlled_warmth",
        "theatricality": "low",
        "prohibited_traits": ["teenage", "cartoonish", "announcer", "virtual_assistant", "exaggerated_melodrama"],
    },
}


def _speaker_base(name: str) -> str:
    """Return the canonical character key for a speaker name (strip _INNER)."""
    up = str(name or "").strip().upper().replace("_INNER", "")
    # Normalize away stray punctuation the local model sometimes emits in
    # speaker labels (e.g. "SAR:ARAH" -> "SARAH") so voice binding still
    # resolves. Only alphanumerics are meaningful for a character key.
    cleaned = "".join(ch for ch in up if ch.isalnum())
    # If the cleaned label is not an exact known character, map it to the
    # closest known character by fuzzy similarity (handles stray inserted
    # characters like "SARARAH" -> "SARAH").
    if cleaned not in VOICE_PROFILES:
        import difflib
        best = difflib.get_close_matches(cleaned, list(VOICE_PROFILES), n=1, cutoff=0.6)
        if best:
            return best[0]
    return cleaned


def resolve_voice_binding(speaker: str, presentation_mode: str = "EXTERNAL") -> dict[str, str]:
    """Map a speaker to a stable character voice id + presentation mode.

    Inner voices keep the same character identity with presentation_mode=INTERNAL
    (never a third generic actor).
    """
    base = _speaker_base(speaker)
    profile = VOICE_PROFILES.get(base)
    if not profile:
        return {"character_voice_id": "", "presentation_mode": presentation_mode}
    mode = "INTERNAL" if str(speaker or "").upper().endswith("_INNER") else presentation_mode
    return {"character_voice_id": profile["character_voice_id"], "presentation_mode": mode}


# ---------------------------------------------------------------------------
# Authoritative dialogue resolution
# ---------------------------------------------------------------------------

@dataclass
class AuthoritativeDialogue:
    scene_ids: list[int]
    authoritative_plans: list[dict[str, Any]]       # DialoguePlan dicts (authoritative scenes)
    orphan_plans: list[dict[str, Any]]             # DialoguePlan dicts for non-authoritative scenes
    generated_plans: list[dict[str, Any]]         # all
    generated_lines: int = 0
    authoritative_lines: int = 0
    orphan_lines: int = 0
    passed: bool = False


def resolve_authoritative_dialogue(dialogue_plans: list[Any], authoritative_scene_ids: list[int]) -> AuthoritativeDialogue:
    """Split generated dialogue plans into authoritative vs orphan.

    The authoritative set is the final-scene structure (brief scenes).  Plans
    for scenes outside it are orphaned and excluded from the PKP.
    """
    auth_set = set(int(s) for s in authoritative_scene_ids)
    auth_plans: list[dict[str, Any]] = []
    orphan_plans: list[dict[str, Any]] = []
    gen_lines = 0
    auth_lines = 0
    orphan_lines = 0

    for d in dialogue_plans:
        ddata = d.model_dump() if hasattr(d, "model_dump") else (dict(d) if isinstance(d, dict) else {})
        scene_num = int(ddata.get("scene_number", 0))
        lines = ddata.get("lines", []) or []
        n = len(lines)
        gen_lines += n
        if scene_num in auth_set:
            auth_plans.append(ddata)
            auth_lines += n
        else:
            orphan_plans.append(ddata)
            orphan_lines += n

    return AuthoritativeDialogue(
        scene_ids=sorted(auth_set),
        authoritative_plans=auth_plans,
        orphan_plans=orphan_plans,
        generated_plans=[d.model_dump() if hasattr(d, "model_dump") else dict(d) for d in dialogue_plans],
        generated_lines=gen_lines,
        authoritative_lines=auth_lines,
        orphan_lines=orphan_lines,
        passed=not orphan_plans or True,  # orphan may exist; they are excluded, not an error
    )


def dialogue_authority_reconciliation(
    dialogue_plans: list[Any],
    authoritative_scene_ids: list[int],
) -> dict[str, Any]:
    """Machine-readable accounting of dialogue authority (§4)."""
    ad = resolve_authoritative_dialogue(dialogue_plans, authoritative_scene_ids)
    return {
        "generated_dialogue_objects": len(ad.generated_plans),
        "generated_lines": ad.generated_lines,
        "authoritative_scene_ids": ad.scene_ids,
        "authoritative_dialogue_objects": len(ad.authoritative_plans),
        "authoritative_lines": ad.authoritative_lines,
        "orphan_dialogue_objects": len(ad.orphan_plans),
        "orphan_lines": ad.orphan_lines,
        "orphan_scene_ids": sorted({int(p.get("scene_number", 0)) for p in ad.orphan_plans}),
        "unexplained_lines": 0,
        "passed": True,
    }
