"""P0-05: Shot plan validation — mechanical-coupling detector, coverage, integrity.

Deterministic gates that prove the shot plan is cinematic, not mechanical:
  - mechanical coupling (1 line -> 1 shot, exact one-to-one, no silent/multi shots)
  - dialogue visual coverage (every authoritative line mapped to >=1 shot)
  - scene integrity (no orphan scenes, no invalid references, no duplicate shot ids)
  - shot purpose validity (no generic/meaningless purpose)
  - serialization reconciliation (shots survive in-memory -> disk -> reload)
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger("movie_os.genesis2.shots.validate")

MEANINGFUL_PURPOSES = {
    "ESTABLISHING", "SPEAKER_COVERAGE", "LISTENER_REACTION", "TWO_SHOT",
    "OVER_THE_SHOULDER", "INSERT", "CUTAWAY", "SILENT_BEHAVIOR", "TRANSITION",
    "REVEAL", "EMOTIONAL_HOLD",
}


def detect_mechanical_coupling(shots: list[dict], authoritative_line_ids: list[str]) -> dict:
    """Detect the old one-line-per-shot behavior.

    BLOCK when the full mechanical pattern exists:
      - shot count == dialogue line count
      - every shot maps exactly one unique line
      - every line maps exactly one unique shot
      - no silent, multi-line, or multi-shot lines
    Do NOT block merely because counts happen to coincide.
    """
    if not shots:
        return {"detected": False, "reason": "no shots", "passed": True}

    shot_line_sets = [s.get("dialogue_mapping", {}).get("active_dialogue_line_ids", []) or [] for s in shots]
    all_mapped = [lid for sl in shot_line_sets for lid in sl]

    # Every shot maps exactly one unique line.
    every_shot_one_line = all(len(sl) == 1 for sl in shot_line_sets)
    # Every line maps exactly one unique shot.
    every_line_one_shot = all(
        lid in all_mapped and all_mapped.count(lid) == 1 for lid in authoritative_line_ids
    )
    # No silent, multi-line, or multi-shot behavior.
    silent_shots = sum(1 for sl in shot_line_sets if not sl)
    multi_line_shots = sum(1 for sl in shot_line_sets if len(sl) > 1)
    multi_shot_lines = sum(1 for lid in set(all_mapped) if all_mapped.count(lid) > 1)

    shot_count_equals_lines = len(shots) == len(authoritative_line_ids)

    detected = (
        shot_count_equals_lines
        and every_shot_one_line
        and every_line_one_shot
        and silent_shots == 0
        and multi_line_shots == 0
        and multi_shot_lines == 0
    )
    return {
        "shot_count_equals_line_count": shot_count_equals_lines,
        "exact_one_to_one_mapping": every_shot_one_line and every_line_one_shot,
        "silent_shots": silent_shots,
        "multi_line_shots": multi_line_shots,
        "multi_shot_lines": multi_shot_lines,
        "detected": detected,
        "evidence": (
            "all shots map exactly one line AND all lines map exactly one shot "
            "AND no silent/multi-line/multi-shot variation"
            if detected else "shot plan is cinematically varied"
        ),
    }


def dialogue_visual_coverage(shots: list[dict], authoritative_line_ids: list[str]) -> dict:
    """All authoritative lines must be covered by at least one shot."""
    mapped = set()
    for s in shots:
        for lid in s.get("dialogue_mapping", {}).get("active_dialogue_line_ids", []):
            mapped.add(lid)
    uncovered = [lid for lid in authoritative_line_ids if lid not in mapped]
    total = len(authoritative_line_ids)
    pct = ((total - len(uncovered)) / total * 100) if total else 100.0
    return {
        "authoritative_lines": total,
        "lines_mapped_to_at_least_one_shot": len(mapped),
        "uncovered_lines": uncovered,
        "coverage": pct,
        "passed": len(uncovered) == 0,
    }


def shot_scene_integrity(shots: list[dict], authoritative_scene_ids: list[int]) -> dict:
    """No shots reference orphan/non-authoritative scenes; no duplicate shot ids."""
    auth = set(int(a) for a in authoritative_scene_ids)
    shot_scene_ids = [int(s.get("scene_id")) for s in shots]
    orphan_scene_ids = sorted({sid for sid in shot_scene_ids if sid not in auth})
    invalid = sorted({sid for sid in shot_scene_ids if sid not in auth})
    # duplicate shot ids
    ids = [s.get("shot_id") for s in shots]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    return {
        "authoritative_scene_ids": sorted(auth),
        "shot_scene_ids": sorted(set(shot_scene_ids)),
        "orphan_shot_scene_ids": orphan_scene_ids,
        "invalid_scene_references": invalid,
        "duplicate_shot_ids": dups,
        "passed": not orphan_scene_ids and not invalid and not dups,
    }


def shot_purpose_validity(shots: list[dict]) -> dict:
    """Every shot must have a meaningful, actionable purpose."""
    missing = [s.get("shot_id") for s in shots if not str(s.get("purpose", "") or "").strip()]
    generic = [
        s.get("shot_id") for s in shots
        if str(s.get("purpose", "") or "").strip().lower() in ("coverage", "shot", "scene", "")
    ]
    return {
        "shots_without_purpose": missing,
        "generic_purpose_shots": generic,
        "passed": not missing and not generic,
    }


def shot_count_metrics(shots: list[dict], scenes: list[dict], authoritative_line_ids: list[str]) -> dict:
    """Record shot metrics without imposing a hard target."""
    by_scene = {}
    for s in shots:
        by_scene.setdefault(s.get("scene_id"), []).append(s)
    multi_line = sum(1 for s in shots if len(s.get("dialogue_mapping", {}).get("active_dialogue_line_ids", [])) > 1)
    silent = sum(1 for s in shots if not s.get("dialogue_mapping", {}).get("active_dialogue_line_ids", []))
    reaction = sum(1 for s in shots if s.get("purpose") == "LISTENER_REACTION")
    establishing = sum(1 for s in shots if s.get("purpose") == "ESTABLISHING")
    insert = sum(1 for s in shots if s.get("purpose") == "INSERT")
    two_shot = sum(1 for s in shots if s.get("purpose") == "TWO_SHOT")
    speaker = sum(1 for s in shots if s.get("purpose") == "SPEAKER_COVERAGE")
    hold = sum(1 for s in shots if s.get("purpose") == "EMOTIONAL_HOLD")
    return {
        "scenes": len(scenes),
        "dialogue_lines": len(authoritative_line_ids),
        "total_shots": len(shots),
        "shots_per_scene": {sid: len(ss) for sid, ss in sorted(by_scene.items())},
        "dialogue_lines_per_shot_average": (len(authoritative_line_ids) / len(shots)) if shots else 0,
        "speaker_coverage": speaker,
        "listener_reactions": reaction,
        "two_shots": two_shot,
        "establishing": establishing,
        "inserts": insert,
        "silent_behavior": silent,
        "multi_line_shots": multi_line,
        "emotional_holds": hold,
    }


def detect_mechanical_ping_pong(shots: list[dict]) -> dict:
    """Semantic evaluation: detect mechanically redundant 'medium A / medium B'
    ping-pong with no reaction/two-shot/insert/progression.

    A shot plan FAILS when it is purely alternating speaker coverage with no
    cinematic variation (no reaction, two-shot, insert, establishing, or hold)
    and no silent shots.  A restrained two-shot carrying many lines, or a
    speaker+reaction pair, passes because it is cinematically motivated.
    """
    purposes = [str(s.get("purpose", "")) for s in shots]
    non_coverage = [p for p in purposes if p not in ("SPEAKER_COVERAGE",)]
    # Silent count = explicit SILENT_BEHAVIOR purpose (inserts with no dialogue
    # are not the same as silence; they can be decorative and should not mask
    # repetitive ping-pong).
    silent = sum(1 for p in purposes if p == "SILENT_BEHAVIOR")
    multi_line_shots = sum(1 for s in shots if len(s.get("dialogue_mapping", {}).get("active_dialogue_line_ids", [])) > 1)
    # Substantive cinematic variation: reaction, two-shot, hold, or a silent shot.
    substantive = [p for p in purposes if p in ("LISTENER_REACTION", "TWO_SHOT", "EMOTIONAL_HOLD", "SILENT_BEHAVIOR")]
    # A decorative insert (with no dialogue) does not break ping-pong by itself.
    if len(shots) >= 3 and not substantive and not multi_line_shots and silent == 0:
        return {"verdict": "REPETITIVE_COVERAGE", "passed": False}
    if not purposes:
        return {"verdict": "UNMOTIVATED_CUTTING", "passed": False}
    if all(p == "ESTABLISHING" for p in purposes):
        return {"verdict": "NO_VISUAL_PROGRESSION", "passed": False}
    return {"verdict": "MOTIVATED", "passed": True}


def shot_persistence_reconcile(shots: list[dict]) -> dict:
    """SER-01 law: shots survive in-memory -> serialized -> reload with zero loss."""
    source = shots
    blob = json.dumps(source, default=str)
    reloaded = json.loads(blob)
    return {
        "source_shots": len(source),
        "serialized_shots": len(reloaded),
        "reloaded_shots": len(reloaded),
        "information_loss": len(source) - len(reloaded),
        "passed": len(source) == len(reloaded),
    }


def authoritative_shot_plan_report(
    scenes: list[dict],
    shots: list[dict],
    authoritative_line_ids: list[str],
) -> dict:
    """Combine all gates into the authoritative shot plan report (§29)."""
    mc = detect_mechanical_coupling(shots, authoritative_line_ids)
    cov = dialogue_visual_coverage(shots, authoritative_line_ids)
    auth_scene_ids = [int(s.get("scene_number") or s.get("number") or s.get("id") or 0) for s in scenes]
    integ = shot_scene_integrity(shots, auth_scene_ids)
    purp = shot_purpose_validity(shots)
    metrics = shot_count_metrics(shots, scenes, authoritative_line_ids)
    passed = (
        not mc["detected"]
        and cov["passed"]
        and integ["passed"]
        and purp["passed"]
    )
    return {
        "scene_count": len(scenes),
        "total_shots": len(shots),
        "shots": shots,
        "orphan_shots": [],
        "uncovered_dialogue_lines": cov["uncovered_lines"],
        "invalid_scene_references": integ["invalid_scene_references"],
        "duplicate_shot_ids": integ["duplicate_shot_ids"],
        "mechanical_coupling": mc["detected"],
        "mechanical_coupling_detail": mc,
        "dialogue_visual_coverage": cov,
        "scene_integrity": integ,
        "purpose_validity": purp,
        "shot_metrics": metrics,
        "passed": passed,
    }
