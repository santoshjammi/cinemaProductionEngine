"""P0-05: Cinematic shot-planning tests.

Proves the shot plan is cinematic (not mechanical one-line-per-shot), covers all
authoritative dialogue, respects scene integrity, and survives serialization.
"""
from __future__ import annotations

import json

import pytest

from movie_os.genesis2.shot_planner import (
    plan_episode_shots, plan_scene_shots, empty_shot,
)
from movie_os.genesis2.shot_validation import (
    detect_mechanical_coupling,
    dialogue_visual_coverage,
    shot_scene_integrity,
    shot_purpose_validity,
    shot_persistence_reconcile,
    authoritative_shot_plan_report,
)


def _scene(sid, title="Scene", desc="", emo="tense"):
    return {
        "scene_number": sid, "number": sid, "title": title,
        "scene_description": desc, "emotional_state": emo,
        "act": "Act I", "characters_present": ["Mark", "Sarah"],
        "narrative_beat": "",
    }


def _line(lid, speaker, text, **kw):
    return {
        "line_id": lid, "speaker": speaker, "text": text,
        "emotional_state_primary": "guarded", "delivery_intent": "quiet",
        "subtext": "don't push", "character_voice_id": "MSVR-" + speaker,
        "presentation_mode": "EXTERNAL",
        "listener_reaction_intent": "",
        **kw,
    }


def _dlg(scene_num, lines):
    return {"scene_number": scene_num, "lines": lines, "inner_voice": []}


# ---------------------------------------------------------------------------
# Mechanical coupling detector
# ---------------------------------------------------------------------------

def test_old_one_line_one_shot_fixture_detected():
    # Simulate the old mechanical behavior: 4 shots, each mapping 1 of 4 lines.
    shots = []
    for i, lid in enumerate(["L1", "L2", "L3", "L4"]):
        s = empty_shot(1, i + 1)
        s["dialogue_mapping"]["active_dialogue_line_ids"] = [lid]
        shots.append(s)
    mc = detect_mechanical_coupling(shots, ["L1", "L2", "L3", "L4"])
    assert mc["detected"] is True


def test_coincidental_equal_counts_not_automatically_blocked():
    # 4 shots / 4 lines but with a silent shot and a multi-line shot -> NOT mechanical.
    s1 = empty_shot(1, 1); s1["dialogue_mapping"]["active_dialogue_line_ids"] = ["L1"]
    s2 = empty_shot(1, 2); s2["dialogue_mapping"]["active_dialogue_line_ids"] = ["L2", "L3"]  # multi-line
    s3 = empty_shot(1, 3); s3["dialogue_mapping"]["active_dialogue_line_ids"] = []  # silent
    s4 = empty_shot(1, 4); s4["dialogue_mapping"]["active_dialogue_line_ids"] = ["L4"]
    mc = detect_mechanical_coupling([s1, s2, s3, s4], ["L1", "L2", "L3", "L4"])
    assert mc["detected"] is False


def test_multi_line_shot_supported():
    # A longer exchange produces at least one grouped two-shot (multi-line).
    shots = plan_scene_shots(
        _scene(1, "Dinner", "a quiet dinner at the kitchen table"),
        _dlg(1, [_line(f"1:D{i:03d}", "MARK" if i % 2 else "SARAH", f"line {i}")
                 for i in range(1, 8)]),
        1)
    multi = [s for s in shots if len(s["dialogue_mapping"]["active_dialogue_line_ids"]) > 1]
    assert len(multi) >= 1  # grouping produces at least one multi-line shot


def test_silent_shot_supported():
    shots = plan_scene_shots(_scene(1, "Opening", "Mark stands alone in the doorway"),
                             None, 1)  # no dialogue -> silence shots
    silent = [s for s in shots if not s["dialogue_mapping"]["active_dialogue_line_ids"]]
    assert len(silent) >= 1


def test_establishing_shot_without_dialogue_supported():
    scene = _scene(1, "The Home", "establishes the kitchen and front door")
    shots = plan_scene_shots(scene, _dlg(1, [_line("L1", "A", "hi")]), 1)
    est = [s for s in shots if s["purpose"] == "ESTABLISHING"]
    assert len(est) >= 1


def test_reaction_shot_with_offscreen_speaker_supported():
    scene = _scene(1, "Confront", "quiet confrontation at the table")
    lines = [
        _line("L1", "B", "Why did you keep this from me?"),  # question -> warrants reaction
        _line("L2", "A", "I couldn't."),
    ]
    shots = plan_scene_shots(scene, _dlg(1, lines), 1)
    reacts = [s for s in shots if s["purpose"] == "LISTENER_REACTION"]
    assert len(reacts) >= 1


