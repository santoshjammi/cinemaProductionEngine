"""Editing Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class EditingStandard(Standard):
    name = "editing"
    purpose = "Rhythm, continuity, pacing of cuts and transitions."
    principles = ["Objective quality criteria for editing dimension."]
    criteria = [
        QualityCriterion(name="cut_rhythm", description="Quality check for cut_rhythm", weight=0.25),
        QualityCriterion(name="continuity", description="Quality check for continuity", weight=0.25),
        QualityCriterion(name="pacing", description="Quality check for pacing", weight=0.25),
        QualityCriterion(name="transition_quality", description="Quality check for transition_quality", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="editing-001", description="Validate editing quality", evaluator="heuristic"),
    ]
    failure_conditions = ["cut_rhythm fails to meet minimum threshold", "continuity fails to meet minimum threshold", "pacing fails to meet minimum threshold", "transition_quality fails to meet minimum threshold"]
    required_evidence = ["cut_rhythm_evidence", "continuity_evidence", "pacing_evidence", "transition_quality_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("editing", {})
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
