"""Character Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class CharacterStandard(Standard):
    name = "character"
    purpose = "Arc completeness, growth tracking, consistency, relationships."
    principles = ["Objective quality criteria for character dimension."]
    criteria = [
        QualityCriterion(name="arc_completeness", description="Quality check for arc_completeness", weight=0.25),
        QualityCriterion(name="growth_tracking", description="Quality check for growth_tracking", weight=0.25),
        QualityCriterion(name="consistency", description="Quality check for consistency", weight=0.25),
        QualityCriterion(name="relationship_dynamics", description="Quality check for relationship_dynamics", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="character-001", description="Validate character quality", evaluator="heuristic"),
    ]
    failure_conditions = ["arc_completeness fails to meet minimum threshold", "growth_tracking fails to meet minimum threshold", "consistency fails to meet minimum threshold", "relationship_dynamics fails to meet minimum threshold"]
    required_evidence = ["arc_completeness_evidence", "growth_tracking_evidence", "consistency_evidence", "relationship_dynamics_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("character", {})
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
