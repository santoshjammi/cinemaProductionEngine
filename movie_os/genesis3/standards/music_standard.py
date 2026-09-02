"""Music Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class MusicStandard(Standard):
    name = "music"
    purpose = "Thematic score, emotional alignment, musical pacing."
    principles = ["Objective quality criteria for music dimension."]
    criteria = [
        QualityCriterion(name="thematic_score", description="Quality check for thematic_score", weight=0.25),
        QualityCriterion(name="emotional_alignment", description="Quality check for emotional_alignment", weight=0.25),
        QualityCriterion(name="musical_pacing", description="Quality check for musical_pacing", weight=0.25),
        QualityCriterion(name="leitmotif_use", description="Quality check for leitmotif_use", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="music-001", description="Validate music quality", evaluator="heuristic"),
    ]
    failure_conditions = ["thematic_score fails to meet minimum threshold", "emotional_alignment fails to meet minimum threshold", "musical_pacing fails to meet minimum threshold", "leitmotif_use fails to meet minimum threshold"]
    required_evidence = ["thematic_score_evidence", "emotional_alignment_evidence", "musical_pacing_evidence", "leitmotif_use_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("music", {})
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
