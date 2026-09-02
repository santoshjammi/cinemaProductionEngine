"""Tests for GENESIS Standards Framework."""
from __future__ import annotations
import pytest
from movie_os.genesis3.standards import (
    STANDARDS, get_standard, list_standards, evaluate_all,
    Standard, QualityCriterion, StandardResult,
)
from movie_os.genesis3.standards.evaluator import StandardsEvaluator, StandardsReport


class TestBaseModels:
    def test_quality_criterion_creation(self):
        c = QualityCriterion(name="test", description="Test criterion")
        assert c.name == "test"
        assert c.weight == 0.25

    def test_standard_result_creation(self):
        r = StandardResult(standard_name="test", passed=True, score=0.8)
        assert r.passed is True
        assert r.score == 0.8


class TestStandardsRegistry:
    def test_list_standards_returns_all(self):
        names = list_standards()
        assert len(names) == 14
        assert "story" in names
        assert "cinema" in names
        assert "production" in names

    def test_get_standard_by_name(self):
        std = get_standard("story")
        assert std.name == "story"
        assert isinstance(std, Standard)

    def test_get_standard_unknown_raises(self):
        with pytest.raises(KeyError):
            get_standard("nonexistent")

    def test_all_standards_have_purpose(self):
        for name in list_standards():
            std = get_standard(name)
            assert std.purpose, f"{name} missing purpose"
            assert len(std.principles) > 0, f"{name} missing principles"
            assert len(std.criteria) > 0, f"{name} missing criteria"

    def test_all_standards_have_threshold(self):
        for name in list_standards():
            std = get_standard(name)
            assert 0.0 <= std.certification_threshold <= 1.0


class TestStandardEvaluation:
    def test_story_standard_passes_with_good_evidence(self):
        std = get_standard("story")
        evidence = {
            "story": {
                "premise": "A man withdraws from his wife",
                "premise_resolved": True,
                "plot_outline": "Three act structure",
                "plot_holes": [],
                "climax": "Final confrontation",
                "theme": "Emotional withdrawal",
                "theme_reinforced": True,
            }
        }
        result = std.evaluate(evidence)
        assert result.passed is True
        assert result.score >= 0.7

    def test_story_standard_fails_with_bad_evidence(self):
        std = get_standard("story")
        evidence = {"story": {}}
        result = std.evaluate(evidence)
        assert result.passed is False
        assert len(result.failures) > 0

    def test_evaluate_all_runs_all_standards(self):
        evidence = {"story": {}, "cinema": {}, "emotional": {}, "psychological": {},
                     "narrative": {}, "character": {}, "dialogue": {}, "scene": {},
                     "shot": {}, "visual": {}, "audio": {}, "music": {},
                     "editing": {}, "production": {}}
        results = evaluate_all(evidence)
        assert len(results) == 14


class TestStandardsEvaluator:
    def test_evaluator_produces_report(self):
        evaluator = StandardsEvaluator()
        evidence = {"story": {"premise": "x", "premise_resolved": True, "plot_outline": "x", "plot_holes": [], "climax": "x", "theme": "x", "theme_reinforced": True}}
        report = evaluator.evaluate(evidence)
        assert isinstance(report, StandardsReport)
        assert report.total_standards == 14
        assert 0 <= report.overall_score <= 1.0

    def test_evaluator_empty_evidence(self):
        evaluator = StandardsEvaluator()
        report = evaluator.evaluate({})
        assert report.total_standards == 14
        assert report.certification_eligible is False

    def test_evaluator_all_pass(self):
        evaluator = StandardsEvaluator()
        evidence = {}
        for name in list_standards():
            evidence[name] = {}
        evidence["story"] = {"premise": "x", "premise_resolved": True, "plot_outline": "x", "plot_holes": [], "climax": "x", "theme": "x", "theme_reinforced": True}
        report = evaluator.evaluate(evidence)
        assert report.passed_standards >= 1