# ---------------------------------------------------------------------------
# Coverage + integrity
# ---------------------------------------------------------------------------

def test_all_authoritative_lines_receive_visual_coverage():
    scene = _scene(1, "Scene", "kitchen table dinner")
    lines = [_line(f"L{i}", "A" if i % 2 else "B", f"line {i}") for i in range(1, 7)]
    shots = plan_scene_shots(scene, _dlg(1, lines), 1)
    cov = dialogue_visual_coverage(shots, [l["line_id"] for l in lines])
    assert cov["passed"] is True
    assert cov["coverage"] == 100.0


def test_orphan_dialogue_does_not_generate_shots():
    # Only authoritative scene 1 dialogue is planned; scenes 6/7 dialogue is ignored.
    scene = _scene(1, "S1", "dinner")
    shots = plan_episode_shots([scene], {1: _dlg(1, [_line("L1", "A", "hi")])})
    assert all(int(s["scene_id"]) == 1 for s in shots)


def test_orphan_scene_reference_blocks():
    s = empty_shot(99, 1)  # scene 99 not authoritative
    integ = shot_scene_integrity([s], [1])
    assert integ["passed"] is False
    assert integ["orphan_shot_scene_ids"] == [99]


def test_duplicate_shot_id_blocks():
    a = empty_shot(1, 1); a["shot_id"] = "SC01-SH01"
    b = empty_shot(1, 2); b["shot_id"] = "SC01-SH01"  # duplicate
    integ = shot_scene_integrity([a, b], [1])
    assert integ["passed"] is False
    assert integ["duplicate_shot_ids"] == ["SC01-SH01"]


def test_unmapped_authoritative_line_blocks():
    s = empty_shot(1, 1); s["dialogue_mapping"]["active_dialogue_line_ids"] = []
    cov = dialogue_visual_coverage([s], ["L1"])
    assert cov["passed"] is False
    assert cov["uncovered_lines"] == ["L1"]


def test_shot_purpose_missing_blocks():
    s = empty_shot(1, 1)  # purpose = ""
    purp = shot_purpose_validity([s])
    assert purp["passed"] is False
    assert purp["shots_without_purpose"] == ["SC01-SH01"]


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def test_shot_serialization_round_trip():
    scene = _scene(1, "S1", "dinner")
    shots = plan_scene_shots(scene, _dlg(1, [_line("L1", "A", "hi")]), 1)
    rep = shot_persistence_reconcile(shots)
    assert rep["passed"] is True
    assert rep["information_loss"] == 0


def test_shot_information_loss_blocks_freeze():
    # A report that shows loss must not pass.
    # (The freeze gate reads the report; a lossy report -> pass=False.)
    from movie_os.genesis2.freeze_gate import evaluate_genesis_freeze_eligibility
    from movie_os.genesis2.models import ProductionKnowledgePackage, PhaseResult
    pkg = ProductionKnowledgePackage(episode_id="E", run_id="r")
    for i in range(1, 13):
        pkg.phase_results.append(PhaseResult(phase_number=i, phase_name=f"P{i}"))
    brief = {
        "scenes": [{"scene_number": 1, "title": "S", "realizes_requirements": ["REQ-001"]}],
        "canonical_requirements": [{"id": "REQ-001", "obligation": "MUST"}],
        "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"},
        "ending": "They reconnect.",
        "authoritative_shot_plan": {
            "mechanical_coupling": False,
            "dialogue_visual_coverage": {"uncovered_lines": ["L1"]},
            "scene_integrity": {"invalid_scene_references": [], "orphan_shot_scene_ids": [], "duplicate_shot_ids": []},
        },
    }
    res = evaluate_genesis_freeze_eligibility(pkg, brief)
    assert res.freeze_allowed is False
    assert any(b["code"] == "UNMAPPED_AUTHORITATIVE_LINE" for b in res.blocking_reasons)


# ---------------------------------------------------------------------------
# Planner-level: non-mechanical
# ---------------------------------------------------------------------------

def test_planner_produces_cinematic_not_mechanical():
    scene = _scene(1, "Confront", "confrontation at the dinner table")
    lines = [_line(f"L{i}", "A" if i % 2 else "B", f"line {i}") for i in range(1, 8)]
    shots = plan_scene_shots(scene, _dlg(1, lines), 1)
    mc = detect_mechanical_coupling(shots, [l["line_id"] for l in lines])
    assert mc["detected"] is False
    purposes = {s["purpose"] for s in shots}
    assert "LISTENER_REACTION" in purposes or "TWO_SHOT" in purposes


# helper for readability in this module
def coverage_dummy(s):
    return s
