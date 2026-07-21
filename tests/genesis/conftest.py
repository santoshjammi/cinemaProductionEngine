"""Shared pytest fixtures for Genesis tests.

Provides:
- A rich MockLLMClient that returns valid JSON satisfying every agent's
  required fields, so all 30 agents can run end-to-end in tests.
- A real-but-disabled LLMClient for connectivity/parsing tests.
- A fresh in-memory ProductionKnowledgeGraph per test.
- A populated PKG containing all 19 PKP specs for review/gate tests.
"""

from __future__ import annotations

from typing import Any

import pytest

from movie_os.genesis.llm_client import MockLLMClient
from movie_os.genesis.mock_data import (
    DISCOVERY_RESPONSES,
    PKP_RESPONSES,
    REVIEWER_RESPONSES,
    build_rich_mock_llm,
)
from movie_os.genesis.models import (
    ConfidenceLevel,
    Specification,
)
from movie_os.genesis.pkg import ProductionKnowledgeGraph
from movie_os.genesis.session import SessionManager


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def rich_mock_llm() -> MockLLMClient:
    """Mock LLM with valid JSON responses for every agent."""
    return build_rich_mock_llm()


@pytest.fixture
def empty_mock_llm() -> MockLLMClient:
    """Mock LLM that always returns the default empty payload (empty content)."""
    return MockLLMClient()


@pytest.fixture
def failing_mock_llm():
    """Mock LLM that raises on every call (to test failure paths)."""

    class _FailingMock:
        def generate(self, prompt: str, system: str = "") -> str:
            raise RuntimeError("LLM unavailable (test)")

        def generate_json(self, prompt: str, system: str = "") -> dict[str, Any]:
            raise RuntimeError("LLM unavailable (test)")

    return _FailingMock()  # type: ignore[return-value]


@pytest.fixture
def pkg() -> ProductionKnowledgeGraph:
    """Fresh in-memory ProductionKnowledgeGraph."""
    return ProductionKnowledgeGraph(":memory:")


@pytest.fixture
def session_db_path(tmp_path):
    """Temporary file path for SessionManager tests."""
    return str(tmp_path / "test_sessions.db")


_SPEC_ID_TO_AGENT: dict[str, str] = {
    "PKP-00": "vision_agent",
    "PKP-01": "creative_strategy_agent",
    "PKP-02": "project_agent",
    "PKP-03": "research_agent",
    "PKP-04": "story_agent",
    "PKP-05": "world_agent",
    "PKP-06": "character_agent",
    "PKP-07": "relationship_agent",
    "PKP-08": "psychology_agent",
    "PKP-09": "narrative_agent",
    "PKP-10": "directorial_agent",
    "PKP-11": "production_design_agent",
    "PKP-12": "audio_intent_agent",
    "PKP-13": "editing_language_agent",
    "PKP-14": "animation_intent_agent",
    "PKP-15": "blueprint_agent",
    "PKP-16": "distribution_agent",
    "PKP-17": "quality_agent",
    "PKP-18": "knowledge_graph_agent",
}


@pytest.fixture
def populated_pkg() -> ProductionKnowledgeGraph:
    """PKG with all 19 PKP specs populated and validated.

    Useful for testing CompletionGate and Reviewer logic in isolation.
    """
    g = ProductionKnowledgeGraph(":memory:")
    g.synopsis = "A man withdraws from his wife after losing his job."
    g.constraints = {"runtime": "15min", "format": "short"}

    for i in range(19):
        spec_id = f"PKP-{i:02d}"
        agent_name = _SPEC_ID_TO_AGENT.get(spec_id, "")
        if agent_name and agent_name in PKP_RESPONSES:
            content = dict(PKP_RESPONSES[agent_name])
        else:
            content = {"placeholder_field": f"value_{i}", "confidence": "inferred"}

        g.set_specification(Specification(
            spec_id=spec_id,
            spec_name=f"Spec {i}",
            phase=(
                "A" if i < 3
                else "B" if i < 6
                else "C" if i < 9
                else "D" if i < 10
                else "E" if i < 15
                else "F" if i < 16
                else "G"
            ),
            content=content,
            confidence=ConfidenceLevel.CONFIRMED,
            dependencies=[],
            validation_status="passed",
            validation_errors=[],
        ))

    g.set_completeness("story", 1.0)
    g.set_completeness("character", 1.0)
    g.set_completeness("world", 1.0)

    # Add review results so the gate's reviews_completed check passes
    for key in ["story_review", "character_review", "narrative_review", "psychology_review"]:
        g.set_discovery_result(key, {"contradictions": [], "recommendations": [], "confidence": "confirmed"})

    g.save_state()
    return g
