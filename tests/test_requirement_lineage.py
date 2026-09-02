"""Tests for P0-03R: canonical requirement lineage repair.

The architectural rule: the denominator for reconciliation must come from the
frozen canonical requirement manifest (upstream of creative transformations),
NEVER from the artifact being evaluated.  Eight requirements do not require
eight scenes; a scene may realize several requirements.  But requirement IDs
must never be compressed away.
"""
from __future__ import annotations

import pytest

from movie_os.genesis2.requirement_manifest import (
    compile_episode_requirements,
    map_scene_to_requirements,
    RequirementManifest,
    EpisodeRequirement,
)
from movie_os.genesis2.freeze_gate import (
    evaluate_genesis_freeze_eligibility,
    reconcile_requirements,
    _beat_to_req,
)
from run_space_between_us import SYNOPSIS


def _canonical() -> list[dict]:
    m = compile_episode_requirements(episode_id="EP-0001", synopsis=SYNOPSIS, contract={"working_title": "x"})
    return [r.to_dict() for r in m.requirements]


def _pkg(scenes: list[dict], *, validation_passed=True) -> dict:
    return {
        "phase_results": [
            {"phase_number": i, "phase_name": f"P{i}", "status": "completed", "knowledge": {}}
            for i in range(1, 13)
        ],
        "validation": {"passed": validation_passed, "score": 1.0},
        "scene_planning": {"scenes": scenes},
        "dialogue_planning": {"dialogues": []},
        "creative_critique": {"findings": []},
        "story": {"ending": "Mark reaches for her hand."},
        "narrative_expansion": {"scenes": scenes},
    }


def _brief(scenes: list[dict], canon: list[dict]) -> dict:
    return {
        "scenes": scenes,
        "dialogues": [],
        "canonical_requirements": canon,
        "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"},
    }


# ---------------------------------------------------------------------------
# Canonical denominator
# ---------------------------------------------------------------------------

def test_canonical_denominator_not_derived_from_scenes():
    canon = _canonical()
    assert len(canon) == 8
    # The manifest is frozen and has a content hash.
    m = compile_episode_requirements(episode_id="EP-0001", synopsis=SYNOPSIS, contract={"working_title": "x"})
    assert m.frozen is True
    assert m.content_hash


def test_downstream_requirement_compression_does_not_change_denominator():
    # Even if scenes only realize 5 requirements, the denominator stays 8.
    canon = _canonical()
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "A", "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "realizes_requirements": ["REQ-003", "REQ-004"]},
        {"scene_number": 3, "narrative_beat": "climax", "title": "C", "realizes_requirements": ["REQ-005"]},
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert rec["required_coverage"]["total"] == 8  # denominator is canonical, not scene-derived


def test_missing_one_of_eight_requirements_blocks():
    canon = _canonical()
    scenes = [
        {"scene_number": n, "narrative_beat": "x", "title": f"S{n}",
         "realizes_requirements": [f"REQ-{n:03d}"]} for n in range(1, 8)  # drops REQ-008
    ]
    res = evaluate_genesis_freeze_eligibility(_pkg(scenes), _brief(scenes, canon))
    assert res.freeze_allowed is False
    assert any("REQ-008" in b.get("detail", "") for b in res.blocking_reasons)


