"""Scene Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class SceneStandard(Standard):
    name = "scene"
    purpose = "Scene purpose, transitions, dramatic value."
    principles = ["Objective quality criteria for scene dimension."]
    criteria = [
        QualityCriterion(name="scene_purpose", description="Quality check for scene_purpose", weight=0.25),
        QualityCriterion(name="transition_quality", description="Quality check for transition_quality", weight=0.25),
        QualityCriterion(name="dramatic_value", description="Quality check for dramatic_value", weight=0.25),
        QualityCriterion(name="scene_necessity", description="Quality check for scene_necessity", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="scene-001", description="Validate scene quality", evaluator="heuristic"),
    ]
    failure_conditions = ["scene_purpose fails to meet minimum threshold", "transition_quality fails to meet minimum threshold", "dramatic_value fails to meet minimum threshold", "scene_necessity fails to meet minimum threshold"]
    required_evidence = ["scene_purpose_evidence", "transition_quality_evidence", "dramatic_value_evidence", "scene_necessity_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("scene", {})
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
