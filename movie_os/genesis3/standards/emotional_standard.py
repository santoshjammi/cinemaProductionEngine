"""Emotional Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class EmotionalStandard(Standard):
    name = "emotional"
    purpose = "Emotional arc, payoff delivery, catharsis quality."
    principles = ["Objective quality criteria for emotional dimension."]
    criteria = [
        QualityCriterion(name="emotional_arc", description="Quality check for emotional_arc", weight=0.25),
        QualityCriterion(name="payoff_delivery", description="Quality check for payoff_delivery", weight=0.25),
        QualityCriterion(name="catharsis_quality", description="Quality check for catharsis_quality", weight=0.25),
        QualityCriterion(name="intended_emotion", description="Quality check for intended_emotion", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="emotional-001", description="Validate emotional quality", evaluator="heuristic"),
    ]
    failure_conditions = ["emotional_arc fails to meet minimum threshold", "payoff_delivery fails to meet minimum threshold", "catharsis_quality fails to meet minimum threshold", "intended_emotion fails to meet minimum threshold"]
    required_evidence = ["emotional_arc_evidence", "payoff_delivery_evidence", "catharsis_quality_evidence", "intended_emotion_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("emotional", {})
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
