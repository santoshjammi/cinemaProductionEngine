"""Tests for GENESIS freeze-eligibility gate (P0-01), creative-fallback
removal (P0-02), and story→scene reconciliation (P0-03).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from movie_os.genesis2.freeze_gate import (
    evaluate_genesis_freeze_eligibility,
    FreezeEligibilityResult,
    FreezeIneligibleError,
    act_order_valid,
    reconcile_requirements,
    story_requirements_from_contract,
)
from movie_os.frozen_pkp import freeze_from_brief, FreezeIneligibleError as FrozenFreezeIneligibleError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _pkg_dict(*, validation_passed=None, validation_exists=True,
              scene_plan_scenes=None, dialogue_dialogues=None,
              critique_findings=None, ending="", acts=None,
              phase_status="completed", phase_count=12):
    """Build a ProductionKnowledgePackage-shaped dict for gate tests."""
    phases = []
    for i in range(1, 13):
        phases.append({
            "phase_number": i,
            "phase_name": f"Phase {i:02d}",
            "status": phase_status if i not in (6, 7) else phase_status,
            "knowledge": {},
        })
    val = None
    if validation_exists:
        val = {"passed": validation_passed, "score": 1.0 if validation_passed else 0.0}
    sp = None
    if scene_plan_scenes:
        sp = {
            "scenes": [
                {
                    "scene_number": 1, "act": (acts[0] if acts else "Act I"),
                    "narrative_beat": "inciting", "title": "Job Loss",
                    "realizes_requirements": ["BEAT-001"],
                },
                {
                    "scene_number": 2, "act": (acts[1] if acts else "Act II"),
                    "narrative_beat": "confrontation", "title": "Confrontation",
                    "realizes_requirements": ["BEAT-006"],
                },
                {
                    "scene_number": 3, "act": (acts[2] if acts else "Act III"),
                    "narrative_beat": "resolution", "title": "Resolution",
                    "realizes_requirements": ["BEAT-008"],
                },
            ]
        }
    dp = None
    if dialogue_dialogues:
        dp = {"dialogues": dialogue_dialogues}
    cc = None
    if critique_findings is not None:
        cc = {"findings": critique_findings}
    return {
        "phase_results": phases,
        "validation": val,
        "scene_planning": sp,
        "dialogue_planning": dp,
        "creative_critique": cc,
        "story": {"ending": ending},
        "narrative_expansion": {"scenes": []},
    }


def _conversation_dialogue():
    return [
        {
            "scene_number": 1,
            "lines": [
                {"speaker": "MARK", "text": "We need to talk.", "emotion": "tense"},
                {"speaker": "SARAH", "text": "I'm listening.", "emotion": "calm"},
                {"speaker": "MARK", "text": "I lost my job.", "emotion": "ashamed"},
                {"speaker": "SARAH", "text": "It will be okay.", "emotion": "reassuring"},
            ],
        }
    ]


def _full_brief():
    """A brief that freeze can succeed on after gate passes."""
    return {
        "scenes": [
            {"number": 1, "title": "Job Loss", "act": "Act I", "narrative_beat": "inciting",
             "entry_state": "quiet", "turning_point": "Mark hides news", "exit_state": "distance"},
            {"number": 2, "title": "Confrontation", "act": "Act II", "narrative_beat": "confrontation",
             "entry_state": "tense", "turning_point": "Sarah pushes", "exit_state": "guarded"},
            {"number": 3, "title": "Resolution", "act": "Act III", "narrative_beat": "resolution",
             "entry_state": "vulnerable", "turning_point": "Mark opens up", "exit_state": "connected"},
        ],
        "dialogues": [
            {"scene_number": 1, "lines": [{"speaker": "MARK", "text": "I lost my job.", "emotion": "ashamed"}]},
            {"scene_number": 2, "lines": [{"speaker": "SARAH", "text": "Why didn't you tell me?", "emotion": "hurt"}]},
            {"scene_number": 3, "lines": [{"speaker": "MARK", "text": "I was scared.", "emotion": "vulnerable"}]},
        ],
        "characters": ["MARK", "SARAH"],
        "context": {"characters": [{"name": "MARK", "role": "protagonist", "visual_reference_id": "MSVI-MARK", "voice_reference_id": "MSVR-MARK", "approved_identity": "Mark canon"}, {"name": "SARAH", "role": "supporting", "visual_reference_id": "MSVI-SARAH", "voice_reference_id": "MSVR-SARAH", "approved_identity": "Sarah canon"}]},
        "logline": "A man withdraws after job loss.",
        "synopsis": "A man withdraws after job loss until his wife reaches out.",
        "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"},
    }


# ---------------------------------------------------------------------------
# P0-01 — Freeze eligibility (fail closed)
# ---------------------------------------------------------------------------

def test_validation_passed_true_allows_evaluation_to_continue():
    pkg = _pkg_dict(validation_passed=True, dialogue_dialogues=_conversation_dialogue(), ending="reconnect")
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief())
    # validation itself is fine; other blockers may remain but passed=True must not add one
    assert not any(b["code"].startswith("GENESIS_VALIDATION") for b in res.blocking_reasons)


def test_validation_passed_false_blocks_freeze():
    pkg = _pkg_dict(validation_passed=False, dialogue_dialogues=_conversation_dialogue())
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief())
    assert res.freeze_allowed is False
    assert any(b["code"] == "GENESIS_VALIDATION_FAILED" for b in res.blocking_reasons)


def test_validation_passed_none_blocks_freeze():
    pkg = _pkg_dict(validation_passed=None, dialogue_dialogues=_conversation_dialogue())
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief())
    assert res.freeze_allowed is False
    assert any(b["code"] == "GENESIS_VALIDATION_MISSING" for b in res.blocking_reasons)


def test_validation_missing_blocks_freeze():
    pkg = _pkg_dict(validation_exists=False, dialogue_dialogues=_conversation_dialogue())
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief())
    assert res.freeze_allowed is False
    assert any(b["code"] == "GENESIS_VALIDATION_MISSING" for b in res.blocking_reasons)


def test_critical_finding_blocks_freeze():
    pkg = _pkg_dict(
        validation_passed=True,
        dialogue_dialogues=_conversation_dialogue(),
        critique_findings=[{"severity": "critical", "question": "Q", "answer": "A"}],
        ending="reconnect",
    )
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief())
    assert res.freeze_allowed is False
    assert any(b["code"] == "BLOCKER_CRITIQUE_FINDING" for b in res.blocking_reasons)


def test_major_finding_is_nonblocking_warning():
    """Per rule-severity model: only critical/blocker blocks; major is a warning."""
    pkg = _pkg_dict(
        validation_passed=True,
        dialogue_dialogues=_conversation_dialogue(),
        critique_findings=[{"severity": "major", "question": "Q", "answer": "A"}],
        ending="reconnect",
    )
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief())
    assert not any(b["code"] == "BLOCKER_CRITIQUE_FINDING" for b in res.blocking_reasons)
    # The warning should be surfaced in the report.
    assert any("major/warning" in w for w in res.warnings)


def test_missing_required_phase_payload_blocks_freeze():
    pkg = _pkg_dict(validation_passed=True, scene_plan_scenes=False, dialogue_dialogues=_conversation_dialogue())
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief())
    assert res.freeze_allowed is False
    assert any(b["code"] == "SCENE_PLANNING_PAYLOAD_MISSING" for b in res.blocking_reasons)


def test_unresolved_creative_fallback_blocks_freeze():
    brief = _full_brief()
    brief["dialogues"] = [
        {"scene_number": 1, "lines": [{"speaker": "MARK", "text": "Sequence 5: I need to tell you something important.", "emotion": "steady"}]}
    ]
    pkg = _pkg_dict(validation_passed=True, dialogue_dialogues=[], ending="reconnect")
    res = evaluate_genesis_freeze_eligibility(pkg, brief)
    assert res.freeze_allowed is False
    assert any(b["code"] == "CREATIVE_FALLBACK_DETECTED" for b in res.blocking_reasons)


def test_defective_fixture_regression_rejected():
    """The known defective RUN-20260822-114418 must no longer freeze."""
    run_root = Path("productions/EP-0001/runs/RUN-20260822-114418/genesis")
    if not run_root.exists():
        pytest.skip("defective fixture not present")
    pkg = json.loads((run_root / "production_knowledge_package.json").read_text())
    brief = json.loads((run_root / "movie_os_brief.json").read_text())
    res = evaluate_genesis_freeze_eligibility(pkg, brief)
    assert res.freeze_allowed is False
    codes = {b["code"] for b in res.blocking_reasons}
    assert "GENESIS_VALIDATION_FAILED" in codes
    assert "STORY_ENDING_MISSING" in codes
    assert "SCENE_ORDER_INVALID" in codes


def test_freeze_from_brief_raises_on_ineligible_pkg():
    pkg = _pkg_dict(validation_passed=False, dialogue_dialogues=_conversation_dialogue())
    with pytest.raises(FreezeIneligibleError):
        freeze_from_brief(
            episode_id="EP-0001",
            policy_snapshot_id="POLICY-1",
            episode_contract_id="EP-0001",
            episode_contract_hash="c1",
            policy_snapshot_hash="p1",
            production={"episode_id": "EP-0001", "run_id": "RUN-1"},
            brief=_full_brief(),
            genesis_pkg=pkg,
        )


# ---------------------------------------------------------------------------
# P0-03 — Reconciliation & order
# ---------------------------------------------------------------------------

def test_required_beat_missing_from_all_scenes():
    reqs = story_requirements_from_contract()
    pkg = _pkg_dict(validation_passed=True, dialogue_dialogues=_conversation_dialogue(),
                    ending="reconnect")
    # scene_plan_scenes map only BEAT-001/006/008 -> others missing
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief())
    assert res.freeze_allowed is False
    assert any(b["code"] == "REQUIRED_STORY_BEAT_COVERAGE" for b in res.blocking_reasons)


def test_all_required_beats_mapped():
    # Give scenes that realize every requirement.
    scenes = []
    for n in range(1, 9):
        scenes.append({"scene_number": n, "act": "Act I", "narrative_beat": "x",
                       "realizes_requirements": [f"BEAT-{n:03d}"], "title": f"S{n}"})
    reqs = [{"id": f"BEAT-{n:03d}", "required": True} for n in range(1, 9)]
    rec = reconcile_requirements({"scene_planning": {"scenes": scenes}, "narrative_expansion": {"scenes": []}, "phase_results": []}, reqs)
    assert rec["passed"] is True
    assert rec["required_coverage"]["preserved"] == 8


def test_reversed_act_sequence():
    ok, reason = act_order_valid([
        {"act": "Act III"},
        {"act": "Act II"},
        {"act": "Act I"},
    ])
    assert ok is False


def test_valid_linear_act_sequence():
    ok, reason = act_order_valid([
        {"act": "Act I"},
        {"act": "Act II"},
        {"act": "Act III"},
    ])
    assert ok is True


def test_empty_required_ending_fails():
    pkg = _pkg_dict(validation_passed=True, dialogue_dialogues=_conversation_dialogue(), ending="")
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief(), resolution_requirement="REQUIRED")
    assert any(b["code"] == "STORY_ENDING_MISSING" for b in res.blocking_reasons)


def test_open_ended_contract_with_empty_resolution_passes_ending_check():
    pkg = _pkg_dict(validation_passed=True, dialogue_dialogues=_conversation_dialogue(), ending="")
    res = evaluate_genesis_freeze_eligibility(pkg, _full_brief(), resolution_requirement="OPEN_ENDED")
    assert not any(b["code"] == "STORY_ENDING_MISSING" for b in res.blocking_reasons)
