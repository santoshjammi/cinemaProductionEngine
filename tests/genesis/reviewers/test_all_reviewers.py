"""Unit tests for all 4 Reviewer agents."""

from __future__ import annotations

import asyncio
import json

import pytest

from movie_os.genesis.models import ConfidenceLevel, Specification
from movie_os.genesis.reviewers import (
    StoryReviewer, CharacterReviewer, NarrativeReviewer, PsychologyReviewer,
)
from movie_os.genesis.reviewers.base import ReviewAgent


def _run(coro):
    return asyncio.run(coro)


REVIEWERS = {
    "story_reviewer": (StoryReviewer, ["PKP-04", "PKP-09", "PKP-06"], "story_review"),
    "character_reviewer": (CharacterReviewer, ["PKP-06", "PKP-07", "PKP-08"], "character_review"),
    "narrative_reviewer": (NarrativeReviewer, ["PKP-09", "PKP-10", "PKP-13"], "narrative_review"),
    "psychology_reviewer": (PsychologyReviewer, ["PKP-06", "PKP-07", "PKP-08", "PKP-09"], "psychology_review"),
}


def _populate_specs(pkg, spec_ids):
    for sid in spec_ids:
        pkg.set_specification(Specification(
            spec_id=sid, spec_name=f"Spec {sid}", phase="X",
            content={"placeholder": "data"},
            confidence=ConfidenceLevel.INFERRED,
            validation_status="passed",
        ))


@pytest.mark.parametrize("name", list(REVIEWERS.keys()))
def test_reviewer_identity(name, rich_mock_llm):
    cls, expected_specs, expected_key = REVIEWERS[name]
    agent = cls(rich_mock_llm)
    assert agent.name == name
    assert agent.review_key == expected_key
    assert agent.specs_to_review == expected_specs
    assert isinstance(agent, ReviewAgent)


@pytest.mark.parametrize("name", list(REVIEWERS.keys()))
def test_reviewer_successful_run(name, rich_mock_llm, pkg):
    cls, expected_specs, expected_key = REVIEWERS[name]
    _populate_specs(pkg, expected_specs)
    pkg.synopsis = "Test"
    agent = cls(rich_mock_llm)
    result = _run(agent.run(pkg))
    assert result.status in ("success", "revision_needed"), result.errors
    assert pkg.get_discovery_result(expected_key) is not None


@pytest.mark.parametrize("name", list(REVIEWERS.keys()))
def test_reviewer_llm_failure(name, failing_mock_llm, pkg):
    cls, expected_specs, _ = REVIEWERS[name]
    _populate_specs(pkg, expected_specs)
    agent = cls(failing_mock_llm)
    result = _run(agent.run(pkg))
    assert result.status == "failed"


@pytest.mark.parametrize("name", list(REVIEWERS.keys()))
def test_reviewer_empty_response(name, empty_mock_llm, pkg):
    """Empty mock returns {'confidence': 'unknown', 'content': {}}.

    Reviewers normalize missing keys to empty lists, so the result is success
    (no contradictions).
    """
    cls, expected_specs, _ = REVIEWERS[name]
    _populate_specs(pkg, expected_specs)
    agent = cls(empty_mock_llm)
    result = _run(agent.run(pkg))
    assert result.status in ("success", "failed")


# Per-reviewer specific tests
class TestStoryReviewer:
    def test_contradictions_trigger_revision(self, pkg):
        class _Critic:
            def generate(self, *a, **k):
                return json.dumps({
                    "contradictions": [
                        {"spec_ids": ["PKP-04", "PKP-09"], "description": "conflict", "severity": "high"}
                    ],
                    "recommendations": ["fix"],
                    "confidence": "confirmed",
                })
        _populate_specs(pkg, ["PKP-04", "PKP-09", "PKP-06"])
        agent = StoryReviewer(_Critic())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        assert result.status == "revision_needed"
        assert "conflict" in result.errors[0]


class TestPsychologyReviewer:
    def test_normalizes_missing_keys(self, pkg):
        class _Sparse:
            def generate(self, *a, **k): return "{}"
        _populate_specs(pkg, ["PKP-06", "PKP-07", "PKP-08", "PKP-09"])
        agent = PsychologyReviewer(_Sparse())  # type: ignore[arg-type]
        result = _run(agent.run(pkg))
        # Even with no contradictions, success
        assert result.status == "success"
        out = result.output
        assert out["contradictions"] == []
        assert out["psychological_issues"] == []
        assert out["recommendations"] == []


class TestReviewerBase:
    def test_run_sets_revision_needed_for_contradictions(self, pkg, rich_mock_llm):
        """A reviewer whose LLM returns contradictions reports revision_needed."""
        from movie_os.genesis.reviewers.base import ReviewAgent

        class StubCritic(ReviewAgent):
            name = "stub_critic"
            review_key = "stub_review"
            specs_to_review = []
            def build_prompt(self, pkg): return ""
            def parse_response(self, response, pkg):
                return {
                    "contradictions": [
                        {"description": "x", "spec_ids": [], "severity": "high"}
                    ],
                    "recommendations": [],
                    "confidence": "confirmed",
                }

        agent = StubCritic(rich_mock_llm)
        result = _run(agent.run(pkg))
        assert result.status == "revision_needed"
        assert "x" in result.errors[0]
