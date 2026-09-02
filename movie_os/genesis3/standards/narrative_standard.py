"""Narrative Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class NarrativeStandard(Standard):
    name = "narrative"
    purpose = "Cause-effect structure, subplot integration, narrative logic."
    principles = ["Objective quality criteria for narrative dimension."]
    criteria = [
        QualityCriterion(name="cause_effect_chain", description="Quality check for cause_effect_chain", weight=0.25),
        QualityCriterion(name="subplot_integration", description="Quality check for subplot_integration", weight=0.25),
        QualityCriterion(name="narrative_logic", description="Quality check for narrative_logic", weight=0.25),
        QualityCriterion(name="structural_coherence", description="Quality check for structural_coherence", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="narrative-001", description="Validate narrative quality", evaluator="heuristic"),
    ]
    failure_conditions = ["cause_effect_chain fails to meet minimum threshold", "subplot_integration fails to meet minimum threshold", "narrative_logic fails to meet minimum threshold", "structural_coherence fails to meet minimum threshold"]
    required_evidence = ["cause_effect_chain_evidence", "subplot_integration_evidence", "narrative_logic_evidence", "structural_coherence_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("narrative", {})
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
