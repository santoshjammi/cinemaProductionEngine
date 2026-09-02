"""Tests for P0-03: story → narrative → scene semantic preservation and reconciliation.

GENESIS must become a transformation chain where later phases preserve
contractual meaning.  Required beats must be mapped, act order must be valid
for LINEAR stories, required resolution must be present, and the cross-phase
reconciliation matrix must reach 100% required coverage.
"""
from __future__ import annotations

import pytest

from movie_os.genesis2.freeze_gate import (
    act_order_valid,
    reconcile_requirements,
    story_requirements_from_contract,
)
from movie_os.genesis2.requirement_manifest import compile_episode_requirements
from run_space_between_us import SYNOPSIS


def _beats(count: int = 8) -> list[dict]:
    return [{"id": f"BEAT-{n:03d}", "required": True} for n in range(1, count + 1)]


def _pkg_with_scenes(scenes: list[dict]) -> dict:
    return {
        "scene_planning": {"scenes": scenes},
        "narrative_expansion": {"scenes": scenes},
        "phase_results": [],
    }


def test_required_beat_missing_from_all_scenes():
    scenes = [
        {"scene_number": 1, "act": "Act I", "narrative_beat": "inciting",
         "title": "A", "realizes_requirements": ["BEAT-001", "BEAT-002"]},
    ]
    rec = reconcile_requirements(_pkg_with_scenes(scenes), _beats())
    assert rec["passed"] is False
    assert set(rec["missing_requirements"]) >= {"BEAT-003", "BEAT-008"}


def test_all_required_beats_mapped():
    scenes = [
        {"scene_number": n, "act": "Act I", "narrative_beat": "x",
         "realizes_requirements": [f"BEAT-{n:03d}"], "title": f"S{n}"}
        for n in range(1, 9)
    ]
    rec = reconcile_requirements(_pkg_with_scenes(scenes), _beats())
    assert rec["passed"] is True
    assert rec["required_coverage"]["preserved"] == 8
    assert rec["required_coverage"]["percentage"] == 100.0


def test_multi_scene_arc_candidate_generated_for_valid_progression():
    reqs = [r.to_dict() for r in compile_episode_requirements(episode_id="EP-0001", synopsis=SYNOPSIS, contract={"working_title": "x"}).requirements]
    scenes = [
        {"scene_number": 1, "title": "Silent Dinner", "narrative_beat": "hook",
         "conflict": "Mark's fear of being seen as a failure vs. Sarah's desire for connection",
         "outcome": "Mark gives short answers at dinner, avoiding eye contact",
         "emotional_objective": "Mark feels isolated from Sarah"},
        {"scene_number": 2, "title": "Connection Attempt", "narrative_beat": "plot",
         "conflict": "Mark's fear of being perceived as inadequate vs. Sarah's need for intimacy",
         "outcome": "Sarah says, 'You don't have to disappear just because you're hurting.'",
         "emotional_objective": "Sarah hopes Mark will respond"},
        {"scene_number": 3, "title": "Fractured Light", "narrative_beat": "turning_point",
         "conflict": "Mark's internal fear vs. the urge to reconnect",
         "outcome": "Mark almost reaches for Sarah's hand but stops himself",
         "emotional_objective": "Mark feels his fear is overwhelming"},
    ]
    rec = reconcile_requirements(_pkg_with_scenes(scenes), reqs, {"scenes": scenes, "dialogues": []})
    req005 = rec["requirements"]["REQ-005"]
    assert req005["candidates"]
    assert req005["realized"] is True
    assert req005["by_scenes"]


def test_multi_scene_arc_rejects_non_progressive_window():
    reqs = [r.to_dict() for r in compile_episode_requirements(episode_id="EP-0001", synopsis=SYNOPSIS, contract={"working_title": "x"}).requirements]
    scenes = [
        {"scene_number": 1, "title": "Stillness", "narrative_beat": "hook",
         "conflict": "Mark feels distant", "outcome": "Mark remains silent", "emotional_objective": "Mark stays withdrawn"},
        {"scene_number": 2, "title": "Stillness Again", "narrative_beat": "plot",
         "conflict": "Mark feels distant", "outcome": "Mark remains silent", "emotional_objective": "Mark stays withdrawn"},
        {"scene_number": 3, "title": "Stillness Again", "narrative_beat": "turning_point",
         "conflict": "Mark feels distant", "outcome": "Mark remains silent", "emotional_objective": "Mark stays withdrawn"},
    ]
    rec = reconcile_requirements(_pkg_with_scenes(scenes), reqs, {"scenes": scenes, "dialogues": []})
    req005 = rec["requirements"]["REQ-005"]
    assert req005["candidates"] == []
    assert req005["realized"] is False
    ok, reason = act_order_valid([
        {"act": "Act III", "scene_number": 1},
        {"act": "Act II", "scene_number": 2},
        {"act": "Act I", "scene_number": 3},
    ])
    assert ok is False
    assert "regress" in reason.lower()


def test_valid_linear_act_sequence():
    ok, _ = act_order_valid([
        {"act": "Act I", "scene_number": 1},
        {"act": "Act II", "scene_number": 2},
        {"act": "Act III", "scene_number": 3},
    ])
    assert ok is True


def test_later_phase_drops_required_beat():
    # A beat missing from BOTH scene_planning and narrative_expansion is lost.
    reqs = _beats()
    rec = reconcile_requirements(
        {
            "scene_planning": {"scenes": [
                {"scene_number": n, "act": "Act I", "realizes_requirements": [f"BEAT-{n:03d}"]}
                for n in range(1, 8)  # drops BEAT-008
            ]},
            "narrative_expansion": {"scenes": [
                {"scene_number": n, "act": "Act I", "realizes_requirements": [f"BEAT-{n:03d}"]}
                for n in range(1, 8)  # also drops BEAT-008
            ]},
            "phase_results": [],
        },
        reqs,
    )
    assert "BEAT-008" in rec["missing_requirements"]


def test_later_phase_preserves_all_required_beats():
    reqs = _beats()
    rec = reconcile_requirements(
        {
            "scene_planning": {"scenes": [
                {"scene_number": n, "realizes_requirements": [f"BEAT-{n:03d}"]} for n in range(1, 9)
            ]},
            "narrative_expansion": {"scenes": [
                {"scene_number": n, "realizes_requirements": [f"BEAT-{n:03d}"]} for n in range(1, 9)
            ]},
            "phase_results": [],
        },
        reqs,
    )
    assert rec["passed"] is True


def test_contract_declared_requirements_win_over_default():
    contract = {"story_requirements": [{"id": "B-1", "required": True}]}
    reqs = story_requirements_from_contract(contract)
    assert reqs == [{"id": "B-1", "required": True}]


def test_default_requirements_used_when_contract_silent():
    reqs = story_requirements_from_contract(None)
    assert len(reqs) == 8
    assert reqs[0]["id"] == "BEAT-001"
