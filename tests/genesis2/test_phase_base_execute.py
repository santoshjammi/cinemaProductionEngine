"""Tests for PhaseBase.execute() — full Draft → Review → Critique → Improve → Validate → Freeze cycle."""

from __future__ import annotations

import json

import pytest

from movie_os.genesis2.phase_base import PhaseBase
from movie_os.genesis2.models import (
    KnowledgeObject,
    PhaseResult,
    PhaseStatus,
)
from movie_os.genesis2.llm_client import MockLLMClient


# ── Concrete test phase ─────────────────────────────────────────────────────

class _TestPhase(PhaseBase):
    """A concrete phase for testing the lifecycle."""

    phase_number = 99
    phase_name = "TestPhase"

    def draft(self, pkg: dict) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt, tier="planner")
        return self.parse_draft(response)

    def build_draft_prompt(self, pkg: dict) -> str:
        return "draft prompt"

    def parse_draft(self, response: str) -> KnowledgeObject:
        if isinstance(response, list):
            return KnowledgeObject(purpose="array", creative_intent="x", reasoning="y")
        data = json.loads(response) if (isinstance(response, str) and response.strip().startswith("{")) else {}
        return KnowledgeObject(
            purpose=data.get("purpose", ""),
            creative_intent=data.get("creative_intent", ""),
            reasoning=data.get("reasoning", ""),
            confidence="confirmed" if data.get("confidence") else "inferred",
        )

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:
        from movie_os.genesis2.models import ValidationIssue
        issues = []
        if not knowledge.purpose:
            issues.append(ValidationIssue(
                category="test_error",
                severity="error",
                location="TestPhase.purpose",
                description="purpose must not be empty"
            ))
        return issues


# ── Pytest fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def good_mock():
    """Mock returning valid structured data."""
    m = MockLLMClient()
    good_ko = json.dumps({
        "purpose": "Test purpose",
        "creative_intent": "Test intent",
        "reasoning": "Test reasoning",
    })
    empty_critique = "[]"
    m.set_default(good_ko)
    m.set_response("Critique the following TestPhase output", empty_critique)
    return m


@pytest.fixture
def bad_purpose_mock():
    """Mock returning missing purpose — will cause review failure + improve."""
    m = MockLLMClient()
    bad_ko = json.dumps({
        "creative_intent": "present",
        "reasoning": "present",
    })  # no 'purpose'
    good_fix = json.dumps({
        "purpose": "fixed",
        "creative_intent": "fixed",
        "reasoning": "fixed",
    })
    m.set_default(bad_ko)
    m.set_response("Improve the following TestPhase output based on critique", good_fix)
    m.set_response("Is this emotionally believable?", json.dumps([{"question": "Missing purpose", "answer": "needs purpose", "severity": "critical", "recommendation": "Add purpose"}]))
    return m


@pytest.fixture
def empty_ko_mock():
    """Returns an entirely empty KnowledgeObject."""
    m = MockLLMClient()
    m.set_default(json.dumps({}))

    def loop(prompt, tier="planner"):
        if "Improve" in prompt:
            return json.dumps({})
        return "{}"

    m.generate = loop
    return m


# ── Tests for the execute() method ──────────────────────────────────────────

class TestExecute:
    """Test execute(): sync wrapper around run()."""

    def test_execute_method_exists(self):
        p = _TestPhase.__new__(_TestPhase)
        assert hasattr(p, "execute")

    def test_execute_returns_phase_result(self, good_mock):
        p = _TestPhase(good_mock)
        result = p.execute({})
        assert isinstance(result, PhaseResult)

    def test_execute_completes_successfully(self, good_mock):
        """Happy path: all phases of the cycle succeed."""
        p = _TestPhase(good_mock)
        result = p.execute({})
        assert result.status == PhaseStatus.COMPLETED

    def test_execute_tracks_draft_count(self, good_mock):
        p = _TestPhase(good_mock)
        result = p.execute({})
        assert result.draft_count >= 1

    def test_execute_sets_status_throughout(self, good_mock):
        p = _TestPhase(good_mock)
        result = p.execute({})
        # After execution the final status should be COMPLETED
        assert result.status == PhaseStatus.COMPLETED


