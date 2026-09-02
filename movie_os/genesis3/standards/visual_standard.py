"""Visual Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class VisualStandard(Standard):
    name = "visual"
    purpose = "Color palette, lighting, visual language consistency."
    principles = ["Objective quality criteria for visual dimension."]
    criteria = [
        QualityCriterion(name="color_palette", description="Quality check for color_palette", weight=0.25),
        QualityCriterion(name="lighting_scheme", description="Quality check for lighting_scheme", weight=0.25),
        QualityCriterion(name="visual_language", description="Quality check for visual_language", weight=0.25),
        QualityCriterion(name="visual_metaphor", description="Quality check for visual_metaphor", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="visual-001", description="Validate visual quality", evaluator="heuristic"),
    ]
    failure_conditions = ["color_palette fails to meet minimum threshold", "lighting_scheme fails to meet minimum threshold", "visual_language fails to meet minimum threshold", "visual_metaphor fails to meet minimum threshold"]
    required_evidence = ["color_palette_evidence", "lighting_scheme_evidence", "visual_language_evidence", "visual_metaphor_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("visual", {})
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
