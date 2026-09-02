"""Psychological Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class PsychologicalStandard(Standard):
    name = "psychological"
    purpose = "Character psychology, motivation consistency, behavioral logic."
    principles = ["Objective quality criteria for psychological dimension."]
    criteria = [
        QualityCriterion(name="behavioral_consistency", description="Quality check for behavioral_consistency", weight=0.25),
        QualityCriterion(name="motivation_soundness", description="Quality check for motivation_soundness", weight=0.25),
        QualityCriterion(name="internal_logic", description="Quality check for internal_logic", weight=0.25),
        QualityCriterion(name="psychological_depth", description="Quality check for psychological_depth", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="psychological-001", description="Validate psychological quality", evaluator="heuristic"),
    ]
    failure_conditions = ["behavioral_consistency fails to meet minimum threshold", "motivation_soundness fails to meet minimum threshold", "internal_logic fails to meet minimum threshold", "psychological_depth fails to meet minimum threshold"]
    required_evidence = ["behavioral_consistency_evidence", "motivation_soundness_evidence", "internal_logic_evidence", "psychological_depth_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("psychological", {})
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
