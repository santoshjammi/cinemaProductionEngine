"""Cinema Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class CinemaStandard(Standard):
    name = "cinema"
    purpose = "Visual storytelling, pacing, shot composition quality."
    principles = ["Objective quality criteria for cinema dimension."]
    criteria = [
        QualityCriterion(name="pacing_quality", description="Quality check for pacing_quality", weight=0.25),
        QualityCriterion(name="shot_composition", description="Quality check for shot_composition", weight=0.25),
        QualityCriterion(name="visual_storytelling", description="Quality check for visual_storytelling", weight=0.25),
        QualityCriterion(name="dramatic_structure", description="Quality check for dramatic_structure", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="cinema-001", description="Validate cinema quality", evaluator="heuristic"),
    ]
    failure_conditions = ["pacing_quality fails to meet minimum threshold", "shot_composition fails to meet minimum threshold", "visual_storytelling fails to meet minimum threshold", "dramatic_structure fails to meet minimum threshold"]
    required_evidence = ["pacing_quality_evidence", "shot_composition_evidence", "visual_storytelling_evidence", "dramatic_structure_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("cinema", {})
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