class TestExecuteWithReviewFailure:
    """Test execute() when review finds issues → improve loop kicks in."""

    def test_improve_fires_on_review_issues(self, bad_purpose_mock):
        m = bad_purpose_mock
        p = _TestPhase(m)
        result = p.execute({})
        # The improve cycle should attempt to fix issues
        assert result.status in (PhaseStatus.COMPLETED, PhaseStatus.FAILED)
        assert result.draft_count >= 1

    def test_improve_max_iterations_capped(self, empty_ko_mock):
        """If improve keeps producing bad results it should stop after max_iterations."""
        m = empty_ko_mock
        p = _TestPhase(m)
        # max_iterations defaults to 3
        result = p.execute({})
        # Will fail because nothing passes validation
        assert result.status == PhaseStatus.FAILED


class TestExecuteWithValidateFailure:
    """Test execute() when validate fails."""

    def test_failed_after_exhausted_iterations(self, empty_ko_mock):
        m = empty_ko_mock
        p = _TestPhase(m)
        result = p.execute({})
        assert result.status == PhaseStatus.FAILED


# ── Tests for run() (async base method) ─────────────────────────────────────

class TestRun:
    """Test the async run(): same lifecycle as execute()."""

    def test_run_completes(self, good_mock):
        import asyncio
        p = _TestPhase(good_mock)
        result = asyncio.run(p.run({}))
        assert result.status == PhaseStatus.COMPLETED

    def test_result_has_knowledge(self, good_mock):
        import asyncio
        p = _TestPhase(good_mock)
        result = asyncio.run(p.run({}))
        assert result.knowledge is not None


# ── Tests for freeze() ──────────────────────────────────────────────────────

class TestFreeze:
    def test_freeze_sets_metadata(self):
        p = _TestPhase.__new__(_TestPhase)
        p.llm = MockLLMClient()
        p.result = PhaseResult(phase_number=99, phase_name="Test")
        p.result.draft_count = 2
        ko = KnowledgeObject(purpose="x", creative_intent="y", reasoning="z")
        ko = p.freeze(ko)
        assert "frozen_at" in ko.metadata
        assert ko.metadata["phase"] == "TestPhase"
        assert ko.metadata["draft_count"] == 2


# ── Tests for build_critique_prompt() ───────────────────────────────────────

class TestCritiquePrompt:
    def test_contains_knowledge_json(self):
        p = _TestPhase.__new__(_TestPhase)
        p.llm = MockLLMClient()
        ko = KnowledgeObject(purpose="test", creative_intent="test", reasoning="test")
        prompt = p.build_critique_prompt(ko)
        assert "test" in prompt

    def test_contains_phase_name(self):
        p = _TestPhase.__new__(_TestPhase)
        p.llm = MockLLMClient()
        ko = KnowledgeObject(purpose="test", creative_intent="test", reasoning="test")
        prompt = p.build_critique_prompt(ko)
        assert "TestPhase" in prompt


# ── Tests for _get_human_questions ──────────────────────────────────────────

class TestHumanQuestions:
    def test_empty_for_non_critical_findings(self):
        from movie_os.genesis2.models import CritiqueFinding
        p = _TestPhase.__new__(_TestPhase)
        p.llm = MockLLMClient()
        findings = [CritiqueFinding(severity="minor", recommendation="")]
        q = p._get_human_questions(findings)
        assert q == []

    def test_critical_with_recommendation_yields_question(self):
        from movie_os.genesis2.models import CritiqueFinding
        p = _TestPhase.__new__(_TestPhase)
        p.llm = MockLLMClient()
        findings = [CritiqueFinding(
            question="Key issue?",
            answer="because X",
            severity="critical",
            recommendation="Fix by Y",
        )]
        q = p._get_human_questions(findings)
        assert len(q) == 1
        assert "Key issue?" in q[0]["question"]


# ── Tests for critique() with MockLLM failure ───────────────────────────────

class TestCritiqueRobustness:
    def test_critique_returns_empty_on_parse_failure(self):
        p = _TestPhase.__new__(_TestPhase)
        bad_llm = MockLLMClient()
        bad_llm.set_default("not valid json {{{")

        # We need to also patch the LLM client that's actually used by critique
        class BadCritiquePhase(PhaseBase):
            phase_number = 98
            phase_name = "BadCritique"
            def draft(self, pkg): return KnowledgeObject()
            def build_draft_prompt(self, pkg): return ""
            def parse_draft(self, response):
                return KnowledgeObject(purpose="test", creative_intent="test", reasoning="test")

        p = BadCritiquePhase(bad_llm)
        ko = KnowledgeObject(purpose="test", creative_intent="test", reasoning="test")
        result = p.critique(ko)  # should not raise
        assert result == []
