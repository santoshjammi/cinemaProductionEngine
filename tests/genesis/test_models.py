"""Unit tests for movie_os.genesis.models."""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from movie_os.genesis.models import (
    AgentResult,
    ConfidenceLevel,
    KnowledgeEdge,
    KnowledgeNode,
    PKGState,
    Specification,
)


class TestConfidenceLevel:
    def test_all_five_levels_exist(self):
        assert ConfidenceLevel.EXPLICIT.value == "explicit"
        assert ConfidenceLevel.INFERRED.value == "inferred"
        assert ConfidenceLevel.CONFIRMED.value == "confirmed"
        assert ConfidenceLevel.ASSUMED.value == "assumed"
        assert ConfidenceLevel.UNKNOWN.value == "unknown"

    def test_inherits_from_str(self):
        # String enum allows direct string comparison
        assert ConfidenceLevel.EXPLICIT == "explicit"
        assert ConfidenceLevel.UNKNOWN == "unknown"

    def test_count(self):
        assert len(list(ConfidenceLevel)) == 5


class TestKnowledgeNode:
    def test_default_construction(self):
        node = KnowledgeNode(type="character", label="Daniel")
        assert node.type == "character"
        assert node.label == "Daniel"
        assert node.properties == {}
        assert node.confidence == ConfidenceLevel.UNKNOWN
        assert node.provenance == ""
        assert len(node.id) > 0  # UUID generated
        assert isinstance(node.created_at, str)

    def test_custom_id(self):
        node = KnowledgeNode(id="node-1", type="scene", label="Dinner")
        assert node.id == "node-1"

    def test_json_round_trip(self):
        node = KnowledgeNode(
            id="n1", type="character", label="Daniel",
            properties={"age": 42}, confidence=ConfidenceLevel.CONFIRMED,
        )
        data = node.model_dump()
        restored = KnowledgeNode(**data)
        assert restored.id == node.id
        assert restored.properties == node.properties


class TestKnowledgeEdge:
    def test_required_fields(self):
        with pytest.raises(ValidationError):
            KnowledgeEdge(type="married_to")  # missing source_id, target_id

    def test_construction(self):
        edge = KnowledgeEdge(type="married_to", source_id="d", target_id="e")
        assert edge.type == "married_to"
        assert edge.source_id == "d"
        assert edge.target_id == "e"
        assert edge.confidence == ConfidenceLevel.UNKNOWN

    def test_json_round_trip(self):
        edge = KnowledgeEdge(
            id="e1", type="causes", source_id="a", target_id="b",
            properties={"weight": 0.8}, confidence=ConfidenceLevel.INFERRED,
        )
        restored = KnowledgeEdge(**edge.model_dump())
        assert restored.properties == edge.properties
        assert restored.confidence == edge.confidence


class TestSpecification:
    def test_default_construction(self):
        spec = Specification(spec_id="PKP-00", spec_name="Vision", phase="A")
        assert spec.spec_id == "PKP-00"
        assert spec.content == {}
        assert spec.dependencies == []
        assert spec.validation_status == "pending"
        assert spec.validation_errors == []

    def test_with_content(self):
        spec = Specification(
            spec_id="PKP-04",
            spec_name="Story",
            phase="B",
            content={"premise": "A man withdraws"},
            confidence=ConfidenceLevel.INFERRED,
            dependencies=["PKP-03"],
        )
        assert spec.content["premise"] == "A man withdraws"
        assert spec.dependencies == ["PKP-03"]
        assert spec.confidence == ConfidenceLevel.INFERRED


class TestPKGState:
    def test_default_construction(self):
        state = PKGState()
        assert state.synopsis == ""
        assert state.constraints == {}
        assert state.specifications == {}
        assert state.discovery_results == {}
        assert state.questions == []
        assert state.overall_completeness == 0.0
        assert state.current_stage == "init"
        assert len(state.session_id) > 0

    def test_construction_with_synopsis(self):
        state = PKGState(synopsis="A test", current_stage="discovery")
        assert state.synopsis == "A test"
        assert state.current_stage == "discovery"


class TestAgentResult:
    def test_default_construction(self):
        result = AgentResult(agent_name="test")
        assert result.agent_name == "test"
        assert result.spec_id == ""
        assert result.status == "success"
        assert result.confidence == ConfidenceLevel.UNKNOWN
        assert result.errors == []
        assert result.output == {}

    def test_all_statuses(self):
        for status in ("success", "failed", "skipped", "revision_needed"):
            r = AgentResult(agent_name="t", status=status)
            assert r.status == status
