"""Tests for P0-03R phase-10 validation consistency retry."""
from __future__ import annotations

import pytest

from movie_os.genesis2.phases.phase10_validation import ValidationPhase


def _ko(passed, score, issues, reasoning):
    from movie_os.genesis2.models import Validation as ValidationKO, ConfidenceLevel
    return ValidationKO(
        issues=issues,
        passed=passed,
        score=score,
        purpose="", creative_intent="", reasoning=reasoning, confidence=ConfidenceLevel.CONFIRMED,
    )


def test_contradictory_verdict_detected():
    # 0 issues + high score + passed=false = contradictory.
    ko = _ko(False, 0.85, [], "")
    assert ValidationPhase._is_contradictory(ko) is True


def test_contradictory_empty_reasoning_detected():
    ko = _ko(False, 0.0, [], "")
    assert ValidationPhase._is_contradictory(ko) is True


def test_clear_failure_not_contradictory():
    # Genuine failure with issues is NOT contradictory.
    from movie_os.genesis2.models import ValidationIssue
    ko = _ko(False, 0.4, [ValidationIssue(category="plot", severity="error", location="s1", description="x")], "real defect")
    assert ValidationPhase._is_contradictory(ko) is False


def test_clear_pass_not_contradictory():
    ko = _ko(True, 1.0, [], "all good")
    assert ValidationPhase._is_contradictory(ko) is False


def test_fail_with_explanation_but_no_issues_not_contradictory():
    # Explicitly failed with reasoning but no issues — treated as genuine.
    ko = _ko(False, 0.3, [], "found pacing problem")
    assert ValidationPhase._is_contradictory(ko) is False
