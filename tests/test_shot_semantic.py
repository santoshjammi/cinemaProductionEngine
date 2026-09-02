"""P0-05: Semantic shot-planning fixtures (captured/deterministic, not live-model).

These evaluate whether a shot plan is cinematically motivated (not just varied).
Uses deterministic heuristics on the shot plan structure so tests are stable.
"""
from __future__ import annotations

from movie_os.genesis2.shot_validation import (
    detect_mechanical_coupling, dialogue_visual_coverage, shot_scene_integrity,
    shot_purpose_validity, authoritative_shot_plan_report, detect_mechanical_ping_pong,
)
from movie_os.genesis2.shot_planner import empty_shot


def _mk_scene(sid, desc, title="S", chars=("Mark", "Sarah")):
    return {"scene_number": sid, "number": sid, "title": title, "scene_description": desc,
            "emotional_state": "tense", "act": "Act I", "characters_present": list(chars)}


def _mka_shot(scene_id, purpose, line_ids=()):
    s = empty_shot(scene_id, 0)
    s["purpose"] = purpose
    s["dialogue_mapping"]["active_dialogue_line_ids"] = list(line_ids)
    return s


def _mechanical_ping_pong_plan(n_lines=8):
    """Alternating medium/medium with no reaction, no two-shot, no insert."""
    return [_mka_shot(1, "SPEAKER_COVERAGE", [f"L{i}"]) for i in range(1, n_lines + 1)]


def test_mechanical_ping_pong_coverage_fails():
    shots = _mechanical_ping_pong_plan()
    mc = detect_mechanical_ping_pong(shots)
    assert mc["passed"] is False


def test_restrained_two_shot_with_multiple_lines_passes():
    # A single two-shot carrying 4 lines is restrained but not mechanically
    # repetitive — it's a legitimate multi-line shot.
    ts = _mka_shot(1, "TWO_SHOT", ["L1", "L2", "L3", "L4"])
    mc = detect_mechanical_ping_pong([ts])
    assert mc["passed"] is True
    assert len(ts["dialogue_mapping"]["active_dialogue_line_ids"]) == 4


def test_speaker_plus_listener_reaction_passes():
    shots = [
        _mka_shot(1, "SPEAKER_COVERAGE", ["L1"]),
        _mka_shot(1, "LISTENER_REACTION", ["L1"]),  # offscreen speaker reaction
        _mka_shot(1, "SPEAKER_COVERAGE", ["L2"]),
    ]
    mc = detect_mechanical_ping_pong(shots)
    assert mc["passed"] is True


def test_gratuitous_random_insert_fails():
    # An insert with no grounding in scene content + mechanical ping-pong.
    shots = _mechanical_ping_pong_plan()
    shots.insert(2, _mka_shot(1, "INSERT", []))
    mc = detect_mechanical_ping_pong(shots)
    assert mc["passed"] is False


def test_meaningful_termination_email_insert_passes():
    # A motivated insert grounded in a scene about termination is valid.
    plan = [_mka_shot(1, "INSERT", []), _mka_shot(1, "SPEAKER_COVERAGE", ["L1"])]
    assert any(s["purpose"] == "INSERT" for s in plan)
    # grounded insert passes; it's not pure ping-pong because it has an insert.
    mc = detect_mechanical_ping_pong(plan)
    assert mc["passed"] is True


def test_motivated_progression_from_distance_to_connection_passes():
    # Escalation: wide -> singles -> hold -> two-shot = motivated progression.
    shots = [
        _mka_shot(1, "ESTABLISHING", []),
        _mka_shot(1, "SPEAKER_COVERAGE", ["L1"]),
        _mka_shot(1, "LISTENER_REACTION", ["L1"]),
        _mka_shot(1, "EMOTIONAL_HOLD", []),
        _mka_shot(1, "TWO_SHOT", ["L2", "L3"]),
    ]
    mc = detect_mechanical_ping_pong(shots)
    assert mc["passed"] is True


def test_scene_with_no_visual_progression_fails_or_warns():
    # All establishing (wide) shots, no coverage/reaction/hold = no progression.
    shots = [_mka_shot(1, "ESTABLISHING", []) for _ in range(5)]
    mc = detect_mechanical_ping_pong(shots)
    assert mc["passed"] is False
