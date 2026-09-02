"""Tests for Phase 01: Creative Understanding — full lifecycle."""

from __future__ import annotations

import json

import pytest

from movie_os.genesis2.phases.phase01_creative_understanding import (
    CreativeUnderstandingPhase,
)
from movie_os.genesis2.models import (
    KnowledgeObject,
    PhaseResult,
    PhaseStatus,
)
from movie_os.genesis2.llm_client import MockLLMClient


def _build_mock() -> MockLLMClient:
    """Build a MockLLMClient for testing."""
    return MockLLMClient()


class TestPhase01Draft:
    """Tests for phase 01 draft functionality and review logic."""

    def test_draft_exists(self):
        m = _build_mock()
        p = CreativeUnderstandingPhase(m)
        assert hasattr(p, "draft")

    def test_review_finds_missing_fields(self):
        """A minimal KnowledgeObject with only base fields should fail phase-specific review."""
        p = CreativeUnderstandingPhase.__new__(CreativeUnderstandingPhase)
        p.llm = _build_mock()

        # Only base fields — missing genre, theme, etc.
        ko = KnowledgeObject(purpose="x", creative_intent="y", reasoning="z")
        issues = p.review(ko)
        assert len(issues) > 0
        # Should find missing phase-specific required fields
        assert any("theme" in i or "genre" in i or "mood" in i for i in issues)

    def test_review_passes_with_full_fields(self):
        from movie_os.genesis2.models import CreativeUnderstanding

        ko = CreativeUnderstanding(
            purpose="understand the story",
            creative_intent="emotional truth",
            reasoning="from synopsis analysis",
            theme="loss of connection",
            genre="Drama",
            mood="melancholic",
            core_question="Can silence speak?",
            audience="adults",
            success_criteria=["truthfulness", "coherence"],
            confidence="confirmed",
        )
        p = CreativeUnderstandingPhase.__new__(CreativeUnderstandingPhase)
        p.llm = _build_mock()
        issues = p.review(ko)
        assert issues == []

    def test_phase_review_has_more_issues_than_base(self):
        """Phase review should catch more than the generic base review."""
        from movie_os.genesis2.models import CreativeUnderstanding, ConfidenceLevel

        # This would pass base review (has purpose/creative_intent/reasoning) but miss phase fields
        ko = KnowledgeObject(purpose="x", creative_intent="y", reasoning="z")
        p = CreativeUnderstandingPhase.__new__(CreativeUnderstandingPhase)
        p.llm = _build_mock()

        base_issues = []  # what PhaseBase.review returns on this KO
        phase_issues = p.review(ko)
        assert len(phase_issues) > len(base_issues)


class TestPhase01Validate:
    """Tests for phase 01 validation logic."""

    def test_validate_finds_missing_theme(self):
        from movie_os.genesis2.models import CreativeUnderstanding

        ko = KnowledgeObject(purpose="x", creative_intent="y", reasoning="z")
        p = CreativeUnderstandingPhase.__new__(CreativeUnderstandingPhase)
        p.llm = _build_mock()
        issues = p.validate(ko)
        theme_issues = [i for i in issues if "theme" in i.description.lower()]
        assert len(theme_issues) > 0

    def test_validate_passes_with_all_required(self):
        from movie_os.genesis2.models import CreativeUnderstanding

        ko = CreativeUnderstanding(
            purpose="understand story",
            creative_intent="emotional truth",
            reasoning="from synopsis",
            theme="test theme",
            genre="Drama",
            mood="melancholic",
            core_question="What matters?",
            success_criteria=["criterion1"],
        )
        p = CreativeUnderstandingPhase.__new__(CreativeUnderstandingPhase)
        p.llm = _build_mock()
        issues = p.validate(ko)
        # With all required fields present, should pass (no issues)
        assert len(issues) == 0


class TestPhase01HappyPath:
    """Test full happy path flow."""

    def test_full_execute_with_good_mock(self):
        m = _build_mock()
        m.set_default(json.dumps({
            "purpose": "understand the story",
            "creative_intent": "emotional truth",
            "reasoning": "from synopsis",
            "theme": "loss of connection",
            "genre": "Drama",
            "mood": "melancholic",
            "core_question": "What matters?",
            "audience": "adults",
            "success_criteria": ["truthfulness"],
            "confidence": "confirmed",
        }))
        p = CreativeUnderstandingPhase(m)
        result = p.execute({"synopsis": "A man withdraws."})
        assert result.status == PhaseStatus.COMPLETED
