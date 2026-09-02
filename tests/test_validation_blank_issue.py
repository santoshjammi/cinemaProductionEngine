"""Phase-10 structural retry: blank ValidationIssue is not a genuine finding."""
from movie_os.genesis2.models import Validation as ValidationKO, ValidationIssue
from movie_os.genesis2.phases.phase10_validation import ValidationPhase


def _blank_issue():
    return ValidationIssue(category="", severity="", location="", description="", suggestion="")


def test_blank_issue_is_contradictory():
    ko = ValidationKO(passed=False, score=0.0, issues=[_blank_issue()], reasoning="")
    assert ValidationPhase._is_contradictory(ko) is True


def test_genuine_issue_is_not_contradictory():
    ko = ValidationKO(passed=False, score=0.5,
                      issues=[ValidationIssue(category="quality", severity="blocker",
                                              location="phase_08", description="missing content")],
                      reasoning="phase 8 malformed")
    assert ValidationPhase._is_contradictory(ko) is False
