"""P0-04: deterministic performance-preservation tests.

Every authoritative spoken line must carry a complete, provider-independent
acting/performance contract through Dialogue -> Bridge -> PKP -> Serialization.
Orphan dialogue (for non-final scenes) must be resolved away and never reach the
PKP.  Existing authored performance is preserved, never regenerated.
"""
from __future__ import annotations

import json

import pytest

from movie_os.genesis2.performance_model import (
    resolve_voice_binding,
    resolve_authoritative_dialogue,
    dialogue_authority_reconciliation,
    VOICE_PROFILES,
)
from movie_os.genesis2.performance_eval import (
    normalize_performance_fields,
    performance_coverage,
    voice_binding_coverage,
    MANDATORY_PERF_FIELDS,
)
from movie_os.genesis2.freeze_gate import evaluate_genesis_freeze_eligibility


# ---------------------------------------------------------------------------
# Voice binding
# ---------------------------------------------------------------------------

def test_mark_voice_binding():
    b = resolve_voice_binding("MARK")
    assert b["character_voice_id"] == "MSVR-MARK"
    assert b["presentation_mode"] == "EXTERNAL"


def test_inner_voice_uses_same_character_identity():
    # MARK_INNER must resolve to MSVR-MARK (not a third generic actor).
    b = resolve_voice_binding("MARK_INNER")
    assert b["character_voice_id"] == "MSVR-MARK"
    assert b["presentation_mode"] == "INTERNAL"


def test_sarah_voice_binding():
    b = resolve_voice_binding("SARAH")
    assert b["character_voice_id"] == "MSVR-SARAH"


# ---------------------------------------------------------------------------
# Authoritative dialogue resolution (orphan exclusion)
# ---------------------------------------------------------------------------

def _plans_with_scenes(scene_nums):
    from movie_os.genesis2.models import DialoguePlan, DialogueLine
    return [DialoguePlan(scene_number=n, lines=[
        DialogueLine(speaker="MARK", text=f"line {i}", delivery_intent="x", emotion="calm")
        for i in range(2)
    ]) for n in scene_nums]


def test_authoritative_dialogue_denominator_excludes_orphans():
    plans = _plans_with_scenes([1, 2, 3, 4, 5, 6, 7])
    rec = dialogue_authority_reconciliation(plans, [1, 2, 3, 4, 5])
    assert rec["authoritative_dialogue_objects"] == 5
    assert rec["authoritative_lines"] == 10
    assert rec["orphan_dialogue_objects"] == 2
    assert rec["orphan_scene_ids"] == [6, 7]


def test_orphan_dialogue_never_reaches_pkp():
    plans = _plans_with_scenes([1, 2, 3, 4, 5, 6, 7])
    ad = resolve_authoritative_dialogue(plans, [1, 2, 3, 4, 5])
    # Only authoritative plans flow downstream.
    assert all(int(p["scene_number"]) in {1, 2, 3, 4, 5} for p in ad.authoritative_plans)
    # Orphans are separated, never in authoritative set.
    assert all(int(p["scene_number"]) in {6, 7} for p in ad.orphan_plans)


# ---------------------------------------------------------------------------
# Mandatory performance coverage
# ---------------------------------------------------------------------------

def _perf_line(**overrides):
    base = {
        "line_id": "SC01-L001", "speaker": "MARK", "text": "I'm fine.",
        "emotional_state_primary": "guarded", "delivery_intent": "defensive",
        "subtext": "don't push", "character_voice_id": "MSVR-MARK",
        "presentation_mode": "EXTERNAL",
    }
    base.update(overrides)
    return base


def test_line_without_emotional_state_blocks():
    ln = _perf_line(emotional_state_primary="")
    cov = performance_coverage([ln])
    assert cov["passed"] is False
    assert "emotional_state_primary" in cov["incomplete_records"][0]["missing"]


def test_line_without_delivery_intent_blocks():
    ln = _perf_line(delivery_intent="")
    cov = performance_coverage([ln])
    assert cov["passed"] is False


def test_line_without_required_subtext_blocks():
    ln = _perf_line(subtext="")
    cov = performance_coverage([ln])
    assert cov["passed"] is False


def test_line_without_voice_binding_blocks():
    ln = _perf_line(character_voice_id="")
    cov = performance_coverage([ln])
    assert cov["passed"] is False


def test_complete_line_passes():
    cov = performance_coverage([_perf_line()])
    assert cov["passed"] is True
    assert cov["percentage"] == 100.0


