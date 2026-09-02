"""QA Department - orchestrates 9 constitutional reviews over compiler evidence."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, QADepartmentReport


class DepartmentResult(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    constitution_name: str
    reviewed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    review: ConstitutionReview


class QADepartment(BaseModel):
    _constitutions: Dict[str, BaseConstitution] = {}

    @classmethod
    def register(cls, name: str, constitution: BaseConstitution) -> None:
        cls._constitutions[name] = constitution

    @classmethod
    def get_constitution(cls, name: str) -> BaseConstitution | None:
        return cls._constitutions.get(name)

    @classmethod
    def list_constitutions(cls) -> List[str]:
        return sorted(cls._constitutions.keys())

    def review_all(self, evidence: Dict[str, Any]) -> QADepartmentReport:
        reviews: Dict[str, ConstitutionReview] = {}
        for name in sorted(self._constitutions):
            reviews[name] = self._constitutions[name].review(evidence)
        return self._aggregate(reviews)

    def review_specific(self, constitution_name: str, evidence: Dict[str, Any]) -> ConstitutionReview:
        const_obj = self._constitutions.get(constitution_name)
        if not const_obj:
            available = ", ".join(sorted(self._constitutions))
            raise ValueError("Unknown constitution '" + constitution_name + "'. Available: " + available)
        return const_obj.review(evidence)

    def review_batch(self, evidence_list: List[Dict[str, Any]]) -> List[QADepartmentReport]:
        return [self.review_all(e) for e in evidence_list]

    def _aggregate(self, reviews: Dict[str, ConstitutionReview]) -> QADepartmentReport:
        statuses = {}
        for rname, review_obj in reviews.items():
            statuses[rname] = review_obj.status
        scores = [r[1].overall_score for r in reviews.items()]

        has_fail = "FAIL" in statuses.values()
        has_conditional = "CONDITIONAL" in statuses.values()

        if has_fail:
            overall_status = "FAIL"
        elif has_conditional:
            overall_status = "CONDITIONAL"
        else:
            overall_status = "PASS"

        overall_score = round(sum(scores) / len(scores), 4) if scores else 0.0

        critical_issues: List[str] = []
        all_recs: List[str] = []
        for rname, review_obj in sorted(reviews.items()):
            if review_obj.status == "FAIL":
                failed_stds = [s.standard_name for s in review_obj.standards_checked if s.status == "FAIL"]
                detail = ", ".join(failed_stds) if failed_stds else "no detail"
                critical_issues.append("[" + rname + "] FAILED: " + detail)
            for rec_item in review_obj.recommendations:
                all_recs.append("[" + rname + "] " + rec_item)

        summary = (str(overall_status) + ": " + str(len(reviews)) + " constitutions reviewed. "
                  + "Overall score: " + f"{overall_score:.2f}" + ". "
                  + str(len(critical_issues)) + " critical issue(s).")

        return QADepartmentReport(
            reviews=reviews,
            overall_status=overall_status,
            overall_score=overall_score,
            summary=summary,
            critical_issues=critical_issues,
            recommendations=all_recs,
        )
