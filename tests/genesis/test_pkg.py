"""Unit tests for movie_os.genesis.pkg.ProductionKnowledgeGraph."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from movie_os.genesis.models import (
    ConfidenceLevel,
    KnowledgeEdge,
    KnowledgeNode,
    Specification,
)
from movie_os.genesis.pkg import ProductionKnowledgeGraph


class TestProductionKnowledgeGraphBasics:
    def test_in_memory_construction(self, pkg):
        assert pkg.db_path == ":memory:"
        # Touching conn materializes schema
        assert pkg.conn is not None

    def test_synopsis_property(self, pkg):
        pkg.synopsis = "A test synopsis"
        assert pkg.synopsis == "A test synopsis"

    def test_constraints_property(self, pkg):
        pkg.constraints = {"runtime": "15min"}
        assert pkg.constraints == {"runtime": "15min"}


class TestNodes:
    def test_add_and_get_node(self, pkg):
        node = KnowledgeNode(
            id="n1", type="character", label="Daniel",
            properties={"age": 42}, confidence=ConfidenceLevel.CONFIRMED,
        )
        pkg.add_node(node)
        retrieved = pkg.get_node("n1")
        assert retrieved is not None
        assert retrieved.id == "n1"
        assert retrieved.type == "character"
        assert retrieved.properties == {"age": 42}
        assert retrieved.confidence == ConfidenceLevel.CONFIRMED

    def test_get_node_missing_returns_none(self, pkg):
        assert pkg.get_node("missing") is None

    def test_get_nodes_by_type(self, pkg):
        pkg.add_node(KnowledgeNode(id="n1", type="character", label="A"))
        pkg.add_node(KnowledgeNode(id="n2", type="character", label="B"))
        pkg.add_node(KnowledgeNode(id="n3", type="scene", label="S1"))
        chars = pkg.get_nodes_by_type("character")
        assert len(chars) == 2
        assert all(n.type == "character" for n in chars)

    def test_get_nodes_by_type_empty(self, pkg):
        assert pkg.get_nodes_by_type("nothing") == []

    def test_add_node_is_idempotent(self, pkg):
        node = KnowledgeNode(id="x", type="t", label="L")
        pkg.add_node(node)
        node.label = "L2"
        pkg.add_node(node)
        # INSERT OR REPLACE updates the row
        assert pkg.get_node("x").label == "L2"


class TestEdges:
    def test_add_and_get_edge(self, pkg):
        edge = KnowledgeEdge(
            id="e1", type="married_to", source_id="d", target_id="e",
            confidence=ConfidenceLevel.EXPLICIT,
        )
        pkg.add_edge(edge)
        from_edges = pkg.get_edges_from("d")
        assert len(from_edges) == 1
        assert from_edges[0].type == "married_to"

    def test_get_edges_to(self, pkg):
        pkg.add_edge(KnowledgeEdge(id="e1", type="x", source_id="a", target_id="b"))
        pkg.add_edge(KnowledgeEdge(id="e2", type="x", source_id="c", target_id="b"))
        to_b = pkg.get_edges_to("b")
        assert len(to_b) == 2

    def test_get_edges_missing(self, pkg):
        assert pkg.get_edges_from("nothing") == []


class TestSpecifications:
    def test_set_and_get_spec(self, pkg):
        spec = Specification(
            spec_id="PKP-00", spec_name="Vision", phase="A",
            content={"vision_statement": "test"},
            confidence=ConfidenceLevel.INFERRED,
        )
        pkg.set_specification(spec)
        retrieved = pkg.get_specification("PKP-00")
        assert retrieved is not None
        assert retrieved.spec_name == "Vision"
        assert retrieved.content == {"vision_statement": "test"}

    def test_get_spec_missing(self, pkg):
        assert pkg.get_specification("PKP-99") is None

    def test_has_specification(self, pkg):
        assert not pkg.has_specification("PKP-00")
        pkg.set_specification(Specification(
            spec_id="PKP-00", spec_name="V", phase="A"
        ))
        assert pkg.has_specification("PKP-00")

    def test_get_all_specifications(self, pkg):
        for i in range(3):
            pkg.set_specification(Specification(
                spec_id=f"PKP-0{i}", spec_name=f"S{i}", phase="A"
            ))
        all_specs = pkg.get_all_specifications()
        assert len(all_specs) == 3
        assert "PKP-00" in all_specs


class TestDiscoveryResults:
    def test_set_and_get(self, pkg):
        pkg.set_discovery_result("intent", {"intent": "x"})
        assert pkg.get_discovery_result("intent") == {"intent": "x"}

    def test_get_missing_returns_none(self, pkg):
        assert pkg.get_discovery_result("missing") is None

    def test_get_all_discovery_results(self, pkg):
        pkg.set_discovery_result("a", 1)
        pkg.set_discovery_result("b", 2)
        assert pkg.get_all_discovery_results() == {"a": 1, "b": 2}


class TestQuestions:
    def test_add_question(self, pkg):
        pkg.add_question({"question": "Why?", "index": 0})
        qs = pkg.get_questions()
        assert len(qs) == 1
        assert qs[0]["question"] == "Why?"

    def test_answer_question(self, pkg):
        pkg.add_question({"question": "Why?"})
        pkg.answer_question(0, "Because")
        q = pkg.get_questions()[0]
        assert q["answer"] == "Because"
        assert q["answered"] is True

    def test_answer_out_of_range_does_nothing(self, pkg):
        pkg.add_question({"question": "Why?"})
        pkg.answer_question(5, "x")  # no error
        assert pkg.get_questions()[0].get("answered", False) is False


class TestCompleteness:
    def test_set_completeness(self, pkg):
        pkg.set_completeness("story", 0.8)
        assert pkg.get_overall_completeness() == 0.8

    def test_overall_completeness_is_average(self, pkg):
        pkg.set_completeness("story", 1.0)
        pkg.set_completeness("character", 0.5)
        assert pkg.get_overall_completeness() == pytest.approx(0.75)

    def test_empty_completeness_is_zero(self, pkg):
        assert pkg.get_overall_completeness() == 0.0


class TestPersistence:
    def test_save_and_load_state(self, tmp_path):
        path = str(tmp_path / "test.db")
        g = ProductionKnowledgeGraph(path)
        g.synopsis = "Test"
        g.constraints = {"k": "v"}
        g.set_discovery_result("intent", {"a": 1})
        g.set_completeness("story", 0.5)
        g.save_state()

        # New PKG instance, load state
        g2 = ProductionKnowledgeGraph(path)
        loaded = g2.load_state(g.state.session_id)
        assert loaded is True
        assert g2.synopsis == "Test"
        assert g2.constraints == {"k": "v"}
        assert g2.get_discovery_result("intent") == {"a": 1}
        assert g2.get_overall_completeness() == 0.5

    def test_load_state_missing(self, pkg):
        assert pkg.load_state("nonexistent-session") is False

    def test_close(self, tmp_path):
        path = str(tmp_path / "test.db")
        g = ProductionKnowledgeGraph(path)
        g.set_specification(Specification(spec_id="PKP-00", spec_name="V", phase="A"))
        g.close()
        # Should be safe to close again
        g.close()
        # Can re-open
        g2 = ProductionKnowledgeGraph(path)
        assert g2.has_specification("PKP-00")