def test_missing_two_of_eight_reports_75_percent():
    canon = _canonical()
    scenes = [
        {"scene_number": n, "narrative_beat": "x", "title": f"S{n}",
         "realizes_requirements": [f"REQ-{n:03d}"]} for n in range(1, 7)  # drops REQ-007, REQ-008
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert rec["required_coverage"]["total"] == 8
    assert rec["required_coverage"]["preserved"] == 6
    assert rec["required_coverage"]["percentage"] == 75.0
    assert set(rec["missing_requirements"]) == {"REQ-007", "REQ-008"}


def test_all_eight_requirements_across_five_scenes_pass():
    # 8 requirements realized across only 5 scenes (many-to-one) must pass.
    canon = _canonical()
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "A", "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "realizes_requirements": ["REQ-003"]},
        {"scene_number": 3, "narrative_beat": "plot", "title": "C", "realizes_requirements": ["REQ-004", "REQ-005"]},
        {"scene_number": 4, "narrative_beat": "climax", "title": "D", "realizes_requirements": ["REQ-006", "REQ-007"]},
        {"scene_number": 5, "narrative_beat": "resolution", "title": "E", "realizes_requirements": ["REQ-008"]},
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert rec["passed"] is True
    assert rec["required_coverage"]["percentage"] == 100.0


def test_one_scene_realizes_multiple_requirements():
    canon = _canonical()
    scenes = [
        {"scene_number": 1, "narrative_beat": "climax", "title": "Confrontation",
         "realizes_requirements": ["REQ-004", "REQ-006", "REQ-007"]},
        {"scene_number": 2, "narrative_beat": "resolution", "title": "Reconnect",
         "realizes_requirements": ["REQ-008"]},
        {"scene_number": 3, "narrative_beat": "hook", "title": "Job Loss",
         "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 4, "narrative_beat": "plot", "title": "Distance",
         "realizes_requirements": ["REQ-003", "REQ-005"]},
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert rec["passed"] is True
    assert rec["required_coverage"]["percentage"] == 100.0


def test_one_requirement_realized_across_multiple_scenes():
    canon = _canonical()
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "A", "realizes_requirements": ["REQ-001"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 3, "narrative_beat": "plot", "title": "C", "realizes_requirements": ["REQ-003", "REQ-004"]},
        {"scene_number": 4, "narrative_beat": "climax", "title": "D", "realizes_requirements": ["REQ-005", "REQ-006"]},
        {"scene_number": 5, "narrative_beat": "resolution", "title": "E", "realizes_requirements": ["REQ-007", "REQ-008"]},
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert rec["passed"] is True


# ---------------------------------------------------------------------------
# Inciting incident representation modes
# ---------------------------------------------------------------------------

def test_inciting_incident_visual_evidence_passes():
    canon = _canonical()
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "The Email",
         "scene_description": "Sarah sees the termination email while Mark closes the laptop.",
         "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "realizes_requirements": ["REQ-003", "REQ-004"]},
        {"scene_number": 3, "narrative_beat": "plot", "title": "C", "realizes_requirements": ["REQ-005"]},
        {"scene_number": 4, "narrative_beat": "climax", "title": "D", "realizes_requirements": ["REQ-006", "REQ-007"]},
        {"scene_number": 5, "narrative_beat": "resolution", "title": "E", "realizes_requirements": ["REQ-008"]},
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert rec["passed"] is True


def test_inciting_incident_uncommunicated_fails():
    # Story starts with Mark withdrawn, never establishes why (job loss absent).
    canon = _canonical()
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "The Silence",
         "scene_description": "Mark eats in silence.", "realizes_requirements": ["REQ-002"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "realizes_requirements": ["REQ-003", "REQ-004"]},
        {"scene_number": 3, "narrative_beat": "plot", "title": "C", "realizes_requirements": ["REQ-005"]},
        {"scene_number": 4, "narrative_beat": "climax", "title": "D", "realizes_requirements": ["REQ-006", "REQ-007"]},
        {"scene_number": 5, "narrative_beat": "resolution", "title": "E", "realizes_requirements": ["REQ-008"]},
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert "REQ-001" in rec["missing_requirements"]


# ---------------------------------------------------------------------------
# Confrontation representation
# ---------------------------------------------------------------------------

def test_quiet_confrontation_passes():
    canon = _canonical()
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "A", "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "realizes_requirements": ["REQ-003", "REQ-004"]},
        {"scene_number": 3, "narrative_beat": "plot", "title": "C", "realizes_requirements": ["REQ-005"]},
        {"scene_number": 4, "narrative_beat": "climax", "title": "The Quiet Truth",
         "scene_description": "Sarah directly names the avoidance and forces the central truth into the interaction.",
         "realizes_requirements": ["REQ-006", "REQ-007"]},
        {"scene_number": 5, "narrative_beat": "resolution", "title": "E", "realizes_requirements": ["REQ-008"]},
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert rec["passed"] is True


def test_absent_confrontation_fails():
    # withdrawal -> quiet confession -> hand reach, with no moment directly
    # engaging the central relational tension.
    canon = _canonical()
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "A", "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "realizes_requirements": ["REQ-003", "REQ-004"]},
        {"scene_number": 3, "narrative_beat": "plot", "title": "C", "realizes_requirements": ["REQ-005"]},
        {"scene_number": 4, "narrative_beat": "climax", "title": "The Confession",
         "scene_description": "Sarah quietly confesses her hurt.", "realizes_requirements": ["REQ-007"]},
        {"scene_number": 5, "narrative_beat": "resolution", "title": "E", "realizes_requirements": ["REQ-008"]},
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert "REQ-006" in rec["missing_requirements"]


# ---------------------------------------------------------------------------
# Phase preservation / id survival
# ---------------------------------------------------------------------------

def test_requirement_disappears_between_phases():
    canon = _canonical()
    # A requirement dropped from BOTH scene_planning and narrative_expansion is lost.
    sp_scenes = [
        {"scene_number": n, "narrative_beat": "x", "title": f"S{n}",
         "realizes_requirements": [f"REQ-{n:03d}"]} for n in range(1, 8)  # drops REQ-008
    ]
    ne_scenes = [
        {"scene_number": n, "narrative_beat": "x", "title": f"S{n}",
         "realizes_requirements": [f"REQ-{n:03d}"]} for n in range(1, 8)  # also drops REQ-008
    ]
    pkg = _pkg(sp_scenes)
    pkg["narrative_expansion"] = {"scenes": ne_scenes}
    rec = reconcile_requirements(pkg, canon, None)
    assert "REQ-008" in rec["missing_requirements"]


def test_requirement_id_survives_all_phases():
    canon = _canonical()
    scenes = [
        {"scene_number": n, "narrative_beat": "x", "title": f"S{n}",
         "realizes_requirements": [f"REQ-{n:03d}"]} for n in range(1, 9)
    ]
    rec = reconcile_requirements(_pkg(scenes), canon, _brief(scenes, canon))
    assert rec["passed"] is True
    assert rec["missing_requirements"] == []


def test_beat_to_req_translation():
    assert _beat_to_req("BEAT-001") == "REQ-001"
    assert _beat_to_req("BEAT-006") == "REQ-006"
    assert _beat_to_req("REQ-003") == "REQ-003"


def test_story_ending_not_reverse_fabricated():
    # The bridge must not derive ending from the last scene; it uses the
    # authoritative synopsis resolution.  Verify the manifest compiler is
    # independent of scene count.
    m = compile_episode_requirements(episode_id="EP-0001", synopsis=SYNOPSIS, contract={"working_title": "x"})
    assert m.frozen is True
    assert len(m.must_requirements()) == 8
