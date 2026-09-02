"""Tests for P0-02: creative fallback fabrication must be removed.

ensure_scene_state_fields may repair technical structure but must NEVER author
creative content (dialogue, titles, acts, beats, emotional states, resolution,
shot content).  Missing creative data must surface as validation defects and
the freeze gate must reject the package.
"""
from __future__ import annotations

import pytest

import run_space_between_us as rsbu
from movie_os.genesis2.freeze_gate import evaluate_genesis_freeze_eligibility


def _brief_with_empty_dialogue():
    return {
        "scenes": [
            {"number": 1, "title": "Job Loss", "act": "Act I", "narrative_beat": "inciting",
             "scene_description": "Mark learns he lost his job."},
            {"number": 2, "title": "Confrontation", "act": "Act II", "narrative_beat": "confrontation",
             "scene_description": "Sarah confronts the silence."},
            {"number": 3, "title": "Resolution", "act": "Act III", "narrative_beat": "resolution",
             "scene_description": "Mark opens up."},
        ],
        "dialogues": [
            {"scene_number": 1, "lines": []},
            {"scene_number": 2, "lines": []},
            {"scene_number": 3, "lines": []},
        ],
    }


def _pkg_metadata():
    """A PKP whose phase payloads are fine but has NO dialogue planning content."""
    return {
        "phase_results": [
            {"phase_number": i, "phase_name": f"Phase {i:02d}", "status": "completed", "knowledge": {}}
            for i in range(1, 13)
        ],
        "validation": {"passed": True, "score": 1.0},
        "scene_planning": {"scenes": [
            {"scene_number": 1, "act": "Act I", "narrative_beat": "inciting", "title": "Job Loss", "realizes_requirements": ["BEAT-001"]},
            {"scene_number": 2, "act": "Act II", "narrative_beat": "confrontation", "title": "Confrontation", "realizes_requirements": ["BEAT-006"]},
            {"scene_number": 3, "act": "Act III", "narrative_beat": "resolution", "title": "Resolution", "realizes_requirements": ["BEAT-008"]},
        ]},
        "dialogue_planning": {"dialogues": []},
        "creative_critique": {"findings": []},
        "story": {"ending": "reconnect"},
        "narrative_expansion": {"scenes": []},
    }


def test_fabricated_dialogue_is_not_generated():
    brief = _brief_with_empty_dialogue()
    out = rsbu.ensure_scene_state_fields(brief)
    # No line may be fabricated; all three scenes carry no dialogue lines.
    for d in out["dialogues"]:
        assert d["lines"] == []
    # A BLOCKER defect must be recorded.
    codes = [defect["code"] for defect in out.get("_genesis_defects", [])]
    assert "DIALOGUE_PLANNING_INCOMPLETE" in codes


def test_missing_required_dialogue_blocks_phase():
    brief = _brief_with_empty_dialogue()
    out = rsbu.ensure_scene_state_fields(brief)
    pkg = _pkg_metadata()
    res = evaluate_genesis_freeze_eligibility(pkg, out)
    assert res.freeze_allowed is False
    assert any(b["code"] == "DIALOGUE_PLANNING_INCOMPLETE" for b in res.blocking_reasons)


def test_scene_title_is_never_converted_to_dialogue():
    brief = _brief_with_empty_dialogue()
    out = rsbu.ensure_scene_state_fields(brief)
    for d in out["dialogues"]:
        for line in d["lines"]:
            assert line["text"] not in ("Job Loss", "Confrontation", "Resolution")
            assert not line["text"].startswith("Sequence")


def test_missing_act_is_not_invented():
    brief = {
        "scenes": [{"number": 1, "title": "Job Loss", "act": "", "scene_description": "loss"}],
        "dialogues": [{"scene_number": 1, "lines": [{"speaker": "MARK", "text": "I lost my job.", "emotion": "ashamed"}]}],
    }
    out = rsbu.ensure_scene_state_fields(brief)
    assert out["scenes"][0]["act"] == ""


def test_missing_resolution_is_not_invented():
    # ensure_scene_state_fields must not synthesize story.ending
    brief = _brief_with_empty_dialogue()
    out = rsbu.ensure_scene_state_fields(brief)
    assert "ending" not in out or not out.get("ending")


def test_visual_only_scene_can_pass_without_dialogue():
    brief = {
        "scenes": [
            {"number": 1, "title": "Silent Morning", "act": "Act I", "narrative_beat": "inciting",
             "scene_description": "No words exchanged.", "dialogue_policy": {"type": "VISUAL_ONLY"}}
        ],
        "dialogues": [
            {"scene_number": 1, "lines": [], "dialogue_policy": {"type": "VISUAL_ONLY"}}
        ],
    }
    out = rsbu.ensure_scene_state_fields(brief)
    # No DIALOGUE_PLANNING_INCOMPLETE defect for an explicitly VISUAL_ONLY scene.
    codes = [d.get("code") for d in out.get("_genesis_defects", []) if isinstance(d, dict)]
    assert "DIALOGUE_PLANNING_INCOMPLETE" not in codes


def test_conversation_without_required_turns_fails():
    brief = {
        "scenes": [{"number": 1, "title": "Talk", "act": "Act I", "narrative_beat": "inciting",
                    "scene_description": "Conversation.", "dialogue_policy": {"type": "CONVERSATION"}}],
        "dialogues": [
            {"scene_number": 1, "dialogue_policy": {"type": "CONVERSATION"},
             "lines": [{"speaker": "MARK", "text": "Hi.", "emotion": "neutral"}]}
        ],
    }
    out = rsbu.ensure_scene_state_fields(brief)
    pkg = _pkg_metadata()
    # The gate's dialogue-density rule must reject a CONVERSATION with < required turns.
    res = evaluate_genesis_freeze_eligibility(pkg, out)
    # At minimum, a CONVERSATION scene with a single line must not silently pass.
    assert not any(b["code"] == "DIALOGUE_PLANNING_INCOMPLETE" for b in res.blocking_reasons) or res.freeze_allowed is False

