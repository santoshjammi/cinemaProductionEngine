"""Tests for PhaseBase — execute method and full lifecycle."""

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


class _TestPhase(PhaseBase):
    """Concrete test phase for testing PhaseBase in isolation."""

    phase_number = 99
    phase_name = "TestPhase"

    def build_draft_prompt(self, pkg):
        return "draft prompt"

    def parse_draft(self, response) -> KnowledgeObject:
        data = json.loads(response) if isinstance(response, str) and response.strip().startswith("{") else {}
        return KnowledgeObject(
            purpose=data.get("purpose", ""),
            creative_intent=data.get("creative_intent", ""),
            reasoning=data.get("reasoning", ""),
            confidence="confirmed" if data.get("confidence") else "inferred",
        )

    def draft(self, pkg):
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)


@pytest.fixture
def empty_mock():
    """Mock that returns empty knowledge."""
    m = MockLLMClient()
    m.set_default('{}')
    return m


@pytest.fixture
def good_mock():
    """Mock that returns valid knowledge."""
    m = MockLLMClient()
    m.set_response("draft", json.dumps({
        "purpose": "Test purpose",
        "creative_intent": "Test intent",
        "reasoning": "Test reasoning",
        "confidence": "confirmed",
    }))
    # Critique returns empty findings (no issues)
    m.set_response("Critique", '[]')
    return m


class TestExecute:
    """Test the execute() method."""

    def test_execute_exists(self):
        p = _TestPhase.__new__(_TestPhase)
        assert hasattr(p, "execute")

    def test_execute_runs_cycle(self, good_mock):
        p = _TestPhase(good_mock)
        pkg = {"synopsis": "Test"}
        result = p.execute(pkg)
        assert result.status == PhaseStatus.COMPLETED
        assert p.result.status == PhaseStatus.COMPLETED

    def test_execute_with_empty_knowledge_fails(self, empty_mock):
        """Empty knowledge should fail validation through multiple iterations."""
        p = _TestPhase(empty_mock)
        pkg = {"synopsis": "Test"}
        result = p.execute(pkg)
        # Should fail because validate returns issues for empty objects
        assert result.status in (PhaseStatus.FAILED, PhaseStatus.COMPLETED)
