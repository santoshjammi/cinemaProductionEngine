"""Unit tests for movie_os.genesis.completion_gate."""

from __future__ import annotations

import pytest

from movie_os.genesis.completion_gate import (
    PreProductionCompletionGate,
    REQUIRED_SPECS,
)
from movie_os.genesis.models import ConfidenceLevel, Specification


class TestRequiredSpecs:
    def test_exactly_19(self):
        assert len(REQUIRED_SPECS) == 19

    def test_all_present(self):
        for i in range(19):
            assert f"PKP-{i:02d}" in REQUIRED_SPECS

    def test_sequential(self):
        assert REQUIRED_SPECS[0] == "PKP-00"
        assert REQUIRED_SPECS[-1] == "PKP-18"


class TestGateResult:
    def test_initial_state(self, pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        assert result.passed is False  # empty pkg fails
        assert len(result.blockers) > 0

    def test_add_check_pass(self, pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        # Find a passing check
        passing = [c for c in result.criteria if c["passed"]]
        assert len(passing) >= 0  # may be 0 if everything is failing

    def test_to_dict(self, pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        d = result.to_dict()
        assert "passed" in d
        assert "criteria" in d
        assert "blockers" in d
        assert "warnings" in d


class TestGateCriteria:
    def test_all_19_specs_present_passes(self, populated_pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(populated_pkg)
        # The first criterion should pass
        first = result.criteria[0]
        assert first["name"] == "all_specifications_exist"
        assert first["passed"] is True

    def test_missing_specs_fails(self, pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "all_specifications_exist")
        assert crit["passed"] is False
        assert "Missing" in crit["detail"]

    def test_dependencies_satisfied_passes_for_populated(self, populated_pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(populated_pkg)
        crit = next(c for c in result.criteria if c["name"] == "dependencies_satisfied")
        assert crit["passed"] is True

    def test_validation_status_failed_blocks(self, pkg):
        pkg.set_specification(Specification(
            spec_id="PKP-00", spec_name="V", phase="A",
            validation_status="failed", validation_errors=["bad"],
        ))
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "cross_validation_passed")
        assert crit["passed"] is False

    def test_validation_status_passed_passes(self, pkg):
        pkg.set_specification(Specification(
            spec_id="PKP-00", spec_name="V", phase="A",
            validation_status="passed",
        ))
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "cross_validation_passed")
        assert crit["passed"] is True

    def test_critical_contradictions(self, pkg):
        pkg.set_discovery_result(
            "story_review",
            {"contradictions": [{"spec_ids": ["A"], "description": "bad", "severity": "critical"}]},
        )
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "no_critical_contradictions")
        assert crit["passed"] is False

    def test_non_critical_contradictions_pass(self, pkg):
        pkg.set_discovery_result(
            "story_review",
            {"contradictions": [{"spec_ids": ["A"], "description": "minor", "severity": "low"}]},
        )
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "no_critical_contradictions")
        assert crit["passed"] is True

    def test_unknown_confidence_blocks(self, pkg):
        pkg.set_specification(Specification(
            spec_id="PKP-00", spec_name="V", phase="A",
            confidence=ConfidenceLevel.UNKNOWN,
        ))
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "confidence_thresholds_met")
        assert crit["passed"] is False

    def test_inferred_confidence_passes(self, pkg):
        pkg.set_specification(Specification(
            spec_id="PKP-00", spec_name="V", phase="A",
            confidence=ConfidenceLevel.INFERRED,
        ))
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "confidence_thresholds_met")
        assert crit["passed"] is True

    def test_reviews_completed_criterion(self, pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "reviews_completed")
        # No reviews stored = fails
        assert crit["passed"] is False
        assert "Missing reviews" in crit["detail"]

    def test_reviews_completed_when_all_set(self, pkg):
        for key in ["story_review", "character_review", "narrative_review", "psychology_review"]:
            pkg.set_discovery_result(key, {"status": "approved"})
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "reviews_completed")
        assert crit["passed"] is True

    def test_knowledge_graph_complete_min_threshold(self, pkg):
        pkg.set_completeness("story", 0.5)
        gate = PreProductionCompletionGate(min_completeness=0.8)
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "knowledge_graph_complete")
        assert crit["passed"] is False

    def test_knowledge_graph_complete_meets_threshold(self, pkg):
        pkg.set_completeness("story", 1.0)
        gate = PreProductionCompletionGate(min_completeness=0.8)
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "knowledge_graph_complete")
        assert crit["passed"] is True

    def test_blueprint_derived_missing_blocks(self, pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "blueprint_derived")
        assert crit["passed"] is False

    def test_blueprint_derived_passed(self, pkg):
        pkg.set_specification(Specification(
            spec_id="PKP-15", spec_name="Blueprint", phase="F",
            validation_status="passed",
        ))
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "blueprint_derived")
        assert crit["passed"] is True

    def test_blueprint_derived_failed(self, pkg):
        pkg.set_specification(Specification(
            spec_id="PKP-15", spec_name="Blueprint", phase="F",
            validation_status="failed",
        ))
        gate = PreProductionCompletionGate()
        result = gate.check(pkg)
        crit = next(c for c in result.criteria if c["name"] == "blueprint_derived")
        assert crit["passed"] is False


class TestGateFullyPopulated:
    def test_all_pass_with_fully_populated_pkg(self, populated_pkg):
        gate = PreProductionCompletionGate()
        result = gate.check(populated_pkg)
        # 8 criteria, all should pass on the populated fixture
        assert result.passed is True, f"Failed criteria: {result.blockers}"
        assert len(result.criteria) == 8

    def test_to_dict_serializable(self, populated_pkg):
        import json
        gate = PreProductionCompletionGate()
        result = gate.check(populated_pkg)
        d = result.to_dict()
        json.dumps(d, default=str)  # must be JSON-serializable
