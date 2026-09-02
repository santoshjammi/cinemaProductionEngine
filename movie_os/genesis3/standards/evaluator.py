"""Standards Evaluator — runs all standards against a story package."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from . import STANDARDS, _init_registry, evaluate_all


class StandardsReport(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    per_standard: dict[str, dict] = Field(default_factory=dict)
    certification_eligible: bool = False
    total_standards: int = 0
    passed_standards: int = 0
    failed_standards: int = 0


class StandardsEvaluator:
    def evaluate(self, evidence: dict[str, Any]) -> StandardsReport:
        _init_registry()
        results = evaluate_all(evidence)
        per_std = {name: r.model_dump() for name, r in results.items()}
        passed = sum(1 for r in results.values() if r.passed)
        total = len(results)
        overall = sum(r.score for r in results.values()) / total if total > 0 else 0.0
        return StandardsReport(
            overall_score=round(overall, 4),
            per_standard=per_std,
            certification_eligible=passed == total,
            total_standards=total,
            passed_standards=passed,
            failed_standards=total - passed,
        )
