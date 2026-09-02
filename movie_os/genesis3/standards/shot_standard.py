"""Shot Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class ShotStandard(Standard):
    name = "shot"
    purpose = "Composition, coverage, visual storytelling per shot."
    principles = ["Objective quality criteria for shot dimension."]
    criteria = [
        QualityCriterion(name="composition_quality", description="Quality check for composition_quality", weight=0.25),
        QualityCriterion(name="coverage", description="Quality check for coverage", weight=0.25),
        QualityCriterion(name="visual_storytelling", description="Quality check for visual_storytelling", weight=0.25),
        QualityCriterion(name="shot_variety", description="Quality check for shot_variety", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="shot-001", description="Validate shot quality", evaluator="heuristic"),
    ]
    failure_conditions = ["composition_quality fails to meet minimum threshold", "coverage fails to meet minimum threshold", "visual_storytelling fails to meet minimum threshold", "shot_variety fails to meet minimum threshold"]
    required_evidence = ["composition_quality_evidence", "coverage_evidence", "visual_storytelling_evidence", "shot_variety_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("shot", {})
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
