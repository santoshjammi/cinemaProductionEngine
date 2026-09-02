"""Dialogue Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class DialogueStandard(Standard):
    name = "dialogue"
    purpose = "Authenticity, subtext, character voice, plot advancement."
    principles = ["Objective quality criteria for dialogue dimension."]
    criteria = [
        QualityCriterion(name="authenticity", description="Quality check for authenticity", weight=0.25),
        QualityCriterion(name="subtext_presence", description="Quality check for subtext_presence", weight=0.25),
        QualityCriterion(name="character_voice", description="Quality check for character_voice", weight=0.25),
        QualityCriterion(name="plot_advancement", description="Quality check for plot_advancement", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="dialogue-001", description="Validate dialogue quality", evaluator="heuristic"),
    ]
    failure_conditions = ["authenticity fails to meet minimum threshold", "subtext_presence fails to meet minimum threshold", "character_voice fails to meet minimum threshold", "plot_advancement fails to meet minimum threshold"]
    required_evidence = ["authenticity_evidence", "subtext_presence_evidence", "character_voice_evidence", "plot_advancement_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("dialogue", {})
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
