"""Base models and abstract constitution for Story QA Department."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Literal, Dict

from pydantic import BaseModel, Field


class StandardCheck(BaseModel):
    """A single objective standard check against evidence."""

    standard_name: str = Field(description="Name of the standard checked")
    status: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        description="Result of this standard check"
    )
    score: float = Field(
        ge=0.0, le=1.0, description="Score for this standard (0-1)"
    )
    evidence_used: List[str] = Field(
        default_factory=list, description="Evidence chunks used to make the decision"
    )
    reasoning: str = Field(default="", description="Why this pass/fail/conditional was chosen")
    failure_reasons: List[str] = Field(
        default_factory=list,
        description="If FAIL or CONDITIONAL, why it failed",
    )


class ConstitutionReview(BaseModel):
    """The full review produced by a constitution."""

    constitution_name: str = Field(description="Which constitution was applied")
    status: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        description="Overall verdict of this review"
    )
    standards_checked: List[StandardCheck] = Field(default_factory=list)
    overall_score: float = Field(ge=0.0, le=1.0, description="Weighted average of all standards")
    summary: str = Field(default="", description="High-level narrative of findings")
    recommendations: List[str] = Field(default_factory=list)


class BaseConstitution(ABC):
    """Abstract base class every constitution MUST implement."""

    name: str
    standards: list[str]

    @abstractmethod
    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        """Evaluate evidence against this constitution's standards.

        Args:
            evidence: Dict keyed by compilation phase (story, character, etc.)
                      containing raw compiler output for this domain.

        Returns:
            A ConstitutionReview with all standards checked and an overall verdict.
        """

    # ------------------------------------------------------------------
    # helpers that subclasses can call
    # ------------------------------------------------------------------

    @staticmethod
    def _score_from_bool(value: bool) -> float:
        return 1.0 if value else 0.0

    @classmethod
    def _pass_or_condition(cls, passes: bool, detail: str = "") -> tuple[str, list[str]]:
        if passes:
            return "PASS", []
        return "CONDITIONAL", [detail] if detail else ["Insufficient evidence"]

    # ------------------------------------------------------------------
    # aggregation helper — subclasses call this after building standards
    # ------------------------------------------------------------------

    def _aggregate(
        self,
        standards: List[StandardCheck],
    ) -> tuple[str, float, str, list[str]]:
        """Compute overall status/score/summary from a list of StandardChecks.

        Returns (status, score, summary, recommendations).
        """
        if not standards:
            return "PASS", 0.0, "No standards checked.", []

        # Score is weighted average
        total_weight = sum(s.score * 10 for s in standards)
        overall_score = round(total_weight / sum(10 for _ in standards), 4)

        # Status logic: any FAIL -> FAIL; else CONDITIONAL if any present; else PASS
        statuses = {s.status for s in standards}
        if "FAIL" in statuses:
            status = "FAIL"
        elif "CONDITIONAL" in statuses:
            status = "CONDITIONAL"
        else:
            status = "PASS"

        # Summary
        pass_count = len([s for s in standards if s.status == "PASS"])
        fail_count = len([s for s in standards if s.status == "FAIL"])
        conditional_count = len([s for s in standards if s.status == "CONDITIONAL"])
        summary = (
            f"{status}: {pass_count}/{len(standards)} standards passed. "
            f"Score: {overall_score:.2f}. Failed: {fail_count}, Conditional: {conditional_count}."
        )

        # Recommendations from failures/conditionals
        recommendations: list[str] = []
        for s in standards:
            if s.status != "PASS":
                reason = s.failure_reasons[0] if s.failure_reasons else f"Score ({s.score}) below threshold"
                recommendations.append(f"{s.standard_name}: {reason}")

        return status, overall_score, summary, recommendations


class QADepartmentReport(BaseModel):
    """Composite report from running every constitution."""

    reviews: Dict[str, ConstitutionReview]
    overall_status: Literal["PASS", "FAIL", "CONDITIONAL"]
    overall_score: float = Field(ge=0.0, le=1.0)
    summary: str
    critical_issues: List[str]
    recommendations: List[str]
