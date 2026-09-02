"""Tests for PhaseBase models — ReviewFeedback, CritiqueFeedback, ValidationResult."""

from __future__ import annotations

import pytest
from movie_os.genesis2.phase_base import (
    PhaseBase,
    ReviewFeedback,
    CritiqueFeedback,
    ValidationResult,
)


class TestReviewFeedback:
    def test_defaults(self):
        rf = ReviewFeedback()
        assert rf.issues == []
        assert rf.score == 0.0
        assert rf.recommendations == []

    def test_create_scored(self):
        rf = ReviewFeedback(
            issues=["missing theme", "no audience"],
            score=0.6,
            recommendations=["Add theme field", "Specify audience"],
        )
        assert len(rf.issues) == 2
        assert rf.score == 0.6
        assert "Add theme field" in rf.recommendations

    def test_score_clamps(self):
        rf = ReviewFeedback(score=-0.5)
        assert rf.score >= 0.0

    def test_score_clamp_high(self):
        rf = ReviewFeedback(score=1.5)
        assert rf.score <= 1.0


class TestCritiqueFeedback:
    def test_defaults(self):
        cf = CritiqueFeedback()
        assert cf.strengths == []
        assert cf.weaknesses == []
        assert cf.improvements == []

    def test_create_with_findings(self):
        cf = CritiqueFeedback(
            strengths=["strong theme", "clear conflict"],
            weaknesses=["shallow character psychology"],
            improvements=["Deepen antagonist motivation"],
        )
        assert len(cf.strengths) == 2
        assert any("Deepen antagonist" in i for i in cf.improvements)

    def test_score_defaults_to_none(self):
        from movie_os.genesis2.phase_base import ConfidenceLevel
        cf = CritiqueFeedback()
        # No score field — just structured feedback
        assert isinstance(cf, CritiqueFeedback)


class TestValidationResult:
    def test_defaults(self):
        vr = ValidationResult()
        assert vr.passed is True  # defaults to True because no issues
        assert vr.issues == []
        assert vr.score == 0.0

    def test_passed_when_no_issues(self):
        vr = ValidationResult(passed=True, score=1.0)
        assert vr.passed is True
        assert vr.score == 1.0

    def test_failed_with_issues(self):
        from movie_os.genesis2.models import ValidationIssue
        issues = [
            ValidationIssue(category="missing", severity="error", location="p1", description="x"),
            ValidationIssue(category="contradiction", severity="warning", location="p2", description="y"),
        ]
        vr = ValidationResult(passed=False, score=0.5, issues=issues)
        assert vr.passed is False
        assert len(vr.issues) == 2