def test_generic_neutral_fallback_not_inserted():
    # A source line with NO emotion must NOT be auto-filled with 'neutral'.
    ln = {"line_id": "S1", "speaker": "MARK", "text": "hi", "delivery_intent": "quiet"}
    n = normalize_performance_fields(ln)
    # normalize fills emotional_state_primary from emotion only if present.
    # Since neither emotion nor emotional_state is present, it stays empty
    # (the coverage gate will flag it) rather than fabricating 'neutral'.
    assert n.get("emotional_state_primary", "") == ""
    assert "neutral" != n.get("emotional_state_primary", "")


# ---------------------------------------------------------------------------
# Source preservation — compiler does not replace valid performance
# ---------------------------------------------------------------------------

def test_valid_source_delivery_intent_survives_normalization():
    src = {"speaker": "SARAH", "text": "How long?", "delivery_intent": "quiet but direct",
           "emotion": "controlled hurt"}
    n = normalize_performance_fields(src)
    assert n["delivery_intent"] == "quiet but direct"


def test_valid_source_emotion_survives_normalization():
    src = {"speaker": "MARK", "text": "I'm empty.", "emotion": "shame"}
    n = normalize_performance_fields(src)
    assert n["emotional_state_primary"] == "shame"


def test_valid_source_subtext_survives_compilation():
    src = {"speaker": "MARK", "text": "I'm just tired.", "subtext": "I can't tell you I lost my job"}
    n = normalize_performance_fields(src)
    assert n["subtext"] == "I can't tell you I lost my job"


def test_compiler_does_not_replace_existing_performance():
    # A line with valid delivery_intent + subtext keeps both; nothing overwrites.
    src = {"speaker": "MARK", "text": "x", "emotion": "guarded",
           "delivery_intent": "quiet defensiveness", "subtext": "stay hidden"}
    n = normalize_performance_fields(src)
    assert n["delivery_intent"] == "quiet defensiveness"
    assert n["subtext"] == "stay hidden"
    assert n["emotional_state_primary"] == "guarded"


# ---------------------------------------------------------------------------
# Voice binding coverage
# ---------------------------------------------------------------------------

def test_voice_binding_coverage_100_percent():
    lines = [_perf_line(speaker="MARK", character_voice_id="MSVR-MARK"),
             _perf_line(line_id="S2", speaker="SARAH", character_voice_id="MSVR-SARAH")]
    vb = voice_binding_coverage(lines)
    assert vb["passed"] is True
    assert vb["coverage"] == 100.0


def test_voice_binding_wrong_character_flags():
    # MARK line bound to SARAH voice is a wrong binding.
    ln = _perf_line(speaker="MARK", character_voice_id="MSVR-SARAH")
    vb = voice_binding_coverage([ln])
    assert vb["passed"] is False
    assert len(vb["wrong_character_bindings"]) == 1


# ---------------------------------------------------------------------------
# Freeze-gate integration: performance blocker
# ---------------------------------------------------------------------------

def test_performance_loss_blocks_freeze():
    pkg = _minimal_pkg()
    brief = {
        "scenes": [{"scene_number": 1, "title": "A", "realizes_requirements": ["REQ-001"]}],
        "canonical_requirements": [{"id": "REQ-001", "obligation": "MUST"}],
        "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"},
        "ending": "They reconnect.",
        "dialogues": [{"scene_number": 1, "lines": [_perf_line(emotional_state_primary="")]}],
    }
    from movie_os.genesis2.freeze_gate import evaluate_genesis_freeze_eligibility
    res = evaluate_genesis_freeze_eligibility(pkg, brief)
    assert res.freeze_allowed is False
    assert any(b["code"] == "LINE_PERFORMANCE_INCOMPLETE" for b in res.blocking_reasons)


def test_complete_performance_does_not_block_freeze():
    pkg = _minimal_pkg()
    brief = {
        "scenes": [{"scene_number": 1, "title": "A", "realizes_requirements": ["REQ-001"]}],
        "canonical_requirements": [{"id": "REQ-001", "obligation": "MUST"}],
        "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"},
        "ending": "They reconnect.",
        "dialogues": [{"scene_number": 1, "lines": [_perf_line()]}],
    }
    from movie_os.genesis2.freeze_gate import evaluate_genesis_freeze_eligibility
    res = evaluate_genesis_freeze_eligibility(pkg, brief)
    assert not any(b["code"] == "LINE_PERFORMANCE_INCOMPLETE" for b in res.blocking_reasons)


def _minimal_pkg():
    from movie_os.genesis2.models import ProductionKnowledgePackage, PhaseResult
    pkg = ProductionKnowledgePackage(episode_id="EP-0001", run_id="r")
    for i in range(1, 13):
        pkg.phase_results.append(PhaseResult(phase_number=i, phase_name=f"P{i}"))
    return pkg
