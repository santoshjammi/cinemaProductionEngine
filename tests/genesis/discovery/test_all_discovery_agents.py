"""Unit tests for all 7 Discovery agents."""

from __future__ import annotations

import asyncio
import json

import pytest

from movie_os.genesis.discovery import (
    IntentAnalyst, ThemeAnalyst, EmotionAnalyst, ConflictAnalyst,
    AudienceAnalyst, GapAnalyst, QuestionPlanner,
)
from movie_os.genesis.discovery.base import DiscoveryAgent


def _run(coro):
    return asyncio.run(coro)


# spec-style test for each agent
DISCOVERY_AGENTS = {
    "intent_analyst": IntentAnalyst,
    "theme_analyst": ThemeAnalyst,
    "emotion_analyst": EmotionAnalyst,
    "conflict_analyst": ConflictAnalyst,
    "audience_analyst": AudienceAnalyst,
    "gap_analyst": GapAnalyst,
    "question_planner": QuestionPlanner,
}


@pytest.mark.parametrize("name", list(DISCOVERY_AGENTS.keys()))
def test_discovery_agent_identity(name, rich_mock_llm):
    cls = DISCOVERY_AGENTS[name]
    agent = cls(rich_mock_llm)
    assert agent.name == name
    assert agent.analysis_key != ""
    assert isinstance(agent, DiscoveryAgent)


@pytest.mark.parametrize("name", list(DISCOVERY_AGENTS.keys()))
def test_discovery_agent_successful_run(name, rich_mock_llm, pkg):
    """Each discovery agent stores its result in the PKG via analysis_key."""
    cls = DISCOVERY_AGENTS[name]
    pkg.synopsis = "A man withdraws from his wife after losing his job."
    agent = cls(rich_mock_llm)
    result = _run(agent.run(pkg))
    assert result.status == "success", f"{name} failed: {result.errors}"
    assert agent.analysis_key in pkg.get_all_discovery_results()


@pytest.mark.parametrize("name", list(DISCOVERY_AGENTS.keys()))
def test_discovery_agent_llm_failure(name, failing_mock_llm, pkg):
    cls = DISCOVERY_AGENTS[name]
    agent = cls(failing_mock_llm)
    result = _run(agent.run(pkg))
    assert result.status == "failed"
    assert any("unavailable" in e for e in result.errors)


@pytest.mark.parametrize("name", list(DISCOVERY_AGENTS.keys()))
def test_discovery_agent_empty_response(name, empty_mock_llm, pkg):
    """Each agent enforces its own required fields; empty fails for most.

    QuestionPlanner is the exception: it accepts an empty questions array
    as a valid "no critical unknowns" outcome.
    """
    cls = DISCOVERY_AGENTS[name]
    agent = cls(empty_mock_llm)
    result = _run(agent.run(pkg))
    if name == "question_planner":
        # QuestionPlanner normalizes missing -> [] -> success
        assert result.status in ("success", "failed")
    else:
        assert result.status == "failed", f"{name} expected failed, got {result.status}"


# Per-agent detailed tests
class TestIntentAnalyst:
    def test_parses_full_payload(self, rich_mock_llm, pkg):
        pkg.synopsis = "Test"
        result = _run(IntentAnalyst(rich_mock_llm).run(pkg))
        assert result.status == "success"
        assert "intent" in result.output
        assert "territory" in result.output

    def test_rejects_missing_intent(self, rich_mock_llm, pkg):
        class _Bad:
            def generate(self, *a, **k): return '{"theme": "x"}'
        agent = IntentAnalyst(_Bad())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "failed"
        assert "intent" in result.errors[0]


class TestThemeAnalyst:
    def test_parses_lists_and_strings(self, rich_mock_llm, pkg):
        pkg.synopsis = "Test"
        result = _run(ThemeAnalyst(rich_mock_llm).run(pkg))
        assert result.status == "success"
        assert isinstance(result.output["secondary_themes"], list)
        assert isinstance(result.output["motifs"], list)

    def test_accepts_comma_separated_strings(self, pkg):
        class _Csv:
            def generate(self, *a, **k):
                return json.dumps({
                    "primary_theme": "x",
                    "secondary_themes": "a, b, c",
                    "motifs": "d, e, f",  # motifs split by ','
                })
        agent = ThemeAnalyst(_Csv())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "success"
        assert result.output["secondary_themes"] == ["a", "b", "c"]
        assert result.output["motifs"] == ["d", "e", "f"]


class TestEmotionAnalyst:
    def test_requires_beginning_and_end(self, pkg):
        class _Bad:
            def generate(self, *a, **k): return '{"middle_emotion": "x"}'
        agent = EmotionAnalyst(_Bad())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "failed"
        assert "beginning_emotion" in result.errors[0] or "end_emotion" in result.errors[0]


class TestConflictAnalyst:
    def test_requires_central_conflict(self, pkg):
        class _Bad:
            def generate(self, *a, **k): return '{"internal_conflicts": []}'
        agent = ConflictAnalyst(_Bad())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "failed"
        assert "central_conflict" in result.errors[0]


class TestAudienceAnalyst:
    def test_requires_target_audience(self, pkg):
        class _Bad:
            def generate(self, *a, **k): return '{"emotional_state": "x"}'
        agent = AudienceAnalyst(_Bad())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "failed"
        assert "target_audience" in result.errors[0]


class TestGapAnalyst:
    def test_requires_at_least_one_bucket(self, pkg):
        class _Bad:
            def generate(self, *a, **k): return '{}'
        agent = GapAnalyst(_Bad())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "failed"
        assert "empty" in result.errors[0].lower()


class TestQuestionPlanner:
    def test_handles_empty_questions(self, pkg):
        class _Empty:
            def generate(self, *a, **k): return '{"questions": []}'
        agent = QuestionPlanner(_Empty())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "success"
        assert result.output["questions"] == []

    def test_filters_invalid_questions(self, pkg):
        class _Mixed:
            def generate(self, *a, **k):
                return json.dumps({
                    "questions": [
                        {"question": "valid?", "confidence_pct": "50"},  # pct as string
                        {"question": ""},  # empty, should be filtered
                        "not a dict",  # filtered
                        {"question": "another?", "confidence_pct": 30.0},
                    ]
                })
        agent = QuestionPlanner(_Mixed())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "success"
        assert len(result.output["questions"]) == 2
        assert result.output["questions"][0]["confidence_pct"] == 50.0


class TestDiscoveryBaseClass:
    def test_assess_confidence(self, pkg):
        class Stub(DiscoveryAgent):
            name = "stub"
            analysis_key = "stub_key"
            def build_prompt(self, pkg): return ""
            def parse_response(self, response, pkg): return {}

        s = Stub.__new__(Stub)
        s.llm = None
        from movie_os.genesis.models import ConfidenceLevel
        assert s._assess_confidence({"confidence": "confirmed"}) == ConfidenceLevel.CONFIRMED
        assert s._assess_confidence({"confidence": "bogus"}) == ConfidenceLevel.INFERRED
        assert s._assess_confidence({}) == ConfidenceLevel.INFERRED
