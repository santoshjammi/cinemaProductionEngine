"""Production Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class ProductionStandard(Standard):
    name = "production"
    purpose = "Feasibility, budget, schedule, resource requirements."
    principles = ["Objective quality criteria for production dimension."]
    criteria = [
        QualityCriterion(name="feasibility", description="Quality check for feasibility", weight=0.25),
        QualityCriterion(name="budget_realism", description="Quality check for budget_realism", weight=0.25),
        QualityCriterion(name="schedule_feasibility", description="Quality check for schedule_feasibility", weight=0.25),
        QualityCriterion(name="resource_availability", description="Quality check for resource_availability", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="production-001", description="Validate production quality", evaluator="heuristic"),
    ]
    failure_conditions = ["feasibility fails to meet minimum threshold", "budget_realism fails to meet minimum threshold", "schedule_feasibility fails to meet minimum threshold", "resource_availability fails to meet minimum threshold"]
    required_evidence = ["feasibility_evidence", "budget_realism_evidence", "schedule_feasibility_evidence", "resource_availability_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("production", {})
        checks = []
        for cn in self.criteria:
            key = cn.name
            val = data.get(key, data.get(key + "_score", 0.5))
            if isinstance(val, bool):
                checks.append((self._score_from_bool(val), cn.weight))
            elif isinstance(val, (int, float)):
                checks.append((min(val, 1.0), cn.weight))
            else:
                checks.append((0.5, cn.weight))
        score = self._weighted_score(checks)
        failures = [c.name for c, (s, _) in zip(self.criteria, checks) if s < 0.5]
        return StandardResult(
            standard_name=self.name,
            passed=score >= self.certification_threshold,
            score=round(score, 4),
            evidence=[f"score={score:.2f}"],
            failures=failures,
            details=f"{{len(failures)}} failure(s) out of {len(self.criteria)} criteria",
        )
