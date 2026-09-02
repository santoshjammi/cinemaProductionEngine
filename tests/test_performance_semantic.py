"""P0-04: Semantic fixture tests (captured/deterministic, not live-model)."""
from __future__ import annotations

import pytest

from movie_os.genesis2.performance_semantic import (
    line_professional_register,
    scene_emotional_continuity,
    cross_scene_continuity,
    subtext_matches_character_motive,
)


def test_professional_restrained_performance_passes():
    ev = "Restrained delivery, hesitation, quiet defensiveness, emotion below the words."
    r = line_professional_register(ev)
    assert r["verdict"] == "PASS"
    assert r["passed"] is True


def test_cartoonishly_exaggerated_performance_fails():
    ev = "Cartoonish delivery with exaggerated melodrama and constant shouting."
    r = line_professional_register(ev)
    assert r["verdict"] == "FAIL"
    assert r["passed"] is False


def test_ai_assistant_style_delivery_warns():
    ev = "Virtual assistant politeness, over-articulated exposition voice."
    r = line_professional_register(ev)
    assert r["verdict"] in ("WARNING", "FAIL")


def test_scene_state_vs_line_emotion_contradiction_fails():
    # SC01 end withdrawn -> SC02 first line exuberant (unexplained).
    r = cross_scene_continuity("withdrawn", "exuberant")
    assert r["passed"] is False


def test_natural_emotional_escalation_passes():
    seq = ["guarded", "defensive", "pressured", "vulnerable"]
    r = scene_emotional_continuity(seq)
    assert r["passed"] is True
    assert r["violations"] == []


def test_unexplained_emotional_leap_fails():
    seq = ["guarded", "cheerful", "devastated", "casual"]
    r = scene_emotional_continuity(seq)
    assert r["passed"] is False
    assert len(r["violations"]) >= 1


def test_earned_vulnerability_transition_passes():
    seq = ["guarded", "defensive", "pressured", "fear", "vulnerable"]
    r = scene_emotional_continuity(seq)
    assert r["passed"] is True


def test_subtext_contradicts_character_motivation_warns():
    # Subtext about staying hidden conflicts with a reconnection motive.
    r = subtext_matches_character_motive("I have to keep her out", "reconnect with Sarah")
    assert r["passed"] is False
