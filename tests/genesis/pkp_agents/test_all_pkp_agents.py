"""Unit tests for all 19 PKP agents + ChiefArchitect.

Each test class verifies:
- The agent's identity (name, spec_id, phase, dependencies).
- A successful run with valid mock JSON produces a stored spec.
- A missing dependency is skipped.
- An LLM failure is reported, not crashed.
- The validate() method catches missing required fields.
- The assess_confidence() method reads the 'confidence' field if present.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Type

import pytest

from movie_os.genesis.models import ConfidenceLevel, Specification
from movie_os.genesis.pkg import ProductionKnowledgeGraph
from movie_os.genesis.pkp_agents import (
    VisionAgent, CreativeStrategyAgent, ProjectAgent,
    ResearchAgent, StoryAgent, WorldAgent,
    CharacterAgent, RelationshipAgent, PsychologyAgent,
    NarrativeAgent, DirectorialAgent, ProductionDesignAgent,
    AudioIntentAgent, EditingLanguageAgent, AnimationIntentAgent,
    BlueprintAgent, DistributionAgent, QualityAgent,
    KnowledgeGraphAgent,
)
from movie_os.genesis.chief_architect import ChiefArchitect


def _run(coro):
    """Helper to run an async coroutine in a sync test."""
    return asyncio.run(coro)


# Registry: spec_id -> (agent class, phase, dependencies, mock_key)
PKP_AGENTS = {
    "PKP-00": (VisionAgent,             "A", [],                                                  "vision_agent"),
    "PKP-01": (CreativeStrategyAgent,   "A", ["PKP-00"],                                          "creative_strategy_agent"),
    "PKP-02": (ProjectAgent,            "A", ["PKP-00", "PKP-01"],                                "project_agent"),
    "PKP-03": (ResearchAgent,           "B", ["PKP-02"],                                          "research_agent"),
    "PKP-04": (StoryAgent,              "B", ["PKP-03"],                                          "story_agent"),
    "PKP-05": (WorldAgent,              "B", ["PKP-04"],                                          "world_agent"),
    "PKP-06": (CharacterAgent,          "C", ["PKP-04", "PKP-05"],                                "character_agent"),
    "PKP-07": (RelationshipAgent,       "C", ["PKP-06"],                                          "relationship_agent"),
    "PKP-08": (PsychologyAgent,         "C", ["PKP-06", "PKP-07"],                                "psychology_agent"),
    "PKP-09": (NarrativeAgent,          "D", ["PKP-04", "PKP-08"],                                "narrative_agent"),
    "PKP-10": (DirectorialAgent,        "E", ["PKP-09"],                                          "directorial_agent"),
    "PKP-11": (ProductionDesignAgent,   "E", ["PKP-05"],                                          "production_design_agent"),
    "PKP-12": (AudioIntentAgent,        "E", ["PKP-09"],                                          "audio_intent_agent"),
    "PKP-13": (EditingLanguageAgent,    "E", ["PKP-09"],                                          "editing_language_agent"),
    "PKP-14": (AnimationIntentAgent,    "E", ["PKP-10"],                                          "animation_intent_agent"),
    "PKP-15": (BlueprintAgent,          "F", ["PKP-09", "PKP-10", "PKP-11", "PKP-12", "PKP-13", "PKP-14"], "blueprint_agent"),
    "PKP-16": (DistributionAgent,       "G", ["PKP-02"],                                          "distribution_agent"),
    "PKP-17": (QualityAgent,            "G", ["PKP-09", "PKP-10", "PKP-06"],                      "quality_agent"),
    "PKP-18": (KnowledgeGraphAgent,     "G", [],                                                  "knowledge_graph_agent"),
}

SPEC_IDS = list(PKP_AGENTS.keys())


def _ensure_dependencies(pkg: ProductionKnowledgeGraph, deps: list[str]) -> None:
    """Insert minimal satisfied dependency specs."""
    for dep in deps:
        if not pkg.has_specification(dep):
            pkg.set_specification(Specification(
                spec_id=dep, spec_name=f"Stub {dep}", phase="X",
                confidence=ConfidenceLevel.INFERRED,
                validation_status="passed",
            ))


@pytest.mark.parametrize("spec_id", SPEC_IDS)
def test_pkp_agent_identity(spec_id, rich_mock_llm):
    """Every PKP agent has the right identity metadata."""
    agent_class, phase, deps, key = PKP_AGENTS[spec_id]
    agent = agent_class(rich_mock_llm)
    assert agent.spec_id == spec_id
    assert agent.phase == phase
    assert agent.dependencies == deps
    assert agent.name == key


@pytest.mark.parametrize("spec_id", SPEC_IDS)
def test_pkp_agent_successful_run(spec_id, rich_mock_llm, pkg):
    """With valid mock JSON, the agent writes a spec to the PKG."""
    agent_class, _, deps, _ = PKP_AGENTS[spec_id]
    pkg.synopsis = "A man withdraws from his wife after losing his job."
    _ensure_dependencies(pkg, deps)

    agent = agent_class(rich_mock_llm)
    result = _run(agent.run(pkg))

    assert result.status in ("success", "revision_needed"), (
        f"{spec_id} failed: {result.errors}"
    )
    assert pkg.has_specification(spec_id)
    spec = pkg.get_specification(spec_id)
    assert spec.spec_id == spec_id
    assert isinstance(spec.content, dict)
    assert len(spec.content) > 0


@pytest.mark.parametrize("spec_id", SPEC_IDS)
def test_pkp_agent_missing_dependency_skipped(spec_id, rich_mock_llm, pkg):
    """If a required dep is missing, the agent returns 'skipped'."""
    agent_class, _, deps, _ = PKP_AGENTS[spec_id]
    if not deps:
        pytest.skip(f"{spec_id} has no dependencies")
    agent = agent_class(rich_mock_llm)
    result = _run(agent.run(pkg))
    assert result.status == "skipped"
    assert any("Dependency" in e for e in result.errors)


@pytest.mark.parametrize("spec_id", SPEC_IDS)
def test_pkp_agent_llm_failure_reported(spec_id, failing_mock_llm, pkg):
    """If the LLM raises, the agent returns 'failed' with the error."""
    agent_class, _, deps, _ = PKP_AGENTS[spec_id]
    _ensure_dependencies(pkg, deps)
    agent = agent_class(failing_mock_llm)
    result = _run(agent.run(pkg))
    assert result.status == "failed"
    assert any("unavailable" in e or "test" in e for e in result.errors)


@pytest.mark.parametrize("spec_id", SPEC_IDS)
def test_pkp_agent_empty_response_causes_failure(spec_id, empty_mock_llm, pkg):
    """Empty mock default causes parse/validation failure."""
    agent_class, _, deps, _ = PKP_AGENTS[spec_id]
    _ensure_dependencies(pkg, deps)
    agent = agent_class(empty_mock_llm)
    result = _run(agent.run(pkg))
    # Either failed (parse error) or revision_needed (validation error)
    assert result.status in ("failed", "revision_needed", "skipped"), (
        f"{spec_id} unexpected status: {result.status}"
    )


class TestPKPBaseClass:
    """Direct tests of the PKPAgent base class methods."""

    def test_validate_empty_content(self):
        from movie_os.genesis.pkp_agents.base import PKPAgent

        class Stub(PKPAgent):
            name = "stub"
            spec_id = "X-0"
            spec_name = "Stub"
            phase = "A"
            dependencies = []
            def build_prompt(self, pkg): return ""
            def parse_response(self, response, pkg): return {}

        s = Stub.__new__(Stub)
        s.llm = None
        errors = s.validate({}, None)  # type: ignore[arg-type]
        assert "Empty" in errors[0]

    def test_assess_confidence_from_field(self):
        from movie_os.genesis.pkp_agents.base import PKPAgent

        class Stub(PKPAgent):
            name = "stub"
            spec_id = "X-0"
            spec_name = "Stub"
            phase = "A"
            dependencies = []
            def build_prompt(self, pkg): return ""
            def parse_response(self, response, pkg): return {}

        s = Stub.__new__(Stub)
        s.llm = None
        assert s.assess_confidence({"confidence": "confirmed"}, None) == ConfidenceLevel.CONFIRMED
        assert s.assess_confidence({"confidence": "bogus"}, None) == ConfidenceLevel.INFERRED
        assert s.assess_confidence({}, None) == ConfidenceLevel.INFERRED

    def test_get_dependency_content(self, rich_mock_llm, pkg):
        from movie_os.genesis.pkp_agents.base import PKPAgent

        class Stub(PKPAgent):
            name = "stub"
            spec_id = "X-0"
            spec_name = "Stub"
            phase = "A"
            dependencies = ["PKP-00"]
            def build_prompt(self, pkg): return ""
            def parse_response(self, response, pkg): return {}

        pkg.set_specification(Specification(
            spec_id="PKP-00", spec_name="V", phase="A",
            content={"vision_statement": "x"},
        ))
        s = Stub.__new__(Stub)
        s.llm = rich_mock_llm
        deps = s.get_dependency_content(pkg)
        assert "PKP-00" in deps
        assert deps["PKP-00"]["vision_statement"] == "x"


class TestChiefArchitect:
    def test_identity(self, rich_mock_llm):
        ca = ChiefArchitect(rich_mock_llm)
        assert ca.name == "chief_architect"
        assert ca.spec_id == "CHIEF"
        assert ca.phase == "G"
        # Depends on all 19 PKP specs
        assert len(ca.dependencies) == 19

    def test_runs_when_all_pkps_present(self, rich_mock_llm, populated_pkg):
        ca = ChiefArchitect(rich_mock_llm)
        result = _run(ca.run(populated_pkg))
        assert result.status in ("success", "revision_needed"), result.errors

    def test_skipped_when_pkps_missing(self, rich_mock_llm, pkg):
        ca = ChiefArchitect(rich_mock_llm)
        result = _run(ca.run(pkg))
        assert result.status == "skipped"
        assert any("Dependency" in e for e in result.errors)

    def test_validate_missing_required_fields(self, rich_mock_llm):
        ca = ChiefArchitect(rich_mock_llm)
        errors = ca.validate({}, None)  # type: ignore[arg-type]
        assert any("overall_assessment" in e for e in errors)
        assert any("readiness" in e for e in errors)
